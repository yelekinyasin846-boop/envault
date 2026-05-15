"""Vault locking mechanism to prevent concurrent modifications."""

import os
import json
import time
from pathlib import Path
from envault.storage import get_vault_path
from envault.exceptions import EnvaultError


LOCK_TIMEOUT_SECONDS = 30


class LockError(EnvaultError):
    def __init__(self, vault_name: str, reason: str = ""):
        self.vault_name = vault_name
        msg = f"Vault '{vault_name}' is locked"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


def _lock_path(vault_name: str, vault_dir: str | None = None) -> Path:
    base = get_vault_path(vault_name, vault_dir)
    return Path(str(base) + ".lock")


def acquire_lock(vault_name: str, vault_dir: str | None = None) -> None:
    """Acquire an exclusive lock on a vault. Raises LockError if already locked."""
    lock_file = _lock_path(vault_name, vault_dir)
    now = time.time()

    if lock_file.exists():
        try:
            data = json.loads(lock_file.read_text())
            acquired_at = data.get("acquired_at", 0)
            if now - acquired_at < LOCK_TIMEOUT_SECONDS:
                pid = data.get("pid", "unknown")
                raise LockError(vault_name, f"held by PID {pid}")
        except (json.JSONDecodeError, OSError):
            pass  # Stale or corrupt lock — overwrite

    lock_data = {"pid": os.getpid(), "acquired_at": now}
    lock_file.write_text(json.dumps(lock_data))


def release_lock(vault_name: str, vault_dir: str | None = None) -> None:
    """Release the lock on a vault."""
    lock_file = _lock_path(vault_name, vault_dir)
    try:
        lock_file.unlink()
    except FileNotFoundError:
        pass


def is_locked(vault_name: str, vault_dir: str | None = None) -> bool:
    """Return True if the vault has an active (non-expired) lock."""
    lock_file = _lock_path(vault_name, vault_dir)
    if not lock_file.exists():
        return False
    try:
        data = json.loads(lock_file.read_text())
        age = time.time() - data.get("acquired_at", 0)
        return age < LOCK_TIMEOUT_SECONDS
    except (json.JSONDecodeError, OSError):
        return False
