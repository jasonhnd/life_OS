---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# Compliance Violation Log Specification

> Formal specification for the dual-repo violation logging mechanism introduced in v1.6.3 as part of COURT-START-001 fix.

## Purpose

Persist HARD RULE violations as markdown + git, not in `~/.claude/` private storage. Enables:

- **Cross-device auditability** — violations follow user to any machine via GitHub
- **Zero dependency on LLM's private memory** — works for any user who clones the repo, not only the developer with specific `~/.claude/projects/*/memory/` entries
- **AUDITOR can read historical patterns and escalate** — the rule is in the file, not in an LLM's recollection
- **Eval scenarios can assert** "this violation was caught and logged"

## Dual-Repo Strategy

Violations are written to different paths depending on which repo type is detected at runtime:

| Context | Path | Who writes |
|---------|------|-----------|
| Life OS dev repo (`pro/agents/retrospective.md` exists) | `pro/compliance/violations.md` | Hooks + AUDITOR in dev repo |
| User second-brain (`_meta/config.md` exists) | `_meta/compliance/violations.md` | Hooks + AUDITOR in user repo |
| Other (generic project) | *no log* | N/A (violations not recorded) |

### Path resolution logic

Used by `scripts/lifeos-pre-prompt-guard.sh` and AUDITOR's Compliance Patrol Mode:

```bash
if [ -f "./pro/agents/retrospective.md" ]; then
  LOG="./pro/compliance/violations.md"
elif [ -f "./_meta/config.md" ]; then
  LOG="./_meta/compliance/violations.md"
else
  LOG=""  # skip logging in non-Life-OS contexts
fi
```

**Rationale for two paths (not one)**:
- Dev repo violations are about *product bugs* — they should be public via GitHub so other users can see fix history
- User repo violations are about *individual usage patterns* — they stay in the user's private second-brain
- Same format, different privacy scope

## Entry Format

Each violation is one row in a markdown table:

```
| Timestamp (ISO 8601) | Trigger | Type | Severity | Details | Resolved |
```

### Fields

- **Timestamp** (required): ISO 8601 with timezone, e.g. `2026-04-19T22:47+09:00`
- **Trigger** (required): the user word that initiated the sequence (`上朝`, `start`, `退朝`, `閣議開始`, etc.)
- **Type** (required): one of the classified codes (see Taxonomy below)
- **Severity** (required): `P0` / `P1` / `P2`
- **Details** (required): one-sentence description + evidence marker (grep output, tool call ID, specific quote from transcript)
- **Resolved** (required): `false` / `partial` / `true`

### Type Taxonomy

Active Type Legend (v1.7.2.1): A1, A2, A3, B, C, D, E.

Default P0 classes: A1, B, C, E. Default P1 classes: A2, A3, D. No active P2 class in v1.7.2.1.

Deprecated v1.7.2.1 subclasses remain documented below only for old evals, incident archaeology, and compatibility scenarios in `scripts/lifeos-compliance-check.sh`. They MUST NOT be written as active Mode 3 violation types: B-fabricate-fact, B-fabricate-toolcall, B-source-drift, B-source-stale, B-stale, B-trail-mismatch, C-step-skipped, C-brief-incomplete, C-fresh-skip, C-no-audit-trail, C-trail-incomplete, C-banner-missing, C-output-suppressed, C-translation-drift, C-toctou-frame-md, F, CX1, CX2, CX3, CX4, CX5, CX6, CX7.

| Type | Name | Definition |
|------|------|------------|
| **A1** | Skip subagent | ROUTER simulated subagent's work in main context instead of `Task(agent)` call |
| **A2** | Skip directory check | In dev repo, retrospective Mode 0 Step 2 (DIRECTORY TYPE CHECK) bypassed |
| **A3** | Skip Pre-flight check | ROUTER's first response after trigger did not contain the `🌅 Trigger: …` line (v1.6.3 new) |
| **B** | Fabricate fact | Referenced non-existent path / section / process / escape route as authority |
| **C** | Incomplete Phase | archiver exited before all 4 phases (stopped mid-execution) |
| **D** | Placeholder value | Completion Checklist contained `TBD`, empty field, or literal `{...}` |
| **E** | Main-context Phase execution | ROUTER executed archiver's Phase 1/2/3/4 logic in main context |

