from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import buildkit_cli.generator as generator
from buildkit_cli.cli import main
from buildkit_cli.generator import (
    GenerationError,
    _merge_configuration,
    _merge_dependency_maps,
    create_project,
)
from buildkit_cli.manifest import ModuleManifest


def read_state(project: Path) -> dict:
    return json.loads((project / ".buildkit/project.json").read_text(encoding="utf-8"))


def test_create_default_project(tmp_path: Path) -> None:
    result = create_project("demo", working_directory=tmp_path)
    assert result.installed_modules == ("config", "logging", "fastapi", "frontend")
    assert result.selected_modules == ()
    assert (result.project_path / "backend/app/main.py").is_file()
    assert (result.project_path / "frontend/src/App.tsx").is_file()


def test_create_with_one_module_includes_transitive_dependencies(tmp_path: Path) -> None:
    result = create_project("demo", ["auth"], working_directory=tmp_path)
    assert result.selected_modules == ("auth",)
    assert set(result.installed_modules) == {
        "config", "logging", "fastapi", "frontend", "postgres", "migrations", "auth"
    }
    assert (result.project_path / "backend/app/api/routes/auth.py").is_file()
    assert not (result.project_path / "frontend/src/features/upload/UploadPage.tsx").exists()


def test_create_with_multiple_modules_excludes_unselected_features(tmp_path: Path) -> None:
    result = create_project("demo", ["charts", "maps"], working_directory=tmp_path)
    assert set(result.installed_modules) == {
        "config", "logging", "fastapi", "frontend", "charts", "maps"
    }
    assert not (result.project_path / "backend/app/api/routes/upload.py").exists()
    assert not (result.project_path / "frontend/src/features/auth/LoginPage.tsx").exists()


def test_duplicate_module_arguments_are_deduplicated(tmp_path: Path) -> None:
    result = create_project("demo", ["charts", "charts"], working_directory=tmp_path)
    assert result.selected_modules == ("charts",)
    assert result.installed_modules.count("charts") == 1


@pytest.mark.parametrize("modules", [["missing"], ["frontend"]])
def test_unknown_and_non_selectable_modules_are_rejected(tmp_path: Path, modules: list[str]) -> None:
    with pytest.raises(GenerationError):
        create_project("demo", modules, working_directory=tmp_path)
    assert not (tmp_path / "demo").exists()


@pytest.mark.parametrize("name", ["../demo", "a/b", "a\\b", ".", "..", "bad name"])
def test_unsafe_project_names_are_rejected(tmp_path: Path, name: str) -> None:
    with pytest.raises(GenerationError, match="Project name"):
        create_project(name, working_directory=tmp_path)


def test_existing_destination_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "demo").mkdir()
    with pytest.raises(GenerationError, match="already exists"):
        create_project("demo", working_directory=tmp_path)


def test_project_state_is_deterministic_and_records_hashes(tmp_path: Path) -> None:
    first_root, second_root = tmp_path / "one", tmp_path / "two"
    first_root.mkdir(); second_root.mkdir()
    first = create_project("demo", ["charts"], working_directory=first_root).project_path
    second = create_project("demo", ["charts"], working_directory=second_root).project_path
    first_text = (first / ".buildkit/project.json").read_text(encoding="utf-8")
    second_text = (second / ".buildkit/project.json").read_text(encoding="utf-8")
    assert first_text == second_text
    assert first_text.endswith("\n")
    state = json.loads(first_text)
    assert set(state) == {
        "schema_version", "buildkit_version", "project_name", "selected_modules",
        "installed_modules", "files",
    }
    for path, metadata in state["files"].items():
        assert set(metadata) == {"owner", "sha256"}
        assert metadata["sha256"] == hashlib.sha256((first / path).read_bytes()).hexdigest()


