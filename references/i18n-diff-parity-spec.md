---
spec_id: i18n-diff-parity-spec.v1
description: Specification for change-line three-language parity verification. When `references/*.md` changes between releases, the corresponding `i18n/zh/references/<same>.md` and `i18n/ja/references/<same>.md` MUST also change in alignment. Enforced as verify-release check #9 (WARN level in v1.8.7, BLOCK target v1.8.8). Eliminates the recurring "EN spec updated but zh/ja drifted" violations from `pro/compliance/violations.md`.
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman AGENTS.md:118-120 (coverage gate on changed lines via diff-cover), pattern adapted from "coverage on diff" to "i18n mirror on diff"
introduced_in: v1.8.7
referenced_by:
  - .claude/commands/verify-release.md (check 9)
  - pro/agents/auditor.md (Mode 7 M7-5)
---

# i18n Diff Parity Specification v1

When EN spec files in `references/*.md` change between two tags (or HEAD vs last tag), the corresponding ZH/JA mirror files MUST also change in matching scope. This spec defines:

1. How "changed scope" is identified
2. How EN ↔ zh / EN ↔ ja correspondence is verified
3. What counts as parity (sufficient) vs drift (failure)
4. WARN vs BLOCK escalation timeline

## Files in scope

All three-mirrored documents:

- `references/*.md` ↔ `i18n/zh/references/*.md` ↔ `i18n/ja/references/*.md`
- `CHANGELOG.md` ↔ `i18n/zh/CHANGELOG.md` ↔ `i18n/ja/CHANGELOG.md`
- `README.md` ↔ `i18n/zh/README.md` ↔ `i18n/ja/README.md`
- `MIGRATION.md` ↔ `i18n/zh/MIGRATION.md` ↔ `i18n/ja/MIGRATION.md` (when present)

**Not in scope** (deliberately):

- `SKILL.md` — single file (theming handles output language)
- `references/hard-rules-index.md` — single file (dev-internal index)
- `pro/gotchas.md` — single file (dev-internal knowledge base)
- `pro/agents/*.md` — single file per agent (themes/ handles display)
- `pro/*.md` (CLAUDE.md / GEMINI.md / AGENTS.md / GLOBAL.md) — host-specific orchestration, not user-facing translations
- `_meta/**/*` — runtime artifacts and RFCs
- `themes/*.md` — theme files use native culture language

## Change identification (section-level)

A "section" is identified by `## ` second-level heading. The diff parity check works section by section:

1. Use `git diff <base>..HEAD -- references/<file>.md` to find changed lines
2. Map each changed line to its enclosing `## ` section by walking backward to nearest `## `
3. Collect unique set of changed sections
4. For each changed section, verify same section also changed in `i18n/zh/references/<file>.md` and `i18n/ja/references/<file>.md`

Section-level granularity (not line-level) is deliberate: word-for-word translation is not required; **substantive content alignment** is.

## Correspondence rules

### Section count parity (HARD)

For any file in scope:

```
count(## sections in EN) == count(## sections in zh) == count(## sections in ja)
```

Drift: one language adding/removing a section without the other two = parity failure.

### Section title alignment (SOFT)

Section titles MAY translate to native language. To support automated cross-reference, encourage (but not enforce in v1.8.7) including an English anchor in translated titles:

- ✅ `## 背景 (Background)` — title translated + English anchor
- ✅ `## 背景` — title translated, no anchor
- ❌ Section reordered such that "third section in EN" ≠ "third section in zh"

If anchor present: cross-reference by anchor.
If no anchor: cross-reference by **section ordinal position** (1st, 2nd, 3rd).

Section reordering across languages breaks ordinal cross-reference and is flagged.

### Changed-section parity (HARD)

If section N in EN file changed in a commit, section N in zh file AND section N in ja file MUST also change in that commit OR the immediately preceding 3 commits (allowing slight timing offset for translation work).

