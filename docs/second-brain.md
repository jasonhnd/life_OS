# Second Brain — Architecture and Setup

## Core Architecture

```
GitHub second-brain (disk) = Source of truth, complete records
Notion (memory) = Lightweight working memory, active topics on mobile
CC (Prime Minister / Morning Court Official) = The only role that touches both sides
```

### Data Channels

```
Mobile: Claude.ai ↔ Notion MCP
Desktop: CC ↔ GitHub second-brain + Notion MCP
```

### Sync Rules

**git commit = Notion update, mechanically bound.** File changes trigger sync; pure chat does not.

---

## GitHub second-brain Directory

Three methodologies fused: **GTD drives action, PARA organizes structure, Zettelkasten lets knowledge grow.**

```
second-brain/
├── inbox/                    # GTD entry: unprocessed items land here first
├── projects/{project}/       # PARA·P: things with goals and deadlines
│   ├── index.md             # Goals, status, related areas
│   ├── tasks/               # next actions
│   ├── decisions/           # Three Departments and Six Ministries memorials
│   ├── notes/               # Working notes
│   └── research/            # Project-specific research
├── areas/{area}/             # PARA·A: ongoing life areas to maintain
│   ├── index.md             # Direction, related projects
│   ├── goals.md             # Goals
│   └── tasks/               # Area tasks not belonging to a project
├── zettelkasten/             # Knowledge growth
│   ├── fleeting/            # Fleeting ideas
│   ├── literature/          # Input (what you read)
│   └── permanent/           # Output (your own insights, interlinked)
├── records/                  # Life data
│   ├── journal/             # Journals, morning court briefings, Censorate/Remonstrator reports
│   ├── meetings/
│   ├── contacts/
│   ├── finance/
│   └── health/
├── gtd/                      # GTD system
│   ├── waiting/             # Waiting on others
│   ├── someday/             # Someday/maybe
│   └── reviews/             # Review records
├── archive/                  # Completed projects move here
└── templates/
```

## Area List (areas/)

```
career/    product/    finance/    health/    family/
social/    learning/   ops/        creation/  spirit/
```

---

## GTD Flow

```
Something comes to mind → inbox/
  ├── Actionable, belongs to a project → projects/{p}/tasks/
  ├── Actionable, belongs to an area → areas/{a}/tasks/
  ├── Waiting on someone → gtd/waiting/
  ├── Later → gtd/someday/
  ├── Knowledge, not a task → zettelkasten/
  └── Useless → delete
```

## Zettelkasten Growth

```
Fleeting idea → zettelkasten/fleeting/
Read an article → zettelkasten/literature/
  → Distill an insight → zettelkasten/permanent/ (link to existing notes)
```

## Project → Knowledge Bridge

When a project is archived, working notes go with it; permanent notes stay in zettelkasten and keep growing.

---

## Notion Memory (3 Components)

### 📬 Inbox (Database)

Message queue between mobile and desktop. Fields: Content / Source (Mobile/Desktop) / Status (Pending/Synced) / Time.

### 🧠 Current Status (Page)

Global snapshot, overwritten by CC at the end of each session. Contains: things in progress, recent decisions, open questions, this week's focus.

### 📝 Working Memory (Topic Pages)

One page per active topic (about 5-10). Contains: background, current stage, key decisions, technical ideas, open questions, next steps. When no longer active, archived to GitHub and deleted from Notion.

---

## Multi-Repo Workflow

- **Project code** (EIP, life_OS, etc.) → each in its own repo
- **Thinking about projects** (decisions, notes, tasks) → second-brain repo

The same CC conversation connects both directories. `/save` command: write files → cd ~/second-brain → git commit/push → return to project.

---

## Three Departments and Six Ministries Output Destinations

| Output | GitHub Path |
|--------|------------|
| Decision memorials | `projects/{p}/decisions/` |
| Action items | `projects/{p}/tasks/` |
| Reviews / Censorate / Remonstrator | `records/journal/` |
| Research | `zettelkasten/literature/` |
| General insights | `zettelkasten/permanent/` |
| Goals | `areas/{a}/goals.md` |

---

## Without a Data Layer

If you don't set up the second-brain, all features work as normal — you just won't have persistence or cross-session memory.
