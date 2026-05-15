"""CLI commands for linting vault env variables."""

from __future__ import annotations

import argparse
import sys

from envault.lint import lint_env
from envault.vault import pull
from envault.exceptions import EnvaultError


def cmd_lint(args: argparse.Namespace) -> None:
    """Lint a named vault and report issues."""
    try:
        env = pull(args.name, args.passphrase)
    except EnvaultError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)

    result = lint_env(env)

    if not result.issues:
        print(f"[envault] lint: no issues found in '{args.name}'.")
        sys.exit(0)

    for issue in result.issues:
        prefix = "ERROR  " if issue.severity == "error" else "WARNING"
        print(f"  {prefix}  {issue.key}: {issue.message}")

    print(f"\n[envault] lint summary for '{args.name}': {result.summary()}")

    if args.strict and result.has_errors:
        sys.exit(1)
    elif args.strict and result.has_warnings:
        sys.exit(1)
    elif result.has_errors:
        sys.exit(1)


def build_lint_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("lint", help="Lint env variable names and values in a vault.")
    parser.add_argument("name", help="Vault name to lint.")
    parser.add_argument("--passphrase", required=True, help="Passphrase to decrypt the vault.")
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 on warnings as well as errors.",
    )
    parser.set_defaults(func=cmd_lint)
