from __future__ import annotations

import argparse
from collections.abc import Sequence

from buildkit_cli.commands import (
    add_command,
    create_command,
    modules_command,
    remove_command,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="buildkit",
        description="BuildKit project and module management CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a BuildKit project.")
    create_parser.add_argument("project_name", help="Name of the project to create.")
    create_parser.add_argument(
        "--modules",
        nargs="+",
        default=None,
        metavar="MODULE",
        help="Modules to include in the project.",
    )
    create_parser.set_defaults(handler=create_command)

    add_parser = subparsers.add_parser("add", help="Add modules to a BuildKit project.")
    add_parser.add_argument("modules", nargs="+", metavar="MODULE")
    add_parser.set_defaults(handler=add_command)

    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove modules from a BuildKit project.",
    )
    remove_parser.add_argument("modules", nargs="+", metavar="MODULE")
    remove_parser.set_defaults(handler=remove_command)

    modules_parser = subparsers.add_parser(
        "modules",
        help="List available and installed BuildKit modules.",
    )
    modules_parser.set_defaults(handler=modules_command)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)
