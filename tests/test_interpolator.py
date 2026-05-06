"""Tests for envforge.interpolator."""

import pytest

from envforge.interpolator import InterpolationResult, interpolate_env


class TestInterpolateEnv:
    def test_plain_values_are_unchanged(self):
        env = {"HOST": "localhost", "PORT": "5432"}
        result = interpolate_env(env)
        assert result.resolved["HOST"] == "localhost"
        assert result.resolved["PORT"] == "5432"
        assert not result.has_unresolved

    def test_curly_brace_reference_resolved(self):
        env = {"BASE": "http://example.com", "URL": "${BASE}/api"}
        result = interpolate_env(env)
        assert result.resolved["URL"] == "http://example.com/api"

    def test_bare_dollar_reference_resolved(self):
        env = {"NAME": "world", "GREETING": "hello $NAME"}
        result = interpolate_env(env)
        assert result.resolved["GREETING"] == "hello world"

    def test_chained_references_resolved(self):
        env = {"A": "foo", "B": "${A}_bar", "C": "${B}_baz"}
        result = interpolate_env(env)
        assert result.resolved["C"] == "foo_bar_baz"

    def test_missing_reference_left_unresolved(self):
        env = {"URL": "${MISSING}/path"}
        result = interpolate_env(env)
        assert result.has_unresolved
        assert "URL" in result.unresolved

    def test_circular_reference_detected(self):
        env = {"A": "${B}", "B": "${A}"}
        result = interpolate_env(env)
        # At least one of the two keys must end up unresolved due to circular ref
        assert result.has_unresolved

    def test_multiple_references_in_one_value(self):
        env = {"PROTO": "https", "HOST": "example.com", "URL": "${PROTO}://${HOST}"}
        result = interpolate_env(env)
        assert result.resolved["URL"] == "https://example.com"

    def test_empty_env_returns_empty_result(self):
        result = interpolate_env({})
        assert result.resolved == {}
        assert result.unresolved == {}
        assert not result.has_unresolved

    def test_summary_no_unresolved(self):
        env = {"KEY": "value"}
        result = interpolate_env(env)
        summary = result.summary()
        assert "Resolved: 1" in summary
        assert "Unresolved" not in summary

    def test_summary_with_unresolved(self):
        env = {"KEY": "${MISSING}"}
        result = interpolate_env(env)
        summary = result.summary()
        assert "Unresolved" in summary
        assert "KEY" in summary

    def test_self_reference_detected(self):
        env = {"LOOP": "${LOOP}"}
        result = interpolate_env(env)
        assert result.has_unresolved