### Deprecated subclass: B-fabricate-fact (R8; not active v1.7.2.1)

- **Definition**: A concrete factual claim, path, process, count, or authority is presented as real without source evidence, and the claim is not limited to a tool-call claim.
- **Detection**: AUDITOR Mode 3 runs `bash scripts/lifeos-compliance-check.sh <transcript> fabricate-path-check` and validates quoted paths plus known fabricated escape routes against repository files and primary-source evidence.
- **Logged fields**: `Type=B-fabricate-fact`; `Severity=P0`; `claim: <literal>`; `expected_source: <path/tool>`; `evidence: <grep/stdout>`.
- **Escalation**: Inherits Class B standard ladder (`>=3/30d` -> Compliance Watch).

### Deprecated subclass: B-fabricate-toolcall (R5; not active v1.7.2.1)

- **Definition**: Subagent claims a tool call result (success or failure) without the corresponding tool call appearing in transcript.
- **Detection**: Deprecated. The old checker may observe Step 8 evidence markers and confabulation wording patterns, but active Mode 3 uses only `version-markers`.
- **Logged fields**: Deprecated. Normalize any active production finding to core `B` or `C`.
- **Escalation**: Deprecated. Inherits no active ladder in v1.7.2.1.
- **Why introduced**: 2026-04-25 Jason 测试机实测 retrospective subagent 虚构 "private repo" 借口掩盖 Step 8 未执行,触发 v1.7.0.1 R5 anti-confabulation patch.
- **Confabulation observation patterns**: private repo / private 仓库; WebFetch 失败 / WebFetch failed; 网络问题 / network unavailable; 权限问题 / 401 / 403; curl 失败. These are manual review hints only.

### Deprecated subclass: B-source-drift (not active v1.7.2.1)

- **Definition**: Primary-source measured count and INDEX count differ by `|delta| >= 3`, but the briefing omits literal `⚠️ DRIFT` or rationalizes the mismatch as consistent.
- **Detection**: AUDITOR Mode 3 compares briefing primary-source markers (`[Wiki count: measured`, `[Sessions count: measured`, `[Concepts count: measured`) against corresponding INDEX values using Bash stdout.
- **Logged fields**: `Type=B-source-drift`; `Severity=P1`; `measured: <number>`; `index: <number>`; `drift: <measured-index>`; `marker: <literal marker line>`; `Details` must include concrete grep/stdout evidence.
- **Escalation**: Inherits Class B standard ladder (`>=3/30d` -> Compliance Watch).

### Deprecated subclass: B-source-stale (not active v1.7.2.1)

- **Definition**: `STATUS.md` is `>=7` days stale, but the briefing still quotes numeric claims from `STATUS.md`.
- **Detection**: AUDITOR Mode 3 checks `[STATUS staleness:` marker and verifies whether stale STATUS-derived numeric claims appear in the briefing.
- **Logged fields**: `Type=B-source-stale`; `Severity=P1`; `status_days: <integer>`; `quoted_claim: <numeric claim text>`; `source: <STATUS.md path or marker>`; `Details` must include concrete grep/stdout evidence.
- **Escalation**: Inherits Class B standard ladder (`>=3/30d` -> Compliance Watch).

### Deprecated subclass: B-stale (R8; not active v1.7.2.1)

- **Definition**: A numeric claim (`N items`, `K days`, percentages, counts, version counts, etc.) appears in briefing, STATUS, or Summary output without a primary-source measurement record in the transcript.
- **Detection**: AUDITOR Mode 3 runs `bash scripts/lifeos-compliance-check.sh <briefing> numeric-stale` and requires `find`/`wc`, `git log`, `ls`, explicit `measured`, or equivalent primary-source evidence for numeric claims.
- **Logged fields**: `Type=B-stale`; `Severity=P1`; `claimed: <literal numeric claim>`; `missing_source: <expected primary source>`; `evidence: <grep/stdout>`.
- **Escalation**: Inherits Class B standard ladder (`>=3/30d` -> Compliance Watch).

