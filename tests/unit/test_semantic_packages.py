r"""Phase 6 package warning follows PackageTable model status."""

from __future__ import annotations

from pathlib import Path

import pytest

from auxflow.ast import build_forest
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.diagnostics import check_packages
from auxflow.semantic.resolve import declare


def _warnings(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    return check_packages(forest, declare(forest))


def _project_warnings(root: Path):
    file_id = str(root)
    source = root.read_text(encoding="utf-8")
    document = parse(tokenize(source, file_id=file_id), file_id=file_id).document
    forest = build_forest({file_id: document})
    return check_packages(forest, declare(forest))


def test_unmodelled_package_warns_at_usepackage_span() -> None:
    source = "\\usepackage{exotic}"

    warnings = _warnings(source)

    assert len(warnings) == 1
    assert warnings[0].message == "unmodelled package: 'exotic'"
    assert warnings[0].severity == "warning"
    assert warnings[0].span.file_id == "main.tex"
    assert (warnings[0].span.start, warnings[0].span.end) == (0, len(source))


def test_modelled_package_does_not_warn() -> None:
    assert _warnings("\\usepackage{graphicx}") == []


def test_local_class_reports_transitive_requirements_with_provenance(tmp_path: Path) -> None:
    root = tmp_path / "main.tex"
    root.write_text(r"\documentclass[final]{MyClass}", encoding="utf-8")
    class_file = tmp_path / "MyClass.cls"
    class_file.write_text(
        r"\RequirePackage[margin=1in]{geometry,graphicx}"
        "\n"
        r"\RequirePackage{helper}"
        "\n",
        encoding="utf-8",
    )
    style_file = tmp_path / "helper.sty"
    style_file.write_text(r"\RequirePackage[demo]{exotic}", encoding="utf-8")

    warnings = _project_warnings(root)

    assert warnings[0].message == f"unmodelled class: 'MyClass' (local file: '{class_file}')"
    assert warnings[0].span.file_id == str(root)
    assert [(item.message, item.span.file_id) for item in warnings[1:]] == [
        ("unmodelled package: 'geometry' (required by 'MyClass.cls')", str(class_file)),
        ("unmodelled package: 'graphicx' (required by 'MyClass.cls')", str(class_file)),
        ("unmodelled package: 'helper' (required by 'MyClass.cls')", str(class_file)),
        (
            "unmodelled package: 'exotic' (required by 'MyClass.cls' -> 'helper.sty')",
            str(style_file),
        ),
    ]
    assert all(item.severity == "warning" for item in warnings)
    assert warnings[-1].span.start == 0


def test_class_requirements_ignore_comments_but_not_escaped_percent(tmp_path: Path) -> None:
    root = tmp_path / "main.tex"
    root.write_text(r"\documentclass{MyClass}", encoding="utf-8")
    (tmp_path / "MyClass.cls").write_text(
        "% \\RequirePackage{invisible}\n"
        "\\RequirePackage{visible}% \\RequirePackage{hidden}\n"
        "\\% \\RequirePackage{alsoVisible}\n",
        encoding="utf-8",
    )

    warnings = _project_warnings(root)

    assert [item.message.split("'")[1] for item in warnings] == [
        "MyClass",
        "visible",
        "alsoVisible",
    ]


def test_repeated_requirements_and_style_cycle_report_once(tmp_path: Path) -> None:
    root = tmp_path / "main.tex"
    root.write_text(r"\documentclass{MyClass}", encoding="utf-8")
    (tmp_path / "MyClass.cls").write_text(
        "\\RequirePackage{a,b,a}\n\\RequirePackage{b}\n", encoding="utf-8"
    )
    (tmp_path / "a.sty").write_text(r"\RequirePackage{b}", encoding="utf-8")
    (tmp_path / "b.sty").write_text(r"\RequirePackage{a,c}", encoding="utf-8")
    (tmp_path / "c.sty").write_text(r"\RequirePackage{a}", encoding="utf-8")

    warnings = _project_warnings(root)

    assert [item.message.split("'")[1] for item in warnings] == ["MyClass", "a", "b", "c"]


def test_absent_local_class_is_unknown_not_assumed_safe(tmp_path: Path) -> None:
    name = "MissingClass"
    root = tmp_path / "main.tex"
    root.write_text(rf"\documentclass{{{name}}}", encoding="utf-8")

    warnings = _project_warnings(root)

    assert len(warnings) == 1
    assert warnings[0].message == (
        f"unmodelled class: '{name}' (no local .cls file found; external class not inspected)"
    )
    assert warnings[0].severity == "warning"


@pytest.mark.parametrize("name", ["article", "report", "book"])
def test_standard_class_without_local_file_does_not_flood_warnings(
    tmp_path: Path, name: str
) -> None:
    root = tmp_path / "main.tex"
    root.write_text(rf"\documentclass{{{name}}}", encoding="utf-8")

    assert _project_warnings(root) == []


def test_class_inventory_does_not_change_direct_package_warning(tmp_path: Path) -> None:
    root = tmp_path / "main.tex"
    root.write_text(r"\documentclass{MyClass}\usepackage{exotic}", encoding="utf-8")
    (tmp_path / "MyClass.cls").write_text(r"\RequirePackage{graphicx}", encoding="utf-8")

    warnings = _project_warnings(root)

    assert [warning.message for warning in warnings] == [
        f"unmodelled class: 'MyClass' (local file: '{tmp_path / 'MyClass.cls'}')",
        "unmodelled package: 'graphicx' (required by 'MyClass.cls')",
        "unmodelled package: 'exotic'",
    ]
