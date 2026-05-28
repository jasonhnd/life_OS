# Adapter: Notion

Translates standard data model operations into Notion databases and pages via Notion MCP.

## Notion Structure

Notion serves as both a full storage backend (when chosen) and a transport layer (when used alongside GitHub/GDrive).

### As Full Backend (Notion only)

All 6 data types map to Notion databases:

| Data Type | Notion Database |
|-----------|----------------|
| Decision | 🤔 Decisions |
| Task | ✅ Tasks |
| JournalEntry | 📓 Journal |
| WikiNote | 📚 Wiki |
| Project | 🎯 Projects |
| Area | 🌊 Areas |

### As Transport Layer (alongside GitHub/GDrive)

Only 3 components used:
- 📬 Inbox (database): message queue between devices
- 🧠 Status Dashboard (page): mirror of `meta/STATUS.md`
- 🗄️ Archive: read-only archive access

**Important**: In transport mode, Notion does NOT have Task/Decision/Journal databases. If the user edits content directly in Notion outside of the inbox, those changes are invisible to the sync protocol. The RETROSPECTIVE should remind the user on first setup: "In transport mode, use the 📬 Inbox for all mobile captures. Direct edits to Notion pages outside the inbox will not sync to GitHub/GDrive."

## Field Mapping

### Decision → 🤔 Decisions

| Standard Field | Notion Property | Notion Type |
|---------------|----------------|-------------|
| id | ID | Text |
| title | Title | Title |
| type | Type | Select: change / no_change / escalation / superseded |
| projects | Projects | Relation → Projects |
| domains | Domains | Multi-select: governance / execution / finance / infra / people / growth |
| reviewed_by | Reviewed By | Text |
| reviewed_at | Date | Date |
| decision | Decision | Text |
| rationale | Rationale | Text |
| applied_methods | Applied Methods | Relation → Methods |
| journal_date | Journal Date | Date |
| content | Page body | Page content |

### Task → ✅ Tasks

| Standard Field | Notion Property | Notion Type |
|---------------|----------------|-------------|
| title | Title | Title |
| status | Status | Select: To Do / In Progress / Waiting / Done / Cancelled |
| priority | Priority | Select: P0 / P1 / P2 / P3 |
| due_date | Due Date | Date |
| context | Context | Select |
| energy | Energy | Select |
| project | Project | Relation → Projects |
| area | Area | Relation → Areas |

### JournalEntry → 📓 Journal

| Standard Field | Notion Property | Notion Type |
|---------------|----------------|-------------|
| date | Date | Date (also the title) |
| projects | Projects | Relation → Projects |
| session_ids | Session IDs | Multi-select |
| type_tags | Type Tags | Multi-select: briefing / dream / advisor / auditor / migration / … |
| referenced_decisions | Referenced Decisions | Relation → Decisions |
| referenced_methods | Referenced Methods | Relation → Methods |
| content | Page body | Page content |

### WikiNote → 📚 Wiki

| Standard Field | Notion Property | Notion Type |
|---------------|----------------|-------------|
| title | Title | Title |
| tags | Tags | Multi-select |
| content | Page body | Page content |

### Project → 🎯 Projects

| Standard Field | Notion Property | Notion Type |
|---------------|----------------|-------------|
| name | Name | Title |
| status | Status | Select |
| priority | Priority | Select |
| deadline | Deadline | Date |
| area | Area | Relation → Areas |

### Area → 🌊 Areas

| Standard Field | Notion Property | Notion Type |
|---------------|----------------|-------------|
| name | Name | Title |
| description | Description | Text |
| status | Status | Select |
| review_cycle | Review Cycle | Select |

## Operations

All operations use Notion MCP tools.

### Save(type, data)
1. Map fields to Notion properties per mapping table above
2. `notion-create-pages` with parent = the corresponding database
3. Body content → page content

### Update(type, id, data)
1. `notion-update-page` with page_id and changed properties
2. Body content changes → `update_content` command

### Archive(type, id)
1. Update status to archived/done
2. Or move page to Archive database via `notion-move-pages`

### Read(type, id)
1. `notion-fetch` with page ID
2. Map Notion properties back to standard fields

### List(type, filters)
1. `notion-search` or `notion-query-database-view` on the corresponding database
2. Map results back to standard fields

### Search(keyword)
1. `notion-search` with query = keyword
2. Map results back to standard fields, annotate source database

### ReadProjectContext(project_id)
1. Read the project page
2. Query tasks filtered by project relation
3. Query decisions filtered by project
4. Query journal filtered by project

## Change Detection

For sync: `notion-search` or `notion-query-database-view` filtering by `last_edited_time > last_sync_time`

## Deletion

Same principle: soft delete by changing status. Do not use `notion-move-pages` to trash until user confirms.

## Setup

User needs:
1. Notion MCP connected (Claude.ai: Settings → Connected Apps → Notion. Claude Code: MCP config)
2. Create the required databases in Notion (or use provided templates)
3. Database IDs are discovered at runtime via `notion-search` by name — no hardcoding
