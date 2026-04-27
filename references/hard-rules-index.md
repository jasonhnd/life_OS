# HARD RULES Index

This index is the public pointer for non-overridable Life OS behavior. README files must link here instead of embedding a hard-coded rule count.

## Source Of Truth

- `SKILL.md`: universal system contract, theme-language rule, trigger templates, ROUTER fact-checking, session binding, pre-session display, adjourn behavior, and router code of conduct.
- `pro/{CLAUDE,GEMINI,AGENTS}.md`: host-specific orchestration contracts. Use the file for the active host; do not add the three host copies together.
- `pro/GLOBAL.md`: universal agent behavior, including research-process display and progress reporting.
- `pro/agents/*.md`: role-local contracts that are enforced when the active host launches that role. These files are authoritative for the role, but are not added into the top-level per-host marker count below.

## v1.7.2 Release Deltas

- **Hermes Local / paste compression**: `SKILL.md` now treats every launched subagent output as a compressed paste plus an R11 audit trail link. The compressed paste must preserve substantive claims, decisions, blockers, user-facing requests, file writes, tool side effects, and quoted evidence needed for review; it cannot be replaced by an unsupported summary.
- **Manual compression trigger**: `/compress [focus]` is part of the `SKILL.md` Trigger Execution Templates section. v1.7.3 wires the slash command via `scripts/commands/compress.md` (installed to `~/.claude/commands/`). ROUTER does inline compression, archives to `_meta/compression/<sid>-compress-<ts>.md`, and reports original/retained turn count + rough tokens released + preserved decisions. The dead `tools/context_compressor.py` (1370 lines, 0 callers) and `tools/manual_compression_feedback.py` (51 lines, 0 callers) were removed in v1.7.3.
- **Cortex always-on scope**: v1.7.2 host contracts attempt Step 0.5 for every user message. This changes activation semantics but does not add a new top-level `HARD RULE` marker to the count below. `_meta/config.md` may hold thresholds and secondary switches; it is not an activation gate, and missing indexes trigger auto-bootstrap or graceful degradation rather than a config-gated skip.

## Current Count

Current explicit HARD RULE marker count is counted per active host, as of v1.7.2. Do not add host files together.

| Host | Count | Breakdown |
|------|-------|-----------|
| Claude Code | 40 | `SKILL.md` 18 + `pro/CLAUDE.md` 20 + `pro/GLOBAL.md` 2 |
| Gemini CLI / Antigravity | 36 | `SKILL.md` 18 + `pro/GEMINI.md` 16 + `pro/GLOBAL.md` 2 |
| OpenAI Codex CLI | 36 | `SKILL.md` 18 + `pro/AGENTS.md` 16 + `pro/GLOBAL.md` 2 |

Count method: count lines containing an explicit `HARD RULE` marker in `SKILL.md`, exactly one active host orchestration file, and `pro/GLOBAL.md`. Security boundaries in `pro/GLOBAL.md` remain inviolable even when not labeled with the literal phrase `HARD RULE`.

## Maintenance

- Update this index whenever a HARD RULE marker is added, removed, or moved in an authoritative file.
- Keep README language generic and link here instead of repeating the count.
- If host files intentionally diverge, record the per-host delta here before changing release docs.
- Do not count all three host orchestration files together. Do not count role-local `pro/agents/*.md` markers in the top-level per-host table unless this index is explicitly expanded to a full-corpus count.
