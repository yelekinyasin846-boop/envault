"""Tests for envault.cli_template module."""

import argparse
import sys
import pytest
from unittest.mock import patch, MagicMock

from envault.cli_template import cmd_template_render, cmd_template_inspect, build_template_subparser


VARS = {"APP_HOST": "0.0.0.0", "APP_PORT": "8080"}


def _args(**kwargs):
    defaults = dict(vault="myvault", passphrase="secret", template="tpl.txt", output=None, loose=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_template_render_stdout(tmp_path, capsys):
    tpl = tmp_path / "app.cfg"
    tpl.write_text("host=${APP_HOST}\nport=${APP_PORT}\n")

    with patch("envault.cli_template.pull", return_value=VARS):
        cmd_template_render(_args(template=str(tpl)))

    out = capsys.readouterr().out
    assert "0.0.0.0" in out
    assert "8080" in out


def test_cmd_template_render_to_file(tmp_path):
    tpl = tmp_path / "app.cfg"
    tpl.write_text("${APP_HOST}:${APP_PORT}")
    out_file = tmp_path / "rendered.cfg"

    with patch("envault.cli_template.pull", return_value=VARS):
        cmd_template_render(_args(template=str(tpl), output=str(out_file)))

    assert out_file.read_text() == "0.0.0.0:8080"


def test_cmd_template_render_missing_var_exits(tmp_path):
    tpl = tmp_path / "tpl.txt"
    tpl.write_text("${UNDEFINED}")

    with patch("envault.cli_template.pull", return_value=VARS):
        with pytest.raises(SystemExit) as exc_info:
            cmd_template_render(_args(template=str(tpl)))
    assert exc_info.value.code == 1


def test_cmd_template_render_loose_does_not_exit(tmp_path, capsys):
    tpl = tmp_path / "tpl.txt"
    tpl.write_text("${UNDEFINED}")

    with patch("envault.cli_template.pull", return_value=VARS):
        cmd_template_render(_args(template=str(tpl), loose=True))

    out = capsys.readouterr().out
    assert "${UNDEFINED}" in out


def test_cmd_template_render_vault_error_exits(tmp_path):
    from envault.exceptions import EnvaultError
    tpl = tmp_path / "tpl.txt"
    tpl.write_text("${APP_HOST}")

    with patch("envault.cli_template.pull", side_effect=EnvaultError("bad vault")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_template_render(_args(template=str(tpl)))
    assert exc_info.value.code == 1


def test_cmd_template_inspect_lists_vars(tmp_path, capsys):
    tpl = tmp_path / "tpl.txt"
    tpl.write_text("${APP_HOST} $APP_PORT $APP_HOST")

    cmd_template_inspect(argparse.Namespace(template=str(tpl)))

    out = capsys.readouterr().out
    assert "APP_HOST" in out
    assert "APP_PORT" in out
    assert out.count("APP_HOST") == 1  # deduplicated


def test_cmd_template_inspect_no_vars(tmp_path, capsys):
    tpl = tmp_path / "tpl.txt"
    tpl.write_text("no placeholders at all")

    cmd_template_inspect(argparse.Namespace(template=str(tpl)))

    out = capsys.readouterr().out
    assert "No placeholders" in out


def test_build_template_subparser_registers_commands():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    build_template_subparser(subs)
    args = parser.parse_args(["template", "inspect", "some_file.txt"])
    assert args.template == "some_file.txt"
