# Second Brain — Architecture and Setup (v1.9)

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

## Vault Directory Structure (v1.9)

```
<vault root>/
│
├── inbox/                          # 📥 User drop-zone (raw materials, captures, research)
├── SOUL.md                         # 🧬 Identity — values, principles, behavioral patterns (stays at root)
│
├── meta/                           # 🔧 System metadata — TRANSPARENT, no hidden subdirs (v1.9)
│   │
│   │  ★ Category 1: Configuration (you write)
│   ├── config.md                   # Backend config + migrated_to
│   ├── strategic-lines.md          # Strategic line definitions
│   ├── extraction-rules.md         # Extraction rules
│   ├── lint-rules.md               # Lint rules
│   │
│   │  ★ Category 2: Compiled artifacts (system shows you)
│   ├── STATUS.md                   # Global status snapshot
│   ├── STRATEGIC-MAP.md            # Strategic map (compiled from project strategic fields)
│   ├── MAP.md                      # Knowledge map
│   ├── sessions/INDEX.md           # Session index (hippocampus source)
│   ├── user-patterns.md            # ★ v1.9: moved from vault-root to meta/
│   │
│   │  ★ Category 3: Curated content (you + system collaborate)
│   ├── decisions/<YYYY-MM>/<id>.md # ★ v1.9: monthly subdirs, single canonical path
│   ├── journal/<YYYY-MM-DD>.md     # ★ v1.9: time-axis canonical
│   ├── methods/<name>.md           # Method library (含 born_from_decisions field)
│   ├── queue/                      # ★ v1.9: renamed from inbox/
│   │   ├── to-process/.gitkeep
│   │   ├── notifications.md
│   │   └── README.md
│   │
│   │  ★ Category 4: Audit logs (system's accountability records)
│   ├── compliance/violations.md    # Censorate violation records
│   ├── eval-history/<YYYY-MM>/     # Audit statistics
│   ├── snapshots/soul/<YYYY-MM-DD-HHMM>.md  # SOUL historical snapshots
│   ├── lint-state.md
│   ├── lint-reports/
│   ├── extraction-log.md
│   │
│   │  ★ Category 5: Runtime state (system's temporary workbench)
│   ├── runtime/<sid>/              # Audit trail (R11/R12/R13)
│   ├── outbox/                     # Offline session staging
│   └── .merge-lock                 # Single-file lock (dot-prefix is sort hint, not hide)
│
├── projects/{name}/                # 🎯 Things with endpoints (含 archived projects)
│   ├── index.md                    # ★ v1.9: frontmatter has lifecycle_stage + ## Journal/Decisions
│   ├── tasks/                      # Next actions
│   └── research/                   # Project-specific research
│       # decisions/ has moved to meta/decisions/
│       # journal/ has moved to meta/journal/
│
├── areas/                          # 🌊 Ongoing life areas (no enforcement of names)
│   ├── README.md                   # ★ v1.9: explains "Recommended seed, not enforced"
│   └── {name}/                     # User's actual areas
│
├── wiki/                           # 📚 Knowledge archive (unchanged in v1.9)
│   ├── INDEX.md
│   ├── log.md
│   ├── OBSIDIAN-SETUP.md
│   ├── .templates/
│   └── {domain}/{topic}.md
│
└── templates/                      # 📋 Top-level templates (unchanged in v1.9)
```

**v1.9 changes summary**:
- `_meta/` → `meta/` (drop underscore prefix; transparency)
- `meta/inbox/` → `meta/queue/` (avoid confusion with vault-root inbox/)
- decisions consolidated to `meta/decisions/<YYYY-MM>/<id>.md`
- archive replaced by frontmatter `lifecycle_stage: archived` (projects stay in `projects/`)
- journal time-axis canonical at `meta/journal/<YYYY-MM-DD>.md`
- `user-patterns.md` moved into `meta/`
- areas no longer pre-creates 10 empty directories

---

## Understanding `meta/` — 5-Class Mental Model (v1.9)

Per v1.9 RFC §3.1, `meta/` content falls into 5 distinct categories. All are visible (no `.system/` hidden layer); the categories are documentation-only conceptual groupings, not directory boundaries.

| Category | Examples | Who writes | Who reads | Retention |
|----------|---------|------------|-----------|-----------|
| **Configuration**（你写的） | `config.md`, `strategic-lines.md`, `extraction-rules.md`, `lint-rules.md` | Human | All agents | Permanent |
| **Compiled artifacts**（系统给你看的） | `STATUS.md`, `STRATEGIC-MAP.md`, `MAP.md`, `sessions/INDEX.md`, `user-patterns.md` | retrospective / archiver / advisor | Human + ROUTER | Regeneratable, safe to delete |
| **Curated content**（你和系统一起写的） | `decisions/`, `journal/`, `methods/`, `queue/notifications.md` | Human + machine collab | Human + all agents | Permanent |
| **Audit logs**（系统的问责档案） | `compliance/violations.md`, `eval-history/`, `snapshots/soul/`, `lint-reports/`, `extraction-log.md` | Agent (machine) | auditor / advisor / human occasionally | Long-term |
| **Runtime state**（系统的临时工作台） | `runtime/<sid>/`, `outbox/`, `.merge-lock` | Agent (machine) | auditor Mode 3 | Short-term (30-90 days) |

**Transparency principle**: lifeos is single-user; the system has no secrets from the user. Even audit trail and runtime data are visible — you can `cd meta/runtime/<sid>/` and read every step the agents took. This is intentional (DR-1.9.1).

---

## Areas — Recommended Seed, Not Enforced (v1.9)

In v1.9, `areas/` no longer pre-creates 10 categories at FIRST-RUN. Instead, you get an empty `areas/` directory with a `README.md` listing recommended seeds:

