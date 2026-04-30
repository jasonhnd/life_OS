---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# Session Index Specification

Session index is the data source for Cortex's hippocampus (cross-session retrieval). Two artifacts are produced, with a strict separation between writer (archiver) and compiler (retrospective).

## 1. Purpose

The session index exists so the hippocampus subagent can perform per-message cross-session retrieval without a vector database, SQLite, or any non-markdown runtime. Per `devdocs/architecture/cortex-integration.md` §3.1, retrieval is LLM-driven over a compiled plaintext index — fast to scan, cheap to regenerate, fully markdown-first.

Two artifacts carry the load:

- **`INDEX.md`** — one line per session, compiled by retrospective at Start Session. This is the fast-scan surface the hippocampus reads first.
- **`{session_id}.md`** — structured session summary with YAML frontmatter, written by archiver at session close. Loaded by the hippocampus only after `INDEX.md` has narrowed the candidate set.

This two-tier design matches the brain analogy: `INDEX.md` is the "session gist," and `{session_id}.md` is the "full episodic trace." The hippocampus scans gist first, then retrieves traces on demand.

## 2. File Locations

```
_meta/sessions/
├── INDEX.md                    # Compiled by retrospective (Mode 0, at Start Session)
└── {session_id}.md             # Written by archiver (Phase 1, at session close)
```

**session-id format**: `{platform}-{YYYYMMDD}-{HHMM}`

Examples:
- `claude-20260419-1238`
- `gemini-20260420-0915`
- `codex-20260420-1403`

**HARD RULE (inherited from v1.4.4b)**: archiver MUST run the `date` command to obtain the actual timestamp. Fabricating the timestamp is a process violation. The archiver already enforces this in Phase 1 Step 2 — the session index reuses that session-id as the filename.

## 3. Session Summary Schema (`{session_id}.md`)

The archiver writes exactly one file per session. The file is immutable after write.

### YAML Frontmatter (complete schema)

```yaml
---
session_id: string                      # required, format {platform}-{YYYYMMDD}-{HHMM}
date: ISO 8601 date                     # YYYY-MM-DD
started_at: ISO 8601 timestamp          # with timezone
ended_at: ISO 8601 timestamp            # with timezone
duration_minutes: integer
platform: claude | gemini | codex
theme: en-roman | en-us-gov | en-corporate | zh-classical | zh-cn-gov | zh-corporate | ja-meiji | ja-kasumigaseki | ja-corporate
project: string                         # bound project scope; session binding HARD RULE enforces this
workflow: full_deliberation | express_analysis | direct_handle | strategist | review
subject: string                         # extracted during intent clarification, max 200 chars
domains_activated:                      # which of the six domains ran
  - PEOPLE
  - FINANCE
  - GROWTH
  - EXECUTION
  - GOVERNANCE
  - INFRA
overall_score: float                    # 0-10, from Summary Report
domain_scores:
  FINANCE: float
  GOVERNANCE: float
  # ...only include domains that ran
veto_count: integer                     # REVIEWER veto events (0 if approved first pass)
council_triggered: boolean              # COUNCIL debate fired?
soul_dimensions_touched:                # dimensions referenced by REVIEWER or updated by ADVISOR
  - string
wiki_written:                           # wiki entry IDs auto-written this session
  - entry_id
methods_used:                           # method IDs applied from method library
  - method_id
methods_discovered:                     # new methods added by archiver
  - method_id
concepts_activated:                     # concept IDs referenced during session
  - concept_id
concepts_discovered:                    # new concepts written by archiver Phase 2
  - concept_id
dream_triggers:                         # trigger names fired in Phase 3 REM
  - trigger_name
keywords:                               # max 10, for hippocampus Wave 1 scan
  - string
action_items:
  - text: string
    deadline: ISO 8601 date
    status: pending | completed | dropped
compliance_violations: integer          # AUDITOR-flagged violations, 0 if clean
---
```

### Body

Body is short, structured, and human-readable. No raw message content.

