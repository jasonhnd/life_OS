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

Three methodologies fused: **GTD drives action, PARA organizes structure, Zettelkasten lets knowledge grow.**

```
second-brain/
│
├── inbox/                          # GTD entry: unprocessed items land here first
│
├── projects/                       # PARA·P: things with goals and deadlines
│   └── {project}/
│       ├── index.md               # Goals, status, related areas
│       ├── tasks/                 # next actions
│       ├── decisions/             # Three Departments and Six Ministries memorials
│       ├── notes/                 # Working notes
│       └── research/              # Project-specific research
│
├── areas/                          # PARA·A: ongoing life areas to maintain
│   └── {area}/
│       ├── index.md               # Direction, related projects, current status
│       ├── goals.md               # Goals
│       └── tasks/                 # Area tasks not belonging to any project
│
├── zettelkasten/                   # Knowledge growth
│   ├── fleeting/                  # Fleeting ideas
│   ├── literature/                # What you read, what you learned
│   └── permanent/                 # Your own insights, interlinked
│
├── records/                        # Life data
│   ├── journal/                   # Journals, morning court briefings, reviews, Censorate/Remonstrator reports
│   ├── meetings/
│   ├── contacts/
│   ├── finance/
│   └── health/
│
├── gtd/                            # GTD system
│   ├── waiting/                   # Waiting on others
│   ├── someday/                   # Someday/maybe
│   └── reviews/                   # Weekly/monthly reviews
│
├── archive/                        # Completed projects move here
│
└── templates/
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
| Decision memorials | `projects/{p}/decisions/` or `areas/{a}/decisions/` |
| Action items | `projects/{p}/tasks/` or `areas/{a}/tasks/` |
| Reviews / Censorate / Remonstrator reports | `records/journal/` |
| Research analysis | `projects/{p}/research/` or `zettelkasten/literature/` |
| General insights | `zettelkasten/permanent/` |
| Goals | `areas/{a}/goals.md` |

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

Global snapshot, overwritten by CC at the end of each session. Contains: things in progress, recent key decisions, open questions, this week's focus.

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
2. Read ~/second-brain/projects/ and areas/ index.md files (current status)
3. Search second-brain/projects/*/decisions/ for relevant historical decisions
4. Read user-patterns.md
5. Check Notion 📬 Inbox (new messages from mobile) → pull into second-brain/inbox/
6. Platform awareness + version check
```

### Wrap-Up Mode (End of Process)

```
1. Memorials → second-brain/projects/{p}/decisions/ or areas/{a}/decisions/
2. Action items → second-brain/projects/{p}/tasks/ or areas/{a}/tasks/
3. Censorate reports → second-brain/records/journal/
4. Remonstrator reports → second-brain/records/journal/
5. Update user-patterns.md
6. git add + commit + push (to second-brain repo)
7. Sync Notion: update 🧠 Current Status + 📝 relevant topic Working Memory
```

### Review Mode

```
1. Traverse second-brain/projects/*/tasks/ to compute completion rates
2. Read second-brain/areas/*/goals.md for goal progress
3. Read second-brain/records/journal/ recent journals
4. Read second-brain/gtd/reviews/ last review record
5. Metrics dashboard computed from files
```

## Prime Minister History Lookup

The Prime Minister no longer queries data directly — the Morning Court Official's housekeeping mode has all context ready.

## Remonstrator Data Retrieval

```
1. Read user-patterns.md
2. Read second-brain/records/journal/ last 3 Remonstrator reports
3. Read second-brain/projects/*/decisions/ last 5 decisions
4. Traverse second-brain/projects/*/tasks/ to compute completion rates
```

## Degradation Rules

- second-brain repo unreachable → annotate "⚠️ second-brain unavailable, this session's output not archived"
- Notion unavailable → only affects mobile sync, does not affect core functionality
- Both unavailable → operates normally, output displayed in conversation but not persisted
