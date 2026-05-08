"""CLI command for transforming .env files using schema rules."""

import sys
from argparse import ArgumentParser, Namespace
from envforge.parser import parse_env_file
from envforge.schema import Schema
from envforge.transformer import transform_env
from envforge.generator import generate_env_string


def _load_schema(path: str) -> Schema | None:
    """Load and parse a schema from a JSON file path.

    Returns the parsed Schema on success, or raises an exception on failure.
    """
    with open(path) as f:
        return Schema.from_json(f.read())


def cmd_transform(args: Namespace) -> int:
    """Transform env values based on schema metadata."""
    schema = None
    if args.schema:
        try:
            schema = _load_schema(args.schema)
        except FileNotFoundError:
            print(f"Error loading schema: file not found: {args.schema}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error loading schema: {e}", file=sys.stderr)
            return 1

    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error reading env file: file not found: {args.env_file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error reading env file: {e}", file=sys.stderr)
        return 1

    result = transform_env(env, schema)

    if args.summary:
        print(result.summary())
        return 0

    output = generate_env_string(schema, overrides=result.transformed) if schema else (
        "\n".join(f"{k}={v}" for k, v in result.transformed.items())
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)

    if args.verbose and result.has_changes:
        print(result.summary(), file=sys.stderr)

    return 0


def register(subparsers) -> None:
    parser: ArgumentParser = subparsers.add_parser(
        "transform",
        help="Apply schema-defined transforms to .env values"
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument("--schema", help="Path to schema JSON file")
    parser.add_argument("--output", "-o", help="Write output to file instead of stdout")
    parser.add_argument("--summary", action="store_true", help="Print transform summary only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print change summary to stderr")
    parser.set_defaults(func=cmd_transform)