```markdown
## Subject

{One-paragraph expanded subject. This is the "what was this session about" answer.
Must stand alone — a reader who sees only this paragraph should understand the session's
scope. Max 500 chars.}

## Key Decisions

1. {Decision one — one sentence, action-oriented}
2. {Decision two}
3. {Decision three}

## Outcome

{One-paragraph summary of what was decided or achieved. Include the overall rating
from the Summary Report. Max 400 chars.}

## Notable Signals

- {Anything the narrator layer marked as important for future reference}
- {Cross-session patterns the archiver surfaced}
- {Unresolved tensions worth revisiting}
```

**Body rules**:
- No raw message quotes
- No PII (names, amounts, account numbers) — follow archiver's Phase 2 privacy filter
- No thinking-process dumps from any agent

## 4. INDEX.md Format

One line per session, most recent first, grouped by month. This is the scan surface for the hippocampus.

### Line format

```
{date} | {project} | {subject-truncated-80chars} | {overall_score}/10 | [{keywords-top3}] | {session_id}
```

### Example

```markdown
# Session Index

## 2026-04

2026-04-19 | passpay | Technical whitepaper v0.5 to v0.6 refinement | 8.2/10 | [whitepaper, refinement, evidence] | claude-20260419-1238
2026-04-17 | life-os | v1.6.2 SOUL auto-write and DREAM 10 triggers design | 9.1/10 | [architecture, soul, dream] | claude-20260417-0902
2026-04-15 | passpay | Go-to-market positioning for Q3 launch | 7.8/10 | [gtm, positioning, launch] | claude-20260415-1510

## 2026-03

2026-03-28 | ledger-io | Schema migration risk review | 8.0/10 | [schema, migration, risk] | claude-20260328-1143
2026-03-22 | life-os | Theme system expansion to 9 themes | 8.6/10 | [theme, i18n, design] | claude-20260322-0834
```

### Formatting rules

- Month heading `## YYYY-MM` — enables jump-navigation and future sharding
- Sessions within a month sorted by `date desc` (most recent on top)
- Truncate `subject` to 80 chars, append ellipsis if truncated
- Keywords shown as comma-separated list inside brackets, max 3 (full keyword set lives in the session summary)
- No trailing whitespace; one blank line between month sections

## 5. Write Flow

### Session summary creation (archiver Phase 1 generates session-id; Phase 2 writes the file)

The archiver owns both ends of the write. session-id generation stays in **Phase 1** (needs a real `date` call at session close). The **file write moves to the end of Phase 2** because the summary's YAML frontmatter references Phase 2 outputs (`wiki_written`, `methods_used`, `methods_discovered`, `concepts_activated`, `concepts_discovered`) that do not yet exist when Phase 1 runs. See `references/cortex-spec.md` Step 10 for the Phase 2 step list.

```
Phase 1:
1. Session ends → orchestrator launches archiver subagent
2. archiver Phase 1 generates session-id via the real `date` command
3. archiver stages metadata it can already gather:
   - Timestamps (started_at / ended_at / duration_minutes)
   - Workflow type from the orchestrator's trace
   - Domain scores and overall_score from the Summary Report
   - veto_count and council_triggered from the AUDITOR trace
   - SOUL dimensions touched from the ADVISOR report
   - DREAM triggers fired (from Phase 3 triggered_actions YAML block — Phase 3 runs before Phase 2)

Phase 2 (after wiki/SOUL auto-write, concept extraction + Hebbian update,
method-candidate detection, SYNAPSES-INDEX regeneration, SOUL snapshot dump):
4. archiver populates Phase 2 outputs into staged metadata:
   - wiki_written entries (from wiki auto-write)
   - methods_used, methods_discovered (from method-candidate detection)
   - concepts_activated, concepts_discovered (from concept extraction)
5. archiver extracts keywords (§7) — max 10
6. archiver writes _meta/outbox/{session_id}/sessions/{session_id}.md
7. File is added to the outbox directory for atomic git commit alongside other session artifacts
```

