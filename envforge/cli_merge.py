"""CLI sub-command helpers for the 'merge' command."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from envforge.merger import merge_many
from envforge.parser import parse_env_file
from envforge.generator import generate_env_string
from envforge.schema import Schema


def cmd_merge(
    env_files: List[str],
    output: Optional[str],
    remove_missing: bool,
    schema_file: Optional[str],
    quiet: bool,
) -> int:
    """Merge multiple .env files and write the result.

    Returns an exit code (0 = success, 1 = error).
    """
    if len(env_files) < 2:
        print("error: at least two env files are required for merge.", file=sys.stderr)
        return 1

    envs = []
    for path in env_files:
        try:
            envs.append(parse_env_file(path))
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1

    result = merge_many(envs, remove_missing=remove_missing)

    schema: Optional[Schema] = None
    if schema_file:
        try:
            schema = Schema.from_json(Path(schema_file).read_text())
        except Exception as exc:  # noqa: BLE001
            print(f"error: could not load schema: {exc}", file=sys.stderr)
            return 1

    if not quiet:
        print(result.summary(), file=sys.stderr)

    if schema:
        content = generate_env_string(schema, overrides=result.merged)
    else:
        lines = [f"{k}={v}" for k, v in sorted(result.merged.items())]
        content = "\n".join(lines) + "\n"

    if output:
        Path(output).write_text(content)
    else:
        sys.stdout.write(content)

    return 0
