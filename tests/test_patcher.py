"""Tests for envforge.patcher module."""
import pytest
from envforge.patcher import patch_env, PatchResult, PatchEntry


class TestPatchEnv:
    def _base_env(self):
        return {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}

    def test_returns_patch_result(self):
        result = patch_env(self._base_env())
        assert isinstance(result, PatchResult)

    def test_no_ops_env_unchanged(self):
        env = self._base_env()
        result = patch_env(env)
        assert result.env == env
        assert not result.has_changes

    def test_set_new_key_adds_to_env(self):
        result = patch_env(self._base_env(), set_pairs=[("NEW_KEY", "new_val")])
        assert result.env["NEW_KEY"] == "new_val"
        assert result.has_changes

    def test_set_existing_key_updates_value(self):
        result = patch_env(self._base_env(), set_pairs=[("PORT", "9999")])
        assert result.env["PORT"] == "9999"

    def test_set_records_old_value_on_update(self):
        result = patch_env(self._base_env(), set_pairs=[("PORT", "9999")])
        entry = next(c for c in result.changes if c.key == "PORT")
        assert entry.old_value == "5432"
        assert entry.new_value == "9999"

    def test_set_new_key_has_none_old_value(self):
        result = patch_env(self._base_env(), set_pairs=[("BRAND_NEW", "x")])
        entry = next(c for c in result.changes if c.key == "BRAND_NEW")
        assert entry.old_value is None

    def test_delete_existing_key_removes_it(self):
        result = patch_env(self._base_env(), delete_keys=["DEBUG"])
        assert "DEBUG" not in result.env
        assert result.has_changes

    def test_delete_nonexistent_key_records_error(self):
        result = patch_env(self._base_env(), delete_keys=["MISSING"])
        assert result.has_errors
        assert any("MISSING" in e for e in result.errors)

    def test_delete_nonexistent_key_env_unchanged(self):
        env = self._base_env()
        result = patch_env(env, delete_keys=["MISSING"])
        assert result.env == env

    def test_empty_key_in_set_records_error(self):
        result = patch_env(self._base_env(), set_pairs=[("  ", "val"), ("", "val2")])
        assert result.has_errors

    def test_combined_set_and_delete(self):
        result = patch_env(
            self._base_env(),
            set_pairs=[("PORT", "8080"), ("LOG_LEVEL", "info")],
            delete_keys=["DEBUG"],
        )
        assert result.env["PORT"] == "8080"
        assert result.env["LOG_LEVEL"] == "info"
        assert "DEBUG" not in result.env
        assert len(result.changes) == 3

    def test_original_env_not_mutated(self):
        env = self._base_env()
        original_copy = dict(env)
        patch_env(env, set_pairs=[("PORT", "0")], delete_keys=["HOST"])
        assert env == original_copy

    def test_summary_no_changes(self):
        result = patch_env(self._base_env())
        assert "No changes" in result.summary()

    def test_summary_with_changes(self):
        result = patch_env(self._base_env(), set_pairs=[("PORT", "9000")], delete_keys=["DEBUG"])
        summary = result.summary()
        assert "PORT" in summary
        assert "DEBUG" in summary

    def test_patch_entry_str_add(self):
        entry = PatchEntry(key="FOO", operation="set", old_value=None, new_value="bar")
        assert "ADD" in str(entry)
        assert "FOO" in str(entry)

    def test_patch_entry_str_delete(self):
        entry = PatchEntry(key="FOO", operation="delete", old_value="old")
        assert "DELETE" in str(entry)
