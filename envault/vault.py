"""High-level vault operations: push, pull, and list env vars."""

from typing import Dict, Optional

from envault.crypto import encrypt, decrypt
from envault.dotenv import parse_dotenv, serialize_dotenv
from envault.exceptions import DecryptionError, EnvaultError
from envault.storage import ensure_vault_dir, load_vault, save_vault, list_vaults


def push(vault_name: str, dotenv_content: str, passphrase: str) -> str:
    """Encrypt and store dotenv content into a named vault.

    Returns the vault name on success.
    """
    try:
        parsed = parse_dotenv(dotenv_content)
    except Exception as exc:
        raise EnvaultError(f"Failed to parse .env content: {exc}") from exc

    plain = serialize_dotenv(parsed)
    blob = encrypt(plain, passphrase)

    ensure_vault_dir()
    save_vault(vault_name, blob)
    return vault_name


def pull(vault_name: str, passphrase: str) -> Dict[str, str]:
    """Load and decrypt a named vault, returning a dict of env vars."""
    ensure_vault_dir()
    blob: Optional[str] = load_vault(vault_name)

    if blob is None:
        raise EnvaultError(f"Vault '{vault_name}' does not exist.")

    try:
        plain = decrypt(blob, passphrase)
    except DecryptionError as exc:
        raise DecryptionError(f"Could not decrypt vault '{vault_name}': {exc}") from exc

    return parse_dotenv(plain)


def list_vault_names() -> list:
    """Return a sorted list of available vault names."""
    ensure_vault_dir()
    return sorted(list_vaults())


def export_dotenv(vault_name: str, passphrase: str) -> str:
    """Return the decrypted vault content as a .env-formatted string."""
    env_vars = pull(vault_name, passphrase)
    return serialize_dotenv(env_vars)
