---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# Eval History Specification (v1.7)

Eval history is Life OS's structured self-evaluation feedback loop. It is the spec-layer equivalent of Hermes's RL training signal — without training any model. AUDITOR writes one structured evaluation per session; RETROSPECTIVE scans history at Start Session to surface systemic quality drift.

---

## 1. Purpose

Eval history is the mechanism through which Life OS inspects itself over time.

Individual AUDITOR reports already grade each session's agent performance, but they evaporate after the session ends. They are good for *this* deliberation; they do not tell the system anything about *the last ten deliberations*. That missing loop is what eval history closes.

- **AUDITOR** is the writer. After every full deliberation or express workflow it serialises its judgement as structured YAML + markdown into `_meta/eval-history/`.
- **RETROSPECTIVE Mode 0** is the primary reader. At each Start Session it reads the last 10 eval files and detects systemic patterns — repeated violations, declining scores, hallucinated citations, skipped phases.
- **Tools** (stats, reconcile) read the history for monthly summaries and orphan detection.

The inspiration is Hermes's RL training loop: Hermes compresses agent trajectories into training signal, then fine-tunes the model. Life OS cannot fine-tune its hosts (Claude, Gemini, Codex), but it can fine-tune its *rules* — by writing quality signal to disk and making RETROSPECTIVE surface it next session. The signal changes system behaviour through human attention, not gradient descent.

This is also the direct answer to Hermes Lesson 5 in `devdocs/research/2026-04-19-hermes-analysis.md`: self-evaluation must feed back into the system, not merely accumulate as one-off reports.

---

## 2. File Location

```
_meta/eval-history/
└── {YYYY-MM-DD}-{project}.md
```

One file per session that went through AUDITOR.

- `{YYYY-MM-DD}` — session start date (ISO).
- `{project}` — slug of the bound project (kebab-case, lowercase).
- Multi-session days on the same project append `-{HHMM}` to disambiguate: `2026-04-20-career-change-1430.md`.

Eval files live next to other `_meta/` artifacts (STATUS.md, STRATEGIC-MAP.md, lint-state.md) and follow the same convention: compiled by agents, readable by humans, never hand-edited after the fact.

---

## 3. YAML Frontmatter Schema

Every eval file begins with a YAML frontmatter block. Unknown fields are ignored by readers; missing required fields are flagged by `tools/reconcile.py`.

```yaml
---
eval_id: {YYYY-MM-DD-HHMM}-{project}
session_id: string                 # references _meta/sessions/{session_id}.md
evaluator: auditor | auditor-patrol
evaluation_mode: decision-review | patrol-inspection
date: ISO 8601 timestamp
scores:
  information_isolation: integer (0-10)
  veto_substantiveness: integer (0-10)
  score_honesty: integer (0-10)
  action_specificity: integer (0-10)
  process_compliance: integer (0-10)
  adjourn_completeness: integer (0-10)
  soul_reference_quality: integer (0-10)
  wiki_extraction_quality: integer (0-10)
  cognitive_annotation_quality: integer (0-10)    # v1.7: hippocampus output quality
  citation_groundedness: integer (0-10)           # v1.7: narrator citation validity
violations:
  - type: adjourn_phase_skip | notion_sync_skip | citation_missing | ...
    agent: ROUTER | ARCHIVER | ...
    severity: critical | high | medium | low
    detail: string
agent_quality_notes:
  PLANNER: string
  REVIEWER: string
  DISPATCHER: string
  FINANCE: string
  EXECUTION: string
  GROWTH: string
  INFRA: string
  PEOPLE: string
  GOVERNANCE: string
  AUDITOR: string
  ADVISOR: string
  ARCHIVER: string
---
```

Notes:

- `scores` are integers 0–10. Half-scores are not allowed — force AUDITOR to commit.
- `violations` is a list; an empty list means "no violations observed".
- `agent_quality_notes` only includes agents that actually participated in the session. Express path will omit most entries.

---

## 4. Body Format

The markdown body follows the frontmatter and is consumed by both human readers and RETROSPECTIVE's Mode 0 pattern scan.

```markdown
## Summary
{one-paragraph high-level assessment — what happened, whether the workflow held, headline scores}

## Strengths
- {what went well, grounded in specific evidence}

## Weaknesses
- {what needs improvement, grounded in specific evidence}

## Systemic Pattern Observations
{if this session shows patterns consistent with prior sessions, note them here — e.g. "third consecutive session where ARCHIVER Phase 2 produced zero wiki candidates"}

## Recommendations
- {specific improvements for next session, named agent + named mechanism}
```

