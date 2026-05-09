"""Tests for envault.crypto encryption and decryption."""

import pytest
from cryptography.exceptions import InvalidTag

from envault.crypto import encrypt, decrypt, derive_key, SALT_SIZE, KEY_SIZE


PASSPHRASE = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/db\nSECRET_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSPHRASE)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_decrypt_roundtrip():
    blob = encrypt(PLAINTEXT, PASSPHRASE)
    recovered = decrypt(blob, PASSPHRASE)
    assert recovered == PLAINTEXT


def test_encrypt_produces_unique_blobs():
    blob1 = encrypt(PLAINTEXT, PASSPHRASE)
    blob2 = encrypt(PLAINTEXT, PASSPHRASE)
    assert blob1 != blob2, "Each encryption call should produce a unique blob due to random salt/nonce"


def test_decrypt_wrong_passphrase_raises():
    blob = encrypt(PLAINTEXT, PASSPHRASE)
    with pytest.raises(InvalidTag):
        decrypt(blob, "wrong-passphrase")


def test_decrypt_corrupted_blob_raises():
    blob = encrypt(PLAINTEXT, PASSPHRASE)
    corrupted = blob[:-4] + "AAAA"
    with pytest.raises(Exception):
        decrypt(corrupted, PASSPHRASE)


def test_derive_key_deterministic():
    import os
    salt = os.urandom(SALT_SIZE)
    key1 = derive_key(PASSPHRASE, salt)
    key2 = derive_key(PASSPHRASE, salt)
    assert key1 == key2
    assert len(key1) == KEY_SIZE


def test_derive_key_different_salts_produce_different_keys():
    import os
    salt1 = os.urandom(SALT_SIZE)
    salt2 = os.urandom(SALT_SIZE)
    key1 = derive_key(PASSPHRASE, salt1)
    key2 = derive_key(PASSPHRASE, salt2)
    assert key1 != key2


def test_encrypt_empty_string():
    blob = encrypt("", PASSPHRASE)
    assert decrypt(blob, PASSPHRASE) == ""


def test_encrypt_unicode_content():
    unicode_text = "API_KEY=🔑secret\nNAME=tëst"
    blob = encrypt(unicode_text, PASSPHRASE)
    assert decrypt(blob, PASSPHRASE) == unicode_text
