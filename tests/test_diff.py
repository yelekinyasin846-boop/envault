"""Tests for envault.diff module."""

import pytest
from envault.diff import diff_envs, DiffResult


OLD = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
NEW = {"HOST": "prod.db", "PORT": "5432", "SECRET": "abc123"}


def test_diff_detects_added_keys():
    result = diff_envs(OLD, NEW)
    assert "SECRET" in result.added
    assert result.added["SECRET"] == "abc123"


def test_diff_detects_removed_keys():
    result = diff_envs(OLD, NEW)
    assert "DEBUG" in result.removed
    assert result.removed["DEBUG"] == "true"


def test_diff_detects_changed_keys():
    result = diff_envs(OLD, NEW)
    assert "HOST" in result.changed
    old_val, new_val = result.changed["HOST"]
    assert old_val == "localhost"
    assert new_val == "prod.db"


def test_diff_detects_unchanged_keys():
    result = diff_envs(OLD, NEW)
    assert "PORT" in result.unchanged
    assert result.unchanged["PORT"] == "5432"


def test_diff_has_changes_true_when_differences():
    result = diff_envs(OLD, NEW)
    assert result.has_changes is True


def test_diff_has_changes_false_when_identical():
    result = diff_envs(OLD, OLD)
    assert result.has_changes is False


def test_diff_empty_dicts():
    result = diff_envs({}, {})
    assert not result.has_changes
    assert result.summary() == "  (no changes)"


def test_diff_redact_values():
    result = diff_envs(OLD, NEW, redact_values=True)
    assert result.added["SECRET"] == "***"
    assert result.removed["DEBUG"] == "***"
    old_val, new_val = result.changed["HOST"]
    assert old_val == "***"
    assert new_val == "***"


def test_summary_contains_plus_for_added():
    result = diff_envs({}, {"FOO": "bar"})
    assert "+ FOO=bar" in result.summary()


def test_summary_contains_minus_for_removed():
    result = diff_envs({"FOO": "bar"}, {})
    assert "- FOO=bar" in result.summary()


def test_summary_contains_tilde_for_changed():
    result = diff_envs({"FOO": "old"}, {"FOO": "new"})
    assert "~ FOO" in result.summary()
