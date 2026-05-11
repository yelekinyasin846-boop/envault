"""Tests for envault.storage — local vault persistence."""

import json
from pathlib import Path

import pytest

from envault.exceptions import EnvaultError
from envault.storage import (
    delete_vault,
    get_vault_path,
    list_vaults,
    load_vault,
    save_vault,
)

BLOB = "gAAAAABencrypted_example_blob=="


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path / "vaults"


def test_get_vault_path_returns_correct_filename(vault_dir):
    path = get_vault_path("myproject", vault_dir)
    assert path.name == "myproject.vault"
    assert path.parent == vault_dir


def test_save_vault_creates_file(vault_dir):
    path = save_vault("demo", BLOB, vault_dir)
    assert path.exists()


def test_save_vault_stores_valid_json(vault_dir):
    save_vault("demo", BLOB, vault_dir)
    raw = (vault_dir / "demo.vault").read_text(encoding="utf-8")
    payload = json.loads(raw)
    assert payload["vault"] == "demo"
    assert payload["data"] == BLOB


def test_load_vault_returns_blob(vault_dir):
    save_vault("demo", BLOB, vault_dir)
    loaded = load_vault("demo", vault_dir)
    assert loaded == BLOB


def test_load_vault_missing_raises(vault_dir):
    with pytest.raises(EnvaultError, match="not found"):
        load_vault("nonexistent", vault_dir)


def test_load_vault_corrupted_raises(vault_dir):
    vault_dir.mkdir(parents=True, exist_ok=True)
    (vault_dir / "bad.vault").write_text("not json", encoding="utf-8")
    with pytest.raises(EnvaultError):
        load_vault("bad", vault_dir)


def test_list_vaults_empty_when_no_dir(vault_dir):
    assert list_vaults(vault_dir) == []


def test_list_vaults_returns_names(vault_dir):
    save_vault("alpha", BLOB, vault_dir)
    save_vault("beta", BLOB, vault_dir)
    save_vault("gamma", BLOB, vault_dir)
    assert list_vaults(vault_dir) == ["alpha", "beta", "gamma"]


def test_delete_vault_removes_file(vault_dir):
    save_vault("temp", BLOB, vault_dir)
    delete_vault("temp", vault_dir)
    assert not get_vault_path("temp", vault_dir).exists()


def test_delete_vault_missing_raises(vault_dir):
    with pytest.raises(EnvaultError, match="not found"):
        delete_vault("ghost", vault_dir)


def test_save_vault_overwrites_existing(vault_dir):
    save_vault("proj", BLOB, vault_dir)
    new_blob = "gAAAAABupdated_blob=="
    save_vault("proj", new_blob, vault_dir)
    assert load_vault("proj", vault_dir) == new_blob
