from __future__ import annotations

import argparse


def _not_implemented(command: str) -> int:
    print(f"The '{command}' command is not implemented yet.")
    return 1


def create_command(args: argparse.Namespace) -> int:
    """Handle the create command once project generation is implemented."""
    del args
    return _not_implemented("create")


def add_command(args: argparse.Namespace) -> int:
    """Handle the add command once module management is implemented."""
    del args
    return _not_implemented("add")


def remove_command(args: argparse.Namespace) -> int:
    """Handle the remove command once module management is implemented."""
    del args
    return _not_implemented("remove")


def modules_command(args: argparse.Namespace) -> int:
    """Handle the modules command once the module registry is implemented."""
    del args
    return _not_implemented("modules")
