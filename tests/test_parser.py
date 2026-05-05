"""Tests for envforge.parser module."""

import pytest

from envforge.parser import parse_env_string, parse_env_file


class TestParseEnvString:
    def test_basic_key_value(self):
        result = parse_env_string("FOO=bar")
        assert result == {"FOO": "bar"}

    def test_multiple_entries(self):
        text = "A=1\nB=2\nC=3"
        assert parse_env_string(text) == {"A": "1", "B": "2", "C": "3"}

    def test_comments_ignored(self):
        text = "# comment\nFOO=bar\n# another"
        assert parse_env_string(text) == {"FOO": "bar"}

    def test_blank_lines_ignored(self):
        text = "\nFOO=bar\n\n"
        assert parse_env_string(text) == {"FOO": "bar"}

    def test_double_quoted_value(self):
        result = parse_env_string('FOO="hello world"')
        assert result["FOO"] == "hello world"

    def test_single_quoted_value(self):
        result = parse_env_string("FOO='hello world'")
        assert result["FOO"] == "hello world"

    def test_value_with_equals_sign(self):
        result = parse_env_string("URL=http://example.com?a=1")
        assert result["URL"] == "http://example.com?a=1"

    def test_missing_equals_raises(self):
        with pytest.raises(ValueError, match="missing '='"):
            parse_env_string("BADLINE")

    def test_empty_key_raises(self):
        with pytest.raises(ValueError, match="empty key"):
            parse_env_string("=value")

    def test_empty_value_allowed(self):
        result = parse_env_string("FOO=")
        assert result["FOO"] == ""


class TestParseEnvFile:
    def test_reads_fixture_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("APP=test\nPORT=9000\n", encoding="utf-8")
        result = parse_env_file(env_file)
        assert result == {"APP": "test", "PORT": "9000"}

    def test_sample_fixture(self):
        from pathlib import Path
        fixture = Path(__file__).parent / "fixtures" / "sample.env"
        result = parse_env_file(fixture)
        assert result["APP_NAME"] == "envforge"
        assert result["PORT"] == "8080"
        assert result["DEBUG"] == "true"
