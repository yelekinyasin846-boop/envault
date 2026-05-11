"""Local storage backend for encrypted .env vaults."""

import json
import os
from pathlib import Path
from typing import Optional

from envault.exceptions import EnvaultError

DEFAULT_VAULT_DIR = Path.home() / ".envault" / "vaults"


def get_vault_path(vault_name: str, vault_dir: Optional[Path] = None) -> Path:
    """Return the file path for a named vault."""
    base = vault_dir or DEFAULT_VAULT_DIR
    return base / f"{vault_name}.vault"


def ensure_vault_dir(vault_dir: Optional[Path] = None) -> Path:
    """Create the vault directory if it does not exist."""
    base = vault_dir or DEFAULT_VAULT_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_vault(vault_name: str, encrypted_blob: str, vault_dir: Optional[Path] = None) -> Path:
    """Persist an encrypted blob to disk under the given vault name.

    Returns the path where the vault was written.
    """
    ensure_vault_dir(vault_dir)
    path = get_vault_path(vault_name, vault_dir)
    payload = {"vault": vault_name, "data": encrypted_blob}
    try:
        path.write_text(json.dumps(payload), encoding="utf-8")
    except OSError as exc:
        raise EnvaultError(f"Failed to write vault '{vault_name}': {exc}") from exc
    return path


def load_vault(vault_name: str, vault_dir: Optional[Path] = None) -> str:
    """Load and return the encrypted blob for the given vault name.

    Raises EnvaultError if the vault does not exist or is malformed.
    """
    path = get_vault_path(vault_name, vault_dir)
    if not path.exists():
        raise EnvaultError(f"Vault '{vault_name}' not found at {path}")
    try:
        raw = path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        return payload["data"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        raise EnvaultError(f"Failed to read vault '{vault_name}': {exc}") from exc


def list_vaults(vault_dir: Optional[Path] = None) -> list[str]:
    """Return a sorted list of vault names stored in the vault directory."""
    base = vault_dir or DEFAULT_VAULT_DIR
    if not base.exists():
        return []
    return sorted(p.stem for p in base.glob("*.vault"))


def delete_vault(vault_name: str, vault_dir: Optional[Path] = None) -> None:
    """Delete a vault file from disk.

    Raises EnvaultError if the vault does not exist.
    """
    path = get_vault_path(vault_name, vault_dir)
    if not path.exists():
        raise EnvaultError(f"Vault '{vault_name}' not found at {path}")
    try:
        path.unlink()
    except OSError as exc:
        raise EnvaultError(f"Failed to delete vault '{vault_name}': {exc}") from exc
