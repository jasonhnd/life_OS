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

```
second-brain/
│
├── inbox/                    # 📥 Unprocessed (captures, materials, notes, raw research)
│
├── SOUL.md                   # 🧬 Identity — values, principles, behavioral patterns
├── user-patterns.md          # 📊 Behavioral patterns observed across sessions
│
├── _meta/                    # 🔧 System metadata
│   ├── STATUS.md             # Global status snapshot
│   ├── MAP.md                # Knowledge map
│   ├── outbox/               # 📤 Pending outputs for external sync
│   ├── decisions/            # Cross-domain major decisions
│   ├── journal/              # Morning court briefings, Censorate/Remonstrator reports
│   ├── extraction-rules.md
│   ├── extraction-log.md
│   ├── lint-rules.md
│   ├── lint-state.md
│   ├── lint-reports/
│   └── roles/                # System role definitions
│
├── projects/{name}/          # 🎯 Things with endpoints
│   ├── index.md              # Goals, status, related areas
│   ├── tasks/                # Next actions
│   ├── decisions/            # Project-specific memorials
│   ├── research/             # Project-specific research
│   └── journal/              # Project-specific logs
│
├── areas/{name}/             # 🌊 Ongoing life areas
│   ├── index.md              # Direction, related projects
│   ├── goals.md              # Goals
│   ├── tasks/                # Area tasks
│   └── notes/                # Area notes
│
├── wiki/                     # 📚 Knowledge archive — reusable conclusions (grows from DREAM)
│   ├── INDEX.md              # Wiki entry index
│   └── {domain}/{topic}.md   # Domain-organized knowledge pages
│
├── archive/                  # 🗄️ Completed project archives
│
└── templates/                # 📋 Templates
```

## Area List (areas/)

```
career/    product/    finance/    health/    family/
social/    learning/   ops/        creation/  spirit/
```

---

## Key Concepts

### _meta/ — System Metadata

The brain about the brain. Contains:
- **STATUS.md**: Global snapshot of what's happening across all projects and areas. Updated by Morning Court Official at session end.
- **MAP.md**: Knowledge map linking concepts across wiki/.
- **decisions/**: Cross-domain decisions that don't belong to any single project.
- **journal/**: System-level logs — morning court briefings, Censorate and Remonstrator reports.
- **roles/**: System role definitions for quality control (censor, historian, reviewer).
- **lint-***: Quality check rules and reports for the second-brain itself.
- **extraction-***: Rules and logs for extracting insights from raw materials.

### projects/ — Things with Endpoints

Each project has its own self-contained world: tasks, decisions, research, and journal. When a project completes, the entire folder moves to archive/. Knowledge extracted into wiki/ stays and keeps growing.

### areas/ — Ongoing Life Areas

No endpoint, no deadline. Each area has goals, tasks, and notes. A project can reference an area; an area can spawn projects.

### wiki/ — Knowledge Archive

Replaces the previous zettelkasten structure. A domain-organized wiki of interlinked notes with an INDEX.md entry point. Not bound to any project — projects die, knowledge lives. Grows from DREAM: the Court Diarist extracts reusable conclusions from session analysis into wiki pages.

### SOUL.md — Identity Profile

Captures the user's core values, principles, decision-making tendencies, and behavioral patterns. Referenced by the Remonstrator and Hanlin Academy to provide personalized counsel.

### DREAM — Knowledge Extraction

The Court Diarist's session-close process: reviews the session, extracts reusable insights, and writes them to wiki/ as permanent knowledge entries. This is how ephemeral analysis becomes lasting knowledge.

---

## Three Departments and Six Ministries Output Destinations

| Output | GitHub Path |
|--------|------------|
| Decision memorials (project) | `projects/{p}/decisions/` |
| Decision memorials (cross-domain) | `_meta/decisions/` |
| Action items | `projects/{p}/tasks/` or `areas/{a}/tasks/` |
| Morning court briefings | `_meta/journal/` |
| Censorate/Remonstrator reports | `_meta/journal/` |
| Research | `projects/{p}/research/` |
| Cross-domain knowledge | `wiki/` |
| Goals | `areas/{a}/goals.md` |
| Session journal (session-close) | `_meta/journal/` (via Court Diarist) |
| Wiki extraction (session-close) | `wiki/{domain}/{topic}.md` (via Court Diarist) |
| Global status | `_meta/STATUS.md` |

---

## Notion Memory (4 Components)

### 📬 Inbox (Database)

Message queue between mobile and desktop. Fields: Content / Source (Mobile/Desktop) / Status (Pending/Synced) / Time.

### 🧠 Current Status (Page)

Mirrors `_meta/STATUS.md`. Overwritten by CC at session end.

### 📝 Working Memory (Topic Pages)

One page per active topic (about 5-10). When no longer active, archived to GitHub and deleted from Notion.

### 📋 Todo Board (Database)

Active tasks synced from projects/*/tasks/ and areas/*/tasks/. Viewable and checkable on mobile.

---

## Multi-Repo Workflow

- **Project code** (EIP, life_OS, etc.) → each in its own repo
- **Thinking about projects** (decisions, notes, tasks) → second-brain repo

The same CC conversation connects both directories. `/save` command: write files → cd ~/second-brain → git commit/push → return to project.

---

## Without a Data Layer

If you don't set up the second-brain, all features work as normal — you just won't have persistence or cross-session memory.
