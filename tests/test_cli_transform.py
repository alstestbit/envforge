"""Tests for envforge.cli_transform module."""

import json
import pytest
from argparse import Namespace
from unittest.mock import patch
from envforge.cli_transform import cmd_transform


@pytest.fixture
def schema_file(tmp_path):
    schema = {
        "vars": {
            "APP_ENV": {"type": "string", "required": True, "metadata": {"transform": "uppercase"}},
            "DEBUG": {"type": "string", "required": False, "metadata": {"transform": "boolean_normalize"}}
        }
    }
    f = tmp_path / "schema.json"
    f.write_text(json.dumps(schema))
    return str(f)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "test.env"
    f.write_text("APP_ENV=production\nDEBUG=yes\n")
    return str(f)


def make_args(**kwargs):
    defaults = {
        "env_file": None,
        "schema": None,
        "output": None,
        "summary": False,
        "verbose": False,
    }
    defaults.update(kwargs)
    return Namespace(**defaults)


class TestCmdTransform:
    def test_transform_writes_to_stdout(self, env_file, schema_file, capsys):
        args = make_args(env_file=env_file, schema=schema_file)
        rc = cmd_transform(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "PRODUCTION" in out

    def test_boolean_normalized_in_output(self, env_file, schema_file, capsys):
        args = make_args(env_file=env_file, schema=schema_file)
        cmd_transform(args)
        out = capsys.readouterr().out
        assert "true" in out

    def test_summary_flag_prints_summary(self, env_file, schema_file, capsys):
        args = make_args(env_file=env_file, schema=schema_file, summary=True)
        rc = cmd_transform(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "Transformed" in out

    def test_output_written_to_file(self, env_file, schema_file, tmp_path):
        out_file = str(tmp_path / "out.env")
        args = make_args(env_file=env_file, schema=schema_file, output=out_file)
        rc = cmd_transform(args)
        assert rc == 0
        content = open(out_file).read()
        assert "PRODUCTION" in content

    def test_invalid_schema_returns_error(self, env_file, tmp_path):
        bad_schema = tmp_path / "bad.json"
        bad_schema.write_text("{invalid json")
        args = make_args(env_file=env_file, schema=str(bad_schema))
        rc = cmd_transform(args)
        assert rc == 1

    def test_no_schema_passes_through(self, env_file, capsys):
        args = make_args(env_file=env_file)
        rc = cmd_transform(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "APP_ENV" in out
