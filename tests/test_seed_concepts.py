"""Tests for tools.seed_concepts — bootstrap concept graph from second-brain."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.seed_concepts import collect_text, main


# ─── collect_text ───────────────────────────────────────────────────────────


class TestCollectText:
    def test_empty_root(self, tmp_path: Path):
        assert collect_text(tmp_path) == ""

    def test_collects_wiki(self, tmp_path: Path):
        wiki_dir = tmp_path / "wiki" / "finance"
        wiki_dir.mkdir(parents=True)
        (wiki_dir / "test.md").write_text("PassPay content", encoding="utf-8")
        text = collect_text(tmp_path)
        assert "PassPay content" in text

    def test_collects_decisions(self, tmp_path: Path):
        d = tmp_path / "decisions"
        d.mkdir()
        (d / "2026-04-21.md").write_text("decision text", encoding="utf-8")
        text = collect_text(tmp_path)
        assert "decision text" in text

    def test_recursive_projects(self, tmp_path: Path):
        p = tmp_path / "projects" / "passpay" / "decisions"
        p.mkdir(parents=True)
        (p / "d1.md").write_text("nested decision", encoding="utf-8")
        text = collect_text(tmp_path)
        assert "nested decision" in text

    def test_skips_non_md(self, tmp_path: Path):
        d = tmp_path / "wiki"
        d.mkdir()
        (d / "test.txt").write_text("not collected", encoding="utf-8")
        (d / "test.md").write_text("collected", encoding="utf-8")
        text = collect_text(tmp_path)
        assert "collected" in text
        assert "not collected" not in text


# ─── CLI main() ─────────────────────────────────────────────────────────────


class TestMain:
    def test_dry_run_no_content(self, tmp_path: Path, capsys):
        with patch.object(sys, "argv", ["seed", "--root", str(tmp_path)]):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "No content found" in captured.out

    def test_dry_run_with_content(self, tmp_path: Path, capsys):
        wiki = tmp_path / "wiki" / "finance"
        wiki.mkdir(parents=True)
        (wiki / "test.md").write_text(
            "PassPay PassPay PassPay PassPay PassPay PassPay "
            "compliance compliance compliance compliance compliance compliance",
            encoding="utf-8",
        )
        with patch.object(sys, "argv", ["seed", "--root", str(tmp_path), "--top", "5"]):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "passpay" in captured.out.lower()
        assert "compliance" in captured.out.lower()
        assert "Add --write" in captured.out

    def test_write_creates_concept_files(self, tmp_path: Path, capsys):
        wiki = tmp_path / "wiki" / "finance"
        wiki.mkdir(parents=True)
        (wiki / "test.md").write_text(
            "passpay " * 10 + "compliance " * 10,
            encoding="utf-8",
        )
        with patch.object(
            sys,
            "argv",
            ["seed", "--root", str(tmp_path), "--top", "2", "--write"],
        ):
            result = main()
        assert result == 0

        # Concept files created at _meta/concepts/_tentative/
        tentative = tmp_path / "_meta" / "concepts" / "_tentative"
        assert tentative.exists()
        files = sorted(tentative.glob("*.md"))
        assert len(files) == 2
        slugs = {f.stem for f in files}
        assert "passpay" in slugs
        assert "compliance" in slugs

    def test_min_count_threshold(self, tmp_path: Path, capsys):
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        # Only 3 mentions of "rare", below default --min-count 5
        (wiki / "test.md").write_text("rare rare rare " + "common " * 10, encoding="utf-8")
        with patch.object(sys, "argv", ["seed", "--root", str(tmp_path)]):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "common" in captured.out.lower()
        assert "rare" not in captured.out.lower()

    def test_lower_min_count_includes_more(self, tmp_path: Path, capsys):
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "test.md").write_text("rare rare rare " + "common " * 10, encoding="utf-8")
        with patch.object(
            sys, "argv", ["seed", "--root", str(tmp_path), "--min-count", "2"]
        ):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "rare" in captured.out.lower()
        assert "common" in captured.out.lower()

    def test_nonexistent_root_returns_2(self, tmp_path: Path):
        bad = tmp_path / "nonexistent"
        with patch.object(sys, "argv", ["seed", "--root", str(bad)]):
            result = main()
        assert result == 2
