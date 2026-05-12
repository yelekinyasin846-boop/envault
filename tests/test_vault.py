"""Tests for high-level vault push/pull/list operations."""

import pytest

from envault.exceptions import DecryptionError, EnvaultError
from envault.vault import export_dotenv, list_vault_names, pull, push


PASSPHRASE = "supersecret"
DOTENV_CONTENT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


@pytest.fixture(autouse=True)
def isolated_vault_dir(tmp_path, monkeypatch):
    """Redirect vault storage to a temporary directory for each test."""
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    import envault.storage as storage
    monkeypatch.setattr(storage, "_vault_dir", lambda: tmp_path)
    yield tmp_path


def test_push_returns_vault_name():
    name = push("myapp", DOTENV_CONTENT, PASSPHRASE)
    assert name == "myapp"


def test_pull_returns_correct_vars():
    push("myapp", DOTENV_CONTENT, PASSPHRASE)
    env = pull("myapp", PASSPHRASE)
    assert env["DB_HOST"] == "localhost"
    assert env["DB_PORT"] == "5432"
    assert env["SECRET"] == "abc123"


def test_pull_nonexistent_vault_raises():
    with pytest.raises(EnvaultError, match="does not exist"):
        pull("ghost", PASSPHRASE)


def test_pull_wrong_passphrase_raises():
    push("myapp", DOTENV_CONTENT, PASSPHRASE)
    with pytest.raises(DecryptionError):
        pull("myapp", "wrongpassphrase")


def test_list_vault_names_empty():
    assert list_vault_names() == []


def test_list_vault_names_after_push():
    push("alpha", DOTENV_CONTENT, PASSPHRASE)
    push("beta", DOTENV_CONTENT, PASSPHRASE)
    names = list_vault_names()
    assert names == ["alpha", "beta"]


def test_export_dotenv_roundtrip():
    push("myapp", DOTENV_CONTENT, PASSPHRASE)
    result = export_dotenv("myapp", PASSPHRASE)
    assert "DB_HOST=localhost" in result
    assert "SECRET=abc123" in result


def test_push_invalid_dotenv_raises():
    with pytest.raises(EnvaultError):
        push("bad", "===NOTVALID===", PASSPHRASE)
