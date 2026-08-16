from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from buildkit_cli.cli import main
from buildkit_cli.generator import create_project
from buildkit_cli.module_manager import ModuleOperationError, add_modules


def state(project: Path) -> dict:
    return json.loads((project / ".buildkit/project.json").read_text(encoding="utf-8"))


def test_add_one_feature_and_transitive_dependencies(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    result = add_modules(["auth"], project_root=project)
    assert result.requested_modules == ("auth",)
    assert set(result.automatic_modules) == {"postgres", "migrations"}
    assert set(result.installed_modules) == {
        "config", "logging", "fastapi", "frontend", "postgres", "migrations", "auth"
    }
    assert (project / "backend/app/api/routes/auth.py").is_file()
    assert not (project / "frontend/src/features/upload/UploadPage.tsx").exists()


def test_add_multiple_and_duplicate_features(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    result = add_modules(["maps", "charts", "maps"], project_root=project)
    assert result.requested_modules == ("charts", "maps")
    assert state(project)["selected_modules"] == ["charts", "maps"]
    assert (project / "frontend/src/features/charts/ChartsPage.tsx").is_file()
    assert (project / "frontend/src/features/maps/MapsPage.tsx").is_file()


def test_already_selected_add_is_idempotent(tmp_path: Path) -> None:
    project = create_project("demo", ["charts"], working_directory=tmp_path).project_path
    before = (project / ".buildkit/project.json").read_bytes()
    result = add_modules(["charts"], project_root=project)
    assert result.changed is False
    assert (project / ".buildkit/project.json").read_bytes() == before


@pytest.mark.parametrize("module", ["missing", "frontend", "postgres"])
def test_invalid_requested_module_is_rejected(tmp_path: Path, module: str) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    with pytest.raises(ModuleOperationError):
        add_modules([module], project_root=project)


def test_unmanaged_and_invalid_state_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ModuleOperationError, match="not a BuildKit-managed"):
        add_modules(["charts"], project_root=tmp_path)
    project = create_project("demo", working_directory=tmp_path).project_path
    (project / ".buildkit/project.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ModuleOperationError, match="state"):
        add_modules(["charts"], project_root=project)


def test_unowned_destination_collision_blocks_add(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    collision = project / "frontend/src/features/auth/LoginPage.tsx"
    collision.parent.mkdir(parents=True)
    collision.write_text("user file", encoding="utf-8")
    before = (project / ".buildkit/project.json").read_bytes()
    with pytest.raises(ModuleOperationError, match="Destination already exists"):
        add_modules(["auth"], project_root=project)
    assert collision.read_text() == "user file"
    assert (project / ".buildkit/project.json").read_bytes() == before


def test_modified_generator_file_blocks_add(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    package = project / "frontend/package.json"
    package.write_text(package.read_text() + "\n", encoding="utf-8")
    with pytest.raises(ModuleOperationError, match="frontend/package.json"):
        add_modules(["charts"], project_root=project)
    assert not (project / "frontend/src/features/charts").exists()


def test_add_regenerates_dependencies_configuration_and_integrations(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    add_modules(["auth", "maps", "upload"], project_root=project)
    package = json.loads((project / "frontend/package.json").read_text())
    assert "leaflet" in package["dependencies"]
    requirements = (project / "backend/requirements.txt").read_text()
    assert "PyJWT>=2.8.0" in requirements and "python-multipart>=0.0.6" in requirements
    environment = (project / ".env.example").read_text()
    assert "JWT_SECRET_KEY=" in environment and "MAX_UPLOAD_SIZE=" in environment
    routes = (project / "frontend/src/app/moduleRoutes.tsx").read_text()
    assert "LoginPage" in routes and "MapsPage" in routes and "UploadPage" in routes
    backend = (project / "backend/app/module_routes.py").read_text()
    assert "auth_router" in backend and "upload_router" in backend
    assert not (project / ".env").exists()


def test_add_updates_ownership_and_hashes(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    add_modules(["charts"], project_root=project)
    project_state = state(project)
    path = "frontend/src/features/charts/ChartsPage.tsx"
    assert project_state["files"][path]["owner"] == "charts"
    assert project_state["files"][path]["sha256"] == hashlib.sha256((project / path).read_bytes()).hexdigest()


def test_add_cli_reports_result(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    monkeypatch.chdir(project)
    assert main(["add", "auth"]) == 0
    output = capsys.readouterr().out
    assert "Added modules: auth" in output
    assert "Automatically included: postgres, migrations" in output
