<!--
=============================================================================
gotchas.md — lifeos project-level technical gotcha knowledge base
=============================================================================

Format spec: references/gotchas-spec.md
Sole writer: agents/memory-keeper.md (do NOT hand-edit; bypasses dedup)
Invoked from: agents/archiver.md wrap-up phase 5

Initial seed populated by memory-keeper in seed mode during v1.8.7 release session.
Sources scanned: _meta/rfc/v1.8.5-cleanup-and-hardening.md /
v1.8.7-openhuman-borrowed-patterns.md / v1.9-second-brain-structure-optimization.md / compliance/violations.md
(technical-root-cause subset).

Subsequent updates: archiver Phase 5 invokes memory-keeper after every Adjourn.
=============================================================================
-->

# Project Gotchas

> Last updated: v1.8.7 release session (seed mode). Total entries: 14.

## archiver

- **archiver wrap-up phase 5 is mandatory after v1.8.7** — Skipping phase 5 = missing gotchas extraction. archiver Mode 0 enforces phase 5 even on short sessions; gotchas table can be empty but phase MUST run. Fix: never split adjourn flow across messages. (#RFC-v1.8.7 §2.1 C6)

- **archiver.md adjourn report contract is now 7-H2 not 6-H2 (v1.8.7)** — Previous spec said "6 core H2 headings"; v1.8.7 added Phase 5 (memory-keeper). Missing Phase 5 H2 in adjourn report = `Class C-brief-incomplete` per AUDITOR Mode 3. Fix: see `agents/archiver.md` §"Adjourn Report Completeness Contract". (#RFC-v1.8.7 §2.1)

- **archiver Phase 4 reports "pushed" when git push actually failed (silent failure F8)** — Fix: archiver MUST NOT claim push success when `git push` failed (offline / no remote); annotate "⚠️ not pushed — syncs next session" and keep the commit local. See `agents/archiver.md` failure_modes. (#v1.7-era fix)

- **`compliance/violations.md` is auditor's domain — memory-keeper NEVER writes there** — Cross-domain capture violation. Gotchas (technical) vs violations (process) are different stores. memory-keeper writes ONLY `gotchas.md`. (#v1.8.7 gotchas-spec.md)

## retrospective

- **COURT-START-001 (2026-04-19): ROUTER must launch retrospective subagent, NOT simulate 18 steps in main context** — Historical violation. Root cause: ROUTER pattern-matched on trigger word but skipped Task() launch. Fix: 5-layer defense in v1.6.3 (hook + Pre-flight + subagent self-check + AUDITOR Mode 3 + regression test). See `compliance/2026-04-19-court-start-violation.md`. (#v1.6.3 fix · COURT-START-001)

- **Retrospective Mode 0 Step 0.5 `[Wiki count: measured]` / `[Sessions count: measured]` markers required** — Without markers, ROUTER cannot fact-check numeric claims; subagent may confabulate. Fix: retrospective subagent MUST include literal marker strings; ROUTER refuses to show briefing missing them. (#v1.7.0.1 R5 anti-confabulation)

## verify-release

- **`git push --tags` does NOT auto-create GitHub Release** — Pushing tag is git-layer only; GitHub Release is separate layer requiring `gh release create`. Without explicit publish, Releases page Latest badge stays frozen on previous version (e.g. v1.7.3 visible after v1.8.0 tag pushed). Fix: full sequence per SKILL.md HARD RULE — push main → tag → push tag → `gh release create --latest` → verify-release script. (#v1.8.0 R-1.8.0-019)

- **Force-moving a git tag breaks the bound GitHub Release** — When tag is deleted+recreated to point to a new sha, GitHub Release becomes orphaned: `isDraft: true`, `url: untagged-<id>`, no longer findable by tag. Fix: delete the orphan Release then recreate with `gh release create v<X.Y.Z> --notes-file ... --latest`. Tag re-pointing without release recreate = release breakage. (#v1.8.7 ship session, this RFC)

- **v1.8.7 verify-release expanded from 9 to 11 checks** — Old check 9 (regression fixtures FAIL) renumbered to check 11; new check 9 = i18n diff parity (WARN), new check 10 = diff-scoped forbidden extensions. Scripts/docs referencing "check 9" by number alone need v1.8.7 audit. (#RFC-v1.8.7 §2.3 F11)

## md-only enforcement

- **v1.8.6 → v1.8.7: md-only is now ontological constraint, no escape hatch** — v1.8.5/v1.8.6 banned `.py/.sh/.yml/.json`; v1.8.7 adds `.sql/.db/.sqlite` and elevates the rule to *definitional* — no future RFC may relax it. Borrowing OpenHuman patterns means borrowing the *pattern*, never the *implementation tech stack*. Fix: see `SKILL.md` "md-only ontological constraint" HARD RULE + DR-10. (#RFC-v1.8.7 DR-10)

- **`.claude/settings.json` is gitignored — NOT a md-only violation** — Claude Code platform requires it; lifeos repo HARD RULE does not apply to gitignored platform-required files. Don't try to "fix" this file's presence on disk. (#v1.8.5/v1.8.6 expansion rationale)

- **`meta/` is gitignored — use `git add -f` for tracked files inside** — Adding new RFC or release-notes to `meta/` needs `git add -f meta/rfc/<new>.md` because `.gitignore:39` blanket-ignores `meta/`. Existing tracked files (v1.8.5 RFC etc.) survive because git already tracks them, but new files default to ignored. (#v1.8.7 ship session)

## i18n + three-language sync

- **EN spec changes without zh/ja mirror updates = recurring violation class** — v1.8.7 adds verify-release check 9 (i18n diff parity, WARN) to catch this systematically. Pattern: dev updates `references/<spec>.md`, forgets `i18n/zh/references/<same>.md` and `i18n/ja/references/<same>.md`. Fix: every spec change must update three files; v1.8.8 escalates this from WARN to BLOCK. (#RFC-v1.8.7 §2.3 F11)

- **Section count parity is HARD across three languages, title translation is SOFT** — `count(## EN) == count(## zh) == count(## ja)` is required; title text may translate to native language. Section ordering must match (1st in EN = 1st in zh = 1st in ja). Anchor pattern `## 背景 (Background)` recommended for rename-safe cross-reference. (#v1.8.7 i18n-diff-parity-spec)
