"""CLI command for auditing .env files against a schema."""

import sys
import json
from envforge.schema import Schema
from envforge.parser import parse_env_file
from envforge.auditor import audit_env


def cmd_audit(args) -> int:
    """Run audit command. Returns exit code."""
    try:
        schema = Schema.from_json(args.schema)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError as exc:
        print(f"Error reading env file: {exc}", file=sys.stderr)
        return 2

    report = audit_env(env, schema)

    if getattr(args, "format", "text") == "json":
        output = {
            "passed": report.passed,
            "summary": report.summary(),
            "entries": [
                {"key": e.key, "status": e.status, "message": e.message}
                for e in report.entries
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        for entry in report.entries:
            print(str(entry))
        print()
        print(report.summary())

    return 0 if report.passed else 1
