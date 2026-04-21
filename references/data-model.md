# Standard Data Model

All Life OS data operations use these standard types and interfaces. Adapters translate them to platform-specific calls.

## Data Types

### Decision

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | auto | Unique identifier (filename or database ID) |
| title | string | yes | Subject (≤20 chars) |
| type | enum | yes | `simple` / `3d6m` (Draft-Review-Execute and Six Domains) |
| domains | string[] | no | Activated domains |
| score | number | no | Composite score (1-10) |
| veto_count | number | no | Number of REVIEWER vetoes |
| status | enum | yes | `considering` / `decided` / `reversed` |
| category | enum | no | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | no | `good` / `neutral` / `bad` / `tbd` |
| date | date | yes | Decision date |
| project | string | no | Associated project |
| area | string | no | Associated area |
| last_modified | datetime | auto | Last modification timestamp |
| content | text | yes | Summary report full text (body) |

### Task

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | auto | |
| title | string | yes | Task name |
| status | enum | yes | `todo` / `in-progress` / `waiting` / `done` / `cancelled` |
| priority | enum | no | `p0` / `p1` / `p2` / `p3` |
| due_date | date | no | Deadline |
| context | enum | no | `computer` / `phone` / `home` / `office` / `call` / `errand` |
| energy | enum | no | `high` / `medium` / `low` |
| project | string | no | Associated project |
| area | string | no | Associated area |
| last_modified | datetime | auto | |

### JournalEntry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | auto | |
| title | string | yes | Entry title |
| date | date | yes | Entry date |
| type | enum | yes | `morning-court` / `censorate` / `remonstrator` / `inspection` / `manual` |
| mood | enum | no | `great` / `good` / `neutral` / `low` / `bad` |
| energy | enum | no | `high` / `medium` / `low` |
| tags | string[] | no | |
| last_modified | datetime | auto | |
| content | text | yes | Report full text (body) |

### WikiNote

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | auto | |
| title | string | yes | Note title |
| tags | string[] | no | |
| links | string[] | no | Wikilinks to other notes |
| last_modified | datetime | auto | |
| content | text | yes | Note body |

### Project

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | auto | |
| name | string | yes | Project name |
| status | enum | yes | `planning` / `active` / `on-hold` / `done` / `dropped` |
| priority | enum | no | `p0` / `p1` / `p2` / `p3` |
| deadline | date | no | |
| area | string | no | Associated area |
| last_modified | datetime | auto | |
| outcome | text | no | Result description |

### Area

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | auto | |
| name | string | yes | Area name |
| description | text | no | |
| status | enum | yes | `active` / `inactive` |
| review_cycle | enum | no | `weekly` / `monthly` / `quarterly` |
| last_modified | datetime | auto | |
| goals | text | no | Goals description |

### StrategicLine

