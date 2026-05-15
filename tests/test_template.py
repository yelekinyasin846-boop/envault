"""Tests for envault.template module."""

import os
import pytest

from envault.template import (
    render_template,
    render_template_file,
    list_placeholders,
    TemplateError,
)


VARS = {"HOST": "localhost", "PORT": "5432", "DB": "mydb"}


def test_render_dollar_brace_syntax():
    result = render_template("connect to ${HOST}:${PORT}/${DB}", VARS)
    assert result == "connect to localhost:5432/mydb"


def test_render_plain_dollar_syntax():
    result = render_template("host=$HOST port=$PORT", VARS)
    assert result == "host=localhost port=5432"


def test_render_mixed_syntax():
    result = render_template("${HOST}:$PORT", VARS)
    assert result == "localhost:5432"


def test_render_no_placeholders():
    result = render_template("no vars here", VARS)
    assert result == "no vars here"


def test_render_strict_raises_on_missing():
    with pytest.raises(TemplateError) as exc_info:
        render_template("value=${MISSING}", VARS, strict=True)
    assert "MISSING" in str(exc_info.value)


def test_render_loose_leaves_unresolved():
    result = render_template("value=${MISSING}", VARS, strict=False)
    assert result == "value=${MISSING}"


def test_render_empty_variables():
    with pytest.raises(TemplateError):
        render_template("${HOST}", {}, strict=True)


def test_list_placeholders_returns_sorted_unique():
    text = "${HOST} $PORT ${HOST} $DB"
    result = list_placeholders(text)
    assert result == ["DB", "HOST", "PORT"]


def test_list_placeholders_empty_template():
    assert list_placeholders("no placeholders here") == []


def test_render_template_file_success(tmp_path):
    tpl = tmp_path / "app.conf"
    tpl.write_text("host=${HOST}\nport=${PORT}\n")
    result = render_template_file(str(tpl), VARS)
    assert result == "host=localhost\nport=5432\n"


def test_render_template_file_missing_raises(tmp_path):
    with pytest.raises(TemplateError) as exc_info:
        render_template_file(str(tmp_path / "nonexistent.conf"), VARS)
    assert "Cannot read" in str(exc_info.value)


def test_render_template_file_strict_missing_var(tmp_path):
    tpl = tmp_path / "tpl.txt"
    tpl.write_text("${UNDEFINED_VAR}")
    with pytest.raises(TemplateError) as exc_info:
        render_template_file(str(tpl), VARS, strict=True)
    assert "UNDEFINED_VAR" in str(exc_info.value)


def test_render_partial_match_does_not_substitute_invalid_names():
    # Names starting with digits are not valid — should not be substituted
    result = render_template("$123abc", {"123abc": "bad"}, strict=False)
    assert result == "$123abc"
