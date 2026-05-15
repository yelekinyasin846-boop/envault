"""CLI sub-commands for importing env vars into a vault."""

import argparse
import sys

from envault.import_ import import_from_dotenv, import_from_json, import_from_env, ImportError
from envault.vault import push


def cmd_import(args: argparse.Namespace) -> None:
    """Handle the `envault import` command."""
    try:
        if args.format == "dotenv":
            variables = import_from_dotenv(args.source)
        elif args.format == "json":
            variables = import_from_json(args.source)
        elif args.format == "env":
            prefix = getattr(args, "prefix", None)
            variables = import_from_env(prefix=prefix)
        else:
            print(f"Unknown format: {args.format}", file=sys.stderr)
            sys.exit(1)
    except ImportError as exc:
        print(f"Import error: {exc.message}", file=sys.stderr)
        sys.exit(1)

    if not variables:
        print("No variables found to import.", file=sys.stderr)
        sys.exit(1)

    try:
        vault_name = push(args.vault, variables, args.passphrase,
                         vault_dir=getattr(args, "vault_dir", None))
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to push vault: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Imported {len(variables)} variable(s) into vault '{vault_name}'.")


def build_import_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("import", help="Import env vars into a vault from a file or environment.")
    p.add_argument("vault", help="Name of the vault to write to.")
    p.add_argument("passphrase", help="Encryption passphrase for the vault.")
    p.add_argument(
        "--format",
        choices=["dotenv", "json", "env"],
        default="dotenv",
        help="Source format (default: dotenv).",
    )
    p.add_argument(
        "--source",
        default=".env",
        help="Path to the source file (for dotenv/json formats).",
    )
    p.add_argument(
        "--prefix",
        default=None,
        help="Only import env vars with this prefix (env format only); prefix is stripped.",
    )
    p.set_defaults(func=cmd_import)
