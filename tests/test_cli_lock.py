"""Tests for envault.cli_lock."""

import argparse
import pytest
from unittest.mock import patch, MagicMock
from envault.cli_lock import cmd_lock, cmd_unlock, cmd_lock_status
from envault.lock import LockError


def _args(vault_name, vault_dir=None):
    ns = argparse.Namespace(vault_name=vault_name, vault_dir=vault_dir)
    return ns


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / "vaults"
    d.mkdir()
    (d / "alpha.enc").write_text("{}")
    return str(d)


def test_cmd_lock_success(vault_dir, capsys):
    cmd_lock(_args("alpha", vault_dir=vault_dir))
    out = capsys.readouterr().out
    assert "locked" in out


def test_cmd_lock_already_locked_exits(vault_dir):
    cmd_lock(_args("alpha", vault_dir=vault_dir))
    with pytest.raises(SystemExit) as exc:
        cmd_lock(_args("alpha", vault_dir=vault_dir))
    assert exc.value.code == 1


def test_cmd_unlock_success(vault_dir, capsys):
    cmd_lock(_args("alpha", vault_dir=vault_dir))
    cmd_unlock(_args("alpha", vault_dir=vault_dir))
    out = capsys.readouterr().out
    assert "unlocked" in out


def test_cmd_unlock_when_not_locked(vault_dir, capsys):
    cmd_unlock(_args("alpha", vault_dir=vault_dir))
    out = capsys.readouterr().out
    assert "not locked" in out


def test_cmd_lock_status_locked(vault_dir, capsys):
    cmd_lock(_args("alpha", vault_dir=vault_dir))
    capsys.readouterr()  # clear
    cmd_lock_status(_args("alpha", vault_dir=vault_dir))
    out = capsys.readouterr().out
    assert "locked" in out


def test_cmd_lock_status_unlocked(vault_dir, capsys):
    cmd_lock_status(_args("alpha", vault_dir=vault_dir))
    out = capsys.readouterr().out
    assert "unlocked" in out
