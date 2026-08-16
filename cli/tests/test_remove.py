from __future__ import annotations

import json
from pathlib import Path

import pytest

from buildkit_cli.cli import main
from buildkit_cli.generator import create_project
from buildkit_cli.module_manager import ModuleOperationError, add_modules, remove_modules


def state_bytes(project: Path) -> bytes:
    return (project / ".buildkit/project.json").read_bytes()


def state(project: Path) -> dict:
    return json.loads(state_bytes(project))


def test_remove_feature_and_unused_dependencies(tmp_path: Path) -> None:
    project = create_project("demo", ["auth"], working_directory=tmp_path).project_path
    result = remove_modules(["auth"], project_root=project)
    assert result.requested_modules == ("auth",)
    assert set(result.automatic_modules) == {"postgres", "migrations"}
    assert result.installed_modules == ("config", "logging", "fastapi", "frontend")
    assert not (project / "backend/app/api/routes/auth.py").exists()
    assert (project / "backend/app/main.py").is_file()


def test_remove_multiple_features_and_retain_shared_foundations(tmp_path: Path) -> None:
    project = create_project("demo", ["charts", "maps", "upload"], working_directory=tmp_path).project_path
    remove_modules(["charts", "maps"], project_root=project)
    project_state = state(project)
    assert project_state["selected_modules"] == ["upload"]
    assert "frontend" in project_state["installed_modules"] and "fastapi" in project_state["installed_modules"]
    assert (project / "frontend/src/features/upload/UploadPage.tsx").is_file()


@pytest.mark.parametrize("module", ["frontend", "fastapi", "postgres", "missing"])
def test_foundation_and_unknown_removal_is_rejected(tmp_path: Path, module: str) -> None:
    project = create_project("demo", ["auth"], working_directory=tmp_path).project_path
    with pytest.raises(ModuleOperationError):
        remove_modules([module], project_root=project)


def test_non_selected_remove_is_clean_noop(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    before = state_bytes(project)
    result = remove_modules(["maps"], project_root=project)
    assert result.changed is False and result.requested_modules == ()
    assert state_bytes(project) == before


def test_modified_module_file_blocks_entire_removal(tmp_path: Path) -> None:
    project = create_project("demo", ["charts", "maps"], working_directory=tmp_path).project_path
    changed = project / "frontend/src/features/charts/ChartsPage.tsx"
    changed.write_text(changed.read_text() + "// user change\n", encoding="utf-8")
    with pytest.raises(ModuleOperationError, match="ChartsPage.tsx"):
        remove_modules(["charts", "maps"], project_root=project)
    assert (project / "frontend/src/features/maps/MapsPage.tsx").is_file()
    assert set(state(project)["selected_modules"]) == {"charts", "maps"}


def test_failed_remove_after_module_lifecycle_preserves_state_and_default_foundation(
    tmp_path: Path,
) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    add_modules(["auth"], project_root=project)
    add_modules(["charts", "maps"], project_root=project)
    remove_modules(["maps"], project_root=project)
    remove_modules(["auth"], project_root=project)

    before_state = state(project)
    before_bytes = state_bytes(project)
    assert before_state["selected_modules"] == ["charts"]
    assert before_state["installed_modules"] == [
        "config", "logging", "fastapi", "frontend", "charts"
    ]

    chart = project / "frontend/src/features/charts/ChartsPage.tsx"
    chart.write_text(chart.read_text(encoding="utf-8") + "// user modification\n", encoding="utf-8")

    with pytest.raises(ModuleOperationError, match="ChartsPage.tsx"):
        remove_modules(["charts"], project_root=project)

    after_bytes = state_bytes(project)
    after_state = state(project)
    assert after_bytes == before_bytes
    assert after_state["selected_modules"] == ["charts"]
    assert after_state["installed_modules"] == [
        "config", "logging", "fastapi", "frontend", "charts"
    ]
    assert after_state["files"] == before_state["files"]


def test_modified_generator_file_blocks_removal(tmp_path: Path) -> None:
    project = create_project("demo", ["charts"], working_directory=tmp_path).project_path
    routes = project / "frontend/src/app/moduleRoutes.tsx"
    routes.write_text(routes.read_text() + "// user change\n", encoding="utf-8")
    with pytest.raises(ModuleOperationError, match="moduleRoutes.tsx"):
        remove_modules(["charts"], project_root=project)
    assert (project / "frontend/src/features/charts/ChartsPage.tsx").is_file()


def test_user_file_is_retained_and_empty_directories_are_pruned(tmp_path: Path) -> None:
    first = create_project("first", ["maps"], working_directory=tmp_path).project_path
    remove_modules(["maps"], project_root=first)
    assert not (first / "frontend/src/features/maps").exists()

    second = create_project("second", ["maps"], working_directory=tmp_path).project_path
    user_file = second / "frontend/src/features/maps/notes.txt"
    user_file.write_text("keep", encoding="utf-8")
    remove_modules(["maps"], project_root=second)
    assert user_file.read_text() == "keep"
    assert not (second / "frontend/src/features/maps/MapsPage.tsx").exists()


def test_remove_regenerates_all_controlled_files(tmp_path: Path) -> None:
    project = create_project("demo", ["auth", "charts", "maps", "upload"], working_directory=tmp_path).project_path
    remove_modules(["auth", "maps", "upload"], project_root=project)
    package = json.loads((project / "frontend/package.json").read_text())
    assert "recharts" in package["dependencies"] and "leaflet" not in package["dependencies"]
    requirements = (project / "backend/requirements.txt").read_text()
    assert "PyJWT" not in requirements and "python-multipart" not in requirements
    environment = (project / ".env.example").read_text()
    assert "JWT_SECRET_KEY" not in environment and "MAX_UPLOAD_SIZE" not in environment
    routes = (project / "frontend/src/app/moduleRoutes.tsx").read_text()
    assert "ChartsPage" in routes and "LoginPage" not in routes and "MapsPage" not in routes
    assert "auth_router" not in (project / "backend/app/module_routes.py").read_text()


def test_create_add_remove_returns_to_equivalent_controlled_state(tmp_path: Path) -> None:
    project = create_project("demo", working_directory=tmp_path).project_path
    before = state_bytes(project)
    add_modules(["auth", "charts"], project_root=project)
    remove_modules(["auth", "charts"], project_root=project)
    assert state_bytes(project) == before


def test_remove_cli_reports_result(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    project = create_project("demo", ["auth"], working_directory=tmp_path).project_path
    monkeypatch.chdir(project)
    assert main(["remove", "auth"]) == 0
    output = capsys.readouterr().out
    assert "Removed modules: auth" in output
    assert "Automatically removed: postgres, migrations" in output
