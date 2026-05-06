"""Tests for envforge.merger."""

import pytest

from envforge.merger import MergeResult, merge_envs, merge_many


BASE = {"APP_ENV": "development", "DB_HOST": "localhost", "SECRET": "base_secret"}
OVERLAY = {"APP_ENV": "production", "DB_HOST": "db.prod", "NEW_KEY": "new_value"}


class TestMergeEnvs:
    def test_overlay_overrides_base_values(self):
        result = merge_envs(BASE, OVERLAY)
        assert result.merged["APP_ENV"] == "production"
        assert result.merged["DB_HOST"] == "db.prod"

    def test_base_keys_not_in_overlay_are_kept(self):
        result = merge_envs(BASE, OVERLAY)
        assert "SECRET" in result.merged
        assert result.merged["SECRET"] == "base_secret"

    def test_new_keys_in_overlay_are_added(self):
        result = merge_envs(BASE, OVERLAY)
        assert "NEW_KEY" in result.merged
        assert "NEW_KEY" in result.added

    def test_overrides_dict_contains_changed_keys(self):
        result = merge_envs(BASE, OVERLAY)
        assert "APP_ENV" in result.overrides
        assert result.overrides["APP_ENV"] == "production"

    def test_unchanged_keys_not_in_overrides(self):
        result = merge_envs(BASE, {"APP_ENV": "development"})  # same value
        assert "APP_ENV" not in result.overrides

    def test_remove_missing_drops_base_only_keys(self):
        result = merge_envs(BASE, OVERLAY, remove_missing=True)
        assert "SECRET" not in result.merged
        assert "SECRET" in result.removed

    def test_remove_missing_false_keeps_base_keys(self):
        result = merge_envs(BASE, OVERLAY, remove_missing=False)
        assert "SECRET" in result.merged
        assert result.removed == []

    def test_empty_overlay_returns_base_unchanged(self):
        result = merge_envs(BASE, {})
        assert result.merged == BASE
        assert not result.has_changes

    def test_empty_base_returns_overlay_as_added(self):
        result = merge_envs({}, OVERLAY)
        assert set(result.added) == set(OVERLAY.keys())
        assert result.merged == OVERLAY


class TestMergeMany:
    def test_merges_three_layers(self):
        a = {"KEY": "a", "ONLY_A": "1"}
        b = {"KEY": "b", "ONLY_B": "2"}
        c = {"KEY": "c", "ONLY_C": "3"}
        result = merge_many([a, b, c])
        assert result.merged["KEY"] == "c"
        assert "ONLY_A" in result.merged
        assert "ONLY_B" in result.merged
        assert "ONLY_C" in result.merged

    def test_empty_list_returns_empty_result(self):
        result = merge_many([])
        assert result.merged == {}
        assert not result.has_changes

    def test_single_env_returned_unchanged(self):
        result = merge_many([BASE])
        assert result.merged == BASE


class TestMergeResult:
    def test_has_changes_true_when_overrides(self):
        r = MergeResult(overrides={"K": "v"})
        assert r.has_changes

    def test_has_changes_false_when_empty(self):
        r = MergeResult()
        assert not r.has_changes

    def test_summary_no_changes(self):
        r = MergeResult()
        assert r.summary() == "No changes."

    def test_summary_lists_all_change_types(self):
        r = MergeResult(
            overrides={"A": "x"},
            added=["B"],
            removed=["C"],
        )
        summary = r.summary()
        assert "Added" in summary
        assert "Changed" in summary
        assert "Removed" in summary
