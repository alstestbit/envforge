"""Tests for envforge.validator module."""

import pytest

from envforge.schema import Schema
from envforge.validator import Validator, ValidationResult


SAMPLE_SCHEMA_DICT = {
    "vars": [
        {"name": "APP_NAME", "type": "string", "required": True},
        {"name": "PORT", "type": "int", "required": True},
        {"name": "DEBUG", "type": "bool", "required": False},
        {"name": "API_KEY", "type": "string", "required": False,
         "pattern": "[A-Za-z0-9]{16,}"},
    ]
}


@pytest.fixture
def schema():
    return Schema.from_dict(SAMPLE_SCHEMA_DICT)


@pytest.fixture
def validator(schema):
    return Validator(schema)


class TestValidator:
    def test_valid_env_passes(self, validator):
        env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "true"}
        result = validator.validate(env)
        assert result.is_valid

    def test_missing_required_field_fails(self, validator):
        env = {"PORT": "8080"}
        result = validator.validate(env)
        assert not result.is_valid
        assert any(e.key == "APP_NAME" for e in result.errors)

    def test_invalid_int_fails(self, validator):
        env = {"APP_NAME": "myapp", "PORT": "not_a_number"}
        result = validator.validate(env)
        assert not result.is_valid
        assert any(e.key == "PORT" for e in result.errors)

    def test_invalid_bool_fails(self, validator):
        env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "yes"}
        result = validator.validate(env)
        assert not result.is_valid
        assert any(e.key == "DEBUG" for e in result.errors)

    def test_valid_bool_values(self, validator):
        for val in ("true", "false", "1", "0", "True", "FALSE"):
            env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": val}
            result = validator.validate(env)
            assert result.is_valid, f"Expected valid for DEBUG={val!r}"

    def test_pattern_mismatch_fails(self, validator):
        env = {"APP_NAME": "myapp", "PORT": "8080", "API_KEY": "short"}
        result = validator.validate(env)
        assert not result.is_valid
        assert any(e.key == "API_KEY" for e in result.errors)

    def test_pattern_match_passes(self, validator):
        env = {"APP_NAME": "myapp", "PORT": "8080",
               "API_KEY": "AbCdEfGh12345678"}
        result = validator.validate(env)
        assert result.is_valid

    def test_optional_missing_field_passes(self, validator):
        env = {"APP_NAME": "myapp", "PORT": "3000"}
        result = validator.validate(env)
        assert result.is_valid

    def test_str_representation_on_failure(self, validator):
        result = validator.validate({})
        text = str(result)
        assert "Validation failed" in text

    def test_str_representation_on_success(self, validator):
        env = {"APP_NAME": "myapp", "PORT": "3000"}
        result = validator.validate(env)
        assert str(result) == "Validation passed."
