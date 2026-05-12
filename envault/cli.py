"""CLI entry points for envault using argparse."""

import argparse
import sys
from getpass import getpass
from pathlib import Path

from envault.exceptions import EnvaultError
from envault.vault import export_dotenv, list_vault_names, pull, push


def cmd_push(args: argparse.Namespace) -> None:
    dotenv_path = Path(args.file)
    if not dotenv_path.exists():
        print(f"Error: file '{dotenv_path}' not found.", file=sys.stderr)
        sys.exit(1)

    passphrase = getpass("Passphrase: ")
    content = dotenv_path.read_text(encoding="utf-8")

    try:
        name = push(args.vault, content, passphrase)
        print(f"Vault '{name}' saved successfully.")
    except EnvaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pull(args: argparse.Namespace) -> None:
    passphrase = getpass("Passphrase: ")

    try:
        dotenv_str = export_dotenv(args.vault, passphrase)
    except EnvaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = Path(args.output) if args.output else Path(".env")
    output.write_text(dotenv_str, encoding="utf-8")
    print(f"Vault '{args.vault}' written to '{output}'.")


def cmd_list(_args: argparse.Namespace) -> None:
    names = list_vault_names()
    if not names:
        print("No vaults found.")
    else:
        for name in names:
            print(f"  {name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Securely store and sync .env files.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_push = sub.add_parser("push", help="Encrypt and store a .env file.")
    p_push.add_argument("vault", help="Vault name")
    p_push.add_argument("--file", default=".env", help="Path to .env file (default: .env)")
    p_push.set_defaults(func=cmd_push)

    p_pull = sub.add_parser("pull", help="Decrypt and restore a .env file.")
    p_pull.add_argument("vault", help="Vault name")
    p_pull.add_argument("--output", default=None, help="Output path (default: .env)")
    p_pull.set_defaults(func=cmd_pull)

    p_list = sub.add_parser("list", help="List available vaults.")
    p_list.set_defaults(func=cmd_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
