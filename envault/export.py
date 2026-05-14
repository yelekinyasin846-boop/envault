"""Export vault contents to various formats (shell, JSON, Docker)."""

from __future__ import annotations

import json
from typing import Dict

from envault.exceptions import EnvaultError


class ExportError(EnvaultError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


SUPPORTED_FORMATS = ("dotenv", "shell", "json", "docker")


def export_as_dotenv(vars: Dict[str, str]) -> str:
    """Export vars as a standard .env file."""
    lines = []
    for key, value in vars.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_as_shell(vars: Dict[str, str]) -> str:
    """Export vars as shell export statements."""
    lines = []
    for key, value in vars.items():
        escaped = value.replace("'", "'\\''")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")


def export_as_json(vars: Dict[str, str]) -> str:
    """Export vars as a JSON object."""
    return json.dumps(vars, indent=2) + "\n"


def export_as_docker(vars: Dict[str, str]) -> str:
    """Export vars as Docker --env-file compatible format (KEY=VALUE, no quotes)."""
    lines = []
    for key, value in vars.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_vars(vars: Dict[str, str], fmt: str) -> str:
    """Dispatch export to the requested format."""
    if fmt == "dotenv":
        return export_as_dotenv(vars)
    elif fmt == "shell":
        return export_as_shell(vars)
    elif fmt == "json":
        return export_as_json(vars)
    elif fmt == "docker":
        return export_as_docker(vars)
    else:
        raise ExportError(
            f"Unsupported export format '{fmt}'. "
            f"Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
