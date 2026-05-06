"""Tests for envforge.auditor module."""

import pytest
from envforge.auditor import audit_env, AuditReport, AuditEntry
from envforge.schema import Schema, EnvVar


@pytest.fixture
def simple_schema():
    return Schema(variables=[
        EnvVar(name="APP_ENV", required=True, type="string"),
        EnvVar(name="PORT", required=False, type="integer", default="8080"),
        EnvVar(name="DEBUG", required=False, type="boolean"),
        EnvVar(name="API_KEY", required=True, type="string", pattern=r"^[A-Z0-9]{16}$"),
    ])


class TestAuditEnv:
    def test_all_valid_returns_pass(self, simple_schema):
        env = {"APP_ENV": "production", "PORT": "9000", "API_KEY": "ABCD1234ABCD1234"}
        report = audit_env(env, simple_schema)
        assert report.passed

    def test_missing_required_key_fails(self, simple_schema):
        env = {"PORT": "9000", "API_KEY": "ABCD1234ABCD1234"}
        report = audit_env(env, simple_schema)
        assert not report.passed
        missing = report.by_status("missing")
        assert any(e.key == "APP_ENV" for e in missing)

    def test_extra_key_detected(self, simple_schema):
        env = {"APP_ENV": "dev", "API_KEY": "ABCD1234ABCD1234", "UNKNOWN_VAR": "foo"}
        report = audit_env(env, simple_schema)
        extras = report.by_status("extra")
        assert any(e.key == "UNKNOWN_VAR" for e in extras)

    def test_default_used_when_optional_absent(self, simple_schema):
        env = {"APP_ENV": "dev", "API_KEY": "ABCD1234ABCD1234"}
        report = audit_env(env, simple_schema)
        defaults = report.by_status("default_used")
        assert any(e.key == "PORT" for e in defaults)

    def test_invalid_pattern_flagged(self, simple_schema):
        env = {"APP_ENV": "dev", "API_KEY": "bad-key"}
        report = audit_env(env, simple_schema)
        invalid = report.by_status("invalid")
        assert any(e.key == "API_KEY" for e in invalid)

    def test_summary_contains_status_counts(self, simple_schema):
        env = {"APP_ENV": "dev", "API_KEY": "ABCD1234ABCD1234"}
        report = audit_env(env, simple_schema)
        summary = report.summary()
        assert "Audit" in summary

    def test_audit_entry_str(self):
        entry = AuditEntry(key="FOO", status="missing", message="required variable not set")
        assert "[MISSING]" in str(entry)
        assert "FOO" in str(entry)

    def test_empty_env_against_empty_schema(self):
        schema = Schema(variables=[])
        report = audit_env({}, schema)
        assert report.passed
        assert report.entries == []

    def test_optional_not_set_no_default_is_ok(self, simple_schema):
        env = {"APP_ENV": "dev", "API_KEY": "ABCD1234ABCD1234"}
        report = audit_env(env, simple_schema)
        ok_entries = report.by_status("ok")
        assert any(e.key == "DEBUG" for e in ok_entries)
