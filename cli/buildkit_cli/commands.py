from __future__ import annotations

import argparse

from buildkit_cli.registry import load_registry


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
    """List modules from the internal BuildKit registry."""
    del args
    registry = load_registry()
    selectable = [registry[name] for name in registry if registry[name].selectable]
    foundations = [registry[name] for name in registry if not registry[name].selectable]

    print("Selectable feature modules:")
    for manifest in selectable:
        print(f"  {manifest.name:<10} {manifest.description}")
    print("Foundation modules (automatically required):")
    for manifest in foundations:
        print(f"  {manifest.name:<10} {manifest.description}")
    return 0
