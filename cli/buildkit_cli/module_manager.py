from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from buildkit_cli.generator import DEFAULT_MODULES, GenerationError, _materialize_project, _preflight
from buildkit_cli.registry import ModuleRegistry, RegistryError, load_registry


class ModuleOperationError(ValueError):
    """Raised for controlled add/remove failures."""


@dataclass(frozen=True)
class ModuleOperationResult:
    requested_modules: tuple[str, ...]
    automatic_modules: tuple[str, ...]
    installed_modules: tuple[str, ...]
    changed: bool


def add_modules(
    requested: list[str],
    *,
    project_root: Path | None = None,
    registry: ModuleRegistry | None = None,
) -> ModuleOperationResult:
    root, state, module_registry = _context(project_root, registry)
    requested_names = _validate_requested(requested, module_registry)
    desired_selected = tuple(sorted(set(state["selected_modules"]) | set(requested_names)))
    desired_installed = _resolve(module_registry, desired_selected)
    added = tuple(name for name in desired_installed if name not in state["installed_modules"])
    changed = desired_selected != tuple(state["selected_modules"]) or bool(added)
    if changed:
        _mutate(root, state, desired_selected, desired_installed, module_registry)
    automatic = tuple(name for name in added if name not in requested_names)
    return ModuleOperationResult(requested_names, automatic, desired_installed, changed)


def remove_modules(
    requested: list[str],
    *,
    project_root: Path | None = None,
    registry: ModuleRegistry | None = None,
) -> ModuleOperationResult:
    root, state, module_registry = _context(project_root, registry)
    requested_names = _validate_requested(requested, module_registry)
    actually_removed = tuple(name for name in requested_names if name in state["selected_modules"])
    desired_selected = tuple(sorted(set(state["selected_modules"]) - set(requested_names)))
    desired_installed = _resolve(module_registry, desired_selected)
    removed = tuple(name for name in state["installed_modules"] if name not in desired_installed)
    changed = bool(actually_removed or removed)
    if changed:
        _mutate(root, state, desired_selected, desired_installed, module_registry)
    automatic = tuple(name for name in removed if name not in actually_removed)
    return ModuleOperationResult(actually_removed, automatic, desired_installed, changed)


def _context(
    project_root: Path | None, registry: ModuleRegistry | None
) -> tuple[Path, dict[str, Any], ModuleRegistry]:
    root = (project_root or Path.cwd()).resolve()
    module_registry = registry or load_registry()
    state = _load_state(root)
    _validate_state(state, root, module_registry)
    return root, state, module_registry


def _load_state(root: Path) -> dict[str, Any]:
    path = root / ".buildkit" / "project.json"
    if not path.is_file():
        raise ModuleOperationError("Current directory is not a BuildKit-managed project")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModuleOperationError(f"Invalid project state: {path}") from exc
    if not isinstance(state, dict):
        raise ModuleOperationError("Invalid project state: expected a JSON object")
    return state


def _validate_state(state: dict[str, Any], root: Path, registry: ModuleRegistry) -> None:
    expected = {
        "schema_version", "buildkit_version", "project_name", "selected_modules",
        "installed_modules", "files",
    }
    if set(state) != expected or state.get("schema_version") != 1:
        raise ModuleOperationError("Invalid or unsupported project state schema")
    if not isinstance(state["project_name"], str) or not state["project_name"]:
        raise ModuleOperationError("Invalid project state: project_name")
    for field in ("selected_modules", "installed_modules"):
        value = state[field]
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ModuleOperationError(f"Invalid project state: {field}")
        if len(value) != len(set(value)):
            raise ModuleOperationError(f"Invalid project state: duplicate {field}")
    if not isinstance(state["files"], dict):
        raise ModuleOperationError("Invalid project state: files")

    try:
        expected_installed = _resolve(registry, tuple(state["selected_modules"]))
    except ModuleOperationError as exc:
        raise ModuleOperationError(f"Invalid project state: {exc}") from exc
    if tuple(state["installed_modules"]) != expected_installed:
        raise ModuleOperationError("Invalid project state: installed_modules does not match selection")

    installed = set(state["installed_modules"])
    for relative, metadata in state["files"].items():
        if not _safe_relative_path(relative):
            raise ModuleOperationError(f"Invalid project state path: {relative}")
        if not isinstance(metadata, dict) or set(metadata) != {"owner", "sha256"}:
            raise ModuleOperationError(f"Invalid project state metadata: {relative}")
        owner, digest = metadata["owner"], metadata["sha256"]
        if owner != "generator" and owner not in installed:
            raise ModuleOperationError(f"Invalid project state owner for: {relative}")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ModuleOperationError(f"Invalid project state hash for: {relative}")

    for module_name in installed:
        for template_file in registry[module_name].files:
            relative = template_file.destination.replace("\\", "/")
            metadata = state["files"].get(relative)
            expected_owner = "generator" if relative in _generator_paths() else module_name
            if not metadata or metadata["owner"] != expected_owner:
                raise ModuleOperationError(f"Invalid project state ownership for: {relative}")


def _safe_relative_path(value: object) -> bool:
    if not isinstance(value, str):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and value not in {"", "."}


