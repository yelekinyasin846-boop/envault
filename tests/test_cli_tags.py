"""Tests for envault.cli_tags CLI sub-commands."""

from __future__ import annotations

import argparse
import sys

import pytest

from envault.cli_tags import (
    build_tags_subparser,
    cmd_tag_add,
    cmd_tag_list,
    cmd_tag_remove,
    cmd_tag_search,
)
from envault.tags import add_tag
from envault.vault import push


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture(autouse=True)
def _seeded(vault_dir):
    push({"K": "v"}, "testvault", "pass", vault_dir=vault_dir)


def _args(vault_dir, **kwargs):
    ns = argparse.Namespace(vault_dir=vault_dir, **kwargs)
    return ns


def test_cmd_tag_add_prints_tags(vault_dir, capsys):
    cmd_tag_add(_args(vault_dir, vault="testvault", tag="prod"))
    out = capsys.readouterr().out
    assert "prod" in out


def test_cmd_tag_list_shows_tags(vault_dir, capsys):
    add_tag("testvault", "staging", vault_dir=vault_dir)
    cmd_tag_list(_args(vault_dir, vault="testvault"))
    out = capsys.readouterr().out
    assert "staging" in out


def test_cmd_tag_list_empty_message(vault_dir, capsys):
    cmd_tag_list(_args(vault_dir, vault="testvault"))
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_remove_success(vault_dir, capsys):
    add_tag("testvault", "to-del", vault_dir=vault_dir)
    cmd_tag_remove(_args(vault_dir, vault="testvault", tag="to-del"))
    out = capsys.readouterr().out
    assert "to-del" not in out


def test_cmd_tag_remove_missing_tag_exits(vault_dir):
    with pytest.raises(SystemExit) as exc_info:
        cmd_tag_remove(_args(vault_dir, vault="testvault", tag="ghost"))
    assert exc_info.value.code == 1


def test_cmd_tag_add_invalid_tag_exits(vault_dir):
    with pytest.raises(SystemExit) as exc_info:
        cmd_tag_add(_args(vault_dir, vault="testvault", tag="bad tag!"))
    assert exc_info.value.code == 1


def test_cmd_tag_search_finds_vault(vault_dir, capsys):
    add_tag("testvault", "searchable", vault_dir=vault_dir)
    cmd_tag_search(_args(vault_dir, tag="searchable"))
    out = capsys.readouterr().out
    assert "testvault" in out


def test_cmd_tag_search_no_match_message(vault_dir, capsys):
    cmd_tag_search(_args(vault_dir, tag="nobody-has-this"))
    out = capsys.readouterr().out
    assert "No vaults found" in out


def test_build_tags_subparser_registers_commands():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    build_tags_subparser(subs)
    args = parser.parse_args(["tag", "add", "myvault", "mytag"])
    assert args.vault == "myvault"
    assert args.tag == "mytag"
    assert args.func is cmd_tag_add
