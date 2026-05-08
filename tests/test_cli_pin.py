"""Tests for envforge.cli_pin."""

import argparse
import json
import os
import tempfile
import pytest

from envforge.cli_pin import cmd_pin


@pytest.fixture
def schema_file(tmp_path):
    schema = {
        "variables": [
            {"name": "APP_HOST", "type": "string", "required": True, "default": "localhost"},
            {"name": "APP_PORT", "type": "string", "required": True, "default": "8080"},
        ]
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return str(p)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "test.env"
    p.write_text("APP_HOST=prod.example.com\nAPP_PORT=443\n")
    return str(p)


def make_args(**kwargs):
    defaults = {
        "schema": None,
        "env": None,
        "output": None,
        "verbose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestCmdPin:
    def test_pin_writes_to_stdout(self, schema_file, env_file, capsys):
        args = make_args(schema=schema_file, env=env_file)
        rc = cmd_pin(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "APP_HOST" in out
        assert "prod.example.com" in out

    def test_pin_writes_to_file(self, schema_file, env_file, tmp_path):
        out_path = str(tmp_path / "out.env")
        args = make_args(schema=schema_file, env=env_file, output=out_path)
        rc = cmd_pin(args)
        assert rc == 0
        content = open(out_path).read()
        assert "APP_HOST" in content

    def test_missing_env_file_returns_1(self, schema_file):
        args = make_args(schema=schema_file, env="/nonexistent.env")
        rc = cmd_pin(args)
        assert rc == 1

    def test_invalid_schema_returns_1(self, env_file):
        args = make_args(schema="/nonexistent_schema.json", env=env_file)
        rc = cmd_pin(args)
        assert rc == 1

    def test_verbose_flag_prints_entries(self, schema_file, env_file, capsys):
        args = make_args(schema=schema_file, env=env_file, verbose=True)
        rc = cmd_pin(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "~" in out or "=" in out
