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

Optional extension to `projects/{p}/index.md` frontmatter. All fields default to empty/null.

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

- **Multiple sessions can operate the second-brain simultaneously** using the outbox pattern. Each session writes to its own outbox directory (`_meta/outbox/{session-id}/`). The next session to start court merges all outboxes into the main structure. Direct writes to shared files (STATUS.md, user-patterns.md, index.md) only happen during the outbox merge step at Start Court.
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

`index-delta.md` records changes to apply to `projects/{p}/index.md`:

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
