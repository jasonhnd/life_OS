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

| Type | Name | Definition |
|------|------|------------|
| **A1** | Skip subagent | ROUTER simulated subagent's work in main context instead of `Task(agent)` call |
| **A2** | Skip directory check | In dev repo, retrospective Mode 0 Step 2 (DIRECTORY TYPE CHECK) bypassed |
| **A3** | Skip Pre-flight check | ROUTER's first response after trigger did not contain the `🌅 Trigger: …` line (v1.6.3 new) |
| **B** | Fabricate fact | Referenced non-existent path / section / process / escape route as authority |
| **C** | Incomplete Phase | archiver exited before all 4 phases (stopped mid-execution) |
| **D** | Placeholder value | Completion Checklist contained `TBD`, empty field, or literal `{...}` |
| **E** | Main-context Phase execution | ROUTER executed archiver's Phase 1/2/3/4 logic in main context |
| **F** | False positive | Hook fired on paste/quote content, not a real user trigger (v1.6.3a new). Default severity P2. Detected by assistant judgment when trigger word appears in paste indicators (long prompt, trigger not on first line, surrounded by quote/code-fence markers). Excluded from escalation ladder — high count = hook miscalibration, not user behavior. |

### Class B-fabricate-toolcall (v1.7.0.1 R5+)

- **Definition**: Subagent claims a tool call result (success or failure) without the corresponding tool call appearing in transcript.
- **Detection**: AUDITOR Mode 3 scans for Step 8 evidence markers + confabulation phrase blacklist, cross-references with transcript tool call records.
- **Logged fields**: `Type=B-fabricate-toolcall`; `Severity=P1`; `Details` must name the fabricated phrase + tool that was claimed missing. `missing_evidence: <fabricated phrase>`; `expected_tool: <Bash|WebFetch|...>`.
- **Escalation**: Inherits Class B standard ladder (`>=3/30d` -> Compliance Watch).
- **Why introduced**: 2026-04-25 Jason 测试机实测 retrospective subagent 虚构 "private repo" 借口掩盖 Step 8 未执行,触发 v1.7.0.1 R5 anti-confabulation patch.
- **Confabulation phrase blacklist**: private repo / private 仓库; WebFetch 失败 / WebFetch failed; 网络问题 / network unavailable; 权限问题 / 401 / 403; curl 失败.

### Class B-source-drift (v1.7.0.1+)

- **Definition**: Primary-source measured count and INDEX count differ by `|delta| >= 3`, but the briefing omits literal `⚠️ DRIFT` or rationalizes the mismatch as consistent.
- **Detection**: AUDITOR Mode 3 compares briefing primary-source markers (`[Wiki count: measured`, `[Sessions count: measured`, `[Concepts count: measured`) against corresponding INDEX values using Bash stdout.
- **Logged fields**: `Type=B-source-drift`; `Severity=P1`; `measured: <number>`; `index: <number>`; `drift: <measured-index>`; `marker: <literal marker line>`; `Details` must include concrete grep/stdout evidence.
- **Escalation**: Inherits Class B standard ladder (`>=3/30d` -> Compliance Watch).

### Class B-source-stale (v1.7.0.1+)

- **Definition**: `STATUS.md` is `>=7` days stale, but the briefing still quotes numeric claims from `STATUS.md`.
- **Detection**: AUDITOR Mode 3 checks `[STATUS staleness:` marker and verifies whether stale STATUS-derived numeric claims appear in the briefing.
- **Logged fields**: `Type=B-source-stale`; `Severity=P1`; `status_days: <integer>`; `quoted_claim: <numeric claim text>`; `source: <STATUS.md path or marker>`; `Details` must include concrete grep/stdout evidence.
- **Escalation**: Inherits Class B standard ladder (`>=3/30d` -> Compliance Watch).

### Class C-brief-incomplete (v1.7.0.1+)

- **Definition**: Start Session reached final briefing output, but the briefing omitted one or more mandatory fixed-position sections or required evidence fields. This is a Class C subclass for incomplete briefing composition; it does not change base Class C semantics, which remain archiver incomplete-phase failures.
- **Detection**: After `retrospective` Mode 0 returns, scan the transcript for the Start Session output contract using the locked literal heading arrays. Retrospective required H2s exactly: [`## 0. Pre-flight Hook Health Check`, `## 1. Cognitive Layer · Cortex Step 0.5`, `## 2. Second-brain Connection`, `## 3. Python Tools Executed`, `## 4. Retrospective 18 Steps Progress`, `## 5. AUDITOR Mode 3 Compliance Patrol`, `## 6. Ready for User`]. Archiver required H2s exactly: [`## Phase 1 · Outbox`, `## Phase 2 · Wiki Extraction`, `## Phase 3 · DREAM Triggers`, `## Phase 4 · Git Sync`, `## Completion Checklist`]. Log `C-brief-incomplete` when the briefing omits any locked literal heading, omits required evidence fields, or leaves a required block unavailable without explicitly marking it empty/unavailable.
- **Logged fields**: `Type=C-brief-incomplete`; `Severity=P1`; `required_headings.retrospective: [`## 0. Pre-flight Hook Health Check`, `## 1. Cognitive Layer · Cortex Step 0.5`, `## 2. Second-brain Connection`, `## 3. Python Tools Executed`, `## 4. Retrospective 18 Steps Progress`, `## 5. AUDITOR Mode 3 Compliance Patrol`, `## 6. Ready for User`]`; `required_headings.archiver: [`## Phase 1 · Outbox`, `## Phase 2 · Wiki Extraction`, `## Phase 3 · DREAM Triggers`, `## Phase 4 · Git Sync`, `## Completion Checklist`]`; `missing_headings: <comma-separated list of missing literal headings>`; `Details` must include a concrete evidence marker (grep output, transcript quote, or tool-call ID) and state that the run reached final briefing output; `Resolved=false` until the briefing contract fix ships and passes regression.
- **Escalation**: Inherits the Class C standard ladder as its own type (`C-brief-incomplete`). It does not count toward base `C` archiver-incomplete thresholds.

### Class C-banner-missing (v1.7.0.1+)

- **Definition**: The 30-day B-class threshold is tripped, but the briefing top lacks the required Compliance Watch banner.
- **Detection**: AUDITOR Mode 3 reads the applicable `violations.md`, computes unresolved B-class count in the last 30 days, and checks the briefing first line for literal prefix `🚨 Compliance Watch:`.
- **Logged fields**: `Type=C-banner-missing`; `Severity=P0`; `b_count_30d: <integer>`; `expected_banner: <literal expected banner>`; `actual_first_line: <briefing first line>`; `Details` must include concrete grep/stdout evidence.
- **Escalation**: P0 until the banner rule is restored and regression passes.

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
  2. Run 6 detection checks (A1 / A2 / A3 / B × 3 types for Start Session;
     C / D / E for Adjourn)
  3. For each failed check → append row to violations.md with:
     - Full ISO timestamp
     - Trigger word verbatim
     - Type code
     - Severity (derived from type — A1/B/C/E default P0, A2/A3/D default P1)
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
