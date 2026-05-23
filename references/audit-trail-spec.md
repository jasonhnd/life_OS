# Subagent Audit Trail Spec

Version: v1.8.6 R13 (was v1.8.5 R12; bumped Stage 1 v1.8.6 to migrate JSON trail to md trail per "0 .json / 0 .yml" HARD RULE)

Runtime audit trails are Life OS channel 1 evidence: files on disk that AUDITOR can read programmatically without trusting ROUTER's LLM-mediated transcript summary. Every subagent writes a **markdown trail with YAML frontmatter** before returning.

> **v1.8.6 pivot**: R12 used `.json` files for machine parseability. R13 uses `.md` with YAML frontmatter — same parseability (LLM reads frontmatter), zero `.json` files in vault per repo HARD RULE "No .py / .sh / .yml / .json files outside platform-required exceptions".

## Path

```text
_meta/runtime/<session_id>/<subagent>-<step_or_phase>.md
```

Examples:

```text
_meta/runtime/20260426T112233/retrospective-step-1.md
_meta/runtime/20260426T112233/archiver-phase-4.md
_meta/runtime/20260426T112233/notion-sync.md
```

`session_id` is created once by ROUTER for a Life OS flow and reused by every subagent and orchestrator trail. Canonical format is `YYYYMMDDTHHMMSS`, with an optional suffix when a host needs collision avoidance.

## Required Markdown Format

Every audit trail file MUST be a markdown file with this structure:

```markdown
---
subagent: retrospective|archiver|hippocampus|...
step_or_phase: 1|6|phase-1|step-10a|...
step_name: THEME RESOLUTION|SOUL HEALTH SCAN|...
started_at: <ISO8601>
ended_at: <ISO8601>
input_summary: "<key inputs received>"
tool_calls:
  - tool: Read|Bash|WebFetch|...
    args: "..."
    result_summary: "..."
    exit_code: 0
llm_reasoning: "<short summary of LLM judgment, 50-200 chars>"
output_summary: "<key outputs produced>"
tokens:
  input: 0
  output: 0
fresh_invocation: true
trigger_count_in_session: 1
audit_trail_version: v1.8.6-r13

# v1.8.5 R12 PRESERVED + v1.8.6 R13 still required:
# value_invocations — required (non-empty) on contested case decisions made by
# REVIEWER, ARCHIVER Phase 2, ADVISOR drift detection, or any agent that
# resolved a SOUL-dim conflict. Empty array allowed when no contested case
# occurred in this step. Empty array on contested case = F14 SILENT_JUDGMENT_FAILURE.
value_invocations:
  - invocation_id: vi-<session_id>-<seq>
    domain_value_id: dv-truth-over-comfort
    rule_conflict: "<the contested case description>"
    chosen_path: "<what the agent did>"
    rejected_alternative: "<what was rejected, MUST be concrete artifact not strawman>"
---

# <Subagent name> · <step or phase>

## What this step did

<2-3 paragraph human-readable narrative of what happened in this step. Same content as the frontmatter `output_summary` but with more context for human review.>

## Key tool calls

<bullet list expanding the tool_calls frontmatter into readable form>

## Reasoning

<expanded llm_reasoning, 1-2 paragraphs>

## Value invocations (if any contested case)

<expanded value_invocations entries; cite SOUL dim with explanation>
```

## Required Frontmatter Field Meanings

| Field | Type | Meaning |
|-------|------|---------|
| `subagent` | string | Agent or orchestrator actor, e.g. `retrospective`, `archiver`, `notion-sync`. |
| `step_or_phase` | string | Step or phase identifier, e.g. `step-1`, `phase-2`, `step-10a`. |
| `step_name` | string | Human-readable step/phase name. |
| `started_at` | string | ISO 8601 start timestamp. |
| `ended_at` | string | ISO 8601 end timestamp. |
| `input_summary` | string | Short summary of key inputs received. |
| `tool_calls` | array (YAML list) | Tool calls or MCP calls used, with args/result summary/exit status where available. |
| `llm_reasoning` | string | Short LLM judgment summary. Bash prefetch uses `(Bash pre-fetch, no LLM)`. |
| `output_summary` | string | Short summary of key outputs produced. |
| `tokens` | object | Token counts with `input` and `output` numeric fields. Use `0` when unavailable. |
| `fresh_invocation` | boolean | Must be `true` for every Start Session / Adjourn invocation; never infer completion from prior transcript output. |
| `trigger_count_in_session` | integer | Trigger ordinal inside the active session, `1` for the first trigger and `2+` for repeated fresh triggers. |
| `audit_trail_version` | string | Current value: `v1.8.6-r13`. |
| `value_invocations` | array | **v1.8.5 R12 + v1.8.6 R13** — each contested-case SOUL dim invocation as 5-field object (invocation_id / domain_value_id / rule_conflict / chosen_path / rejected_alternative). Empty array `[]` allowed when no contested case in this step; empty array on contested case = F14 SILENT_JUDGMENT_FAILURE. |

## Validation

AUDITOR Mode 3 validates:

- Existence: each completed subagent has at least one expected trail file.
- Schema: every markdown file has valid YAML frontmatter with all required fields.
- Freshness: every trail file has `fresh_invocation: true` and integer `trigger_count_in_session`.
- Cross-check: `output_summary` matches the ROUTER-pasted wrapper, required markers, payloads, Notion handoff receipts, and transactional token table.
- Token receipt: trail token fields can be summed and compared with the visible transaction receipt.
- **v1.8.6 NEW**: no `.json` or `.yml` files in `_meta/runtime/<session_id>/` (per HARD RULE "No .py/.sh/.yml/.json"). Any such file = `F4 SCOPE_FAILURE: forbidden extension in runtime dir`.

## Notion Sync

Step 10a writes:

```text
_meta/runtime/<session_id>/notion-sync.md
```

The file uses `subagent: notion-sync` and `step_or_phase: step-10a` in frontmatter. Its `tool_calls` array records the Notion MCP operations with input and output payload summaries. ROUTER MUST write this file even when MCP is unavailable, using a failure summary instead of pausing for user permission.

## Migration from R12 JSON to R13 markdown (v1.8.5 → v1.8.6)

Historical `_meta/runtime/<sid>/*.json` trail files from v1.8.5 and earlier:
- Remain readable (legacy mode)
- AUDITOR Mode 3 still validates them under R12 schema
- New trail files from v1.8.6 onwards MUST be `.md` per R13 schema
- No retroactive conversion required; lazy migration via `/migrate-trail-r13` slash command if needed

## Violation Mapping

| Failure | Violation | F-code |
|---------|-----------|--------|
| Expected trail file missing | `C-no-audit-trail` | F9_TRACE_FAILURE |
| Trail markdown missing required frontmatter fields or invalid YAML | `C-trail-incomplete` | F3_SCHEMA_FAILURE |
| Trail content contradicts ROUTER-visible output | `B-trail-mismatch` | F12_DRIFT_FAILURE |
| Contested case in step but `value_invocations: []` (R12+) | `F14-silent-judgment` | F14_SILENT_JUDGMENT_FAILURE |
| `domain_value_id` doesn't exist in SOUL.md (R12+) | `F17-value-hallucination` | F17_VALUE_HALLUCINATION_FAILURE |
| `rejected_alternative` is strawman or empty (R12+) | `F14b-strawman-rejection` | F14_SILENT_JUDGMENT_FAILURE (theater pattern) |
| **`.json` or `.yml` file in `_meta/runtime/<sid>/` (v1.8.6+)** | `F4-forbidden-extension-trail` | F4_SCOPE_FAILURE |