def _validate_requested(requested: list[str], registry: ModuleRegistry) -> tuple[str, ...]:
    names = tuple(sorted(set(requested)))
    for name in names:
        try:
            manifest = registry[name]
        except RegistryError as exc:
            raise ModuleOperationError(str(exc)) from exc
        if not manifest.selectable:
            raise ModuleOperationError(f"Module '{name}' is a foundation module and cannot be managed directly")
    return names


def _resolve(registry: ModuleRegistry, selected: tuple[str, ...]) -> tuple[str, ...]:
    try:
        defaults = registry.resolve(list(DEFAULT_MODULES))
        features = registry.resolve(list(selected)) if selected else ()
    except RegistryError as exc:
        raise ModuleOperationError(str(exc)) from exc
    return tuple(dict.fromkeys((*defaults, *features)))


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_owned_file(root: Path, relative: str, metadata: dict[str, str]) -> None:
    path = root / relative
    if not path.is_file():
        raise ModuleOperationError(f"BuildKit-owned file is missing: {relative}")
    if _hash(path) != metadata["sha256"]:
        raise ModuleOperationError(f"BuildKit-owned file has been modified: {relative}")


def _generator_paths() -> set[str]:
    return {
        ".env.example", "backend/app/core/config.py", "backend/requirements.txt",
        "frontend/package.json", "frontend/src/app/moduleRoutes.tsx",
        "frontend/src/app/moduleNavigation.ts", "backend/app/module_routes.py",
    }


def _mutate(
    root: Path,
    state: dict[str, Any],
    desired_selected: tuple[str, ...],
    desired_installed: tuple[str, ...],
    registry: ModuleRegistry,
) -> None:
    old_installed = tuple(state["installed_modules"])
    new_modules = set(desired_installed) - set(old_installed)
    removed_modules = set(old_installed) - set(desired_installed)
    files: dict[str, dict[str, str]] = state["files"]

    for relative, metadata in files.items():
        if metadata["owner"] == "generator" or metadata["owner"] in removed_modules:
            _verify_owned_file(root, relative, metadata)

    new_paths: set[str] = set()
    for module_name in new_modules:
        for template_file in registry[module_name].files:
            relative = template_file.destination.replace("\\", "/")
            if (root / relative).exists():
                raise ModuleOperationError(f"Destination already exists and cannot be overwritten: {relative}")
            new_paths.add(relative)

    try:
        _preflight(registry, desired_installed)
    except GenerationError as exc:
        raise ModuleOperationError(str(exc)) from exc

    staging = Path(tempfile.mkdtemp(prefix=".buildkit-mutation-", dir=root.parent))
    try:
        _materialize_project(
            staging, state["project_name"], desired_selected, desired_installed, registry
        )
        staged_state = json.loads((staging / ".buildkit/project.json").read_text(encoding="utf-8"))

        final_files = {
            path: metadata
            for path, metadata in files.items()
            if metadata["owner"] not in removed_modules and metadata["owner"] != "generator"
        }
        for path in new_paths:
            final_files[path] = staged_state["files"][path]
        for path, metadata in staged_state["files"].items():
            if metadata["owner"] == "generator":
                final_files[path] = metadata
        staged_state["files"] = dict(sorted(final_files.items()))
        (staging / ".buildkit/project.json").write_text(
            json.dumps(staged_state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        removed_paths = [
            path for path, metadata in files.items() if metadata["owner"] in removed_modules
        ]
        replacement_paths = sorted(new_paths | _generator_paths())
        _commit(root, staging, replacement_paths, removed_paths)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _commit(root: Path, staging: Path, replacements: list[str], removals: list[str]) -> None:
    transaction = Path(tempfile.mkdtemp(prefix="transaction-", dir=root / ".buildkit"))
    created: list[Path] = []
    backed_up: list[tuple[Path, Path]] = []
    try:
        affected = sorted(set(replacements) | set(removals))
        for relative in affected:
            destination = root / relative
            if destination.is_file():
                backup = transaction / relative
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(destination, backup)
                backed_up.append((destination, backup))

        for relative in replacements:
            source = staging / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                created.append(destination)
            temporary = destination.with_name(f".{destination.name}.buildkit-tmp")
            shutil.copyfile(source, temporary)
            temporary.replace(destination)

        for relative in removals:
            path = root / relative
            path.unlink()

        state_source = staging / ".buildkit/project.json"
        state_destination = root / ".buildkit/project.json"
        state_temporary = root / ".buildkit/project.json.buildkit-tmp"
        shutil.copyfile(state_source, state_temporary)
        state_temporary.replace(state_destination)
    except Exception:
        for path in created:
            if path.is_file():
                path.unlink()
        for destination, backup in reversed(backed_up):
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(backup, destination)
        raise
    finally:
        shutil.rmtree(transaction, ignore_errors=True)

    for relative in removals:
        _prune_empty_parents((root / relative).parent, root)


def _prune_empty_parents(directory: Path, root: Path) -> None:
    while directory != root and directory != root / ".buildkit":
        try:
            directory.rmdir()
        except OSError:
            break
        directory = directory.parent
