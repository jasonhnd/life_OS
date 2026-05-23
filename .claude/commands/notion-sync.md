---
description: After ROUTER calls the Notion MCP at Step 10a (archiver Phase 4 → Notion sync), write the audit trail JSON to _meta/runtime/<sid>/notion-sync.json. Replaces v1.8.4 scripts/notion-sync.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[--sid SID] [--input SUMMARY] [--output SUMMARY] [--payload TEXT]"
allowed-tools:
  - Write
  - Read
---

# /notion-sync

You are writing the audit trail JSON for ROUTER's Step 10a Notion MCP sync operation. **This command does NOT call the Notion MCP itself** — ROUTER calls Notion MCP directly in the main context (because subagents cannot access environment-specific MCP tools). This command only records what ROUTER observed.

## Inputs

Parse `$ARGUMENTS` for:
- `--sid SID` (required) — runtime session id; if absent, abort with error
- `--input SUMMARY` (required) — input summary observed by ROUTER (e.g. "session 2026-05-22 archive sync to 4 Notion entities")
- `--output SUMMARY` (required) — output summary (e.g. "3/4 succeeded; todo_database_id failed: missing permission")
- `--payload TEXT` (optional) — literal payload or details to store
- `--payload-file PATH` (optional) — read payload from file
- `--subagent NAME` (optional, default: `router`) — trail actor
- `--step STEP` (optional, default: `step-10a`) — trail step id
- `--step-name NAME` (optional, default: `ROUTER Notion MCP Sync`) — human-readable step name

## Procedure

### 1. Compute path
```
target_dir = _meta/runtime/<sid>/
target_file = _meta/runtime/<sid>/notion-sync-<timestamp>.json
```
- `<sid>` is the session id from `--sid`
- `<timestamp>` is current ISO-8601 (e.g. `20260522T180000Z`)

### 2. Determine trigger_count_in_session
Per `references/audit-trail-spec.md`, count existing audit trail entries for this subagent in `_meta/runtime/<sid>/` and add 1. If directory doesn't exist yet, count = 1.

```bash
ls _meta/runtime/<sid>/router-step-10a-*.json 2>/dev/null | wc -l
```

### 3. Build JSON payload

Use this schema (matches R12 trail spec):

```json
{
  "schema_version": "r12",
  "session_id": "<sid>",
  "subagent": "<subagent>",
  "step": "<step>",
  "step_name": "<step-name>",
  "timestamp": "<ISO-8601 UTC now>",
  "trigger_count_in_session": <N + 1>,
  "fresh_invocation": true,
  "input_summary": "<input>",
  "output_summary": "<output>",
  "payload": "<payload or null>",
  "status": "success" | "partial" | "failed",
  "value_invocations": []
}
```

Set `status`:
- `success` if output_summary contains no "failed" / "error" markers
- `partial` if output_summary mentions any failure but also any success
- `failed` if everything failed

### 4. Write JSON

Use the `Write` tool to create the file. Ensure parent directory exists first (use `Bash` `mkdir -p _meta/runtime/<sid>/` if needed).

### 5. Report

Emit one line:
```
✅ Notion sync audit trail written: _meta/runtime/<sid>/notion-sync-<ts>.json (status: <status>)
```

## HARD RULES

- **Cannot be invoked without `--sid`, `--input`, `--output`** — abort with error message if any missing.
- **Do NOT attempt to call Notion MCP from this slash command.** That is ROUTER's job in the main context (Step 10a per `pro/CLAUDE.md`).
- **`fresh_invocation` MUST be `true`** — every Step 10a sync is a fresh invocation per R12 rule (no reuse, no "as above").
- **Per pro/CLAUDE.md Step 10a outbound boundary**: The actual Notion MCP call is intercepted by content scan policy (v1.8.5: now LLM-native check, not hook-based). ROUTER MUST check the payload against `references/outbound-pii-patterns.md` BEFORE calling Notion MCP, and emit pass/warn/block verdict in the input_summary field of this trail.

## v1.8.5 changes vs v1.8.4 scripts/notion-sync.sh

- v1.8.4: bash script reads `scripts/lib/audit-trail.sh` helper, writes JSON via shell heredoc.
- v1.8.5: ROUTER writes JSON directly via `Write` tool. Zero bash dependency. PII scan is LLM-prompt-driven (not hook-based) — see `references/outbound-pii-patterns.md` for pattern groups A-E.
