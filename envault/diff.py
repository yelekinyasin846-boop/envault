"""Utilities for diffing two sets of environment variables."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DiffResult:
    """Holds the result of comparing two env var dicts."""
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # key -> (old, new)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for key, val in sorted(self.added.items()):
            lines.append(f"  + {key}={val}")
        for key, val in sorted(self.removed.items()):
            lines.append(f"  - {key}={val}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"  ~ {key}: {old!r} -> {new!r}")
        if not lines:
            return "  (no changes)"
        return "\n".join(lines)


def diff_envs(
    old: Dict[str, str],
    new: Dict[str, str],
    redact_values: bool = False,
) -> DiffResult:
    """Compare two env var dicts and return a DiffResult.

    Args:
        old: The baseline environment variables.
        new: The updated environment variables.
        redact_values: If True, replace values with '***' in the result.
    """
    def _val(v: str) -> str:
        return "***" if redact_values else v

    result = DiffResult()
    old_keys = set(old)
    new_keys = set(new)

    for key in new_keys - old_keys:
        result.added[key] = _val(new[key])

    for key in old_keys - new_keys:
        result.removed[key] = _val(old[key])

    for key in old_keys & new_keys:
        if old[key] != new[key]:
            result.changed[key] = (_val(old[key]), _val(new[key]))
        else:
            result.unchanged[key] = _val(old[key])

    return result
