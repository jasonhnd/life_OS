# Standard Data Model

All Life OS data operations use these standard types and interfaces. Adapters translate them to platform-specific calls.

## Data Types

### Decision

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | auto | Unique identifier (filename or database ID) |
| title | string | yes | Subject (≤20 chars) |
| type | enum | yes | `simple` / `3d6m` (Three Departments and Six Ministries) |
| ministries | string[] | no | Activated ministries |
| score | number | no | Composite score (1-10) |
| veto_count | number | no | Number of Chancellery vetoes |
| status | enum | yes | `considering` / `decided` / `reversed` |
| category | enum | no | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | no | `good` / `neutral` / `bad` / `tbd` |
| date | date | yes | Decision date |
| project | string | no | Associated project |
| area | string | no | Associated area |
| last_modified | datetime | auto | Last modification timestamp |
| content | text | yes | Memorial full text (body) |

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

### Session Start (Morning Court Official Housekeeping)

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

### Session End (Morning Court Official Wrap-up)

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
| Two backends changed same item, time diff ≤ 1 min | CONFLICT: keep both versions, Prime Minister asks user to choose |
| User resolves conflict | Winning version pushed to all backends |

---

## Deletion Rules

- **Deletion does NOT sync across backends**
- When an item is deleted on one backend → other backends mark it `_deleted: true` (soft delete)
- Next session, Prime Minister asks user: "Item X was deleted on [backend]. Delete from all backends?"
- User confirms → hard delete everywhere
- User declines → restore on the backend where it was deleted

---

## Failure Handling

| Scenario | Handling |
|----------|---------|
| Backend offline during write | Skip that backend, annotate ⚠️, log to sync-log.md. Next session auto-retries. |
| Crash mid-sync | Next startup: compare last_modified across all backends, detect inconsistencies, auto-repair from newest. |
| Data corrupted on one backend | Prime Minister detects anomaly, asks user: "Restore from [other backend]?" |
| New device | Config lives in _meta/config.md. Git clone → config ready. No second-brain → session-level config. |
| Add new backend | Prime Minister asks: "Sync existing data from [primary] to [new backend]?" |
| Remove backend | Prime Minister asks: "Keep data on [removed backend] or clean up?" |

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

No second-brain → config stored in session context, Prime Minister asks each new session.

---

## Constraints

- **Only one agent session should operate the second-brain at a time** — regardless of platform (Claude Code, Gemini CLI, Codex, Antigravity). If two sessions write to the same git repo simultaneously, merge conflicts will occur. The Morning Court Official must check for a lock before writing.
- **Session lock mechanism**: On session start, write `_meta/.lock` with `{platform, timestamp, session_id}`. On session end, delete it. If a lock exists and is <2 hours old, warn user: "⚠️ Another session ([platform]) may still be active. Proceed anyway?" If >2 hours old, treat as stale and overwrite.
- Mobile devices write through Notion inbox or GDrive inbox, not directly to structured data (unless using Method B full sync)
- All adapters must support the 7 standard operations
