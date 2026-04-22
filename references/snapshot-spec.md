# Snapshot Specification

SOUL snapshots are small, immutable metadata dumps captured at the end of every session. They enable the SOUL Health Report at the next Start Session to compute trend arrows (↗↘→) across sessions without maintaining a separate state machine. A snapshot is a frozen moment: what the system knew about the user's identity dimensions at time T.

## Positioning

| Artefact | What it records |
|----------|----------------|
| `SOUL.md` | Current authoritative identity state |
| `_meta/snapshots/soul/` | **Historical SOUL state for trend computation (this spec)** |
| `_meta/concepts/` | Synaptic network (`references/concept-spec.md`) |
| `wiki/` | Reusable world knowledge |

Snapshots are metadata-only — they never duplicate SOUL body content. They record the numeric shape of SOUL at a point in time so the retrospective can compare "then" with "now".

---

## Principles

1. **Immutable** — once written, snapshots are never edited. Corrections go to SOUL.md, not to historical snapshots.
2. **Metadata-only** — snapshots store dimension names, confidence, evidence counts, and tiers. They do not store SOUL body text.
3. **Created every session** — even for trivial sessions. Missing snapshots break trend computation.
4. **Small** — each snapshot is <5KB typical. Thousands of snapshots remain inexpensive.
5. **Archived aggressively** — active snapshots stay hot for 30 days, then move to `_archive/`, then get deleted after 90 days. Git history retains the full audit trail. **Snapshots do NOT sync to Notion** — per user decision #12 and `cortex-spec.md` §Anti-patterns, all Cortex/`_meta/` data (concepts, synapses, snapshots) stays local. Notion only receives session summaries and decision records.

---

## File Location

```
_meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md
```

The timestamp in the filename **must come from the actual `date` command** at capture time — no fabrication (decision from v1.4.4b). If the system clock is unavailable, the snapshot write is aborted and the failure is logged to `_meta/cortex/decay-log.md`.

### Reserved paths

