"""Tests for envforge.transformer module."""

import pytest
from envforge.transformer import transform_env, TransformResult
from envforge.schema import Schema, EnvVar


@pytest.fixture
def simple_schema():
    return Schema(vars={
        "APP_ENV": EnvVar(name="APP_ENV", type="string", metadata={"transform": "uppercase"}),
        "APP_NAME": EnvVar(name="APP_NAME", type="string", metadata={"transform": "lowercase"}),
        "SECRET_KEY": EnvVar(name="SECRET_KEY", type="string", metadata={"transform": "strip"}),
        "DEBUG": EnvVar(name="DEBUG", type="string", metadata={"transform": "boolean_normalize"}),
        "TITLE": EnvVar(name="TITLE", type="string", metadata={"transform": "trim_quotes"}),
        "PORT": EnvVar(name="PORT", type="string"),
    })


class TestTransformEnv:
    def test_returns_transform_result(self, simple_schema):
        result = transform_env({"APP_ENV": "production"}, simple_schema)
        assert isinstance(result, TransformResult)

    def test_uppercase_transform(self, simple_schema):
        result = transform_env({"APP_ENV": "production"}, simple_schema)
        assert result.transformed["APP_ENV"] == "PRODUCTION"

    def test_lowercase_transform(self, simple_schema):
        result = transform_env({"APP_NAME": "MyApp"}, simple_schema)
        assert result.transformed["APP_NAME"] == "myapp"

    def test_strip_transform(self, simple_schema):
        result = transform_env({"SECRET_KEY": "  abc123  "}, simple_schema)
        assert result.transformed["SECRET_KEY"] == "abc123"

    def test_boolean_normalize_true_variants(self, simple_schema):
        for val in ("1", "yes", "true", "on", "YES", "True"):
            result = transform_env({"DEBUG": val}, simple_schema)
            assert result.transformed["DEBUG"] == "true", f"Failed for: {val}"

    def test_boolean_normalize_false_variants(self, simple_schema):
        for val in ("0", "no", "false", "off"):
            result = transform_env({"DEBUG": val}, simple_schema)
            assert result.transformed["DEBUG"] == "false", f"Failed for: {val}"

    def test_trim_quotes_transform(self, simple_schema):
        result = transform_env({"TITLE": '"Hello World"'}, simple_schema)
        assert result.transformed["TITLE"] == "Hello World"

    def test_no_schema_returns_unchanged(self):
        env = {"KEY": "value"}
        result = transform_env(env, schema=None)
        assert result.transformed == env
        assert not result.has_changes

    def test_key_without_transform_is_unchanged(self, simple_schema):
        result = transform_env({"PORT": "8080"}, simple_schema)
        assert result.transformed["PORT"] == "8080"
        assert not result.has_changes

    def test_unknown_transform_adds_error(self):
        schema = Schema(vars={
            "X": EnvVar(name="X", type="string", metadata={"transform": "explode"})
        })
        result = transform_env({"X": "val"}, schema)
        assert result.has_errors
        assert any("explode" in e for e in result.errors)

    def test_changes_recorded(self, simple_schema):
        result = transform_env({"APP_ENV": "dev"}, simple_schema)
        assert result.has_changes
        assert any("APP_ENV" in c for c in result.changes)

    def test_original_is_preserved(self, simple_schema):
        result = transform_env({"APP_ENV": "dev"}, simple_schema)
        assert result.original["APP_ENV"] == "dev"
        assert result.transformed["APP_ENV"] == "DEV"

    def test_summary_output(self, simple_schema):
        result = transform_env({"APP_ENV": "dev"}, simple_schema)
        summary = result.summary()
        assert "Transformed" in summary
