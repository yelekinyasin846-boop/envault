"""Utilities for parsing and serializing .env file content."""

from typing import Dict
from envault.exceptions import EnvaultError


class DotEnvParseError(EnvaultError):
    """Raised when a .env file cannot be parsed."""
    pass


def parse_dotenv(content: str) -> Dict[str, str]:
    """Parse the contents of a .env file into a dictionary.

    Supports:
      - KEY=VALUE pairs
      - Quoted values (single or double quotes)
      - Inline comments (# after value)
      - Full-line comments and blank lines (ignored)

    Args:
        content: Raw string content of a .env file.

    Returns:
        Dictionary mapping variable names to their string values.

    Raises:
        DotEnvParseError: If a non-comment, non-blank line is malformed.
    """
    env_vars: Dict[str, str] = {}

    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()

        # Skip blank lines and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise DotEnvParseError(
                f"Malformed line {lineno}: '{raw_line}' (missing '=')"
            )

        key, _, raw_value = line.partition("=")
        key = key.strip()

        if not key:
            raise DotEnvParseError(
                f"Malformed line {lineno}: '{raw_line}' (empty key)"
            )

        value = raw_value.strip()

        # Strip matching surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        else:
            # Remove inline comment (unquoted values only)
            comment_idx = value.find(" #")
            if comment_idx != -1:
                value = value[:comment_idx].strip()

        env_vars[key] = value

    return env_vars


def serialize_dotenv(env_vars: Dict[str, str]) -> str:
    """Serialize a dictionary of environment variables to .env file format.

    Values containing spaces or special characters are double-quoted.

    Args:
        env_vars: Dictionary of variable names to values.

    Returns:
        A string suitable for writing to a .env file.
    """
    lines = []
    for key, value in env_vars.items():
        needs_quotes = any(ch in value for ch in (" ", "\t", "#", "'", '"'))
        if needs_quotes:
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
