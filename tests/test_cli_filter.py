import argparse
import pytest
from unittest.mock import patch, mock_open
from envforge.cli_filter import cmd_filter, register


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "test.env"
    p.write_text("APP_NAME=myapp\nDB_HOST=localhost\nSECRET_KEY=abc123\n")
    return str(p)


def make_args(**kwargs):
    defaults = {
        "env_file": "",
        "keys": None,
        "pattern": None,
        "prefix": None,
        "invert": False,
        "summary": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestCmdFilter:
    def test_filter_writes_to_stdout(self, env_file, capsys):
        args = make_args(env_file=env_file)
        result = cmd_filter(args)
        out = capsys.readouterr().out
        assert "APP_NAME=myapp" in out
        assert result == 0

    def test_filter_by_prefix(self, env_file, capsys):
        args = make_args(env_file=env_file, prefix="APP_")
        cmd_filter(args)
        out = capsys.readouterr().out
        assert "APP_NAME=myapp" in out
        assert "DB_HOST" not in out

    def test_filter_by_keys(self, env_file, capsys):
        args = make_args(env_file=env_file, keys="DB_HOST")
        cmd_filter(args)
        out = capsys.readouterr().out
        assert "DB_HOST=localhost" in out
        assert "APP_NAME" not in out

    def test_filter_by_pattern(self, env_file, capsys):
        args = make_args(env_file=env_file, pattern="SECRET")
        cmd_filter(args)
        out = capsys.readouterr().out
        assert "SECRET_KEY=abc123" in out
        assert "APP_NAME" not in out

    def test_invert_flag(self, env_file, capsys):
        args = make_args(env_file=env_file, prefix="APP_", invert=True)
        cmd_filter(args)
        out = capsys.readouterr().out
        assert "APP_NAME" not in out
        assert "DB_HOST=localhost" in out

    def test_summary_flag(self, env_file, capsys):
        args = make_args(env_file=env_file, prefix="APP_", summary=True)
        result = cmd_filter(args)
        out = capsys.readouterr().out
        assert "Excluded" in out or "No keys" in out
        assert result == 0

    def test_missing_env_file_returns_1(self, capsys):
        args = make_args(env_file="/nonexistent/path.env")
        result = cmd_filter(args)
        assert result == 1

    def test_register_adds_filter_subcommand(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register(subparsers)
        args = parser.parse_args(["filter", "some.env"])
        assert hasattr(args, "func")
