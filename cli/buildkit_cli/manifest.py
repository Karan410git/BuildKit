from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    """Raised when a module manifest is invalid."""


@dataclass(frozen=True)
class TemplateFile:
    source: str
    destination: str


@dataclass(frozen=True)
class ModuleManifest:
    schema_version: int
    name: str
    description: str
    selectable: bool
    requires: tuple[str, ...]
    files: tuple[TemplateFile, ...]
    frontend_dependencies: dict[str, str]
    frontend_dev_dependencies: dict[str, str]
    backend_dependencies: tuple[str, ...]
    backend_routes: tuple[dict[str, str], ...]
    frontend_routes: tuple[dict[str, str], ...]
    navigation: tuple[dict[str, str], ...]
    configuration: tuple[dict[str, str], ...]
    migrations: tuple[str, ...]
    manifest_path: Path

    @classmethod
    def from_dict(cls, data: Any, manifest_path: Path) -> ModuleManifest:
        if not isinstance(data, dict):
            raise ManifestError(f"{manifest_path}: manifest must be a JSON object")

        expected = {
            "schema_version", "name", "description", "selectable", "requires", "files",
            "frontend_dependencies", "frontend_dev_dependencies", "backend_dependencies",
            "backend_routes", "frontend_routes", "navigation", "configuration", "migrations",
        }
        missing = expected - data.keys()
        extra = data.keys() - expected
        if missing:
            raise ManifestError(f"{manifest_path}: missing fields: {', '.join(sorted(missing))}")
        if extra:
            raise ManifestError(f"{manifest_path}: unknown fields: {', '.join(sorted(extra))}")
        if data["schema_version"] != 1:
            raise ManifestError(f"{manifest_path}: schema_version must be 1")
        if not isinstance(data["name"], str) or not data["name"]:
            raise ManifestError(f"{manifest_path}: name must be a non-empty string")
        if not isinstance(data["description"], str) or not data["description"]:
            raise ManifestError(f"{manifest_path}: description must be a non-empty string")
        if not isinstance(data["selectable"], bool):
            raise ManifestError(f"{manifest_path}: selectable must be a boolean")

        requires = _string_list(data["requires"], "requires", manifest_path)
        backend_dependencies = _string_list(
            data["backend_dependencies"], "backend_dependencies", manifest_path
        )
        migrations = _string_list(data["migrations"], "migrations", manifest_path)
        files = _template_files(data["files"], manifest_path)

        return cls(
            schema_version=1,
            name=data["name"],
            description=data["description"],
            selectable=data["selectable"],
            requires=requires,
            files=files,
            frontend_dependencies=_string_map(
                data["frontend_dependencies"], "frontend_dependencies", manifest_path
            ),
            frontend_dev_dependencies=_string_map(
                data["frontend_dev_dependencies"], "frontend_dev_dependencies", manifest_path
            ),
            backend_dependencies=backend_dependencies,
            backend_routes=_record_list(data["backend_routes"], "backend_routes", manifest_path),
            frontend_routes=_record_list(data["frontend_routes"], "frontend_routes", manifest_path),
            navigation=_record_list(data["navigation"], "navigation", manifest_path),
            configuration=_record_list(data["configuration"], "configuration", manifest_path),
            migrations=migrations,
            manifest_path=manifest_path,
        )


def _string_list(value: Any, field: str, path: Path) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ManifestError(f"{path}: {field} must be a list of non-empty strings")
    return tuple(value)


def _string_map(value: Any, field: str, path: Path) -> dict[str, str]:
    if not isinstance(value, dict) or any(
        not isinstance(key, str) or not key or not isinstance(item, str) or not item
        for key, item in value.items()
    ):
        raise ManifestError(f"{path}: {field} must map non-empty strings to non-empty strings")
    return dict(value)


def _record_list(value: Any, field: str, path: Path) -> tuple[dict[str, str], ...]:
    if not isinstance(value, list):
        raise ManifestError(f"{path}: {field} must be a list")
    records: list[dict[str, str]] = []
    for record in value:
        if not isinstance(record, dict) or not record or any(
            not isinstance(key, str) or not key or not isinstance(item, str) or not item
            for key, item in record.items()
        ):
            raise ManifestError(f"{path}: {field} entries must be non-empty string maps")
        records.append(dict(record))
    return tuple(records)


def _template_files(value: Any, path: Path) -> tuple[TemplateFile, ...]:
    if not isinstance(value, list):
        raise ManifestError(f"{path}: files must be a list")
    files: list[TemplateFile] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {"source", "destination"}:
            raise ManifestError(f"{path}: each file must contain source and destination")
        if any(not isinstance(item[key], str) or not item[key] for key in item):
            raise ManifestError(f"{path}: file paths must be non-empty strings")
        files.append(TemplateFile(item["source"], item["destination"]))
    return tuple(files)
