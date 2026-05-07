"""Tests for envforge.trimmer."""

import pytest
from envforge.trimmer import trim_env, TrimResult, TrimEntry


class TestTrimEnv:
    def test_returns_trim_result(self):
        result = trim_env({"KEY": "value"})
        assert isinstance(result, TrimResult)

    def test_clean_env_has_no_changes(self):
        result = trim_env({"KEY": "value", "OTHER": "clean"})
        assert not result.has_changes()

    def test_trailing_whitespace_removed(self):
        result = trim_env({"KEY": "value   "})
        assert result.env["KEY"] == "value"

    def test_leading_whitespace_removed(self):
        result = trim_env({"KEY": "   value"})
        assert result.env["KEY"] == "value"

    def test_both_sides_trimmed(self):
        result = trim_env({"KEY": "  hello world  "})
        assert result.env["KEY"] == "hello world"

    def test_change_recorded_for_trimmed_value(self):
        result = trim_env({"KEY": "  val  "})
        assert result.has_changes()
        assert len(result.changes) == 1
        entry = result.changes[0]
        assert isinstance(entry, TrimEntry)
        assert entry.key == "KEY"
        assert entry.original == "  val  "
        assert entry.trimmed == "val"

    def test_multiple_changes_recorded(self):
        env = {"A": " one ", "B": "two", "C": "three  "}
        result = trim_env(env)
        assert len(result.changes) == 2
        changed_keys = {e.key for e in result.changes}
        assert changed_keys == {"A", "C"}

    def test_empty_value_stays_empty(self):
        result = trim_env({"KEY": ""})
        assert result.env["KEY"] == ""
        assert not result.has_changes()

    def test_whitespace_only_value_becomes_empty(self):
        result = trim_env({"KEY": "   "})
        assert result.env["KEY"] == ""
        assert result.has_changes()

    def test_trim_keys_false_by_default(self):
        result = trim_env({" KEY ": "value"})
        assert " KEY " in result.env

    def test_trim_keys_strips_key_whitespace(self):
        result = trim_env({" KEY ": "value"}, trim_keys=True)
        assert "KEY" in result.env
        assert " KEY " not in result.env

    def test_summary_no_changes(self):
        result = trim_env({"KEY": "clean"})
        assert result.summary() == "No values were trimmed."

    def test_summary_with_changes(self):
        result = trim_env({"KEY": " val "})
        summary = result.summary()
        assert "Trimmed 1 value(s)" in summary
        assert "KEY" in summary

    def test_original_env_not_mutated(self):
        original = {"KEY": "  value  "}
        trim_env(original)
        assert original["KEY"] == "  value  "
