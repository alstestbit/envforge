"""Tests for envforge.sorter."""

import pytest

from envforge.schema import Schema
from envforge.sorter import SortResult, sort_env


@pytest.fixture
def simple_schema():
    return Schema.from_dict(
        {
            "variables": {
                "ZEBRA": {"required": True},
                "ALPHA": {"required": True},
                "MIDDLE": {"required": False, "default": "mid"},
            }
        }
    )


class TestSortEnv:
    def test_returns_sort_result(self):
        result = sort_env({"B": "2", "A": "1"})
        assert isinstance(result, SortResult)

    def test_alpha_order(self):
        env = {"ZEBRA": "z", "ALPHA": "a", "MIDDLE": "m"}
        result = sort_env(env, order="alpha")
        assert list(result.sorted_env.keys()) == ["ALPHA", "MIDDLE", "ZEBRA"]

    def test_alpha_desc_order(self):
        env = {"ZEBRA": "z", "ALPHA": "a", "MIDDLE": "m"}
        result = sort_env(env, order="alpha_desc")
        assert list(result.sorted_env.keys()) == ["ZEBRA", "MIDDLE", "ALPHA"]

    def test_schema_order_follows_definition(self, simple_schema):
        env = {"ALPHA": "a", "ZEBRA": "z", "MIDDLE": "m"}
        result = sort_env(env, order="schema", schema=simple_schema)
        assert list(result.sorted_env.keys()) == ["ZEBRA", "ALPHA", "MIDDLE"]

    def test_schema_order_appends_extra_keys_alphabetically(self, simple_schema):
        env = {"ALPHA": "a", "ZEBRA": "z", "MIDDLE": "m", "EXTRA_B": "b", "EXTRA_A": "a"}
        result = sort_env(env, order="schema", schema=simple_schema)
        keys = list(result.sorted_env.keys())
        assert keys[:3] == ["ZEBRA", "ALPHA", "MIDDLE"]
        assert keys[3:] == ["EXTRA_A", "EXTRA_B"]

    def test_schema_order_without_schema_raises(self):
        with pytest.raises(ValueError, match="Schema instance is required"):
            sort_env({"A": "1"}, order="schema")

    def test_unknown_order_raises(self):
        with pytest.raises(ValueError, match="Unknown sort order"):
            sort_env({"A": "1"}, order="random")

    def test_already_sorted_has_no_changes(self):
        env = {"ALPHA": "a", "MIDDLE": "m", "ZEBRA": "z"}
        result = sort_env(env, order="alpha")
        assert not result.has_changes

    def test_unsorted_has_changes(self):
        env = {"ZEBRA": "z", "ALPHA": "a"}
        result = sort_env(env, order="alpha")
        assert result.has_changes

    def test_values_are_preserved(self):
        env = {"B": "beta", "A": "alpha"}
        result = sort_env(env, order="alpha")
        assert result.sorted_env["A"] == "alpha"
        assert result.sorted_env["B"] == "beta"

    def test_summary_no_changes(self):
        env = {"A": "1", "B": "2"}
        result = sort_env(env, order="alpha")
        assert "no changes" in result.summary()

    def test_summary_with_changes(self):
        env = {"B": "2", "A": "1"}
        result = sort_env(env, order="alpha")
        assert "alpha" in result.summary()

    def test_original_is_unchanged(self):
        env = {"B": "2", "A": "1"}
        result = sort_env(env, order="alpha")
        assert list(result.original.keys()) == ["B", "A"]
