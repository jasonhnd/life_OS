# Standard Data Model

All Life OS data operations use these standard types and interfaces. Adapters translate them to platform-specific calls.

## Data Types

### Decision

> ⚠️ **v1.9 schema supersedes this table** (per RFC §3.3.2 / §11.2.1 + `hosts/CLAUDE.md` §"Decision Records"). v1.9 is the canonical decision-record frontmatter; the pre-v1.9 fields below are retained for historical reference / legacy file parsing. **Field-name collision note**: v1.9 reuses `type` for the decision-record kind (`change` / `no_change` / `escalation` / `superseded`), NOT the pre-v1.9 workflow kind (`simple` / `3d6m`). When writing a new decision, use the v1.9 schema.

**v1.9 canonical schema** (`meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | `dec-<YYYY-MM-DD>-<NNN>` (per-day sequence) |
| title | string | yes | Short title |
| type | enum | yes | `change` / `no_change` / `escalation` / `superseded` |
| projects | string[] | yes | Owning project(s); `[]` = cross-project |
| domains | string[] | yes | Subset of 6 functional IDs: governance/execution/finance/infra/people/growth |
| reviewed_by | string | yes | agent or human |
| reviewed_at | date | yes | ISO date |
| decision | text | yes | One-line decision |
| rationale | text | yes | Why |
| reopen_condition | text | cond | Mandatory when `type: no_change` |
| supersedes / superseded_by | string[] / string | no | Decision lineage |
| applied_methods | string[] | no | Methods applied (list; Opt #8) |
| journal_date | date | no | Day's journal file (Opt #8) |
| content | text | yes | Summary report full text (body) |

<details><summary>Pre-v1.9 fields (legacy, do not use for new decisions)</summary>

| Field | Type | Description |
|-------|------|-------------|
| type | enum | `simple` / `3d6m` (workflow — superseded by v1.9 `type`) |
| status | enum | `considering` / `decided` / `reversed` |
| category | enum | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | `good` / `neutral` / `bad` / `tbd` |
| score / veto_count | number | composite score / veto events |
| date / project / area | — | superseded by `reviewed_at` / `projects` / (area via project) |

</details>

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

> ⚠️ **v1.9 schema supersedes this table** (per RFC §3.5 Opt #5 time-axis + §3.8 Opt #8 cross-references). v1.9 journal is **one file per day** at `meta/journal/<YYYY-MM-DD>.md` (time-axis canonical; multiple entries appended under the day, merged by `projects:` when the day already exists). The pre-v1.9 per-entry fields below are legacy.

**v1.9 canonical schema** (`meta/journal/<YYYY-MM-DD>.md`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| date | date | yes | The day (also the filename) |
| projects | string[] | yes | Projects mentioned this day; `[]` = none |
| session_ids | string[] | no | Session ids contributing entries to this day |
| type_tags | string[] | yes | Entry kinds present: `briefing` / `dream` / `advisor` / `auditor` / `migration` / … |
| referenced_decisions | string[] | no | Decision ids referenced this day (Opt #8) |
| referenced_methods | string[] | no | Method names applied this day (Opt #8) |
| content | text | yes | Day's entries (body; multiple sections appended) |

<details><summary>Pre-v1.9 fields (legacy per-entry model, do not use for new journal)</summary>

| Field | Type | Description |
|-------|------|-------------|
| id / title | string | superseded — daily file is keyed by `date` |
| type | enum | `morning-court` / `censorate` / `remonstrator` / `inspection` / `manual` — superseded by `type_tags` (list) |
| mood / energy | enum | dropped in the v1.9 daily-aggregate model |
| tags | string[] | folded into `type_tags` |
| last_modified | datetime | superseded |

</details>

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

`projects/{p}/index.md` frontmatter. **v1.9 added `lifecycle_stage` (+ `paused_until` / `archived_*` / `created_at`)** for PARA-archival state (per RFC §3.4 Opt #4 + DR-1.9.20 — replaces the old `archive/` directory; archived projects stay in `projects/{p}/` so wikilinks survive). This is a **separate axis** from the workflow `status`: `lifecycle_stage` answers "active PARA set vs archived?", while `status` + `strategic.status_reason` drive workflow + strategic-map stall detection. Both coexist.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project / name | string | yes | Project name (also the directory) |
| lifecycle_stage | enum | yes | **v1.9** · archival axis — `candidate` / `active` / `archived` / `superseded` |
| paused_until | date \| null | no | **v1.9** · time-bounded pause (replaces "dormant"); `> today` = paused-active, hidden from STATUS warnings |
| created_at | date | yes | **v1.9** · creation date |
| archived_at | date \| null | cond | **v1.9** · set when `lifecycle_stage: archived` |
| archived_at_source | enum \| null | cond | **v1.9** · `git-log` / `migrated-unknown` / `manual` / `auto` (when archived) |
| archived_reason | text | cond | **v1.9** · mandatory when `lifecycle_stage: archived` |
| superseded_by | string | cond | **v1.9** · mandatory when `lifecycle_stage: superseded` |
| status | enum | no | Workflow axis — `planning` / `active` / `on-hold` / `done` / `dropped`; strategic-map stall detection reads this + `strategic.status_reason` |
| strategic | object | no | Strategic-map fields (`line` / `role` / `flows_to` / `flows_from` / `last_activity` / `status_reason`) — see `references/strategic-map-spec.md` |
| related_wiki | wikilink[] | no | **v1.9** · `[[wiki/<entry>]]` links |
| priority | enum | no | `p0` / `p1` / `p2` / `p3` |
| deadline | date | no | |
| area | string | no | Associated area |
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

### StrategicLine

Stored in `meta/strategic-lines.md` (user's second-brain). Multiple lines separated by `---`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique identifier (kebab-case) |
| name | string | yes | Display name |
| purpose | text | yes | One-sentence formal purpose |
| driving_force | text | no | What truly drives investment in this line (can differ from purpose) |
| health_signals | text[] | no | What signals indicate this line is healthy (AI proposes, user confirms) |
| time_window | date | no | Deadline affecting the entire line |
| area | string | no | Associated life area |
| created | date | auto | Creation date |

### Per-Project Strategic Fields

Optional extension to `projects/{project}/index.md` frontmatter. All fields default to empty/null.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| strategic.line | string | no | Strategic line ID (references `meta/strategic-lines.md`) |
| strategic.role | enum | no | `critical-path` / `enabler` / `accelerator` / `insurance` |
| strategic.flows_to[] | array | no | Outgoing flows: [{target, type, description}] |
| strategic.flows_from[] | array | no | Incoming flows: [{source, type, description}] |
| strategic.last_activity | date | auto | Last modification date (auto-updated by ARCHIVER) |
| strategic.status_reason | text | no | Why this project is in its current status |

Flow types: `cognition` / `resource` / `decision` / `trust`. Role and flow definitions: `references/strategic-map-spec.md`.

---

## v1.7 Cortex Data Types

The following types are introduced in v1.7 for the Cortex cognitive layer. Each has its own authoritative spec file; this table is the short form.

### SessionSummary

Authoritative spec: `references/session-index-spec.md` §3.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | yes | Format `{platform}-{YYYYMMDD}-{HHMM}` |
| date | date | yes | ISO 8601 date |
| started_at | datetime | yes | Timezone-aware timestamp |
| ended_at | datetime | yes | Timezone-aware timestamp |
| duration_minutes | integer | yes | |
| platform | enum | yes | `claude` / `gemini` / `codex` |
| theme | enum | yes | Theme ID (e.g. `zh-classical`, `ja-kasumigaseki`) |
| project | string | yes | Bound project (enforces session-binding HARD RULE) |
| workflow | enum | yes | `full_deliberation` / `express_analysis` / `direct_handle` / `strategist` / `review` |
| subject | string | yes | Extracted subject (max 200 chars) |
| domains_activated | string[] | no | Subset of PEOPLE/FINANCE/GROWTH/EXECUTION/GOVERNANCE/INFRA |
| overall_score | number | no | 0-10 from Summary Report |
| domain_scores | map | no | Per-domain 0-10 scores |
| veto_count | integer | no | REVIEWER veto events |
| council_triggered | boolean | no | COUNCIL debate fired? |
| soul_dimensions_touched | string[] | no | SOUL dimension IDs referenced |
| wiki_written | string[] | no | Wiki entry IDs auto-written this session |
| methods_used | string[] | no | Method IDs applied |
| methods_discovered | string[] | no | New method IDs archived |
| concepts_activated | string[] | no | Concept IDs referenced |
| concepts_discovered | string[] | no | New concept IDs written by archiver Phase 2 |
| dream_triggers | string[] | no | DREAM REM trigger names fired |
| keywords | string[] | no | Up to 10, for hippocampus Wave 1 scan |
| action_items | array | no | `[{text, deadline, status}]` |
| compliance_violations | integer | no | AUDITOR-flagged violations |

Storage: `meta/sessions/{session_id}.md`. Immutable after archiver writes.

### Concept

Authoritative spec: `references/concept-spec.md` §YAML Frontmatter Schema.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| concept_id | string | yes | Lowercase + hyphens, ≤64 chars, unique |
| canonical_name | string | yes | Human-readable display name |
| aliases | string[] | no | Alternative surface forms |
| domain | enum | yes | `finance` / `startup` / `personal` / `technical` / `method` / `relationship` / `health` / `legal` / user-extensible |
| status | enum | yes | `tentative` / `confirmed` / `canonical` |
| permanence | enum | yes | `identity` / `skill` / `fact` / `transient` |
| activation_count | integer | yes | Monotonic during active life |
| last_activated | datetime | yes | Used by decay pass |
| created | datetime | yes | Creation timestamp |
| outgoing_edges | array | no | `[{to: concept_id, weight: 1-100, via: [tag], last_reinforced: ISO}]` |
| provenance.source_sessions | string[] | no | Session IDs where evidence appeared |
| provenance.extracted_by | enum | no | `archiver` / `manual` / `dream` |
| decay_policy | enum | yes | Matches `permanence` tier |

Storage: `meta/concepts/{domain}/{concept_id}.md` (confirmed/canonical) or `meta/concepts/_tentative/{concept_id}.md` (tentative).

### SoulSnapshot

Authoritative spec: `references/snapshot-spec.md` §YAML Frontmatter Schema.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| snapshot_id | string | yes | `{YYYY-MM-DD-HHMM}`, matches filename |
| captured_at | datetime | yes | Real ISO 8601 timestamp from system clock |
| session_id | string | yes | References `meta/sessions/{session_id}.md` |
| previous_snapshot | string \| null | yes | Prior filename or null for first snapshot |
| dimensions | array | yes | `[{name, confidence: 0-1, evidence_count, challenges, tier}]` where tier ∈ `core`/`secondary`/`emerging` |

Storage: `meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md`. Metadata only — no SOUL body content. Immutable.

### EvalEntry

Authoritative spec: `references/eval-history-spec.md` §3.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| eval_id | string | yes | `{YYYY-MM-DD-HHMM}-{project}` |
| session_id | string | yes | References `meta/sessions/` entry |
| evaluator | enum | yes | `auditor` / `auditor-patrol` |
| evaluation_mode | enum | yes | `decision-review` / `patrol-inspection` |
| date | datetime | yes | |
| scores | map | yes | 10 dimensions, each 0-10 integer (see eval-history-spec §5) |
| violations | array | no | `[{type, agent, severity, detail}]` |
| agent_quality_notes | map | no | Per-agent one-line observations |

Storage: `meta/eval-history/{YYYY-MM-DD}-{project}.md`. Local-only. Immutable after creation. No migration backfill.

### Soul

Authoritative spec: `references/soul-spec.md`. Unlike the other v1.7 types, `Soul` is the **in-memory view of the live `SOUL.md` file**, not a per-record file. Tools read the whole SOUL.md, parse it into this structure, and (for archiver-side auto-writes) write back.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| path | Path | yes | Absolute path to `SOUL.md` |
| dimensions | `List[SoulDimension]` | yes | All parsed dimensions (may be empty for new users) |
| raw_body | str | yes | Full markdown body (for diff-based writes) |

`SoulDimension` sub-record:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | yes | Dimension name (e.g. "risk-tolerance") |
| confidence | float | yes | 0-1, auto-calculated via `evidence_count / (evidence_count + challenges × 2)` |
| evidence_count | int | yes | |
| challenges | int | yes | |
| source | enum | yes | `dream` / `advisor` / `strategist` / `user` |
| created | date | yes | YYYY-MM-DD |
| last_validated | date | yes | YYYY-MM-DD |
| tier | enum | auto | `core` (≥0.7) / `secondary` (0.3-0.7) / `emerging` (0.2-0.3) / `dormant` (<0.2) — derived at read time |
| what_is | str | no | Body section "What IS (实然)" |
| what_should_be | str | no | Body section "What SHOULD BE (应然)" |
| gap | str | no | Body section "Gap (差距)" |
| evidence | `List[str]` | no | Body section "Evidence" bullets |
| challenges_list | `List[str]` | no | Body section "Challenges" bullets |

Storage: single file `SOUL.md` at second-brain root. Read by every major role; written by ARCHIVER Phase 2 (auto-write criteria in soul-spec) and by user directly.

### Method

Authoritative spec: `references/method-library-spec.md` §4.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| method_id | string | yes | Lowercase + hyphens, unique |
| name | string | yes | Display name |
| description | string | yes | One-liner for INDEX.md |
| domain | enum | yes | Same domain vocabulary as Concept |
| status | enum | yes | `tentative` / `confirmed` / `canonical` |
| confidence | number | yes | 0-1, formula `evidence_count / (evidence_count + challenges × 2)` |
| times_used | integer | yes | Increments every session that applies the method |
| last_used | datetime | no | ISO 8601 |
| applicable_when | array | no | `[{condition, signal}]` |
| not_applicable_when | array | no | `[{condition}]` |
| source_sessions | string[] | no | session_ids that contributed |
| evidence_count | integer | yes | Sessions where the method worked |
| challenges | integer | yes | Sessions where it failed |
| related_concepts | string[] | no | concept_ids |
| related_methods | string[] | no | method_ids (soft composition) |

Storage: `meta/methods/{domain}/{method_id}.md` or `meta/methods/_tentative/{method_id}.md`. Local-only.

---

## Standard Operations

All agents use these operations. Adapters translate them to platform-specific calls.

| Operation | Signature | Description |
|-----------|-----------|-------------|
| **Save** | `Save(type, data)` | Create a new record |
| **Update** | `Update(type, id, data)` | Modify an existing record |
| **Archive** | `Archive(type, id)` | **v1.9 semantics change** (DR-1.9.4): for projects, sets `lifecycle_stage: archived` + `archived_at` + `archived_at_source` in frontmatter; does NOT physically move directory (preserves wikilinks). For other types (decisions/sessions), legacy archive semantics still apply. |
| **Read** | `Read(type, id)` | Get a single record |
| **List** | `List(type, filters)` | Get records matching filters. **v1.9**: default `List(Project, ...)` filters `lifecycle_stage != archived`; pass `include_archived: true` to override. |
| **Search** | `Search(keyword)` | Full-text search across all types |
| **ReadProjectContext** | `ReadProjectContext(project_id)` | Batch read: project index + tasks + (v1.9 update) cross-referenced decisions from `meta/decisions/<YYYY-MM>/` via projects field + journal from `meta/journal/` via projects field |

### v1.9 archive semantics (per RFC §3.4 + DR-1.9.4)

Pre-v1.9: `Archive(Project, id)` = `mv projects/{id}/ archive/{id}/` — broke all wikilinks pointing to `[[projects/{id}/...]]`.

v1.9: `Archive(Project, id)` = `Update(Project, id, {lifecycle_stage: archived, archived_at: <today>, archived_at_source: auto, archived_reason: <description>})`. The project stays in `projects/{id}/`. All wikilinks remain resolvable.

Index compilers (retrospective Mode 0 → STATUS.md / STRATEGIC-MAP.md, archiver Phase 1 → STATUS update) filter `lifecycle_stage: archived` by default. Obsidian graph view colorGroup styles archived projects in muted gray. wiki/INDEX does NOT filter (historical knowledge stays visible).

`archived_at_source` enum (4 values per DR-1.9.26):
- `git-log` — `/migrate-v1.9` Stage 3 derived from git log timestamps
- `migrated-unknown` — `/migrate-v1.9` fallback when git log returned nothing
- `manual` — user hand-edited the frontmatter
- `auto` — archiver/REVIEWER auto-archive in normal session flow

---

## Storage Backend (GitHub + local working copy)

Life OS uses a **single storage backend**: a git repository. The second-brain lives as a local working copy on disk (also your Obsidian vault); GitHub is the remote that backs it up and syncs it across devices. There is no primary/sync split, no per-backend probing, and no cross-backend conflict layer — git provides versioning, backup, and multi-device sync natively.

> Earlier versions also offered Google Drive and Notion as selectable backends with a multi-backend sync protocol; both were removed — storage is GitHub-only.

### Read / Write

- **Read** — from the local working copy (the files on disk).
- **Write** — to the local working copy. Persistence to the GitHub remote happens at session end via git (ARCHIVER Phase 4).

---

## Sync Protocol

Sync is plain git — no MCP probing, no primary/sync split, no per-platform `last_sync` bookkeeping. Git history is the record of "what changed since last time".

### Session Start (RETROSPECTIVE Housekeeping)

```
1. `git pull` (fetch + merge) the second-brain repo to absorb changes pushed from other devices.
2. Not a git repo / no remote configured → operate on the local working copy only; annotate "💾 Storage: local only (no remote)".
3. Merge conflict on pull → surface the conflicting files to the user to resolve (rare for single-user vaults).
```

### Session End (ARCHIVER Phase 4)

```
1. Merge session outboxes into the main structure (see Constraints · outbox pattern).
2. `git add` + `git commit` the session's changes.
3. `git push` to the remote. Push fails (offline / no remote) → annotate "⚠️ not pushed — will sync next session", keep the commit local.
```

---

## Conflict Resolution

A single backend means no cross-backend divergence. The only conflict source is two devices editing the same file between syncs, which surfaces as a **git merge conflict** on `git pull`:

| Situation | Action |
|-----------|--------|
| Clean pull (no overlap) | Fast-forward / auto-merge, proceed |
| Same file edited on two devices | git merge conflict → ROUTER surfaces the conflicting files, user resolves, commit the resolution |

The outbox pattern (one directory per session) makes same-file conflicts rare even with concurrent local sessions.

---

## Deletion Rules

- Deletion is a normal git operation (`git rm` / delete the file + commit). It propagates on the next push/pull like any other change.
- No soft-delete `_deleted: true` tombstones and no cross-backend deletion prompts — those existed only to reconcile multiple backends.

---

## Failure Handling

| Scenario | Handling |
|----------|---------|
| Remote unreachable at session end | Commit locally, skip push, annotate ⚠️. Next session's `git push` catches up. |
| Merge conflict on pull | Surface the conflicting files; user resolves before proceeding. |
| Not a git repo / no remote | Operate on the local working copy only; nothing is pushed. Output still shown in conversation. |
| New device | `git clone` the second-brain repo → ready. No second-brain → session-level config. |

---

## Configuration

The git remote lives in the repo's own `.git/config` — Life OS does not duplicate it. `meta/config.md` no longer carries a `storage.backends` list or per-platform `last_sync` timestamps (git history is the source of truth for "what changed since last time").

```yaml
# meta/config.md (storage section)
storage:
  remote: github          # single backend; "none" = local-only working copy

# optional (v1.10.0 · issue #4 D1) — where the behavioral-patterns file lives
user_patterns_path: meta/user-patterns.md   # default: vault-resident
```

### `user_patterns_path` override (v1.10.0)

`meta/user-patterns.md` accumulates the system's most expensive asset — learned behavioral rules, each paid for with a real mistake. Since v1.9 (Opt #7) the **default is vault-resident**: versioned by git, synced across machines, visible to patrols. The override exists for privacy-cautious users who prefer the file outside the vault:

- `user_patterns_path: meta/user-patterns.md` (default) — versioned + backed up + patrol-visible; travels with vault backups/shares.
- `user_patterns_path: ~/.claude/user-patterns.md` (opt-out) — machine-local; NOT versioned, NOT synced, invisible to patrols. A laptop migration or disk failure silently loses it. Choose this only when the vault is shared and the patterns must not travel with it.

All readers/writers (ADVISOR guidance writeback, retrospective context loading, outbox `patterns-delta.md` merge, AUDITOR Mode 2 patrol) resolve the path from this field; when the field is absent, use the default.

**Migration note (pre-v1.9 installs)**: if a legacy `~/.claude/user-patterns.md` exists and `user_patterns_path` is unset/default, move it into the vault — `mv ~/.claude/user-patterns.md <vault>/meta/user-patterns.md` (or run `/migrate-v1.9` Stage 6, which does this for a vault-root copy) — then commit. Keeping months of behavioral tuning in an unversioned machine-local file is the failure mode this override closes.

No second-brain → ROUTER operates session-local (no persistence).

---

## Constraints

- **Multiple sessions can operate the second-brain simultaneously** using the outbox pattern. Each session writes to its own outbox directory (`meta/outbox/{session_id}/`). The next session to start court merges all outboxes into the main structure. Direct writes to shared files (STATUS.md, meta/user-patterns.md, index.md) only happen during the outbox merge step at Start Court.
- **Session-id format**: `{platform}-{YYYYMMDD}-{HHMM}`, generated at adjourn time (not session start). Example: `claude-20260412-1700`, `gemini-20260412-1900`.
- **Outbox merge lock**: During merge, write `meta/.merge-lock`. If it exists and is < 5 minutes old, skip merge and proceed normally. Delete after merge completes.
- **Empty sessions**: If a session has no output (no decisions, tasks, or journal entries), do not create an outbox.
- Mobile capture lands in `inbox/` via the user's own git workflow (mobile git client / synced folder), not directly into structured data; it is processed on the next desktop session
- All adapters must support the 7 standard operations

### Outbox Manifest Format

Each outbox directory contains a `manifest.md`:

```yaml
---
session_id: "claude-20260412-1700"
platform: claude-code
model: opus
projects: [project-a, project-b]
adjourned: "2026-04-12T17:00:00+09:00"
outputs:
  decisions: 2
  tasks: 5
  journal: 3
  wiki: 1
  dream: 1
  index_delta: true
  patterns_delta: true
---
```

### Index Delta Format

`index-delta.md` records changes to apply to `projects/{project}/index.md`:

```markdown
# Index Delta

## Target: projects/my-project/index.md
## Fields to update:
- Phase: "v5.4 deployed"
- Current focus: "打磨计划书到对外版本"
```

### Patterns Delta Format

`patterns-delta.md` records content to append to `meta/user-patterns.md`:

```markdown
# Patterns Delta — append to meta/user-patterns.md

### [2026-04-12] New pattern: decision speed increasing
Source: ADVISOR
Observation: Last 3 decisions made after first round of clarification.
```