def test_dependency_manifests_are_generated_from_union(tmp_path: Path) -> None:
    project = create_project("demo", ["auth", "maps"], working_directory=tmp_path).project_path
    package = json.loads((project / "frontend/package.json").read_text(encoding="utf-8"))
    assert set(package["dependencies"]) == {
        "leaflet", "react", "react-dom", "react-leaflet", "react-router-dom"
    }
    assert "@types/leaflet" in package["devDependencies"]
    requirements = (project / "backend/requirements.txt").read_text(encoding="utf-8")
    assert "fastapi>=0.100.0" in requirements
    assert "sqlalchemy>=2.0" in requirements
    assert "PyJWT>=2.8.0" in requirements


def test_configuration_contains_only_installed_contributions_and_no_real_env(tmp_path: Path) -> None:
    default = create_project("default", working_directory=tmp_path).project_path
    default_env = (default / ".env.example").read_text(encoding="utf-8")
    assert "APP_NAME=BuildKit" in default_env
    assert "VITE_API_BASE_URL=" in default_env
    assert "DATABASE_URL=" not in default_env
    assert "JWT_SECRET_KEY=" not in default_env
    assert not (default / ".env").exists()

    auth = create_project("auth-project", ["auth"], working_directory=tmp_path).project_path
    auth_env = (auth / ".env.example").read_text(encoding="utf-8")
    assert "DATABASE_URL=" in auth_env
    assert "JWT_SECRET_KEY=" in auth_env
    assert "Development/example value only" in auth_env


def test_integrations_contain_only_installed_features(tmp_path: Path) -> None:
    default = create_project("default", working_directory=tmp_path).project_path
    assert "ChartsPage" not in (default / "frontend/src/app/moduleRoutes.tsx").read_text()
    assert "auth" not in (default / "backend/app/module_routes.py").read_text()
    assert "export const moduleRoutes = [" in (default / "frontend/src/app/moduleRoutes.tsx").read_text()

    project = create_project("selected", ["charts", "upload"], working_directory=tmp_path).project_path
    routes = (project / "frontend/src/app/moduleRoutes.tsx").read_text()
    navigation = (project / "frontend/src/app/moduleNavigation.ts").read_text()
    backend = (project / "backend/app/module_routes.py").read_text()
    assert "ChartsPage" in routes and "UploadPage" in routes
    assert "LoginPage" not in routes and "MapsPage" not in routes
    assert '"Charts"' in navigation and '"Upload"' in navigation
    assert "upload_router" in backend and "auth_router" not in backend


def fake_manifest(name: str, *, frontend: dict[str, str] | None = None, configuration: tuple[dict[str, str], ...] = ()) -> ModuleManifest:
    return ModuleManifest(
        schema_version=1, name=name, description=name, selectable=True, requires=(), files=(),
        frontend_dependencies=frontend or {}, frontend_dev_dependencies={}, backend_dependencies=(),
        backend_routes=(), frontend_routes=(), navigation=(), configuration=configuration,
        migrations=(), manifest_path=Path(name) / "module.json",
    )


def test_dependency_and_configuration_conflicts_are_rejected() -> None:
    one = fake_manifest("one", frontend={"example": "^1"}, configuration=({"name": "VALUE", "default": "one"},))
    two = fake_manifest("two", frontend={"example": "^2"}, configuration=({"name": "VALUE", "default": "two"},))
    with pytest.raises(GenerationError, match="Conflicting frontend_dependencies"):
        _merge_dependency_maps([one, two], "frontend_dependencies")
    with pytest.raises(GenerationError, match="Conflicting configuration"):
        _merge_configuration([one, two])


def test_failed_creation_leaves_no_partial_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("generation failed")
    monkeypatch.setattr(generator, "_materialize_project", fail)
    with pytest.raises(RuntimeError, match="generation failed"):
        create_project("demo", working_directory=tmp_path)
    assert not (tmp_path / "demo").exists()
    assert not list(tmp_path.glob(".demo.buildkit-*"))


def test_create_cli_reports_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["create", "demo", "--modules", "charts"]) == 0
    output = capsys.readouterr().out
    assert "Created project:" in output
    assert "Selected modules: charts" in output
    assert "Automatically included: config, logging, fastapi, frontend" in output
