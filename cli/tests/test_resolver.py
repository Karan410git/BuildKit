from pathlib import Path

import pytest

from buildkit_cli.manifest import ModuleManifest
from buildkit_cli.resolver import ResolutionError, resolve_modules


def manifest(name: str, requires: list[str]) -> ModuleManifest:
    return ModuleManifest(
        schema_version=1, name=name, description=name, selectable=True,
        requires=tuple(requires), files=(), frontend_dependencies={},
        frontend_dev_dependencies={}, backend_dependencies=(), backend_routes=(),
        frontend_routes=(), navigation=(), configuration=(), migrations=(),
        manifest_path=Path(name) / "module.json",
    )


def test_resolves_transitive_dependencies_before_dependents() -> None:
    manifests = {
        "config": manifest("config", []),
        "fastapi": manifest("fastapi", ["config"]),
        "upload": manifest("upload", ["fastapi", "config"]),
    }
    assert resolve_modules(manifests, ["upload"]) == ("config", "fastapi", "upload")


def test_resolution_is_deduplicated_and_deterministic() -> None:
    manifests = {
        "frontend": manifest("frontend", []),
        "charts": manifest("charts", ["frontend"]),
        "maps": manifest("maps", ["frontend"]),
    }
    expected = ("frontend", "charts", "maps")
    assert resolve_modules(manifests, ["maps", "charts", "maps"]) == expected
    assert resolve_modules(manifests, ["charts", "maps"]) == expected


def test_unknown_module_is_rejected() -> None:
    with pytest.raises(ResolutionError, match="Unknown module: missing"):
        resolve_modules({}, ["missing"])


def test_dependency_cycle_is_rejected() -> None:
    manifests = {"a": manifest("a", ["b"]), "b": manifest("b", ["a"])}
    with pytest.raises(ResolutionError, match="Dependency cycle"):
        resolve_modules(manifests, ["a"])