Body rules:

- Strengths and Weaknesses must reference concrete evidence (quoted agent output, score contradictions, skipped phases). Generic praise like "all agents performed well" is an AUDITOR anti-pattern and is banned by `pro/agents/auditor.md`.
- Systemic Pattern Observations is optional for single-session anomalies and required when a repeated pattern was detected across the last 10 evals (RETROSPECTIVE provides a cross-session hint; AUDITOR restates it here).
- Recommendations must target a specific agent (PLANNER / REVIEWER / ARCHIVER / ...) and a specific mechanism (score calibration / checklist coverage / wiki criteria), not vague exhortations.

---

## 5. Score Dimensions

Ten dimensions, each 0–10 with three calibrated anchor points. Every AUDITOR evaluation must fill all ten — missing dimensions are flagged by `tools/reconcile.py`.

### 5.1 information_isolation (0–10)

Whether HARD RULES on upstream context leakage held across all agents.

- **10**: PLANNER shows no awareness of ROUTER reasoning. REVIEWER receives only the planning document. Domains do not reference each other's scores or conclusions. No contamination anywhere.
- **5**: Minor leakage — e.g. ROUTER hints at which domains will fire, or a domain mentions "as the other review noted".
- **0**: Obvious cross-contamination. REVIEWER sees PLANNER's raw thoughts, or two domains reference each other by name.

### 5.2 veto_substantiveness (0–10)

Whether REVIEWER's approval/veto was grounded in the 8-item checklist with specific evidence.

- **10**: Every checklist item addressed with concrete observation. Veto decisions cite the failed item and required correction direction.
- **5**: Checklist applied but evidence is shallow ("logic is sound" without saying why).
- **0**: Rubber-stamp approval. No checklist pass. Veto reasons are vague or missing.

### 5.3 score_honesty (0–10)

Whether domain scores correspond to their own analysis text.

- **10**: Every domain's numeric score matches the severity of its narrative. No face-saving. Standard deviation across domains > 1.0 when analyses differ meaningfully.
- **5**: One or two suspicious scores — e.g. a 7 accompanying a paragraph of serious concerns.
- **0**: Blanket 7s or 8s everywhere, or a score that directly contradicts its own risk assessment.

### 5.4 action_specificity (0–10)

Whether action items are specific, actionable, timed, and owned.

- **10**: Every action item names a domain owner, a deadline, and a concrete first step.
- **5**: Actions are specific but missing deadlines or owners.
- **0**: Actions are aspirations ("think this over", "consider implications").

### 5.5 process_compliance (0–10)

Whether the workflow state machine was obeyed end-to-end.

- **10**: Every mandatory step ran in the mandatory order. No skipped AUDITOR, no skipped ADVISOR, no skipped Notion sync. Adjourn state machine held.
- **5**: One skipped step that was caught and recovered mid-session.
- **0**: Multiple phase skips, or an illegal transition (Summary Report → ARCHIVER without AUDITOR + ADVISOR).

### 5.6 adjourn_completeness (0–10)

Whether the ARCHIVER subagent executed all four phases (Archive, Knowledge Extraction, DREAM, Sync) and produced a clean Completion Checklist.

- **10**: All 4 phases ran. Checklist values are real (not "TBD"). Notion sync returned to orchestrator and executed.
- **5**: 3 of 4 phases ran, or Phase 3 DREAM produced no journal entry.
- **0**: Split flow. Multi-message archiver. Placeholder values in the checklist.

### 5.7 soul_reference_quality (0–10)

Whether REVIEWER referenced relevant SOUL dimensions for the decision under review.

- **10**: Every decision-relevant SOUL dimension (active + dormant + conflict zone) was explicitly cited with confidence and direction.
- **5**: SOUL referenced but selectively — e.g. only high-confidence dimensions, ignoring dormant ones that matter.
- **0**: SOUL not referenced at all, or referenced without integrating into the review.

### 5.8 wiki_extraction_quality (0–10)

Whether ARCHIVER Phase 2 extracted wiki candidates that passed all 6 criteria + privacy filter, and whether extractions were reusable across sessions.

- **10**: Candidates are specific, reusable, privacy-clean, and placed in the correct domain.
- **5**: Some candidates pass but are redundant with existing entries or too narrow to reuse.
- **0**: Either no extraction happened when it should have, or extractions failed privacy filter and shipped anyway.

