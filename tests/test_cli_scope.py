"""Tests for envforge.cli_scope."""
import argparse
import os
import tempfile
import pytest

from envforge.cli_scope import cmd_scope


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "test.env"
    p.write_text(
        "APP_HOST=localhost\n"
        "APP_PORT=8080\n"
        "DB_HOST=db.local\n"
        "LOG_LEVEL=info\n"
    )
    return str(p)


def make_args(**kwargs):
    defaults = {
        "env_file": None,
        "prefix": "APP_",
        "keep_prefix": False,
        "ignore_case": False,
        "summary": False,
        "output": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestCmdScope:
    def test_scope_writes_to_stdout(self, env_file, capsys):
        args = make_args(env_file=env_file, prefix="APP_")
        rc = cmd_scope(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "HOST=localhost" in out
        assert "PORT=8080" in out

    def test_db_prefix_excluded_from_app_scope(self, env_file, capsys):
        args = make_args(env_file=env_file, prefix="APP_")
        cmd_scope(args)
        out = capsys.readouterr().out
        assert "DB_HOST" not in out

    def test_keep_prefix_retains_prefix_in_output(self, env_file, capsys):
        args = make_args(env_file=env_file, prefix="APP_", keep_prefix=True)
        cmd_scope(args)
        out = capsys.readouterr().out
        assert "APP_HOST=localhost" in out

    def test_summary_flag_prints_summary(self, env_file, capsys):
        args = make_args(env_file=env_file, prefix="APP_", summary=True)
        rc = cmd_scope(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "matched" in out

    def test_missing_env_file_returns_1(self, capsys):
        args = make_args(env_file="/nonexistent/path.env", prefix="APP_")
        rc = cmd_scope(args)
        assert rc == 1

    def test_output_to_file(self, env_file, tmp_path):
        out_file = str(tmp_path / "scoped.env")
        args = make_args(env_file=env_file, prefix="APP_", output=out_file)
        rc = cmd_scope(args)
        assert rc == 0
        assert os.path.exists(out_file)
        content = open(out_file).read()
        assert "HOST=localhost" in content

    def test_no_matches_produces_empty_output(self, env_file, capsys):
        args = make_args(env_file=env_file, prefix="REDIS_")
        rc = cmd_scope(args)
        assert rc == 0
        out = capsys.readouterr().out.strip()
        assert out == ""
