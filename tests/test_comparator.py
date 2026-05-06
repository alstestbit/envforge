"""Tests for envforge.comparator module."""

import pytest
from envforge.comparator import compare_envs, CompareResult, CompareEntry


LEFT = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "DB_HOST": "localhost",
}

RIGHT = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "API_KEY": "secret",
}


class TestCompareEnvs:
    def test_returns_compare_result(self):
        result = compare_envs(LEFT, RIGHT)
        assert isinstance(result, CompareResult)

    def test_no_differences_on_identical_envs(self):
        result = compare_envs({"A": "1"}, {"A": "1"})
        assert not result.has_differences

    def test_changed_key_detected(self):
        result = compare_envs(LEFT, RIGHT)
        keys = [e.key for e in result.changed]
        assert "DEBUG" in keys

    def test_changed_entry_has_correct_values(self):
        result = compare_envs(LEFT, RIGHT)
        entry = next(e for e in result.changed if e.key == "DEBUG")
        assert entry.left_value == "true"
        assert entry.right_value == "false"
        assert entry.status == "changed"

    def test_left_only_key_detected(self):
        result = compare_envs(LEFT, RIGHT)
        keys = [e.key for e in result.left_only]
        assert "DB_HOST" in keys

    def test_right_only_key_detected(self):
        result = compare_envs(LEFT, RIGHT)
        keys = [e.key for e in result.right_only]
        assert "API_KEY" in keys

    def test_shared_unchanged_key_not_in_entries(self):
        result = compare_envs(LEFT, RIGHT)
        keys = [e.key for e in result.entries]
        assert "APP_NAME" not in keys

    def test_labels_stored_on_result(self):
        result = compare_envs(LEFT, RIGHT, left_label="prod", right_label="staging")
        assert result.left_label == "prod"
        assert result.right_label == "staging"

    def test_has_differences_true_when_diffs_exist(self):
        result = compare_envs(LEFT, RIGHT)
        assert result.has_differences

    def test_summary_no_diff(self):
        result = compare_envs({"X": "1"}, {"X": "1"}, "a", "b")
        assert "No differences" in result.summary()

    def test_summary_with_diffs(self):
        result = compare_envs(LEFT, RIGHT, "prod", "dev")
        summary = result.summary()
        assert "prod" in summary
        assert "dev" in summary
        assert "Changed" in summary

    def test_str_changed_entry(self):
        entry = CompareEntry(key="FOO", left_value="a", right_value="b", status="changed")
        assert "~" in str(entry)
        assert "FOO" in str(entry)

    def test_str_left_only_entry(self):
        entry = CompareEntry(key="BAR", left_value="x", right_value=None, status="left_only")
        assert "-" in str(entry)

    def test_str_right_only_entry(self):
        entry = CompareEntry(key="BAZ", left_value=None, right_value="y", status="right_only")
        assert "+" in str(entry)

    def test_empty_envs_produce_no_differences(self):
        result = compare_envs({}, {})
        assert not result.has_differences
        assert result.entries == []
