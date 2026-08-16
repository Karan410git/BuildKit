from __future__ import annotations

import pytest

from buildkit_cli.cli import build_parser, main


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        (["create", "my-project"], {"project_name": "my-project", "modules": None}),
        (
            ["create", "my-project", "--modules", "auth", "charts"],
            {"project_name": "my-project", "modules": ["auth", "charts"]},
        ),
        (["add", "auth"], {"modules": ["auth"]}),
        (["add", "auth", "charts", "maps"], {"modules": ["auth", "charts", "maps"]}),
        (["remove", "maps"], {"modules": ["maps"]}),
        (["remove", "charts", "upload"], {"modules": ["charts", "upload"]}),
        (["modules"], {}),
    ],
)
def test_command_arguments_are_parsed(arguments: list[str], expected: dict[str, object]) -> None:
    args = build_parser().parse_args(arguments)

    for name, value in expected.items():
        assert getattr(args, name) == value


@pytest.mark.parametrize("command", ["create", "add", "remove"])
def test_commands_return_controlled_not_implemented_result(
    command: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    arguments = {
        "create": ["create", "my-project"],
        "add": ["add", "auth"],
        "remove": ["remove", "maps"],
    }[command]

    assert main(arguments) == 1
    assert capsys.readouterr().out == f"The '{command}' command is not implemented yet.\n"


def test_modules_command_uses_registry(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["modules"]) == 0
    output = capsys.readouterr().out
    assert "Selectable feature modules:" in output
    assert "auth" in output
    assert "charts" in output
    assert "maps" in output
    assert "upload" in output
    assert "Foundation modules (automatically required):" in output
    assert "frontend" in output


@pytest.mark.parametrize("arguments", [["create"], ["add"], ["remove"]])
def test_required_arguments_are_enforced(arguments: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        build_parser().parse_args(arguments)

    assert error.value.code == 2