### 5.9 cognitive_annotation_quality (0–10) — v1.7

Whether hippocampus-tier retrieval surfaced the right wiki entries and annotated them with relevance scores that align with actual utility in the session.

- **10**: Retrieved entries were used. Relevance scores tracked actual influence on the decision.
- **5**: Retrieved entries were used but relevance scoring was coarse.
- **0**: Retrieved entries were ignored, or relevance was hallucinated.

### 5.10 citation_groundedness (0–10) — v1.7

Whether narrator-tier citations (references to past sessions, wiki entries, SOUL dimensions) point to artifacts that actually exist and say what is claimed.

- **10**: Every citation resolves to a real artifact with the claimed content.
- **5**: Most citations resolve; a minority are paraphrased beyond the source.
- **0**: Citations are fabricated or point to nonexistent sessions/entries.

---

## 6. Trigger Conditions

### 6.1 AUDITOR writes an eval-history entry when

- After every full deliberation workflow (Step 8 in `pro/CLAUDE.md`).
- After every express analysis workflow that produces a Brief Report of sufficient depth to evaluate.
- After a Patrol Inspection triggered by RETROSPECTIVE Mode 0 (lint-state > 4h). Patrol writes with `evaluation_mode: patrol-inspection`.

### 6.2 AUDITOR does NOT write an entry when

- ROUTER handled the request directly (no subagent work to evaluate).
- STRATEGIST sessions (different evaluation domain — thinker dialogue quality, not deliberation quality).
- First-run / empty-second-brain sessions where no decision took place.
- Sessions that aborted before PLANNER produced output.

### 6.3 Write timing

AUDITOR writes the eval file at the end of Step 8, before ADVISOR runs. Writing is synchronous from AUDITOR's perspective but does not block ROUTER — if the write fails, AUDITOR reports the failure and the session continues.

---

## 7. Systemic Issue Detection

RETROSPECTIVE Mode 0 reads the last 10 eval files at Start Session and applies the following detection rules. Detected patterns appear in the morning briefing as a systemic-issue warning block.

### 7.1 adjourn_completeness trend

If 3 or more consecutive sessions show `adjourn_completeness < 6` → warn: "archiver subagent may not be launching properly".

This catches the recurring v1.6.x bug where ROUTER interjected between ARCHIVER phases, producing split flows.

### 7.2 wiki_extraction_quality decline

If `wiki_extraction_quality` shows a downward trend across 5 or more sessions → warn: "ARCHIVER Phase 2 may be silently skipping extraction".

### 7.3 citation_groundedness failures

If narrator citations fail resolution > 20% over the last 10 sessions → warn: "narrator layer is hallucinating signals".

### 7.4 cognitive_annotation_quality floor

If `cognitive_annotation_quality < 5` across the last 5 sessions → warn: "hippocampus retrieval tuning needed".

### 7.5 process_compliance recurrence

If the same `violations[].type` appears 3 or more times within the last 30 days → trigger compliance log upgrade: the violation graduates from eval history to `user-patterns.md` as a tracked behavioural pattern, and next session's ADVISOR surfaces it as a direct observation.

### 7.6 Briefing format

Warnings appear immediately after the DREAM Auto-Triggers block in the Start Session briefing, before the Strategic Overview. Format (localised per active theme language):

```
⚠️ 系统性问题检测：
- 退朝完整度连续 3 次 ≤6 → 建议检查 archiver subagent 启动
- Wiki 萃取质量从 4/15 起下降 → 建议本次重点关注
```

If no systemic issues are detected, the block is omitted entirely (no placeholder).

---

## 8. Archive Policy

- Eval files are retained indefinitely. Each file is small (~5 KB), so 1000 sessions total ~5 MB.
- Files older than 6 months may be compressed into a quarterly digest at `_meta/eval-history/_digest/{YYYY-Q}.md`, with the original files moved to `_meta/eval-history/_archive/`. The digest preserves headline scores and systemic patterns; individual sessions remain accessible.
- The digest is written by `tools/stats.py` when run with `--compress-old`. It is never written automatically.

---

## 9. Read Flow

Multiple consumers read eval history for different purposes.

| Consumer | Frequency | Scope | Purpose |
|----------|-----------|-------|---------|
| retrospective Mode 0 | Every Start Session | Last 10 files | Systemic pattern detection for morning briefing |
| auditor | When invoked | Last 5–10 files, same project | Historical calibration reference before evaluating current session |
| tools/stats.py | On demand | All files or date range | Monthly / quarterly quality reports |
| tools/reconcile.py | On demand | All files | Orphan detection — evals without matching sessions, sessions without evals |

