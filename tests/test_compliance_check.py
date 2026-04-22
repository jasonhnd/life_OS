"""Tests for scripts/lifeos-compliance-check.sh via subprocess.

Validates the bash compliance check script behavior on synthetic inputs.
Each test creates a temp output file and config, invokes the script, and
asserts on exit code + stdout/stderr.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _REPO_ROOT / "scripts" / "lifeos-compliance-check.sh"
_BASH_CANDIDATES = (
    "bash",
    "bash.exe",
    r"C:\Program Files\Git\bin\bash.exe",
    r"C:\Program Files\Git\usr\bin\bash.exe",
    r"C:\Windows\System32\bash.exe",
)


def _find_bash() -> str:
    """Resolve a usable bash executable on Windows test runners."""
    for candidate in _BASH_CANDIDATES:
        resolved = shutil.which(candidate) or (candidate if Path(candidate).exists() else None)
        if resolved:
            return resolved
    raise FileNotFoundError("No bash executable found for compliance-check subprocess tests.")


_BASH = _find_bash()


def _run(output_file: Path, scenario: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Invoke the compliance check script and return CompletedProcess.

    Forces UTF-8 decoding of stdout/stderr so emoji and CJK characters emitted
    by the bash script do not crash the default Windows cp932 codec.
    """
    return subprocess.run(
        [_BASH, str(_SCRIPT), str(output_file), scenario],
        cwd=cwd or _REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


# ─── start-session-compliance scenario ──────────────────────────────────────


class TestStartSession:
    def test_clean_output_passes(self, tmp_path: Path):
        out = tmp_path / "clean.md"
        out.write_text(
            "🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0\n"
            "✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation)\n"
            "Step 2 DIRECTORY TYPE CHECK:\n"
            "a) 连接到 second-brain\n"
            "b) 开发模式\n"
            "c) 新建 second-brain\n",
            encoding="utf-8",
        )
        result = _run(out, "start-session-compliance")
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "PASSED" in result.stdout

    def test_missing_preflight_fails(self, tmp_path: Path):
        out = tmp_path / "no_preflight.md"
        out.write_text(
            "✅ I am the RETROSPECTIVE subagent\n"
            "a) 连接到 second-brain\nb) 开发模式\n",
            encoding="utf-8",
        )
        result = _run(out, "start-session-compliance")
        assert result.returncode == 1
        assert "A3" in result.stderr

    def test_fabricated_path_detected(self, tmp_path: Path):
        out = tmp_path / "fabricated.md"
        out.write_text(
            "🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0\n"
            "✅ I am the RETROSPECTIVE subagent\n"
            "a) 连接到 second-brain\nb) 开发模式\n"
            "Per _meta/roles/CLAUDE.md, we do XYZ\n",
            encoding="utf-8",
        )
        result = _run(out, "start-session-compliance")
        assert result.returncode == 1
        assert "B" in result.stderr

    def test_fabricated_escape_phrase_detected(self, tmp_path: Path):
        out = tmp_path / "escape.md"
        out.write_text(
            "🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0\n"
            "✅ I am the RETROSPECTIVE subagent\n"
            "a) 连接到 second-brain\nb) 开发模式\n"
            "Using the 轻量简报路径\n",
            encoding="utf-8",
        )
        result = _run(out, "start-session-compliance")
        assert result.returncode == 1
        assert "B" in result.stderr


# ─── adjourn-compliance scenario ────────────────────────────────────────────


class TestAdjourn:
    def test_clean_adjourn_passes(self, tmp_path: Path):
        out = tmp_path / "clean.md"
        out.write_text(
            "📝 Trigger: 退朝 → Theme: 三省六部 → Action: Launch(archiver) (4 phases)\n"
            "✅ Adjourn Completion Checklist:\n"
            "- Phase 1 outbox: _meta/outbox/claude-20260421-1530/\n"
            "- Phase 2 wiki: 2 entries\n"
            "- Phase 3 DREAM: 0 triggers\n"
            "- Phase 4 git: pushed (hash abc1234)\n",
            encoding="utf-8",
        )
        result = _run(out, "adjourn-compliance")
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "PASSED" in result.stdout

    def test_missing_phase_3_and_4_detected(self, tmp_path: Path):
        out = tmp_path / "incomplete.md"
        out.write_text(
            "📝 Trigger: 退朝 → Theme: 三省六部 → Action: Launch(archiver) (4 phases)\n"
            "- Phase 1 outbox: x\n- Phase 2 wiki: x\n",
            encoding="utf-8",
        )
        result = _run(out, "adjourn-compliance")
        assert result.returncode == 1
        assert "Phase 3" in result.stderr
        assert "Phase 4" in result.stderr

    def test_placeholder_value_detected(self, tmp_path: Path):
        out = tmp_path / "placeholder.md"
        out.write_text(
            "📝 Trigger: 退朝 → Theme: 三省六部 → Action: Launch(archiver) (4 phases)\n"
            "- Phase 1 outbox: TBD\n"
            "- Phase 2 wiki: 2 entries\n"
            "- Phase 3 DREAM: 0 triggers\n"
            "- Phase 4 git: pushed\n",
            encoding="utf-8",
        )
        result = _run(out, "adjourn-compliance")
        assert result.returncode == 1
        assert "TBD" in result.stderr
        assert "D" in result.stderr  # Class D


# ─── cortex-retrieval scenario ──────────────────────────────────────────────


class TestCortex:
    def test_cortex_disabled_passes_silently(self, tmp_path: Path):
        # No config file -> assumed OFF
        out = tmp_path / "no_agents.md"
        out.write_text("just a user message, no Cortex agents\n", encoding="utf-8")
        result = _run(out, "cortex-retrieval", cwd=tmp_path)
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_cortex_explicit_false_passes(self, tmp_path: Path):
        config_dir = tmp_path / "_meta"
        config_dir.mkdir()
        (config_dir / "config.md").write_text("cortex_enabled: false\n", encoding="utf-8")
        out = tmp_path / "no_agents.md"
        out.write_text("no agents\n", encoding="utf-8")
        result = _run(out, "cortex-retrieval", cwd=tmp_path)
        assert result.returncode == 0

    def test_cortex_enabled_no_agents_fails(self, tmp_path: Path):
        config_dir = tmp_path / "_meta"
        config_dir.mkdir()
        (config_dir / "config.md").write_text(
            "cortex_enabled: true\n", encoding="utf-8"
        )
        out = tmp_path / "no_agents.md"
        out.write_text("no agents fired\n", encoding="utf-8")
        result = _run(out, "cortex-retrieval", cwd=tmp_path)
        assert result.returncode == 1
        # Should detect CX1 (3 missing subagents) + CX2 + CX3
        assert "CX1" in result.stderr
        assert "CX2" in result.stderr
        assert "CX3" in result.stderr


# ─── unknown scenario ──────────────────────────────────────────────────────


class TestUnknownScenario:
    def test_unknown_scenario_skips_silently(self, tmp_path: Path):
        out = tmp_path / "any.md"
        out.write_text("anything\n", encoding="utf-8")
        result = _run(out, "no-such-scenario")
        assert result.returncode == 0
        assert "skipping" in result.stderr.lower()
