"""User-level configuration management for envault."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from envault.exceptions import EnvaultError

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "envault"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "vault_dir": str(Path.home() / ".envault" / "vaults"),
    "default_backend": "local",
    "auto_backup": False,
}


def get_config_path() -> Path:
    """Return the path to the config file, respecting ENVAULT_CONFIG env var."""
    env_override = os.environ.get("ENVAULT_CONFIG")
    if env_override:
        return Path(env_override)
    return DEFAULT_CONFIG_FILE


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load config from disk, falling back to defaults for missing keys."""
    path = config_path or get_config_path()
    config = dict(DEFAULT_CONFIG)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                on_disk = json.load(f)
            if not isinstance(on_disk, dict):
                raise EnvaultError(f"Config file {path} is malformed.")
            config.update(on_disk)
        except json.JSONDecodeError as exc:
            raise EnvaultError(f"Failed to parse config file {path}: {exc}") from exc
    return config


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> None:
    """Persist config dict to disk."""
    path = config_path or get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


def set_config_value(key: str, value: Any, config_path: Optional[Path] = None) -> None:
    """Set a single config key and save."""
    if key not in DEFAULT_CONFIG:
        raise EnvaultError(
            f"Unknown config key '{key}'. Valid keys: {list(DEFAULT_CONFIG.keys())}"
        )
    config = load_config(config_path)
    config[key] = value
    save_config(config, config_path)


def get_config_value(key: str, config_path: Optional[Path] = None) -> Any:
    """Retrieve a single config value by key."""
    config = load_config(config_path)
    if key not in config:
        raise EnvaultError(f"Unknown config key '{key}'.")
    return config[key]