**Immutability**: once archiver writes the file, it is never re-edited. If a correction is needed (rare), add a `corrections/{session_id}.md` note rather than mutating the original. This parallels the immutability of journal entries — append-only, never rewritten.

**Placement under outbox**: during the archiver's Phase 1, the new file initially lands at `_meta/outbox/{session_id}/sessions/{session_id}.md`. Outbox merge (retrospective Mode 0 Step 7) moves it to the canonical `_meta/sessions/{session_id}.md` location. This matches the existing outbox pattern for decisions, tasks, and journal entries.

**Failure modes**:

- `date` command unavailable (extremely rare) → archiver halts Phase 1 with a clear error; session cannot be safely archived without a real timestamp
- Outbox directory write fails (disk full, permission) → archiver logs to `_meta/sync-log.md`, session summary file is not created, subsequent retrospective compile step simply omits the session from INDEX
- Partial frontmatter (e.g., Summary Report missing) → archiver fills required fields with sentinels (`overall_score: null`, empty arrays) and proceeds; retrospective's parser treats null scores as `n/a` in INDEX

### INDEX compilation (retrospective Mode 0)

The retrospective compiles — never writes per-session files. Extends the existing Mode 0 flow (see `pro/agents/retrospective.md`):

```
1. Start Session triggered
2. retrospective enumerates _meta/sessions/*.md (glob pattern: *.md excluding INDEX.md)
3. For each file, parse YAML frontmatter — extract:
   - date
   - project
   - subject (truncate to 80 chars)
   - overall_score (render as n/a if null)
   - keywords (take first 3)
   - session_id
4. Sort by date desc (secondary sort: started_at desc for same-day ties)
5. Group by YYYY-MM derived from the date field
6. Overwrite _meta/sessions/INDEX.md with the compiled output
7. If compilation produced a structurally different output, note the diff size in
   retrospective's Start Session report ("📚 Session Index: N sessions indexed")
```

**Compilation is idempotent**. Running it twice produces byte-identical output (given the same input files). This matters because retrospective runs every Start Session — no incremental logic needed. Idempotence also simplifies debugging: if the index looks wrong, deleting it and recompiling cannot lose data.

**Parse failures**: if a `{session_id}.md` file has malformed YAML, retrospective logs the filename to `_meta/sync-log.md` and continues. The corrupt session is omitted from INDEX but the file itself is preserved for manual inspection. This matches v1.6.2's posture on snapshot corruption — degrade gracefully, never block the Start Session briefing.

## 6. Read Flow (Hippocampus)

The hippocampus subagent consumes the session index. Per `devdocs/architecture/cortex-integration.md` §3.1 and the three-wave activation model:

```
1. Hippocampus receives the user's current subject (from Step 0.5)
2. Hippocampus reads _meta/sessions/INDEX.md (one file, fast)
3. LLM judgment identifies top 5-7 semantically relevant sessions
   - Wave 1: direct keyword match against the keywords column
   - Wave 2: semantic proximity to subject (LLM judgment over the 80-char subject blurbs)
   - Wave 3: sub-threshold activation from strong-synapse neighbors (if concept graph available)
4. For each selected session, hippocampus reads the full {session_id}.md
5. Returns concept-level summary to the GWT arbitrator (not to ROUTER directly)
```

**Read budget per message**: one `INDEX.md` read (always) + at most 7 `{session_id}.md` reads (only for surviving candidates). With typical sizes, this costs <50KB of context per message and <3 seconds of LLM scan time at scale targets in §8.

