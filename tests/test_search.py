"""Tests for envault.search and envault.cli_search."""

import argparse
import pytest

from unittest.mock import patch
from envault.search import search_vaults, SearchResult, SearchMatch
from envault.cli_search import cmd_search


FAKE_VAULTS = {
    "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123"},
    "prod": {"DB_HOST": "prod.db.example.com", "API_KEY": "xyz789"},
}


def _mock_pull(vault_name, passphrase):
    if passphrase != "correct":
        from envault.exceptions import DecryptionError
        raise DecryptionError("bad passphrase")
    return FAKE_VAULTS.get(vault_name, {})


def _mock_list():
    return list(FAKE_VAULTS.keys())


@pytest.fixture(autouse=True)
def patch_storage(monkeypatch):
    monkeypatch.setattr("envault.search.pull", _mock_pull)
    monkeypatch.setattr("envault.search.list_vaults", _mock_list)


def test_search_by_key_pattern():
    result = search_vaults(passphrase="correct", key_pattern="DB_")
    keys = [m.key for m in result.matches]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "SECRET_KEY" not in keys


def test_search_by_value_pattern():
    result = search_vaults(passphrase="correct", value_pattern="localhost")
    assert result.found
    assert all(m.value is None for m in result.matches)  # include_values=False default


def test_search_include_values():
    result = search_vaults(passphrase="correct", key_pattern="DB_HOST", include_values=True)
    values = [m.value for m in result.matches]
    assert "localhost" in values


def test_search_limits_to_specified_vaults():
    result = search_vaults(passphrase="correct", key_pattern="DB_HOST", vault_names=["dev"])
    assert all(m.vault_name == "dev" for m in result.matches)
    assert len(result.matches) == 1


def test_search_no_matches_returns_empty_result():
    result = search_vaults(passphrase="correct", key_pattern="NONEXISTENT_KEY_XYZ")
    assert not result.found
    assert result.matches == []


def test_search_skips_vaults_with_wrong_passphrase():
    result = search_vaults(passphrase="wrong", key_pattern="DB_")
    assert not result.found


def test_search_requires_at_least_one_pattern():
    with pytest.raises(ValueError):
        search_vaults(passphrase="correct")


def test_by_vault_groups_correctly():
    result = search_vaults(passphrase="correct", key_pattern="DB_HOST")
    grouped = result.by_vault()
    assert set(grouped.keys()) == {"dev", "prod"}


def test_cmd_search_prints_matches(capsys):
    args = argparse.Namespace(
        key="DB_HOST",
        value="",
        vaults=None,
        show_values=False,
        count=False,
        passphrase="correct",
    )
    cmd_search(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "[dev]" in out or "[prod]" in out


def test_cmd_search_no_pattern_exits(capsys):
    args = argparse.Namespace(
        key="",
        value="",
        vaults=None,
        show_values=False,
        count=False,
        passphrase="correct",
    )
    with pytest.raises(SystemExit) as exc:
        cmd_search(args)
    assert exc.value.code == 1
