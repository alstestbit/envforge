"""Tests for envforge.scoper."""
import pytest
from envforge.scoper import scope_env, ScopeResult, ScopeEntry


SAMPLE_ENV = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PORT": "5432",
    "LOG_LEVEL": "info",
}


class TestScopeEnv:
    def test_returns_scope_result(self):
        result = scope_env(SAMPLE_ENV, prefix="APP_")
        assert isinstance(result, ScopeResult)

    def test_matching_keys_extracted(self):
        result = scope_env(SAMPLE_ENV, prefix="APP_")
        assert result.has_matches
        assert len(result.entries) == 2

    def test_prefix_stripped_by_default(self):
        result = scope_env(SAMPLE_ENV, prefix="APP_")
        keys = [e.scoped_key for e in result.entries]
        assert "HOST" in keys
        assert "PORT" in keys

    def test_keep_prefix_preserves_original_key(self):
        result = scope_env(SAMPLE_ENV, prefix="APP_", strip_prefix=False)
        keys = [e.scoped_key for e in result.entries]
        assert "APP_HOST" in keys
        assert "APP_PORT" in keys

    def test_excluded_contains_non_matching_keys(self):
        result = scope_env(SAMPLE_ENV, prefix="APP_")
        assert "DB_HOST" in result.excluded
        assert "LOG_LEVEL" in result.excluded

    def test_scoped_env_dict_has_stripped_keys(self):
        result = scope_env(SAMPLE_ENV, prefix="APP_")
        scoped = result.scoped_env
        assert scoped["HOST"] == "localhost"
        assert scoped["PORT"] == "8080"

    def test_original_env_dict_has_full_keys(self):
        result = scope_env(SAMPLE_ENV, prefix="APP_", strip_prefix=False)
        orig = result.original_env
        assert orig["APP_HOST"] == "localhost"

    def test_no_matches_returns_empty_entries(self):
        result = scope_env(SAMPLE_ENV, prefix="REDIS_")
        assert not result.has_matches
        assert result.entries == []

    def test_case_insensitive_match(self):
        env = {"app_host": "localhost", "DB_HOST": "db.local"}
        result = scope_env(env, prefix="APP_", case_sensitive=False)
        assert result.has_matches
        assert len(result.entries) == 1

    def test_case_sensitive_no_match_on_lowercase(self):
        env = {"app_host": "localhost"}
        result = scope_env(env, prefix="APP_", case_sensitive=True)
        assert not result.has_matches

    def test_summary_string(self):
        result = scope_env(SAMPLE_ENV, prefix="APP_")
        summary = result.summary()
        assert "APP_" in summary
        assert "2 matched" in summary

    def test_scope_entry_str(self):
        entry = ScopeEntry(key="APP_HOST", scoped_key="HOST", value="localhost")
        assert "APP_HOST" in str(entry)
        assert "HOST=localhost" in str(entry)

    def test_empty_env_returns_no_matches(self):
        result = scope_env({}, prefix="APP_")
        assert not result.has_matches
        assert result.excluded == []
