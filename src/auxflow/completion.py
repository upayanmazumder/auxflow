"""Shell completion scripts generated from the argparse parser.

The scripts are built by reading the parser, so a new command or option is
completed without editing this module. Completions are static: they list
commands, options, and fixed choices, and fall back to file completion for FILE.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

SHELLS = ("bash", "zsh", "fish")


@dataclass(frozen=True)
class _Option:
    flags: tuple[str, ...]
    help: str
    choices: tuple[str, ...]
    takes_value: bool


@dataclass(frozen=True)
class _Command:
    name: str
    help: str
    options: tuple[_Option, ...]
    takes_file: bool
    words: tuple[str, ...]
    """Fixed words accepted as the first positional argument, if any."""


def _options(parser: argparse.ArgumentParser) -> tuple[_Option, ...]:
    return tuple(
        _Option(
            flags=tuple(action.option_strings),
            help=(action.help or "").replace("%(prog)s", "auxflow"),
            choices=tuple(str(choice) for choice in (action.choices or ())),
            takes_value=action.nargs != 0,
        )
        for action in parser._actions
        if action.option_strings
    )


def _introspect(
    parser: argparse.ArgumentParser,
) -> tuple[tuple[_Option, ...], tuple[_Command, ...]]:
    commands: list[_Command] = []
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        summaries = {item.dest: item.help or "" for item in action._choices_actions}
        for name, sub in action.choices.items():
            positionals = [item for item in sub._actions if not item.option_strings]
            words = next(
                (tuple(str(c) for c in item.choices) for item in positionals if item.choices), ()
            )
            if name == "help":
                words = tuple(action.choices)
            takes_file = any(item.dest == "file" for item in positionals)
            commands.append(
                _Command(name, summaries.get(name, ""), _options(sub), takes_file, words)
            )
    return _options(parser), tuple(commands)


def _flags(options: tuple[_Option, ...]) -> str:
    return " ".join(flag for option in options for flag in option.flags)


def _quote(text: str) -> str:
    return "'" + text.replace("'", "'\\''") + "'"


def _bash(options: tuple[_Option, ...], commands: tuple[_Command, ...]) -> str:
    names = " ".join(command.name for command in commands)
    value_lines: dict[str, None] = {}
    for option in (*options, *(o for c in commands for o in c.options)):
        if not option.takes_value:
            continue
        pattern = "|".join(option.flags)
        if option.choices:
            words = " ".join(option.choices)
            reply = f'COMPREPLY=($(compgen -W "{words}" -- "$cur"))'
        else:
            reply = 'compopt -o filenames 2>/dev/null; COMPREPLY=($(compgen -f -- "$cur"))'
        value_lines[f"        {pattern}) {reply}; return ;;"] = None
    value_block = "\n".join(value_lines)
    global_value = "|".join(f for o in options if o.takes_value for f in o.flags) or "__none__"
    case_block = "\n".join(
        f'        {c.name}) opts="{_flags(c.options)}"; '
        f'file={"1" if c.takes_file else "0"}; words="{" ".join(c.words)}" ;;'
        for c in commands
    )
    return f"""# bash completion for auxflow. Load with: eval "$(auxflow completion bash)"
