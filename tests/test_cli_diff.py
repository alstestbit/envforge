"""Tests for the 'diff' subcommand in the CLI."""
import json
import pytest
from unittest.mock import patch, mock_open
from envforge.cli import main


@pytest.fixture
def schema_file(tmp_path):
    schema = {
        "variables": [
            {"name": "APP_NAME", "type": "string", "required": True},
            {"name": "PORT", "type": "int", "required": True},
        ]
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return str(p)


@pytest.fixture
def matching_env_file(tmp_path):
    p = tmp_path / "match.env"
    p.write_text("APP_NAME=myapp\nPORT=8080\n")
    return str(p)


@pytest.fixture
def mismatched_env_file(tmp_path):
    p = tmp_path / "mismatch.env"
    p.write_text("APP_NAME=myapp\n")
    return str(p)


@pytest.fixture
def base_env_file(tmp_path):
    p = tmp_path / "base.env"
    p.write_text("APP_NAME=myapp\nPORT=8080\n")
    return str(p)


@pytest.fixture
def other_env_file(tmp_path):
    p = tmp_path / "other.env"
    p.write_text("APP_NAME=otherapp\nPORT=9090\n")
    return str(p)


class TestDiffCommand:
    def test_diff_schema_no_differences(self, schema_file, matching_env_file, capsys):
        rc = main(["diff", schema_file, matching_env_file, "--mode", "schema"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "No differences" in out

    def test_diff_schema_with_differences(self, schema_file, mismatched_env_file, capsys):
        rc = main(["diff", schema_file, mismatched_env_file, "--mode", "schema"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "difference" in out

    def test_diff_schema_missing_key_in_output(self, schema_file, mismatched_env_file, capsys):
        main(["diff", schema_file, mismatched_env_file, "--mode", "schema"])
        out = capsys.readouterr().out
        assert "PORT" in out

    def test_diff_env_mode_no_differences(self, base_env_file, capsys):
        rc = main(["diff", base_env_file, base_env_file, "--mode", "env"])
        assert rc == 0

    def test_diff_env_mode_with_differences(self, base_env_file, other_env_file, capsys):
        rc = main(["diff", base_env_file, other_env_file, "--mode", "env"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "difference" in out

    def test_diff_default_mode_is_schema(self, schema_file, matching_env_file, capsys):
        rc = main(["diff", schema_file, matching_env_file])
        assert rc == 0
