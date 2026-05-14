"""Tag management for envault vaults.

Allows users to assign, remove, and query string tags on vaults,
stored as metadata alongside the encrypted blob in the vault JSON.
"""

from __future__ import annotations

from typing import List

from envault.exceptions import EnvaultError
from envault.storage import load_vault, save_vault


class TagError(EnvaultError):
    """Raised when a tag operation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


_MAX_TAG_LENGTH = 64
_MAX_TAGS_PER_VAULT = 20


def _validate_tag(tag: str) -> None:
    """Raise TagError if *tag* is not a valid tag string."""
    if not tag or not tag.strip():
        raise TagError("Tag must not be empty or whitespace.")
    if len(tag) > _MAX_TAG_LENGTH:
        raise TagError(
            f"Tag '{tag}' exceeds maximum length of {_MAX_TAG_LENGTH} characters."
        )
    if not all(c.isalnum() or c in "-_" for c in tag):
        raise TagError(
            f"Tag '{tag}' contains invalid characters. "
            "Only alphanumeric characters, hyphens, and underscores are allowed."
        )


def get_tags(vault_name: str, vault_dir: str | None = None) -> List[str]:
    """Return the list of tags for *vault_name*."""
    data = load_vault(vault_name, vault_dir=vault_dir)
    return list(data.get("tags", []))


def add_tag(vault_name: str, tag: str, vault_dir: str | None = None) -> List[str]:
    """Add *tag* to *vault_name* and return the updated tag list."""
    _validate_tag(tag)
    data = load_vault(vault_name, vault_dir=vault_dir)
    tags: List[str] = list(data.get("tags", []))
    if tag in tags:
        return tags
    if len(tags) >= _MAX_TAGS_PER_VAULT:
        raise TagError(
            f"Vault '{vault_name}' already has the maximum of "
            f"{_MAX_TAGS_PER_VAULT} tags."
        )
    tags.append(tag)
    data["tags"] = tags
    save_vault(vault_name, data, vault_dir=vault_dir)
    return tags


def remove_tag(vault_name: str, tag: str, vault_dir: str | None = None) -> List[str]:
    """Remove *tag* from *vault_name* and return the updated tag list."""
    data = load_vault(vault_name, vault_dir=vault_dir)
    tags: List[str] = list(data.get("tags", []))
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on vault '{vault_name}'.")
    tags.remove(tag)
    data["tags"] = tags
    save_vault(vault_name, data, vault_dir=vault_dir)
    return tags


def list_vaults_by_tag(tag: str, vault_dir: str | None = None) -> List[str]:
    """Return vault names that carry *tag*."""
    from envault.vault import list_vault_names

    matched: List[str] = []
    for name in list_vault_names(vault_dir=vault_dir):
        try:
            if tag in get_tags(name, vault_dir=vault_dir):
                matched.append(name)
        except Exception:
            pass
    return matched