_auxflow() {{
    local cur prev cmd opts file words i cmd_index=0
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    # bash splits --opt=value into three words: --opt, =, value.
    if [[ "$prev" == "=" && $COMP_CWORD -ge 2 ]]; then
        prev="${{COMP_WORDS[COMP_CWORD-2]}}"
    fi
    cmd=""
    for ((i = 1; i < COMP_CWORD; i++)); do
        case "${{COMP_WORDS[i]}}" in
            {global_value})
                i=$((i + 1))
                if [[ "${{COMP_WORDS[i]}}" == "=" ]]; then i=$((i + 1)); fi ;;
            -*) ;;
            *) cmd="${{COMP_WORDS[i]}}"; cmd_index=$i; break ;;
        esac
    done
    case "$prev" in
{value_block}
    esac
    if [[ -z "$cmd" ]]; then
        if [[ "$cur" == -* ]]; then
            COMPREPLY=($(compgen -W "{_flags(options)}" -- "$cur"))
        else
            COMPREPLY=($(compgen -W "{names}" -- "$cur"))
        fi
        return
    fi
    opts=""; file=0; words=""
    case "$cmd" in
{case_block}
    esac
    if [[ "$cur" == -* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
    elif [[ "$file" == 1 ]]; then
        compopt -o filenames 2>/dev/null
        COMPREPLY=($(compgen -f -- "$cur"))
    elif [[ -n "$words" && $((COMP_CWORD - cmd_index)) -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$words" -- "$cur"))
    fi
}}
complete -F _auxflow auxflow
"""


def _zsh_text(text: str) -> str:
    """Escape text for a `[description]` inside a single-quoted _arguments spec."""
    escaped = text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    return escaped.replace(":", "\\:").replace("'", "'\\''")


def _zsh_spec(option: _Option) -> str:
    description = _zsh_text(option.help)
    if len(option.flags) > 1:
        group = " ".join(option.flags)
        head = f"'({group})'{{{','.join(option.flags)}}}'[{description}]"
    else:
        head = f"'{option.flags[0]}[{description}]"
    if option.takes_value:
        head += f":value:({' '.join(option.choices)})" if option.choices else ":path:_files"
    return head + "'"


def _zsh(options: tuple[_Option, ...], commands: tuple[_Command, ...]) -> str:
    colon = "\\:"
    listing = "\n".join(
        f"        {_quote(c.name + ':' + c.help.replace(':', colon))}" for c in commands
    )
    global_specs = " \\\n        ".join(_zsh_spec(option) for option in options)
    branches = []
    for command in commands:
        specs = [_zsh_spec(option) for option in command.options]
        if command.takes_file:
            specs.append("'1:file:_files -g \"*.tex\"'")
        elif command.words:
            specs.append(f"'1:command:({' '.join(command.words)})'")
        body = " \\\n                    ".join(specs)
        branches.append(
            f"            {command.name})\n"
            f"                _arguments \\\n                    {body} ;;"
        )
    branch_block = "\n".join(branches)
    return f"""#compdef auxflow
# zsh completion for auxflow. Load with: eval "$(auxflow completion zsh)"
_auxflow() {{
    local curcontext="$curcontext" state line
    typeset -A opt_args
    local -a commands
    commands=(
{listing}
    )
    _arguments -C \\
        {global_specs} \\
        '1: :->command' \\
        '*:: :->args'
    case $state in
        command) _describe -t commands 'auxflow command' commands ;;
        args)
            case $words[1] in
{branch_block}
            esac ;;
    esac
}}
if [ "$funcstack[1]" = "_auxflow" ]; then
    _auxflow "$@"
else
    compdef _auxflow auxflow
fi
"""


def _fish_flags(option: _Option) -> str:
    return " ".join(
        f"-l {flag[2:]}" if flag.startswith("--") else f"-s {flag[1:]}" for flag in option.flags
    )


def _fish_option(condition: str, option: _Option) -> str:
    extra = ""
    if option.takes_value:
        extra = f" -x -a {_quote(' '.join(option.choices))}" if option.choices else " -r -F"
    return f"complete -c auxflow{condition} {_fish_flags(option)}{extra} -d {_quote(option.help)}"


_FISH_NEEDS_COMMAND = """function __auxflow_needs_command
    set -l tokens (commandline -opc)
    set -e tokens[1]
    while set -q tokens[1]
        switch $tokens[1]
            case --color
                set -e tokens[1]
            case '-*'
            case '*'
                return 1
        end
        set -e tokens[1]
    end
    return 0
end"""


def _fish(options: tuple[_Option, ...], commands: tuple[_Command, ...]) -> str:
    # Global options are only valid before the subcommand, so scope them there.
    first = " -n __auxflow_needs_command"
    lines = ["# fish completion for auxflow. Load with: auxflow completion fish | source", ""]
    lines.extend((_FISH_NEEDS_COMMAND, "complete -c auxflow -f"))
    lines.extend(_fish_option(first, option) for option in options)
    for command in commands:
        lines.append(f"complete -c auxflow{first} -a {command.name} -d {_quote(command.help)}")
    for command in commands:
        condition = f" -n '__fish_seen_subcommand_from {command.name}'"
        lines.extend(_fish_option(condition, option) for option in command.options)
        if command.takes_file:
            lines.append(f"complete -c auxflow{condition} -F")
        elif command.words:
            lines.append(f"complete -c auxflow{condition} -a {_quote(' '.join(command.words))}")
    return "\n".join(lines) + "\n"


def generate(parser: argparse.ArgumentParser, shell: str) -> str:
    """The completion script for `shell`, built from `parser`."""
    if shell not in SHELLS:
        raise ValueError(f"unsupported shell: {shell}")
    options, commands = _introspect(parser)
    if shell == "bash":
        return _bash(options, commands)
    if shell == "zsh":
        return _zsh(options, commands)
    return _fish(options, commands)
