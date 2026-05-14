"""Tests for envault.tags."""

from __future__ import annotations

import pytest

from envault.tags import (
    TagError,
    _MAX_TAG_LENGTH,
    _MAX_TAGS_PER_VAULT,
    add_tag,
    get_tags,
    list_vaults_by_tag,
    remove_tag,
)
from envault.vault import push


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def seeded_vault(vault_dir):
    push({"KEY": "val"}, "myvault", "secret", vault_dir=vault_dir)
    return "myvault"


def test_get_tags_empty_by_default(seeded_vault, vault_dir):
    assert get_tags(seeded_vault, vault_dir=vault_dir) == []


def test_add_tag_returns_updated_list(seeded_vault, vault_dir):
    tags = add_tag(seeded_vault, "production", vault_dir=vault_dir)
    assert "production" in tags


def test_add_tag_persists(seeded_vault, vault_dir):
    add_tag(seeded_vault, "staging", vault_dir=vault_dir)
    assert "staging" in get_tags(seeded_vault, vault_dir=vault_dir)


def test_add_duplicate_tag_is_idempotent(seeded_vault, vault_dir):
    add_tag(seeded_vault, "ci", vault_dir=vault_dir)
    tags = add_tag(seeded_vault, "ci", vault_dir=vault_dir)
    assert tags.count("ci") == 1


def test_remove_tag(seeded_vault, vault_dir):
    add_tag(seeded_vault, "to-remove", vault_dir=vault_dir)
    tags = remove_tag(seeded_vault, "to-remove", vault_dir=vault_dir)
    assert "to-remove" not in tags


def test_remove_nonexistent_tag_raises(seeded_vault, vault_dir):
    with pytest.raises(TagError, match="not found"):
        remove_tag(seeded_vault, "ghost", vault_dir=vault_dir)


def test_add_empty_tag_raises(seeded_vault, vault_dir):
    with pytest.raises(TagError, match="empty"):
        add_tag(seeded_vault, "", vault_dir=vault_dir)


def test_add_tag_with_invalid_chars_raises(seeded_vault, vault_dir):
    with pytest.raises(TagError, match="invalid characters"):
        add_tag(seeded_vault, "bad tag!", vault_dir=vault_dir)


def test_add_tag_exceeding_max_length_raises(seeded_vault, vault_dir):
    long_tag = "a" * (_MAX_TAG_LENGTH + 1)
    with pytest.raises(TagError, match="exceeds maximum length"):
        add_tag(seeded_vault, long_tag, vault_dir=vault_dir)


def test_add_too_many_tags_raises(seeded_vault, vault_dir):
    for i in range(_MAX_TAGS_PER_VAULT):
        add_tag(seeded_vault, f"tag-{i}", vault_dir=vault_dir)
    with pytest.raises(TagError, match="maximum"):
        add_tag(seeded_vault, "one-too-many", vault_dir=vault_dir)


def test_list_vaults_by_tag(vault_dir):
    push({"A": "1"}, "vault-a", "pass", vault_dir=vault_dir)
    push({"B": "2"}, "vault-b", "pass", vault_dir=vault_dir)
    add_tag("vault-a", "shared", vault_dir=vault_dir)
    add_tag("vault-b", "shared", vault_dir=vault_dir)
    add_tag("vault-b", "extra", vault_dir=vault_dir)
    result = list_vaults_by_tag("shared", vault_dir=vault_dir)
    assert set(result) == {"vault-a", "vault-b"}


def test_list_vaults_by_tag_no_match(vault_dir):
    push({"X": "y"}, "lone", "pass", vault_dir=vault_dir)
    assert list_vaults_by_tag("nonexistent", vault_dir=vault_dir) == []
