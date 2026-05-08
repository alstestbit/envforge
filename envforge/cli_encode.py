"""CLI sub-command: encode an .env file to a chosen output format."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envforge.encoder import encode_env, _SUPPORTED_FORMATS
from envforge.parser import parse_env_file


def cmd_encode(args: argparse.Namespace) -> int:
    """Entry point for the `envforge encode` sub-command."""
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        return 1

    env = parse_env_file(env_path)

    try:
        result = encode_env(env, fmt=args.format, strict=True)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(result.output, encoding="utf-8")
        print(f"Encoded {result.key_count} keys to {out_path} ({args.format})", file=sys.stderr)
    else:
        print(result.output)

    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "encode",
        help="Encode an .env file to dotenv, shell, json, or csv format.",
    )
    parser.add_argument("env_file", help="Path to the source .env file.")
    parser.add_argument(
        "--format",
        "-f",
        default="dotenv",
        choices=_SUPPORTED_FORMATS,
        help="Output format (default: dotenv).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    parser.set_defaults(func=cmd_encode)
