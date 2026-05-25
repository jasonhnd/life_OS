# WHEN NOT TO ADD to `_meta/`

> **Intentionally near-empty principle**: this directory is for **runtime artifacts** + **historical snapshots** + **RFC documents**. It is the system's working memory, NOT a place for canonical specs or agent definitions.

## What does NOT belong here

1. **Canonical specifications** — e.g. "definition of how audit trails work". → Goes to: `references/<name>-spec.md` (with three-language mirror).
2. **Agent definitions** — those are `pro/agents/` exclusive.
3. **User decisions or knowledge** — e.g. "my decision to use trust structure". → Goes to (in user's second-brain): `decisions/` or `_meta/wiki/`.
4. **SOUL.md or theme files** — SOUL goes to user's second-brain root; themes go to `themes/`.
5. **Build outputs / compiled artifacts** — lifeos has no build step (md-only). If you find yourself wanting to add `_meta/dist/` or `_meta/build/`, you're solving the wrong problem.
6. **Anything matching forbidden_extensions** — `.sql / .json / .sh / .bash / .py / .yml / .yaml / .db / .sqlite` (see `SKILL.md` md-only ontological constraint). Per DR-10 v1.8.7, this is non-negotiable.

## What DOES belong here

- `_meta/runtime/<sid>/*.md` — per-session audit trails (R12 + R13 schema)
- `_meta/rfc/v<X.Y>-*.md` — RFC documents for releases
- `_meta/sessions/<sid>.md` — per-session archives
- `_meta/wiki/` — user's knowledge base (in user's second-brain, not dev repo)
- `_meta/concepts/` — Cortex synaptic graph (in user's second-brain)
- `_meta/snapshots/soul/<sid>.md` — SOUL snapshots at adjourn
- `_meta/journal/` — DREAM reports
- `_meta/outbox/<sid>/` — pending writes before git sync
- `_meta/compression/<sid>-compress-<ts>.md` — manual `/compress` outputs
- `_meta/release-notes/v<X.Y>.md` — release notes
- `_meta/incidents/<id>.md` — incident decision records (`no-change` etc.)

## Dev-repo vs user-second-brain distinction

The lifeos **dev repo** `_meta/` contains: `rfc/` + `release-notes/` + `methods/` + historical `v1.8.4-snapshot/`. It does NOT contain `sessions/` / `concepts/` / `wiki/` — those exist only in users' second-brains at runtime.

When writing a new spec or feature that touches `_meta/`, clarify whether the path lives in:
- **dev repo** `_meta/` (the lifeos source code) — examples: `_meta/rfc/`, `_meta/release-notes/`
- **user's second-brain** `_meta/` (the user's running data) — examples: `_meta/sessions/`, `_meta/runtime/`, `_meta/wiki/`

Confusion between these two is a recurring gotcha (see `pro/gotchas.md` once seeded).

## Reference

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- Pattern source: `tinyhumansai/openhuman` `.claude/rules/README.md`
- Companion: `SKILL.md` HARD RULE md-only ontological constraint (DR-10)
