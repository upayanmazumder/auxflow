"""Completion scripts are exercised in the real shells, not just generated.

bash and fish are asked for completions the way an interactive session asks. zsh is
checked for syntax and registration. A shell that is not installed skips its tests.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import pytest

from auxflow import cli, completion

_BASH = shutil.which("bash")
_ZSH = shutil.which("zsh")
_FISH = shutil.which("fish")

_BASH_DRIVER = r"""
source "$1"; shift
COMP_WORDS=("$@"); COMP_CWORD=$(($# - 1)); _auxflow
printf '%s\n' "${COMPREPLY[@]}"
"""


def _script(shell: str, tmp_path: Path) -> Path:
    path = tmp_path / f"auxflow.{shell}"
    path.write_text(completion.generate(cli.build_parser(), shell), encoding="utf-8")
    return path


def _bash_complete(script: Path, line: str | list[str], cwd: Path) -> set[str]:
    words = line.split(" ") if isinstance(line, str) else line
    result = subprocess.run(
        ["bash", "--norc", "-c", _BASH_DRIVER, "_", str(script), *words],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return {item for item in result.stdout.splitlines() if item}


def _fish_complete(script: Path, line: str, cwd: Path) -> set[str]:
    result = subprocess.run(
        ["fish", "--no-config", "-c", "source $argv[1]; complete -C $argv[2]", str(script), line],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return {item.split("\t")[0] for item in result.stdout.splitlines() if item}


_CASES = [
    ("auxflow cla", {"classify"}),
    ("auxflow --color ", {"auto", "always", "never"}),
    ("auxflow --color always cl", {"classify"}),
    ("auxflow help c", {"check", "classify", "completion"}),
    ("auxflow completion ", {"bash", "zsh", "fish"}),
    ("auxflow plan --e", {"--explain"}),
]


@pytest.mark.skipif(_BASH is None, reason="bash is not installed")
@pytest.mark.parametrize(("line", "expected"), _CASES)
def test_bash_completes_like_an_interactive_session(
    line: str, expected: set[str], tmp_path: Path
) -> None:
    assert _bash_complete(_script("bash", tmp_path), line, tmp_path) == expected


@pytest.mark.skipif(_BASH is None, reason="bash is not installed")
@pytest.mark.parametrize(
    ("words", "expected"),
    [
        (["auxflow", "--color", "=", "never", "cl"], {"classify"}),
        (["auxflow", "--color", "=", ""], {"auto", "always", "never"}),
        (["auxflow", "--color", "=", "al"], {"always"}),
    ],
)
def test_bash_handles_equals_form_that_readline_splits_into_words(
    words: list[str], expected: set[str], tmp_path: Path
) -> None:
    assert _bash_complete(_script("bash", tmp_path), words, tmp_path) == expected


@pytest.mark.skipif(_FISH is None, reason="fish is not installed")
@pytest.mark.parametrize(("line", "expected"), _CASES)
def test_fish_completes_like_an_interactive_session(
    line: str, expected: set[str], tmp_path: Path
) -> None:
    assert _fish_complete(_script("fish", tmp_path), line, tmp_path) == expected


@pytest.mark.skipif(_FISH is None, reason="fish is not installed")
def test_fish_handles_the_equals_form_of_a_global_option(tmp_path: Path) -> None:
    found = _fish_complete(_script("fish", tmp_path), "auxflow --color=never cl", tmp_path)

    assert found == {"classify"}


@pytest.mark.skipif(_BASH is None, reason="bash is not installed")
def test_bash_offers_every_command_and_only_command_options(tmp_path: Path) -> None:
    script = _script("bash", tmp_path)

    commands = _bash_complete(script, "auxflow ", tmp_path)
    options = _bash_complete(script, "auxflow classify -", tmp_path)

    assert commands == set(cli.COMMANDS) | {"help", "completion", "info", "update"}
    assert {"--verbose", "--force", "-v"} <= options
    assert "--color" not in options
    assert "--strict" not in options


@pytest.mark.skipif(_FISH is None, reason="fish is not installed")
def test_fish_scopes_global_options_before_the_subcommand(tmp_path: Path) -> None:
    script = _script("fish", tmp_path)

    assert "--color" in _fish_complete(script, "auxflow -", tmp_path)
    assert "--color" not in _fish_complete(script, "auxflow classify -", tmp_path)


@pytest.mark.skipif(_BASH is None, reason="bash is not installed")
def test_bash_completes_file_names_for_the_file_argument(tmp_path: Path) -> None:
    (tmp_path / "thesis.tex").write_text("x", encoding="utf-8")

    found = _bash_complete(_script("bash", tmp_path), "auxflow check the", tmp_path)

    assert found == {"thesis.tex"}


@pytest.mark.skipif(_FISH is None, reason="fish is not installed")
def test_fish_completes_file_names_for_the_file_argument(tmp_path: Path) -> None:
    (tmp_path / "thesis.tex").write_text("x", encoding="utf-8")

    found = _fish_complete(_script("fish", tmp_path), "auxflow check the", tmp_path)

    assert found == {"thesis.tex"}


@pytest.mark.skipif(_BASH is None, reason="bash is not installed")
def test_bash_gives_no_second_word_after_help_topic(tmp_path: Path) -> None:
    assert _bash_complete(_script("bash", tmp_path), "auxflow help check ", tmp_path) == set()


@pytest.mark.skipif(_ZSH is None, reason="zsh is not installed")
def test_zsh_script_parses_and_registers_for_auxflow(tmp_path: Path) -> None:
    script = _script("zsh", tmp_path)

    subprocess.run(["zsh", "-n", str(script)], check=True)
    registered = subprocess.run(
        [
            "zsh",
            "-f",
            "-c",
            "autoload -Uz compinit; compinit -u -d $1.dump; source $1; "
            "print -r -- $_comps[auxflow]",
            "_",
            str(script),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert registered.stdout.strip() == "_auxflow"


def _every_flag(parser: argparse.ArgumentParser) -> set[str]:
    flags = {flag for action in parser._actions for flag in action.option_strings}
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for sub in action.choices.values():
                flags |= {flag for item in sub._actions for flag in item.option_strings}
    return flags


@pytest.mark.parametrize("shell", completion.SHELLS)
def test_scripts_cover_every_command_and_option_in_the_parser(shell: str) -> None:
    parser = cli.build_parser()
    script = completion.generate(parser, shell)

    for name in (*cli.COMMANDS, "help", "completion", "info"):
        assert name in script
    for flag in _every_flag(parser):
        assert flag.lstrip("-") in script


@pytest.mark.parametrize("shell", completion.SHELLS)
def test_command_prints_the_script_and_never_colours_it(
    shell: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["--color", "always", "completion", shell]) == 0
    out = capsys.readouterr().out

    assert out == completion.generate(cli.build_parser(), shell)
    assert "\033[" not in out


def test_unknown_shell_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["completion", "powershell"])

    assert excinfo.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_completion_needs_no_input_file(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["completion", "bash"]) == 0
    assert "file" not in capsys.readouterr().err
