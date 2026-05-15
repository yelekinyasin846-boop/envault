"""CLI subcommand: envault search."""

import argparse
import getpass
import sys

from envault.search import search_vaults


def cmd_search(args: argparse.Namespace) -> None:
    if not args.key and not args.value:
        print("error: provide --key and/or --value to search.", file=sys.stderr)
        sys.exit(1)

    passphrase = args.passphrase or getpass.getpass("Passphrase: ")
    vault_names = args.vaults if args.vaults else None

    result = search_vaults(
        passphrase=passphrase,
        key_pattern=args.key or None,
        value_pattern=args.value or None,
        vault_names=vault_names,
        include_values=args.show_values,
    )

    if not result.found:
        print("No matches found.")
        sys.exit(0)

    by_vault = result.by_vault()
    for vault_name, matches in by_vault.items():
        print(f"[{vault_name}]")
        for m in matches:
            if args.show_values and m.value is not None:
                print(f"  {m.key}={m.value}")
            else:
                print(f"  {m.key}")

    if args.count:
        print(f"\nTotal matches: {len(result.matches)}")


def build_search_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("search", help="Search for keys or values across vaults")
    p.add_argument("--key", default="", help="Substring to match against key names")
    p.add_argument("--value", default="", help="Substring to match against values")
    p.add_argument(
        "--vaults",
        nargs="+",
        metavar="VAULT",
        help="Limit search to these vault names (default: all)",
    )
    p.add_argument(
        "--show-values",
        action="store_true",
        help="Include values in output (use with caution)",
    )
    p.add_argument(
        "--count",
        action="store_true",
        help="Print total number of matches at the end",
    )
    p.add_argument("--passphrase", default="", help="Passphrase (omit to be prompted)")
    p.set_defaults(func=cmd_search)
