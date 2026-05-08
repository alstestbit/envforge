"""Tests for envforge.pinner."""

import pytest
from envforge.schema import Schema, EnvVar
from envforge.pinner import pin_env, PinResult, PinEntry


@pytest.fixture
def simple_schema():
    return Schema(variables=[
        EnvVar(name="APP_HOST", default="localhost", required=True),
        EnvVar(name="APP_PORT", default="8080", required=True),
        EnvVar(name="DEBUG", default="false", required=False),
    ])


class TestPinEnv:
    def test_returns_pin_result(self, simple_schema):
        result = pin_env(simple_schema, {})
        assert isinstance(result, PinResult)

    def test_no_env_no_changes(self, simple_schema):
        result = pin_env(simple_schema, {})
        assert not result.has_changes
        assert result.entries == []

    def test_matching_default_not_marked_changed(self, simple_schema):
        result = pin_env(simple_schema, {"APP_HOST": "localhost"})
        assert len(result.entries) == 1
        assert not result.entries[0].changed

    def test_new_value_marks_changed(self, simple_schema):
        result = pin_env(simple_schema, {"APP_HOST": "prod.example.com"})
        assert result.has_changes
        assert "APP_HOST" in result.changed_keys

    def test_default_is_updated_on_schema(self, simple_schema):
        pin_env(simple_schema, {"APP_PORT": "9000"})
        var = next(v for v in simple_schema.variables if v.name == "APP_PORT")
        assert var.default == "9000"

    def test_old_default_recorded_in_entry(self, simple_schema):
        result = pin_env(simple_schema, {"APP_PORT": "9000"})
        entry = result.entries[0]
        assert entry.old_default == "8080"
        assert entry.new_default == "9000"

    def test_unknown_key_is_skipped(self, simple_schema):
        result = pin_env(simple_schema, {"UNKNOWN_KEY": "value"})
        assert "UNKNOWN_KEY" in result.skipped
        assert result.entries == []

    def test_multiple_keys_pinned(self, simple_schema):
        result = pin_env(simple_schema, {
            "APP_HOST": "prod.example.com",
            "APP_PORT": "443",
            "DEBUG": "false",
        })
        assert len(result.entries) == 3
        assert len(result.changed_keys) == 2

    def test_summary_reports_counts(self, simple_schema):
        result = pin_env(simple_schema, {
            "APP_HOST": "new.host",
            "EXTRA": "ignored",
        })
        summary = result.summary()
        assert "1/1" in summary
        assert "skipped" in summary

    def test_str_changed_entry(self, simple_schema):
        result = pin_env(simple_schema, {"APP_HOST": "new.host"})
        text = str(result.entries[0])
        assert "~" in text
        assert "APP_HOST" in text

    def test_str_unchanged_entry(self, simple_schema):
        result = pin_env(simple_schema, {"APP_HOST": "localhost"})
        text = str(result.entries[0])
        assert "=" in text
        assert "unchanged" in text
