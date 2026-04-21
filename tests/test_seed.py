"""Tests for tools.seed — new-user second-brain bootstrap.

Per references/tools-spec.md §6.10. seed.py creates an empty-but-valid
second-brain layout, runs ``git init``, and produces an initial commit.

These tests exercise the CLI contract (idempotence is explicitly NOT a
property — re-running against a non-empty target must fail).
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

from tools.seed import main

# ─── Helpers ────────────────────────────────────────────────────────────────


def _git_available() -> bool:
    """Check that a git binary is on PATH. Skips git-dependent tests if not."""
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


# ─── Fresh-target tests (empty directory or not-yet-existing path) ──────────


class TestFreshTarget:
    def test_empty_dir_accepted_all_files_created(self, tmp_path: Path):
        target = tmp_path / "sb"
        target.mkdir()  # empty
        rc = main(["--path", str(target)])
        assert rc == 0
        # Required top-level scaffolding
        assert (target / "SOUL.md").is_file()
        assert (target / ".life-os.toml").is_file()
        assert (target / ".gitignore").is_file()
        assert (target / "projects" / "example-project" / "index.md").is_file()

    def test_meta_directories_present_with_gitkeep(self, tmp_path: Path):
        target = tmp_path / "sb"
        target.mkdir()
        main(["--path", str(target)])
        for subdir in (
            "_meta/sessions",
            "_meta/concepts",
            "_meta/snapshots",
            "_meta/eval-history",
            "_meta/methods",
        ):
            d = target / subdir
            assert d.is_dir(), f"Missing {subdir}"
            assert (d / ".gitkeep").is_file(), f"Missing {subdir}/.gitkeep"

    def test_inbox_and_wiki_gitkeep(self, tmp_path: Path):
        target = tmp_path / "sb"
        target.mkdir()
        main(["--path", str(target)])
        assert (target / "inbox" / ".gitkeep").is_file()
        assert (target / "wiki" / ".gitkeep").is_file()

    def test_nonexistent_path_creates_parents(self, tmp_path: Path):
        target = tmp_path / "deep" / "nested" / "sb"
        rc = main(["--path", str(target)])
        assert rc == 0
        assert target.is_dir()
        assert (target / "SOUL.md").is_file()

    def test_gitignore_includes_recommended_entries(self, tmp_path: Path):
        target = tmp_path / "sb"
        target.mkdir()
        main(["--path", str(target)])
        gitignore = (target / ".gitignore").read_text(encoding="utf-8")
        assert ".DS_Store" in gitignore
        # At least one junk-file pattern
        assert any(pat in gitignore for pat in ("*.tmp", ".DS_Store", "*.swp"))

    def test_life_os_toml_parseable(self, tmp_path: Path):
        target = tmp_path / "sb"
        target.mkdir()
        main(["--path", str(target)])
        with (target / ".life-os.toml").open("rb") as fh:
            data = tomllib.load(fh)
        assert "second_brain" in data
        assert "root" in data["second_brain"]
        # Tilde notation is tolerated — doesn't need to match tmp_path.

    def test_soul_md_has_section_headings(self, tmp_path: Path):
        target = tmp_path / "sb"
        target.mkdir()
        main(["--path", str(target)])
        soul = (target / "SOUL.md").read_text(encoding="utf-8")
        # At least one typical section heading to prove it's a real skeleton.
        assert "##" in soul
        # Title heading present too
        assert soul.startswith("# ")


# ─── Non-empty-target rejection ─────────────────────────────────────────────


class TestNonEmptyTarget:
    def test_non_empty_dir_exits_one(self, tmp_path: Path):
        target = tmp_path / "sb"
        target.mkdir()
        (target / "preexisting.md").write_text("hello", encoding="utf-8")
        rc = main(["--path", str(target)])
        assert rc == 1
        # The preexisting file must NOT be overwritten or removed.
        assert (target / "preexisting.md").read_text(encoding="utf-8") == "hello"
        # seed should not have written its own scaffolding.
        assert not (target / "SOUL.md").exists()

    def test_non_empty_only_dot_dirs_still_rejected(self, tmp_path: Path):
        """A dir with e.g. a user .git/ or a stray .DS_Store is not empty."""
        target = tmp_path / "sb"
        target.mkdir()
        (target / ".DS_Store").write_bytes(b"\x00\x01\x02")
        rc = main(["--path", str(target)])
        # Per spec: any non-empty content means we refuse.
        assert rc == 1


# ─── Git-integration tests (skipped when git is unavailable) ────────────────


class TestGitInitIntegration:
    def test_git_dir_present_after_seed(self, tmp_path: Path):
        if not _git_available():
            import pytest

            pytest.skip("git not on PATH")
        target = tmp_path / "sb"
        target.mkdir()
        rc = main(["--path", str(target)])
        assert rc == 0
        assert (target / ".git").is_dir()

    def test_initial_commit_recorded(self, tmp_path: Path):
        if not _git_available():
            import pytest

            pytest.skip("git not on PATH")
        target = tmp_path / "sb"
        target.mkdir()
        main(["--path", str(target)])
        # `git log` must have at least one commit.
        result = subprocess.run(
            ["git", "-C", str(target), "log", "--oneline"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        # Non-empty stdout implies at least one commit exists.
        assert result.stdout.strip(), (
            f"Expected initial commit, got stdout={result.stdout!r} "
            f"stderr={result.stderr!r}"
        )

    def test_initial_commit_message_matches_spec(self, tmp_path: Path):
        if not _git_available():
            import pytest

            pytest.skip("git not on PATH")
        target = tmp_path / "sb"
        target.mkdir()
        main(["--path", str(target)])
        result = subprocess.run(
            ["git", "-C", str(target), "log", "--format=%s"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        assert "Initial Life OS v1.7 second-brain" in result.stdout


# ─── Module entry point via python -m (sanity) ──────────────────────────────


class TestModuleEntry:
    def test_runs_via_python_m(self, tmp_path: Path):
        target = tmp_path / "sb_mod"
        target.mkdir()
        # Use python -m to ensure the module is callable that way too.
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-m", "tools.seed", "--path", str(target)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        assert (target / "SOUL.md").is_file()