Readers must tolerate missing fields (different Life OS versions may have written different schemas). The YAML schema is forward-compatible: unknown fields are ignored, missing-but-expected fields trigger reconcile warnings rather than hard failures.

---

## 10. Write Flow

- Trigger: AUDITOR completes Decision Review in Step 8 of the full deliberation workflow (or the Brief-Report equivalent in express path, or Patrol Inspection).
- Path: `_meta/eval-history/{YYYY-MM-DD}-{project}.md`.
- Conflict resolution: if the file already exists (same date, same project, second or later session of the day), AUDITOR appends `-{HHMM}` to the filename: `2026-04-20-career-change-1430.md`.
- Failure handling: if the write fails (disk full, permission error, path missing), AUDITOR reports the failure in its regular Decision Review output. The session continues. The failure itself is logged as a process compliance violation for the next session's eval.
- Immutability: eval files are never edited after creation. If the evaluation was wrong, a new file is written at the next session with a reversal note. Prior files remain as historical record.

---

## 11. Migration

No eval history existed before v1.7.

- `tools/migrate.py` does **not** backfill historical AUDITOR reports from `_meta/journal/`. Those reports were unstructured prose and do not fit the schema; attempting to backfill would produce low-signal noise that contaminates systemic detection.
- Eval history starts fresh on v1.7 day one. The first Start Session on v1.7 shows no systemic warnings (no history to scan). Warnings begin appearing once at least 3 consecutive sessions are recorded.
- Users who want historical analysis of pre-v1.7 sessions should use the pre-existing `_meta/journal/` reports directly; they are not migrated.

---

## 12. Anti-patterns

These are prohibited. RETROSPECTIVE and `tools/reconcile.py` flag them when detected.

- **Do not** embed the full Summary Report inside an eval file. Reference `session_id` instead. Eval files are quality metadata, not duplicate session content.
- **Do not** skip eval writes for "minor" sessions. Patterns emerge across volume — skipping the easy ones destroys the signal for the hard ones.
- **Do not** edit eval files after creation. If the evaluation was wrong, write a new file next session that notes the reversal. Prior files are immutable.
- **Do not** let AUDITOR's eval write block the user-facing workflow. The write is synchronous from AUDITOR's perspective, but a write failure must not stall ADVISOR, ARCHIVER, or session close.
- **Do not** sync eval files to Notion (user decision #12). Eval history is a local introspection artifact; pushing it to Notion makes the mobile view noisy and has no mobile-side consumer.
- **Do not** allow face-saving in AUDITOR's own evaluation. If `score_honesty: 3` is warranted, write 3 — AUDITOR evaluating itself with uniform 7s is the exact anti-pattern AUDITOR was built to detect in others.
- **Do not** invent scores for dimensions that could not be observed. If no SOUL references were relevant, mark `soul_reference_quality` as the session's default (usually 10 — "not applicable, therefore no violation") and note the rationale in `agent_quality_notes`.

---

## 13. Related Specs

- `references/cortex-spec.md` — overall Cortex architecture; eval-history is one of the five v1.7 core artifacts
- `references/session-index-spec.md` — `session_id` field links every eval entry back to its session summary
- `references/hippocampus-spec.md` — produces the signals AUDITOR grades via `cognitive_annotation_quality` (§5.9)
- `references/gwt-spec.md` — produces arbitration quality signals AUDITOR grades via `cognitive_annotation_quality`
- `references/narrator-spec.md` — produces citation quality signals AUDITOR grades via `citation_groundedness` (§5.10)
- `references/hooks-spec.md` — violation logs feed the `process_compliance` dimension (§5.5) and §7.5 recurrence detection
- `references/tools-spec.md` — `stats.py` and `reconcile.py` consume eval-history for monthly reports and orphan detection
- `references/soul-spec.md` — `soul_reference_quality` (§5.7) grades how REVIEWER cites SOUL dimensions
- `references/wiki-spec.md` — `wiki_extraction_quality` (§5.8) grades ARCHIVER Phase 2 wiki candidates
- `pro/agents/auditor.md` — sole writer of eval-history entries (end of Step 8)
- `pro/agents/retrospective.md` — Mode 0 reader for systemic pattern detection (last 10 files)
- `devdocs/research/2026-04-19-hermes-analysis.md` — Hermes Lesson 5 (self-evaluation must feed back) motivates this spec
