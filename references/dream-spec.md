# DREAM Specification

DREAM is the system's offline memory processing — inspired by human sleep cycles. It runs as **Phase 3 of the ARCHIVER** (`pro/agents/archiver.md`) at the end of every session, scanning the last 3 days of activity to organize, consolidate, and discover.

> **Note**: DREAM is not a standalone agent. It was merged into the ARCHIVER in v1.4.4. This spec defines the three stages; the ARCHIVER integrates them into its closing flow.

## Trigger

```
User says "退朝" / "adjourn" / "終わり"
    ↓
ARCHIVER: Phase 1 Archive → Phase 2 Knowledge Extraction
    ↓
ARCHIVER: Phase 3 DREAM (runs three stages below)
    ↓
Dream report written to _meta/journal/{date}-dream.md
    ↓
ARCHIVER: Phase 4 Sync (git + Notion) → Session ends
```

If DREAM fails or times out → log warning to `_meta/sync-log.md`, don't block session end.

---

## Scope

**Default: files modified in the last 3 days (72 hours).** If no files were modified in the last 3 days, automatically expand to "since the last dream report" (read the date from the most recent `_meta/journal/*-dream.md`). If no dream report exists, scan the last 7 days as a fallback.

Detection method:
- GitHub backend: `git log --since="3 days ago" --name-only --format=""` → if empty, `git log --since="{last_dream_date}" --name-only --format=""`
- GDrive backend: `modifiedTime > 3_days_ago` → if empty, `modifiedTime > last_dream_date`
- Notion backend: `last_edited_time > 3_days_ago` → if empty, `last_edited_time > last_dream_date`

---

## Three Stages

Inspired by human sleep architecture:

### Stage N1-N2: Organize & Archive

**Human equivalent**: Light sleep — the brain sorts the day's experiences into categories.

Scan recent 3 days for loose ends:
- `inbox/` items not yet classified → suggest target project/area/wiki
- `_meta/journal/` entries with extractable insights → suggest `user-patterns.md` update
- `projects/*/tasks/` with expired due dates or duplicates → flag for cleanup
- Orphan files (created but not linked from any index.md) → flag

For each finding, classify:
- **Auto-fixable** (e.g., missing index entry) → note in report
- **Needs user input** (e.g., classify this inbox item) → add to suggested actions

### Stage N3: Deep Consolidation

**Human equivalent**: Deep sleep — important memories move from short-term to long-term storage.

N3 asks two questions:
- **Q1 (about the person)**: Did this session reveal anything new about the user? → SOUL candidates
- **Q2 (about the world)**: Did this session produce any reusable conclusions for next time? → Wiki candidates

From the recent 3 days, extract deeper patterns:
- Reusable conclusions from decisions → propose wiki candidates (see Wiki Candidate format below)
  **Dedup**: Check the most recent outbox manifest — if `wiki: N` (N > 0), that session's adjourn flow already extracted wiki candidates. Focus only on conclusions the adjourn flow missed. Don't re-propose.
- Scan wiki/INDEX.md (if exists): new evidence supporting existing entries → propose evidence_count update; new evidence contradicting existing entries → propose challenges update
- `user-patterns.md` entries that need updating based on new evidence → propose changes
- **SOUL.md candidate entries** → propose new entries or updates to existing ones (see SOUL Candidate format below)

### Stage REM: Creative Connections

**Human equivalent**: REM sleep — the brain makes unexpected connections between unrelated memories. This is where dreams happen, and where insights emerge.

No checklist for this stage — let the data speak:
- **Cross-project associations**: Does something learned in Project A apply to Project B?
- **Behavior-value alignment**: If SOUL.md exists, are recent behaviors consistent with stated values?
- **Dimension blind spots**: What life dimensions were completely absent from recent decisions?
- **Unexpected insight**: What pattern or connection would surprise the user?

Quality over quantity. 1-3 genuine insights. If nothing non-obvious emerges, say so — do not fabricate.

---

## Auto-Triggered Actions (REM)

When REM discovers patterns, DREAM automatically performs these actions — no user confirmation. Each trigger has a **hard threshold** (quantitative rule) and **soft signals** (LLM qualitative cues). `mode: hard` means the threshold was met automatically; `mode: soft` means the LLM detected a qualitative signal beyond the threshold and the auto-action requires AUDITOR review.

All triggers are subject to **24h anti-spam suppression** — if the same trigger fired within the last 24 hours (per `_meta/journal/*-dream.md`), it is skipped.

#### 1. new-project-relationship

