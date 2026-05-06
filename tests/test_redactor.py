"""Tests for envforge.redactor."""

from __future__ import annotations

import pytest

from envforge.redactor import DEFAULT_MASK, RedactResult, redact_env
from envforge.schema import EnvVar, Schema


@pytest.fixture
def simple_schema() -> Schema:
    return Schema(
        vars={
            "APP_NAME": EnvVar(name="APP_NAME", required=True),
            "DB_PASSWORD": EnvVar(name="DB_PASSWORD", required=True, sensitive=True),
            "PORT": EnvVar(name="PORT", required=False),
        }
    )


class TestRedactEnv:
    def test_non_sensitive_keys_unchanged(self):
        env = {"APP_NAME": "myapp", "PORT": "8080"}
        result = redact_env(env)
        assert result.redacted["APP_NAME"] == "myapp"
        assert result.redacted["PORT"] == "8080"

    def test_default_pattern_masks_password(self):
        env = {"DB_PASSWORD": "supersecret"}
        result = redact_env(env)
        assert result.redacted["DB_PASSWORD"] == DEFAULT_MASK

    def test_default_pattern_masks_token(self):
        env = {"API_TOKEN": "abc123"}
        result = redact_env(env)
        assert result.redacted["API_TOKEN"] == DEFAULT_MASK

    def test_default_pattern_masks_secret(self):
        env = {"APP_SECRET": "xyz"}
        result = redact_env(env)
        assert result.redacted["APP_SECRET"] == DEFAULT_MASK

    def test_original_is_unchanged(self):
        env = {"DB_PASSWORD": "supersecret"}
        result = redact_env(env)
        assert result.original["DB_PASSWORD"] == "supersecret"

    def test_redacted_keys_listed(self):
        env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
        result = redact_env(env)
        assert "DB_PASSWORD" in result.redacted_keys
        assert "APP_NAME" not in result.redacted_keys

    def test_has_redactions_true(self):
        env = {"API_KEY": "key123"}
        result = redact_env(env)
        assert result.has_redactions is True

    def test_has_redactions_false(self):
        env = {"APP_NAME": "myapp"}
        result = redact_env(env)
        assert result.has_redactions is False

    def test_custom_mask_applied(self):
        env = {"API_KEY": "key123"}
        result = redact_env(env, mask="[HIDDEN]")
        assert result.redacted["API_KEY"] == "[HIDDEN]"

    def test_extra_patterns_respected(self):
        env = {"MY_CERT": "certdata"}
        result = redact_env(env, extra_patterns=["CERT"])
        assert result.redacted["MY_CERT"] == DEFAULT_MASK

    def test_schema_sensitive_flag_triggers_redaction(self, simple_schema):
        env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
        result = redact_env(env, schema=simple_schema)
        assert result.redacted["DB_PASSWORD"] == DEFAULT_MASK
        assert result.redacted["APP_NAME"] == "myapp"

    def test_summary_with_redactions(self):
        env = {"API_KEY": "key"}
        result = redact_env(env)
        assert "1" in result.summary()
        assert "API_KEY" in result.summary()

    def test_summary_without_redactions(self):
        env = {"APP_NAME": "myapp"}
        result = redact_env(env)
        assert result.summary() == "No sensitive keys redacted."
