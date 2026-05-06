"""Integration tests for the merge CLI sub-command."""

import os
import tempfile
from pathlib import Path

import pytest

from envforge.cli_merge import cmd_merge


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def base_env_file(tmp_path):
    p = tmp_path / "base.env"
    p.write_text("APP_ENV=development\nDB_HOST=localhost\nSECRET=abc123\n")
    return str(p)


@pytest.fixture()
def overlay_env_file(tmp_path):
    p = tmp_path / "overlay.env"
    p.write_text("APP_ENV=production\nDB_HOST=db.prod\nNEW_KEY=hello\n")
    return str(p)


class TestCmdMerge:
    def test_merge_writes_to_stdout(self, capsys, base_env_file, overlay_env_file):
        code = cmd_merge(
            [base_env_file, overlay_env_file],
            output=None,
            remove_missing=False,
            schema_file=None,
            quiet=True,
        )
        assert code == 0
        out = capsys.readouterr().out
        assert "APP_ENV=production" in out
        assert "NEW_KEY=hello" in out

    def test_base_only_key_retained_by_default(self, capsys, base_env_file, overlay_env_file):
        cmd_merge(
            [base_env_file, overlay_env_file],
            output=None,
            remove_missing=False,
            schema_file=None,
            quiet=True,
        )
        out = capsys.readouterr().out
        assert "SECRET=abc123" in out

    def test_remove_missing_drops_base_only_keys(self, capsys, base_env_file, overlay_env_file):
        cmd_merge(
            [base_env_file, overlay_env_file],
            output=None,
            remove_missing=True,
            schema_file=None,
            quiet=True,
        )
        out = capsys.readouterr().out
        assert "SECRET" not in out

    def test_merge_writes_to_file(self, tmp_path, base_env_file, overlay_env_file):
        out_file = str(tmp_path / "merged.env")
        code = cmd_merge(
            [base_env_file, overlay_env_file],
            output=out_file,
            remove_missing=False,
            schema_file=None,
            quiet=True,
        )
        assert code == 0
        content = Path(out_file).read_text()
        assert "APP_ENV=production" in content

    def test_missing_file_returns_error(self, capsys, base_env_file):
        code = cmd_merge(
            [base_env_file, "/nonexistent/path.env"],
            output=None,
            remove_missing=False,
            schema_file=None,
            quiet=True,
        )
        assert code == 1

    def test_single_file_returns_error(self, capsys, base_env_file):
        code = cmd_merge(
            [base_env_file],
            output=None,
            remove_missing=False,
            schema_file=None,
            quiet=True,
        )
        assert code == 1

    def test_summary_printed_when_not_quiet(self, capsys, base_env_file, overlay_env_file):
        cmd_merge(
            [base_env_file, overlay_env_file],
            output=None,
            remove_missing=False,
            schema_file=None,
            quiet=False,
        )
        err = capsys.readouterr().err
        # Summary should mention at least one change category
        assert any(word in err for word in ("Added", "Changed", "Removed", "No changes"))
