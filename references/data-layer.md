# Data Layer Architecture

All agents refer to this file when reading or writing data.

## Design Principles

1. **Full coverage**: The second brain covers life, family, shopping, hobbies, day job, side ventures — everything
2. **LLM-agnostic**: Not bound to any specific model. All "intelligence" is encoded in markdown files, not model weights
3. **Works without AI**: Open the markdown files in Obsidian and you can read, write, and navigate. LLM is an accelerator, not a prerequisite
4. **Markdown is the single source of truth**: All knowledge ultimately lands as .md files. Notion is the transport layer (inbox), not the storage layer
5. **Obsidian is the viewing layer**: Clone the GitHub repo locally, open in Obsidian. Wikilinks and standard markdown links enable automatic knowledge graph visualization

## Model Independence

**CLAUDE.md is the only file bound to a specific model.** Everything else — extraction rules, lint rules, role definitions, knowledge network, directory structure — is pure markdown readable by any model. Switching models means only updating CLAUDE.md references.

---

## Cognitive Pipeline

Information flows through five stages, each mapped to a methodology:

```
Perceive → Capture → Associate → Judge → Settle → Emerge
   ↑         ↑          ↑          ↑        ↑         ↑
 Phone      GTD      Zettelkasten  3D6M    PARA    Lint/Censorate
 Experience  inbox/    wiki/      Desktop   dirs    health check
```

### Stage Details

**Perceive → Capture (GTD)**: Zero-friction capture on mobile. User says something, phone AI saves to inbox. No classification at this stage — inbox is the GTD collection basket.

**Capture → Associate (Zettelkasten)**: Desktop CC pulls from inbox, first step is building associations — what existing wiki articles relate? What entities mentioned? What relationships between entities? Build backlink network with wikilinks.

**Associate → Judge (Three Departments)**: Not all information needs decisions. Only when major resource allocation, multi-option trade-offs, or hard-to-reverse consequences are involved, activate the Three Departments decision mode.

**Judge → Settle (PARA)**: Conclusions from decisions stored per PARA — Projects (things with endpoints), Areas (ongoing domains), Wiki (cross-domain knowledge), Archive (completed).

**Settle → Emerge (Lint/Censorate)**: When knowledge network density reaches critical mass, emergence happens automatically. Lint scans discover cross-domain associations, suggest new concept articles, find contradictions.

### Mobile vs Desktop Division

Mobile handles perception and capture only (occasionally lightweight association like web search). Desktop handles association, judgment, settlement, and emergence — all heavy lifting. Mobile can read pipeline outputs (STATUS.md, archives) but writes only at the capture stage.

---

## GitHub Directory Structure

```
second-brain/
│
├── inbox/                             # 📥 Unprocessed (mobile captures, materials, book notes, raw research)
│
├── _meta/                             # 🔧 System metadata
│   ├── STATUS.md                      # Global status dashboard (mirrored to Notion)
│   ├── MAP.md                         # Knowledge map (all area entry points)
│   ├── decisions/                     # Cross-domain major decisions
│   ├── journal/                       # Morning court briefings, Censorate/Remonstrator reports
│   ├── extraction-rules.md            # Knowledge extraction rules (trained by user)
│   ├── extraction-log.md              # Extraction history
│   ├── lint-rules.md                  # Inspection rules
│   ├── lint-state.md                  # Inspection state (last run time, etc.)
│   ├── lint-reports/                  # Historical inspection reports
│   └── roles/                         # Resident role definitions
│       ├── censor.md                  # Censorate (inspection mode)
│       ├── historian.md               # Historian (optional: auto-records daily work)
│       └── reviewer.md               # Chancellery on-duty (optional: reviews content quality on write)
│
├── projects/                          # 🎯 Things with endpoints (PARA-P)
│   └── {name}/
│       ├── index.md
│       ├── tasks/
│       ├── decisions/
│       ├── research/
│       └── journal/
│
├── areas/                             # 🌊 Ongoing life areas (PARA-A)
│   └── {name}/
│       ├── index.md
│       ├── goals.md
│       ├── tasks/
│       └── notes/
│
├── wiki/                              # 📚 Cross-domain knowledge network (Zettelkasten + wikilinks)
│
├── archive/                           # 🗄️ Completed project archives (PARA-Archive)
│
└── templates/
```

