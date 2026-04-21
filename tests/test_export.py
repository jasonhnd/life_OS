"""Tests for tools.export — v1.7 Sprint 5.

Spec: references/tools-spec.md §6.9.

Covers all 4 formats (pdf/html/json/anki), per-type Anki field mapping,
scope empty / missing-pandoc error paths, and the scope-slug + date
filename convention.
"""

from __future__ import annotations

import json
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tools import export

# ─── Fixtures ───────────────────────────────────────────────────────────────


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def scope_with_mixed_files(tmp_path: Path) -> Path:
    """A scope directory with concept, method, wiki, and session markdown."""
    root = tmp_path / "scope"
    _write(
        root / "concept.md",
        "---\n"
        "type: concept\n"
        "concept_id: autonomy\n"
        "canonical_name: Autonomy\n"
        "aliases:\n"
        "  - independence\n"
        "  - self-direction\n"
        "outgoing_edges:\n"
        "  - target: agency\n"
        "    weight: 9\n"
        "  - target: freedom\n"
        "    weight: 6\n"
        "---\n"
        "A core SOUL dimension — the capacity to act on one's own reasons.\n",
    )
    _write(
        root / "method.md",
        "---\n"
        "type: method\n"
        "method_id: tdd\n"
        "name: Test-Driven Development\n"
        "summary: Write a failing test, then the code to pass it.\n"
        "---\n"
        "## Steps\n"
        "1. Write a failing test.\n"
        "2. Make it pass.\n"
        "3. Refactor.\n",
    )
    _write(
        root / "wiki.md",
        "---\n"
        "type: wiki\n"
        "title: Compound interest beats market timing\n"
        "---\n"
        "## Reasoning\n"
        "Time in the market > timing the market.\n"
        "## Applicable When\n"
        "You have a 10+ year horizon.\n",
    )
    _write(
        root / "session.md",
        "---\n"
        "type: session\n"
        "session_id: 2026-04-20-001\n"
        "subject: Ship Sprint 5 export tool\n"
        "---\n"
        "## Key Decisions\n"
        "- Use pandoc for pdf, genanki for anki.\n"
        "## Outcome\n"
        "Tool merged, coverage at 90%.\n",
    )
    return root


@pytest.fixture
def empty_scope(tmp_path: Path) -> Path:
    root = tmp_path / "empty"
    root.mkdir()
    return root


# ─── slug_from_scope ─────────────────────────────────────────────────────────


class TestSlugFromScope:
    def test_simple_path(self, tmp_path: Path) -> None:
        scope = tmp_path / "projects" / "passpay"
        scope.mkdir(parents=True)
        assert export.slug_from_scope(scope) == "passpay"

    def test_nested_path(self, tmp_path: Path) -> None:
        scope = tmp_path / "_meta" / "concepts" / "money"
        scope.mkdir(parents=True)
        assert export.slug_from_scope(scope) == "money"

    def test_replaces_unsafe_chars(self, tmp_path: Path) -> None:
        scope = tmp_path / "My Weird Scope"
        scope.mkdir()
        slug = export.slug_from_scope(scope)
        assert " " not in slug
        assert slug == "my-weird-scope"


# ─── collect_markdown ────────────────────────────────────────────────────────


class TestCollectMarkdown:
    def test_finds_all_markdown(self, scope_with_mixed_files: Path) -> None:
        docs = export.collect_markdown(scope_with_mixed_files)
        assert len(docs) == 4
        types = sorted(d.frontmatter.get("type", "") for d in docs)
        assert types == ["concept", "method", "session", "wiki"]

    def test_empty_scope(self, empty_scope: Path) -> None:
        assert export.collect_markdown(empty_scope) == []

    def test_ignores_non_markdown(self, tmp_path: Path) -> None:
        root = tmp_path / "s"
        root.mkdir()
        _write(root / "a.md", "---\ntype: concept\n---\nbody")
        _write(root / "b.txt", "not markdown")
        assert len(export.collect_markdown(root)) == 1


# ─── export_json ─────────────────────────────────────────────────────────────