### Deprecated subclass: B-trail-mismatch (R11; not active v1.7.2.1)

- **Definition**: Runtime audit trail content contradicts the ROUTER-pasted summary.
- **Detection**: AUDITOR compares `output_summary` and other trail fields against the corresponding ROUTER markers pasted into the briefing or summary.
- **Logged fields**: `Type=B-trail-mismatch`; `Severity=P1`; `trail_file: <path>`; `mismatch_field: <field>`; `trail_value: <value>`; `router_value: <value>`.
- **Escalation**: Class B standard ladder (`>=3/30d` -> Compliance Watch).

### Deprecated subclass: C-brief-incomplete (not active v1.7.2.1)

- **Definition**: Start Session reached final briefing output, but the briefing omitted one or more mandatory fixed-position sections or required evidence fields. This is a Class C subclass for incomplete briefing composition; it does not change base Class C semantics, which remain archiver incomplete-phase failures.
- **Detection**: After `retrospective` Mode 0 returns, scan the transcript for the Start Session output contract using the locked heading array. Retrospective required H2s: [`## 0. ${RETRO_NAME} · 上朝准备(含 hook 健康 + 版本核查 + Cortex 状态)`, `## 1. 二脑同步状态`, `## 2. SOUL Health 报告`, `## 3. 18 步执行(自然输出,不强制 marker)`, `## 4. 御史台巡查(AUDITOR Mode 3)`, `## 5. 待陛下圣裁`]. Heading 0 matches the active theme's retrospective display name in the `${RETRO_NAME}` slot. Archiver required H2s exactly: [`## Phase 1 · Outbox`, `## Phase 2 · Wiki Extraction`, `## Phase 3 · DREAM Triggers`, `## Phase 4 · Git Sync`, `## Completion Checklist`]. Log `C-brief-incomplete` when the briefing omits any locked heading, omits required evidence fields, or leaves a required block unavailable without explicitly marking it empty/unavailable.
- **Logged fields**: `Type=C-brief-incomplete`; `Severity=P1`; `required_headings.retrospective: [`## 0. ${RETRO_NAME} · 上朝准备(含 hook 健康 + 版本核查 + Cortex 状态)`, `## 1. 二脑同步状态`, `## 2. SOUL Health 报告`, `## 3. 18 步执行(自然输出,不强制 marker)`, `## 4. 御史台巡查(AUDITOR Mode 3)`, `## 5. 待陛下圣裁`]`; `required_headings.archiver: [`## Phase 1 · Outbox`, `## Phase 2 · Wiki Extraction`, `## Phase 3 · DREAM Triggers`, `## Phase 4 · Git Sync`, `## Completion Checklist`]`; `missing_headings: <comma-separated list of missing literal headings>`; `Details` must include a concrete evidence marker (grep output, transcript quote, or tool-call ID) and state that the run reached final briefing output; `Resolved=false` until the briefing contract fix ships and passes regression.
- **Escalation**: Inherits the Class C standard ladder as its own type (`C-brief-incomplete`). It does not count toward base `C` archiver-incomplete thresholds.

### Retired subclass: C-step-skipped (R10; deprecated v1.7.2.1, fully retired v1.8.0 R-1.8.0-011)

- **v1.8.0 status (Round-7 audit fix)**: This subclass is RETIRED. The
  underlying script `scripts/retrospective-mode-0.sh` was deleted in the
  R-1.8.0-011 Option A pivot — retrospective now executes all 18 Mode 0
  steps inline, so there is no pre-fetch path that could be "skipped".
- **Equivalent v1.8.0 violation**: missing-step compliance is now caught
  by `briefing-completeness` (existing C class) — if retrospective bails
  before producing the 6 H2 sections + version markers + Cortex status,
  the existing `briefing-completeness` check fires.
