from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from buildkit_cli.generator import create_project
from buildkit_cli.module_manager import add_modules, remove_modules
from buildkit_cli.registry import load_registry


@pytest.mark.parametrize(
    "modules",
    [
        [],
        ["auth"],
        ["upload"],
        ["charts"],
        ["maps"],
        ["auth", "charts", "maps"],
        ["upload", "charts"],
    ],
)
def test_generated_project_matrix_has_valid_controlled_source(
    tmp_path: Path,
    modules: list[str],
) -> None:
    project = create_project("demo", modules, working_directory=tmp_path).project_path

    for python_file in project.glob("backend/**/*.py"):
        ast.parse(python_file.read_text(encoding="utf-8"), filename=str(python_file))

    package = json.loads((project / "frontend/package.json").read_text(encoding="utf-8"))
    assert isinstance(package["dependencies"], dict)
    assert isinstance(package["devDependencies"], dict)

    for generated_file in [
        project / "backend/app/module_routes.py",
        project / "frontend/src/app/moduleRoutes.tsx",
        project / "frontend/src/app/moduleNavigation.ts",
        project / "backend/app/core/config.py",
        project / ".env.example",
    ]:
        assert "__BUILDKIT_" not in generated_file.read_text(encoding="utf-8")

    assert not (project / ".env").exists()
    state = json.loads((project / ".buildkit/project.json").read_text(encoding="utf-8"))
    for relative, metadata in state["files"].items():
        assert hashlib.sha256((project / relative).read_bytes()).hexdigest() == metadata["sha256"]


def test_generated_project_lifecycle_remains_structurally_valid(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    add_modules(["auth"], project_root=project)
    add_modules(["charts", "maps"], project_root=project)
    add_modules(["charts"], project_root=project)
    remove_modules(["maps"], project_root=project)
    remove_modules(["upload"], project_root=project)
    remove_modules(["auth", "charts"], project_root=project)
    add_modules(["upload", "charts"], project_root=project)

    state = json.loads((project / ".buildkit/project.json").read_text(encoding="utf-8"))
    assert state["selected_modules"] == ["charts", "upload"]
    assert set(state["installed_modules"]) == {
        "config", "logging", "fastapi", "frontend", "charts", "upload"
    }
    for python_file in project.glob("backend/**/*.py"):
        ast.parse(python_file.read_text(encoding="utf-8"), filename=str(python_file))


def test_docker_template_has_expected_static_structure() -> None:
    docker = load_registry()["docker"]
    compose_mapping = next(file for file in docker.files if file.destination == "docker-compose.yml")
    compose = (docker.manifest_path.parent / compose_mapping.source).read_text(encoding="utf-8")
    assert "services:" in compose
    assert "backend:" in compose
    assert "postgres:" in compose
    assert "postgres_data:" in compose
