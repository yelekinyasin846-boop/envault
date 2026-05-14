"""CLI sub-commands for vault tag management."""

from __future__ import annotations

import argparse
import sys

from envault.tags import TagError, add_tag, get_tags, list_vaults_by_tag, remove_tag


def cmd_tag_add(args: argparse.Namespace) -> None:
    """Add a tag to a vault."""
    try:
        tags = add_tag(args.vault, args.tag, vault_dir=getattr(args, "vault_dir", None))
        print(f"Tags for '{args.vault}': {', '.join(tags) if tags else '(none)'}")
    except TagError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_remove(args: argparse.Namespace) -> None:
    """Remove a tag from a vault."""
    try:
        tags = remove_tag(
            args.vault, args.tag, vault_dir=getattr(args, "vault_dir", None)
        )
        print(f"Tags for '{args.vault}': {', '.join(tags) if tags else '(none)'}")
    except TagError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_list(args: argparse.Namespace) -> None:
    """List tags on a vault."""
    try:
        tags = get_tags(args.vault, vault_dir=getattr(args, "vault_dir", None))
        if tags:
            for t in tags:
                print(t)
        else:
            print(f"No tags set for '{args.vault}'.")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_search(args: argparse.Namespace) -> None:
    """Search for vaults that carry a specific tag."""
    try:
        vaults = list_vaults_by_tag(
            args.tag, vault_dir=getattr(args, "vault_dir", None)
        )
        if vaults:
            for v in vaults:
                print(v)
        else:
            print(f"No vaults found with tag '{args.tag}'.")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_tags_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'tag' sub-commands onto *subparsers*."""
    tag_parser = subparsers.add_parser("tag", help="Manage vault tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd", required=True)

    # add
    p_add = tag_sub.add_parser("add", help="Add a tag to a vault")
    p_add.add_argument("vault", help="Vault name")
    p_add.add_argument("tag", help="Tag to add")
    p_add.set_defaults(func=cmd_tag_add)

    # remove
    p_rm = tag_sub.add_parser("remove", help="Remove a tag from a vault")
    p_rm.add_argument("vault", help="Vault name")
    p_rm.add_argument("tag", help="Tag to remove")
    p_rm.set_defaults(func=cmd_tag_remove)

    # list
    p_ls = tag_sub.add_parser("list", help="List tags on a vault")
    p_ls.add_argument("vault", help="Vault name")
    p_ls.set_defaults(func=cmd_tag_list)

    # search
    p_search = tag_sub.add_parser("search", help="Find vaults by tag")
    p_search.add_argument("tag", help="Tag to search for")
    p_search.set_defaults(func=cmd_tag_search)
