"""CLI subcommands for vault locking."""

import argparse
import sys
from envault.lock import acquire_lock, release_lock, is_locked, LockError


def cmd_lock(args: argparse.Namespace) -> None:
    """Lock a vault to prevent concurrent modifications."""
    try:
        acquire_lock(args.vault_name, vault_dir=getattr(args, "vault_dir", None))
        print(f"Vault '{args.vault_name}' locked.")
    except LockError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_unlock(args: argparse.Namespace) -> None:
    """Release the lock on a vault."""
    vault_dir = getattr(args, "vault_dir", None)
    if not is_locked(args.vault_name, vault_dir=vault_dir):
        print(f"Vault '{args.vault_name}' is not locked.")
        return
    release_lock(args.vault_name, vault_dir=vault_dir)
    print(f"Vault '{args.vault_name}' unlocked.")


def cmd_lock_status(args: argparse.Namespace) -> None:
    """Check whether a vault is currently locked."""
    vault_dir = getattr(args, "vault_dir", None)
    locked = is_locked(args.vault_name, vault_dir=vault_dir)
    status = "locked" if locked else "unlocked"
    print(f"Vault '{args.vault_name}' is {status}.")


def build_lock_subparser(subparsers: argparse._SubParsersAction) -> None:
    lock_p = subparsers.add_parser("lock", help="Lock a vault")
    lock_p.add_argument("vault_name")
    lock_p.set_defaults(func=cmd_lock)

    unlock_p = subparsers.add_parser("unlock", help="Unlock a vault")
    unlock_p.add_argument("vault_name")
    unlock_p.set_defaults(func=cmd_unlock)

    status_p = subparsers.add_parser("lock-status", help="Show lock status of a vault")
    status_p.add_argument("vault_name")
    status_p.set_defaults(func=cmd_lock_status)
