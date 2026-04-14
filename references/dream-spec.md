# DREAM Specification

DREAM is the system's offline memory processing — inspired by human sleep cycles. It runs as **Phase 3 of the Court Diarist** (`pro/agents/qiju.md`) at the end of every session, scanning the last 3 days of activity to organize, consolidate, and discover.

> **Note**: DREAM is not a standalone agent. It was merged into the Court Diarist (起居郎) in v1.4.4. This spec defines the three stages; the Court Diarist integrates them into its closing flow.

## Trigger

```
User says "退朝" / "adjourn" / "終わり"
    ↓
Court Diarist (起居郎): Phase 1 Archive → Phase 2 Knowledge Extraction
    ↓
Court Diarist: Phase 3 DREAM (runs three stages below)
    ↓
Dream report written to _meta/journal/{date}-dream.md
    ↓
Court Diarist: Phase 4 Sync (git + Notion) → Session ends
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

The user will confirm, edit, or reject during the next Start Court.

---

## Wiki Candidate Format

When DREAM discovers a reusable conclusion worth recording in wiki/:

```
📚 Wiki Candidate:
- Domain: [domain name]
- Topic: [short identifier]
- Conclusion: [one sentence — the reusable takeaway]
- Evidence:
  - [date] [decision/behavior] — [description]
  - [date] [decision/behavior] — [description]
- Applicable when: [in what scenarios to recall this]
```

For existing wiki entries, propose updates:

```
📚 Wiki Update:
- Entry: wiki/[domain]/[file].md
- Change: evidence_count +1 (or challenges +1)
- New evidence: [date] [what happened]
```

The user will confirm, edit, or reject during the next Start Court.

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
---
```

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
- [concrete actions for user to review at next Start Court]
```

---

## Morning Briefing Integration

Next Start Court, the Morning Court Official reads the latest unread dream report and includes in the briefing:

```
💤 Last session the system had a dream:
- [1-3 line summary of key findings]
- [SOUL candidates for user confirmation, if any]
```

After presenting, mark the dream report as "presented" so it is not shown again.

---

## Constraints

- **3-day scope is hard** — do not scan older files, even if they seem relevant
- **Do not modify SOUL.md directly** — only propose candidates
- **Do not modify wiki/ directly** — only propose candidates and updates
- **Do not modify user-patterns.md directly** — only propose updates
- **Conciseness** — a dream report should be 20-50 lines, not 500
- **Honesty** — "no significant findings" is a valid dream. Do not fabricate insights.
- **No blocking** — if DREAM fails, the session still ends normally
