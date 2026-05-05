"""CLI entry point for envforge."""
import argparse
import sys
from envforge.schema import Schema
from envforge.generator import generate_env_string
from envforge.validator import Validator
from envforge.parser import parse_env_file
from envforge.differ import diff_env_against_schema, diff_two_envs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envforge",
        description="Generate and validate .env files from schema definitions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate a .env file from a schema.")
    gen_parser.add_argument("schema", help="Path to schema JSON file.")
    gen_parser.add_argument("-o", "--output", help="Output .env file path (default: stdout).")

    # validate
    val_parser = subparsers.add_parser("validate", help="Validate a .env file against a schema.")
    val_parser.add_argument("schema", help="Path to schema JSON file.")
    val_parser.add_argument("env", help="Path to .env file to validate.")

    # diff
    diff_parser = subparsers.add_parser("diff", help="Diff a .env file against a schema or another .env.")
    diff_parser.add_argument("base", help="Schema JSON file or base .env file.")
    diff_parser.add_argument("target", help="Target .env file to compare.")
    diff_parser.add_argument(
        "--mode",
        choices=["schema", "env"],
        default="schema",
        help="Diff mode: against schema (default) or another env file.",
    )

    return parser


def cmd_generate(args) -> int:
    schema = Schema.from_json(args.schema)
    content = generate_env_string(schema)
    if args.output:
        with open(args.output, "w") as f:
            f.write(content)
        print(f"Generated: {args.output}")
    else:
        print(content, end="")
    return 0


def cmd_validate(args) -> int:
    schema = Schema.from_json(args.schema)
    env = parse_env_file(args.env)
    validator = Validator(schema)
    result = validator.validate(env)
    if result.is_valid:
        print("Validation passed.")
        return 0
    else:
        print("Validation failed:")
        for error in result.errors:
            print(f"  {error}")
        return 1


def cmd_diff(args) -> int:
    target_env = parse_env_file(args.target)
    if args.mode == "schema":
        schema = Schema.from_json(args.base)
        result = diff_env_against_schema(target_env, schema)
    else:
        base_env = parse_env_file(args.base)
        result = diff_two_envs(base_env, target_env)

    print(result.summary())
    return 1 if result.has_differences else 0


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "generate":
        return cmd_generate(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "diff":
        return cmd_diff(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
