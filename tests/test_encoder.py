"""Tests for envforge.encoder."""

from __future__ import annotations

import json
import pytest

from envforge.encoder import encode_env, EncodeResult


SAMPLE_ENV = {
    "APP_NAME": "envforge",
    "DEBUG": "true",
    "DATABASE_URL": "postgres://user:pass@localhost/db",
    "GREETING": "hello world",
}


class TestEncodeResult:
    def test_returns_encode_result(self):
        result = encode_env(SAMPLE_ENV)
        assert isinstance(result, EncodeResult)

    def test_key_count_matches(self):
        result = encode_env(SAMPLE_ENV)
        assert result.key_count == len(SAMPLE_ENV)

    def test_str_returns_output(self):
        result = encode_env(SAMPLE_ENV)
        assert str(result) == result.output


class TestDotenvFormat:
    def test_default_format_is_dotenv(self):
        result = encode_env(SAMPLE_ENV)
        assert result.format == "dotenv"

    def test_all_keys_present(self):
        result = encode_env(SAMPLE_ENV, fmt="dotenv")
        for key in SAMPLE_ENV:
            assert key in result.output

    def test_value_with_space_is_quoted(self):
        result = encode_env({"MSG": "hello world"}, fmt="dotenv")
        assert 'MSG="hello world"' in result.output

    def test_plain_value_not_quoted(self):
        result = encode_env({"PORT": "8080"}, fmt="dotenv")
        assert "PORT=8080" in result.output


class TestShellFormat:
    def test_starts_with_shebang(self):
        result = encode_env(SAMPLE_ENV, fmt="shell")
        assert result.output.startswith("#!/usr/bin/env sh")

    def test_uses_export_keyword(self):
        result = encode_env(SAMPLE_ENV, fmt="shell")
        for key in SAMPLE_ENV:
            assert f"export {key}=" in result.output

    def test_values_single_quoted(self):
        result = encode_env({"KEY": "value"}, fmt="shell")
        assert "export KEY='value'" in result.output


class TestJsonFormat:
    def test_output_is_valid_json(self):
        result = encode_env(SAMPLE_ENV, fmt="json")
        parsed = json.loads(result.output)
        assert isinstance(parsed, dict)

    def test_all_keys_in_json(self):
        result = encode_env(SAMPLE_ENV, fmt="json")
        parsed = json.loads(result.output)
        assert set(parsed.keys()) == set(SAMPLE_ENV.keys())

    def test_values_preserved(self):
        result = encode_env(SAMPLE_ENV, fmt="json")
        parsed = json.loads(result.output)
        assert parsed["APP_NAME"] == "envforge"


class TestCsvFormat:
    def test_first_line_is_header(self):
        result = encode_env(SAMPLE_ENV, fmt="csv")
        first_line = result.output.splitlines()[0]
        assert first_line == "key,value"

    def test_all_keys_present(self):
        result = encode_env(SAMPLE_ENV, fmt="csv")
        for key in SAMPLE_ENV:
            assert key in result.output


class TestUnknownFormat:
    def test_strict_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown format"):
            encode_env(SAMPLE_ENV, fmt="xml", strict=True)

    def test_non_strict_falls_back_to_dotenv(self):
        result = encode_env(SAMPLE_ENV, fmt="xml", strict=False)
        assert result.format == "dotenv"
        assert result.warnings
