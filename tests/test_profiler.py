"""Tests for envforge.profiler."""
import pytest
from envforge.schema import Schema, EnvVar
from envforge.profiler import profile_envs, ProfileReport


@pytest.fixture
def simple_schema():
    return Schema(variables=[
        EnvVar(name="APP_ENV", required=True),
        EnvVar(name="DATABASE_URL", required=True),
        EnvVar(name="DEBUG", required=False, default="false"),
    ])


class TestProfileEnvs:
    def test_returns_profile_report(self, simple_schema):
        result = profile_envs(simple_schema, {})
        assert isinstance(result, ProfileReport)

    def test_all_passing_environments(self, simple_schema):
        envs = {
            "dev": {"APP_ENV": "dev", "DATABASE_URL": "sqlite:///dev.db"},
            "prod": {"APP_ENV": "prod", "DATABASE_URL": "postgres://prod"},
        }
        report = profile_envs(simple_schema, envs)
        assert set(report.passed()) == {"dev", "prod"}
        assert report.failed() == []

    def test_failing_environment_detected(self, simple_schema):
        envs = {
            "dev": {"APP_ENV": "dev", "DATABASE_URL": "sqlite:///dev.db"},
            "broken": {"APP_ENV": "staging"},
        }
        report = profile_envs(simple_schema, envs)
        assert "broken" in report.failed()
        assert "dev" in report.passed()

    def test_get_entry_by_name(self, simple_schema):
        envs = {"dev": {"APP_ENV": "dev", "DATABASE_URL": "sqlite:///dev.db"}}
        report = profile_envs(simple_schema, envs)
        entry = report.get("dev")
        assert entry is not None
        assert entry.environment == "dev"

    def test_get_missing_entry_returns_none(self, simple_schema):
        report = profile_envs(simple_schema, {})
        assert report.get("nonexistent") is None

    def test_summary_contains_environment_names(self, simple_schema):
        envs = {
            "dev": {"APP_ENV": "dev", "DATABASE_URL": "sqlite:///dev.db"},
            "prod": {"APP_ENV": "prod", "DATABASE_URL": "postgres://prod"},
        }
        report = profile_envs(simple_schema, envs)
        summary = report.summary()
        assert "dev" in summary
        assert "prod" in summary

    def test_entry_str_shows_pass(self, simple_schema):
        envs = {"dev": {"APP_ENV": "dev", "DATABASE_URL": "sqlite:///dev.db"}}
        report = profile_envs(simple_schema, envs)
        assert "PASS" in str(report.get("dev"))

    def test_entry_str_shows_fail(self, simple_schema):
        envs = {"bad": {}}
        report = profile_envs(simple_schema, envs)
        assert "FAIL" in str(report.get("bad"))

    def test_empty_envs_produces_empty_report(self, simple_schema):
        report = profile_envs(simple_schema, {})
        assert report.entries == []
        assert report.passed() == []
        assert report.failed() == []
