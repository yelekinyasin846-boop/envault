"""Tests for envault.sync remote sync operations."""

import json
import pytest
from unittest.mock import patch, MagicMock
from envault.sync import push_remote, pull_remote, list_remote, SyncError
import urllib.error

ENDPOINT = "https://example.com/api"
API_KEY = "test-api-key"
VAULT_NAME = "myproject"
BLOB = "encryptedblob=="


def _mock_response(status=200, body=None):
    mock = MagicMock()
    mock.status = status
    mock.read.return_value = (json.dumps(body) if body else b"").encode("utf-8") if isinstance(body, dict) else (body or b"")
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


class TestPushRemote:
    def test_push_success(self):
        resp = _mock_response(status=200)
        with patch("urllib.request.urlopen", return_value=resp):
            push_remote(VAULT_NAME, BLOB, ENDPOINT, API_KEY)  # should not raise

    def test_push_http_error_raises_sync_error(self):
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
            url=None, code=500, msg="Server Error", hdrs=None, fp=None
        )):
            with pytest.raises(SyncError, match="500"):
                push_remote(VAULT_NAME, BLOB, ENDPOINT, API_KEY)

    def test_push_url_error_raises_sync_error(self):
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")):
            with pytest.raises(SyncError, match="connection"):
                push_remote(VAULT_NAME, BLOB, ENDPOINT, API_KEY)


class TestPullRemote:
    def test_pull_success_returns_blob(self):
        body = json.dumps({"blob": BLOB}).encode("utf-8")
        resp = MagicMock()
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=resp):
            result = pull_remote(VAULT_NAME, ENDPOINT, API_KEY)
        assert result == BLOB

    def test_pull_missing_blob_field_raises(self):
        body = json.dumps({"other": "data"}).encode("utf-8")
        resp = MagicMock()
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=resp):
            with pytest.raises(SyncError, match="blob"):
                pull_remote(VAULT_NAME, ENDPOINT, API_KEY)

    def test_pull_404_raises_sync_error(self):
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
            url=None, code=404, msg="Not Found", hdrs=None, fp=None
        )):
            with pytest.raises(SyncError, match="not found"):
                pull_remote(VAULT_NAME, ENDPOINT, API_KEY)


class TestListRemote:
    def test_list_returns_vault_names(self):
        body = json.dumps({"vaults": ["proj1", "proj2"]}).encode("utf-8")
        resp = MagicMock()
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=resp):
            result = list_remote(ENDPOINT, API_KEY)
        assert result == ["proj1", "proj2"]

    def test_list_empty_response(self):
        body = json.dumps({}).encode("utf-8")
        resp = MagicMock()
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=resp):
            result = list_remote(ENDPOINT, API_KEY)
        assert result == []

    def test_list_url_error_raises_sync_error(self):
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
            with pytest.raises(SyncError):
                list_remote(ENDPOINT, API_KEY)
