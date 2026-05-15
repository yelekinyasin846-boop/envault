"""Import env vars into a vault from various sources."""

import json
import os
from typing import Dict, Optional

from envault.dotenv import parse_dotenv, DotEnvParseError
from envault.exceptions import EnvaultError


class ImportError(EnvaultError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def import_from_dotenv(path: str) -> Dict[str, str]:
    """Parse a .env file and return a dict of key/value pairs."""
    if not os.path.isfile(path):
        raise ImportError(f"File not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        return parse_dotenv(content)
    except DotEnvParseError as exc:
        raise ImportError(f"Failed to parse .env file: {exc}") from exc


def import_from_json(path: str) -> Dict[str, str]:
    """Load a JSON file (flat object) and return a dict of key/value pairs."""
    if not os.path.isfile(path):
        raise ImportError(f"File not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ImportError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ImportError("JSON root must be an object.")
    bad = [k for k, v in data.items() if not isinstance(v, str)]
    if bad:
        raise ImportError(f"All values must be strings. Non-string keys: {bad}")
    return data


def import_from_env(prefix: Optional[str] = None) -> Dict[str, str]:
    """Capture variables from the current process environment.

    Args:
        prefix: If given, only import variables whose names start with this
                prefix (case-sensitive). The prefix is stripped from the key.
    """
    env = dict(os.environ)
    if prefix:
        env = {
            k[len(prefix):]: v
            for k, v in env.items()
            if k.startswith(prefix)
        }
    return env
