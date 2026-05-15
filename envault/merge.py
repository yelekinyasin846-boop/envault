"""Merge two or more vaults into a single vault, with conflict resolution."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Tuple

from envault.exceptions import EnvaultError
from envault.vault import pull, push


class MergeStrategy(str, Enum):
    OURS = "ours"       # keep value from the first (base) vault on conflict
    THEIRS = "theirs"   # keep value from the last source vault on conflict
    FAIL = "fail"       # raise an error on any conflict


class MergeError(EnvaultError):
    def __init__(self, message: str, conflicts: List[str] | None = None):
        super().__init__(message)
        self.conflicts: List[str] = conflicts or []


MergeResult = Dict[str, object]  # {"merged": dict, "conflicts": list, "sources": list}


def merge_vaults(
    vault_names: List[str],
    passphrase: str,
    dest_vault: str,
    strategy: MergeStrategy = MergeStrategy.THEIRS,
    vault_dir: str | None = None,
) -> MergeResult:
    """Pull *vault_names*, merge them, and push to *dest_vault*.

    Returns a dict with keys ``merged``, ``conflicts``, and ``sources``.
    """
    if len(vault_names) < 2:
        raise MergeError("At least two source vaults are required for a merge.")

    merged: Dict[str, str] = {}
    conflicts: List[Tuple[str, str, str]] = []  # (key, existing_val, new_val)

    kwargs = {"vault_dir": vault_dir} if vault_dir else {}

    for name in vault_names:
        env_vars = pull(name, passphrase, **kwargs)
        for key, value in env_vars.items():
            if key in merged and merged[key] != value:
                conflicts.append((key, merged[key], value))
                if strategy is MergeStrategy.FAIL:
                    conflict_keys = [c[0] for c in conflicts]
                    raise MergeError(
                        f"Conflict on key '{key}' between vaults. "
                        "Use a different strategy to resolve.",
                        conflicts=conflict_keys,
                    )
                if strategy is MergeStrategy.THEIRS:
                    merged[key] = value
                # MergeStrategy.OURS: keep existing value (do nothing)
            else:
                merged[key] = value

    push(dest_vault, merged, passphrase, **kwargs)

    return {
        "merged": merged,
        "conflicts": [(k, ov, nv) for k, ov, nv in conflicts],
        "sources": list(vault_names),
    }
