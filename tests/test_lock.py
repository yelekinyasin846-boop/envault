"""Tests for envault.lock."""

import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch
from envault.lock import (
    acquire_lock, release_lock, is_locked, _lock_path,
    LockError, LOCK_TIMEOUT_SECONDS,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / "vaults"
    d.mkdir()
    # Create a dummy vault file so get_vault_path resolves correctly
    (d / "myvault.enc").write_text("{}")
    return str(d)


def test_acquire_lock_creates_lock_file(vault_dir):
    acquire_lock("myvault", vault_dir=vault_dir)
    lp = _lock_path("myvault", vault_dir)
    assert lp.exists()


def test_lock_file_contains_pid_and_timestamp(vault_dir):
    acquire_lock("myvault", vault_dir=vault_dir)
    lp = _lock_path("myvault", vault_dir)
    data = json.loads(lp.read_text())
    assert "pid" in data
    assert "acquired_at" in data
    assert isinstance(data["acquired_at"], float)


def test_is_locked_true_after_acquire(vault_dir):
    acquire_lock("myvault", vault_dir=vault_dir)
    assert is_locked("myvault", vault_dir=vault_dir) is True


def test_is_locked_false_before_acquire(vault_dir):
    assert is_locked("myvault", vault_dir=vault_dir) is False


def test_release_lock_removes_file(vault_dir):
    acquire_lock("myvault", vault_dir=vault_dir)
    release_lock("myvault", vault_dir=vault_dir)
    assert not _lock_path("myvault", vault_dir).exists()


def test_release_lock_idempotent(vault_dir):
    release_lock("myvault", vault_dir=vault_dir)  # Should not raise


def test_acquire_lock_raises_if_already_locked(vault_dir):
    acquire_lock("myvault", vault_dir=vault_dir)
    with pytest.raises(LockError, match="myvault"):
        acquire_lock("myvault", vault_dir=vault_dir)


def test_acquire_lock_overwrites_expired_lock(vault_dir):
    lp = _lock_path("myvault", vault_dir)
    old_data = {"pid": 9999, "acquired_at": time.time() - LOCK_TIMEOUT_SECONDS - 5}
    lp.write_text(json.dumps(old_data))
    # Should not raise — expired lock is overwritten
    acquire_lock("myvault", vault_dir=vault_dir)
    data = json.loads(lp.read_text())
    assert data["pid"] != 9999


def test_is_locked_false_for_expired_lock(vault_dir):
    lp = _lock_path("myvault", vault_dir)
    old_data = {"pid": 9999, "acquired_at": time.time() - LOCK_TIMEOUT_SECONDS - 1}
    lp.write_text(json.dumps(old_data))
    assert is_locked("myvault", vault_dir=vault_dir) is False


def test_lock_error_message_contains_vault_name():
    err = LockError("testvault", "held by PID 42")
    assert "testvault" in str(err)
    assert "42" in str(err)
