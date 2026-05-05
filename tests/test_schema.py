"""Tests for envforge schema parsing and validation."""

import json
import pytest
from envforge.schema import EnvVar, Schema, VALID_TYPES


SAMPLE_SCHEMA_PATH = "tests/fixtures/sample_schema.json"


class TestEnvVar:
    def test_default_type_is_string(self):
        var = EnvVar(name="FOO")
        assert var.type == "string"

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid type"):
            EnvVar(name="FOO", type="list")

    def test_invalid_pattern_raises(self):
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            EnvVar(name="FOO", pattern="[invalid")

    def test_valid_pattern_accepted(self):
        var = EnvVar(name="FOO", pattern="^https?://")
        assert var.pattern == "^https?://"

    def test_all_valid_types_accepted(self):
        for t in VALID_TYPES:
            var = EnvVar(name="FOO", type=t)
            assert var.type == t


class TestSchema:
    def test_from_dict_parses_correctly(self):
        data = {
            "name": "test-app",
            "version": "2.0",
            "variables": [
                {"name": "SECRET", "type": "string", "required": True}
            ],
        }
        schema = Schema.from_dict(data)
        assert schema.name == "test-app"
        assert schema.version == "2.0"
        assert len(schema.variables) == 1
        assert schema.variables[0].name == "SECRET"

    def test_from_dict_defaults_version(self):
        schema = Schema.from_dict({"name": "app", "variables": []})
        assert schema.version == "1.0"

    def test_from_json(self):
        payload = json.dumps({
            "name": "json-app",
            "variables": [{"name": "KEY", "type": "string"}]
        })
        schema = Schema.from_json(payload)
        assert schema.name == "json-app"
        assert schema.variables[0].name == "KEY"

    def test_from_file(self):
        schema = Schema.from_file(SAMPLE_SCHEMA_PATH)
        assert schema.name == "my-app"
        assert len(schema.variables) == 5
        names = [v.name for v in schema.variables]
        assert "DATABASE_URL" in names
        assert "PORT" in names

    def test_to_dict_round_trip(self):
        schema = Schema.from_file(SAMPLE_SCHEMA_PATH)
        d = schema.to_dict()
        restored = Schema.from_dict(d)
        assert restored.name == schema.name
        assert len(restored.variables) == len(schema.variables)

    def test_variable_with_allowed_values(self):
        schema = Schema.from_file(SAMPLE_SCHEMA_PATH)
        app_env = next(v for v in schema.variables if v.name == "APP_ENV")
        assert app_env.allowed_values == ["development", "staging", "production"]

    def test_variable_with_pattern(self):
        schema = Schema.from_file(SAMPLE_SCHEMA_PATH)
        db_url = next(v for v in schema.variables if v.name == "DATABASE_URL")
        assert db_url.pattern == "^postgres://"
