"""Context manager for safe vault locking/unlocking."""

from envault.lock import acquire_lock, release_lock, LockError


class VaultLock:
    """Context manager that acquires a vault lock on enter and releases on exit.

    Usage::

        with VaultLock("myvault", vault_dir="/path/to/vaults"):
            # safe to modify vault here
            ...

    Raises:
        LockError: if the vault is already locked by another process.
    """

    def __init__(self, vault_name: str, vault_dir: str | None = None):
        self.vault_name = vault_name
        self.vault_dir = vault_dir
        self._acquired = False

    def __enter__(self) -> "VaultLock":
        acquire_lock(self.vault_name, vault_dir=self.vault_dir)
        self._acquired = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._acquired:
            release_lock(self.vault_name, vault_dir=self.vault_dir)
            self._acquired = False
        return False  # Do not suppress exceptions

    def __repr__(self) -> str:
        state = "acquired" if self._acquired else "released"
        return f"VaultLock(vault_name={self.vault_name!r}, state={state})"
