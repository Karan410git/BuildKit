from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from buildkit_cli import __version__
from buildkit_cli.manifest import ModuleManifest
from buildkit_cli.registry import ModuleRegistry, RegistryError, load_registry

DEFAULT_MODULES = ("frontend", "fastapi")
PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class GenerationError(ValueError):
    """Raised for controlled project-generation failures."""


@dataclass(frozen=True)
class CreationResult:
    project_path: Path
    selected_modules: tuple[str, ...]
    installed_modules: tuple[str, ...]


def create_project(
    project_name: str,
    selected_modules: list[str] | None = None,
    *,
    working_directory: Path | None = None,
    registry: ModuleRegistry | None = None,
) -> CreationResult:
    base_directory = (working_directory or Path.cwd()).resolve()
    _validate_project_name(project_name)
    destination = (base_directory / project_name).resolve()
    if destination.parent != base_directory:
        raise GenerationError("Project destination must remain inside the current directory")
    if destination.exists():
        raise GenerationError(f"Destination already exists: {destination}")

    module_registry = registry or load_registry()
    selected = tuple(sorted(set(selected_modules or [])))
    for name in selected:
        try:
            manifest = module_registry[name]
        except RegistryError as exc:
            raise GenerationError(str(exc)) from exc
        if not manifest.selectable:
            raise GenerationError(f"Module '{name}' is a foundation module and cannot be selected explicitly")

    try:
        default_resolved = module_registry.resolve(list(DEFAULT_MODULES))
        selected_resolved = module_registry.resolve(list(selected)) if selected else ()
        installed = tuple(dict.fromkeys((*default_resolved, *selected_resolved)))
    except RegistryError as exc:
        raise GenerationError(str(exc)) from exc

    _preflight(module_registry, installed)
    temporary = Path(tempfile.mkdtemp(prefix=f".{project_name}.buildkit-", dir=base_directory))
    try:
        _materialize_project(temporary, project_name, selected, installed, module_registry)
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    return CreationResult(destination, selected, installed)


def _validate_project_name(project_name: str) -> None:
    if not PROJECT_NAME_PATTERN.fullmatch(project_name) or project_name in {".", ".."}:
        raise GenerationError(
            "Project name must start with a letter or number and contain only letters, "
            "numbers, dots, hyphens, or underscores"
        )


def _preflight(registry: ModuleRegistry, installed: tuple[str, ...]) -> None:
    manifests = [registry[name] for name in installed]
    _merge_dependency_maps(manifests, "frontend_dependencies")
    _merge_dependency_maps(manifests, "frontend_dev_dependencies")
    _merge_backend_dependencies(manifests)
    _merge_configuration(manifests)


def _merge_dependency_maps(
    manifests: list[ModuleManifest], field: str
) -> dict[str, str]:
    merged: dict[str, str] = {}
    for manifest in manifests:
        for name, version in getattr(manifest, field).items():
            if name in merged and merged[name] != version:
                raise GenerationError(
                    f"Conflicting {field} declaration for '{name}': "
                    f"'{merged[name]}' and '{version}'"
                )
            merged[name] = version
    return dict(sorted(merged.items()))


def _requirement_name(requirement: str) -> str:
    match = re.match(r"^([A-Za-z0-9_.-]+)", requirement)
    if not match:
        raise GenerationError(f"Invalid backend dependency: {requirement}")
    return match.group(1).lower().replace("_", "-")


def _merge_backend_dependencies(manifests: list[ModuleManifest]) -> tuple[str, ...]:
    merged: dict[str, str] = {}
    for manifest in manifests:
        for requirement in manifest.backend_dependencies:
            name = _requirement_name(requirement)
            if name in merged and merged[name] != requirement:
                raise GenerationError(
                    f"Conflicting backend dependency declaration for '{name}': "
                    f"'{merged[name]}' and '{requirement}'"
                )
            merged[name] = requirement
    return tuple(merged[name] for name in sorted(merged))


def _merge_configuration(
    manifests: list[ModuleManifest],
) -> dict[str, tuple[str, str]]:
    merged: dict[str, tuple[str, str]] = {}
    for manifest in manifests:
        for item in manifest.configuration:
            name, default = item["name"], item["default"]
            if name in merged and merged[name][0] != default:
                raise GenerationError(
                    f"Conflicting configuration definition for '{name}': "
                    f"'{merged[name][0]}' and '{default}'"
                )
            merged[name] = (default, manifest.name)
    return dict(sorted(merged.items()))


