# Subagent Audit Trail Spec

Version: v1.7.1 R11

Runtime audit trails are Life OS channel 1 evidence: files on disk that AUDITOR
can read programmatically without trusting ROUTER's LLM-mediated transcript
summary. Every subagent writes a JSON trail before returning.

## Path

```text
_meta/runtime/<session_id>/<subagent>-<step_or_phase>.json
```

Examples:

```text
_meta/runtime/20260426T112233/retrospective-step-1.json
_meta/runtime/20260426T112233/archiver-phase-4.json
_meta/runtime/20260426T112233/notion-sync.json
```

`session_id` is created once by ROUTER for a Life OS flow and reused by every
subagent and orchestrator trail. Canonical format is `YYYYMMDDTHHMMSS`, with an
optional suffix when a host needs collision avoidance.

## Required JSON Schema

Every audit trail file MUST be a JSON object with these fields:

```json
{
  "subagent": "retrospective|archiver|hippocampus|...",
  "step_or_phase": "1|6|phase-1|step-10a|...",
  "step_name": "THEME RESOLUTION|SOUL HEALTH SCAN|...",
  "started_at": "ISO8601",
  "ended_at": "ISO8601",
  "input_summary": "<key inputs received>",
  "tool_calls": [
    {"tool": "Read|Bash|WebFetch|...", "args": "...", "result_summary": "...", "exit_code": 0}
  ],
  "llm_reasoning": "<short summary of LLM judgment, 50-200 chars>",
  "output_summary": "<key outputs produced>",
  "tokens": {"input": 0, "output": 0},
  "fresh_invocation": true,
  "trigger_count_in_session": 1,
  "audit_trail_version": "v1.7.1-r11"
}
```

Required field meanings:

| Field | Type | Meaning |
|-------|------|---------|
| `subagent` | string | Agent or orchestrator actor, e.g. `retrospective`, `archiver`, `notion-sync`. |
| `step_or_phase` | string | Step or phase identifier, e.g. `step-1`, `phase-2`, `step-10a`. |
| `step_name` | string | Human-readable step/phase name. |
| `started_at` | string | ISO 8601 start timestamp. |
| `ended_at` | string | ISO 8601 end timestamp. |
| `input_summary` | string | Short summary of key inputs received. |
| `tool_calls` | array | Tool calls or MCP calls used, with args/result summary/exit status where available. |
| `llm_reasoning` | string | Short LLM judgment summary. Bash prefetch uses `(Bash pre-fetch, no LLM)`. |
| `output_summary` | string | Short summary of key outputs produced. |
| `tokens` | object | Token counts with `input` and `output` numeric fields. Use `0` when unavailable. |
| `fresh_invocation` | boolean | Must be `true` for every Start Session / Adjourn invocation; never infer completion from prior transcript output. |
| `trigger_count_in_session` | integer | Trigger ordinal inside the active session, `1` for the first trigger and `2+` for repeated fresh triggers. |
| `audit_trail_version` | string | Current value: `v1.7.1-r11`. |

## Validation

AUDITOR Mode 3 validates:

- Existence: each completed subagent has at least one expected trail file.
- Schema: every JSON file has all required fields and parses successfully.
- Freshness: every JSON file has `fresh_invocation: true` and integer
  `trigger_count_in_session`.
- Cross-check: `output_summary` matches the ROUTER-pasted wrapper, required
  markers, YAML payloads, Notion handoff receipts, and transactional token table.
- Token receipt: trail token fields can be summed and compared with the visible
  transaction receipt.

## Notion Sync

Step 10a writes:

```text
_meta/runtime/<session_id>/notion-sync.json
```

The file uses `subagent: "notion-sync"` and `step_or_phase: "step-10a"`.
Its `tool_calls` array records the four Notion MCP operations with input and
output payload summaries. ROUTER MUST write this file even when MCP is
unavailable, using a failure summary instead of pausing for user permission.

## Violation Mapping

| Failure | Violation |
|---------|-----------|
| Expected trail file missing | `C-no-audit-trail` |
| Trail JSON missing required fields or invalid JSON | `C-trail-incomplete` |
| Trail content contradicts ROUTER-visible output | `B-trail-mismatch` |
