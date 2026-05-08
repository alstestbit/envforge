"""Tests for envforge.flattener."""

import pytest
from envforge.flattener import flatten_env, FlattenResult, FlattenEntry


class TestFlattenEnv:
    def test_returns_flatten_result(self):
        result = flatten_env({})
        assert isinstance(result, FlattenResult)

    def test_empty_env_has_no_changes(self):
        result = flatten_env({})
        assert not result.has_changes()
        assert result.env == {}

    def test_plain_keys_unchanged(self):
        env = {"HOST": "localhost", "PORT": "5432"}
        result = flatten_env(env)
        assert not result.has_changes()
        assert result.env == env

    def test_double_underscore_replaced_with_dot(self):
        env = {"DB__HOST": "localhost"}
        result = flatten_env(env)
        assert "DB.HOST" in result.env
        assert result.env["DB.HOST"] == "localhost"

    def test_original_key_removed_after_flatten(self):
        env = {"DB__PORT": "5432"}
        result = flatten_env(env)
        assert "DB__PORT" not in result.env

    def test_multiple_separators_in_one_key(self):
        env = {"A__B__C": "val"}
        result = flatten_env(env)
        assert "A.B.C" in result.env

    def test_custom_separator(self):
        env = {"DB--HOST": "localhost"}
        result = flatten_env(env, separator="--")
        assert "DB.HOST" in result.env

    def test_custom_replacement(self):
        env = {"DB__HOST": "localhost"}
        result = flatten_env(env, replacement="_")
        assert "DB_HOST" in result.env

    def test_has_changes_true_when_keys_renamed(self):
        env = {"DB__HOST": "localhost"}
        result = flatten_env(env)
        assert result.has_changes()

    def test_changed_keys_lists_originals(self):
        env = {"DB__HOST": "localhost", "PORT": "5432"}
        result = flatten_env(env)
        assert result.changed_keys() == ["DB__HOST"]

    def test_summary_no_changes(self):
        result = flatten_env({"PORT": "5432"})
        assert "No keys" in result.summary()

    def test_summary_with_changes(self):
        result = flatten_env({"DB__HOST": "localhost"})
        assert "1 key(s) flattened" in result.summary()
        assert "DB__HOST" in result.summary()

    def test_prefix_filter_only_affects_matching_keys(self):
        env = {"DB__HOST": "localhost", "CACHE__HOST": "redis"}
        result = flatten_env(env, prefix_filter="DB")
        assert "DB.HOST" in result.env
        assert "CACHE__HOST" in result.env
        assert "CACHE.HOST" not in result.env

    def test_entry_str_unchanged(self):
        env = {"PORT": "5432"}
        result = flatten_env(env)
        assert "unchanged" in str(result.entries[0])

    def test_entry_str_changed(self):
        env = {"DB__HOST": "localhost"}
        result = flatten_env(env)
        entry = result.entries[0]
        assert "->" in str(entry)
        assert "DB.HOST" in str(entry)
