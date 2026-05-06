"""CLI command for profiling multiple env files against a schema."""
import argparse
import sys
from typing import Dict
from envforge.schema import Schema
from envforge.parser import parse_env_file
from envforge.profiler import profile_envs


def cmd_profile(args: argparse.Namespace) -> int:
    """Validate multiple named env files against a schema and report results."""
    try:
        schema = Schema.from_json(open(args.schema).read())
    except Exception as e:
        print(f"Error loading schema: {e}", file=sys.stderr)
        return 2

    envs: Dict[str, dict] = {}
    for env_spec in args.envs:
        if ":" not in env_spec:
            print(f"Invalid env spec '{env_spec}' — expected name:path", file=sys.stderr)
            return 2
        name, path = env_spec.split(":", 1)
        try:
            envs[name] = parse_env_file(path)
        except FileNotFoundError:
            print(f"File not found: {path}", file=sys.stderr)
            return 2

    report = profile_envs(schema, envs)
    print(report.summary())

    if args.strict and report.failed():
        return 1
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "profile",
        help="Validate multiple env files against a schema",
    )
    parser.add_argument("schema", help="Path to schema JSON file")
    parser.add_argument(
        "envs",
        nargs="+",
        metavar="NAME:FILE",
        help="Named env files to profile (e.g. dev:.env.dev)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any environment fails validation",
    )
    parser.set_defaults(func=cmd_profile)