- **Data source**: `projects/*/index.md` strategic fields, `_meta/strategic-lines.md`
- **Hard threshold**: new cross-project dependency or bottleneck edge detected since last dream report
- **Soft signals**: recent decisions implicitly reference another project without a formal strategic link
- **Auto-action**: write STRATEGIC-MAP candidate + flag for next briefing prominent display
- **Anti-spam**: suppressed if fired within last 24h

#### 2. behavior-mismatch-driving-force

- **Data source**: last 3 days' decisions + SOUL.md driving_force dimension
- **Hard threshold**: ≥2 recent decisions contradict the stated driving_force
- **Soft signals**: user expresses discomfort or hesitation while executing a driving_force-aligned path
- **Auto-action**: inject into next ADVISOR briefing input
- **Anti-spam**: suppressed if fired within last 24h

#### 3. wiki-contradicted

- **Data source**: `wiki/**/*.md`, recent decisions, new evidence notes
- **Hard threshold**: ≥1 piece of new evidence directly contradicts an existing wiki conclusion
- **Soft signals**: user tone shifts from certainty to doubt on a topic covered in wiki
- **Auto-action**: increment `challenges: +1` on that wiki entry
- **Anti-spam**: suppressed if same entry was challenged within last 24h

#### 4. soul-dormant-30d

- **Data source**: SOUL.md `last_validated` timestamps
- **Hard threshold**: dimension with `last_validated` older than 30 days AND `confidence ≥ 0.5`
- **Soft signals**: (none — purely time-based)
- **Auto-action**: flag briefing warning ("⚠️ [dimension] not activated in 30+ days")
- **Anti-spam**: suppressed if fired within last 24h

#### 5. cross-project-cognition-unused

- **Data source**: `wiki/INDEX.md`, recent decisions across projects
- **Hard threshold**: ≥1 wiki entry directly applicable to recent decision was not referenced
- **Soft signals**: user is re-deriving a conclusion already established in another project's wiki
- **Auto-action**: flag for next DISPATCHER to force-inject relevant wiki entries
- **Anti-spam**: suppressed if same entry was flagged within last 24h

#### 6. decision-fatigue

- **Data source**: last 3 days' decision timestamps + REVIEWER scores
- **Hard threshold**: ≥5 decisions in 24h AND avg score of second half ≤ first half - 2
- **Soft signals**: user expresses fatigue in session ("whatever" / "fine" / "随便" / "まあいい")
- **Auto-action**: flag next briefing with "consider no major decisions today"
- **Anti-spam**: suppressed if fired within last 24h

#### 7. value-drift

- **Data source**: SOUL.md evidence/challenge history + last 30 days' decisions
- **Hard threshold**: dimension accumulates ≥3 challenges with ≤1 new supporting evidence in 30 days
- **Soft signals**: user's framing of a value shifts over time (e.g., "security" → "freedom")
- **Auto-action**: auto-propose SOUL dimension revision
- **Anti-spam**: suppressed if same dimension was revised within last 24h

#### 8. stale-commitment

- **Data source**: decisions where user said "I will X" + task completion state
- **Hard threshold**: commitment statement ≥30 days old AND no associated task completed / no follow-up decision
- **Soft signals**: user avoids mentioning the topic in subsequent sessions
- **Auto-action**: flag for next briefing to resurface ("You said you would X — what happened?")
- **Anti-spam**: suppressed if same commitment was resurfaced within last 24h

#### 9. emotional-decision

- **Data source**: decision session journals + user expression patterns
- **Hard threshold**: ≥2 recent decisions made during sessions flagged with strong emotional markers
- **Soft signals**: elevated punctuation, short replies, rapid subject changes during decision phase
- **Auto-action**: flag for next REVIEWER to add mandatory "emotional state check" dimension
- **Anti-spam**: suppressed if fired within last 24h

#### 10. repeated-decisions

- **Data source**: `_meta/decisions/*.md` + project decisions history
- **Hard threshold**: same question/subject decided ≥3 times without execution in between
- **Soft signals**: user rephrases the question to avoid recognizing it as repetition
- **Auto-action**: flag for next briefing ("You're deciding X again — are you avoiding commitment?")
- **Anti-spam**: suppressed if fired within last 24h

All flags are written to `_meta/journal/{date}-dream.md` with a structured `triggered_actions` YAML block. RETROSPECTIVE reads this at next Start Session and surfaces relevant flags in the briefing.

---

## SOUL Candidate Format

When DREAM discovers a value pattern worth recording in SOUL.md:

```
🌱 SOUL Candidate:
- Dimension: [name]
- Observation: [what you observed in the data]
- Evidence:
  - [date] [decision/behavior]
  - [date] [decision/behavior]
- Proposed entry:
  - What IS: [observed pattern]
  - What SHOULD BE: [to be confirmed by user]
  - Gap: [if apparent]
```

Passing candidates are auto-written to SOUL.md at confidence 0.3, with "What SHOULD BE" left empty for the user to fill in later. Users can edit freely or delete at any time, or say "undo recent SOUL" at the next session to roll back.

---

## Wiki Auto-Write (no user confirmation)

When DREAM discovers a reusable conclusion during N3, apply the 6 Auto-Write Criteria and Privacy Filter defined in `references/wiki-spec.md`:

1. Cross-project reusable
2. About the world, not about you
3. Zero personal privacy
4. Factual or methodological
5. Multiple evidence points (≥2 independent)
6. No contradiction with existing wiki

If ALL 6 pass → auto-write directly to `wiki/{domain}/{topic}.md`. No user confirmation in the main context.

**Internal candidate structure** used during evaluation:

```
📚 Wiki Auto-Write (internal):
- Domain: [domain name]
- Topic: [short identifier]
- Conclusion: [one sentence — the reusable takeaway]
- Evidence:
  - [date] [decision/behavior] — [description]
  - [date] [decision/behavior] — [description]
- Applicable when: [in what scenarios to recall this]
- Criteria check: [6/6 passed or X/6 → discarded with reason]
- Privacy filter: [what was stripped, or "nothing to strip"]
```

**Initial confidence**:
- 3+ independent evidence points → 0.5
- Exactly 2 evidence points → 0.3
- 1 evidence or below → DISCARD

For existing wiki entries, auto-update directly:

```
📚 Wiki Update (auto):
- Entry: wiki/[domain]/[file].md
- Change: evidence_count +1 (or challenges +1)
- New evidence: [date] [what happened]
```

Users nudge wiki post-hoc (delete file = retire; "undo recent wiki" = rollback). See `references/wiki-spec.md` for the full auto-write specification.

---

## Output Format

Written to `_meta/journal/{date}-dream.md`:

```yaml
---
type: journal
journal_type: dream
date: YYYY-MM-DD
scope_files: N
stages: [N1-N2, N3, REM]
soul_candidates: N
wiki_candidates: N
triggered_actions:
  - trigger_id: 6
    trigger_name: "decision-fatigue"
    mode: "hard"          # or "soft"
    detection:
      hard_signals:
        - "6 decisions in 18 hours"
        - "avg score 7.5 → 4.2"
      soft_signals: []
    action: "flag-next-briefing"
    surfaces_at: "next-start-session"
    auditor_review: false  # true if mode=soft
---
```

`mode` = **hard** means the threshold was met automatically; **soft** means the LLM detected a qualitative signal beyond the threshold and requires AUDITOR review before the auto-action surfaces in the next briefing.

```markdown
## 💤 Dream Report · YYYY-MM-DD

### N1-N2 · Organize & Archive
- [findings with recommended actions]

### N3 · Deep Consolidation
- [patterns extracted, wiki suggestions, pattern updates]

### REM · Creative Connections
- [cross-domain insights, value-behavior observations]

### 🌱 SOUL Candidates
- [proposed entries, if any — or "No new candidates"]

### 📚 Wiki Candidates
- [proposed entries or updates, if any — or "No new knowledge candidates"]

### 📋 Suggested Actions
- [concrete actions for user to review at next session start]
```

---

## Morning Briefing Integration

Next session start, the RETROSPECTIVE reads the latest unread dream report and includes in the briefing:

```
💤 Last session the system had a dream:
- [1-3 line summary of key findings]
- [Auto-written SOUL dimensions awaiting "What SHOULD BE" input, if any]
- [Auto-written Wiki entries with paths, if any; user can delete to retire]
```

After presenting, mark the dream report as "presented" so it is not shown again.

---

## Constraints

- **3-day scope is hard** — do not scan older files, even if they seem relevant
- **Do not modify SOUL.md directly** — only propose candidates (SOUL auto-write is scoped to archiver Phase 2, not DREAM)
- **Wiki auto-write under strict criteria** — write directly when all 6 Auto-Write Criteria pass (see wiki-spec.md); discard otherwise
- **Do not modify user-patterns.md directly** — only propose updates
- **Conciseness** — a dream report should be 20-50 lines, not 500
- **Honesty** — "no significant findings" is a valid dream. Do not fabricate insights.
- **No blocking** — if DREAM fails, the session still ends normally