def _materialize_project(
    root: Path,
    project_name: str,
    selected: tuple[str, ...],
    installed: tuple[str, ...],
    registry: ModuleRegistry,
) -> None:
    owners: dict[str, str] = {}
    manifests = [registry[name] for name in installed]
    for manifest in manifests:
        module_root = manifest.manifest_path.parent
        for template_file in manifest.files:
            destination = root / template_file.destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(module_root / template_file.source, destination)
            owners[template_file.destination.replace("\\", "/")] = manifest.name

    configuration = _merge_configuration(manifests)
    _render_configuration(root, configuration)
    _render_dependencies(root, manifests)
    _render_integrations(root, manifests, registry.modules_root.parent / "integrations")

    generated_paths = {
        ".env.example", "backend/app/core/config.py", "backend/requirements.txt",
        "frontend/package.json", "frontend/src/app/moduleRoutes.tsx",
        "frontend/src/app/moduleNavigation.ts", "backend/app/module_routes.py",
    }
    for path in generated_paths:
        if (root / path).is_file():
            owners[path] = "generator"

    files: dict[str, dict[str, str]] = {}
    for relative_path, owner in sorted(owners.items()):
        content = (root / relative_path).read_bytes()
        files[relative_path] = {"owner": owner, "sha256": hashlib.sha256(content).hexdigest()}

    state = {
        "schema_version": 1,
        "buildkit_version": __version__,
        "project_name": project_name,
        "selected_modules": list(selected),
        "installed_modules": list(installed),
        "files": files,
    }
    state_path = root / ".buildkit" / "project.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _render_dependencies(root: Path, manifests: list[ModuleManifest]) -> None:
    package_path = root / "frontend" / "package.json"
    package: dict[str, Any] = json.loads(package_path.read_text(encoding="utf-8"))
    package["dependencies"] = _merge_dependency_maps(manifests, "frontend_dependencies")
    package["devDependencies"] = _merge_dependency_maps(manifests, "frontend_dev_dependencies")
    package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

    requirements = _merge_backend_dependencies(manifests)
    requirements_path = root / "backend" / "requirements.txt"
    requirements_path.parent.mkdir(parents=True, exist_ok=True)
    requirements_path.write_text("\n".join(requirements) + "\n", encoding="utf-8")


def _python_setting(name: str, default: str) -> str:
    field = name.lower()
    if default.lower() in {"true", "false"}:
        return f"    {field}: bool = {default.title()}"
    if default.isdigit():
        return f"    {field}: int = {default}"
    if default.startswith("[") and default.endswith("]"):
        values = [item.strip() for item in default[1:-1].split(",") if item.strip()]
        return f"    {field}: list[str] = {values!r}"
    return f"    {field}: str = {default!r}"


def _render_configuration(root: Path, configuration: dict[str, tuple[str, str]]) -> None:
    base_names = {"APP_NAME", "ENVIRONMENT", "DEBUG", "LOG_LEVEL"}
    additions = [
        _python_setting(name, default)
        for name, (default, _) in configuration.items()
        if name not in base_names and not name.startswith("VITE_") and not name.startswith("POSTGRES_")
    ]
    config_path = root / "backend" / "app" / "core" / "config.py"
    config_text = config_path.read_text(encoding="utf-8").replace(
        "__BUILDKIT_CONFIGURATION__", "\n" + "\n".join(additions) if additions else ""
    )
    config_path.write_text(config_text, encoding="utf-8")

    env_path = root / ".env.example"
    env_lines: list[str] = []
    for name, (default, owner) in configuration.items():
        if name in base_names:
            continue
        if name == "JWT_SECRET_KEY":
            env_lines.append("# Development/example value only; replace outside local development.")
        env_lines.append(f"{name}={default}")
    env_text = env_path.read_text(encoding="utf-8").replace(
        "__BUILDKIT_ENVIRONMENT__", "\n".join(env_lines)
    )
    env_path.write_text(env_text.rstrip() + "\n", encoding="utf-8")


def _render_integrations(root: Path, manifests: list[ModuleManifest], integrations: Path) -> None:
    backend_imports: list[str] = []
    backend_register: list[str] = []
    frontend_imports: list[str] = []
    frontend_routes: list[str] = []
    navigation: list[str] = []

    for manifest in manifests:
        for route in manifest.backend_routes:
            alias = f"{manifest.name}_router"
            backend_imports.append(f"from {route['module']} import {route['router']} as {alias}")
            backend_register.append(f"    app.include_router({alias})")
        for route in manifest.frontend_routes:
            frontend_imports.append(f"import {route['component']} from \"{route['import']}\";")
            frontend_routes.append(
                f"  {{ path: {json.dumps(route['path'])}, element: <{route['component']} /> }},"
            )
        for item in manifest.navigation:
            navigation.append(
                f"  {{ label: {json.dumps(item['label'])}, to: {json.dumps(item['to'])} }},"
            )

    backend_template = (integrations / "backend_module_routes.py.tpl").read_text(encoding="utf-8")
    backend_text = backend_template.replace("__BUILDKIT_IMPORTS__", "\n".join(backend_imports))
    backend_text = backend_text.replace(
        "__BUILDKIT_ROUTE_REGISTRATION__", "\n".join(backend_register) or "    pass"
    )
    _write(root / "backend/app/module_routes.py", backend_text)

    routes_template = (integrations / "frontend_module_routes.tsx.tpl").read_text(encoding="utf-8")
    routes_text = routes_template.replace("__BUILDKIT_IMPORTS__", "\n".join(frontend_imports))
    routes_text = routes_text.replace("__BUILDKIT_ROUTES__", "\n".join(frontend_routes))
    _write(root / "frontend/src/app/moduleRoutes.tsx", routes_text)

    navigation_template = (integrations / "frontend_module_navigation.ts.tpl").read_text(encoding="utf-8")
    navigation_text = navigation_template.replace("__BUILDKIT_NAVIGATION__", "\n".join(navigation))
    _write(root / "frontend/src/app/moduleNavigation.ts", navigation_text)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
