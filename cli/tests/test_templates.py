from pathlib import Path

from buildkit_cli.registry import load_registry


def test_all_declared_template_sources_exist() -> None:
    registry = load_registry()
    for manifest in registry.values():
        module_root = manifest.manifest_path.parent
        for template_file in manifest.files:
            assert (module_root / template_file.source).is_file()


def test_generator_owned_integration_templates_exist() -> None:
    templates_root = Path(__file__).resolve().parents[2] / "templates" / "integrations"
    assert (templates_root / "frontend_module_routes.tsx.tpl").is_file()
    assert (templates_root / "frontend_module_navigation.ts.tpl").is_file()
    assert (templates_root / "backend_module_routes.py.tpl").is_file()
