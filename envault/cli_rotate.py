"""CLI sub-commands for passphrase rotation."""

import argparse
import getpass
import sys

from envault.rotate import rotate_vault, rotate_all_vaults, RotationError


def cmd_rotate(args: argparse.Namespace) -> None:
    """Handle the 'rotate' sub-command."""
    old_passphrase = getpass.getpass("Current passphrase: ")
    new_passphrase = getpass.getpass("New passphrase: ")
    confirm = getpass.getpass("Confirm new passphrase: ")

    if new_passphrase != confirm:
        print("Error: new passphrases do not match.", file=sys.stderr)
        sys.exit(1)

    vault_dir = getattr(args, "vault_dir", None)

    try:
        if args.all:
            rotated = rotate_all_vaults(old_passphrase, new_passphrase, vault_dir=vault_dir)
            if rotated:
                print(f"Rotated {len(rotated)} vault(s): {', '.join(rotated)}")
            else:
                print("No vaults found to rotate.")
        else:
            rotate_vault(args.vault, old_passphrase, new_passphrase, vault_dir=vault_dir)
            print(f"Passphrase rotated successfully for vault '{args.vault}'.")
    except RotationError as exc:
        print(f"Rotation failed: {exc.message}", file=sys.stderr)
        sys.exit(1)


def build_rotate_subparser(subparsers) -> None:
    """Register the 'rotate' sub-command with *subparsers*."""
    parser = subparsers.add_parser(
        "rotate",
        help="Re-encrypt a vault (or all vaults) with a new passphrase.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--vault", metavar="NAME", help="Name of the vault to rotate.")
    group.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Rotate all vaults in the vault directory.",
    )
    parser.set_defaults(func=cmd_rotate)
