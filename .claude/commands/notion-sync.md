---
description: After ROUTER calls the Notion MCP at Step 10a (archiver Phase 4 → Notion sync), write the markdown audit trail to meta/runtime/<sid>/notion-sync.md. Replaces v1.8.4 scripts/notion-sync.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[--sid SID] [--input SUMMARY] [--output SUMMARY] [--payload TEXT]"
allowed-tools:
  - Write
  - Read
  - Glob
---

# /notion-sync

You are writing the audit trail for ROUTER's Step 10a Notion MCP sync operation. **This command does NOT call the Notion MCP itself** — ROUTER calls Notion MCP directly in the main context (because subagents cannot access environment-specific MCP tools). This command only records what ROUTER observed, as a **markdown audit trail with YAML frontmatter** per `references/audit-trail-spec.md` (R13).

## Inputs

Parse `$ARGUMENTS` for:
- `--sid SID` (required) — runtime session id; if absent, abort with error
- `--input SUMMARY` (required) — input summary observed by ROUTER (e.g. "session 2026-05-22 archive sync to 4 Notion entities")
- `--output SUMMARY` (required) — output summary (e.g. "3/4 succeeded; todo_database_id failed: missing permission")
- `--payload TEXT` (optional) — literal payload or details to store
- `--payload-file PATH` (optional) — read payload from file
- `--subagent NAME` (optional, default: `notion-sync`) — trail actor
- `--step STEP` (optional, default: `step-10a`) — trail step id
- `--step-name NAME` (optional, default: `ROUTER Notion MCP Sync`) — human-readable step name

## Procedure

### 1. Compute path
```
target_dir  = meta/runtime/<sid>/
target_file = meta/runtime/<sid>/notion-sync.md
```
- `<sid>` is the session id from `--sid`.
- Per `references/audit-trail-spec.md` §"Notion Sync", the Step 10a trail file is `notion-sync.md`. It MUST be markdown — a `.json` or `.yml` file in `meta/runtime/<sid>/` is an `F4 SCOPE_FAILURE` (md-only / DR-10).

### 2. Determine trigger_count_in_session
Per `references/audit-trail-spec.md`, count existing audit trail entries for this subagent in `meta/runtime/<sid>/` (use `Glob` on `meta/runtime/<sid>/notion-sync*.md`) and add 1. If the directory doesn't exist yet, count = 1.

### 3. Set status
Derive `status` from the output summary:
- `success` if output_summary contains no "failed" / "error" markers
- `partial` if output_summary mentions any failure but also any success
- `failed` if everything failed

### 4. Write the markdown trail

Use the `Write` tool to create `meta/runtime/<sid>/notion-sync.md` with this structure (R13 schema per `references/audit-trail-spec.md`). The `Write` tool creates the parent directory automatically.

```markdown
---
subagent: <subagent>
step_or_phase: <step>
step_name: <step-name>
started_at: <ISO8601>
ended_at: <ISO8601>
input_summary: "<input>"
tool_calls:
  - tool: <Notion MCP op, or N/A when MCP unavailable>
    args: "<short arg summary>"
    result_summary: "<short result summary>"
    exit_code: 0
llm_reasoning: "<short summary of sync outcome + outbound PII verdict>"
output_summary: "<output>"
tokens:
  input: 0
  output: 0
fresh_invocation: true
trigger_count_in_session: <N + 1>
audit_trail_version: v1.8.6-r13
value_invocations: []
---

# notion-sync · step-10a

## What this step did

<2-3 sentence narrative: which configured Notion entities synced, the per-entity outcome, and the outbound PII verdict (pass / warn / block).>

## Key tool calls

<bullet list expanding the tool_calls frontmatter into readable form>

## Reasoning

<expanded llm_reasoning, 1-2 sentences>
```

### 5. Report

Emit one line:
```
✅ Notion sync audit trail written: meta/runtime/<sid>/notion-sync.md (status: <status>)
```

## HARD RULES

- **Cannot be invoked without `--sid`, `--input`, `--output`** — abort with error message if any missing.
- **Do NOT attempt to call Notion MCP from this slash command.** That is ROUTER's job in the main context (Step 10a per `pro/CLAUDE.md`).
- **`fresh_invocation` MUST be `true`** — every Step 10a sync is a fresh invocation per the trail spec (no reuse, no "as above").
- **Output MUST be `.md`, never `.json`** — `references/audit-trail-spec.md` R13 stores trails as markdown with YAML frontmatter. A `.json` / `.yml` file in `meta/runtime/<sid>/` is an `F4 SCOPE_FAILURE`.
- **Per pro/CLAUDE.md Step 10a outbound boundary**: ROUTER MUST scan the payload against `references/outbound-pii-patterns.md` BEFORE calling Notion MCP (inline LLM scan since v1.8.5, not hook-based) and record the pass / warn / block verdict in `llm_reasoning`.

## v1.8.5 / v1.8.6 changes vs v1.8.4 scripts/notion-sync.sh

- v1.8.4: bash script reads `scripts/lib/audit-trail.sh` helper, writes JSON via shell heredoc.
- v1.8.5: ROUTER writes the trail directly via the `Write` tool. Zero bash dependency. PII scan is inline LLM-prompt-driven (not hook-based) — see `references/outbound-pii-patterns.md` for pattern groups A-E.
- v1.8.6: trail format migrated from R12 JSON to R13 markdown + YAML frontmatter (`notion-sync.md`, not `notion-sync-<ts>.json`) per the md-only ontological constraint — no `.json` files in the vault.
