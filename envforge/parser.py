"""Parses .env files into a plain dict of key/value strings."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, IO


def parse_env_string(text: str) -> Dict[str, str]:
    """Parse the contents of a .env file and return a dict."""
    result: Dict[str, str] = {}

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        # Skip blank lines and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ValueError(
                f"Line {lineno}: invalid syntax (missing '='): {raw_line!r}"
            )

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError(f"Line {lineno}: empty key")

        # Strip surrounding quotes if present
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]

        result[key] = value

    return result


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """Read and parse a .env file from disk."""
    path = Path(path)
    return parse_env_string(path.read_text(encoding="utf-8"))


def parse_env_stream(stream: IO[str]) -> Dict[str, str]:
    """Parse a .env file from an open text stream."""
    return parse_env_string(stream.read())
