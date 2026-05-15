"""Tests for envault.cli_import"""

import argparse
import json
import sys
import pytest

from envault.cli_import import cmd_import, build_import_subparser
from envault.vault import pull


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    """Redirect vault storage to a temp directory."""
    monkeypatch.setattr("envault.storage.VAULT_DIR", str(tmp_path))
    monkeypatch.setattr("envault.vault.VAULT_DIR", str(tmp_path))
    return tmp_path


def _args(vault_dir, **kwargs):
    defaults = dict(
        vault="myapp",
        passphrase="secret",
        format="dotenv",
        source=".env",
        prefix=None,
        vault_dir=str(vault_dir),
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_import_dotenv(tmp_path, vault_dir, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=123\n")
    args = _args(vault_dir, format="dotenv", source=str(env_file))
    cmd_import(args)
    out = capsys.readouterr().out
    assert "2 variable(s)" in out
    assert "myapp" in out


def test_cmd_import_json(tmp_path, vault_dir, capsys):
    jf = tmp_path / "vars.json"
    jf.write_text(json.dumps({"KEY": "val"}))
    args = _args(vault_dir, format="json", source=str(jf))
    cmd_import(args)
    out = capsys.readouterr().out
    assert "1 variable(s)" in out


def test_cmd_import_missing_source_exits(tmp_path, vault_dir):
    args = _args(vault_dir, format="dotenv", source="/no/such/.env")
    with pytest.raises(SystemExit) as exc_info:
        cmd_import(args)
    assert exc_info.value.code == 1


def test_cmd_import_empty_env_exits(tmp_path, vault_dir, monkeypatch):
    monkeypatch.setattr("envault.import_.import_from_env", lambda prefix=None: {})
    args = _args(vault_dir, format="env")
    with pytest.raises(SystemExit) as exc_info:
        cmd_import(args)
    assert exc_info.value.code == 1


def test_build_import_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_import_subparser(subs)
    parsed = parser.parse_args(["import", "myvault", "mypass", "--format", "json", "--source", "f.json"])
    assert parsed.vault == "myvault"
    assert parsed.passphrase == "mypass"
    assert parsed.format == "json"
    assert parsed.source == "f.json"
