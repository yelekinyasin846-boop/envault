"""Tests for envault.rotate — passphrase rotation."""

import pytest

from envault.rotate import rotate_vault, rotate_all_vaults, RotationError
from envault.storage import save_vault, load_vault, list_vaults
from envault.crypto import encrypt, decrypt


PLAINTEXT = b"SECRET=hunter2\nDB_URL=postgres://localhost/mydb"
OLD_PASS = "old-correct-passphrase"
NEW_PASS = "new-secure-passphrase"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def seeded_vault(vault_dir):
    blob = encrypt(PLAINTEXT, OLD_PASS)
    save_vault("myvault", blob, vault_dir=vault_dir)
    return vault_dir


def test_rotate_vault_re_encrypts_with_new_passphrase(seeded_vault):
    rotate_vault("myvault", OLD_PASS, NEW_PASS, vault_dir=seeded_vault)
    new_blob = load_vault("myvault", vault_dir=seeded_vault)
    recovered = decrypt(new_blob, NEW_PASS)
    assert recovered == PLAINTEXT


def test_rotate_vault_old_passphrase_no_longer_works(seeded_vault):
    from envault.exceptions import DecryptionError
    rotate_vault("myvault", OLD_PASS, NEW_PASS, vault_dir=seeded_vault)
    new_blob = load_vault("myvault", vault_dir=seeded_vault)
    with pytest.raises(DecryptionError):
        decrypt(new_blob, OLD_PASS)


def test_rotate_vault_wrong_old_passphrase_raises(seeded_vault):
    with pytest.raises(RotationError) as exc_info:
        rotate_vault("myvault", "wrong-passphrase", NEW_PASS, vault_dir=seeded_vault)
    assert "myvault" in exc_info.value.message


def test_rotate_nonexistent_vault_raises(vault_dir):
    with pytest.raises(RotationError) as exc_info:
        rotate_vault("ghost", OLD_PASS, NEW_PASS, vault_dir=vault_dir)
    assert "ghost" in exc_info.value.message


def test_rotate_all_vaults_rotates_every_vault(vault_dir):
    for name in ("alpha", "beta", "gamma"):
        blob = encrypt(PLAINTEXT, OLD_PASS)
        save_vault(name, blob, vault_dir=vault_dir)

    rotated = rotate_all_vaults(OLD_PASS, NEW_PASS, vault_dir=vault_dir)
    assert set(rotated) == {"alpha", "beta", "gamma"}

    for name in rotated:
        blob = load_vault(name, vault_dir=vault_dir)
        assert decrypt(blob, NEW_PASS) == PLAINTEXT


def test_rotate_all_vaults_empty_dir_returns_empty_list(vault_dir):
    result = rotate_all_vaults(OLD_PASS, NEW_PASS, vault_dir=vault_dir)
    assert result == []


def test_rotation_error_stores_message():
    err = RotationError("something went wrong")
    assert err.message == "something went wrong"
    assert isinstance(err, Exception)
