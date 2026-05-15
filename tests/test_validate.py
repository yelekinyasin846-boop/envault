"""Tests for envault.validate."""

import pytest
from envault.validate import validate_env, ValidationResult, ValidationIssue


def test_valid_env_returns_no_issues():
    result = validate_env({"DATABASE_URL": "postgres://localhost/db", "PORT": "8080"})
    assert result.is_valid
    assert result.issues == []


def test_invalid_key_characters_is_error():
    result = validate_env({"bad-key": "value"})
    errors = [i for i in result.errors if "invalid characters" in i.message]
    assert errors, "Expected an error for invalid key characters"


def test_empty_value_is_warning():
    result = validate_env({"MY_VAR": ""})
    warnings = [i for i in result.warnings if "empty value" in i.message]
    assert warnings


def test_short_secret_value_is_warning():
    result = validate_env({"API_SECRET": "abc"})
    warnings = [i for i in result.warnings if "suspiciously short" in i.message]
    assert warnings


def test_long_enough_secret_no_warning():
    result = validate_env({"API_SECRET": "supersecretvalue"})
    short_warnings = [i for i in result.warnings if "suspiciously short" in i.message]
    assert not short_warnings


def test_schema_required_key_missing_is_error():
    schema = {"REQUIRED_KEY": {"required": True}}
    result = validate_env({}, schema=schema)
    errors = [i for i in result.errors if "REQUIRED_KEY" in i.message]
    assert errors


def test_schema_min_length_violation_is_error():
    schema = {"TOKEN": {"min_length": 10}}
    result = validate_env({"TOKEN": "short"}, schema=schema)
    errors = [i for i in result.errors if "min_length" in i.message]
    assert errors


def test_schema_max_length_violation_is_error():
    schema = {"SHORT_VAL": {"max_length": 3}}
    result = validate_env({"SHORT_VAL": "toolongvalue"}, schema=schema)
    errors = [i for i in result.errors if "max_length" in i.message]
    assert errors


def test_schema_pattern_violation_is_error():
    schema = {"PORT": {"pattern": r'^\d+$'}}
    result = validate_env({"PORT": "not_a_number"}, schema=schema)
    errors = [i for i in result.errors if "pattern" in i.message]
    assert errors


def test_schema_pattern_match_no_error():
    schema = {"PORT": {"pattern": r'^\d+$'}}
    result = validate_env({"PORT": "8080"}, schema=schema)
    pattern_errors = [i for i in result.errors if "pattern" in i.message]
    assert not pattern_errors


def test_is_valid_false_when_errors_present():
    result = validate_env({"bad-key": "value"})
    assert not result.is_valid


def test_summary_no_issues():
    result = validate_env({"OK_KEY": "value"})
    assert "passed" in result.summary()


def test_summary_with_issues():
    result = validate_env({"bad-key": ""})
    summary = result.summary()
    assert "error" in summary or "warning" in summary


def test_as_dict_contains_expected_fields():
    issue = ValidationIssue(key="FOO", message="some message", severity="warning")
    d = issue.as_dict()
    assert d["key"] == "FOO"
    assert d["severity"] == "warning"
    assert "message" in d
