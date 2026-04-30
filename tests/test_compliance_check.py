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


# Round-4 audit fix: reusable full-briefing skeleton with all 6 H2 sections
# + version markers + cortex status marker so individual tests only trigger
# the specific failure they're asserting (instead of the catch-all
# C (P0): briefing-completeness fail blocking every other check).
_FULL_START_BRIEFING_BASE = (
    "🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0\n"
    "✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation)\n"
    "Step 2 DIRECTORY TYPE CHECK:\n"
    "a) 连接到 second-brain\n"
    "b) 开发模式\n"
    "c) 新建 second-brain\n"
    "[Local SKILL.md version: 1.8.0]\n"
    "[Remote check (forced fresh): up-to-date]\n"
    "[Cortex: skipped - per-message pull mode in v1.8.0]\n"
    "## 0. <display name> · 上朝准备\nReady\n\n"
    "## 1. 第二大脑同步状态\nClean\n\n"
    "## 2. SOUL Health 报告\nNo drift\n\n"
    "## 3. DREAM / 隔夜更新\nNone\n\n"
    "## 4. Today's Focus + 待陛下圣裁\nReady\n\n"
    "## 5. 系统状态\nGreen\n"
)


class TestStartSession:
    def test_clean_output_passes(self, tmp_path: Path):
        out = tmp_path / "clean.md"
        out.write_text(_FULL_START_BRIEFING_BASE, encoding="utf-8")
        result = _run(out, "start-session-compliance")
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "PASSED" in result.stdout

    def test_missing_preflight_fails(self, tmp_path: Path):
        # Round-4 audit fix: A3 (preflight-check) lives in the dedicated
        # `preflight-check` scenario, not in `start-session-compliance`'s
        # 5-check bundle. Use the specific scenario so the assertion
        # exercises the actual capability without coupling to which
        # scenarios bundle which checks.
        without_preflight = "\n".join(
            line for line in _FULL_START_BRIEFING_BASE.splitlines()
            if not line.startswith("🌅 Trigger")
        )
        out = tmp_path / "no_preflight.md"
        out.write_text(without_preflight, encoding="utf-8")
        result = _run(out, "preflight-check")
        assert result.returncode == 1
        assert "A3" in result.stderr

    def test_fabricated_path_detected(self, tmp_path: Path):
        # B (fabricate-path-check) lives in the dedicated scenario,
        # same as above.
        out = tmp_path / "fabricated.md"
        out.write_text(
            _FULL_START_BRIEFING_BASE
            + "\nPer _meta/roles/CLAUDE.md, we do XYZ\n",
            encoding="utf-8",
        )
        result = _run(out, "fabricate-path-check")
        assert result.returncode == 1
        assert "B" in result.stderr

    def test_fabricated_escape_phrase_detected(self, tmp_path: Path):
        # Round-4 audit fix: denylist uses the English form
        # "lightweight briefing path" (verified against
        # scripts/lifeos-compliance-check.sh check_fabricate_path list).
        # Earlier "轻量简报路径" Chinese form was a fixture artefact, never
        # in the denylist.
        out = tmp_path / "escape.md"
        out.write_text(
            _FULL_START_BRIEFING_BASE
            + "\nUsing the lightweight briefing path\n",
            encoding="utf-8",
        )
        result = _run(out, "fabricate-path-check")
        assert result.returncode == 1
        assert "B" in result.stderr


# ─── adjourn-compliance scenario ────────────────────────────────────────────


class TestAdjourn:
    def test_clean_adjourn_passes(self, tmp_path: Path):
        out = tmp_path / "clean.md"
        out.write_text(
            # Round-4 audit fix: archiver adjourn checker now also requires
            # `archiver self-check: I am the ARCHIVER subagent` line plus
            # `## Phase 1` through `## Phase 4` H2 sections plus
            # `## Completion Checklist` H2.
            "📝 Trigger: 退朝 → Theme: 三省六部 → Action: Launch(archiver) (4 phases)\n"
            "I am the ARCHIVER subagent\n"
            "## Phase 1\nPhase 1 outbox: _meta/outbox/claude-20260421-1530/\n\n"
            "## Phase 2\nwiki: 2 entries\n\n"
            "## Phase 3\nDREAM: 0 triggers\n\n"
            "## Phase 4\ngit: pushed (hash abc1234)\n\n"
            "## Completion Checklist\n"
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

    def test_cortex_enabled_no_agents_passes_post_pivot(self, tmp_path: Path) -> None:
        """v1.8.0 R-1.8.0-011 pull-based pivot: `cortex_enabled: true` is no
        longer a gate. ROUTER decides per-message whether to launch any
        Cortex subagent. A transcript with no Cortex launches is now valid
        regardless of the legacy config flag — there's nothing to verify
        when ROUTER chose to skip Cortex.
        """
        config_dir = tmp_path / "_meta"
        config_dir.mkdir()
        # Legacy flag — kept here only to confirm it is now ignored.
        (config_dir / "config.md").write_text(
            "cortex_enabled: true\n", encoding="utf-8"
        )
        out = tmp_path / "no_agents.md"
        out.write_text("no agents fired\n", encoding="utf-8")
        result = _run(out, "cortex-retrieval", cwd=tmp_path)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "CX1" not in result.stderr
        assert "CX2" not in result.stderr
        assert "CX3" not in result.stderr

    def test_cortex_partial_launch_fails(self, tmp_path: Path) -> None:
        """v1.8.0 pull-based: if ROUTER launches Cortex subagents, the
        transcript must also include GWT arbitration evidence (CX2) and
        the [COGNITIVE CONTEXT] delimiter block (CX3). A partial transcript
        that only shows module launches but no GWT or delimiter triggers
        CX2 + CX3 violations. This is the post-pivot replacement for the
        old cortex_enabled gate test.
        """
        out = tmp_path / "partial.md"
        out.write_text(
            "Task(hippocampus) launched\nTask(concept-lookup) launched\n",
            encoding="utf-8",
        )
        result = _run(out, "cortex-retrieval", cwd=tmp_path)
        assert result.returncode == 1
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