Stored in `_meta/strategic-lines.md` (user's second-brain). Multiple lines separated by `---`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique identifier (kebab-case) |
| name | string | yes | Display name |
| purpose | text | yes | One-sentence formal purpose |
| driving_force | text | no | What truly drives investment in this line (can differ from purpose) |
| health_signals | text[] | no | What signals indicate this line is healthy (AI proposes, user confirms) |
| time_window | date | no | Deadline affecting the entire line |
| area | string | no | Associated life area |
| created | date | auto | Creation date |

### Per-Project Strategic Fields

Optional extension to `projects/{project}/index.md` frontmatter. All fields default to empty/null.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| strategic.line | string | no | Strategic line ID (references `_meta/strategic-lines.md`) |
| strategic.role | enum | no | `critical-path` / `enabler` / `accelerator` / `insurance` |
| strategic.flows_to[] | array | no | Outgoing flows: [{target, type, description}] |
| strategic.flows_from[] | array | no | Incoming flows: [{source, type, description}] |
| strategic.last_activity | date | auto | Last modification date (auto-updated by ARCHIVER) |
| strategic.status_reason | text | no | Why this project is in its current status |

Flow types: `cognition` / `resource` / `decision` / `trust`. Role and flow definitions: `references/strategic-map-spec.md`.

---

## v1.7 Cortex Data Types

The following types are introduced in v1.7 for the Cortex cognitive layer. Each has its own authoritative spec file; this table is the short form that `tools/lib/second_brain.py` dataclasses consume.

### SessionSummary

Authoritative spec: `references/session-index-spec.md` §3.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | yes | Format `{platform}-{YYYYMMDD}-{HHMM}` |
| date | date | yes | ISO 8601 date |
| started_at | datetime | yes | Timezone-aware timestamp |
| ended_at | datetime | yes | Timezone-aware timestamp |
| duration_minutes | integer | yes | |
| platform | enum | yes | `claude` / `gemini` / `codex` |
| theme | enum | yes | Theme ID (e.g. `zh-classical`, `ja-kasumigaseki`) |
| project | string | yes | Bound project (enforces session-binding HARD RULE) |
| workflow | enum | yes | `full_deliberation` / `express_analysis` / `direct_handle` / `strategist` / `review` |
| subject | string | yes | Extracted subject (max 200 chars) |
| domains_activated | string[] | no | Subset of PEOPLE/FINANCE/GROWTH/EXECUTION/GOVERNANCE/INFRA |
| overall_score | number | no | 0-10 from Summary Report |
| domain_scores | map | no | Per-domain 0-10 scores |
| veto_count | integer | no | REVIEWER veto events |
| council_triggered | boolean | no | COUNCIL debate fired? |
| soul_dimensions_touched | string[] | no | SOUL dimension IDs referenced |
| wiki_written | string[] | no | Wiki entry IDs auto-written this session |
| methods_used | string[] | no | Method IDs applied |
| methods_discovered | string[] | no | New method IDs archived |
| concepts_activated | string[] | no | Concept IDs referenced |
| concepts_discovered | string[] | no | New concept IDs written by archiver Phase 2 |
| dream_triggers | string[] | no | DREAM REM trigger names fired |
| keywords | string[] | no | Up to 10, for hippocampus Wave 1 scan |
| action_items | array | no | `[{text, deadline, status}]` |
| compliance_violations | integer | no | AUDITOR-flagged violations |

Storage: `_meta/sessions/{session_id}.md`. Immutable after archiver writes.

### Concept

Authoritative spec: `references/concept-spec.md` §YAML Frontmatter Schema.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| concept_id | string | yes | Lowercase + hyphens, ≤64 chars, unique |
| canonical_name | string | yes | Human-readable display name |
| aliases | string[] | no | Alternative surface forms |
| domain | enum | yes | `finance` / `startup` / `personal` / `technical` / `method` / `relationship` / `health` / `legal` / user-extensible |
| status | enum | yes | `tentative` / `confirmed` / `canonical` |
| permanence | enum | yes | `identity` / `skill` / `fact` / `transient` |
| activation_count | integer | yes | Monotonic during active life |
| last_activated | datetime | yes | Used by decay pass |
| created | datetime | yes | Creation timestamp |
| outgoing_edges | array | no | `[{to: concept_id, weight: 1-100, via: [tag], last_reinforced: ISO}]` |
| provenance.source_sessions | string[] | no | Session IDs where evidence appeared |
| provenance.extracted_by | enum | no | `archiver` / `manual` / `dream` |
| decay_policy | enum | yes | Matches `permanence` tier |

Storage: `_meta/concepts/{domain}/{concept_id}.md` (confirmed/canonical) or `_meta/concepts/_tentative/{concept_id}.md` (tentative).

### SoulSnapshot

Authoritative spec: `references/snapshot-spec.md` §YAML Frontmatter Schema.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| snapshot_id | string | yes | `{YYYY-MM-DD-HHMM}`, matches filename |
| captured_at | datetime | yes | Real ISO 8601 timestamp from system clock |
| session_id | string | yes | References `_meta/sessions/{session_id}.md` |
| previous_snapshot | string \| null | yes | Prior filename or null for first snapshot |
| dimensions | array | yes | `[{name, confidence: 0-1, evidence_count, challenges, tier}]` where tier ∈ `core`/`secondary`/`emerging` |

Storage: `_meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md`. Local-only (not Notion-synced). Metadata only — no SOUL body content. Immutable.

### EvalEntry

Authoritative spec: `references/eval-history-spec.md` §3.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| eval_id | string | yes | `{YYYY-MM-DD-HHMM}-{project}` |
| session_id | string | yes | References `_meta/sessions/` entry |
| evaluator | enum | yes | `auditor` / `auditor-patrol` |
| evaluation_mode | enum | yes | `decision-review` / `patrol-inspection` |
| date | datetime | yes | |
| scores | map | yes | 10 dimensions, each 0-10 integer (see eval-history-spec §5) |
| violations | array | no | `[{type, agent, severity, detail}]` |
| agent_quality_notes | map | no | Per-agent one-line observations |

Storage: `_meta/eval-history/{YYYY-MM-DD}-{project}.md`. Local-only. Immutable after creation. No migration backfill.

### Soul

Authoritative spec: `references/soul-spec.md`. Unlike the other v1.7 types, `Soul` is the **in-memory view of the live `SOUL.md` file**, not a per-record file. Tools read the whole SOUL.md, parse it into this structure, and (for archiver-side auto-writes) write back.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| path | Path | yes | Absolute path to `SOUL.md` |
| dimensions | `List[SoulDimension]` | yes | All parsed dimensions (may be empty for new users) |
| raw_body | str | yes | Full markdown body (for diff-based writes) |

`SoulDimension` sub-record:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | yes | Dimension name (e.g. "risk-tolerance") |
| confidence | float | yes | 0-1, auto-calculated via `evidence_count / (evidence_count + challenges × 2)` |
| evidence_count | int | yes | |
| challenges | int | yes | |
| source | enum | yes | `dream` / `advisor` / `strategist` / `user` |
| created | date | yes | YYYY-MM-DD |
| last_validated | date | yes | YYYY-MM-DD |
| tier | enum | auto | `core` (≥0.7) / `secondary` (0.3-0.7) / `emerging` (0.2-0.3) / `dormant` (<0.2) — derived at read time |
| what_is | str | no | Body section "What IS (实然)" |
| what_should_be | str | no | Body section "What SHOULD BE (应然)" |
| gap | str | no | Body section "Gap (差距)" |
| evidence | `List[str]` | no | Body section "Evidence" bullets |
| challenges_list | `List[str]` | no | Body section "Challenges" bullets |

Storage: single file `SOUL.md` at second-brain root. Read by every major role; written by ARCHIVER Phase 2 (auto-write criteria in soul-spec) and by user directly.

### Method

Authoritative spec: `references/method-library-spec.md` §4.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| method_id | string | yes | Lowercase + hyphens, unique |
| name | string | yes | Display name |
| description | string | yes | One-liner for INDEX.md |
| domain | enum | yes | Same domain vocabulary as Concept |
| status | enum | yes | `tentative` / `confirmed` / `canonical` |
| confidence | number | yes | 0-1, formula `evidence_count / (evidence_count + challenges × 2)` |
| times_used | integer | yes | Increments every session that applies the method |
| last_used | datetime | no | ISO 8601 |
| applicable_when | array | no | `[{condition, signal}]` |
| not_applicable_when | array | no | `[{condition}]` |
| source_sessions | string[] | no | session_ids that contributed |
| evidence_count | integer | yes | Sessions where the method worked |
| challenges | integer | yes | Sessions where it failed |
| related_concepts | string[] | no | concept_ids |
| related_methods | string[] | no | method_ids (soft composition) |

Storage: `_meta/methods/{domain}/{method_id}.md` or `_meta/methods/_tentative/{method_id}.md`. Local-only.

---

## Standard Operations

All agents use these operations. Adapters translate them to platform-specific calls.

| Operation | Signature | Description |
|-----------|-----------|-------------|
| **Save** | `Save(type, data)` | Create a new record |
| **Update** | `Update(type, id, data)` | Modify an existing record |
| **Archive** | `Archive(type, id)` | Move to archive |
| **Read** | `Read(type, id)` | Get a single record |
| **List** | `List(type, filters)` | Get records matching filters |
| **Search** | `Search(keyword)` | Full-text search across all types |
| **ReadProjectContext** | `ReadProjectContext(project_id)` | Batch read: project index + tasks + decisions + journal |

---

## Multi-Backend Rules

### Backend Selection

Users choose 1, 2, or 3 backends. When multiple are selected, one is automatically designated as **primary** (reads + writes), others are **sync** (writes only).

**Auto-selection rule**: GitHub > Google Drive > Notion

| Config | Primary | Sync |
|--------|---------|------|
| GitHub only | GitHub | — |
| GDrive only | GDrive | — |
| Notion only | Notion | — |
| GitHub + Notion | GitHub | Notion |
| GitHub + GDrive | GitHub | GDrive |
| GDrive + Notion | GDrive | Notion |
| All three | GitHub | GDrive + Notion |

### Write Order

1. Write to primary backend first
2. Then write to each sync backend in order
3. If any sync backend fails → annotate `⚠️ [backend] write failed`, log to `_meta/sync-log.md`, continue with others
4. Next session auto-retries failed writes

### Read Order

1. Read from primary backend
2. If primary unavailable or search returns nothing → try sync backends in order
3. Search results annotate which backend they came from

---

## Sync Protocol

### Session Start (RETROSPECTIVE Housekeeping)

```
0. Read _meta/config.md → get backend list and last sync timestamp
1. Probe each configured backend for availability:
   - GitHub: check if git repo is accessible (git status)
   - GDrive: check if Google Drive MCP is connected (attempt list)
   - Notion: check if Notion MCP is connected (attempt search)
   Mark unavailable backends as SKIPPED for this session.
   If primary is unavailable, temporarily promote the next available backend.
   Log: "💾 Backends: GitHub ✅ | GDrive ❌ (MCP not connected) | Notion ✅"
2. For each AVAILABLE sync backend:
   - Query "items modified since [this platform's last_sync_time]"
   - GitHub: git log --since
   - GDrive: modifiedTime > last_sync_time
   - Notion: last_edited_time > last_sync_time
3. Compare changes:
   - Only one backend changed an item → adopt it
   - Two backends changed the same item → last_modified wins
   - Time difference < 1 minute → mark as CONFLICT, keep both versions
4. Apply winning changes to primary backend
5. Push primary state to all sync backends
6. Update _meta/sync-log.md with sync results
7. Update this platform's last_sync_time in _meta/config.md (do not touch other platforms' timestamps)
```

### Session End (RETROSPECTIVE Wrap-up)

```
1. Write all outputs to primary backend
2. Write all outputs to each sync backend
3. Update _meta/config.md last_sync_time
4. Any backend failure → log, don't block
```

---

## Conflict Resolution

| Situation | Action |
|-----------|--------|
| One backend changed | Adopt the change |
| Two backends changed same item, time diff > 1 min | Last_modified wins (last write wins) |
| Two backends changed same item, time diff ≤ 1 min | CONFLICT: keep both versions, ROUTER asks user to choose |
| User resolves conflict | Winning version pushed to all backends |

---

## Deletion Rules

- **Deletion does NOT sync across backends**
- When an item is deleted on one backend → other backends mark it `_deleted: true` (soft delete)
- Next session, ROUTER asks user: "Item X was deleted on [backend]. Delete from all backends?"
- User confirms → hard delete everywhere
- User declines → restore on the backend where it was deleted

---

## Failure Handling

| Scenario | Handling |
|----------|---------|
| Backend offline during write | Skip that backend, annotate ⚠️, log to sync-log.md. Next session auto-retries. |
| Crash mid-sync | Next startup: compare last_modified across all backends, detect inconsistencies, auto-repair from newest. |
| Data corrupted on one backend | ROUTER detects anomaly, asks user: "Restore from [other backend]?" |
| New device | Config lives in _meta/config.md. Git clone → config ready. No second-brain → session-level config. |
| Add new backend | ROUTER asks: "Sync existing data from [primary] to [new backend]?" |
| Remove backend | ROUTER asks: "Keep data on [removed backend] or clean up?" |

---

## Configuration

Stored in `_meta/config.md` (in second-brain repo):

```yaml
storage:
  backends:
    - type: github
      role: primary
    - type: notion
      role: sync
  sync_log:
    - platform: claude-code
      last_sync: "2026-04-10T15:30:00Z"
    - platform: gemini-cli
      last_sync: "2026-04-10T14:00:00Z"
```

**Per-platform sync timestamps**: Each platform records its own `last_sync` time. When Gemini CLI starts a session, it reads **its own** `last_sync` and queries for changes since that time — not since Claude Code's last sync. This prevents missed changes when the user alternates between platforms.

No second-brain → config stored in session context, ROUTER asks each new session.

---

## Constraints

- **Multiple sessions can operate the second-brain simultaneously** using the outbox pattern. Each session writes to its own outbox directory (`_meta/outbox/{session_id}/`). The next session to start court merges all outboxes into the main structure. Direct writes to shared files (STATUS.md, user-patterns.md, index.md) only happen during the outbox merge step at Start Court.
- **Session-id format**: `{platform}-{YYYYMMDD}-{HHMM}`, generated at adjourn time (not session start). Example: `claude-20260412-1700`, `gemini-20260412-1900`.
- **Outbox merge lock**: During merge, write `_meta/.merge-lock`. If it exists and is < 5 minutes old, skip merge and proceed normally. Delete after merge completes.
- **Empty sessions**: If a session has no output (no decisions, tasks, or journal entries), do not create an outbox.
- Mobile devices write through Notion inbox or GDrive inbox, not directly to structured data
- All adapters must support the 7 standard operations

### Outbox Manifest Format

Each outbox directory contains a `manifest.md`:

```yaml
---
session_id: "claude-20260412-1700"
platform: claude-code
model: opus
projects: [project-a, project-b]
adjourned: "2026-04-12T17:00:00+09:00"
outputs:
  decisions: 2
  tasks: 5
  journal: 3
  wiki: 1
  dream: 1
  index_delta: true
  patterns_delta: true
---
```

### Index Delta Format

`index-delta.md` records changes to apply to `projects/{project}/index.md`:

```markdown
# Index Delta

## Target: projects/my-project/index.md
## Fields to update:
- Phase: "v5.4 deployed"
- Current focus: "打磨计划书到对外版本"
```

### Patterns Delta Format

`patterns-delta.md` records content to append to `user-patterns.md`:

```markdown
# Patterns Delta — append to user-patterns.md

### [2026-04-12] New pattern: decision speed increasing
Source: ADVISOR
Observation: Last 3 decisions made after first round of clarification.
```
