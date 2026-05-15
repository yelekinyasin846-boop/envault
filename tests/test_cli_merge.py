"""Tests for envault.cli_merge."""

from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from envault.cli_merge import cmd_merge
from envault.merge import MergeError
from envault.vault import push


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def _seeded(vault_dir):
    push("v1", {"A": "1", "SHARED": "v1_val"}, "secret", vault_dir=vault_dir)
    push("v2", {"B": "2", "SHARED": "v2_val"}, "secret", vault_dir=vault_dir)
    return vault_dir


def _args(sources, dest, strategy="theirs", verbose=False):
    ns = argparse.Namespace(
        sources=sources,
        dest=dest,
        strategy=strategy,
        verbose=verbose,
    )
    return ns


def test_cmd_merge_success(capsys, _seeded):
    with patch("envault.cli_merge.getpass.getpass", return_value="secret"), \
         patch("envault.merge.pull", wraps=lambda n, p, **kw: __import__("envault.vault", fromlist=["pull"]).pull(n, p, **kw)), \
         patch("envault.merge.push", wraps=lambda n, v, p, **kw: __import__("envault.vault", fromlist=["push"]).push(n, v, p, **kw)):
        # Use real merge_vaults but inject vault_dir via monkeypatching merge_vaults directly
        from envault import merge as merge_mod
        original = merge_mod.merge_vaults

        def _wrapped(vault_names, passphrase, dest_vault, strategy, vault_dir=None):
            return original(vault_names, passphrase, dest_vault, strategy, vault_dir=_seeded)

        with patch("envault.cli_merge.merge_vaults", side_effect=_wrapped):
            cmd_merge(_args(["v1", "v2"], "merged"))

    out = capsys.readouterr().out
    assert "merged" in out.lower()
    assert "2" in out  # 2 source vaults


def test_cmd_merge_conflict_fail_exits(capsys):
    with patch("envault.cli_merge.getpass.getpass", return_value="secret"), \
         patch("envault.cli_merge.merge_vaults",
               side_effect=MergeError("Conflict", conflicts=["SHARED"])):
        with pytest.raises(SystemExit) as exc_info:
            cmd_merge(_args(["v1", "v2"], "merged", strategy="fail"))
    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "SHARED" in err


def test_cmd_merge_too_few_sources_exits(capsys):
    with patch("envault.cli_merge.getpass.getpass", return_value="secret"), \
         patch("envault.cli_merge.merge_vaults",
               side_effect=MergeError("At least two source vaults are required")):
        with pytest.raises(SystemExit):
            cmd_merge(_args(["only_one"], "dest"))
