---
status: legacy
authoritative: false
superseded_by: hosts/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in hosts/CLAUDE.md."
---

# Data Layer Architecture

All agents refer to this file when reading or writing data.

## Design Principles

1. **Full coverage**: The second brain covers life, family, shopping, hobbies, day job, side ventures — everything
2. **LLM-agnostic**: Not bound to any specific model. All "intelligence" is encoded in markdown files, not model weights
3. **Works without AI**: Open the markdown files in Obsidian and you can read, write, and navigate. LLM is an accelerator, not a prerequisite
4. **Markdown is the single source of truth**: All knowledge ultimately lands as .md files in the git repo — the local working copy is the storage layer, GitHub is the remote backup
5. **Obsidian is the viewing layer**: Clone the GitHub repo locally, open in Obsidian. Wikilinks and standard markdown links enable automatic knowledge graph visualization

## Model Independence

**CLAUDE.md is the only file bound to a specific model.** Everything else — extraction rules, lint rules, role definitions, knowledge network, directory structure — is pure markdown readable by any model. Switching models means only updating CLAUDE.md references.

---

## Cognitive Pipeline

Information flows through seven stages, each mapped to a methodology. The **Activate** stage is new in v1.7 (Cortex Pre-Router Cognitive Layer) — it turns stored associations into active context before the Judge stage runs.

```
Perceive → Capture → Activate → Judge → Settle → Associate → Strategize → Emerge
   ↑         ↑          ↑         ↑       ↓   ↘        ↑           ↑           ↑
 Phone      GTD      Cortex     3D6M    SOUL  Wiki   Prime+Wiki  Strategic   DREAM REM
 Experience  inbox/  Pre-Router Desktop (person)(knowledge) INDEX match    MAP       cross-domain
                     (v1.7)
```

### Stage Details

**Perceive → Capture (GTD)**: Zero-friction capture on mobile. User says something, phone AI saves to inbox. No classification at this stage — inbox is the GTD collection basket.

