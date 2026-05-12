"""Sync module for envault: push/pull vaults to/from remote backends."""

import os
import json
import urllib.request
import urllib.error
from envault.exceptions import EnvaultError


class SyncError(EnvaultError):
    """Raised when a sync operation fails."""
    pass


def _get_headers(api_key: str) -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }


def push_remote(vault_name: str, blob: str, endpoint: str, api_key: str) -> None:
    """Upload an encrypted vault blob to a remote endpoint."""
    url = f"{endpoint.rstrip('/')}/vaults/{vault_name}"
    payload = json.dumps({"blob": blob}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=_get_headers(api_key), method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status not in (200, 201, 204):
                raise SyncError(f"Remote push failed with status {resp.status}")
    except urllib.error.HTTPError as exc:
        raise SyncError(f"Remote push HTTP error: {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise SyncError(f"Remote push connection error: {exc.reason}") from exc


def pull_remote(vault_name: str, endpoint: str, api_key: str) -> str:
    """Download an encrypted vault blob from a remote endpoint."""
    url = f"{endpoint.rstrip('/')}/vaults/{vault_name}"
    req = urllib.request.Request(url, headers=_get_headers(api_key), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "blob" not in data:
                raise SyncError("Remote response missing 'blob' field")
            return data["blob"]
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise SyncError(f"Vault '{vault_name}' not found on remote") from exc
        raise SyncError(f"Remote pull HTTP error: {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise SyncError(f"Remote pull connection error: {exc.reason}") from exc


def list_remote(endpoint: str, api_key: str) -> list:
    """List vault names available on the remote endpoint."""
    url = f"{endpoint.rstrip('/')}/vaults"
    req = urllib.request.Request(url, headers=_get_headers(api_key), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("vaults", [])
    except urllib.error.HTTPError as exc:
        raise SyncError(f"Remote list HTTP error: {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise SyncError(f"Remote list connection error: {exc.reason}") from exc