```
career     · 工作 / 事业方向
product    · 你在做的产品/项目
finance    · 收支、投资、税务、保险
health     · 身体、睡眠、营养、运动
family     · 家人、伴侣、孩子
social     · 朋友、合作者、社群
learning   · 学习计划、技能升级、个人品牌
ops        · 数字基建、生活流程、居住环境
creation   · 创作、内容、表达
spirit     · 价值观、人生方向、精神世界
```

**The system does not enforce these names.** You can:
- Delete what doesn't apply
- Add new ones (`art/`, `travel/`, `spiritual-practice/`, anything)
- Rename freely
- Start with zero and build up as needed

lifeos's processing of `areas/<name>/` only cares about directory existence, not naming conventions.

---

## Key Concepts

### projects/ — Things with Endpoints

Each project has its own self-contained world: tasks, research, an `index.md` with `## Journal` and `## Decisions` sections (auto-maintained by archiver as Dataview blocks + Recent 5 wikilinks fallback).

**v1.9 change**: When a project completes, it is **NOT** moved to `archive/`. Instead, the project's `index.md` frontmatter gets `lifecycle_stage: archived`. The project stays in `projects/` — preserving all wikilink references. Indexers (retrospective Mode 0 compiling STATUS, archiver Phase 1) filter by `lifecycle_stage` to hide archived from default views; Obsidian graph view uses a "archived" colorGroup to gray them out.

### areas/ — Ongoing Life Areas

No endpoint, no deadline. Each area has goals, tasks, and notes. A project can reference an area; an area can spawn projects.

### wiki/ — Knowledge Archive

Replaces the previous zettelkasten structure. A domain-organized wiki of interlinked notes with an INDEX.md entry point. Not bound to any project — projects die, knowledge lives. Grows from DREAM: the Court Diarist extracts reusable conclusions from session analysis into wiki pages. **v1.9: wiki internals unchanged.**

### SOUL.md — Identity Profile

Captures the user's core values, principles, decision-making tendencies, and behavioral patterns. Referenced by the Remonstrator and Hanlin Academy to provide personalized counsel. **v1.9: stays at vault root** (high-frequency reference + wikilink simplicity `[[SOUL]]` + ~50 spec references).

### DREAM — Knowledge Extraction

The Court Diarist's session-close process: reviews the session, extracts reusable insights, and writes them to wiki/ as permanent knowledge entries. This is how ephemeral analysis becomes lasting knowledge.

### Cross-References Between Decisions / Methods / Journal (v1.9 Opt #8)

Three artifact types in `meta/` now have frontmatter fields that link them:

```
methods            decisions          journal
   │                  │                  │
   ├── born_from_decisions → ←──┘                  │
   │                  │                  │
   │ ←── applied_methods                │
   │                  │                  │
   │                  │ ←── referenced_decisions
   │                  │                  │
   │ ←─────────────── referenced_methods
```

Reverse queries (e.g., "which decisions applied this method?") use Dataview + Recent 5 wikilinks pattern — no maintained inverse field. See `_meta/rfc/v1.9-second-brain-structure-optimization.md` §3.8 for full schema.

---

## Three Departments and Six Ministries Output Destinations (v1.9)

| Output | GitHub Path |
|--------|------------|
| Decision memorials (all) | `meta/decisions/<YYYY-MM>/<id>.md` (含 type / projects / domains / applied_methods / journal_date frontmatter) |
| Action items | `projects/{project}/tasks/` or `areas/{area}/tasks/` |
| Morning court briefings | `meta/journal/<date>.md` (含 type_tags: [briefing]) |
| Censorate/Remonstrator reports | `meta/journal/<date>.md` (含 type_tags: [auditor] / [advisor]) |
| Research | `projects/{project}/research/` |
| Cross-domain knowledge | `wiki/{domain}/{topic}.md` |
| Goals | `areas/{area}/goals.md` |
| Session journal (session-close) | `meta/journal/<date>.md` (含 type_tags: [dream] for DREAM reports) |
| Wiki extraction (session-close) | `wiki/{domain}/{topic}.md` (via Court Diarist) |
| Global status | `meta/STATUS.md` |
| User behavior patterns | `meta/user-patterns.md` (v1.9: moved from vault-root) |

---

## Notion Memory (4 Components)

### 📬 Inbox (Database)

Message queue between mobile and desktop. Fields: Content / Source (Mobile/Desktop) / Status (Pending/Synced) / Time.

### 🧠 Current Status (Page)

Mirrors `meta/STATUS.md`. Overwritten by Court Diarist at session close (as part of archive + sync).

### 📝 Working Memory (Topic Pages)

One page per active topic (about 5-10). When no longer active, archived to GitHub and deleted from Notion.

### 📋 Todo Board (Database)

Active tasks synced from projects/*/tasks/ and areas/*/tasks/. Viewable and checkable on mobile.

---

## Multi-Repo Workflow

- **Project code** (e.g., life_OS) → each in its own repo
- **Thinking about projects** (decisions, notes, tasks) → second-brain repo

The same CC conversation connects both directories. `/save` command: write files → cd ~/second-brain → git commit/push → return to project.

---

## Migrating from v1.8.x to v1.9

Run `/migrate-v1.9` once. The tool will:

1. Pre-flight checks (git working dir clean, version ≥ v1.8.0, no archive non-project content)
2. Show per-stage dry-run summary
3. After user confirms `go`, execute 8 stages
4. Append migration report to today's journal
5. Final `git commit`

After migration, run `/verify-v1.9` to confirm all 8 acceptance criteria PASS.

See `_meta/rfc/v1.9-second-brain-structure-optimization.md` for full RFC.

---

## Without a Data Layer

If you don't set up the second-brain, all features work as normal — you just won't have persistence or cross-session memory.
