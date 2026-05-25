# WHEN NOT TO ADD to `references/`

> **Intentionally near-empty principle**: this directory is for **canonical specifications** (`*-spec.md`) and **shared reference tables** (e.g. `domains.md`, `failure-taxonomy.md`). It is NOT a dumping ground for "any document I want agents to read".

## What does NOT belong here

1. **Per-session reports, runtime artifacts, audit trails** — e.g. "the 2026-05-25 archiver output". → Goes to: `_meta/runtime/<sid>/` or `_meta/sessions/<sid>.md`.
2. **User-facing tutorials or quickstarts** — e.g. "how to install lifeos". → Goes to: `README.md` / `docs/` / `gitbooks/`.
3. **Internal design notes / brainstorms / drafts** — e.g. "ideas for v2.0 cascade seal". → Goes to: `_meta/rfc/v<X.Y>-*.md` (RFC) or `_meta/workpad/` (if introduced).
4. **Agent definitions or theme files** — those are `pro/agents/` and `themes/` exclusive territory.
5. **Pure narrative without normative content** — e.g. "history of lifeos versions". → Goes to: `CHANGELOG.md` / RFC bibliography.
6. **Spec without three-language mirror** — every `references/*-spec.md` MUST have `i18n/zh/references/<same>.md` and `i18n/ja/references/<same>.md` ready before merge. No partial spec.
7. **Spec without `spec_id` / `status` / `authoritative` frontmatter** — see existing spec files for the required schema.

## What DOES belong here

A canonical specification that:
- Defines a schema, format, or contract that ≥2 agents will reference
- Has `spec_id: <name>.v<N>`, `status: active|legacy|proposal`, `authoritative: true|false`, `introduced_in: v<X.Y>` frontmatter
- Has three-language mirror ready (`i18n/zh/references/` + `i18n/ja/references/`)
- Will be referenced by `referenced_by:` (forward-link from at least one agent / command / SKILL.md)
- Is the **single source of truth** for its topic (no duplicate spec elsewhere)

## Before adding a new spec — Minimality Rule check

Per `pro/CLAUDE.md` Minimality Rule (v1.8.5 Stage 7), ask the 6 questions first:

1. Could a **rule** (in `pro/CLAUDE.md` or SKILL.md) accomplish this?
2. Could a **schema field** in an existing spec accomplish this?
3. Could a **section in an existing spec** accomplish this?
4. Could a **regression case** (`evals/scenarios/*.md`) accomplish this?
5. Could **AUDITOR audit rule** accomplish this?
6. Could a **human checklist** in `pro/CLAUDE.md` accomplish this?

If ANY answer is yes, prefer that lower-cost option. New spec = three files (EN + zh + ja) + permanent referenced_by graph maintenance + i18n diff parity check obligation.

## Reference

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- Pattern source: `tinyhumansai/openhuman` `.claude/rules/README.md`
- Companion: `references/i18n-diff-parity-spec.md` (v1.8.7 ensures three-language alignment for everything here)
