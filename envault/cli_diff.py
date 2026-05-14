"""CLI subcommand for diffing vault contents."""

import argparse
import sys
from getpass import getpass

from envault.diff import diff_envs
from envault.exceptions import EnvaultError
from envault.vault import pull


def cmd_diff(args: argparse.Namespace) -> None:
    """Show differences between two vaults or between a vault and a local .env file."""
    passphrase = getpass(f"Passphrase for '{args.vault_a}': ")

    try:
        env_a = pull(args.vault_a, passphrase)
    except EnvaultError as exc:
        print(f"Error reading vault '{args.vault_a}': {exc}", file=sys.stderr)
        sys.exit(1)

    if args.vault_b:
        try:
            env_b = pull(args.vault_b, passphrase)
        except EnvaultError as exc:
            print(f"Error reading vault '{args.vault_b}': {exc}", file=sys.stderr)
            sys.exit(1)
        source_label = args.vault_b
    elif args.file:
        from envault.dotenv import parse_dotenv, DotEnvParseError
        try:
            with open(args.file, "r") as fh:
                env_b = parse_dotenv(fh.read())
        except (OSError, DotEnvParseError) as exc:
            print(f"Error reading file '{args.file}': {exc}", file=sys.stderr)
            sys.exit(1)
        source_label = args.file
    else:
        print("Provide --vault-b or --file to compare against.", file=sys.stderr)
        sys.exit(1)

    result = diff_envs(env_a, env_b, redact_values=args.redact)
    print(f"Diff: '{args.vault_a}' vs '{source_label}'")
    print(result.summary())

    if not result.has_changes:
        sys.exit(0)
    sys.exit(1 if args.exit_code else 0)


def build_diff_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("diff", help="Diff two vaults or a vault and a .env file")
    p.add_argument("vault_a", help="Base vault name")
    p.add_argument("--vault-b", dest="vault_b", default=None, help="Compare against this vault")
    p.add_argument("--file", dest="file", default=None, help="Compare against a local .env file")
    p.add_argument(
        "--redact",
        action="store_true",
        default=False,
        help="Redact values in diff output",
    )
    p.add_argument(
        "--exit-code",
        dest="exit_code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences exist",
    )
    p.set_defaults(func=cmd_diff)
