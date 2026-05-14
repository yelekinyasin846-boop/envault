"""Snapshot support: capture and restore point-in-time copies of a vault."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from envault.storage import get_vault_path, ensure_vault_dir
from envault.exceptions import EnvaultError


class SnapshotError(EnvaultError):
    def __init__(self, message: str):
        super().__init__(message)


def _snapshot_dir(vault_name: str, vault_dir: Optional[Path] = None) -> Path:
    """Return the directory where snapshots for *vault_name* are stored."""
    base = get_vault_path(vault_name, vault_dir).parent
    return base / ".snapshots" / vault_name


def save_snapshot(vault_name: str, blob: str, vault_dir: Optional[Path] = None) -> str:
    """Persist the current encrypted *blob* as a new snapshot.

    Returns the snapshot ID (a timestamp-based string).
    """
    snap_dir = _snapshot_dir(vault_name, vault_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)

    snapshot_id = f"{int(time.time() * 1000)}"
    snap_file = snap_dir / f"{snapshot_id}.snap"
    snap_file.write_text(json.dumps({"id": snapshot_id, "blob": blob}), encoding="utf-8")
    return snapshot_id


def list_snapshots(vault_name: str, vault_dir: Optional[Path] = None) -> List[str]:
    """Return snapshot IDs for *vault_name*, sorted oldest-first."""
    snap_dir = _snapshot_dir(vault_name, vault_dir)
    if not snap_dir.exists():
        return []
    ids = [p.stem for p in snap_dir.glob("*.snap")]
    return sorted(ids)


def load_snapshot(vault_name: str, snapshot_id: str, vault_dir: Optional[Path] = None) -> str:
    """Return the encrypted blob stored in *snapshot_id*."""
    snap_dir = _snapshot_dir(vault_name, vault_dir)
    snap_file = snap_dir / f"{snapshot_id}.snap"
    if not snap_file.exists():
        raise SnapshotError(f"Snapshot '{snapshot_id}' not found for vault '{vault_name}'.")
    data = json.loads(snap_file.read_text(encoding="utf-8"))
    return data["blob"]


def delete_snapshot(vault_name: str, snapshot_id: str, vault_dir: Optional[Path] = None) -> None:
    """Remove a single snapshot by ID."""
    snap_dir = _snapshot_dir(vault_name, vault_dir)
    snap_file = snap_dir / f"{snapshot_id}.snap"
    if not snap_file.exists():
        raise SnapshotError(f"Snapshot '{snapshot_id}' not found for vault '{vault_name}'.")
    snap_file.unlink()
