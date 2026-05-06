"""Tests for envforge.cli_export (cmd_export)."""

import argparse
import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from envforge.cli_export import cmd_export, register


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / "test.env"
    p.write_text("APP_NAME=envforge\nDEBUG=true\nPORT=8080\n")
    return str(p)


def make_args(**kwargs):
    defaults = {"format": "json", "output": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestCmdExport:
    def test_export_json_to_stdout(self, env_file, capsys):
        args = make_args(env_file=env_file)
        rc = cmd_export(args)
        captured = capsys.readouterr()
        assert rc == 0
        data = json.loads(captured.out)
        assert data["APP_NAME"] == "envforge"

    def test_export_json_to_file(self, env_file, tmp_path):
        out = tmp_path / "out.json"
        args = make_args(env_file=env_file, output=str(out))
        rc = cmd_export(args)
        assert rc == 0
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["PORT"] == "8080"

    def test_missing_env_file_returns_error(self, capsys):
        args = make_args(env_file="/nonexistent/path.env")
        rc = cmd_export(args)
        assert rc == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_unsupported_format_returns_error(self, env_file, capsys):
        args = make_args(env_file=env_file, format="xml")
        rc = cmd_export(args)
        assert rc == 1
        captured = capsys.readouterr()
        assert "Export error" in captured.err

    def test_no_stdout_output_when_writing_file(self, env_file, tmp_path, capsys):
        out = tmp_path / "out.json"
        args = make_args(env_file=env_file, output=str(out))
        cmd_export(args)
        captured = capsys.readouterr()
        assert captured.out == ""


class TestRegister:
    def test_register_adds_export_subcommand(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register(subparsers)
        args = parser.parse_args(["export", "some.env", "--format", "json"])
        assert args.env_file == "some.env"
        assert args.format == "json"

    def test_default_format_is_json(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register(subparsers)
        args = parser.parse_args(["export", "some.env"])
        assert args.format == "json"