- **Historical definition (kept for archive readers)**: ROUTER did not
  run `retrospective-mode-0.sh`, or runtime/router evidence showed the
  pre-fetched Mode 0 path was skipped before briefing assembly. AUDITOR
  no longer emits `Type=C-step-skipped` in v1.8.0.

### Deprecated subclass: C-fresh-skip (R12; not active v1.7.2.1)

- **Definition**: A session contains multiple Start Session triggers, but a later trigger reuses, summarizes, or skips prior Mode 0 work instead of performing a fresh full execution.
- **Detection**: Deprecated. The old checker may run `fresh-invocation`, but active Mode 3 does not call it by default.
- **Reuse wording observation patterns**: `如上次`; `参考上次`; `previously reported`; `as before`; `unchanged from last`; `see Mode 0 output above`; `skip step.*already done`. These are manual review hints only.
- **Logged fields**: Deprecated. Normalize any active production finding to core `C`; if phrase matches are relevant, include them as `reuse_wording_hints`, not violation evidence.
- **Escalation**: Deprecated. Inherits no active ladder in v1.7.2.1.

### Deprecated subclass: C-no-audit-trail (R11; not active v1.7.2.1)

- **Definition**: A subagent returned, but no `_meta/runtime/<sid>/<subagent>-*.json` audit trail exists for the session.
- **Detection**: AUDITOR runs `bash scripts/lifeos-compliance-check.sh trail-completeness <session_id>`; the legacy CLI form `bash scripts/lifeos-compliance-check.sh <dummy-existing-file> trail-completeness <session_id>` is also supported.
- **Logged fields**: `Type=C-no-audit-trail`; `Severity=P0`; `subagent: <name>`; `expected_trail_path: <path>`; `session_id: <session_id>`.
- **Escalation**: Standard Class C ladder.

### Deprecated subclass: C-trail-incomplete (R11; not active v1.7.2.1)

- **Definition**: Runtime audit trail exists but is missing one or more required schema fields.
- **Detection**: `python3` JSON parse plus required-field check for `subagent`, `step_or_phase`, `step_name`, `started_at`, `ended_at`, `input_summary`, `tool_calls`, `llm_reasoning`, `output_summary`, `tokens`, `fresh_invocation`, `trigger_count_in_session`, and `audit_trail_version`.
- **Logged fields**: `Type=C-trail-incomplete`; `Severity=P0`; `trail_file: <path>`; `missing_fields[]: <field list>`.
- **Escalation**: Standard Class C ladder.

### Deprecated subclass: C-banner-missing (not active v1.7.2.1)

- **Definition**: The 30-day B-class threshold is tripped, but the briefing top lacks the required Compliance Watch banner.
- **Detection**: AUDITOR Mode 3 reads the applicable `violations.md`, computes unresolved B-class count in the last 30 days, and checks the briefing first line for literal prefix `🚨 Compliance Watch:`.
- **Logged fields**: `Type=C-banner-missing`; `Severity=P0`; `b_count_30d: <integer>`; `expected_banner: <literal expected banner>`; `actual_first_line: <briefing first line>`; `Details` must include concrete grep/stdout evidence.
- **Escalation**: P0 until the banner rule is restored and regression passes.

### Deprecated subclass: C-output-suppressed (R8; not active v1.7.2.1)

- **Definition**: Required AUDITOR, retrospective, archiver, or ROUTER compliance output is suppressed, summarized away, hidden behind "omitted for brevity", or replaced with a claim that checks passed without the required evidence block.
- **Detection**: AUDITOR Mode 3 runs `bash scripts/lifeos-compliance-check.sh <briefing> output-completeness` and greps for suppression indicators such as `output suppressed`, `omitted for brevity`, `details omitted`, `not shown here`, or equivalent localized wording in mandatory compliance sections.
- **Logged fields**: `Type=C-output-suppressed`; `Severity=P0`; `suppressed_block: <section name>`; `evidence: <literal line>`; `Details` must include concrete grep/stdout evidence.
- **Escalation**: P0 until output completeness is restored and regression passes. Counts toward the 30-day Compliance Watch banner threshold.

