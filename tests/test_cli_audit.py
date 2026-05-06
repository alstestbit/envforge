"""Tests for the CLI audit command."""

import json
import pytest
from unittest.mock import patch, MagicMock
from envforge.cli_audit import cmd_audit


@pytest.fixture
def schema_file(tmp_path):
    schema = {
        "variables": [
            {"name": "APP_ENV", "required": True, "type": "string"},
            {"name": "PORT", "required": False, "type": "integer", "default": "8080"},
        ]
    }
    f = tmp_path / "schema.json"
    f.write_text(json.dumps(schema))
    return str(f)


@pytest.fixture
def valid_env_file(tmp_path):
    f = tmp_path / "valid.env"
    f.write_text("APP_ENV=production\nPORT=9000\n")
    return str(f)


@pytest.fixture
def invalid_env_file(tmp_path):
    f = tmp_path / "invalid.env"
    f.write_text("PORT=9000\n")
    return str(f)


def make_args(schema, env_file, fmt="text"):
    args = MagicMock()
    args.schema = schema
    args.env_file = env_file
    args.format = fmt
    return args


class TestCmdAudit:
    def test_valid_env_returns_zero(self, schema_file, valid_env_file):
        args = make_args(schema_file, valid_env_file)
        assert cmd_audit(args) == 0

    def test_invalid_env_returns_one(self, schema_file, invalid_env_file):
        args = make_args(schema_file, invalid_env_file)
        assert cmd_audit(args) == 1

    def test_missing_schema_returns_two(self, valid_env_file):
        args = make_args("/nonexistent/schema.json", valid_env_file)
        assert cmd_audit(args) == 2

    def test_missing_env_file_returns_two(self, schema_file):
        args = make_args(schema_file, "/nonexistent/file.env")
        assert cmd_audit(args) == 2

    def test_json_output_is_valid_json(self, schema_file, valid_env_file, capsys):
        args = make_args(schema_file, valid_env_file, fmt="json")
        cmd_audit(args)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "passed" in data
        assert "entries" in data
        assert "summary" in data

    def test_json_output_entries_have_required_keys(self, schema_file, invalid_env_file, capsys):
        args = make_args(schema_file, invalid_env_file, fmt="json")
        cmd_audit(args)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        for entry in data["entries"]:
            assert "key" in entry
            assert "status" in entry

    def test_text_output_contains_summary(self, schema_file, valid_env_file, capsys):
        args = make_args(schema_file, valid_env_file)
        cmd_audit(args)
        captured = capsys.readouterr()
        assert "Audit" in captured.out
