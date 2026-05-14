"""CLI command for scoping env vars by prefix."""
import argparse
import sys
from typing import Optional

from envforge.parser import parse_env_file
from envforge.scoper import scope_env


def cmd_scope(args: argparse.Namespace) -> int:
    """Extract env vars matching a scope prefix and write to stdout or file."""
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: env file '{args.env_file}' not found.", file=sys.stderr)
        return 1

    result = scope_env(
        env,
        prefix=args.prefix,
        strip_prefix=not args.keep_prefix,
        case_sensitive=not args.ignore_case,
    )

    if args.summary:
        print(result.summary())
        return 0

    output_env = result.scoped_env if not args.keep_prefix else result.original_env

    lines = [f"{k}={v}" for k, v in sorted(output_env.items())]
    output = "\n".join(lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Scoped env written to '{args.output}'.")
    else:
        print(output)

    return 0


def register(subparsers) -> None:
    parser = subparsers.add_parser(
        "scope",
        help="Extract env vars matching a prefix scope.",
    )
    parser.add_argument("env_file", help="Path to the .env file.")
    parser.add_argument("prefix", help="Prefix to scope by (e.g. APP_).")
    parser.add_argument(
        "--keep-prefix",
        action="store_true",
        help="Do not strip the prefix from matched keys.",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Match prefix case-insensitively.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary instead of the scoped env.",
    )
    parser.add_argument("-o", "--output", help="Write output to this file.")
    parser.set_defaults(func=cmd_scope)
