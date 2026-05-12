"""Tests for envault.cli_rotate — rotate CLI sub-command."""

import argparse
import sys
from unittest.mock import patch

import pytest

from envault.cli_rotate import cmd_rotate, build_rotate_subparser
from envault.crypto import encrypt
from envault.storage import save_vault


PLAINTEXT = b"KEY=value"
OLD_PASS = "old"
NEW_PASS = "new"


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path)
    blob = encrypt(PLAINTEXT, OLD_PASS)
    save_vault("testvault", blob, vault_dir=d)
    return d


def _make_args(vault=None, all_vaults=False, vault_dir=None):
    ns = argparse.Namespace(vault=vault, all=all_vaults, vault_dir=vault_dir)
    return ns


def test_cmd_rotate_single_vault_success(vault_dir, capsys):
    args = _make_args(vault="testvault", vault_dir=vault_dir)
    with patch("getpass.getpass", side_effect=[OLD_PASS, NEW_PASS, NEW_PASS]):
        cmd_rotate(args)
    captured = capsys.readouterr()
    assert "testvault" in captured.out
    assert "successfully" in captured.out


def test_cmd_rotate_passphrase_mismatch_exits(vault_dir, capsys):
    args = _make_args(vault="testvault", vault_dir=vault_dir)
    with patch("getpass.getpass", side_effect=[OLD_PASS, NEW_PASS, "different"]):
        with pytest.raises(SystemExit) as exc_info:
            cmd_rotate(args)
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "do not match" in captured.err


def test_cmd_rotate_wrong_old_passphrase_exits(vault_dir, capsys):
    args = _make_args(vault="testvault", vault_dir=vault_dir)
    with patch("getpass.getpass", side_effect=["wrong", NEW_PASS, NEW_PASS]):
        with pytest.raises(SystemExit) as exc_info:
            cmd_rotate(args)
    assert exc_info.value.code == 1


def test_cmd_rotate_all_vaults(vault_dir, capsys):
    args = _make_args(all_vaults=True, vault_dir=vault_dir)
    with patch("getpass.getpass", side_effect=[OLD_PASS, NEW_PASS, NEW_PASS]):
        cmd_rotate(args)
    captured = capsys.readouterr()
    assert "1 vault" in captured.out


def test_build_rotate_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    build_rotate_subparser(subparsers)
    args = parser.parse_args(["rotate", "--vault", "myvault"])
    assert args.vault == "myvault"
    assert args.all is False


def test_build_rotate_subparser_all_flag():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    build_rotate_subparser(subparsers)
    args = parser.parse_args(["rotate", "--all"])
    assert args.all is True
    assert args.vault is None