## Knowledge Classification (7 Types)

| Type | Storage | Example |
|------|---------|---------|
| Entity knowledge | wiki/ | A company discontinued a product line |
| Experience knowledge | wiki/ (marked subjective) | Material X feels better than Material Y |
| Relationship knowledge | wiki/ (backlinks) | Person A met through Event B |
| Decision records | areas/ or projects/ | Project switched from Tool A to Tool B |
| Todos / intentions | tasks/ | Try Product X next time |
| Inspiration / intuition | inbox/ (temporary) | There's an opportunity between X and Y |
| Process knowledge | wiki/ | Steps to register a company in Japan |

These 7 types may expand over time based on actual usage.

---

## Knowledge Extraction: Four-Step Training

1. **User decides**: Desktop CC generates an "extraction proposal", user confirms/modifies
2. **Accumulate samples**: Record to `_meta/extraction-log.md`
3. **LLM induces rules**: From the log, induce preferences and write to `_meta/extraction-rules.md` (pure markdown, model-agnostic)
4. **Periodic correction**: User reviews monthly, reports misclassifications, CC updates rules

Core: The "learning" carrier is markdown files, not model weights. Switching models only requires reading these files.

---

## Censorate: Two Operating Modes

The Censorate (御史台) runs in two modes within the Three Departments system:

### Mode 1: Decision Review (existing)

After every Three Departments workflow, reviews official work quality. Already defined in `pro/agents/yushitai.md`.

### Mode 2: Patrol Inspection (new)

When idle, each ministry inspects its own jurisdiction. Defined in `_meta/roles/censor.md`.

#### Trigger Levels

| Trigger | When | Depth |
|---------|------|-------|
| **Startup inspection** | Every desktop CC session start, if `lint-state.md` shows >4h since last run | Lightweight, 3-line briefing |
| **Post-sync inspection** | After inbox sync completes | Check new content vs wiki consistency, new entities needing wiki articles, STATUS.md update |
| **Deep inspection** | Weekly or manual trigger | Full six-ministry patrol |

#### Six Ministry Patrol Responsibilities

| Ministry | Jurisdiction | Checks |
|----------|-------------|--------|
| Revenue | areas/finance/ | Investment strategy outdated, financial figures need updating |
| War | projects/ | Project activity, TODO completion, resource conflicts |
| Rites | wiki/ (relationships) | Unfulfilled social commitments, new contacts to record |
| Works | wiki/ + _meta/ | Orphan files, broken links, rule validity |
| Personnel | areas/career/ | Career direction aligned with actions |
| Justice | Cross-domain | Strategy contradictions between projects, decisions missing risk assessment |

#### Issue Classification

| Level | Action | Example |
|-------|--------|---------|
| **Auto-fix** | Censorate handles directly | Missing index entries, missing backlinks, format issues |
| **Suggest** | Send to inbox for user | Data inconsistency, project possibly stalled, wiki suggestion |
| **Escalate** | Activate Three Departments decision mode | Financial contradictions >¥1M, multi-project strategy conflict, interpersonal risk |

#### Implementation

