"""CLI subcommands for template rendering."""

import argparse
import sys

from envault.template import render_template_file, list_placeholders, TemplateError
from envault.vault import pull
from envault.exceptions import EnvaultError


def cmd_template_render(args: argparse.Namespace) -> None:
    """Render a template file using variables from a vault."""
    try:
        variables = pull(args.vault, args.passphrase)
    except EnvaultError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        rendered = render_template_file(args.template, variables, strict=not args.loose)
    except TemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(rendered)
        except OSError as exc:
            print(f"error: cannot write output file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(rendered, end="")


def cmd_template_inspect(args: argparse.Namespace) -> None:
    """List all variable placeholders referenced in a template file."""
    try:
        with open(args.template, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    placeholders = list_placeholders(text)
    if not placeholders:
        print("No placeholders found.")
    else:
        for name in placeholders:
            print(name)


def build_template_subparser(subparsers: argparse._SubParsersAction) -> None:
    tp = subparsers.add_parser("template", help="Render templates using vault variables")
    tsub = tp.add_subparsers(dest="template_cmd", required=True)

    render_p = tsub.add_parser("render", help="Render a template with vault variables")
    render_p.add_argument("vault", help="Vault name to load variables from")
    render_p.add_argument("template", help="Path to the template file")
    render_p.add_argument("--passphrase", required=True, help="Vault passphrase")
    render_p.add_argument("--output", "-o", default=None, help="Write output to file instead of stdout")
    render_p.add_argument("--loose", action="store_true", help="Leave unresolved placeholders instead of erroring")
    render_p.set_defaults(func=cmd_template_render)

    inspect_p = tsub.add_parser("inspect", help="List placeholders in a template")
    inspect_p.add_argument("template", help="Path to the template file")
    inspect_p.set_defaults(func=cmd_template_inspect)
