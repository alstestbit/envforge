"""Encoder module: serialize env dicts to various string formats."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


_SUPPORTED_FORMATS = ("dotenv", "shell", "json", "csv")


@dataclass
class EncodeResult:
    format: str
    output: str
    key_count: int
    warnings: list = field(default_factory=list)

    def __str__(self) -> str:
        return self.output


def _encode_dotenv(env: Dict[str, str]) -> str:
    lines = []
    for key, value in sorted(env.items()):
        # Quote values that contain spaces or special chars
        if any(c in value for c in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines)


def _encode_shell(env: Dict[str, str]) -> str:
    lines = ["#!/usr/bin/env sh"]
    for key, value in sorted(env.items()):
        escaped = value.replace("'", "'\\''")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines)


def _encode_json(env: Dict[str, str]) -> str:
    import json
    return json.dumps(dict(sorted(env.items())), indent=2)


def _encode_csv(env: Dict[str, str]) -> str:
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value"])
    for key in sorted(env):
        writer.writerow([key, env[key]])
    return buf.getvalue().rstrip()


_ENCODERS = {
    "dotenv": _encode_dotenv,
    "shell": _encode_shell,
    "json": _encode_json,
    "csv": _encode_csv,
}


def encode_env(
    env: Dict[str, str],
    fmt: str = "dotenv",
    *,
    strict: bool = False,
) -> EncodeResult:
    """Encode an env dict to the requested format string.

    Args:
        env: Mapping of environment variable names to values.
        fmt: One of 'dotenv', 'shell', 'json', 'csv'.
        strict: If True, raise ValueError on unknown format instead of
                falling back to dotenv.

    Returns:
        EncodeResult with the serialised output.
    """
    warnings: list = []
    if fmt not in _ENCODERS:
        if strict:
            raise ValueError(
                f"Unknown format {fmt!r}. Supported: {', '.join(_SUPPORTED_FORMATS)}"
            )
        warnings.append(f"Unknown format {fmt!r}, falling back to 'dotenv'.")
        fmt = "dotenv"

    output = _ENCODERS[fmt](env)
    return EncodeResult(format=fmt, output=output, key_count=len(env), warnings=warnings)
