"""CLI commands for env snapshot management."""

from __future__ import annotations

import argparse
import sys

from envforge.parser import parse_env_file
from envforge.snapshotter import (
    diff_snapshots,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


def cmd_snapshot(args: argparse.Namespace) -> int:
    """Dispatch snapshot subcommands."""
    if args.snapshot_cmd == "take":
        return _take(args)
    elif args.snapshot_cmd == "diff":
        return _diff(args)
    sys.stderr.write("Unknown snapshot subcommand.\n")
    return 1


def _take(args: argparse.Namespace) -> int:
    env = parse_env_file(args.env_file)
    snapshot = take_snapshot(env, label=args.label)
    save_snapshot(snapshot, args.output)
    print(f"Snapshot '{args.label}' saved to {args.output}")
    return 0


def _diff(args: argparse.Namespace) -> int:
    before = load_snapshot(args.before)
    after = load_snapshot(args.after)
    result = diff_snapshots(before, after)

    if not result.has_differences:
        print("No differences between snapshots.")
        return 0

    print(f"Snapshot diff: {result.summary()}")
    for key, value in result.added.items():
        print(f"  + {key}={value}")
    for key, value in result.removed.items():
        print(f"  - {key}={value}")
    for key, (old, new) in result.changed.items():
        print(f"  ~ {key}: {old!r} -> {new!r}")

    return 1 if args.fail_on_diff else 0


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("snapshot", help="Snapshot and diff env files")
    sub = parser.add_subparsers(dest="snapshot_cmd")

    take_p = sub.add_parser("take", help="Take a snapshot of an env file")
    take_p.add_argument("env_file", help="Path to .env file")
    take_p.add_argument("--label", default="snapshot", help="Label for the snapshot")
    take_p.add_argument("--output", required=True, help="Output JSON file path")

    diff_p = sub.add_parser("diff", help="Diff two snapshots")
    diff_p.add_argument("before", help="Path to the 'before' snapshot JSON")
    diff_p.add_argument("after", help="Path to the 'after' snapshot JSON")
    diff_p.add_argument(
        "--fail-on-diff",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found",
    )

    parser.set_defaults(func=cmd_snapshot)
