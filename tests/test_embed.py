"""Tests for tools.embed — v1.7 placeholder (decision #3).

Spec: references/tools-spec.md §6.12.

The tool is intentionally unimplemented. It must:

1. Exit 0 on any invocation (so shell chains don't accidentally break).
2. Print a short notice that points the user to the right alternatives
   (hippocampus subagent for in-session retrieval, search.py for batch
   search).
3. Expose ``main(argv)`` for programmatic invocation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import embed


class TestEmbedPlaceholder:
    def test_main_returns_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        rc = embed.main([])
        assert rc == 0
        captured = capsys.readouterr()
        assert "not implemented" in captured.out.lower()

    def test_main_mentions_alternatives(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        embed.main([])
        captured = capsys.readouterr()
        # Point the user to the documented alternatives.
        assert "hippocampus" in captured.out.lower()
        assert "search.py" in captured.out.lower()

    def test_main_ignores_extra_args(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The tool shouldn't crash regardless of argv noise.
        rc = embed.main(["--foo", "bar", "--format", "anki"])
        assert rc == 0

    def test_invoked_as_script_exits_zero(self) -> None:
        tool_path = Path(__file__).resolve().parent.parent / "tools" / "embed.py"
        result = subprocess.run(
            [sys.executable, str(tool_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "not implemented" in result.stdout.lower()
