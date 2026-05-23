---
spec_id: changelog.v1
description: CHANGELOG.md entry schema v1 (effective v1.8.5+). Borrows ECP YAML frontmatter pattern from eou-foundry — every release entry has structured YAML frontmatter (version, breaking_changes, alternatives_considered, ordering_dependency, regression_cases_added) plus markdown body for narrative release notes. Pre-v1.8.5 entries remain narrative-only (legacy).
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, self-evolution/ecp/ YAML schema
introduced_in: v1.8.5
---

# CHANGELOG Specification v1

CHANGELOG.md entries from v1.8.5 onwards have structured YAML frontmatter followed by markdown body. Pre-v1.8.5 entries are narrative-only and remain unchanged (legacy).

## Why structured frontmatter

v1.8.4 CHANGELOG entries are narrative — useful for humans but not machine-parseable. Three problems eou-foundry helped surface:

1. **No alternatives_considered**: entries record what was done, not what was considered and rejected. "Why we didn't do X" is lost history.
2. **No ordering_dependency**: cohort releases (e.g. ECPs 0015-0017 must land together) had no explicit declaration. Cherry-picking caused issues.
3. **No regression_cases_added**: link from "we fixed this" to "we added a regression test to prevent recurrence" was implicit and often missing.

v1.8.5+ schema fixes these.

## v1.8.5+ Entry Schema

```markdown
---
version: 1.8.5
date: 2026-07-15
type: major | minor | patch
breaking_changes:                          # bullet list
  - "SOUL.md schema v1 → v2 (X-over-Y formulation required)"
  - "wiki entry schema v1 → v2 (outlier slot required for active+)"
  - "21 agent frontmatter v1 → v2 (authority_level / blast_radius required)"
new_features:                              # bullet list
  - "F1-F17 failure taxonomy added (references/failure-taxonomy.md)"
  - "..."
fixes:                                     # bullet list
  - "..."

# REQUIRED v1.8.5+: at least 1 rejected option with reason
alternatives_considered:
  - option: "Stay on v1.8, ship these as 30 minor patches over 6 months"
    rejected_because: "30 separate releases = 30 migration paths; user wants one upgrade"
  - option: "Keep narrative CHANGELOG (no YAML frontmatter)"
    rejected_because: "Lose grep-ability + cohort dependency tracking"

# REQUIRED v1.8.5+: cross-release dependency declaration
ordering_dependency:
  blocked_by: []                           # SHAs / version refs that must land first
  must_coexist_with:                       # other commits/refs that must ship together
    - Stage 0 (failure-taxonomy + refactoring-patterns)
    - Stage 1 (SOUL v2)
    - Stage 2 (wiki v2)
    # ... etc

# REQUIRED v1.8.5+: regression cases added in this release
regression_cases_added:
  - rc-soul-no-priority
  - rc-soul-no-outlier
  - rc-soul-strawman-y
  - rc-wiki-no-outlier
  - rc-wiki-no-hypothesis
  - rc-agent-no-authority
  - rc-agent-blast-radius-violation
---

## v1.8.5 — Hook Retirement + EOU Hardening · 2026-07-15

> 1-paragraph summary of the release.

### Highlights

- Bullet list of user-visible highlights
- ...

### Migration

- How users upgrade from previous version
- Slash commands to run (e.g. `/migrate-soul-v2`)
- Backward compatibility notes (12-month legacy coexistence per D3)

### Acknowledgments / context

- (optional narrative section)
```

## Required YAML fields (v1.8.5+)

For every release entry from v1.8.5 onwards:

1. **version**: semver string, e.g. `"1.8.5"`
2. **date**: ISO YYYY-MM-DD
3. **type**: one of `major | minor | patch | prerelease`
4. **breaking_changes**: array (may be empty for non-breaking releases; required field even when empty)
5. **alternatives_considered**: ≥1 entry with `option` + `rejected_because`. "We considered nothing else" is not a valid value.
6. **ordering_dependency**: `blocked_by` array + `must_coexist_with` array (may be empty for standalone patches)
7. **regression_cases_added**: array of `rc-*` ids (may be empty if no regression cases added, but should be reviewed — most fixes warrant regression coverage)

`new_features` and `fixes` are recommended but not required.

## Validation

AUDITOR Mode 7 (added in Stage 10, planned for v1.8.5 release) will validate:
- Every release entry from v1.8.5+ has all 7 required fields
- `alternatives_considered` has ≥1 substantive entry (LLM heuristic: rejected_because ≥20 chars + non-trivial)
- `ordering_dependency.must_coexist_with` references resolve to actual commits/PRs/Stages
- `regression_cases_added` references exist in `evals/regression-fixtures/`

## Legacy entries (pre-v1.8.5)

CHANGELOG entries before v1.8.5 (v1.0.0 through v1.8.4) remain narrative-only. No retroactive migration required. The schema applies to v1.8.5 entry forward.

## Three-language sync

Per HARD RULE `三语文档同步`, the YAML frontmatter schema applies to all 3 CHANGELOG files:
- `CHANGELOG.md` (EN)
- `i18n/zh/CHANGELOG.md` (ZH)
- `i18n/ja/CHANGELOG.md` (JA)

All 3 must have the same v1.8.5+ entry with same YAML frontmatter (translated body but identical structured fields).

## Source attribution

eou-foundry @ e4b12ce — `self-evolution/ecp/*.yml` YAML schema (every ECP has id / target_eou / target_version_from / target_version_to / problem / proposed_change / alternatives_considered / ordering_dependency). Adapted for life_OS CHANGELOG (release-level vs ECP-level): simplified to 7 fields, kept the 3 most-critical (alternatives_considered / ordering_dependency / regression_cases_added).
