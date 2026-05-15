"""Search across vaults for keys or values."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import pull
from envault.storage import list_vaults
from envault.exceptions import EnvaultError


@dataclass
class SearchMatch:
    vault_name: str
    key: str
    value: Optional[str] = None

    def as_dict(self) -> Dict:
        return {"vault": self.vault_name, "key": self.key, "value": self.value}


@dataclass
class SearchResult:
    matches: List[SearchMatch] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return len(self.matches) > 0

    def by_vault(self) -> Dict[str, List[SearchMatch]]:
        result: Dict[str, List[SearchMatch]] = {}
        for m in self.matches:
            result.setdefault(m.vault_name, []).append(m)
        return result


def search_vaults(
    passphrase: str,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    vault_names: Optional[List[str]] = None,
    include_values: bool = False,
) -> SearchResult:
    """Search across one or more vaults for matching keys/values.

    Args:
        passphrase: Decryption passphrase.
        key_pattern: Substring to match against env var names (case-insensitive).
        value_pattern: Substring to match against env var values (case-insensitive).
        vault_names: Limit search to these vault names; None means all vaults.
        include_values: Whether to include values in results.

    Returns:
        SearchResult containing all matches.
    """
    if key_pattern is None and value_pattern is None:
        raise ValueError("At least one of key_pattern or value_pattern must be provided.")

    targets = vault_names if vault_names else list_vaults()
    result = SearchResult()

    for name in targets:
        try:
            env_vars = pull(name, passphrase)
        except EnvaultError:
            continue

        for k, v in env_vars.items():
            key_match = key_pattern is None or key_pattern.lower() in k.lower()
            val_match = value_pattern is None or value_pattern.lower() in v.lower()

            if key_match and val_match:
                result.matches.append(
                    SearchMatch(
                        vault_name=name,
                        key=k,
                        value=v if include_values else None,
                    )
                )

    return result
