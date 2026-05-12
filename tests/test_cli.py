"""Tests for the CLI layer (cmd_push, cmd_pull, cmd_list)."""

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.cli import build_parser, cmd_list, cmd_pull, cmd_push


DOTENV_CONTENT = "APP_ENV=production\nDEBUG=false\n"
PASSPHRASE = "clitest"


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(DOTENV_CONTENT)
    return p


def _make_args(**kwargs):
    return argparse.Namespace(**kwargs)


def test_push_missing_file_exits(capsys):
    args = _make_args(vault="myapp", file="/nonexistent/.env")
    with pytest.raises(SystemExit) as exc_info:
        cmd_push(args)
    assert exc_info.value.code == 1


def test_push_and_pull_via_cmd(tmp_path, env_file, monkeypatch):
    import envault.storage as storage
    monkeypatch.setattr(storage, "_vault_dir", lambda: tmp_path)

    with patch("envault.cli.getpass", return_value=PASSPHRASE):
        args = _make_args(vault="myapp", file=str(env_file))
        cmd_push(args)

    out_file = tmp_path / "output.env"
    with patch("envault.cli.getpass", return_value=PASSPHRASE):
        args = _make_args(vault="myapp", output=str(out_file))
        cmd_pull(args)

    content = out_file.read_text()
    assert "APP_ENV=production" in content


def test_list_empty(tmp_path, monkeypatch, capsys):
    import envault.storage as storage
    monkeypatch.setattr(storage, "_vault_dir", lambda: tmp_path)
    cmd_list(_make_args())
    out = capsys.readouterr().out
    assert "No vaults found" in out


def test_build_parser_push():
    parser = build_parser()
    args = parser.parse_args(["push", "myapp", "--file", ".env"])
    assert args.command == "push"
    assert args.vault == "myapp"


def test_build_parser_list():
    parser = build_parser()
    args = parser.parse_args(["list"])
    assert args.command == "list"
