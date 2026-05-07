"""Tests for envforge.renamer"""
import pytest
from envforge.renamer import rename_env, RenameResult, RenameEntry


BASE_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "s3cr3t",
}


class TestRenameEnv:
    def test_returns_rename_result(self):
        result = rename_env(BASE_ENV, {})
        assert isinstance(result, RenameResult)

    def test_no_renames_env_unchanged(self):
        result = rename_env(BASE_ENV, {})
        assert result.env == BASE_ENV
        assert not result.has_changes()

    def test_single_key_renamed(self):
        result = rename_env(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
        assert "DATABASE_HOST" in result.env
        assert "DB_HOST" not in result.env
        assert result.env["DATABASE_HOST"] == "localhost"

    def test_renamed_entry_recorded(self):
        result = rename_env(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
        assert len(result.renamed) == 1
        entry = result.renamed[0]
        assert isinstance(entry, RenameEntry)
        assert entry.old_key == "DB_HOST"
        assert entry.new_key == "DATABASE_HOST"
        assert entry.value == "localhost"

    def test_multiple_keys_renamed(self):
        result = rename_env(BASE_ENV, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
        assert "DATABASE_HOST" in result.env
        assert "DATABASE_PORT" in result.env
        assert len(result.renamed) == 2

    def test_missing_key_is_skipped(self):
        result = rename_env(BASE_ENV, {"NONEXISTENT": "NEW_KEY"})
        assert "NONEXISTENT" not in result.env
        assert "NEW_KEY" not in result.env
        assert "NONEXISTENT" in result.skipped

    def test_conflict_without_overwrite_records_error(self):
        env = {"OLD_KEY": "v1", "NEW_KEY": "v2"}
        result = rename_env(env, {"OLD_KEY": "NEW_KEY"}, overwrite=False)
        assert len(result.errors) == 1
        assert "OLD_KEY" in result.errors[0]
        assert result.env["OLD_KEY"] == "v1"  # original unchanged

    def test_conflict_with_overwrite_succeeds(self):
        env = {"OLD_KEY": "v1", "NEW_KEY": "v2"}
        result = rename_env(env, {"OLD_KEY": "NEW_KEY"}, overwrite=True)
        assert result.env["NEW_KEY"] == "v1"
        assert "OLD_KEY" not in result.env
        assert not result.errors

    def test_original_env_not_mutated(self):
        original = dict(BASE_ENV)
        rename_env(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
        assert BASE_ENV == original

    def test_has_changes_false_when_no_renames(self):
        result = rename_env(BASE_ENV, {"MISSING": "WHATEVER"})
        assert not result.has_changes()

    def test_summary_contains_counts(self):
        result = rename_env(BASE_ENV, {"DB_HOST": "DATABASE_HOST", "MISSING": "X"})
        summary = result.summary()
        assert "1 renamed" in summary
        assert "skipped" in summary

    def test_rename_entry_str(self):
        entry = RenameEntry(old_key="A", new_key="B", value="val")
        assert "A" in str(entry)
        assert "B" in str(entry)
