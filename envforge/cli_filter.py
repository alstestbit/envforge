import argparse
import sys
from envforge.parser import parse_env_file
from envforge.filterer import filter_env


def cmd_filter(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: env file '{args.env_file}' not found.", file=sys.stderr)
        return 1

    keys = args.keys.split(",") if args.keys else None

    result = filter_env(
        env,
        keys=keys,
        pattern=args.pattern,
        prefix=args.prefix,
        invert=args.invert,
    )

    if args.summary:
        print(result.summary())
        return 0

    for key, value in result.filtered.items():
        print(f"{key}={value}")

    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "filter",
        help="Filter env variables by key, pattern, or prefix.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument("--keys", default=None, help="Comma-separated list of keys to keep")
    parser.add_argument("--pattern", default=None, help="Regex pattern to match keys")
    parser.add_argument("--prefix", default=None, help="Key prefix to match")
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Exclude matched keys instead of keeping them",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print exclusion summary instead of filtered env",
    )
    parser.set_defaults(func=cmd_filter)
