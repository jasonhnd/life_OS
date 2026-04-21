"""Tests for tools/lib/llm.py — v1.7 Sprint 2.

Per references/tools-spec.md §7 + user decision #16:
 - Only permitted LLM path: `claude -p` subprocess (Claude Code CLI)
 - NO external LLM APIs (anthropic, openai, etc.)
 - Bridge just invokes subprocess and returns text / parsed JSON
"""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock

import pytest

from tools.lib.llm import LLMBridge, LLMError

# ─── Construction ───────────────────────────────────────────────────────────


def test_bridge_defaults() -> None:
    bridge = LLMBridge()
    assert bridge.model == "claude-sonnet-4-6"
    assert bridge.timeout_s == 60


def test_bridge_custom_model_and_timeout() -> None:
    bridge = LLMBridge(model="claude-opus-4-7", timeout_s=120)
    assert bridge.model == "claude-opus-4-7"
    assert bridge.timeout_s == 120


# ─── invoke(): happy path ───────────────────────────────────────────────────


def test_invoke_passes_model_and_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, list[str]] = {}

    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        captured["cmd"] = cmd
        result = MagicMock()
        result.returncode = 0
        result.stdout = "response text"
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge(model="claude-sonnet-4-6")
    out = bridge.invoke("Hello")
    assert out == "response text"
    # Order: claude -p --model <model> <prompt>
    assert captured["cmd"][0] == "claude"
    assert "-p" in captured["cmd"]
    assert "--model" in captured["cmd"]
    assert "claude-sonnet-4-6" in captured["cmd"]
    assert "Hello" in captured["cmd"]


def test_invoke_strips_trailing_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = "response\n\n"
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    assert bridge.invoke("x") == "response"


def test_invoke_with_system_prompt_prepends_it(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, list[str]] = {}

    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        captured["cmd"] = cmd
        result = MagicMock()
        result.returncode = 0
        result.stdout = "ok"
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    bridge.invoke("user prompt", system="you are a robot")

    # System text must appear somewhere in the final prompt arg
    # (via --system flag OR prepended to prompt — implementation detail)
    joined = " ".join(captured["cmd"])
    assert "you are a robot" in joined
    assert "user prompt" in joined


# ─── invoke(): error paths ──────────────────────────────────────────────────


def test_invoke_non_zero_exit_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        result = MagicMock()
        result.returncode = 1
        result.stdout = ""
        result.stderr = "boom"
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    with pytest.raises(LLMError, match="exit|failed|boom"):
        bridge.invoke("x")


def test_invoke_file_not_found_claude_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        raise FileNotFoundError("No such file: claude")

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    with pytest.raises(LLMError, match="Claude Code CLI|not found"):
        bridge.invoke("hi")


def test_invoke_timeout_raises_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        raise subprocess.TimeoutExpired(cmd="claude", timeout=5)

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge(timeout_s=5)
    with pytest.raises(LLMError, match="timed out|timeout"):
        bridge.invoke("slow prompt")


# ─── invoke_json() ─────────────────────────────────────────────────────────


def test_invoke_json_parses_valid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = json.dumps({"name": "x", "count": 3})
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    parsed = bridge.invoke_json("give me json")
    assert parsed == {"name": "x", "count": 3}


def test_invoke_json_handles_markdown_codefence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LLMs commonly wrap JSON in ```json ... ``` fences — bridge must strip them."""

    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = '```json\n{"hello": "world"}\n```'
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    parsed = bridge.invoke_json("x")
    assert parsed == {"hello": "world"}


def test_invoke_json_invalid_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = "this is plainly not JSON"
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    with pytest.raises(LLMError, match="JSON|parse"):
        bridge.invoke_json("x")


def test_invoke_json_empty_output_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    with pytest.raises(LLMError, match="empty|JSON|parse"):
        bridge.invoke_json("x")


# ─── subprocess call-shape ─────────────────────────────────────────────────


def test_invoke_uses_timeout_and_text_and_capture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        captured.update(kwargs)
        result = MagicMock()
        result.returncode = 0
        result.stdout = "ok"
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge(timeout_s=42)
    bridge.invoke("p")
    assert captured["timeout"] == 42
    assert captured["capture_output"] is True
    assert captured["text"] is True


# ─── No API credentials read ────────────────────────────────────────────────


def test_invoke_never_touches_anthropic_or_openai_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    User decision #16: bridge must NOT depend on ANTHROPIC_API_KEY or
    OPENAI_API_KEY. Prove by deleting them and still succeeding.
    """
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = "ok"
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = LLMBridge()
    assert bridge.invoke("x") == "ok"