### Deprecated subclass: C-translation-drift (R8; not active v1.7.2.1)

- **Definition**: A multilingual contract, legend, or required output template has drifted across language copies; one language contains a rule/class/check that another language omits or contradicts.
- **Detection**: AUDITOR Mode 3 runs `bash scripts/lifeos-compliance-check.sh <spec-or-briefing> i18n-sync` and checks for stale Type Legends, missing new classes, explicit translation TODOs, or contradictory localized rule text.
- **Logged fields**: `Type=C-translation-drift`; `Severity=P0`; `source_language: <lang>`; `missing_or_drifted_text: <literal>`; `evidence: <grep/stdout>`.
- **Escalation**: P0 because host-agnostic contracts must be semantically identical across languages before shipping.

### Deprecated subclass: C-toctou-frame-md (R8; not active v1.7.2.1)

- **Definition**: The active project frame is resolved from stale, guessed, cached, or pre-read context instead of reading the current `FRAME.md` at the point of use, creating a time-of-check/time-of-use mismatch.
- **Detection**: AUDITOR Mode 3 runs `bash scripts/lifeos-compliance-check.sh <transcript> frame-md-resolution` and checks for unresolved `FRAME.md` paths, explicit TOCTOU/stale-frame markers, guessed project context, or non-existent quoted `FRAME.md` paths.
- **Logged fields**: `Type=C-toctou-frame-md`; `Severity=P0`; `frame_path: <path>`; `resolution_step: <where stale context was used>`; `evidence: <grep/stdout>`.
- **Escalation**: P0 until current-frame resolution is restored and regression passes.

### Deprecated Cortex subclasses CX1-CX7 (not active v1.7.2.1)

- **CX1**: Missing hippocampus, concept-lookup, or soul-check Pre-Router launch/null placeholder. Default severity P1.
- **CX2**: Missing GWT arbitrator after Cortex module returns. Default severity P1.
- **CX3**: Missing `[COGNITIVE CONTEXT]` or `[END COGNITIVE CONTEXT]` delimiters before ROUTER triage. Default severity P1.
- **CX4**: Hippocampus returned more than 7 sessions. Default severity P1.
- **CX5**: GWT emitted more than 5 signals. Default severity P1.
- **CX6**: Cortex information-isolation breach; one Cortex subagent received peer output. Default severity P0.
- **CX7**: Read-only Cortex subagent wrote or edited files. Default severity P0.

### Severity Rubric

- **P0** — Product-level bug. Unfixed → current version cannot ship. Same class as COURT-START-001 (2026-04-19).
- **P1** — Process violation. User-visible, not product-breaking. Example: skipped 1 of 18 retrospective steps.
- **P2** — Minor deviation. Logged for pattern analysis; does not block anything.

### Resolution States

- **`false`** — Unfixed, no mitigation shipped.
- **`partial`** — Fix shipped, awaiting (a) eval regression verification AND (b) 30-day no-recurrence observation window.
- **`true`** — Fix shipped AND eval passes AND 30 days elapsed without recurrence. Append metadata: `(v-number · eval-id · observed-date)`.

## Write Paths

### 1. Hook write (runtime detection, terse entries)

`scripts/lifeos-pre-prompt-guard.sh` is called by Claude Code on `UserPromptSubmit`. When it detects a trigger word, it schedules a delayed check: if the next assistant turn does NOT contain the Pre-flight line, it appends an A3 entry.

```bash
# Pseudo-code inside the hook
if [[ "$TRIGGER_DETECTED" == "true" ]]; then
  # Inject reminder as system-reminder to assistant context
  emit_reminder

  # Schedule post-check via separate tool — the hook itself can't see assistant output,
  # so actual detection happens in PostToolUse hook checking Task() calls
fi
```

Hook-generated entries are **terse** (one-line Details) because bash cannot do deep analysis. AUDITOR later adds follow-up entry with richer context if needed.

