"""CLI command for detecting duplicate keys in .env files."""
import argparse
import sys
from pathlib import Path
from envforge.duplicator import find_duplicates


def cmd_duplicate(args: argparse.Namespace) -> int:
    """Detect duplicate keys in one or more .env files."""
    exit_code = 0

    for env_path_str in args.env_files:
        env_path = Path(env_path_str)
        if not env_path.exists():
            print(f"Error: file not found: {env_path}", file=sys.stderr)
            exit_code = 1
            continue

        content = env_path.read_text(encoding="utf-8")
        report = find_duplicates(content)

        if args.quiet:
            if report.has_duplicates:
                exit_code = 1
            continue

        print(f"==> {env_path}")
        print(report.summary())

        if report.has_duplicates:
            exit_code = 1

    return exit_code


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "duplicate",
        help="Detect duplicate keys in .env files",
    )
    parser.add_argument(
        "env_files",
        nargs="+",
        metavar="ENV_FILE",
        help="One or more .env files to check for duplicate keys",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="Suppress output; exit with non-zero code if duplicates found",
    )
    parser.set_defaults(func=cmd_duplicate)
