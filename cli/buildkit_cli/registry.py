from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from pathlib import Path

from buildkit_cli.manifest import ManifestError, ModuleManifest
from buildkit_cli.resolver import ResolutionError, resolve_modules


class RegistryError(ValueError):
    """Raised when the internal BuildKit module registry is invalid."""


class ModuleRegistry(Mapping[str, ModuleManifest]):
    def __init__(self, manifests: dict[str, ModuleManifest], modules_root: Path) -> None:
        self._manifests = manifests
        self.modules_root = modules_root

    def __getitem__(self, name: str) -> ModuleManifest:
        try:
            return self._manifests[name]
        except KeyError as exc:
            raise RegistryError(f"Unknown module: {name}") from exc

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._manifests))

    def __len__(self) -> int:
        return len(self._manifests)

    def resolve(self, requested: list[str]) -> tuple[str, ...]:
        try:
            return resolve_modules(self._manifests, requested)
        except ResolutionError as exc:
            raise RegistryError(str(exc)) from exc


def default_modules_root() -> Path:
    return Path(__file__).resolve().parents[2] / "templates" / "modules"


def load_registry(modules_root: Path | None = None) -> ModuleRegistry:
    root = modules_root or default_modules_root()
    if not root.is_dir():
        raise RegistryError(f"Module template directory does not exist: {root}")

    manifests: dict[str, ModuleManifest] = {}
    for manifest_path in sorted(root.glob("*/module.json")):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest = ModuleManifest.from_dict(data, manifest_path)
        except (OSError, json.JSONDecodeError, ManifestError) as exc:
            raise RegistryError(str(exc)) from exc
        if manifest.name in manifests:
            raise RegistryError(f"Duplicate module name: {manifest.name}")
        manifests[manifest.name] = manifest

    if not manifests:
        raise RegistryError(f"No module manifests found in: {root}")

    for manifest in manifests.values():
        missing = sorted(set(manifest.requires) - manifests.keys())
        if missing:
            raise RegistryError(
                f"Module '{manifest.name}' requires missing module(s): {', '.join(missing)}"
            )

        module_root = manifest.manifest_path.parent
        for template_file in manifest.files:
            source = module_root / template_file.source
            if not source.is_file():
                raise RegistryError(f"Template source does not exist: {source}")

    owners: dict[str, str] = {}
    for manifest in manifests.values():
        for template_file in manifest.files:
            previous = owners.get(template_file.destination)
            if previous is not None:
                raise RegistryError(
                    f"Destination '{template_file.destination}' is owned by both "
                    f"'{previous}' and '{manifest.name}'"
                )
            owners[template_file.destination] = manifest.name

    try:
        resolve_modules(manifests, manifests)
    except ResolutionError as exc:
        raise RegistryError(str(exc)) from exc

    return ModuleRegistry(manifests, root)