class TestExportJson:
    def test_produces_flat_array(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out.json"
        rc = export.export_json(scope_with_mixed_files, out)
        assert rc == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 4

    def test_each_entry_has_frontmatter_and_body(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out.json"
        export.export_json(scope_with_mixed_files, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        for entry in data:
            assert "frontmatter" in entry
            assert "body" in entry
            assert isinstance(entry["frontmatter"], dict)
            assert isinstance(entry["body"], str)


# ─── export_html ─────────────────────────────────────────────────────────────


class TestExportHtml:
    def test_self_contained(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out.html"
        rc = export.export_html(scope_with_mixed_files, out)
        assert rc == 0
        html = out.read_text(encoding="utf-8")
        # Inline <style>, no external <link> or <script src="http...">.
        assert "<style>" in html
        assert 'rel="stylesheet"' not in html
        assert 'href="http' not in html.lower() or '<a href="http' in html.lower()

    def test_renders_table(self, tmp_path: Path) -> None:
        root = tmp_path / "s"
        _write(
            root / "note.md",
            "---\ntype: wiki\n---\n| a | b |\n| - | - |\n| 1 | 2 |\n",
        )
        out = tmp_path / "out.html"
        export.export_html(root, out)
        html = out.read_text(encoding="utf-8")
        assert "<table>" in html.lower()

    def test_renders_footnote(self, tmp_path: Path) -> None:
        root = tmp_path / "s"
        _write(
            root / "note.md",
            "---\ntype: wiki\n---\nSee the note[^1].\n\n[^1]: A footnote.\n",
        )
        out = tmp_path / "out.html"
        export.export_html(root, out)
        html = out.read_text(encoding="utf-8")
        assert "footnote" in html.lower() or "fn:1" in html.lower() or "fnref" in html.lower()


# ─── export_pdf (pandoc) ─────────────────────────────────────────────────────


class TestExportPdf:
    def test_missing_pandoc_exit_1(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out.pdf"
        with patch.object(export, "_pandoc_available", return_value=False):
            rc = export.export_pdf(scope_with_mixed_files, out)
        assert rc == 1
        assert not out.exists()

    def test_invokes_pandoc_when_available(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out.pdf"
        with (
            patch.object(export, "_pandoc_available", return_value=True),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0
            )
            rc = export.export_pdf(scope_with_mixed_files, out)
            assert rc == 0
            assert mock_run.called
            call_args = mock_run.call_args.args[0]
            assert call_args[0] == "pandoc"

    def test_pandoc_failure_exit_1(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out.pdf"
        with (
            patch.object(export, "_pandoc_available", return_value=True),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=1, stderr="pandoc fell over"
            )
            rc = export.export_pdf(scope_with_mixed_files, out)
            assert rc == 1


# ─── export_anki (per-type mapping) ──────────────────────────────────────────


class TestExportAnki:
    def test_anki_file_is_apkg(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out.apkg"
        rc = export.export_anki(scope_with_mixed_files, out, deck_name="test-deck")
        assert rc == 0
        assert out.exists()
        # .apkg files are zip archives
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
            assert any(name.endswith(".anki2") or name == "collection.anki2" for name in names)

    def test_concept_card_mapping(self, tmp_path: Path) -> None:
        root = tmp_path / "s"
        _write(
            root / "c.md",
            "---\n"
            "type: concept\n"
            "canonical_name: Autonomy\n"
            "aliases:\n"
            "  - independence\n"
            "outgoing_edges:\n"
            "  - target: agency\n"
            "    weight: 9\n"
            "---\n"
            "Body text for the concept.\n",
        )
        notes = export.build_anki_notes(root)
        # One concept note expected.
        concept_notes = [n for n in notes if n.type_name == "concept"]
        assert len(concept_notes) == 1
        note = concept_notes[0]
        assert "Autonomy" in note.front
        assert "independence" in note.front
        assert "Body text" in note.back
        assert "agency" in note.back

    def test_method_card_mapping(self, tmp_path: Path) -> None:
        root = tmp_path / "s"
        _write(
            root / "m.md",
            "---\n"
            "type: method\n"
            "name: TDD\n"
            "summary: Test first, code second.\n"
            "---\n"
            "## Steps\n"
            "1. Red.\n"
            "2. Green.\n"
            "3. Refactor.\n",
        )
        notes = export.build_anki_notes(root)
        method_notes = [n for n in notes if n.type_name == "method"]
        assert len(method_notes) == 1
        note = method_notes[0]
        assert note.front == "TDD"
        assert "Test first" in note.back
        assert "Red" in note.back

    def test_wiki_card_mapping(self, tmp_path: Path) -> None:
        root = tmp_path / "s"
        _write(
            root / "w.md",
            "---\n"
            "type: wiki\n"
            "title: Time in market beats timing\n"
            "---\n"
            "## Reasoning\n"
            "Math of compounding.\n"
            "## Applicable When\n"
            "Long horizon.\n",
        )
        notes = export.build_anki_notes(root)
        wiki_notes = [n for n in notes if n.type_name == "wiki"]
        assert len(wiki_notes) == 1
        note = wiki_notes[0]
        assert "Time in market" in note.front
        assert "Math of compounding" in note.back
        assert "Long horizon" in note.back

    def test_session_card_mapping(self, tmp_path: Path) -> None:
        root = tmp_path / "s"
        _write(
            root / "s1.md",
            "---\n"
            "type: session\n"
            "subject: Sprint 5 delivery\n"
            "---\n"
            "## Key Decisions\n"
            "- Ship it.\n"
            "## Outcome\n"
            "Shipped.\n",
        )
        notes = export.build_anki_notes(root)
        sess_notes = [n for n in notes if n.type_name == "session"]
        assert len(sess_notes) == 1
        note = sess_notes[0]
        assert note.front == "Sprint 5 delivery"
        assert "Ship it" in note.back
        assert "Shipped" in note.back

    def test_concept_top_5_edges_only(self, tmp_path: Path) -> None:
        root = tmp_path / "s"
        edges = "\n".join(
            f"  - target: n{i}\n    weight: {10 - i}" for i in range(8)
        )
        _write(
            root / "c.md",
            "---\n"
            "type: concept\n"
            "canonical_name: Wide\n"
            f"outgoing_edges:\n{edges}\n"
            "---\n"
            "body\n",
        )
        notes = export.build_anki_notes(root)
        back = notes[0].back
        # Top 5 by weight: n0..n4, not n5/n6/n7.
        assert "n0" in back and "n4" in back
        assert "n7" not in back


# ─── run() dispatcher ────────────────────────────────────────────────────────


class TestRunDispatcher:
    def test_empty_scope_exit_1(self, empty_scope: Path, tmp_path: Path) -> None:
        rc = export.run(
            fmt="json", scope=empty_scope, output_dir=tmp_path
        )
        assert rc == 1

    def test_missing_scope_exit_1(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope"
        rc = export.run(fmt="json", scope=missing, output_dir=tmp_path)
        assert rc == 1

    def test_output_filename_format(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        out_dir = tmp_path / "exports"
        rc = export.run(
            fmt="json", scope=scope_with_mixed_files, output_dir=out_dir
        )
        assert rc == 0
        # Filename: {scope-slug}-{YYYY-MM-DD}.json
        files = list(out_dir.glob("*.json"))
        assert len(files) == 1
        name = files[0].name
        # Stem: scope-YYYY-MM-DD
        assert name.endswith(".json")
        parts = files[0].stem.split("-")
        # Last three parts are YYYY, MM, DD.
        year, month, day = parts[-3], parts[-2], parts[-1]
        assert len(year) == 4 and year.isdigit()
        assert len(month) == 2 and month.isdigit()
        assert len(day) == 2 and day.isdigit()

    def test_unknown_format_exit_1(
        self, scope_with_mixed_files: Path, tmp_path: Path
    ) -> None:
        rc = export.run(
            fmt="docx", scope=scope_with_mixed_files, output_dir=tmp_path
        )
        assert rc == 1
