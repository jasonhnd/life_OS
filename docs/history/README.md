# Historical Archive (frozen v1.7-era docs)

This directory holds **frozen historical documentation** — design snapshots and user guides from the v1.7 era that have been superseded but are kept for understanding how the system evolved. Every file here carries `status: legacy` / `authoritative: false`.

**These are NOT current.** The current authority is:

- `pro/CLAUDE.md` (+ `pro/AGENTS.md` / `pro/GEMINI.md`) — orchestration protocol
- `pro/agents/*.md` — subagent definitions
- `references/*.md` — current data model + specs
- everything in `docs/` **outside** `history/` — current user docs

## Contents

- **`architecture/`** — v1.7-era architecture snapshots (the 4-layer design, the 16-agent listing, orchestration protocol, workflow state machine, information isolation, HARD-RULE catalog, multi-platform orchestration, cognitive pipeline, system overview, roadmap, v1.7 spec map). The Layer 3 bash-hook layer and Layer 4 Python-tools layer described here were **retired in v1.8.x**; runtime enforcement is now inline LLM (host-agnostic).
- **`cortex/`** — v1.7 Cortex user guides (the always-on design). Cortex became **pull-based in v1.8.0** (current behavior: `pro/CLAUDE.md` §0.5). zh/ja mirrors live at `i18n/{zh,ja}/docs/history/cortex/`.
- **`v1.7-migration.md`** — migration guide to v1.7 (superseded by `docs/guides/cross-version-migration.md`).
- **`v1.7-shipping-report-2026-04-21.md`** — one-time v1.7 shipping report.

## Why these still exist (instead of being deleted)

Git history already preserves every deleted file, so nothing is *lost* by deletion. These are kept browsable as a single consolidated archive so the v1.7 design rationale stays readable without `git show`.

> **Inbound-link note:** Frozen records — CHANGELOG entries, `pro/compliance/*`, `_meta/rfc/*` — intentionally still reference the *original* pre-move paths (e.g. `docs/architecture/...`). They are historical records of what the paths were at the time and are deliberately **not** rewritten. Active docs and specs link here at the new `docs/history/...` paths.