**What this architecture deliberately does not use** (user decision #3 from the cortex brainstorm):

- **No embeddings** — semantic similarity is LLM-judged, not vector-computed. This avoids embedding-model drift, embedding-provider lock-in, and the need to re-embed on every schema change.
- **No FTS5 or any database** — markdown-first HARD RULE (see `docs/architecture/markdown-first.md`). All retrieval substrate is plaintext and git-versioned.
- **No background indexing daemon** — index compiles at Start Session only; reads are per-message but limited to markdown I/O. No cron, no watchdog, no long-running process.

The performance math (see §8) confirms this scales well into the thousands of sessions before sharding is needed.

**Failure fallback**: if the hippocampus cannot read `INDEX.md` (file missing, corrupted, empty), it returns an empty signal to the GWT arbitrator with `confidence: 0` and the workflow degrades to v1.6.2a behavior — ROUTER sees raw user message without cross-session annotation. This matches the Cortex degradation policy in `devdocs/architecture/cortex-integration.md` §5 Phase 1 kill-switch design.

## 7. Keyword Extraction Rules

Keywords are the hippocampus's Wave 1 filter. The archiver Phase 1 selects up to 10 keywords using this procedure:

1. **Project name** — always included (1 slot)
2. **Domain names** — include each entry from `domains_activated` (up to 6 slots)
3. **Subject content words** — LLM extracts top 3 content words from the subject string; exclude stopwords, verbs, and generic nouns (up to 3 slots)
4. **Novel concepts** — include up to 3 entries from `concepts_discovered` (up to 3 slots)
5. **Total cap** — 10 keywords maximum. If steps 1-4 yield more than 10, drop in this order: novel concepts (oldest first), subject words (lowest-salience first), domain names (lowest-score first). Project name is never dropped.

**Output shape**: lowercase strings, no spaces inside a keyword (use hyphens), alphabetical order within each category. Example: `[passpay, finance, governance, whitepaper, refinement, evidence, zk-proof]`.

## 8. Scale Limits

Performance is load-bearing for this design — the hippocampus runs on every user message. The scale budget matches `docs/architecture/markdown-first.md` §2:

| Session count | INDEX.md size  | LLM scan time | Decision                                       |
|---------------|----------------|---------------|------------------------------------------------|
| 500           | ~500 lines, 30KB  | <3 seconds    | Fast scan, no optimization needed           |
| 2000          | ~2000 lines, 120KB | ~10 seconds   | Still manageable, monitor tail latency     |
| 5000+         | ~5000+ lines, 300KB+ | >10 seconds   | Shard INDEX by year; trigger database discussion |

**Sharding trigger**: when `INDEX.md` approaches 300KB, introduce `INDEX-{YYYY}.md` files (one per year) plus a `INDEX.md` manifest that links to them. The hippocampus then reads the current year first, and earlier years only if Wave 1 fails.

**Database escalation trigger**: if sharding does not restore scan latency below 10 seconds at extreme scale (hundreds of sessions per year, Wave 1 hit rate dropping), surface to the user for an explicit decision. v1.7 does NOT auto-introduce a database; the markdown-first rule holds unless the user explicitly chooses otherwise.

## 9. Migration from v1.6.2a

No `_meta/sessions/` directory exists before v1.7. Migration is best-effort and one-shot, per user decision #7 from the cortex brainstorm:

`tools/migrate.py` scans the last 3 months of `_meta/journal/`:

```
1. Enumerate _meta/journal/*.md created in the last 90 days
2. For each journal entry:
   a. Parse metadata (date, project, decision titles)
   b. Synthesize YAML frontmatter — best-effort, acknowledging gaps:
      - overall_score: extract from Summary Report heading if present, else null
      - domain_scores: extract from Summary Report table if present, else empty
      - veto_count, council_triggered: parse trace section, default 0/false
      - soul_dimensions_touched, wiki_written, methods_used: leave empty
        (pre-v1.7 sessions did not produce these)
      - concepts_activated, concepts_discovered: leave empty (v1.7 only)
      - dream_triggers: extract from -dream.md journals if timestamp-matched
      - keywords: LLM extraction from decision titles + project
   c. Synthesize body sections from decision summaries and outcome lines
   d. Write _meta/sessions/{synthesized-session-id}.md
3. After all files written, recompile _meta/sessions/INDEX.md
```

**session-id for migrated entries**: `{platform}-{YYYYMMDD}-{HHMM}` using the journal's modification timestamp. If the original platform cannot be inferred, default to `claude`.

**Sessions older than 3 months are not backfilled**. User decision #7 weighed this as diminishing retrieval value — by the time a session is 3+ months old, its value as a retrieval target is marginal, and the synthesis quality would be low (pre-v1.7 journals lack the structured fields the schema expects).

Migration is idempotent: running it twice overwrites any previously migrated files with the same session-id, so reruns are safe.

## 10. Anti-patterns

Do not:

- **Edit existing session summary files** — immutable after archiver writes. Corrections live in `corrections/{session_id}.md`. Mutating a session summary invalidates any downstream analysis (trend reports, DREAM-era pattern detection) that reads from the original.
- **Skip keyword extraction** — a session with zero keywords is invisible to the hippocampus Wave 1 scan. The Phase 1 archiver must always produce at least one keyword (the project name fallback).
- **Compile INDEX during archiver** — compilation is retrospective's job. Splitting the responsibility produces race conditions when two platforms close sessions concurrently, and couples adjourn latency to compile cost.
- **Include raw message content in the session summary** — only structured extractions (subject, key decisions, outcome, signals). Raw messages belong in `_meta/journal/`, not here. A retrieval-focused summary should be shorter than a journal entry, not a copy of it.
- **Sync `_meta/sessions/` to Notion** — per user decision #12, Cortex data stays local. Notion holds the user's mobile-friendly views (STATUS, Todo, Working Memory, Inbox); it does not hold the cognition substrate.
- **Let archiver retry session-id generation** — the `date` HARD RULE means one `date` call per session. Retries risk drift between the filename and the `started_at` timestamp.
- **Compile INDEX incrementally** — always overwrite. Idempotence is a design property; do not trade it for a small performance win.
- **Rely on file modification time for sorting** — sort by the `date` frontmatter field. File mtimes can drift after git operations or cross-device sync.
- **Embed arbitrary metadata not in the §3 schema** — if a new signal is worth tracking, update this spec and the archiver together. Free-form frontmatter extensions break retrospective's parser and create silent drift between agents.
- **Treat `{session_id}.md` as a replacement for the journal** — journal entries record detailed per-role reports (AUDITOR, ADVISOR, dream); session summaries are retrieval bait. Both coexist.
- **Use a different session-id format per platform** — the scheme `{platform}-{YYYYMMDD}-{HHMM}` is fixed across claude / gemini / codex. Platform-specific prefixes are encoded in the first segment, not in the format itself.

## 11. Cross-Platform and Concurrency

Life OS runs on Claude, Gemini, and Codex — and on multiple devices per user. The session index must behave sensibly when two platforms close sessions at nearly the same time.

### Collision avoidance

The `{platform}-{YYYYMMDD}-{HHMM}` session-id has minute resolution. Two sessions on the same platform closing within the same minute would collide. In practice this is very rare (one user, one active session at a time on a given platform), but the rule is:

- Archiver must not overwrite an existing file. Before `Write`, it checks for filename collision.
- On collision, archiver appends a second-precision suffix: `{platform}-{YYYYMMDD}-{HHMMSS}`.
- The collision case is logged to `_meta/sync-log.md` for later review.

### Outbox merge concurrency

Two devices may both be archiving when the next Start Session begins. Retrospective Mode 0 Step 7 already handles this with `_meta/.merge-lock`. The session index just rides along:

- Each outbox directory carries its own `sessions/{session_id}.md`.
- Merge moves them one at a time into `_meta/sessions/`.
- If both outboxes somehow produced the same session-id, the merge preserves both by appending the seconds suffix retroactively, then logs the conflict.

### Cross-device git conflicts

Since every session summary is its own file, concurrent writes from two devices produce independent files — git merges them without conflict. This is the same design principle that makes journal entries safe to co-author.

Two edge cases:

- **`INDEX.md` merge conflicts** — always resolve by regenerating. Retrospective Mode 0 treats `INDEX.md` as a compiled artifact; never hand-edit, never attempt a 3-way merge. On conflict detection, delete the file and let the next Start Session recompile.
- **Clock skew between devices** — if two devices have their clocks out of sync, session-ids may appear out of order in INDEX. The sort in Step 4 of §5 uses the `date` field (and `started_at` as tiebreaker), so small skew is absorbed. Large skew (>1 hour) is a device configuration issue outside this spec's scope.

## 12. Worked Example

A user holds a 90-minute deliberation on the `passpay` project about whitepaper refinement. The archiver produces:

Filename: `_meta/outbox/claude-20260419-1238/sessions/claude-20260419-1238.md`

```yaml
---
session_id: claude-20260419-1238
date: 2026-04-19
started_at: 2026-04-19T12:38:04+09:00
ended_at: 2026-04-19T14:09:17+09:00
duration_minutes: 91
platform: claude
theme: zh-classical
project: passpay
workflow: full_deliberation
subject: Technical whitepaper v0.5 to v0.6 refinement — evidence chain tightening
domains_activated: [FINANCE, GROWTH, GOVERNANCE]
overall_score: 8.2
domain_scores:
  FINANCE: 7.8
  GROWTH: 8.4
  GOVERNANCE: 8.4
veto_count: 1
council_triggered: false
soul_dimensions_touched: [evidence-discipline, quality-over-speed]
wiki_written: [finance/zk-proof-verification-cost]
methods_used: [evidence-laddering-v2]
methods_discovered: []
concepts_activated: [zk-proof, whitepaper, evidence-chain]
concepts_discovered: [modular-evidence-scaffolding]
dream_triggers: []
keywords: [passpay, finance, governance, growth, whitepaper, refinement, evidence, zk-proof]
action_items:
  - text: Tighten Section 4.2 evidence chain with three concrete citations
    deadline: 2026-04-22
    status: pending
  - text: Replace Figure 3 with simpler proof-cost chart
    deadline: 2026-04-21
    status: pending
compliance_violations: 0
---
```

The retrospective compile step then produces the `INDEX.md` line:

```
2026-04-19 | passpay | Technical whitepaper v0.5 to v0.6 refinement — evidence chain | 8.2/10 | [passpay, finance, governance] | claude-20260419-1238
```

Next morning, the user asks a question about whitepaper evidence rigor. The hippocampus reads INDEX, identifies this session via Wave 1 keyword match on `whitepaper` + `evidence`, and loads the full summary to inform the GWT arbitrator.

## 13. Operational Playbook

Quick reference for common operations:

| Situation | Action |
|-----------|--------|
| New session closed normally | archiver Phase 1 writes `{session_id}.md`; retrospective recompiles INDEX next Start Session |
| User edits a session summary (forbidden) | AUDITOR flags mutation; user reverts via git; system behavior undefined until reverted |
| User deletes a session summary | File removed from git; next Start Session compile drops the line from INDEX; the session is no longer retrievable |
| Migration from v1.6.2a | Run `tools/migrate.py` once; verify spot-checks against journals; commit result in a single "v1.7 session index backfill" commit |
| Clock bug produced wrong timestamps | Do not edit; note in `corrections/{session_id}.md`; optionally add a manual correction entry pointing to the corrected time |
| INDEX.md became corrupt | Delete the file; next Start Session recompiles from source-of-truth `{session_id}.md` files |
| Disk pressure approaches | See §8 sharding trigger; do not delete old session summaries without explicit user decision |

## 14. Related Specs

- `references/soul-spec.md` — SOUL dimension lifecycle, snapshot mechanism (parallel pattern: per-session file + INDEX compilation)
- `references/concept-spec.md` — concept storage under `_meta/concepts/`, which the hippocampus consults alongside the session index
- `references/hippocampus-spec.md` — the consumer of this artifact; defines three-wave activation
- `references/gwt-spec.md` — the GWT arbitrator that receives hippocampus output
- `devdocs/architecture/cortex-integration.md` §3.1 — architectural context and scan-cost estimates
- `docs/architecture/markdown-first.md` §2 and §4 — performance baseline and file-layout rules
- `pro/agents/archiver.md` — writer of `{session_id}.md`, Phase 1 scope
- `pro/agents/retrospective.md` — compiler of `INDEX.md`, Mode 0 Start Session responsibility