### 2. AUDITOR Compliance Patrol write (deep analysis)

After each retrospective Mode 0 or archiver completion, AUDITOR runs Compliance Patrol Mode:

```
For each completed session with a trigger word:
  1. Read full session transcript (ROUTER output + all Task() subagent outputs)
  2. Run the five active v1.7.2.1 Bash checks:
     `briefing-completeness`, `version-markers`, `subagent-launched`,
     `cortex-status`, and `placeholder-check`
  3. For each failed check → append row to violations.md with:
     - Full ISO timestamp
     - Trigger word verbatim
     - Type code
     - Severity (derived from active type — A1/B/C/E default P0, A2/A3/D default P1)
     - Details with evidence quote
     - `false` resolution (will be updated later when fix ships)
  4. If all checks pass → emit `✅ Compliance Patrol passed` and do NOT write
```

### 3. Eval scenario write (regression verification)

`evals/scenarios/start-session-compliance.md` + `evals/run-eval.sh`:
- When running regression, any detected violation appends a row with timestamp prefix `eval-` to distinguish from production
- After test completes, rows with `eval-` prefix are moved to `evals/outputs/violations-{scenario}-{timestamp}.md` to keep live log clean

## Read Paths

### retrospective Mode 0 Step 11.5 (v1.6.3 new, optional)

After Step 11 (SOUL trend), **read** `pro/compliance/violations.md` (dev repo) or `_meta/compliance/violations.md` (user repo):

- Count entries in last 30 days grouped by Type
- Count unresolved (`false` / `partial`) entries
- If count ≥ 3 same type in 30 days → include `🚨 Compliance Watch` block in SOUL Health Report
- If count ≥ 5 → briefing top displays warning
- If count ≥ 10 in 90 days → set internal flag triggering AUDITOR Compliance Patrol at every Start Session (not only after decisions)

### AUDITOR Patrol Inspection (extended in v1.6.3)

In Mode 2 (Patrol Inspection), AUDITOR reads `violations.md`:
- Groups by Type, plots 30-day rolling counts
- Identifies resolved-rate (percentage with `Resolved: true`)
- Surfaces highest-severity unresolved entries in patrol report

## Escalation Ladder

Implemented by `tools/stats.py` (v1.7), reading `violations.md` and emitting actions:

| Threshold | Window | Action |
|-----------|--------|--------|
| ≥3 same type | 30 days | Hook reminder strictness upgrades (reminder text adds explicit warning, e.g., "**YOU HAVE VIOLATED THIS N TIMES IN 30 DAYS**") |
| ≥5 same type | 30 days | retrospective Mode 0 briefing prepends `🚨 Compliance Watch: [type]` to SOUL Health Report |
| ≥10 same type | 90 days | AUDITOR Compliance Patrol runs at every Start Session (not only after decisions) |
| Same type ≥3 with unresolved | any | Block shipping new version until at least partial fix lands |

**Implementation note**: the ladder is implemented by stats.py at Phase 2 (v1.7 阶段 B). Until stats.py ships, thresholds are manually observed by the developer during spec reviews.

## Archival

- Entries older than 90 days → moved to `pro/compliance/archive/YYYY-QN.md` (quarterly rolling file)
- Archival triggered by `tools/backup.py` or manual:
  ```bash
  # Manual quarterly rotation (bash)
  q=$(( ($(date +%-m)-1)/3 + 1 ))
  ARCHIVE="pro/compliance/archive/$(date +%Y)-Q${q}.md"
  # ... filter rows older than 90 days from violations.md to $ARCHIVE ...
  ```
- `git log pro/compliance/violations.md` retains full history independently of this rotation
- Incidents (full archives like `2026-04-19-court-start-violation.md`) are **not** moved — they stay alongside violations.md as permanent record

## Resolution Protocol

An entry transitions `false → partial → true` through three gates:

### Gate 1: `false → partial`

- Underlying fix has shipped (cite version number in Details: e.g., `shipped in v1.6.3`)
- No eval regression yet

### Gate 2: `partial → true`

