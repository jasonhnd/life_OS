---
spec_id: memory-tree-spec.v1-proposal
status: proposal
authoritative: false
implementation_target: v1.9 or v2.0 (TBD — pending real-data validation in Jason's second-brain)
description: PROPOSAL — Cascade seal architecture for lifeos sessions/wiki memory. Defines L0 (raw, ≤30 days) → L1 (weekly digest) → L2 (monthly digest) → L3 (yearly digest) folding with bucket-seal cascade. Pattern borrowed from tinyhumansai/openhuman Memory Tree (`gitbooks/features/obsidian-wiki/memory-tree.md`). NOT implemented in v1.8.7 — spec frozen as v2.0 architectural anchor; archiver behavior unchanged from v1.8.6.
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/obsidian-wiki/memory-tree.md (three trees / L0→L1 cascade seal / hotness-driven topic materialization)
introduced_in: v1.8.7 (spec only)
referenced_by:
  - references/wiki-spec.md (v2.0 direction reference)
  - references/session-index-spec.md (v2.0 direction reference)
  - meta/rfc/v1.8.7-openhuman-borrowed-patterns.md §2.6 A1
---

# Memory Tree Specification (PROPOSAL · v1.9 / v2.0 target)

> **Status: PROPOSAL only**. v1.8.7 ships this spec as a future direction anchor. `archiver` behavior is UNCHANGED from v1.8.6. No L0/L1/L2/L3 directory layout exists in user runtime. No cascade seal logic runs. This spec is frozen so future implementation has a clear target — verification of these data structures and thresholds requires running them in Jason's real second-brain across multiple weeks/months, which v1.8.7 dev cycle does not include.

## Why a cascade seal architecture (motivation)

Current lifeos sessions/wiki structure (as of v1.8.6):

- `meta/sessions/<sid>.md` — flat directory, all sessions accumulate forever
- `meta/wiki/<topic>/<entry>.md` — flat per-topic, no automatic compression
- `meta/concepts/<concept>.md` — flat with hotness counts but no derived summary files

Problem after years of accumulation:

- `archiver` reading "last 30 days" is fine; reading "last 2 years" becomes expensive
- `hippocampus` spreading activation over thousands of sessions slows linearly
- User browsing `meta/sessions/` sees 1000+ files with no navigation
- Wiki entries that grew through 50 sessions don't have a compact "what does this concept mean now" summary

OpenHuman's Memory Tree solves this with L0 → L1 → L2 cascade summarization. Borrowing the pattern (not the implementation — OpenHuman uses SQLite, lifeos stays md-only per DR-10).

## Proposed layout

```
meta/sessions/
├── L0/                          # raw sessions, recent 30 days
│   ├── 2026-05-25-<sid>.md
│   └── ...
├── L1-weekly/                   # weekly digests, recent 12 weeks (~3 months)
│   ├── 2026-W21.md              # week 21 of 2026 — digest of L0 sessions in that week
│   └── ...
├── L2-monthly/                  # monthly digests, recent 12 months
│   ├── 2026-05.md
│   └── ...
└── L3-yearly/                   # yearly digests, all years
    ├── 2026.md
    └── ...
```

Same pattern for `meta/wiki/` (sealed wiki entries) and `meta/concepts/` (canonical concept rollups).

## L0 → L1 cascade seal algorithm

```
Each archiver Adjourn (in v1.9 / v2.0):

1. Check L0 buffer state:
   - count files in meta/sessions/L0/
   - check oldest file timestamp

2. Trigger conditions for "seal L0 → L1":
   - Buffer count ≥ 30 sessions, OR
   - Oldest L0 session is > 30 days old

3. If seal triggered:
   a. Determine the week being sealed (oldest week with >0 sessions in L0)
   b. Read all L0 session files for that week
   c. Call chat model with sealing prompt → produce week digest
   d. Write to meta/sessions/L1-weekly/<YYYY>-W<NN>.md
   e. Move sealed L0 files to meta/sessions/_archive/L0-pre-seal/
   f. (do NOT delete; preserve for audit)

4. Cascade to L2 if L1 buffer reaches threshold:
   - L1 buffer count ≥ 12 weekly digests (~3 months), seal oldest month to L2
   - Same procedure: read L1 weeklies of the month → generate L2 monthly → move sealed L1 to archive

5. Cascade to L3 yearly when L2 reaches 12 monthly digests
```

## Buffer thresholds (rationale)

| Layer | Threshold to seal next layer | Rationale |
|-------|------------------------------|-----------|
| L0 → L1 | 30 sessions OR 30 days oldest | Matches "last month" cognitive horizon; archiver reads L0 freely |
| L1 → L2 | 12 weekly digests (~3 months) | Quarter is natural review unit |
| L2 → L3 | 12 monthly digests | Year is the largest practical cognitive unit |
| L3 → (none) | Never seals further | Yearly is the top — no L4 unless lifeos becomes generational |

Buffer counts can be adjusted at implementation time; what matters is the cascade structure.

## Flush_stale (force-seal partial buffer)

If a buffer has been sitting for too long without reaching threshold (e.g. user took a sabbatical for 6 months, only has 5 sessions in L0), force-seal anyway:

- L0 → L1 force-seal: any L0 file older than 60 days (2x normal threshold)
- L1 → L2 force-seal: any L1 weekly older than 180 days
- L2 → L3 force-seal: any L2 monthly older than 24 months

This prevents stale-buffer pathology where a partial week sits in L0 indefinitely.

## Sealing prompt (LLM-driven)

Each seal level uses a level-specific prompt:

- **L0 → L1 (week digest)**: "Summarize this week's sessions. Extract: decisions made, recurring themes, unresolved questions, key concepts activated. Target length: 800-1500 tokens."
- **L1 → L2 (month digest)**: "Compose monthly review from these week digests. Identify: monthly themes, decisions that hardened/softened, concept activations that crossed canonical threshold, recurring people. Target: 1500-2500 tokens."
- **L2 → L3 (year digest)**: "Generate annual review from month digests. Identify: year's central narratives, longest-running unresolved threads, SOUL evolution evidence, strategic-line changes. Target: 3000-5000 tokens."

Prompts live at `scripts/prompts/seal/L0-to-L1.md` / etc. (location TBD, not built in v1.8.7).

## What v1.8.7 does NOT do

To be explicit:

- ❌ No `meta/sessions/L0/` directory created (existing flat layout stays)
- ❌ No archiver cascade seal logic
- ❌ No seal prompt files
- ❌ No automatic L1/L2/L3 generation
- ❌ No migration script for existing sessions

What v1.8.7 DOES do:
- ✅ Freeze this spec as `status: proposal`
- ✅ Add references from `wiki-spec.md` + `session-index-spec.md` pointing to this spec as v2.0 direction
- ✅ Stay buildable target for future implementation

## Open questions (resolve in implementation RFC)

The following are deliberately NOT resolved in this proposal — they require validation on real data:

1. Should L3 yearly cascade further (decadal? lifelong)? Likely no, but check after 3 years of accumulation
2. How to handle `meta/snapshots/soul/` SOUL snapshots in cascade — separate cadence or integrated?
3. Are L1 weekly digests written to vault (Obsidian-visible) or stay in `meta/sessions/` (dev-internal)?
4. When a sealed L1/L2 file conflicts with a fresh-context session (user references "that week in May" but the L1 has paraphrased what really happened), how is provenance recovered? Path to L0 archive must remain accessible
5. Cost calibration: ~$0.50-$2 per L1 weekly digest (1500 tokens at frontier model rates), ~$2-$10 per L2 monthly. Annual cost for active user: $300-$800/year of LLM bills just for sealing. Worth it?

These questions are why v1.8.7 stays at spec-only. Real-data trial answers them.

## Migration path (when v1.9/v2.0 implements)

When future version implements:

1. Add new directories without touching existing flat layout
2. Run a one-time backfill: `/seal-backfill` slash command that walks the existing flat `meta/sessions/` and produces L1/L2/L3 in append-only fashion
3. After backfill, future archiver Adjourns run incremental seal
4. Existing files remain at `meta/sessions/<sid>.md` paths (not moved) for backward compatibility — only NEW sessions go directly to L0 buffer

This migration is non-destructive and reversible.

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.6 A1
- Pattern source: `tinyhumansai/openhuman` `gitbooks/features/obsidian-wiki/memory-tree.md` (three trees / L0→L1 cascade seal)
- Implementation note: OpenHuman uses SQLite `memory_tree/chunks.db` + tokio task pool. lifeos stays md-only per DR-10 (`SKILL.md` HARD RULE) — directory layout above is the lifeos substrate
- Companion: `references/concept-spec.md` §Hotness thresholds (cascade seal triggers + hotness materialization are sister concepts)
