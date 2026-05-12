"""CLI subcommands for remote sync operations."""

import argparse
from envault.config import get_config_value
from envault.storage import load_vault, save_vault
from envault.sync import push_remote, pull_remote, list_remote, SyncError


def _get_remote_settings(args):
    """Resolve endpoint and api_key from args or config."""
    endpoint = getattr(args, "endpoint", None) or get_config_value("remote_endpoint")
    api_key = getattr(args, "api_key", None) or get_config_value("remote_api_key")
    if not endpoint:
        raise SyncError("No remote endpoint configured. Use --endpoint or set remote_endpoint via config.")
    if not api_key:
        raise SyncError("No API key configured. Use --api-key or set remote_api_key via config.")
    return endpoint, api_key


def cmd_sync_push(args):
    """Push a local vault blob to the remote backend."""
    try:
        endpoint, api_key = _get_remote_settings(args)
        blob = load_vault(args.name)
        push_remote(args.name, blob, endpoint, api_key)
        print(f"Pushed vault '{args.name}' to remote.")
    except SyncError as exc:
        print(f"Sync error: {exc}")
        raise SystemExit(1)


def cmd_sync_pull(args):
    """Pull a vault blob from the remote backend and store it locally."""
    try:
        endpoint, api_key = _get_remote_settings(args)
        blob = pull_remote(args.name, endpoint, api_key)
        save_vault(args.name, blob)
        print(f"Pulled vault '{args.name}' from remote.")
    except SyncError as exc:
        print(f"Sync error: {exc}")
        raise SystemExit(1)


def cmd_sync_list(args):
    """List vaults available on the remote backend."""
    try:
        endpoint, api_key = _get_remote_settings(args)
        vaults = list_remote(endpoint, api_key)
        if not vaults:
            print("No vaults found on remote.")
        else:
            for name in vaults:
                print(name)
    except SyncError as exc:
        print(f"Sync error: {exc}")
        raise SystemExit(1)


def build_sync_subparser(subparsers):
    """Register sync subcommands onto an existing subparsers action."""
    sync_parser = subparsers.add_parser("sync", help="Sync vaults with a remote backend")
    sync_sub = sync_parser.add_subparsers(dest="sync_cmd")

    def _add_common(p):
        p.add_argument("--endpoint", help="Remote endpoint URL")
        p.add_argument("--api-key", dest="api_key", help="API key for authentication")

    push_p = sync_sub.add_parser("push", help="Push a vault to remote")
    push_p.add_argument("name", help="Vault name")
    _add_common(push_p)
    push_p.set_defaults(func=cmd_sync_push)

    pull_p = sync_sub.add_parser("pull", help="Pull a vault from remote")
    pull_p.add_argument("name", help="Vault name")
    _add_common(pull_p)
    pull_p.set_defaults(func=cmd_sync_pull)

    list_p = sync_sub.add_parser("list", help="List vaults on remote")
    _add_common(list_p)
    list_p.set_defaults(func=cmd_sync_list)

    return sync_parser
