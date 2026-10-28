r"""Canonical auxiliary-state records for runtime convergence checks.

Parse TeX groups with a brace cursor, not regular expressions. A label or
contents entry can contain nested groups. Unknown commands remain observable
as opaque records rather than silently disappearing from the state.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

CanonicalRecord = tuple[str, ...]
AuxState = frozenset[CanonicalRecord]

_LIST_KIND = {"toc": "toc", "lof": "lof", "lot": "lot"}
_VALID_SUFFIX = frozenset({".aux", ".toc", ".lof", ".lot", ".bbl", ".ind"})
_BIB_END = re.compile(r"\\bibitem(?![A-Za-z@])|\\end\s*\{\s*thebibliography\s*\}")

# One deliberate exclusion. \relax has no arguments or state. The TeX engine
# writes it as boilerplate at the start of .aux files. Do not add other
# exclusions without a reason in docs/RUNTIME-VERIFICATION.md.
EXCLUDED_COMMANDS = frozenset({"relax"})


def _strip_comments(source: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(source):
        if source[index] == "%":
            slash = index - 1
            while slash >= 0 and source[slash] == "\\":
                slash -= 1
            if (index - 1 - slash) % 2 == 0:
                while index < len(source) and source[index] != "\n":
                    index += 1
                continue
        result.append(source[index])
        index += 1
    return "".join(result)


def _canonical(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s*([{}])\s*", r"\1", text)


def _skip_space(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _group(text: str, index: int, opener: str = "{") -> tuple[str, int]:
    index = _skip_space(text, index)
    closer = "}" if opener == "{" else "]"
    if index >= len(text) or text[index] != opener:
        raise ValueError(f"expected {opener!r} at auxiliary offset {index}")
    start = index + 1
    depth = 1
    brace_depth = 0
    index = start
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text) and text[index + 1] in "{}[]":
            index += 2
            continue
        if opener == "[":
            if char == "{":
                brace_depth += 1
            elif char == "}" and brace_depth:
                brace_depth -= 1
            if brace_depth or char == "}":
                index += 1
                continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[start:index], index + 1
        index += 1
    raise ValueError(f"unterminated {opener!r} group at auxiliary offset {start - 1}")


def _command(text: str, index: int) -> tuple[str, int]:
    start = index + 1
    if start == len(text):
        return "", start
    if not (text[start].isalpha() or text[start] == "@"):
        return text[start], start + 1
    end = start + 1
    while end < len(text) and (text[end].isalpha() or text[end] == "@"):
        end += 1
    return text[start:end], end


def _records(text: str, suffix: str) -> set[CanonicalRecord]:
    records: set[CanonicalRecord] = set()
    index = 0
    while index < len(text):
        if text[index] != "\\":
            end = text.find("\\", index)
            if end < 0:
                end = len(text)
            plain = _canonical(text[index:end])
            if plain:
                records.add(("other", "text", plain))
            index = end
            continue
        name, index = _command(text, index)
        if name in EXCLUDED_COMMANDS:
            continue
        if name == "newlabel":
            key, index = _group(text, index)
            details, index = _group(text, index)
            if details.startswith("{", _skip_space(details, 0)):
                number, cursor = _group(details, 0)
                page, _ = _group(details, cursor)
                records.add(("label", _canonical(key), _canonical(number), _canonical(page)))
            else:
                # Packages may reuse \newlabel with a scalar value. Preserve it.
                records.add(("other", "newlabel", _canonical(key), _canonical(details)))
        elif name == "@writefile":
            target, index = _group(text, index)
            content, index = _group(text, index)
            if target in _LIST_KIND:
                records.update(_records(content, f".{target}"))
            else:
                records.add(("other", "@writefile", _canonical(target), _canonical(content)))
        elif name == "contentsline" and suffix[1:] in _LIST_KIND:
            level, index = _group(text, index)
            title, index = _group(text, index)
            page, index = _group(text, index)
            # Hyperref appends a fourth argument. It is not part of the
            # documented canonical contents entry.
            if _skip_space(text, index) < len(text) and text[_skip_space(text, index)] == "{":
                _anchor, index = _group(text, index)
            records.add((suffix[1:], _canonical(level), _canonical(title), _canonical(page)))
        elif name == "bibitem" and suffix == ".bbl":
            label = ""
            if _skip_space(text, index) < len(text) and text[_skip_space(text, index)] == "[":
                label, index = _group(text, index, "[")
            key, index = _group(text, index)
            next_item = _BIB_END.search(text, index)
            end = next_item.start() if next_item else len(text)
            records.add(("bib", _canonical(key), _canonical(f"{label} {text[index:end]}")))
            index = end
        else:
            # Unmodelled records stay observable. Suppressing them could make
            # a changing auxiliary file appear stable to the executor.
            arguments: list[str] = []
            cursor = _skip_space(text, index)
            while cursor < len(text) and text[cursor] in "{[":
                opener = text[cursor]
                arg, cursor = _group(text, cursor, opener)
                closer = "}" if opener == "{" else "]"
                arguments.append(f"{opener}{_canonical(arg)}{closer}")
                cursor = _skip_space(text, cursor)
            records.add(("other", name, *arguments))
            index = cursor
    return records


def normalize_aux_file(source: str, suffix: str) -> AuxState:
    """Read one auxiliary file into order-independent canonical records."""
    if suffix not in _VALID_SUFFIX:
        raise ValueError(f"unsupported auxiliary suffix: {suffix}")
    return frozenset(_records(_strip_comments(source), suffix))


def normalize_state(contents: Mapping[str, str]) -> AuxState:
    """Merge canonical records from all observed auxiliary files."""
    records: set[CanonicalRecord] = set()
    for path, source in contents.items():
        records.update(normalize_aux_file(source, Path(path).suffix))
    return frozenset(records)