**Capture → Activate (Cortex Pre-Router, v1.7)**: Before ROUTER triages the user message, three parallel subagents run — hippocampus (cross-session retrieval from `meta/sessions/INDEX.md`), concept lookup (spreading activation across `meta/concepts/`), SOUL dimension check (reuses RETROSPECTIVE's SOUL Health Report). The GWT arbitrator consolidates their signals into an annotated input. ROUTER receives the annotated input, not the raw message. Failure modes degrade to v1.6.2a behaviour (raw message to ROUTER). See `references/cortex-spec.md` §Workflow Integration.

**Activate → Judge (Draft-Review-Execute cycle)**: Desktop CC pulls from inbox. Not all information needs decisions. Only when major resource allocation, multi-option trade-offs, or hard-to-reverse consequences are involved, activate the Draft-Review-Execute decision mode. The judge stage operates on cognitively-annotated input — PLANNER / REVIEWER / six domains start from context, not cold.

**Judge → Settle (SOUL + Wiki + Concepts + Methods + Snapshots)**: Conclusions from decisions settle into five pools — SOUL (who you are), Wiki (what you know about the world), Concepts (the synaptic graph that connects knowledge), Methods (procedural memory — reusable workflows), and Snapshots (historical SOUL state for trend computation). All are auto-written under strict criteria: ARCHIVER Phase 2 produces wiki / SOUL / concept / method / snapshot candidates; users nudge post-hoc (delete file to retire, say "undo recent" to roll back). See `references/concept-spec.md`, `references/method-library-spec.md`, `references/snapshot-spec.md`.

**Settle → Associate (ROUTER + Wiki INDEX + Concept INDEX + Methods INDEX)**: The ROUTER reads compiled INDEX files at session start (wiki/INDEX.md, meta/concepts/INDEX.md, meta/methods/INDEX.md, meta/sessions/INDEX.md). When a new request arrives, existing knowledge is automatically matched — "we already know X about this domain, and we have a canonical method for Y." This turns accumulated knowledge into active context.

**Associate → Strategize (Strategic Map)**: The ROUTER reads `meta/STRATEGIC-MAP.md` at session start. When a request involves a project with strategic relationships, the system automatically surfaces downstream dependencies, bottleneck status, and decision propagation warnings. This turns per-project analysis into strategic-line-aware analysis. See `references/strategic-map-spec.md`.

**Strategize → Emerge (DREAM REM)**: When wiki entries and strategic relationships accumulate, DREAM's REM stage discovers cross-domain connections using the flow graph as scaffolding — checking SOUL × strategy alignment, wiki × flow completeness, and behavioral pattern × strategic priority consistency. The more knowledge and relationships settle, the more emergence happens. AUDITOR patrol also detects wiki contradictions, knowledge gaps, and strategy contradictions between projects.

### Mobile vs Desktop Division

Mobile handles perception and capture only (occasionally lightweight association like web search). Desktop handles association, judgment, settlement, and emergence — all heavy lifting. Mobile can read pipeline outputs (STATUS.md, archives) but writes only at the capture stage.

---

## GitHub Directory Structure

```
second-brain/
│
├── SOUL.md                            # 🔮 User personality archive (values, beliefs, identity — grows from zero; stays at root)
│
├── inbox/                             # 📥 Unprocessed (mobile captures, materials, book notes, raw research)
│
├── meta/                             # 🔧 System metadata (v1.9: no underscore, fully transparent)
│   ├── user-patterns.md               # 📊 Behavioral patterns (what you DO — ADVISOR-maintained; v1.9 moved from root)
│   ├── STATUS.md                      # Global status dashboard (compiled from index.md files)
│   ├── STRATEGIC-MAP.md               # Strategic map (compiled from project strategic fields)
│   ├── strategic-lines.md             # Strategic line definitions (user-defined)
│   ├── MAP.md                         # Knowledge map (all area entry points)
│   ├── decisions/{YYYY-MM}/           # 🗳️ All decisions (v1.9 consolidated: month subdir, dec-{YYYY-MM-DD}-{NNN}.md)
│   ├── journal/{YYYY-MM-DD}.md        # RETROSPECTIVE briefings, AUDITOR/ADVISOR reports, DREAM (v1.9 time-axis canonical)
│   ├── queue/                         # 📬 System processing queue + notifications (v1.9 renamed from inbox)
│   ├── outbox/                        # 📮 Session output staging area (one subdirectory per session)
│   │   └── {session_id}/              # Each session writes here on adjourn, merged at next start court
│   ├── snapshots/                     # 📸 State snapshots for trend computation
│   │   └── soul/                      # SOUL snapshots per session (YYYY-MM-DD-HHMM.md)
│   │       └── _archive/              # Snapshots older than 30 days
│   ├── sessions/                      # 🧠 Session summaries (v1.7 Cortex)
│   │   ├── INDEX.md                   # Compiled one-liner index (retrospective Mode 0)
│   │   └── {session_id}.md            # Per-session structured summary (archiver Phase 2)
│   ├── concepts/                      # 🧬 Concept graph + synapses (v1.7 Cortex)
│   │   ├── INDEX.md                   # Compiled concept one-liners (retrospective Mode 0)
│   │   ├── SYNAPSES-INDEX.md          # Compiled reverse edge index (archiver Phase 2)
│   │   ├── _tentative/                # Concepts awaiting promotion
│   │   ├── _archive/                  # Retired concepts
│   │   └── {domain}/{concept_id}.md   # One concept per file
│   ├── methods/                       # 📐 Method library — procedural memory (v1.7)
│   │   ├── INDEX.md                   # Compiled method one-liners (retrospective Mode 0)
│   │   ├── _tentative/                # Methods awaiting user confirmation
│   │   ├── _archive/                  # Dormant methods (≥12 months unused)
│   │   └── {domain}/{method_id}.md    # One method per file
│   ├── eval-history/                  # 📊 AUDITOR evaluation history (v1.7)
│   │   ├── {YYYY-MM-DD}-{project}.md  # One per session through AUDITOR
│   │   ├── _digest/{YYYY-Q}.md        # Quarterly digest (tools/stats.py --compress-old)
│   │   └── _archive/                  # Originals moved here after digest
│   ├── cortex/                        # 🧠 Cortex runtime state (v1.7)
│   │   ├── config.md                  # Cortex thresholds and switches
│   │   ├── bootstrap-status.md        # Migration log (tools/migrate.py output)
│   │   └── decay-log.md               # Concept decay actions
│   ├── audit/                         # 🕵️ Meta-cognitive audit (v1.7)
│   │   └── suspicious.md              # Drift candidates awaiting user confirmation
│   ├── ambiguous_corrections/         # Mid-confidence user corrections awaiting confirmation (v1.7)
│   ├── compliance/                    # ⚖️ Runtime violations (shell hooks, v1.7)
│   │   ├── violations.md              # Rolling 90-day window
│   │   └── archive/                   # Quarterly archive of older rows
│   ├── extraction-rules.md            # Knowledge extraction rules (trained by user)
│   ├── extraction-log.md              # Extraction history
│   ├── lint-rules.md                  # Inspection rules
│   ├── lint-state.md                  # Inspection state (last run time, etc.)
│   ├── lint-reports/                  # Historical inspection reports
│   └── roles/                         # Resident role definitions
│       ├── censor.md                  # AUDITOR (inspection mode)
│       ├── historian.md               # Historian (optional: auto-records daily work)
│       └── reviewer.md               # REVIEWER on-duty (optional: reviews content quality on write)
│
├── projects/                          # 🎯 Things with endpoints (PARA-P; archived projects stay here via lifecycle_stage frontmatter)
│   └── {name}/
│       ├── index.md                   # frontmatter: lifecycle_stage + (## Journal / ## Decisions sections via Dataview + Recent 5)
│       ├── tasks/
│       └── research/
│       #  v1.9: decisions/ → meta/decisions/{YYYY-MM}/  ·  journal/ → meta/journal/{YYYY-MM-DD}.md
│
├── areas/                             # 🌊 Ongoing life areas (PARA-A)
│   ├── README.md                      # v1.9: recommended seeds (not enforced)
│   └── {name}/
│       ├── index.md
│       ├── goals.md
│       ├── tasks/
│       └── notes/
│
├── wiki/                              # 📚 Cross-domain knowledge network (Zettelkasten + wikilinks)
│
└── templates/
```

> **v1.9 layout note**: No top-level `archive/` directory (PARA-Archive replaced by `lifecycle_stage: archived` frontmatter per DR-1.9.4 — projects stay in `projects/` to preserve wikilinks). `decisions/` and `journal/` moved out of `projects/{name}/` into `meta/`. `user-patterns.md` moved from root into `meta/`. See `docs/second-brain.md` for full v1.9 tree.

## Knowledge Classification (7 Types)

| Type | Storage | Example |
|------|---------|---------|
| Entity knowledge | wiki/ | A company discontinued a product line |
| Experience knowledge | wiki/ (marked subjective) | Material X feels better than Material Y |
| Relationship knowledge | wiki/ (backlinks) | Person A met through Event B |
| Decision records | areas/ or projects/ | Project switched from Tool A to Tool B |
| Todos / intentions | tasks/ | Try Product X next time |
| Inspiration / intuition | inbox/ (temporary) | There's an opportunity between X and Y |
| Factual / declarative knowledge | wiki/ | "NPO lending in Japan has no 貸金業法 exemption" |
| Procedural knowledge (reusable workflows, v1.7) | `meta/methods/` | "Refine documents in 5 escalating quality rounds" |
| Concept graph (synapses, v1.7) | `meta/concepts/` | "company-a-holding" node with weighted edges to related concepts |

These types may expand over time based on actual usage. v1.7 splits "Process knowledge" into two: factual process descriptions stay in `wiki/`, reusable procedural workflows move to `meta/methods/` (see `references/method-library-spec.md`).

---

## Knowledge Extraction: Four-Step Training

1. **User decides**: Desktop CC generates an "extraction proposal", user confirms/modifies
2. **Accumulate samples**: Record to `meta/extraction-log.md`
3. **LLM induces rules**: From the log, induce preferences and write to `meta/extraction-rules.md` (pure markdown, model-agnostic)
4. **Periodic correction**: User reviews monthly, reports misclassifications, CC updates rules

Core: The "learning" carrier is markdown files, not model weights. Switching models only requires reading these files.

---

## AUDITOR: Two Operating Modes

The AUDITOR runs in two modes within the Draft-Review-Execute system:

### Mode 1: Decision Review (existing)

After every Draft-Review-Execute workflow, reviews official work quality. Already defined in `agents/auditor.md`.

### Mode 2: Patrol Inspection (new)

When idle, each domain inspects its own jurisdiction. Defined in `meta/roles/censor.md`.

#### Trigger Levels

| Trigger | When | Depth |
|---------|------|-------|
| **Startup inspection** | Every desktop CC session start, if `lint-state.md` shows >4h since last run | Lightweight, 3-line briefing |
| **Post-sync inspection** | After inbox sync completes | Check new content vs wiki consistency, new entities needing wiki articles, STATUS.md update |
| **Deep inspection** | Weekly or manual trigger | Full Six Domains patrol |

#### Six Domains Patrol Responsibilities

| Domain | Jurisdiction | Checks |
|--------|-------------|--------|
| FINANCE | areas/finance/ | Investment strategy outdated, financial figures need updating |
| EXECUTION | projects/ | Project activity, TODO completion, resource conflicts |
| GROWTH | wiki/ | Unfulfilled social commitments, new contacts to record, wiki entries with confidence < 0.3 and no update in 90+ days (suggest retire), wiki entries with challenges > evidence_count (suggest review), domains with decisions but no wiki entries (knowledge gap) |
| INFRA | wiki/ + meta/ | Orphan files, broken links, rule validity |
| PEOPLE | areas/career/ | Career direction aligned with actions |
| GOVERNANCE | Cross-domain | Strategy contradictions between projects, decisions missing risk assessment |

#### Issue Classification

| Level | Action | Example |
|-------|--------|---------|
| **Auto-fix** | AUDITOR handles directly | Missing index entries, missing backlinks, format issues |
| **Suggest** | Send to inbox for user | Data inconsistency, project possibly stalled, wiki suggestion |
| **Escalate** | Activate Draft-Review-Execute decision mode | Financial contradictions >¥1M, multi-project strategy conflict, interpersonal risk |

#### Implementation

- Role definition stored in `meta/roles/censor.md`, CLAUDE.md only references it
- Inspection state persisted in `meta/lint-state.md` (solves LLM's lack of cross-session memory)
- Inspection reports stored in `meta/lint-reports/`, summary also sent to inbox
- Switching models: role files stay unchanged, only CLAUDE.md references change

---

## Expandable Resident Roles

| Role | File | Function |
|------|------|----------|
| AUDITOR | `meta/roles/censor.md` | Patrol inspection (required) |
| Historian | `meta/roles/historian.md` | Auto-records daily work at session end (optional) |
| REVIEWER on-duty | `meta/roles/reviewer.md` | Reviews content quality on write (optional) |

---

## Draft-Review-Execute Output Destinations

All outputs use standard operations from `references/data-model.md`. The git adapter (`references/adapter-github.md`) translates these into git operations on the working copy.

| Output | Standard Operation |
|--------|-------------------|
| Decision summary report | Save Decision |
| Action items | Save Task |
| RETROSPECTIVE / AUDITOR / ADVISOR reports | Save JournalEntry |
| Inspection reports | Save JournalEntry (type: inspection) |
| Research / knowledge | Save WikiNote |
| Goals | Update Area (goals field) |
| Global status | Update via adapter-specific STATUS mechanism |

---

## Storage Backend

Life OS uses a **single storage backend**: a git repository (local working copy + GitHub remote).

| Backend | Adapter | Format |
|---------|---------|--------|
| GitHub (git) | `references/adapter-github.md` | .md + front matter |

> Earlier versions also offered Google Drive and Notion; both were removed — storage is GitHub-only.

Standard data types and operations: `references/data-model.md`

Sync, conflict, deletion, failure handling: `references/data-model.md`

---

## RETROSPECTIVE Data Operations

All operations use standard interfaces, mapped to git operations on the local working copy.

### Housekeeping Mode (Start of Conversation)

```
0. DATA LAYER CHECK: If meta/config.md does not exist → FIRST-RUN mode:
   - Create minimum directory structure: meta/ (config.md, STATUS.md, journal/, outbox/), projects/, areas/, wiki/, inbox/, archive/, templates/
   - Write meta/config.md
   - Skip steps 1-8, proceed to briefing
1. Read meta/config.md.
2. Probe git remote availability (git status / git remote). Unreachable → mark local-only for this session.
3. `git pull` to absorb changes pushed from other devices.
   - Not a git repo / no remote → local working copy only (annotate "💾 Storage: local only").
   - Merge conflict → surface conflicting files to the user (see data-model.md).
4. OUTBOX MERGE: scan meta/outbox/ for unmerged sessions
   - If meta/.merge-lock exists and < 5min → skip merge
   - Write .merge-lock → merge each outbox → compile STATUS.md → commit + push → delete .merge-lock
   - Report merged sessions in briefing
5. Read inbox (unprocessed items) — from the local working copy
6. Read meta/STATUS.md (global status)
7. Read meta/lint-state.md (check if inspection needed: >4h since last run)
8. ReadProjectContext(bound project) — tasks, decisions, journal
9. Read meta/user-patterns.md
10. Global overview: List Project + List Area (titles + status only)
11. Strategic Map compilation: If `meta/strategic-lines.md` exists → compile `meta/STRATEGIC-MAP.md`. See `references/strategic-map-spec.md`.
12. If lint-state.md shows >4h → trigger lightweight AUDITOR inspection
13. Platform awareness + version check
```

### Wrap-Up Mode (End of Process)

```
1. Generate session-id: run date command to get actual timestamp, format as {platform}-{YYYYMMDD}-{HHMM}. Do NOT fabricate — use system clock. HARD RULE.
2. Create meta/outbox/{session_id}/
3. Save Decision / Save Task / Save JournalEntry → to meta/outbox/{session_id}/ (NOT to main directories)
4. Write index-delta.md (changes for projects/{project}/index.md)
5. Write patterns-delta.md (append content for meta/user-patterns.md, if ADVISOR has suggestions)
6. Write manifest.md (session metadata)
7. git add meta/outbox/{session_id}/ → commit → push (ONLY the outbox directory)
8. Push fails (offline / no remote) → keep the commit local, annotate "⚠️ not pushed — syncs next session". Do not block.

NOTE: Do NOT write to projects/, STATUS.md, or meta/user-patterns.md directly. Merging happens at next Start Court.
```

### Review Mode

```
1. Read meta/STATUS.md for global state
2. List Task (all projects) → compute completion rates
3. List Area → read goals
4. List JournalEntry (recent) → journals and inspection reports
5. Metrics dashboard computed from results
```

## ADVISOR Data Retrieval

```
1. Read meta/user-patterns.md
2. List JournalEntry (type: remonstrator, limit: 3) → last 3 reports
3. List Decision (limit: 5) → recent decisions
4. List Task → compute completion rates
```

## Single Source of Truth Rules

**`projects/{project}/index.md` is the authoritative source for each project's version, phase, and status.** `meta/STATUS.md` is a compiled dashboard — it must be generated from index.md files, never hand-written.

| Data | Authoritative Source | Compiled View |
|------|---------------------|---------------|
| Project version / phase / status | `projects/{project}/index.md` | `meta/STATUS.md` |
| Area goals / status | `areas/{area}/index.md` | `meta/STATUS.md` |
| Task completion | `projects/{project}/tasks/*.md` | Metrics dashboard |
| Behavior patterns | `meta/user-patterns.md` | ADVISOR reports |
| Strategic relationships | `projects/{project}/index.md` strategic fields + `meta/strategic-lines.md` | `meta/STRATEGIC-MAP.md` |

**Write order is enforced**: Always update the authoritative source first, then compile the dashboard. Never write to STATUS.md directly for project-level information.

**AUDITOR lint rule**: During patrol inspection, check that `meta/STATUS.md` version/status for each project matches `projects/{project}/index.md`. If inconsistent → report 🔴, flag the authoritative source as correct.

---

## Degradation Rules

- Git remote unreachable → commit locally, annotate "⚠️ not pushed — syncs next session"
- Not a git repo / no remote → operates normally, output displayed in conversation but not persisted
