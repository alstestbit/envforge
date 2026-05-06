"""Tests for envforge.exporter."""

import json
import pytest

from envforge.exporter import (
    export_to_json,
    export_env,
    SUPPORTED_FORMATS,
)


SAMPLE_ENV = {
    "APP_NAME": "envforge",
    "DEBUG": "true",
    "PORT": "8080",
}


class TestExportToJson:
    def test_returns_valid_json(self):
        result = export_to_json(SAMPLE_ENV)
        parsed = json.loads(result)
        assert parsed == SAMPLE_ENV

    def test_keys_are_sorted(self):
        result = export_to_json(SAMPLE_ENV)
        parsed = json.loads(result)
        assert list(parsed.keys()) == sorted(parsed.keys())

    def test_indent_applied(self):
        result = export_to_json(SAMPLE_ENV, indent=4)
        assert "    " in result

    def test_empty_env_produces_empty_object(self):
        result = export_to_json({})
        assert json.loads(result) == {}


class TestExportEnv:
    def test_json_format_works(self):
        result = export_env(SAMPLE_ENV, fmt="json")
        assert json.loads(result)["APP_NAME"] == "envforge"

    def test_format_case_insensitive(self):
        result = export_env(SAMPLE_ENV, fmt="JSON")
        assert json.loads(result) is not None

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported format"):
            export_env(SAMPLE_ENV, fmt="xml")

    def test_writes_to_file(self, tmp_path):
        out_file = tmp_path / "output.json"
        export_env(SAMPLE_ENV, fmt="json", output_path=str(out_file))
        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert data["PORT"] == "8080"

    def test_returns_string_even_when_writing_file(self, tmp_path):
        out_file = tmp_path / "output.json"
        result = export_env(SAMPLE_ENV, fmt="json", output_path=str(out_file))
        assert isinstance(result, str)


def test_supported_formats_contains_expected():
    assert "json" in SUPPORTED_FORMATS
    assert "yaml" in SUPPORTED_FORMATS
    assert "toml" in SUPPORTED_FORMATS
