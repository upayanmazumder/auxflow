r"""The argument-signature table: which macros take how many, and what kind
of, arguments.

docs/COMPILER-PIPELINE.md section 2: "`\label{}` takes one mandatory
argument; `\includegraphics[]{}` takes one optional and one mandatory."
Covers every macro in docs/LANGUAGE-SUBSET.md's Required table whose
argument structure is a plain sequence of mandatory/optional groups.
`\forloop`, `\whiledo`, `\newcommand`, `\renewcommand` have condition/body
or name/arity/body structures that do not fit this scheme and are not
listed here; a control sequence with no entry parses as a bare MacroCall
with no arguments, per sub-issue #24's acceptance.

Sectioning (`\chapter`, `\section`, `\subsection`) is handled by
auxflow.parser.recursive directly, not through this table: its title
argument participates in the preamble/body split logic, which a generic
signature-driven MacroCall does not need to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ArgKind = Literal["mandatory", "optional"]


@dataclass(frozen=True)
class Signature:
    args: tuple[ArgKind, ...]


SIGNATURES: dict[str, Signature] = {
    "\\documentclass": Signature(("optional", "mandatory")),
    "\\usepackage": Signature(("optional", "mandatory")),
    "\\input": Signature(("mandatory",)),
    "\\include": Signature(("mandatory",)),
    "\\label": Signature(("mandatory",)),
    "\\ref": Signature(("mandatory",)),
    "\\pageref": Signature(("mandatory",)),
    "\\cite": Signature(("mandatory",)),
    "\\bibliography": Signature(("mandatory",)),
    "\\bibliographystyle": Signature(("mandatory",)),
    "\\caption": Signature(("mandatory",)),
    "\\includegraphics": Signature(("optional", "mandatory")),
    "\\newcounter": Signature(("mandatory",)),
    "\\setcounter": Signature(("mandatory", "mandatory")),
    "\\value": Signature(("mandatory",)),
}
