"""Tests for envault.audit module."""

import json
import pytest
from pathlib import Path

from envault.audit import (
    get_audit_log_path,
    record_event,
    read_events,
    DEFAULT_AUDIT_FILENAME,
)


@pytest.fixture
def audit_dir(tmp_path):
    return tmp_path / "vault"


def test_get_audit_log_path_uses_default_filename(audit_dir):
    path = get_audit_log_path(audit_dir)
    assert path.name == DEFAULT_AUDIT_FILENAME
    assert path.parent == audit_dir


def test_record_event_creates_log_file(audit_dir):
    record_event("push", "myapp", success=True, vault_dir=audit_dir)
    log_path = get_audit_log_path(audit_dir)
    assert log_path.exists()


def test_record_event_writes_valid_jsonl(audit_dir):
    record_event("pull", "myapp", success=True, detail="ok", vault_dir=audit_dir)
    log_path = get_audit_log_path(audit_dir)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["action"] == "pull"
    assert entry["vault"] == "myapp"
    assert entry["success"] is True
    assert entry["detail"] == "ok"
    assert "timestamp" in entry


def test_record_multiple_events_appends(audit_dir):
    record_event("push", "app1", success=True, vault_dir=audit_dir)
    record_event("pull", "app1", success=False, vault_dir=audit_dir)
    events = read_events(vault_dir=audit_dir)
    assert len(events) == 2


def test_read_events_empty_when_no_file(audit_dir):
    events = read_events(vault_dir=audit_dir)
    assert events == []


def test_read_events_filters_by_vault_name(audit_dir):
    record_event("push", "alpha", success=True, vault_dir=audit_dir)
    record_event("push", "beta", success=True, vault_dir=audit_dir)
    events = read_events(vault_dir=audit_dir, vault_name="alpha")
    assert len(events) == 1
    assert events[0]["vault"] == "alpha"


def test_read_events_filters_by_action(audit_dir):
    record_event("push", "app", success=True, vault_dir=audit_dir)
    record_event("pull", "app", success=True, vault_dir=audit_dir)
    record_event("push", "app", success=False, vault_dir=audit_dir)
    events = read_events(vault_dir=audit_dir, action="push")
    assert len(events) == 2
    assert all(e["action"] == "push" for e in events)


def test_read_events_limit_returns_last_n(audit_dir):
    for i in range(5):
        record_event("push", f"app{i}", success=True, vault_dir=audit_dir)
    events = read_events(vault_dir=audit_dir, limit=3)
    assert len(events) == 3
    assert events[-1]["vault"] == "app4"


def test_record_event_creates_parent_dirs(tmp_path):
    deep_dir = tmp_path / "a" / "b" / "c"
    record_event("push", "x", success=True, vault_dir=deep_dir)
    assert get_audit_log_path(deep_dir).exists()
