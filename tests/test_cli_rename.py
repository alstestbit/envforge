"""Tests for envforge.cli_rename"""
import argparse
import pytest
from unittest.mock import patch, mock_open
from envforge.cli_rename import cmd_rename, register


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "test.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_SECRET=s3cr3t\n")
    return str(p)


def make_args(**kwargs):
    defaults = dict(
        env_file=None,
        rename=[],
        output=None,
        overwrite=False,
        force=False,
        verbose=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestCmdRename:
    def test_rename_writes_to_stdout(self, env_file, capsys):
        args = make_args(env_file=env_file, rename=["DB_HOST=DATABASE_HOST"])
        rc = cmd_rename(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "DATABASE_HOST" in out
        assert "DB_HOST" not in out

    def test_missing_env_file_returns_1(self, capsys):
        args = make_args(env_file="/no/such/file.env", rename=["A=B"])
        rc = cmd_rename(args)
        assert rc == 1

    def test_invalid_pair_format_returns_1(self, env_file, capsys):
        args = make_args(env_file=env_file, rename=["BADFORMAT"])
        rc = cmd_rename(args)
        assert rc == 1

    def test_conflict_without_overwrite_returns_1(self, env_file, capsys):
        # DB_PORT already exists; renaming DB_HOST -> DB_PORT should fail
        args = make_args(env_file=env_file, rename=["DB_HOST=DB_PORT"])
        rc = cmd_rename(args)
        assert rc == 1

    def test_conflict_with_overwrite_succeeds(self, env_file, capsys):
        args = make_args(env_file=env_file, rename=["DB_HOST=DB_PORT"], overwrite=True)
        rc = cmd_rename(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "DB_PORT" in out

    def test_conflict_with_force_returns_0(self, env_file, capsys):
        args = make_args(env_file=env_file, rename=["DB_HOST=DB_PORT"], force=True)
        rc = cmd_rename(args)
        assert rc == 0

    def test_output_written_to_file(self, env_file, tmp_path):
        out_file = str(tmp_path / "out.env")
        args = make_args(env_file=env_file, rename=["DB_HOST=DATABASE_HOST"], output=out_file)
        rc = cmd_rename(args)
        assert rc == 0
        content = open(out_file).read()
        assert "DATABASE_HOST" in content

    def test_verbose_prints_summary(self, env_file, capsys):
        args = make_args(env_file=env_file, rename=["DB_HOST=DATABASE_HOST"], verbose=True)
        rc = cmd_rename(args)
        assert rc == 0
        err = capsys.readouterr().err
        assert "renamed" in err

    def test_register_adds_rename_subcommand(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register(subparsers)
        args = parser.parse_args(["rename", "some.env", "A=B"])
        assert args.rename == ["A=B"]
