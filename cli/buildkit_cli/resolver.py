from __future__ import annotations

from collections.abc import Iterable, Mapping

from buildkit_cli.manifest import ModuleManifest


class ResolutionError(ValueError):
    """Raised when requested modules cannot be resolved."""


def resolve_modules(
    manifests: Mapping[str, ModuleManifest],
    requested: Iterable[str],
) -> tuple[str, ...]:
    result: list[str] = []
    complete: set[str] = set()
    visiting: list[str] = []

    def visit(name: str) -> None:
        if name not in manifests:
            raise ResolutionError(f"Unknown module: {name}")
        if name in complete:
            return
        if name in visiting:
            cycle = visiting[visiting.index(name):] + [name]
            raise ResolutionError(f"Dependency cycle: {' -> '.join(cycle)}")

        visiting.append(name)
        for requirement in sorted(manifests[name].requires):
            visit(requirement)
        visiting.pop()
        complete.add(name)
        result.append(name)

    for module_name in sorted(set(requested)):
        visit(module_name)
    return tuple(result)
