"""CLI command for applying patch operations to .env files."""

import argparse
import json
import sys
from pathlib import Path

from envforge.parser import parse_env_file, parse_env_string
from envforge.patcher import patch_env


def cmd_patch(args: argparse.Namespace) -> int:
    """Apply a set of patch operations to an .env file and output the result.

    Patch operations are supplied as a JSON file or inline JSON string.
    Each operation is a dict with keys:
        - op: "set", "delete", or "rename"
        - key: the target key
        - value: (set only) the new value
        - to: (rename only) the new key name

    Returns 0 on success, 1 on error.
    """
    # Load the environment
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Error: env file not found: {env_path}", file=sys.stderr)
        return 1

    env = parse_env_file(str(env_path))

    # Load patch operations
    ops = _load_ops(args)
    if ops is None:
        return 1

    # Apply the patch
    result = patch_env(env, ops)

    if result.has_errors():
        for entry in result.errors:
            print(f"Patch error: {entry}", file=sys.stderr)
        if not args.ignore_errors:
            return 1

    # Output result
    output_lines = [f"{k}={v}" for k, v in result.env.items()]
    output = "\n".join(output_lines)
    if output:
        output += "\n"

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output)
        print(f"Patched env written to {out_path}", file=sys.stderr)
    else:
        print(output, end="")

    # Print summary to stderr if verbose
    if args.verbose:
        print(result.summary(), file=sys.stderr)

    return 0


def _load_ops(args: argparse.Namespace) -> list | None:
    """Load patch operations from --ops-file or --ops inline JSON."""
    if args.ops_file:
        ops_path = Path(args.ops_file)
        if not ops_path.exists():
            print(f"Error: ops file not found: {ops_path}", file=sys.stderr)
            return None
        try:
            ops = json.loads(ops_path.read_text())
        except json.JSONDecodeError as exc:
            print(f"Error: invalid JSON in ops file: {exc}", file=sys.stderr)
            return None
    elif args.ops:
        try:
            ops = json.loads(args.ops)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid inline JSON ops: {exc}", file=sys.stderr)
            return None
    else:
        print("Error: provide --ops or --ops-file", file=sys.stderr)
        return None

    if not isinstance(ops, list):
        print("Error: ops must be a JSON array of operation objects", file=sys.stderr)
        return None

    return ops


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'patch' subcommand with the given subparsers."""
    parser = subparsers.add_parser(
        "patch",
        help="Apply patch operations (set/delete/rename) to a .env file",
    )
    parser.add_argument("env_file", help="Path to the .env file to patch")

    ops_group = parser.add_mutually_exclusive_group()
    ops_group.add_argument(
        "--ops",
        metavar="JSON",
        help="Inline JSON array of patch operations",
    )
    ops_group.add_argument(
        "--ops-file",
        metavar="FILE",
        help="Path to a JSON file containing patch operations",
    )

    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write patched env to FILE instead of stdout",
    )
    parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="Continue and output result even if some patch operations fail",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print patch summary to stderr",
    )
    parser.set_defaults(func=cmd_patch)
