# HARD RULES Index

This index is the public pointer for non-overridable Life OS behavior. README files must link here instead of embedding a hard-coded rule count.

## Source Of Truth

- `SKILL.md`: universal system contract, theme-language rule, trigger templates, ROUTER fact-checking, session binding, pre-session display, adjourn behavior, and router code of conduct.
- `hosts/{CLAUDE,GEMINI,AGENTS}.md`: host-specific orchestration contracts. Use the file for the active host; do not add the three host copies together.
- `hosts/GLOBAL.md`: universal agent behavior, including research-process display and progress reporting.
- `agents/*.md`: role-local contracts that are enforced when the active host launches that role. These files are authoritative for the role, but are not added into the top-level per-host marker count below.

## v1.7.2 Release Deltas

- **Hermes Local / paste compression**: `SKILL.md` now treats every launched subagent output as a compressed paste plus an R11 audit trail link. The compressed paste must preserve substantive claims, decisions, blockers, user-facing requests, file writes, tool side effects, and quoted evidence needed for review; it cannot be replaced by an unsupported summary.
- **Manual compression trigger**: `/compress [focus]` is part of the `SKILL.md` Trigger Execution Templates section. v1.7.3 wires the slash command via `scripts/commands/compress.md` (installed to `~/.claude/commands/`). ROUTER does inline compression, archives to `meta/compression/<sid>-compress-<ts>.md`, and reports original/retained turn count + rough tokens released + preserved decisions. The dead `tools/context_compressor.py` (1370 lines, 0 callers) and `tools/manual_compression_feedback.py` (51 lines, 0 callers) were removed in v1.7.3.
- **Cortex pull-based scope (v1.8.0 pivot — supersedes v1.7.2 always-on)**: As of v1.8.0, Cortex Step 0.5 is **no longer always-on**. ROUTER decides per-message whether to launch any of the 4 Cortex subagents (hippocampus / concept-lookup / soul-check / gwt-arbitrator). The `pre-prompt-guard.sh` always-on enforcement block was removed. There is no `HARD RULE` marker for Cortex activation in the count below. See `hosts/CLAUDE.md` §0.5 for the pull-based heuristics.

## v1.8.7 Release Deltas

- **md-only ontological elevation (DR-10)**: The existing `SKILL.md` HARD RULE "No .py / .sh / .yml / .json files" (v1.8.5 Stage 2 + v1.8.6 expansion) was upgraded in v1.8.7 to "md-only is lifeos's ontological constraint, no escape hatch, permanent". The marker count is unchanged (still 1 marker for this rule), but the rule's scope and authority were elevated:
  - Now lists 9 forbidden extensions (added `.sql` / `.db` / `.sqlite` to existing `.py` / `.sh` / `.bash` / `.yml` / `.yaml` / `.json`)
  - No escape hatch / no conditional exception / applies to all future versions
  - Borrowing patterns from external projects: only borrow patterns, never implementation tech stacks
  - Audit gates: existing `/verify-release` check #8 (full-repo) + v1.8.7 new check #10 (diff-scoped) + AUDITOR Mode 7 M7-7 + 4 regression fixtures (sh existing, sql/json/db new)
  - Reference: `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` DR-10 + §1.5
- **Implemented v1.8.7 additions** (Task 8 complete, ship verified at HEAD == tag v1.8.7):
  - B4 Self-driven loops with ScheduleWakeup section → **+1 marker** in `SKILL.md` (§ "HARD RULE · Self-driven loops with ScheduleWakeup (v1.8.7 B4)")
  - B5 evals_scenarios required field → **+0 markers in SKILL.md** (enforcement lives in `agents/planner.md` template + `agents/dispatcher.md` validation, per agent-local contract)
  - F12 WHEN-NOT-TO-ADD files → **+0 markers** (directory-level guidance, not HARD RULE markers)
  - DR-10 md-only ontological elevation → **+0 markers** (upgrade of existing HARD RULE measurement-method, not a new marker)
  - **Final Claude Code SKILL.md marker count: 18 → 19** (v1.7.2 baseline + 1 v1.8.7 addition)
  - Per-host total: Claude Code = 41 (was 40), Gemini = 37 (was 36), Codex = 37 (was 36)

## v1.10.0 Release Deltas

- **Per-host marker counts UNCHANGED** (Claude Code 41 / Gemini 37 / Codex 37). All v1.10.0 HARD RULEs live in role-local `agents/*.md` or spec-local `references/*.md`, which the count method deliberately excludes:
  - `references/model-dispatch-policy.md` — "No silent fall-through" (judgment-tier work never silently degrades to a weaker model)
  - `agents/dispatcher.md` — §Weak-Model Dispatch Mode + §Flat Fan-Out for Bulk Work (workers never spawn subagents; depth-1 only)
  - `references/multi-window-protocol.md` / `agents/retrospective.md` step 7 — outbox claim discipline (no item survives two consecutive session starts undecided)
  - `agents/archiver.md` — Phase 4 commit scoping (`git add -A` forbidden on a shared vault)
  - `references/maintenance-ledger-spec.md` — overdue = nudge only, never auto-run (3-line hard cap)
- Host files reference these rules without adding literal `HARD RULE` marker lines (hosts/CLAUDE.md model statement, batch-import routing, flat-fan-out reference; hosts/GEMINI.md + hosts/AGENTS.md fallback statements).

## Current Count

Current explicit HARD RULE marker count is counted per active host, as of v1.7.2. Do not add host files together.

| Host | Count | Breakdown |
|------|-------|-----------|
| Claude Code | 41 | `SKILL.md` 19 + `hosts/CLAUDE.md` 20 + `hosts/GLOBAL.md` 2 |
| Gemini CLI / Antigravity | 37 | `SKILL.md` 19 + `hosts/GEMINI.md` 16 + `hosts/GLOBAL.md` 2 |
| OpenAI Codex CLI | 37 | `SKILL.md` 19 + `hosts/AGENTS.md` 16 + `hosts/GLOBAL.md` 2 |

**v1.8.7 update**: `SKILL.md` marker count 18 → 19 due to B4 Self-driven loops with ScheduleWakeup HARD RULE addition. Per-host totals +1 each.

Count method: count lines containing an explicit `HARD RULE` marker in `SKILL.md`, exactly one active host orchestration file, and `hosts/GLOBAL.md`. Security boundaries in `hosts/GLOBAL.md` remain inviolable even when not labeled with the literal phrase `HARD RULE`.

## Maintenance

- Update this index whenever a HARD RULE marker is added, removed, or moved in an authoritative file.
- Keep README language generic and link here instead of repeating the count.
- If host files intentionally diverge, record the per-host delta here before changing release docs.
- Do not count all three host orchestration files together. Do not count role-local `agents/*.md` markers in the top-level per-host table unless this index is explicitly expanded to a full-corpus count.