- `_meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md` — active snapshots (within 30 days)
- `_meta/snapshots/soul/_archive/{YYYY-MM-DD-HHMM}.md` — archived snapshots (30-90 days)
- Snapshots older than 90 days are deleted from the filesystem; the audit trail persists in git history only (snapshots are local-only per user decision #12)

---

## YAML Frontmatter Schema

```yaml
---
snapshot_id: {YYYY-MM-DD-HHMM}      # matches filename, unique
captured_at: ISO 8601               # actual capture timestamp
session_id: string                  # the session that produced this snapshot
previous_snapshot: string | null    # prior filename, or null for the first ever
dimensions:
  - name: string                    # SOUL dimension name
    confidence: float               # 0-1, copied from SOUL.md at capture time
    evidence_count: integer         # supporting decisions
    challenges: integer             # contradicting decisions
    tier: enum                      # core | secondary | emerging | dormant
---

# SOUL Snapshot · {YYYY-MM-DD}

(Body is optional — the frontmatter is the authoritative content. A human-readable table may be included for debugging but is not required.)
```

### Field constraints

| Field | Constraint |
|-------|-----------|
| `snapshot_id` | Must match the filename stem exactly |
| `captured_at` | Must be a real ISO 8601 timestamp from the system clock |
| `session_id` | Must be a valid session ID in `_meta/sessions/` |
| `previous_snapshot` | Filename of the prior snapshot, or `null` for the first |
| `dimensions` | Only dimensions with `confidence > 0.2` are included (skip noise) |
| `dimensions[].tier` | Derived from confidence (see Tier Mapping below) |

### Tier Mapping

Tiers are derived at capture time, not stored separately in SOUL.md.

All confidence bands use half-open intervals `[a, b)` — the lower bound is inclusive and the upper bound is exclusive. Boundary values always belong to the **upper** tier (e.g., confidence exactly 0.3 is `secondary`, not `emerging`; confidence exactly 0.7 is `core`, not `secondary`). This matches `references/soul-spec.md` §Tiered Reference by Confidence and `references/gwt-spec.md` §5.4.

| Tier | Confidence range |
|------|------------------|
| `core` | `[0.7, 1.0]` |
| `secondary` | `[0.3, 0.7)` |
| `emerging` | `[0.2, 0.3)` |
| `dormant` | `[0.0, 0.2)` (excluded from snapshot) |

Snapshots deliberately omit `dormant` dimensions to keep files small. The absence of a dimension in a snapshot is meaningful — it's how the trend algorithm detects retirement or demotion.

---

## Creation

Snapshot creation is owned by `archiver` Phase 2, executed after concept extraction (so concepts reinforced during the session are already persisted). The sequence is:

```
archiver Phase 2
    ├── Step 1 — wiki / SOUL auto-write (existing)
    ├── Step 2 — concept extraction + Hebbian update (concept-spec.md)
    ├── Step 3 — SOUL snapshot dump (THIS SPEC)
    │   1. Run `date` to get actual capture timestamp
    │   2. Read current SOUL.md
    │   3. For each dimension with confidence > 0.2:
    │        - Determine tier from confidence
    │        - Copy name, confidence, evidence_count, challenges
    │   4. Find the latest existing snapshot → set `previous_snapshot`
    │   5. Write _meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md
    │   6. File becomes read-only after write (do not edit)
    └── Step 4 — housekeeping (see Archive Policy)
```

### Invariants

- Even a trivial session (no decisions made) still produces a snapshot. Missing snapshots break trend computation and are treated as a bug.
- A snapshot is never written twice for the same session. If `archiver` re-runs for a session that already has a snapshot, the write is skipped and logged.
- Snapshots are additive — writing a new snapshot never removes or edits the previous one.

---

## Trend Computation

At the next Start Session, `retrospective` reads the **two most recent snapshots** and computes per-dimension deltas. Trend arrows appear in the SOUL Health Report (see `soul-spec.md` Health Report Format).

### Delta rules

| Condition | Trend marker |
|-----------|--------------|
| `confidence_Δ > +0.05` | ↗ rising |
| `confidence_Δ < -0.05` | ↘ falling |
| `|confidence_Δ| ≤ 0.05` | → stable |
| Dimension in current but not previous snapshot | 🌱 new |
| Dimension in previous but not current snapshot | 💤 dormant |

### Special states

The retrospective also emits badges for tier transitions and conflict detection:

| Transition | Badge | Condition |
|------------|-------|-----------|
| Crossed upward through 0.7 | 🌟 promoted to core | previous tier < `core`, current tier = `core` |
| Crossed downward through 0.7 | ⚠️ demoted from core | previous tier = `core`, current tier < `core` |
| Conflict zone | ❗ evidence ≈ challenges | `|evidence_count − challenges| ≤ 1` **and** `evidence_count ≥ 3` |

Badges stack with trend markers — a dimension may simultaneously be ↗ and 🌟 (promoted while rising).

### Handling the first snapshot

When there is no previous snapshot (first Start Session after bootstrap, or the very first session of a brand-new second-brain), all dimensions render as 🌱 and no trend arrows are computed. The Health Report header notes "First snapshot — trends will appear next session."

---

## Archive Policy

`archiver` Phase 2 Step 4 performs housekeeping after snapshot creation:

1. For each file in `_meta/snapshots/soul/` whose `captured_at` is **older than 30 days**: move to `_meta/snapshots/soul/_archive/` (preserving filename)
2. For each file in `_meta/snapshots/soul/_archive/` whose `captured_at` is **older than 90 days**: delete from filesystem
3. Housekeeping is idempotent — running it twice produces the same result

Deletion is safe because:
- Git history preserves all deleted files indefinitely
- Trend computation only needs the two most recent snapshots; deep history is for audit, not for the active algorithm
- Snapshots are local-only (not synced to Notion); the full audit trail lives in git

---

## Size Constraints

- Each snapshot **< 5KB typical** — a SOUL with 20 active dimensions produces ~2KB of YAML
- 1000 snapshots (several years of daily sessions) ≈ **5MB total** — negligible for git and Notion
- Body content is optional; keeping it empty halves file size
- No images, no binary data, no embedded attachments — snapshots are pure YAML + optional markdown

If a snapshot exceeds 10KB, the archiver logs a warning — it usually means SOUL.md has grown to an unusual shape (>50 active dimensions), which itself deserves user attention.

---

## Migration

Pre-v1.7 there are no snapshots (v1.6.2 introduced the mechanism; v1.6.2a stabilised it). For second-brains that pre-date v1.6.2:

1. `tools/migrate.py` scans `_meta/journal/` for SOUL delta blocks (the `🔮 SOUL Delta` sections emitted by ADVISOR)
2. For each journal entry that contains a SOUL delta, synthesise a snapshot timestamped at the journal entry's date
3. Synthetic snapshots carry `provenance: synthetic` in their frontmatter so the retrospective can distinguish them from natural snapshots
4. Migration stops at the earliest journal entry within the last 3 months (user decision #7 — aligned with all other migration scopes). Deeper history is not reconstructed; the signal degrades too much.
5. Log the migration result to `_meta/cortex/bootstrap-status.md`

Migration is idempotent. Synthetic snapshots are treated identically to natural ones by the trend algorithm — the `provenance` field exists only for audit.

---

## Reader Responsibilities

`retrospective` is the sole reader of snapshots during Start Session. Its contract:

1. List files in `_meta/snapshots/soul/` sorted by `captured_at` descending
2. Take the top 2 files (current and previous)
3. If fewer than 2 snapshots exist, fall back to "first snapshot" behaviour (all dimensions render as 🌱)
4. Parse both YAML frontmatters
5. Compute deltas per the rules in §5
6. Emit the SOUL Health Report block (format defined in `soul-spec.md`)

The retrospective does not read archived snapshots during normal operation. `_archive/` is consulted only when the user explicitly asks for long-range trends (e.g. "show me the past year's core identity evolution").

---

## Anti-patterns

These are forbidden by spec:

1. **Editing a snapshot file after creation** — snapshots are immutable. Corrections go to SOUL.md, and the next snapshot will reflect them.
2. **Storing SOUL body content in snapshots** — only metadata. If a snapshot file grows beyond 10KB it's a bug.
3. **Skipping snapshot creation for "trivial" sessions** — every session creates a snapshot. The trend algorithm relies on continuous history; gaps are indistinguishable from dormancy.
4. **Fabricating timestamps** — the filename and `captured_at` must come from the real system clock at write time. No manual timestamps, no synthesized times except in migration (where `provenance: synthetic` is required).
5. **Hand-deleting active snapshots** — the archive policy owns retention. Manual deletion breaks the "two most recent" reader contract.
6. **Reading snapshots outside the retrospective** — other roles must go through the retrospective's Health Report output. Direct reads by other agents break the information-isolation model.

---

## Constraints

- **One snapshot per session** — never two, never zero
- **Immutable after creation** — treat as read-only
- **Metadata only** — no SOUL body content
- **Filename timestamp = actual capture time** — no fabrication
- **Only dimensions with confidence > 0.2 included** — skip noise
- **< 5KB typical, < 10KB hard warning threshold**
- **30 days hot, 30-90 days archived, > 90 days deleted** — archive policy is idempotent
- **`archiver` Phase 2 owns writes, `retrospective` Mode 0 owns reads** — no other role touches snapshot files
- **Local-only — no Notion sync** — snapshots are Cortex/`_meta/` data; audit trail lives in git

---

## Related Specs

- `references/soul-spec.md` — SOUL schema, dimension lifecycle, Health Report format consumer
- `references/session-index-spec.md` — `session_id` field references entries in `_meta/sessions/`
- `references/cortex-spec.md` — overall Cortex architecture; snapshot is one of the five core v1.7 artifacts
- `references/concept-spec.md` — sibling `_meta/` data layer; same markdown-first principles and local-only constraint
- `references/eval-history-spec.md` — AUDITOR's `soul_reference_quality` dimension consumes snapshot-derived trend signals
- `pro/agents/archiver.md` — Phase 2 Step 3 owns snapshot writes
- `pro/agents/retrospective.md` — Mode 0 owns snapshot reads for the Health Report
