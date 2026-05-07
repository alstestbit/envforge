"""CLI subcommand: envforge rename"""
import argparse
import sys
from typing import List

from envforge.parser import parse_env_file
from envforge.renamer import rename_env
from envforge.generator import generate_env_string


def cmd_rename(args: argparse.Namespace) -> int:
    """Rename one or more keys in an env file."""
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: env file not found: {args.env_file}", file=sys.stderr)
        return 1

    rename_map: dict = {}
    for pair in args.rename:
        if "=" not in pair:
            print(f"Error: rename pair must be OLD=NEW, got: {pair!r}", file=sys.stderr)
            return 1
        old, new = pair.split("=", 1)
        rename_map[old.strip()] = new.strip()

    result = rename_env(env, rename_map, overwrite=args.overwrite)

    for err in result.errors:
        print(f"Error: {err}", file=sys.stderr)

    if result.errors and not args.force:
        return 1

    output = generate_env_string(None, overrides=result.env)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
    else:
        print(output, end="")

    if args.verbose:
        print(result.summary(), file=sys.stderr)

    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("rename", help="Rename keys in an env file")
    p.add_argument("env_file", help="Path to the .env file")
    p.add_argument(
        "rename",
        nargs="+",
        metavar="OLD=NEW",
        help="Key rename pairs, e.g. DB_HOST=DATABASE_HOST",
    )
    p.add_argument("-o", "--output", help="Write result to file instead of stdout")
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow renaming even if the target key already exists",
    )
    p.add_argument("--force", action="store_true", help="Continue despite errors")
    p.add_argument("-v", "--verbose", action="store_true", help="Print summary to stderr")
    p.set_defaults(func=cmd_rename)
