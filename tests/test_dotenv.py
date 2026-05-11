"""Tests for envault.dotenv parsing and serialization utilities."""

import pytest
from envault.dotenv import parse_dotenv, serialize_dotenv, DotEnvParseError


# ---------------------------------------------------------------------------
# parse_dotenv tests
# ---------------------------------------------------------------------------

def test_parse_simple_key_value():
    content = "KEY=value\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_multiple_vars():
    content = "FOO=bar\nBAZ=qux\n"
    result = parse_dotenv(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_ignores_blank_lines_and_comments():
    content = "\n# This is a comment\nKEY=value\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_double_quoted_value():
    result = parse_dotenv('DB_URL="postgres://localhost/mydb"')
    assert result["DB_URL"] == "postgres://localhost/mydb"


def test_parse_single_quoted_value():
    result = parse_dotenv("SECRET='my secret value'")
    assert result["SECRET"] == "my secret value"


def test_parse_inline_comment_stripped():
    result = parse_dotenv("PORT=8080 # default port")
    assert result["PORT"] == "8080"


def test_parse_value_with_equals_sign():
    result = parse_dotenv("TOKEN=abc=def=ghi")
    assert result["TOKEN"] == "abc=def=ghi"


def test_parse_empty_value():
    result = parse_dotenv("EMPTY=")
    assert result["EMPTY"] == ""


def test_parse_malformed_line_raises():
    with pytest.raises(DotEnvParseError, match="missing '='"):
        parse_dotenv("THISLINEHASNOEQUALSSIGN\n")


def test_parse_empty_key_raises():
    with pytest.raises(DotEnvParseError, match="empty key"):
        parse_dotenv("=value\n")


# ---------------------------------------------------------------------------
# serialize_dotenv tests
# ---------------------------------------------------------------------------

def test_serialize_simple():
    result = serialize_dotenv({"KEY": "value"})
    assert "KEY=value" in result


def test_serialize_value_with_space_is_quoted():
    result = serialize_dotenv({"MSG": "hello world"})
    assert 'MSG="hello world"' in result


def test_serialize_value_with_hash_is_quoted():
    result = serialize_dotenv({"TAG": "v1.0#stable"})
    assert 'TAG="v1.0#stable"' in result


def test_serialize_ends_with_newline():
    result = serialize_dotenv({"A": "1"})
    assert result.endswith("\n")


def test_serialize_empty_dict_returns_empty_string():
    result = serialize_dotenv({})
    assert result == ""


def test_roundtrip_parse_serialize():
    original = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}
    serialized = serialize_dotenv(original)
    parsed = parse_dotenv(serialized)
    assert parsed == original
