from __future__ import annotations

import argparse

from buildkit_cli.generator import GenerationError, create_project
from buildkit_cli.module_manager import ModuleOperationError, add_modules, remove_modules
from buildkit_cli.registry import load_registry


def _not_implemented(command: str) -> int:
    print(f"The '{command}' command is not implemented yet.")
    return 1


def create_command(args: argparse.Namespace) -> int:
    """Create a standalone BuildKit project."""
    try:
        result = create_project(args.project_name, args.modules)
    except GenerationError as exc:
        print(f"Error: {exc}")
        return 1

    selected = ", ".join(result.selected_modules) or "none"
    automatic = [name for name in result.installed_modules if name not in result.selected_modules]
    print(f"Created project: {result.project_path}")
    print(f"Selected modules: {selected}")
    print(f"Automatically included: {', '.join(automatic)}")
    return 0


def add_command(args: argparse.Namespace) -> int:
    """Add selectable modules to a managed BuildKit project."""
    try:
        result = add_modules(args.modules)
    except ModuleOperationError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Added modules: {', '.join(result.requested_modules)}")
    print(f"Automatically included: {', '.join(result.automatic_modules) or 'none'}")
    print(f"Installed modules: {', '.join(result.installed_modules)}")
    if not result.changed:
        print("No changes were necessary.")
    return 0


def remove_command(args: argparse.Namespace) -> int:
    """Safely remove selectable modules from a managed BuildKit project."""
    try:
        result = remove_modules(args.modules)
    except ModuleOperationError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Removed modules: {', '.join(result.requested_modules) or 'none'}")
    print(f"Automatically removed: {', '.join(result.automatic_modules) or 'none'}")
    print(f"Installed modules: {', '.join(result.installed_modules)}")
    if not result.changed:
        print("No changes were necessary.")
    return 0


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
