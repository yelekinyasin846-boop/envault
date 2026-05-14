"""Tests for envault.cli_diff subcommand."""

import argparse
import sys
import pytest
from unittest.mock import patch, MagicMock

from envault.cli_diff import cmd_diff, build_diff_subparser


ENV_A = {"HOST": "localhost", "PORT": "5432"}
ENV_B = {"HOST": "prod", "PORT": "5432"}


def _make_args(**kwargs):
    defaults = {
        "vault_a": "dev",
        "vault_b": None,
        "file": None,
        "redact": False,
        "exit_code": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@patch("envault.cli_diff.getpass", return_value="secret")
@patch("envault.cli_diff.pull")
def test_diff_two_vaults_no_changes(mock_pull, mock_getpass, capsys):
    mock_pull.side_effect = [ENV_A, ENV_A]
    args = _make_args(vault_b="prod")
    cmd_diff(args)  # should not raise
    out = capsys.readouterr().out
    assert "no changes" in out


@patch("envault.cli_diff.getpass", return_value="secret")
@patch("envault.cli_diff.pull")
def test_diff_two_vaults_with_changes_exits_zero_without_flag(mock_pull, mock_getpass):
    mock_pull.side_effect = [ENV_A, ENV_B]
    args = _make_args(vault_b="prod", exit_code=False)
    cmd_diff(args)  # should not sys.exit(1)


@patch("envault.cli_diff.getpass", return_value="secret")
@patch("envault.cli_diff.pull")
def test_diff_two_vaults_exit_code_flag_exits_one_on_changes(mock_pull, mock_getpass):
    mock_pull.side_effect = [ENV_A, ENV_B]
    args = _make_args(vault_b="prod", exit_code=True)
    with pytest.raises(SystemExit) as exc_info:
        cmd_diff(args)
    assert exc_info.value.code == 1


@patch("envault.cli_diff.getpass", return_value="secret")
@patch("envault.cli_diff.pull")
def test_diff_bad_vault_exits(mock_pull, mock_getpass):
    from envault.exceptions import EnvaultError
    mock_pull.side_effect = EnvaultError("not found")
    args = _make_args(vault_b="prod")
    with pytest.raises(SystemExit) as exc_info:
        cmd_diff(args)
    assert exc_info.value.code == 1


@patch("envault.cli_diff.getpass", return_value="secret")
@patch("envault.cli_diff.pull")
def test_diff_no_comparison_target_exits(mock_pull, mock_getpass):
    mock_pull.return_value = ENV_A
    args = _make_args()  # vault_b=None, file=None
    with pytest.raises(SystemExit) as exc_info:
        cmd_diff(args)
    assert exc_info.value.code == 1


def test_build_diff_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    build_diff_subparser(subparsers)
    args = parser.parse_args(["diff", "myvault", "--vault-b", "other"])
    assert args.vault_a == "myvault"
    assert args.vault_b == "other"