- Role definition stored in `_meta/roles/censor.md`, CLAUDE.md only references it
- Inspection state persisted in `_meta/lint-state.md` (solves LLM's lack of cross-session memory)
- Inspection reports stored in `_meta/lint-reports/`, summary also sent to inbox
- Switching models: role files stay unchanged, only CLAUDE.md references change

---

## Expandable Resident Roles

| Role | File | Function |
|------|------|----------|
| Censorate | `_meta/roles/censor.md` | Patrol inspection (required) |
| Historian | `_meta/roles/historian.md` | Auto-records daily work at session end (optional) |
| Chancellery on-duty | `_meta/roles/reviewer.md` | Reviews content quality on write (optional) |

---

## Three Departments Output Destinations

| Output | GitHub Path |
|--------|------------|
| Decision memorials (project-specific) | `projects/{p}/decisions/` |
| Decision memorials (cross-domain) | `_meta/decisions/` |
| Action items (project) | `projects/{p}/tasks/` |
| Action items (area) | `areas/{a}/tasks/` |
| Morning court briefings | `_meta/journal/` |
| Censorate / Remonstrator reports | `_meta/journal/` |
| Inspection reports | `_meta/lint-reports/` |
| Project research | `projects/{p}/research/` |
| Cross-domain knowledge | `wiki/` |
| Goals | `areas/{a}/goals.md` |
| Global status snapshot | `_meta/STATUS.md` |

---

## Notion (Transport Layer, 3 Components)

Notion is the transport layer only, not the storage layer.

### 📬 Inbox (Database)

Message queue for passing information between mobile and desktop.

| Field | Type | Description |
|-------|------|-------------|
| Content | Title | A sentence or key points |
| Source | Select | Mobile / Desktop |
| Status | Select | Pending / Synced |
| Time | Created time | Automatic |

### 🧠 Status Dashboard (Page)

Mirror of `_meta/STATUS.md`. Overwritten by CC at the end of each session.

### 🗄️ Archive

Read-only archive access from mobile.

---

## Morning Court Official Data Operations

### Housekeeping Mode (Start of Conversation)

```
1. Read ~/second-brain/inbox/ (unprocessed items)
2. Read ~/second-brain/_meta/STATUS.md (global status)
3. Read ~/second-brain/_meta/lint-state.md (check if inspection needed: >4h since last run)
4. Read ~/second-brain/projects/{bound}/index.md (bound project status)
5. Read ~/second-brain/projects/{bound}/decisions/ (historical decisions)
6. Read ~/second-brain/projects/{bound}/tasks/ (active tasks)
7. Read user-patterns.md
8. Global overview: list all projects/ and areas/ index.md titles + status
9. Check Notion 📬 Inbox (new messages from mobile) → pull into second-brain/inbox/
10. If lint-state.md shows >4h since last run → trigger lightweight Censorate inspection
11. Platform awareness + version check
```

### Wrap-Up Mode (End of Process)

```
1. Memorials → projects/{p}/decisions/ or _meta/decisions/ (cross-domain)
2. Action items → projects/{p}/tasks/ or areas/{a}/tasks/
3. Censorate reports → _meta/journal/
4. Remonstrator reports → _meta/journal/
5. Update _meta/STATUS.md (global status snapshot)
6. Update _meta/lint-state.md (last inspection time)
7. Update user-patterns.md
8. git add + commit + push (to second-brain repo)
9. Sync Notion: update 🧠 Status Dashboard
```

### Review Mode

```
1. Read _meta/STATUS.md for global state
2. Traverse projects/*/tasks/ to compute completion rates
3. Read areas/*/goals.md for goal progress
4. Read _meta/journal/ recent journals
5. Read _meta/lint-reports/ recent inspection reports
6. Metrics dashboard computed from files
```

## Remonstrator Data Retrieval

```
1. Read user-patterns.md
2. Read _meta/journal/ last 3 Remonstrator reports
3. Read projects/*/decisions/ + _meta/decisions/ last 5 decisions
4. Traverse projects/*/tasks/ to compute completion rates
```

## Degradation Rules

- second-brain repo unreachable → annotate "⚠️ second-brain unavailable"
- Notion unavailable → only affects mobile sync, does not affect core functionality
- Both unavailable → operates normally, output displayed in conversation but not persisted
