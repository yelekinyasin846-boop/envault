"""Audit log for tracking vault operations (push/pull/sync)."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_AUDIT_FILENAME = "audit.log"


def get_audit_log_path(vault_dir: Optional[Path] = None) -> Path:
    """Return the path to the audit log file."""
    if vault_dir is None:
        vault_dir = Path.home() / ".envault"
    return Path(vault_dir) / DEFAULT_AUDIT_FILENAME


def _utc_now() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def record_event(
    action: str,
    vault_name: str,
    success: bool,
    detail: str = "",
    vault_dir: Optional[Path] = None,
) -> None:
    """Append a single audit event to the log file.

    Each event is a JSON object written as one line (JSONL format).
    """
    log_path = get_audit_log_path(vault_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": _utc_now(),
        "action": action,
        "vault": vault_name,
        "success": success,
        "detail": detail,
    }

    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_events(
    vault_dir: Optional[Path] = None,
    vault_name: Optional[str] = None,
    action: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[dict]:
    """Read audit events from the log, with optional filtering.

    Returns events in chronological order (oldest first).
    """
    log_path = get_audit_log_path(vault_dir)
    if not log_path.exists():
        return []

    events: List[dict] = []
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if vault_name and entry.get("vault") != vault_name:
                continue
            if action and entry.get("action") != action:
                continue
            events.append(entry)

    if limit is not None:
        events = events[-limit:]
    return events
