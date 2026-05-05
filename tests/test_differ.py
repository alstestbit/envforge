"""Tests for envforge.differ module."""
import pytest
from envforge.differ import diff_env_against_schema, diff_two_envs, DiffEntry, DiffResult
from envforge.schema import Schema


@pytest.fixture
def simple_schema():
    return Schema.from_dict({
        "variables": [
            {"name": "APP_NAME", "type": "string", "required": True},
            {"name": "PORT", "type": "int", "required": True},
            {"name": "DEBUG", "type": "bool", "required": False, "default": "false"},
        ]
    })


class TestDiffEnvAgainstSchema:
    def test_no_differences(self, simple_schema):
        env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "true"}
        result = diff_env_against_schema(env, simple_schema)
        assert not result.has_differences

    def test_missing_key_detected(self, simple_schema):
        env = {"APP_NAME": "myapp"}
        result = diff_env_against_schema(env, simple_schema)
        keys = [e.key for e in result.entries]
        assert "PORT" in keys
        assert "DEBUG" in keys

    def test_extra_key_detected(self, simple_schema):
        env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "true", "UNKNOWN": "val"}
        result = diff_env_against_schema(env, simple_schema)
        extra = [e for e in result.entries if e.status == "extra"]
        assert any(e.key == "UNKNOWN" for e in extra)

    def test_int_type_mismatch(self, simple_schema):
        env = {"APP_NAME": "myapp", "PORT": "not_an_int", "DEBUG": "false"}
        result = diff_env_against_schema(env, simple_schema)
        mismatches = [e for e in result.entries if e.status == "type_mismatch"]
        assert any(e.key == "PORT" for e in mismatches)

    def test_bool_type_mismatch(self, simple_schema):
        env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "yes"}
        result = diff_env_against_schema(env, simple_schema)
        mismatches = [e for e in result.entries if e.status == "type_mismatch"]
        assert any(e.key == "DEBUG" for e in mismatches)

    def test_has_differences_true(self, simple_schema):
        env = {}
        result = diff_env_against_schema(env, simple_schema)
        assert result.has_differences

    def test_summary_no_diff(self, simple_schema):
        env = {"APP_NAME": "x", "PORT": "1", "DEBUG": "true"}
        result = diff_env_against_schema(env, simple_schema)
        assert result.summary() == "No differences found."

    def test_summary_with_diff(self, simple_schema):
        env = {}
        result = diff_env_against_schema(env, simple_schema)
        summary = result.summary()
        assert "difference" in summary


class TestDiffTwoEnvs:
    def test_identical_envs(self):
        base = {"A": "1", "B": "2"}
        result = diff_two_envs(base, base)
        assert not result.has_differences

    def test_value_changed(self):
        base = {"A": "1"}
        other = {"A": "2"}
        result = diff_two_envs(base, other)
        assert result.has_differences
        assert result.entries[0].status == "default_changed"

    def test_key_missing_in_other(self):
        base = {"A": "1", "B": "2"}
        other = {"A": "1"}
        result = diff_two_envs(base, other)
        extras = [e for e in result.entries if e.status == "extra"]
        assert any(e.key == "B" for e in extras)

    def test_key_only_in_other(self):
        base = {"A": "1"}
        other = {"A": "1", "C": "3"}
        result = diff_two_envs(base, other)
        missing = [e for e in result.entries if e.status == "missing"]
        assert any(e.key == "C" for e in missing)


class TestDiffEntry:
    def test_str_missing(self):
        e = DiffEntry(key="FOO", status="missing", expected="string")
        assert "missing" in str(e)
        assert "FOO" in str(e)

    def test_str_extra(self):
        e = DiffEntry(key="BAR", status="extra")
        assert "+" in str(e)

    def test_str_type_mismatch(self):
        e = DiffEntry(key="PORT", status="type_mismatch", expected="int", actual="abc")
        assert "type mismatch" in str(e)
