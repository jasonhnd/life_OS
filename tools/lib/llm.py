"""Life OS tools — Claude Code subprocess LLM bridge (v1.7 Sprint 2).

Per references/tools-spec.md §7 and user decision #16, the ONLY permitted
LLM path for Python tools is the local ``claude`` CLI (Claude Code).
This module exposes a minimal wrapper so tools can obtain free-form or
JSON-shaped responses without hard-coupling to the subprocess plumbing.

NOT permitted (by policy):
 - ``anthropic`` SDK, ``openai`` SDK, or any HTTP LLM client
 - Reading ``ANTHROPIC_API_KEY`` / ``OPENAI_API_KEY`` from the environment

All error paths funnel through :class:`LLMError`.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import Any

__all__ = ["LLMBridge", "LLMError"]

_DEFAULT_MODEL = "claude-sonnet-4-6"
_DEFAULT_TIMEOUT_S = 60

# Strip common ```json ... ``` (or bare ```) fences from LLM output so callers
# get clean JSON. Greedy inner match, trailing fence optional.
_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```?\s*$", re.DOTALL | re.IGNORECASE)


class LLMError(Exception):
    """Raised for any failure invoking the Claude Code subprocess bridge."""


class LLMBridge:
    """Thin wrapper around ``claude -p``.

    Usage::

        bridge = LLMBridge()
        text   = bridge.invoke("Summarise this paragraph: ...")
        parsed = bridge.invoke_json("Return JSON: {\"ok\": bool}")
    """

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        timeout_s: int = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self.model = model
        self.timeout_s = timeout_s

    # ─── Public API ────────────────────────────────────────────────────

    def invoke(self, prompt: str, *, system: str | None = None) -> str:
        """Send ``prompt`` to ``claude -p`` and return the stripped stdout.

        If ``system`` is provided, it is prepended to the prompt so the
        model sees it before user content. We intentionally avoid a
        ``--system`` flag (not all CLI versions expose one) and keep the
        call shape minimal and portable.

        :raises LLMError: if ``claude`` is missing, the call times out,
            or the subprocess exits non-zero.
        """
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        cmd = ["claude", "-p", "--model", self.model, full_prompt]

        try:
            result = subprocess.run(  # noqa: S603 — fixed argv, no shell
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
                check=False,
            )
        except FileNotFoundError as exc:
            raise LLMError(
                "Claude Code CLI not found; install from https://claude.com/code"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise LLMError(
                f"LLM invocation timed out after {self.timeout_s}s"
            ) from exc

        if result.returncode != 0:
            err = (result.stderr or "").strip() or "(no stderr)"
            raise LLMError(
                f"Claude CLI exited {result.returncode}: {err}"
            )

        return (result.stdout or "").strip()

    def invoke_json(
        self,
        prompt: str,
        *,
        schema: dict[str, Any] | None = None,  # noqa: ARG002 — reserved for future validation
    ) -> dict[str, Any]:
        """Invoke the CLI and parse the response as JSON.

        Tolerates the common case where the model wraps output in
        ``` ```json``` fences. The ``schema`` argument is accepted but not
        yet enforced (reserved for v1.8 structured output validation).

        :raises LLMError: if the response is empty, not valid JSON, or
            does not decode to a dict.
        """
        text = self.invoke(prompt)
        if not text:
            raise LLMError("LLM returned empty output; cannot parse JSON")

        payload = self._strip_fence(text)
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise LLMError(
                f"Failed to parse LLM output as JSON: {exc.msg} "
                f"(first 120 chars: {payload[:120]!r})"
            ) from exc

        if not isinstance(parsed, dict):
            raise LLMError(
                f"Expected JSON object at top level, got {type(parsed).__name__}"
            )
        return parsed

    # ─── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _strip_fence(text: str) -> str:
        """Strip a leading/trailing markdown code fence, if any."""
        match = _FENCE_RE.match(text.strip())
        if match:
            return match.group(1).strip()
        return text.strip()
