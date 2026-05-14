"""Tests for envault.snapshot and envault.cli_snapshot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

from envault.snapshot import (
    save_snapshot,
    list_snapshots,
    load_snapshot,
    delete_snapshot,
    SnapshotError,
)
from envault.storage import save_vault
from envault.cli_snapshot import (
    cmd_snapshot_save,
    cmd_snapshot_list,
    cmd_snapshot_restore,
    cmd_snapshot_delete,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def seeded(vault_dir: Path) -> tuple[str, str]:
    """Create a vault and a snapshot, return (vault_name, snapshot_id)."""
    name = "myapp"
    blob = "encrypted-blob-v1"
    save_vault(name, blob, vault_dir)
    sid = save_snapshot(name, blob, vault_dir)
    return name, sid


# --- unit tests for snapshot module ---

def test_save_snapshot_returns_string_id(vault_dir):
    sid = save_snapshot("app", "blob123", vault_dir)
    assert isinstance(sid, str) and len(sid) > 0


def test_list_snapshots_empty_by_default(vault_dir):
    assert list_snapshots("nonexistent", vault_dir) == []


def test_list_snapshots_returns_saved_ids(vault_dir):
    sid1 = save_snapshot("app", "blob-a", vault_dir)
    sid2 = save_snapshot("app", "blob-b", vault_dir)
    ids = list_snapshots("app", vault_dir)
    assert sid1 in ids and sid2 in ids
    assert ids == sorted(ids)


def test_load_snapshot_returns_correct_blob(vault_dir, seeded):
    name, sid = seeded
    blob = load_snapshot(name, sid, vault_dir)
    assert blob == "encrypted-blob-v1"


def test_load_snapshot_missing_raises(vault_dir):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot("app", "0000000000000", vault_dir)


def test_delete_snapshot_removes_entry(vault_dir, seeded):
    name, sid = seeded
    delete_snapshot(name, sid, vault_dir)
    assert sid not in list_snapshots(name, vault_dir)


def test_delete_snapshot_missing_raises(vault_dir):
    with pytest.raises(SnapshotError):
        delete_snapshot("app", "9999999999999", vault_dir)


# --- CLI command tests ---

def _args(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_cmd_snapshot_save_prints_id(vault_dir, capsys, monkeypatch):
    save_vault("prod", "blob", vault_dir)
    monkeypatch.setattr("envault.cli_snapshot._vault_dir", lambda: vault_dir)
    cmd_snapshot_save(_args(name="prod"))
    out = capsys.readouterr().out
    assert "Snapshot saved:" in out


def test_cmd_snapshot_save_missing_vault_exits(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.cli_snapshot._vault_dir", lambda: vault_dir)
    with pytest.raises(SystemExit) as exc:
        cmd_snapshot_save(_args(name="ghost"))
    assert exc.value.code == 1


def test_cmd_snapshot_list_shows_ids(vault_dir, capsys, monkeypatch, seeded):
    monkeypatch.setattr("envault.cli_snapshot._vault_dir", lambda: vault_dir)
    name, sid = seeded
    cmd_snapshot_list(_args(name=name))
    out = capsys.readouterr().out
    assert sid in out


def test_cmd_snapshot_restore_overwrites_vault(vault_dir, monkeypatch, seeded):
    monkeypatch.setattr("envault.cli_snapshot._vault_dir", lambda: vault_dir)
    name, sid = seeded
    save_vault(name, "new-blob", vault_dir)
    cmd_snapshot_restore(_args(name=name, snapshot_id=sid))
    from envault.storage import load_vault
    assert load_vault(name, vault_dir) == "encrypted-blob-v1"


def test_cmd_snapshot_delete_removes(vault_dir, capsys, monkeypatch, seeded):
    monkeypatch.setattr("envault.cli_snapshot._vault_dir", lambda: vault_dir)
    name, sid = seeded
    cmd_snapshot_delete(_args(name=name, snapshot_id=sid))
    assert list_snapshots(name, vault_dir) == []