The "3-commit window" tolerance is for cases where EN spec was committed first, then zh + ja translations follow in next 1-2 commits — all within the same logical PR / release.

## Verification implementation (verify-release check 9)

Inside `.claude/commands/verify-release.md` (LLM-driven, since lifeos is md-only — no actual shell script), the check 9 LLM procedure:

1. Determine base tag (previous release tag) and HEAD
2. List all changed files in scope via `git diff --name-only <base>..HEAD -- references/ i18n/zh/references/ i18n/ja/references/ CHANGELOG.md i18n/zh/CHANGELOG.md i18n/ja/CHANGELOG.md README.md i18n/zh/README.md i18n/ja/README.md MIGRATION.md i18n/zh/MIGRATION.md i18n/ja/MIGRATION.md`
3. For each EN file that changed:
   a. Identify changed sections (parse diff for line ranges, walk backward to nearest `## `)
   b. Verify each changed section also has a diff in zh and ja mirrors
   c. Verify section count parity (EN section count == zh count == ja count)
4. Aggregate findings:
   - **PASS**: every changed EN section has matching zh+ja section diff, and counts align
   - **WARN** (v1.8.7 default): some sections drift, but EN file's `referenced_by:` is small / fix can wait
   - **FAIL**: sections drift, especially for HARD RULE-bearing specs

In v1.8.7, output is WARN level regardless of finding severity. v1.8.8 targets escalating major drift to BLOCK.

## WARN vs BLOCK escalation timeline

**v1.8.7 ship** (current): check 9 is WARN. First-run output may be noisy (historical drift); the goal is to surface, not block.

**v1.8.8 target** (4 weeks after v1.8.7 ship): if v1.8.7 WARN output stabilizes (drift types enumerable, false-positive rate <20%), promote check 9 to BLOCK level for the following categories:

- Specs with `authoritative: true` frontmatter (the source-of-truth specs)
- README + CHANGELOG (user-facing docs)
- MIGRATION (user upgrade-critical)

Other lower-stakes drift stays at WARN.

**Permanent WARN**: section ordering issues + minor wording changes that don't affect substantive content.

## Common drift patterns and remedies

### Pattern 1: "I'll translate zh+ja in next PR"

EN spec lands; zh+ja drift open. **Remedy**: PR template requires all three languages or explicit "deferred-to: <PR/issue>" with deadline. Per `references/agent-spec.md` v2, specs need three-language alignment before merge.

### Pattern 2: "Added one section to EN, forgot zh+ja"

Section count diverges. **Remedy**: pre-merge AUDITOR Mode 7 M7-5 catches this. PR can't land until parity restored or explicit `i18n-drift-allowed: <reason>` frontmatter exception.

### Pattern 3: "EN renamed section, mirrors didn't"

Section ordinal alignment breaks. **Remedy**: encourage English anchors `## 背景 (Background)` so renames are detectable by anchor match.

### Pattern 4: "Substantive content rewritten in EN, mirrors only had typo fixes"

Mirror diff exists but is shallow. **Remedy**: check 9 doesn't catch this depth difference automatically — flag manually in PR review until v1.8.8 introduces line-count-ratio heuristic.

## Exceptions

Three legitimate exceptions where parity is NOT required:

1. **English anchor-only adjustments** to translated titles — not a substantive change, mirror diff not required
2. **Translation-only commits** — fixing typos in zh/ja without changing EN — parity is restored by the commit itself, not a violation
3. **`status: legacy` specs** — historical specs marked legacy don't need ongoing parity (their content is frozen)

Exception is documented via frontmatter:

```yaml
i18n_parity_exception: anchor-only|translation-only|legacy
```

AUDITOR Mode 7 M7-5 honors these exceptions.

## Reference

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.3 F11
- Pattern source: `tinyhumansai/openhuman` AGENTS.md:118-120 (coverage on changed lines via diff-cover) — adapted for i18n mirroring
- `pro/compliance/violations.md` — historical drift incidents this spec aims to prevent
