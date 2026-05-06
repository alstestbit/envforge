"""Tests for envforge.cli_profile."""
import argparse
import pytest
from unittest.mock import patch
from envforge.cli_profile import cmd_profile, register


@pytest.fixture
def schema_file(tmp_path):
    content = '{"variables": [{"name": "APP_ENV", "required": true}, {"name": "DATABASE_URL", "required": true}]}'
    p = tmp_path / "schema.json"
    p.write_text(content)
    return str(p)


@pytest.fixture
def valid_env_file(tmp_path):
    p = tmp_path / "valid.env"
    p.write_text("APP_ENV=dev\nDATABASE_URL=sqlite:///dev.db\n")
    return str(p)


@pytest.fixture
def invalid_env_file(tmp_path):
    p = tmp_path / "invalid.env"
    p.write_text("APP_ENV=dev\n")
    return str(p)


def make_args(schema, envs, strict=False):
    return argparse.Namespace(schema=schema, envs=envs, strict=strict)


class TestCmdProfile:
    def test_all_valid_exits_zero(self, schema_file, valid_env_file, capsys):
        args = make_args(schema_file, [f"dev:{valid_env_file}"])
        rc = cmd_profile(args)
        assert rc == 0

    def test_summary_printed(self, schema_file, valid_env_file, capsys):
        args = make_args(schema_file, [f"dev:{valid_env_file}"])
        cmd_profile(args)
        out = capsys.readouterr().out
        assert "dev" in out

    def test_invalid_env_non_strict_exits_zero(self, schema_file, invalid_env_file, capsys):
        args = make_args(schema_file, [f"broken:{invalid_env_file}"], strict=False)
        rc = cmd_profile(args)
        assert rc == 0

    def test_invalid_env_strict_exits_one(self, schema_file, invalid_env_file):
        args = make_args(schema_file, [f"broken:{invalid_env_file}"], strict=True)
        rc = cmd_profile(args)
        assert rc == 1

    def test_missing_file_exits_two(self, schema_file):
        args = make_args(schema_file, ["dev:/nonexistent/.env"])
        rc = cmd_profile(args)
        assert rc == 2

    def test_invalid_schema_exits_two(self, tmp_path, valid_env_file):
        bad = tmp_path / "bad.json"
        bad.write_text("not json")
        args = make_args(str(bad), [f"dev:{valid_env_file}"])
        rc = cmd_profile(args)
        assert rc == 2

    def test_malformed_env_spec_exits_two(self, schema_file):
        args = make_args(schema_file, ["no-colon-here"])
        rc = cmd_profile(args)
        assert rc == 2

    def test_register_adds_profile_subcommand(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register(subparsers)
        parsed = parser.parse_args(["profile", "schema.json", "dev:.env.dev"])
        assert parsed.envs == ["dev:.env.dev"]
