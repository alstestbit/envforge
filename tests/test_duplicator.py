"""Tests for envforge.duplicator."""
import pytest
from envforge.duplicator import find_duplicates, DuplicateReport, DuplicateEntry


class TestFindDuplicates:
    def test_returns_duplicate_report(self):
        result = find_duplicates("KEY=value")
        assert isinstance(result, DuplicateReport)

    def test_no_duplicates_clean_env(self):
        env = "KEY=value\nOTHER=hello"
        result = find_duplicates(env)
        assert not result.has_duplicates

    def test_single_duplicate_detected(self):
        env = "KEY=first\nKEY=second"
        result = find_duplicates(env)
        assert result.has_duplicates
        assert "KEY" in result.duplicate_keys

    def test_duplicate_entry_has_both_values(self):
        env = "KEY=first\nKEY=second"
        result = find_duplicates(env)
        entry = result.duplicates[0]
        assert entry.occurrences == 2
        assert "first" in entry.values
        assert "second" in entry.values

    def test_triple_occurrence_counted(self):
        env = "KEY=a\nKEY=b\nKEY=c"
        result = find_duplicates(env)
        assert result.duplicates[0].occurrences == 3

    def test_comments_are_ignored(self):
        env = "# KEY=value\nKEY=real"
        result = find_duplicates(env)
        assert not result.has_duplicates

    def test_blank_lines_ignored(self):
        env = "KEY=value\n\nKEY=other"
        result = find_duplicates(env)
        assert result.has_duplicates

    def test_multiple_duplicate_keys(self):
        env = "A=1\nA=2\nB=x\nB=y"
        result = find_duplicates(env)
        assert len(result.duplicates) == 2

    def test_duplicate_keys_property_lists_names(self):
        env = "FOO=1\nFOO=2"
        result = find_duplicates(env)
        assert result.duplicate_keys == ["FOO"]

    def test_summary_no_duplicates(self):
        result = find_duplicates("KEY=value")
        assert "No duplicate" in result.summary()

    def test_summary_with_duplicates(self):
        env = "KEY=a\nKEY=b"
        result = find_duplicates(env)
        summary = result.summary()
        assert "KEY" in summary
        assert "duplicate" in summary.lower()

    def test_str_entry(self):
        entry = DuplicateEntry(key="KEY", occurrences=2, values=["a", "b"])
        assert "KEY" in str(entry)
        assert "2" in str(entry)

    def test_quoted_values_stripped(self):
        env = 'KEY="value1"\nKEY="value2"'
        result = find_duplicates(env)
        assert result.has_duplicates
        assert "value1" in result.duplicates[0].values
