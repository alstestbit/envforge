"""Tests for envforge.linter."""

import pytest
from envforge.linter import lint_env, LintIssue, LintReport
from envforge.schema import Schema, EnvVar


@pytest.fixture
def simple_schema() -> Schema:
    return Schema(variables=[
        EnvVar(name="APP_ENV", required=True, type="string"),
        EnvVar(name="PORT", required=False, type="integer", default="8080"),
        EnvVar(name="DEBUG", required=False, type="boolean", default="false"),
    ])


class TestLintEnv:
    def test_clean_env_produces_no_issues(self, simple_schema):
        env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}
        report = lint_env(env, simple_schema)
        assert report.issues == []
        assert report.passed is True

    def test_lowercase_key_raises_error(self, simple_schema):
        env = {"app_env": "production"}
        report = lint_env(env, simple_schema)
        codes = [i.code for i in report.issues]
        assert "E001" in codes
        assert report.passed is False

    def test_required_empty_value_warns(self, simple_schema):
        env = {"APP_ENV": "", "PORT": "8080"}
        report = lint_env(env, simple_schema)
        codes = [i.code for i in report.issues]
        assert "W001" in codes

    def test_unknown_key_warns(self, simple_schema):
        env = {"APP_ENV": "dev", "UNKNOWN_KEY": "value"}
        report = lint_env(env, simple_schema)
        codes = [i.code for i in report.issues]
        assert "W002" in codes

    def test_unresolved_placeholder_warns(self, simple_schema):
        env = {"APP_ENV": "${SOME_VAR}"}
        report = lint_env(env, simple_schema)
        codes = [i.code for i in report.issues]
        assert "W003" in codes

    def test_passed_false_when_errors_present(self, simple_schema):
        env = {"lowercase_key": "value"}
        report = lint_env(env, simple_schema)
        assert report.passed is False

    def test_passed_true_with_only_warnings(self, simple_schema):
        env = {"APP_ENV": "dev", "EXTRA": "value"}
        report = lint_env(env, simple_schema)
        assert report.passed is True
        assert len(report.warnings) >= 1

    def test_summary_format(self, simple_schema):
        env = {"APP_ENV": "dev"}
        report = lint_env(env, simple_schema)
        summary = report.summary()
        assert "error" in summary
        assert "warning" in summary
        assert "PASSED" in summary or "FAILED" in summary

    def test_lint_issue_str(self):
        issue = LintIssue(key="foo", code="E001", message="bad key", severity="error")
        result = str(issue)
        assert "ERROR" in result
        assert "E001" in result
        assert "foo" in result
