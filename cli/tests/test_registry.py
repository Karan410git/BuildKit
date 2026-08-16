from __future__ import annotations

import json
from pathlib import Path

import pytest

from buildkit_cli.registry import RegistryError, load_registry


def manifest_data(name: str, *, requires: list[str] | None = None, destination: str | None = None) -> dict:
    files = []
    if destination:
        files.append({"source": "files/source.txt", "destination": destination})
    return {
        "schema_version": 1, "name": name, "description": f"{name} module",
        "selectable": True, "requires": requires or [], "files": files,
        "frontend_dependencies": {}, "frontend_dev_dependencies": {},
        "backend_dependencies": [], "backend_routes": [], "frontend_routes": [],
        "navigation": [], "configuration": [], "migrations": [],
    }


def write_manifest(root: Path, directory: str, data: dict) -> None:
    module_root = root / directory
    (module_root / "files").mkdir(parents=True)
    (module_root / "files" / "source.txt").write_text("template", encoding="utf-8")
    (module_root / "module.json").write_text(json.dumps(data), encoding="utf-8")


def test_real_registry_loads_all_approved_modules() -> None:
    registry = load_registry()
    assert set(registry) == {
        "auth", "charts", "config", "docker", "fastapi", "frontend",
        "logging", "maps", "migrations", "postgres", "upload",
    }


def test_invalid_manifest_is_rejected(tmp_path: Path) -> None:
    write_manifest(tmp_path, "bad", {"schema_version": 1})
    with pytest.raises(RegistryError, match="missing fields"):
        load_registry(tmp_path)


def test_duplicate_module_name_is_rejected(tmp_path: Path) -> None:
    write_manifest(tmp_path, "one", manifest_data("duplicate"))
    write_manifest(tmp_path, "two", manifest_data("duplicate"))
    with pytest.raises(RegistryError, match="Duplicate module name"):
        load_registry(tmp_path)


def test_missing_required_module_is_rejected(tmp_path: Path) -> None:
    write_manifest(tmp_path, "one", manifest_data("one", requires=["missing"]))
    with pytest.raises(RegistryError, match="requires missing module"):
        load_registry(tmp_path)


def test_destination_ownership_conflict_is_rejected(tmp_path: Path) -> None:
    write_manifest(tmp_path, "one", manifest_data("one", destination="shared.txt"))
    write_manifest(tmp_path, "two", manifest_data("two", destination="shared.txt"))
    with pytest.raises(RegistryError, match="owned by both"):
        load_registry(tmp_path)


def test_registry_rejects_dependency_cycle(tmp_path: Path) -> None:
    write_manifest(tmp_path, "one", manifest_data("one", requires=["two"]))
    write_manifest(tmp_path, "two", manifest_data("two", requires=["one"]))
    with pytest.raises(RegistryError, match="Dependency cycle"):
        load_registry(tmp_path)
