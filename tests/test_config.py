"""Tests for envault.config module."""

import json
import pytest
from pathlib import Path

from envault.config import (
    DEFAULT_CONFIG,
    load_config,
    save_config,
    set_config_value,
    get_config_value,
    get_config_path,
)
from envault.exceptions import EnvaultError


@pytest.fixture
def config_file(tmp_path):
    """Return a temp path for a config file."""
    return tmp_path / "config.json"


def test_load_config_returns_defaults_when_no_file(config_file):
    config = load_config(config_file)
    assert config == DEFAULT_CONFIG


def test_save_and_load_roundtrip(config_file):
    data = {"vault_dir": "/tmp/myvaults", "default_backend": "local", "auto_backup": True}
    save_config(data, config_file)
    loaded = load_config(config_file)
    assert loaded["vault_dir"] == "/tmp/myvaults"
    assert loaded["auto_backup"] is True


def test_save_config_creates_parent_dirs(tmp_path):
    nested = tmp_path / "a" / "b" / "config.json"
    save_config(DEFAULT_CONFIG, nested)
    assert nested.exists()


def test_load_config_merges_with_defaults(config_file):
    partial = {"auto_backup": True}
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(partial))
    config = load_config(config_file)
    assert config["auto_backup"] is True
    assert config["default_backend"] == DEFAULT_CONFIG["default_backend"]


def test_load_config_raises_on_malformed_json(config_file):
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("not json {{{")
    with pytest.raises(EnvaultError, match="Failed to parse"):
        load_config(config_file)


def test_load_config_raises_on_non_dict_json(config_file):
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(["list", "not", "dict"]))
    with pytest.raises(EnvaultError, match="malformed"):
        load_config(config_file)


def test_set_config_value_updates_key(config_file):
    set_config_value("auto_backup", True, config_file)
    assert get_config_value("auto_backup", config_file) is True


def test_set_config_value_rejects_unknown_key(config_file):
    with pytest.raises(EnvaultError, match="Unknown config key"):
        set_config_value("nonexistent_key", "value", config_file)


def test_get_config_value_unknown_key_raises(config_file):
    with pytest.raises(EnvaultError, match="Unknown config key"):
        get_config_value("does_not_exist", config_file)


def test_get_config_path_respects_env_var(monkeypatch, tmp_path):
    custom = tmp_path / "custom_config.json"
    monkeypatch.setenv("ENVAULT_CONFIG", str(custom))
    assert get_config_path() == custom
