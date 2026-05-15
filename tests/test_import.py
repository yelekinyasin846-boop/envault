"""Tests for envault.import_"""

import json
import os
import pytest

from envault.import_ import (
    import_from_dotenv,
    import_from_json,
    import_from_env,
    ImportError,
)


def test_import_from_dotenv_simple(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    result = import_from_dotenv(str(f))
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_import_from_dotenv_missing_file_raises():
    with pytest.raises(ImportError) as exc_info:
        import_from_dotenv("/nonexistent/path/.env")
    assert "not found" in exc_info.value.message


def test_import_from_dotenv_invalid_content_raises(tmp_path):
    f = tmp_path / ".env"
    f.write_text("=NOKEY\n")
    with pytest.raises(ImportError):
        import_from_dotenv(str(f))


def test_import_from_json_simple(tmp_path):
    f = tmp_path / "vars.json"
    f.write_text(json.dumps({"KEY": "value", "OTHER": "123"}))
    result = import_from_json(str(f))
    assert result == {"KEY": "value", "OTHER": "123"}


def test_import_from_json_missing_file_raises():
    with pytest.raises(ImportError) as exc_info:
        import_from_json("/no/such/file.json")
    assert "not found" in exc_info.value.message


def test_import_from_json_invalid_json_raises(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("not json")
    with pytest.raises(ImportError) as exc_info:
        import_from_json(str(f))
    assert "Invalid JSON" in exc_info.value.message


def test_import_from_json_non_string_values_raises(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps({"PORT": 8080}))
    with pytest.raises(ImportError) as exc_info:
        import_from_json(str(f))
    assert "string" in exc_info.value.message


def test_import_from_json_non_dict_raises(tmp_path):
    f = tmp_path / "list.json"
    f.write_text(json.dumps(["a", "b"]))
    with pytest.raises(ImportError) as exc_info:
        import_from_json(str(f))
    assert "object" in exc_info.value.message


def test_import_from_env_returns_dict(monkeypatch):
    monkeypatch.setenv("TEST_VAR_A", "hello")
    monkeypatch.setenv("TEST_VAR_B", "world")
    result = import_from_env()
    assert "TEST_VAR_A" in result
    assert result["TEST_VAR_A"] == "hello"


def test_import_from_env_with_prefix(monkeypatch):
    monkeypatch.setenv("APP_DB_HOST", "localhost")
    monkeypatch.setenv("APP_DB_PORT", "5432")
    monkeypatch.setenv("OTHER_VAR", "ignored")
    result = import_from_env(prefix="APP_")
    assert "DB_HOST" in result
    assert "DB_PORT" in result
    assert "OTHER_VAR" not in result
    assert "APP_DB_HOST" not in result
