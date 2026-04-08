# Data Layer Architecture

All agents refer to this file when reading or writing data.

## Dual-Layer Storage

- **GitHub second-brain (disk)**: Source of truth, stores all complete records and history
- **Notion (memory)**: Lightweight working memory, stores only the context of currently active topics, supports in-depth discussions from mobile
- **CC (Prime Minister / Morning Court Official) is the only role that touches both sides**, responsible for all synchronization

## Data Channels

```
Mobile: Claude.ai ↔ Notion MCP (chat and store here)
Desktop: CC ↔ GitHub second-brain + Notion MCP (CC handles all sync)
```

## Sync Rules

**git commit = Notion update, mechanically bound, no judgment needed.**

Whenever the second-brain repo has file changes, sync to Notion. Pure chat discussions that don't produce files do not trigger sync.

---

## GitHub Directory Structure

```
second-brain/
│
├── inbox/                             # 📥 Unprocessed (mobile captures, materials, book notes, raw research)
│
├── _meta/                             # 🔧 System metadata
│   ├── STATUS.md                      # Global status snapshot
│   ├── MAP.md                         # Knowledge map
│   ├── decisions/                     # Cross-domain major decisions
│   ├── journal/                       # Morning court briefings, Censorate/Remonstrator reports
│   ├── extraction-rules.md            # Extraction rules
│   ├── extraction-log.md              # Extraction log
│   ├── lint-rules.md                  # Quality check rules
│   ├── lint-state.md                  # Quality check state
│   ├── lint-reports/                  # Quality check reports
│   └── roles/                         # System role definitions
│       ├── censor.md                  # Censorate role
│       ├── historian.md               # Historian role
│       └── reviewer.md                # Reviewer role
│
├── projects/                          # 🎯 Things with endpoints
│   └── {name}/
│       ├── index.md                   # Goals, status, related areas
│       ├── tasks/                     # Next actions
│       ├── decisions/                 # Project-specific decisions/memorials
│       ├── research/                  # Project-specific research
│       └── journal/                   # Project-specific logs
│
├── areas/                             # 🌊 Ongoing life areas
│   └── {name}/
│       ├── index.md                   # Direction, related projects, current status
│       ├── goals.md                   # Goals
│       ├── tasks/                     # Area tasks not belonging to any project
│       └── notes/                     # Area notes
│
├── wiki/                              # 📚 Cross-domain knowledge network
│
├── archive/                           # 🗄️ Completed project archives
│
└── templates/                         # 📋 Templates
```

## Area List (areas/)

```
areas/
├── career/        # Career development
├── product/       # Product & entrepreneurship
├── finance/       # Financial management
├── health/        # Health
├── family/        # Family
├── social/        # Social relationships
├── learning/      # Learning
├── ops/           # Life operations
├── creation/      # Creative work
├── spirit/        # Spiritual well-being
└── work-project/  # Current work project (example)
```

---

## Three Departments and Six Ministries Output Destinations

| Output | GitHub Path |
|--------|------------|
| Decision memorials (project-specific) | `projects/{p}/decisions/` |
| Decision memorials (cross-domain) | `_meta/decisions/` |
| Action items (project) | `projects/{p}/tasks/` |
| Action items (area) | `areas/{a}/tasks/` |
| Morning court briefings | `_meta/journal/` |
| Censorate / Remonstrator reports | `_meta/journal/` |
| Project research | `projects/{p}/research/` |
| Cross-domain knowledge | `wiki/` |
| Goals | `areas/{a}/goals.md` |
| Global status snapshot | `_meta/STATUS.md` |

---

## Notion Memory (4 Components)

### 📬 Inbox (Database)

Message queue for passing information between mobile and desktop.

| Field | Type | Description |
|-------|------|-------------|
| Content | Title | A sentence or key points |
| Source | Select | Mobile / Desktop |
| Status | Select | Pending / Synced |
| Time | Created time | Automatic |

### 🧠 Current Status (Page)

Global snapshot, overwritten by CC at the end of each session. Mirrors `_meta/STATUS.md`. Contains: things in progress, recent key decisions, open questions, this week's focus.

### 📝 Working Memory (Topic Pages)

One page per active topic. Contains: background, current stage, key decisions, technical ideas, open questions, next steps. About 5-10 active topics. When no longer active, archived to GitHub and deleted from Notion.

### 📋 Todo Board (Database)

Active task list synced from second-brain's tasks/. Viewable and checkable on mobile; CC syncs back to GitHub in the next session.

| Field | Type | Description |
|-------|------|-------------|
| Task | Title | Task name |
| Project | Select | Parent project |
| Status | Select | Todo / In Progress / Done |
| Priority | Select | P0 / P1 / P2 |
| Due | Date | Due date |

---

## Morning Court Official Data Operations

### Housekeeping Mode (Start of Conversation)

```
1. Read ~/second-brain/inbox/ (unprocessed items)
2. Read ~/second-brain/_meta/STATUS.md (global status)
3. Read ~/second-brain/projects/{bound}/index.md (bound project status)
4. Read ~/second-brain/projects/{bound}/decisions/ (historical decisions)
5. Read ~/second-brain/projects/{bound}/tasks/ (active tasks)
6. Read user-patterns.md
7. Global overview: list all projects/ and areas/ index.md titles + status
8. Check Notion 📬 Inbox (new messages from mobile) → pull into second-brain/inbox/
9. Platform awareness + version check
```

### Wrap-Up Mode (End of Process)

```
1. Memorials → projects/{p}/decisions/ or _meta/decisions/ (cross-domain)
2. Action items → projects/{p}/tasks/ or areas/{a}/tasks/
3. Censorate reports → _meta/journal/
4. Remonstrator reports → _meta/journal/
5. Update _meta/STATUS.md (global status snapshot)
6. Update user-patterns.md
7. git add + commit + push (to second-brain repo)
8. Sync Notion: update 🧠 Current Status + 📝 relevant topic Working Memory + 📋 Todo Board
```

### Review Mode

```
1. Traverse projects/*/tasks/ to compute completion rates
2. Read areas/*/goals.md for goal progress
3. Read _meta/journal/ recent journals
4. Read _meta/STATUS.md for global state
5. Metrics dashboard computed from files
```

## Prime Minister History Lookup

The Prime Minister no longer queries data directly — the Morning Court Official's housekeeping mode has all context ready.

## Remonstrator Data Retrieval

```
1. Read user-patterns.md
2. Read _meta/journal/ last 3 Remonstrator reports
3. Read projects/*/decisions/ last 5 decisions
4. Traverse projects/*/tasks/ to compute completion rates
```

## Degradation Rules

- second-brain repo unreachable → annotate "⚠️ second-brain unavailable, this session's output not archived"
- Notion unavailable → only affects mobile sync, does not affect core functionality
- Both unavailable → operates normally, output displayed in conversation but not persisted
