"""Tests for envforge.cli module."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from envforge.cli import main


SAMPLE_SCHEMA = {
    "name": "cli-test",
    "variables": [
        {"name": "APP_NAME", "type": "string", "default": "testapp", "required": False},
        {"name": "SECRET", "type": "string", "required": True},
    ],
}


@pytest.fixture()
def schema_file():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as fh:
        json.dump(SAMPLE_SCHEMA, fh)
        name = fh.name
    yield name
    os.unlink(name)


@pytest.fixture()
def valid_env_file():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".env", delete=False, encoding="utf-8"
    ) as fh:
        fh.write("APP_NAME=hello\nSECRET=mysecret\n")
        name = fh.name
    yield name
    os.unlink(name)


@pytest.fixture()
def invalid_env_file():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".env", delete=False, encoding="utf-8"
    ) as fh:
        fh.write("APP_NAME=hello\n")
        name = fh.name
    yield name
    os.unlink(name)


class TestGenerateCommand:
    def test_generate_to_stdout(self, capsys, schema_file):
        with pytest.raises(SystemExit) as exc:
            main(["generate", schema_file])
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "APP_NAME" in captured.out
        assert "SECRET" in captured.out

    def test_generate_to_file(self, schema_file):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "out.env")
            with pytest.raises(SystemExit) as exc:
                main(["generate", schema_file, "-o", out])
            assert exc.value.code == 0
            assert os.path.exists(out)
            content = open(out).read()
            assert "APP_NAME" in content

    def test_generate_with_environment(self, capsys, schema_file):
        with pytest.raises(SystemExit) as exc:
            main(["generate", schema_file, "--environment", "staging"])
        assert exc.value.code == 0
        assert "staging" in capsys.readouterr().out

    def test_generate_no_comments(self, capsys, schema_file):
        with pytest.raises(SystemExit) as exc:
            main(["generate", schema_file, "--no-comments"])
        assert exc.value.code == 0
        assert "# type=" not in capsys.readouterr().out

    def test_generate_bad_schema_exits_nonzero(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["generate", "/nonexistent/schema.json"])
        assert exc.value.code != 0


class TestValidateCommand:
    def test_valid_env_exits_zero(self, schema_file, valid_env_file, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["validate", schema_file, valid_env_file])
        assert exc.value.code == 0
        assert "passed" in capsys.readouterr().out

    def test_invalid_env_exits_nonzero(self, schema_file, invalid_env_file, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["validate", schema_file, invalid_env_file])
        assert exc.value.code != 0
        assert "failed" in capsys.readouterr().out

    def test_missing_env_file_exits_nonzero(self, schema_file, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["validate", schema_file, "/no/such/file.env"])
        assert exc.value.code != 0