- Corresponding eval scenario passes (cite test ID: e.g., `eval:start-session-compliance 2026-04-25`)
- 30 days elapsed since fix shipped
- No recurrence in those 30 days (same Type, same failure mode)

### Example transitions

```
# Initial entry (at incident time)
| 2026-04-19T22:47+09:00 | 上朝 | A1 | P0 | ROUTER simulated 18 steps | false |

# After v1.6.3 ships
| 2026-04-19T22:47+09:00 | 上朝 | A1 | P0 | ROUTER simulated 18 steps | partial (v1.6.3 fix) |

# After eval passes + 30 days
| 2026-04-19T22:47+09:00 | 上朝 | A1 | P0 | ROUTER simulated 18 steps | true (v1.6.3 · eval:start-session-compliance · no recurrence 2026-05-19) |
```

## Incident Linking

For P0 violations that become full incidents (like COURT-START-001), create a dedicated incident file:
- Path: `pro/compliance/YYYY-MM-DD-{incident-slug}.md`
- Linked from violations.md Details field: `(see pro/compliance/2026-04-19-court-start-violation.md)`
- Contains: full timeline, root cause analysis, fix plan, resolution checklist

Incidents are **companions to** violations.md, not substitutes. violations.md is the terse ledger; incidents are the deep dives.

## Privacy

- `pro/compliance/violations.md` (dev repo) — **public** via GitHub. No user data.
- `_meta/compliance/violations.md` (user repo) — **private** second-brain.
- Details field must NOT leak user data. Use generic descriptions:
  - ✅ "User decided to invest in a financial instrument"
  - ❌ "User decided to invest $50k in Tesla stock"
- Enforce via same privacy filter as wiki (15 regex patterns defined in `tools/lib/privacy.py`):
  - Strip names, amounts, account IDs, specific companies
  - Keep: decision type, violation mechanism, fix status

## Non-Goals

Clarifying what this log does **not** do:

- **Not a replacement for `user-patterns.md`** — ADVISOR's behavioral observations stay there. This log is only about HARD RULE violations, not general patterns.
- **Not a bug tracker** — use GitHub issues for feature requests and non-compliance bugs.
- **Not a DREAM auto-trigger source** — DREAM's 10 triggers are orthogonal. (DREAM could theoretically read violations.md to detect "user keeps working around a failed hook" but that's future work.)
- **Not a substitute for incident archival** — full incident files (`YYYY-MM-DD-{slug}.md`) live alongside violations.md as separate artifacts.

## Change Log

- **v1.7.2.1** (2026-04-26) - Compressed active Mode 3 taxonomy back to seven core classes (A1/A2/A3/B/C/D/E). Deprecated expanded subclasses and converted R5/R12 phrase blacklists into observation patterns/hints only.

- **v1.7.1 R12** (2026-04-26) - Added `C-fresh-skip` for repeated Start Session triggers that reuse prior Mode 0 output instead of fresh full execution, plus checker scenario `fresh-invocation`.

- **v1.7.1 R11** (2026-04-26) - Added runtime audit trail compliance classes (`C-no-audit-trail`, `C-trail-incomplete`, `B-trail-mismatch`) and checker scenario `trail-completeness`.

- **v1.6.3** (2026-04-21) — Introduced by COURT-START-001 fix. Defines taxonomy (A1/A2/A3/B/C/D/E), dual-repo strategy, escalation ladder.

## See Also

- `pro/compliance/violations.md` — live log (dev repo)
- `pro/compliance/violations.example.md` — entry format examples
- `pro/compliance/2026-04-19-court-start-violation.md` — COURT-START-001 incident archive
- `pro/agents/auditor.md` — Compliance Patrol Mode specification
- `scripts/lifeos-pre-prompt-guard.sh` — UserPromptSubmit hook implementation
- `evals/scenarios/start-session-compliance.md` — regression test scenario
- `SKILL.md` — Pre-flight Compliance Check definition (A3 detection reference)
- `.claude/CLAUDE.md` — project-level HARD RULE for Start Session triggers
