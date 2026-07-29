---
description: Convert a historical compliance/violations.md row into an evals/regression-fixtures/rc-*.md fixture (markdown with YAML frontmatter — no .yml per the md-only ontological constraint). Lazy alternative to bulk historic-row conversion (per Stage 9 D7 default). Use when a recurring violation pattern emerges (3+ similar rows) and you want regression test coverage.
argument-hint: "<violation-row-id-or-timestamp>"
allowed-tools:
  - Read
  - Write
  - Grep
  - AskUserQuestion
---

# /regression-from-violation

Convert a specific row in `compliance/violations.md` into a markdown regression fixture (YAML frontmatter + body) under `evals/regression-fixtures/rc-<descriptor>.md`. 17 regression fixtures currently ship (4 F-class + 4 forbidden-extension + 9 schema/process); remaining historical rows use this slash command for lazy conversion as patterns recur. (Fixtures were `.yml` until v1.8.5 Stage 9 / v1.8.6; the md-only ontological constraint / DR-10 forbids `.yml`, so fixtures are now `.md`.)

## Procedure

### 1. Locate the violation row
```bash
grep -nE "<timestamp-or-keyword>" compliance/violations.md
```
If multiple matches → ask user which row via AskUserQuestion.

### 2. Parse the row
For v1.8.4 legacy format (6 cols): `| Timestamp | Trigger | Type | Severity | Details | Resolved |`
For v1.8.5+ format (7 cols): `| Timestamp | Trigger | Type | F-Code | Severity | Details | Resolved |`

Extract:
- `timestamp`
- `trigger` (e.g. "上朝", "Adjourn", "git sync")
- `type` (A1/A2/A3/B/C/D/E/F)
- `f_code` (F1-F17; for legacy, infer per "A-F → F-Code Typical Mappings" table in violations.md)
- `severity` (P0/P1/P2)
- `details` (free text describing what happened)

### 3. Generate fixture
Slug: `rc-<lowercase-descriptor>-<3-digit-sequence>.md`
- e.g. `rc-archiver-placeholder-001.md` for an archiver placeholder violation
- e.g. `rc-three-lang-sync-miss-002.md` for second occurrence of 三语 sync miss

Use this template — a **markdown file with YAML frontmatter** (matching the shipped `rc-*.md` fixtures; no `.yml` per the md-only ontological constraint / DR-10). Fill from the parsed row:

```markdown
---
id: rc-<descriptor>-<N>
expected_verdict: FAIL
expected_failure_class: <F1-F17 from row>
expected_check: <which AUDITOR Mode or slash command should catch this>
introduced_in: v1.8.5 Stage 9 (lazy conversion)
related_spec: <links to relevant references/*.md or hosts/CLAUDE.md sections>
input_scenario:
  trigger: <trigger>
  actual_behavior: <what went wrong, paraphrased from Details>
  expected_behavior: <what should have happened>
---

# rc-<descriptor>-<N>

## Description
Historic regression converted from compliance/violations.md row dated <timestamp>.
Original violation: <details>
Pattern recurrence count: <K> times in last 90 days (run AUDITOR Mode 3 to refresh).

## Expected finding
<F-Code> <FAILURE_CLASS>: <human-readable summary>
Severity: <P0/P1/P2>
Defense layers that should catch:
- Layer 2 (orchestration enforcement): <relevant SKILL.md / hosts/CLAUDE.md rule>
- Layer 3 (subagent self-check): <relevant agent's frontmatter failure_modes>
- Layer 4 (post-hoc audit): AUDITOR Mode <N> scenario
- Layer 5 (regression test): this file

## Historic context
Original violation row: compliance/violations.md (timestamp <timestamp>)
Incident dossier (if exists): compliance/<incident-file>.md
```

### 4. Write fixture file via Write tool
### 5. Update INDEX (optional)
If `evals/regression-fixtures/INDEX.md` exists, append the new fixture id + 1-line summary.

### 6. Verify
Run `/run-regression rc-<new-fixture-name>` (when implemented) to confirm the new fixture FAILS as expected.

## When to invoke

- **Pattern detection trigger**: AUDITOR Mode 3 reports same violation class ≥3 times in 30 days → recommend `/regression-from-violation <latest-row>` to add coverage.
- **Manual review**: User scanning violations.md and spots a pattern worth preventing.
- **Post-incident**: After resolving a CRITICAL violation, convert to regression to prevent recurrence (F12 DRIFT defense).

## Source attribution

Inspired by eou-foundry `self-evolution/regression/cases/` pattern (rc-f14-* / rc-f15-* / rc-f16-* / rc-f17-* — fixtures generated from F14-F17 incident taxonomy). Adapted for life_OS lazy-conversion model (D7 — 17 fixtures critical-only at ship; remaining via slash command as patterns emerge).
