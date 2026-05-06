"""Tests for envforge.cli_redact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envforge.cli_redact import cmd_redact


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.env"
    p.write_text(
        "APP_NAME=myapp\n"
        "DB_PASSWORD=supersecret\n"
        "API_TOKEN=tok123\n"
        "PORT=8080\n"
    )
    return p


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "schema": None,
        "pattern": None,
        "mask": "***REDACTED***",
        "format": "env",
        "verbose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestCmdRedact:
    def test_redact_writes_env_to_stdout(self, env_file, capsys):
        args = make_args(env_file=str(env_file))
        rc = cmd_redact(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "APP_NAME=myapp" in out
        assert "***REDACTED***" in out

    def test_password_is_masked(self, env_file, capsys):
        args = make_args(env_file=str(env_file))
        cmd_redact(args)
        out = capsys.readouterr().out
        assert "supersecret" not in out
        assert "DB_PASSWORD=***REDACTED***" in out

    def test_token_is_masked(self, env_file, capsys):
        args = make_args(env_file=str(env_file))
        cmd_redact(args)
        out = capsys.readouterr().out
        assert "tok123" not in out

    def test_json_format_output(self, env_file, capsys):
        args = make_args(env_file=str(env_file), format="json")
        rc = cmd_redact(args)
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, dict)
        assert data["APP_NAME"] == "myapp"
        assert data["DB_PASSWORD"] == "***REDACTED***"

    def test_custom_mask(self, env_file, capsys):
        args = make_args(env_file=str(env_file), mask="[HIDDEN]")
        cmd_redact(args)
        out = capsys.readouterr().out
        assert "[HIDDEN]" in out

    def test_extra_pattern_masks_key(self, env_file, capsys):
        args = make_args(env_file=str(env_file), pattern=["PORT"])
        cmd_redact(args)
        out = capsys.readouterr().out
        assert "PORT=***REDACTED***" in out

    def test_verbose_prints_summary_to_stderr(self, env_file, capsys):
        args = make_args(env_file=str(env_file), verbose=True)
        cmd_redact(args)
        err = capsys.readouterr().err
        assert "Redacted" in err
