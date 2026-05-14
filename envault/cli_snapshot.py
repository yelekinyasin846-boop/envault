"""CLI sub-commands for vault snapshot management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from envault.snapshot import (
    save_snapshot,
    list_snapshots,
    load_snapshot,
    delete_snapshot,
    SnapshotError,
)
from envault.storage import load_vault, save_vault
from envault.config import get_config_value


def _vault_dir() -> Optional[Path]:
    d = get_config_value("vault_dir")
    return Path(d) if d else None


def cmd_snapshot_save(args: argparse.Namespace) -> None:
    """Capture the current state of a vault as a new snapshot."""
    vdir = _vault_dir()
    try:
        blob = load_vault(args.name, vdir)
    except FileNotFoundError:
        print(f"error: vault '{args.name}' does not exist.", file=sys.stderr)
        sys.exit(1)
    snapshot_id = save_snapshot(args.name, blob, vdir)
    print(f"Snapshot saved: {snapshot_id}")


def cmd_snapshot_list(args: argparse.Namespace) -> None:
    """List all snapshots for a vault."""
    vdir = _vault_dir()
    ids = list_snapshots(args.name, vdir)
    if not ids:
        print(f"No snapshots found for vault '{args.name}'.")
    else:
        for sid in ids:
            print(sid)


def cmd_snapshot_restore(args: argparse.Namespace) -> None:
    """Restore a vault to a previous snapshot (overwrites current vault file)."""
    vdir = _vault_dir()
    try:
        blob = load_snapshot(args.name, args.snapshot_id, vdir)
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    save_vault(args.name, blob, vdir)
    print(f"Vault '{args.name}' restored to snapshot {args.snapshot_id}.")


def cmd_snapshot_delete(args: argparse.Namespace) -> None:
    """Delete a specific snapshot."""
    vdir = _vault_dir()
    try:
        delete_snapshot(args.name, args.snapshot_id, vdir)
        print(f"Snapshot {args.snapshot_id} deleted.")
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_snapshot_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    snap = subparsers.add_parser("snapshot", help="Manage vault snapshots.")
    sub = snap.add_subparsers(dest="snapshot_cmd", required=True)

    p_save = sub.add_parser("save", help="Save current vault state as a snapshot.")
    p_save.add_argument("name", help="Vault name.")
    p_save.set_defaults(func=cmd_snapshot_save)

    p_list = sub.add_parser("list", help="List snapshots for a vault.")
    p_list.add_argument("name", help="Vault name.")
    p_list.set_defaults(func=cmd_snapshot_list)

    p_restore = sub.add_parser("restore", help="Restore vault from a snapshot.")
    p_restore.add_argument("name", help="Vault name.")
    p_restore.add_argument("snapshot_id", help="Snapshot ID to restore.")
    p_restore.set_defaults(func=cmd_snapshot_restore)

    p_del = sub.add_parser("delete", help="Delete a snapshot.")
    p_del.add_argument("name", help="Vault name.")
    p_del.add_argument("snapshot_id", help="Snapshot ID to delete.")
    p_del.set_defaults(func=cmd_snapshot_delete)
