"""Tests for envault.merge."""

from __future__ import annotations

import pytest

from envault.merge import MergeError, MergeStrategy, merge_vaults
from envault.vault import pull


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def seeded(vault_dir):
    """Create two vaults with some overlapping and unique keys."""
    from envault.vault import push

    push("alpha", {"KEY_A": "alpha_a", "SHARED": "from_alpha", "ONLY_ALPHA": "yes"}, "pass", vault_dir=vault_dir)
    push("beta",  {"KEY_B": "beta_b",  "SHARED": "from_beta",  "ONLY_BETA": "yes"},  "pass", vault_dir=vault_dir)
    return vault_dir


def test_merge_combines_unique_keys(seeded):
    result = merge_vaults(["alpha", "beta"], "pass", "merged", vault_dir=seeded)
    merged = result["merged"]
    assert "KEY_A" in merged
    assert "KEY_B" in merged
    assert "ONLY_ALPHA" in merged
    assert "ONLY_BETA" in merged


def test_merge_strategy_theirs_wins(seeded):
    result = merge_vaults(["alpha", "beta"], "pass", "merged",
                          strategy=MergeStrategy.THEIRS, vault_dir=seeded)
    assert result["merged"]["SHARED"] == "from_beta"
    assert len(result["conflicts"]) == 1


def test_merge_strategy_ours_wins(seeded):
    result = merge_vaults(["alpha", "beta"], "pass", "merged",
                          strategy=MergeStrategy.OURS, vault_dir=seeded)
    assert result["merged"]["SHARED"] == "from_alpha"


def test_merge_strategy_fail_raises_on_conflict(seeded):
    with pytest.raises(MergeError) as exc_info:
        merge_vaults(["alpha", "beta"], "pass", "merged",
                     strategy=MergeStrategy.FAIL, vault_dir=seeded)
    assert "SHARED" in exc_info.value.conflicts


def test_merge_persists_to_dest_vault(seeded):
    merge_vaults(["alpha", "beta"], "pass", "dest_vault", vault_dir=seeded)
    env = pull("dest_vault", "pass", vault_dir=seeded)
    assert "KEY_A" in env
    assert "KEY_B" in env


def test_merge_requires_at_least_two_sources(vault_dir):
    with pytest.raises(MergeError, match="At least two"):
        merge_vaults(["only_one"], "pass", "dest", vault_dir=vault_dir)


def test_merge_returns_source_names(seeded):
    result = merge_vaults(["alpha", "beta"], "pass", "merged", vault_dir=seeded)
    assert result["sources"] == ["alpha", "beta"]
