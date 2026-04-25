# HARD RULES Index

This index is the public pointer for non-overridable Life OS behavior. README files must link here instead of embedding a hard-coded rule count.

## Source Of Truth

- `SKILL.md`: universal system contract, theme-language rule, trigger templates, ROUTER fact-checking, session binding, pre-session display, adjourn behavior, and router code of conduct.
- `pro/{CLAUDE,GEMINI,AGENTS}.md`: host-specific orchestration contracts. Use the file for the active host; do not add the three host copies together.
- `pro/GLOBAL.md`: universal agent behavior, including research-process display and progress reporting.

## Current Count

Current explicit HARD RULE marker count is counted per active host. Do not add host files together.

| Host | Count | Breakdown |
|------|-------|-----------|
| Claude Code | 34 | `SKILL.md` 15 + `pro/CLAUDE.md` 17 + `pro/GLOBAL.md` 2 |
| Gemini CLI / Antigravity | 33 | `SKILL.md` 15 + `pro/GEMINI.md` 16 + `pro/GLOBAL.md` 2 |
| OpenAI Codex CLI | 33 | `SKILL.md` 15 + `pro/AGENTS.md` 16 + `pro/GLOBAL.md` 2 |

Count method: count explicit `HARD RULE` markers in `SKILL.md`, exactly one active host orchestration file, and `pro/GLOBAL.md`. Security boundaries in `pro/GLOBAL.md` remain inviolable even when not labeled with the literal phrase `HARD RULE`.

## Maintenance

- Update this index whenever a HARD RULE marker is added, removed, or moved in an authoritative file.
- Keep README language generic and link here instead of repeating the count.
- If host files intentionally diverge, record the per-host delta here before changing release docs.
