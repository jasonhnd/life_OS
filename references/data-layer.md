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

**Capture → Activate (Cortex Pre-Router, v1.7)**: Before ROUTER triages the user message, three parallel subagents run — hippocampus (cross-session retrieval from `_meta/sessions/INDEX.md`), concept lookup (spreading activation across `_meta/concepts/`), SOUL dimension check (reuses RETROSPECTIVE's SOUL Health Report). The GWT arbitrator consolidates their signals into an annotated input. ROUTER receives the annotated input, not the raw message. Failure modes degrade to v1.6.2a behaviour (raw message to ROUTER). See `references/cortex-spec.md` §Workflow Integration.

**Activate → Judge (Draft-Review-Execute cycle)**: Desktop CC pulls from inbox. Not all information needs decisions. Only when major resource allocation, multi-option trade-offs, or hard-to-reverse consequences are involved, activate the Draft-Review-Execute decision mode. The judge stage operates on cognitively-annotated input — PLANNER / REVIEWER / six domains start from context, not cold.

**Judge → Settle (SOUL + Wiki + Concepts + Methods + Snapshots)**: Conclusions from decisions settle into five pools — SOUL (who you are), Wiki (what you know about the world), Concepts (the synaptic graph that connects knowledge), Methods (procedural memory — reusable workflows), and Snapshots (historical SOUL state for trend computation). All are auto-written under strict criteria: ARCHIVER Phase 2 produces wiki / SOUL / concept / method / snapshot candidates; users nudge post-hoc (delete file to retire, say "undo recent" to roll back). See `references/concept-spec.md`, `references/method-library-spec.md`, `references/snapshot-spec.md`.

**Settle → Associate (ROUTER + Wiki INDEX + Concept INDEX + Methods INDEX)**: The ROUTER reads compiled INDEX files at session start (wiki/INDEX.md, _meta/concepts/INDEX.md, _meta/methods/INDEX.md, _meta/sessions/INDEX.md). When a new request arrives, existing knowledge is automatically matched — "we already know X about this domain, and we have a canonical method for Y." This turns accumulated knowledge into active context.

**Associate → Strategize (Strategic Map)**: The ROUTER reads `_meta/STRATEGIC-MAP.md` at session start. When a request involves a project with strategic relationships, the system automatically surfaces downstream dependencies, bottleneck status, and decision propagation warnings. This turns per-project analysis into strategic-line-aware analysis. See `references/strategic-map-spec.md`.

**Strategize → Emerge (DREAM REM)**: When wiki entries and strategic relationships accumulate, DREAM's REM stage discovers cross-domain connections using the flow graph as scaffolding — checking SOUL × strategy alignment, wiki × flow completeness, and behavioral pattern × strategic priority consistency. The more knowledge and relationships settle, the more emergence happens. AUDITOR patrol also detects wiki contradictions, knowledge gaps, and strategy contradictions between projects.

### Mobile vs Desktop Division

Mobile handles perception and capture only (occasionally lightweight association like web search). Desktop handles association, judgment, settlement, and emergence — all heavy lifting. Mobile can read pipeline outputs (STATUS.md, archives) but writes only at the capture stage.

---

## GitHub Directory Structure

```
second-brain/
│
├── SOUL.md                            # 🔮 User personality archive (values, beliefs, identity — grows from zero)
├── user-patterns.md                   # 📊 Behavioral patterns (what you DO — ADVISOR-maintained)
│
├── inbox/                             # 📥 Unprocessed (mobile captures, materials, book notes, raw research)
│
├── _meta/                             # 🔧 System metadata
│   ├── STATUS.md                      # Global status dashboard (compiled from index.md files)
│   ├── STRATEGIC-MAP.md               # Strategic map (compiled from project strategic fields)
│   ├── strategic-lines.md             # Strategic line definitions (user-defined)
│   ├── MAP.md                         # Knowledge map (all area entry points)
│   ├── decisions/                     # Cross-domain major decisions
│   ├── journal/                       # RETROSPECTIVE briefings, AUDITOR/ADVISOR reports, DREAM reports
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
| Factual / declarative knowledge | wiki/ | "NPO lending in Japan has no 貸金業法 exemption" |
| Procedural knowledge (reusable workflows, v1.7) | `_meta/methods/` | "Refine documents in 5 escalating quality rounds" |
| Concept graph (synapses, v1.7) | `_meta/concepts/` | "company-a-holding" node with weighted edges to related concepts |

These types may expand over time based on actual usage. v1.7 splits "Process knowledge" into two: factual process descriptions stay in `wiki/`, reusable procedural workflows move to `_meta/methods/` (see `references/method-library-spec.md`).

---

## Knowledge Extraction: Four-Step Training

1. **User decides**: Desktop CC generates an "extraction proposal", user confirms/modifies
2. **Accumulate samples**: Record to `_meta/extraction-log.md`
3. **LLM induces rules**: From the log, induce preferences and write to `_meta/extraction-rules.md` (pure markdown, model-agnostic)
4. **Periodic correction**: User reviews monthly, reports misclassifications, CC updates rules

Core: The "learning" carrier is markdown files, not model weights. Switching models only requires reading these files.

---

## AUDITOR: Two Operating Modes

The AUDITOR runs in two modes within the Draft-Review-Execute system:

### Mode 1: Decision Review (existing)

After every Draft-Review-Execute workflow, reviews official work quality. Already defined in `pro/agents/auditor.md`.

### Mode 2: Patrol Inspection (new)

When idle, each domain inspects its own jurisdiction. Defined in `_meta/roles/censor.md`.

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
| INFRA | wiki/ + _meta/ | Orphan files, broken links, rule validity |
| PEOPLE | areas/career/ | Career direction aligned with actions |
| GOVERNANCE | Cross-domain | Strategy contradictions between projects, decisions missing risk assessment |

#### Issue Classification

| Level | Action | Example |
|-------|--------|---------|
| **Auto-fix** | AUDITOR handles directly | Missing index entries, missing backlinks, format issues |
| **Suggest** | Send to inbox for user | Data inconsistency, project possibly stalled, wiki suggestion |
| **Escalate** | Activate Draft-Review-Execute decision mode | Financial contradictions >¥1M, multi-project strategy conflict, interpersonal risk |

#### Implementation

- Role definition stored in `_meta/roles/censor.md`, CLAUDE.md only references it
- Inspection state persisted in `_meta/lint-state.md` (solves LLM's lack of cross-session memory)
- Inspection reports stored in `_meta/lint-reports/`, summary also sent to inbox
- Switching models: role files stay unchanged, only CLAUDE.md references change

---

## Expandable Resident Roles

| Role | File | Function |
|------|------|----------|
| AUDITOR | `_meta/roles/censor.md` | Patrol inspection (required) |
| Historian | `_meta/roles/historian.md` | Auto-records daily work at session end (optional) |
| REVIEWER on-duty | `_meta/roles/reviewer.md` | Reviews content quality on write (optional) |

---

## Draft-Review-Execute Output Destinations

All outputs use standard operations from `references/data-model.md`. The adapter for the user's chosen backend translates these into platform-specific calls.

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

## Storage Backends

Life OS supports three storage backends. Users choose 1, 2, or all 3.

| Backend | Best For | Adapter | Format |
|---------|----------|---------|--------|
| GitHub | Technical users, Claude Code | `references/adapter-github.md` | .md + front matter |
| Google Drive | General users, zero setup | `references/adapter-gdrive.md` | .md + front matter |
| Notion | Notion users | `references/adapter-notion.md` | Notion databases |

Standard data types and operations: `references/data-model.md`

Multi-backend rules (sync, conflict, deletion, failure handling): `references/data-model.md`

---

## RETROSPECTIVE Data Operations

All operations use standard interfaces. Adapt calls per the user's configured backend(s).

### Housekeeping Mode (Start of Conversation)

```
0. Read _meta/config.md → get backend list and THIS PLATFORM's last sync timestamp
0. DATA LAYER CHECK: If _meta/config.md does not exist → FIRST-RUN mode:
   - Ask user for storage backend choice (GitHub / GDrive / Notion)
   - Create minimum directory structure: _meta/ (config.md, STATUS.md, journal/, outbox/), projects/, areas/, wiki/, inbox/, archive/, templates/
   - Write _meta/config.md with chosen backends
   - Skip steps 1-8, proceed to briefing
1. Read _meta/config.md → get backend list and THIS PLATFORM's last sync timestamp
2. Probe each configured backend for MCP availability (mark unavailable as SKIPPED)
3. Multi-backend sync (if multiple backends configured and available):
   - Query each AVAILABLE sync backend for changes since this platform's last_sync_time
   - Compare, resolve conflicts (see data-model.md)
   - Apply changes to primary backend
   - Push to sync backends
4. OUTBOX MERGE: scan _meta/outbox/ for unmerged sessions
   - If _meta/.merge-lock exists and < 5min → skip merge
   - Write .merge-lock → merge each outbox → compile STATUS.md → commit + push → delete .merge-lock
   - Report merged sessions in briefing
5. Read inbox (unprocessed items) — via primary backend
6. Read _meta/STATUS.md (global status)
7. Read _meta/lint-state.md (check if inspection needed: >4h since last run)
8. ReadProjectContext(bound project) — tasks, decisions, journal
9. Read user-patterns.md
10. Global overview: List Project + List Area (titles + status only)
11. Strategic Map compilation: If `_meta/strategic-lines.md` exists → compile `_meta/STRATEGIC-MAP.md`. See `references/strategic-map-spec.md`.
12. If lint-state.md shows >4h → trigger lightweight AUDITOR inspection
13. Platform awareness + version check
```

### Wrap-Up Mode (End of Process)

```
1. Generate session-id: run date command to get actual timestamp, format as {platform}-{YYYYMMDD}-{HHMM}. Do NOT fabricate — use system clock. HARD RULE.
2. Create _meta/outbox/{session_id}/
3. Save Decision / Save Task / Save JournalEntry → to _meta/outbox/{session_id}/ (NOT to main directories)
4. Write index-delta.md (changes for projects/{project}/index.md)
5. Write patterns-delta.md (append content for user-patterns.md, if ADVISOR has suggestions)
6. Write manifest.md (session metadata)
7. git add _meta/outbox/{session_id}/ → commit → push (ONLY the outbox directory)
8. Sync outbox to Notion (if configured)
9. Update this platform's last_sync_time in _meta/config.md
10. Any backend failure → log to _meta/sync-log.md, don't block

NOTE: Do NOT write to projects/, STATUS.md, or user-patterns.md directly. Merging happens at next Start Court.
```

### Review Mode

```
1. Read _meta/STATUS.md for global state
2. List Task (all projects) → compute completion rates
3. List Area → read goals
4. List JournalEntry (recent) → journals and inspection reports
5. Metrics dashboard computed from results
```

## ADVISOR Data Retrieval

```
1. Read user-patterns.md
2. List JournalEntry (type: remonstrator, limit: 3) → last 3 reports
3. List Decision (limit: 5) → recent decisions
4. List Task → compute completion rates
```

## Single Source of Truth Rules

**`projects/{project}/index.md` is the authoritative source for each project's version, phase, and status.** `_meta/STATUS.md` is a compiled dashboard — it must be generated from index.md files, never hand-written.

| Data | Authoritative Source | Compiled View |
|------|---------------------|---------------|
| Project version / phase / status | `projects/{project}/index.md` | `_meta/STATUS.md` |
| Area goals / status | `areas/{area}/index.md` | `_meta/STATUS.md` |
| Task completion | `projects/{project}/tasks/*.md` | Metrics dashboard |
| Behavior patterns | `user-patterns.md` | ADVISOR reports |
| Strategic relationships | `projects/{project}/index.md` strategic fields + `_meta/strategic-lines.md` | `_meta/STRATEGIC-MAP.md` |

**Write order is enforced**: Always update the authoritative source first, then compile the dashboard. Never write to STATUS.md directly for project-level information.

**AUDITOR lint rule**: During patrol inspection, check that `_meta/STATUS.md` version/status for each project matches `projects/{project}/index.md`. If inconsistent → report 🔴, flag the authoritative source as correct.

---

## Degradation Rules

- Primary backend unreachable → annotate "⚠️ primary backend unavailable"
- Sync backend unreachable → annotate ⚠️, log, retry next session
- All backends unavailable → operates normally, output displayed in conversation but not persisted
