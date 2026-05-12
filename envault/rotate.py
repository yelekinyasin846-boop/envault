"""Passphrase rotation for existing vaults."""

from envault.storage import load_vault, save_vault, list_vaults
from envault.crypto import encrypt, decrypt
from envault.exceptions import DecryptionError, EnvaultError
from envault.audit import record_event


class RotationError(EnvaultError):
    """Raised when passphrase rotation fails."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def rotate_vault(vault_name: str, old_passphrase: str, new_passphrase: str, vault_dir: str = None) -> None:
    """Re-encrypt a single vault with a new passphrase.

    Args:
        vault_name: Name of the vault to rotate.
        old_passphrase: Current passphrase used to decrypt the vault.
        new_passphrase: New passphrase to encrypt the vault with.
        vault_dir: Optional override for vault directory.

    Raises:
        RotationError: If decryption with old passphrase fails or vault not found.
    """
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}

    blob = load_vault(vault_name, **kwargs)
    if blob is None:
        raise RotationError(f"Vault '{vault_name}' does not exist.")

    try:
        plaintext = decrypt(blob, old_passphrase)
    except DecryptionError as exc:
        raise RotationError(f"Failed to decrypt vault '{vault_name}': {exc.message}") from exc

    new_blob = encrypt(plaintext, new_passphrase)
    save_vault(vault_name, new_blob, **kwargs)
    record_event("rotate", vault_name)


def rotate_all_vaults(old_passphrase: str, new_passphrase: str, vault_dir: str = None) -> list:
    """Rotate passphrase for every vault in the vault directory.

    Returns:
        List of vault names that were successfully rotated.

    Raises:
        RotationError: If any vault fails to rotate (operation stops at first failure).
    """
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    names = list_vaults(**kwargs)
    rotated = []
    for name in names:
        rotate_vault(name, old_passphrase, new_passphrase, vault_dir=vault_dir)
        rotated.append(name)
    return rotated
