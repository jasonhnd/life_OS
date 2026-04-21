"""Tests for tools.cli — unified subcommand dispatcher."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from tools.cli import _COMMANDS, main

# ─── Help / list ─────────────────────────────────────────────────────────────


class TestHelp:
    def test_no_args_prints_usage(self, capsys):
        with patch.object(sys, "argv", ["life-os-tool"]):
            result = main()
        captured = capsys.readouterr()
        assert result == 0
        assert "Usage:" in captured.out
        assert "Available commands:" in captured.out

    def test_help_flag(self, capsys):
        with patch.object(sys, "argv", ["life-os-tool", "--help"]):
            result = main()
        captured = capsys.readouterr()
        assert result == 0
        assert "Usage:" in captured.out

    def test_list_command(self, capsys):
        with patch.object(sys, "argv", ["life-os-tool", "list"]):
            result = main()
        captured = capsys.readouterr()
        assert result == 0
        # All command names should appear
        for cmd in _COMMANDS:
            assert cmd in captured.out


class TestUnknownCommand:
    def test_unknown_returns_2(self, capsys):
        with patch.object(sys, "argv", ["life-os-tool", "no-such-command"]):
            result = main()
        captured = capsys.readouterr()
        assert result == 2
        assert "Unknown command" in captured.err


# ─── Subcommand dispatch ────────────────────────────────────────────────────


class TestDispatch:
    def test_stats_dispatches(self, tmp_path: Path, capsys):
        # Create a violations.md so stats has something to read
        (tmp_path / "pro" / "compliance").mkdir(parents=True)
        v_path = tmp_path / "pro" / "compliance" / "violations.md"
        v_path.write_text(
            "| 2026-04-19T22:47+09:00 | trigger | A1 | P0 | test | partial |\n",
            encoding="utf-8",
        )
        # Run from tmp_path so resolve_violations_path finds the file
        with (
            patch.object(sys, "argv", ["life-os-tool", "stats"]),
            patch("pathlib.Path.cwd", return_value=tmp_path),
        ):
            result = main()
        captured = capsys.readouterr()
        assert result == 0
        assert "Compliance Stats" in captured.out
        assert "A1" in captured.out

    def test_rebuild_session_index_missing_dir_returns_2(self, tmp_path: Path, capsys):
        with patch.object(
            sys, "argv", ["life-os-tool", "rebuild-session-index", "--root", str(tmp_path)]
        ):
            result = main()
        # Should return 2 because _meta/sessions/ doesn't exist
        assert result == 2

    def test_backup_dry_run_no_data(self, tmp_path: Path, capsys):
        with patch.object(
            sys, "argv", ["life-os-tool", "backup", "--root", str(tmp_path), "--dry-run"]
        ):
            result = main()
        captured = capsys.readouterr()
        assert result == 0
        assert "dry-run" in captured.out


# ─── argv preservation ──────────────────────────────────────────────────────


class TestArgvPreservation:
    def test_argv_restored_after_dispatch(self, tmp_path: Path):
        (tmp_path / "pro" / "compliance").mkdir(parents=True)
        v_path = tmp_path / "pro" / "compliance" / "violations.md"
        v_path.write_text("# empty\n", encoding="utf-8")
        original_argv = ["life-os-tool", "stats"]
        with patch.object(sys, "argv", original_argv.copy()):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                main()
            # After main returns, sys.argv should be restored
            assert sys.argv == original_argv
