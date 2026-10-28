r"""Auxiliary records compare by canonical content, not raw byte order."""

from __future__ import annotations

import pytest

from auxflow.runtime.normalize import normalize_aux_file, normalize_state


def test_reordered_and_reformatted_aux_files_have_equal_canonical_state() -> None:
    first = {
        "main.aux": (
            "\\relax\n"
            "\\newlabel{sec:x}{{1}{ 3 }{First}{section.1}{}}% metadata\n"
            "\\@writefile{toc}{\\contentsline {section}{\\numberline {1}First}{3}{section.1}}\n"
        ),
        "main.bbl": "\n".join(
            (
                r"\begin{thebibliography}{1}",
                r"\bibitem{k} Doe. Title.",
                r"\end{thebibliography}",
                "",
            )
        ),
    }
    second = {
        "main.bbl": "\n".join(
            (
                r"\begin {thebibliography} {1}",
                r"\bibitem {k}   Doe.  Title.",
                r"\end{thebibliography}",
                "",
            )
        ),
        "main.aux": (
            " % ignored comment\n"
            "\\@writefile {toc} {\\contentsline{section}{\\numberline{1} First}{3}{section.1}}\n"
            "\\newlabel {sec:x} {{ 1 }{3}{First}{section.1}{}}\n"
        ),
    }

    assert normalize_state(first) == normalize_state(second)
    assert ("label", "sec:x", "1", "3") in normalize_state(first)
    assert ("toc", "section", r"\numberline{1}First", "3") in normalize_state(first)
    assert ("bib", "k", "Doe. Title.") in normalize_state(first)


def test_direct_generated_lists_and_formatted_bibliography_items() -> None:
    state = normalize_state(
        {
            "main.toc": r"\contentsline {chapter}{Preface}{i}{chapter*.1}",
            "main.lof": r"\contentsline {figure}{\numberline {2}A chart}{4}{figure.2}",
            "main.lot": r"\contentsline {table}{\numberline {1}A table}{5}{table.1}",
            "main.bbl": r"\bibitem[Doe 2024]{doe} Doe. A paper.",
        }
    )

    assert ("toc", "chapter", "Preface", "i") in state
    assert ("lof", "figure", r"\numberline{2}A chart", "4") in state
    assert ("lot", "table", r"\numberline{1}A table", "5") in state
    assert ("bib", "doe", "Doe 2024 Doe. A paper.") in state


def test_excluded_relax_drops_but_unknown_dynamic_state_remains_observable() -> None:
    empty = normalize_aux_file("", ".aux")
    assert normalize_aux_file("\\relax % boilerplate\n", ".aux") == empty

    one = normalize_aux_file(r"\gdef\@abspage@last{1}", ".aux")
    two = normalize_aux_file(r"\gdef\@abspage@last{2}", ".aux")
    assert one != two
    assert ("other", "@abspage@last", "{1}") in one


def test_malformed_recognised_record_is_rejected_instead_of_appearing_stable() -> None:
    with pytest.raises(ValueError, match="unterminated"):
        normalize_aux_file(r"\newlabel{x}{{1}{2}", ".aux")


def test_escaped_percent_does_not_start_a_comment() -> None:
    state = normalize_aux_file(r"\newlabel{x}{{A\%B}{2}}", ".aux")
    assert ("label", "x", r"A\%B", "2") in state


def test_package_defined_scalar_label_remains_observable() -> None:
    first = normalize_aux_file(r"\newlabel{RF1}{12}", ".aux")
    second = normalize_aux_file(r"\newlabel{RF1}{13}", ".aux")

    assert ("other", "newlabel", "RF1", "12") in first
    assert first != second


def test_braced_closing_bracket_in_bibliography_label_is_not_the_option_end() -> None:
    state = normalize_aux_file(r"\bibitem[{A ] B} 2024]{key} Body.", ".bbl")

    assert ("bib", "key", "{A ] B}2024 Body.") in state
