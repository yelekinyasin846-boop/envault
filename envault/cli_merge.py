"""CLI commands for the vault merge feature."""

from __future__ import annotations

import argparse
import getpass
import sys

from envault.merge import MergeError, MergeStrategy, merge_vaults


def cmd_merge(args: argparse.Namespace) -> None:
    """Merge two or more vaults into a destination vault."""
    passphrase = getpass.getpass("Passphrase: ")

    strategy = MergeStrategy(args.strategy)

    try:
        result = merge_vaults(
            vault_names=args.sources,
            passphrase=passphrase,
            dest_vault=args.dest,
            strategy=strategy,
        )
    except MergeError as exc:
        print(f"[error] Merge failed: {exc}", file=sys.stderr)
        if exc.conflicts:
            print("Conflicting keys: " + ", ".join(exc.conflicts), file=sys.stderr)
        sys.exit(1)

    merged = result["merged"]
    conflicts = result["conflicts"]

    print(f"Merged {len(args.sources)} vaults into '{args.dest}'.")
    print(f"  Total keys : {len(merged)}")
    print(f"  Conflicts  : {len(conflicts)}")

    if conflicts and args.verbose:
        print("\nConflict details (key | kept | discarded):")
        for key, kept, discarded in conflicts:
            kept_val = kept if strategy == MergeStrategy.OURS else discarded
            disc_val = discarded if strategy == MergeStrategy.OURS else kept
            print(f"  {key:30s}  kept={kept_val!r}  discarded={disc_val!r}")


def build_merge_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("merge", help="Merge two or more vaults into one.")
    p.add_argument("sources", nargs="+", metavar="VAULT", help="Source vault names (at least 2).")
    p.add_argument("-d", "--dest", required=True, metavar="DEST", help="Destination vault name.")
    p.add_argument(
        "--strategy",
        choices=[s.value for s in MergeStrategy],
        default=MergeStrategy.THEIRS.value,
        help="Conflict resolution strategy (default: theirs).",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Show conflict details.")
    p.set_defaults(func=cmd_merge)
