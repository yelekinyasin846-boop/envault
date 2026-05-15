"""Tests for envault.lint module."""

from __future__ import annotations

import pytest

from envault.lint import lint_env, LintResult, LintIssue


def test_lint_clean_env_has_no_issues():
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    result = lint_env(env)
    assert not result.issues
    assert not result.has_errors
    assert not result.has_warnings


def test_lint_lowercase_key_is_warning():
    result = lint_env({"my_var": "value"})
    assert any(i.key == "my_var" and i.severity == "warning" for i in result.issues)


def test_lint_invalid_key_characters_is_error():
    result = lint_env({"INVALID-KEY": "value"})
    assert any(i.key == "INVALID-KEY" and i.severity == "error" for i in result.issues)


def test_lint_empty_value_is_warning():
    result = lint_env({"EMPTY_VAR": ""})
    assert any(i.key == "EMPTY_VAR" and i.severity == "warning" for i in result.issues)


def test_lint_newline_in_value_is_warning():
    result = lint_env({"MULTILINE": "line1\nline2"})
    assert any(i.key == "MULTILINE" and i.severity == "warning" for i in result.issues)


def test_lint_oversized_value_is_warning():
    result = lint_env({"BIG_VAR": "x" * 5000})
    assert any(i.key == "BIG_VAR" and i.severity == "warning" for i in result.issues)


def test_lint_has_errors_true_when_error_present():
    result = lint_env({"bad-key": "val"})
    assert result.has_errors


def test_lint_has_warnings_true_when_warning_present():
    result = lint_env({"lower_key": "val"})
    assert result.has_warnings


def test_lint_summary_format():
    result = lint_env({"bad-key": "", "lower_key": "val"})
    summary = result.summary()
    assert "error" in summary
    assert "warning" in summary


def test_lint_issue_as_dict():
    issue = LintIssue(key="FOO", severity="warning", message="Test message.")
    d = issue.as_dict()
    assert d == {"key": "FOO", "severity": "warning", "message": "Test message."}


def test_lint_multiple_issues_on_same_key():
    # lowercase key + empty value → warning for case + warning for empty
    result = lint_env({"bad_key": ""})
    keys_with_issues = [i.key for i in result.issues]
    assert keys_with_issues.count("bad_key") >= 2


def test_lint_empty_env_returns_no_issues():
    result = lint_env({})
    assert result.issues == []
