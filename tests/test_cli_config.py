"""Tests for the config CLI sub-commands."""

import argparse
import pytest

from envault.cli_config import (
    build_config_subparser,
    cmd_config_get,
    cmd_config_list,
    cmd_config_set,
)
from envault.config import load_config, DEFAULT_CONFIG
from envault.exceptions import EnvaultError


@pytest.fixture(autouse=True)
def isolate_config(tmp_path, monkeypatch):
    """Redirect config reads/writes to a temp directory."""
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("ENVAULT_CONFIG", str(config_path))
    return config_path


def _make_args(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_config_set_and_get_bool(capsys):
    cmd_config_set(_make_args(key="auto_backup", value="true"))
    cmd_config_get(_make_args(key="auto_backup"))
    out = capsys.readouterr().out
    assert "auto_backup = True" in out


def test_config_set_string_value(capsys):
    cmd_config_set(_make_args(key="vault_dir", value="/custom/path"))
    cmd_config_get(_make_args(key="vault_dir"))
    out = capsys.readouterr().out
    assert "/custom/path" in out


def test_config_list_shows_all_keys(capsys):
    cmd_config_list(_make_args())
    out = capsys.readouterr().out
    for key in DEFAULT_CONFIG:
        assert key in out


def test_config_get_unknown_key_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cmd_config_get(_make_args(key="nonexistent"))
    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "Error" in err


def test_config_set_unknown_key_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cmd_config_set(_make_args(key="nonexistent", value="x"))
    assert exc_info.value.code == 1


def test_build_config_subparser_registers_commands():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    build_config_subparser(subs)
    args = parser.parse_args(["config", "set", "auto_backup", "false"])
    assert args.key == "auto_backup"
    assert args.value == "false"


def test_config_set_false_string(capsys):
    cmd_config_set(_make_args(key="auto_backup", value="false"))
    cmd_config_get(_make_args(key="auto_backup"))
    out = capsys.readouterr().out
    assert "False" in out
