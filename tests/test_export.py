"""Tests for envault.export module."""

import json
import pytest

from envault.export import (
    export_vars,
    export_as_dotenv,
    export_as_shell,
    export_as_json,
    export_as_docker,
    ExportError,
    SUPPORTED_FORMATS,
)

SAMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "abc123"}


def test_export_as_dotenv_format():
    result = export_as_dotenv(SAMPLE)
    assert 'DB_HOST="localhost"' in result
    assert 'DB_PORT="5432"' in result
    assert result.endswith("\n")


def test_export_as_dotenv_escapes_double_quotes():
    result = export_as_dotenv({"MSG": 'say "hello"'})
    assert 'MSG="say \\"hello\\""' in result


def test_export_as_shell_format():
    result = export_as_shell(SAMPLE)
    assert "export DB_HOST='localhost'" in result
    assert "export API_KEY='abc123'" in result
    assert result.endswith("\n")


def test_export_as_shell_escapes_single_quotes():
    result = export_as_shell({"VAR": "it's alive"})
    assert "export VAR='it'\\''s alive'" in result


def test_export_as_json_is_valid_json():
    result = export_as_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_export_as_json_is_pretty_printed():
    result = export_as_json({"A": "1"})
    assert "\n" in result


def test_export_as_docker_format():
    result = export_as_docker(SAMPLE)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result
    assert result.endswith("\n")


def test_export_as_docker_no_quotes():
    result = export_as_docker({"KEY": "value"})
    assert '"' not in result
    assert "'" not in result


def test_export_vars_dispatches_dotenv():
    result = export_vars(SAMPLE, "dotenv")
    assert 'DB_HOST="localhost"' in result


def test_export_vars_dispatches_shell():
    result = export_vars(SAMPLE, "shell")
    assert "export DB_HOST=" in result


def test_export_vars_dispatches_json():
    result = export_vars(SAMPLE, "json")
    assert json.loads(result) == SAMPLE


def test_export_vars_dispatches_docker():
    result = export_vars(SAMPLE, "docker")
    assert "DB_HOST=localhost" in result


def test_export_vars_unsupported_format_raises():
    with pytest.raises(ExportError) as exc_info:
        export_vars(SAMPLE, "yaml")
    assert "yaml" in str(exc_info.value.message)
    assert "dotenv" in str(exc_info.value.message)


def test_export_empty_vars_returns_empty_string():
    for fmt in SUPPORTED_FORMATS:
        result = export_vars({}, fmt)
        if fmt == "json":
            assert json.loads(result) == {}
        else:
            assert result == "" or result == "\n"
