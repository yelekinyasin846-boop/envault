"""CLI sub-commands for managing envault configuration."""

import argparse
import sys
from typing import List, Optional

from envault.config import (
    DEFAULT_CONFIG,
    get_config_value,
    load_config,
    set_config_value,
)
from envault.exceptions import EnvaultError


def cmd_config_get(args: argparse.Namespace) -> None:
    """Print the value of a config key."""
    try:
        value = get_config_value(args.key)
        print(f"{args.key} = {value}")
    except EnvaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_config_set(args: argparse.Namespace) -> None:
    """Set a config key to a new value."""
    value: object = args.value
    # Coerce bool-like strings
    if isinstance(value, str) and value.lower() in ("true", "false"):
        value = value.lower() == "true"
    try:
        set_config_value(args.key, value)
        print(f"Set {args.key} = {value}")
    except EnvaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_config_list(args: argparse.Namespace) -> None:
    """List all current configuration values."""
    try:
        config = load_config()
        for key, val in config.items():
            print(f"{key} = {val}")
    except EnvaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_config_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Attach 'config' sub-commands to an existing subparsers group."""
    config_parser = subparsers.add_parser("config", help="Manage envault configuration")
    config_sub = config_parser.add_subparsers(dest="config_cmd")
    config_parser.set_defaults(func=lambda _: config_parser.print_help())

    # config get
    get_p = config_sub.add_parser("get", help="Get a config value")
    get_p.add_argument("key", choices=list(DEFAULT_CONFIG.keys()))
    get_p.set_defaults(func=cmd_config_get)

    # config set
    set_p = config_sub.add_parser("set", help="Set a config value")
    set_p.add_argument("key", choices=list(DEFAULT_CONFIG.keys()))
    set_p.add_argument("value")
    set_p.set_defaults(func=cmd_config_set)

    # config list
    list_p = config_sub.add_parser("list", help="List all config values")
    list_p.set_defaults(func=cmd_config_list)
