# User-invoked prompt · inbox-process (v1.8.1)

> Walks `_meta/inbox/to-process/` and triages each item into wiki / archive
> / reject / defer with user confirmation. ROUTER reads this when the user
> wants to process inbox drops.

## Trigger keywords

- `处理 inbox` / `扫 inbox` / `inbox 走一遍`
- `process inbox` / `walk inbox` / `triage inbox`
- `/inbox-process` (slash command escape hatch)

## Pre-flight

1. Verify cwd is a second-brain repo (`_meta/` exists). If not: refuse and
   tell user "/inbox-process must run inside a second-brain vault, not the
   Life OS dev repo".
2. Verify `_meta/inbox/to-process/` exists. If missing: create it, write
   `_meta/inbox/README.md` (see template at end of this prompt), tell user
   "Inbox initialized. Drop `.md` files into `_meta/inbox/to-process/` and
   re-run /inbox-process when ready", and exit.
3. Read `wiki/SCHEMA.md` to confirm frontmatter contract for any wiki write
   later in this flow.
4. Read `_meta/inbox/manifest.json` if it exists (create empty
   `{"seen": [], "last_run": null}` if not). The manifest tracks which
   items were processed in prior runs so we know which are *new* this run.
5. List wiki domains (`ls wiki/` excluding `INDEX.md`, `SCHEMA.md`,
   `log.md`, `OBSIDIAN-SETUP.md`, `.templates/`). Cache this list — every
   `accept` proposal must place the new entry under one of these existing
   domains (or explicitly create a new one with user approval).

## Step 1 · Scan + delta

```bash
ls -1 _meta/inbox/to-process/*.md 2>/dev/null
```

For each file, capture:
- filename + size + mtime
- first 30 lines (read via Read tool with limit=30)
- existing frontmatter `defer_until:` (skip if defer date is in future)
- whether filename appears in `manifest.json#/seen` (mark as **delta=new**
  vs **delta=carried-over**)

If zero files: tell user "Inbox empty — nothing to process" and exit
clean. Do NOT invent items.

## Step 2 · LLM-based dedup pre-pass

Before triage, detect candidate duplicates against existing wiki entries.
**No SHA256, no FTS5, no vector math** — pure LLM judgment using grep +
Read.

For each inbox item:

1. Extract a 3-5 word topic phrase from the first H1 + first paragraph.
2. `Grep` `wiki/<candidate-domain>/**/*.md` for keywords from that phrase
   (use `output_mode: files_with_matches`, `head_limit: 8`).
3. For each matched candidate file, `Read` its frontmatter + TL;DR (first
   30 lines) and judge along two dimensions:
   - **Topic overlap** — same subject? (yes / partial / no)
   - **Claim overlap** — same conclusions / facts? (yes / partial / no)
4. Decision:
   - both **yes** → propose `update` against that wiki entry
   - **partial** on either → propose `accept` but with a "Related" link to
     the candidate (and flag for user review in the proposal table)
   - both **no** → propose `accept` (truly new)
5. If the inbox item appears to overlap >= 70% with another *unprocessed*
   inbox item (same batch), propose `merge` — accept one entry, archive
   the other, note both sources in `sources:` array.

This step does NOT use cryptographic hashing. Two articles with identical
SHA256 are obviously duplicate; two articles paraphrasing the same
research differ at every byte but mean the same thing — only LLM judgment
catches the second. The grep narrows the search space; the LLM judges
overlap.

## Step 3 · Triage (per item, after dedup)

For each item, judge along three axes:

**A. Domain fit**
- Which `wiki/<domain>/` does the topic belong to? Use the cached domain
  list. If the topic spans multiple domains, pick the dominant one.
- If no existing domain fits, candidate disposition is `archive` or
  `reject` (do NOT invent new domains without explicit user approval).

**B. Persistence value**
- Does this content carry value for a future decision/lookup?
  - YES + dedup said "truly new" = candidate `accept`
  - YES + dedup said "duplicate" = candidate `update`
  - NO but worth keeping the raw artifact = candidate `archive`
  - NO and no need to keep = candidate `reject`

**C. Confidence (5-bucket enum, v1.8.1+)**
- `certain`  — multi-source convergent, primary source verifiable, math/proof complete (rare for inbox drops)
- `likely`   — clearly cited, plausible, no known counter-evidence
- `possible` — single source plausible, or your own draft you've thought through (default for `/research` output)
- `unlikely` — speculation, anecdote, or source you're not sure about
- `impossible` — known-false claim being recorded for context only (use rarely)

The old `0.0–1.0` float was illusory precision (you can't actually
distinguish `0.65` from `0.70`). The 5-bucket enum forces honest
calibration. See `scripts/prompts/migrate-confidence.md` for batch
conversion of legacy floats.

## Step 4 · Propose to user

Output a single table:

```
📥 Inbox triage proposal — N items (Δ K new, J carried-over)

| # | filename | domain | disposition | confidence | dedup | summary |
|---|----------|--------|-------------|------------|-------|---------|
| 1 | 2026-05-01_stablecoin-b2b.md | fintech | accept | possible | new (no overlap) | 稳定币 B2B 跨境支付现状 |
| 2 | 2026-04-29_random-link.md | — | reject | — | — | 一次性 HN 链接，无持久价值 |
| 3 | 2026-04-28_methodology-update.md | methodology | update wiki/methodology/decision-frameworks.md | likely | dup of decision-frameworks (claim overlap) | 给 decision-frameworks 加 5W2H 分支 |
| 4 | 2026-04-27_pdf-notes.md | — | archive | — | partial overlap with wiki/finance/saas-models | 有参考价值但散乱，留 archive 备查 |
| 5 | 2026-04-15_half-baked-idea.md | — | defer | — | — | 想法未成熟，defer_until: 2026-05-15 |

Confirm? Type "all" to accept all, "1,3" to accept rows, "edit 1
disposition=archive" to override, "skip" to abort.
```

Wait for explicit user confirmation. **Do NOT execute on assumed
agreement.** If user says "looks good but 5 reject not defer" → re-emit
table with the override applied + ask again.

## Step 5 · Execute

For each confirmed row, in order:

### accept (new wiki entry)

1. Compute slug: lowercase, kebab-case, ≤ 50 chars, derived from filename
   topic (strip date prefix).
2. Build frontmatter per `wiki/SCHEMA.md` (v1.8.1 fields):
   ```yaml
   ---
   title: "<one-line title>"
   aliases: []                    # other names this entry might be linked as
   domain: <domain>
   created: <YYYY-MM-DD>          # today
   last_updated: <YYYY-MM-DD>     # same as created
   last_tended: <YYYY-MM-DD>      # same as created (you just tended it)
   review_by: <YYYY-MM-DD>        # today + 180d default
   confidence: <enum>             # impossible | unlikely | possible | likely | certain
   tags: [<domain>, inbox-ingested]
   status: candidate
   sources:                       # PLURAL — list every contributing source
     - _meta/inbox/archive/<original-filename>
   ---
   ```
3. Body: rewrite source content to wiki style (no first-person, no
   ephemeral framing, no "I read this today"). Preserve URLs, citations,
   numbers verbatim. Keep ≤ 800 words for first version.
4. **Provenance tagging in `## Key facts`**: every bullet should carry one
   marker:
   - `^[extracted]` — paraphrased verbatim from a source[]
   - `^[inferred]`  — your synthesis, not stated in any source
   - `^[ambiguous]` — sources disagree or evidence is mixed
   Untagged claims default to `^[extracted]`. Be honest — `^[inferred]`
   is not a demerit; it's information for future-you and downstream
   audits.
5. Write `wiki/<domain>/<slug>.md`.
6. Move `_meta/inbox/to-process/<original>.md` →
   `_meta/inbox/archive/<original>.md` via `mv` (Bash tool).
7. Append one line to `wiki/log.md`:
   ```
   - [HH:MM] created  | wiki/<domain>/<slug>.md | <one-line summary>
   ```
   (If `wiki/log.md` doesn't exist, create it with the H1 header from the
   `wiki/log.md` template — see end of this prompt.)
8. Update `wiki/INDEX.md` to add the new entry under its domain section.

### update (existing wiki entry)

1. Read the target `wiki/<domain>/<existing-slug>.md`.
2. Apply changes: add new sub-section, append a paragraph, refresh `key
   facts`, etc. Preserve existing frontmatter except:
   - bump `last_updated` to today
   - bump `last_tended` to today (active review)
   - extend `sources:` array with the inbox source path
   - re-evaluate `confidence` (raise enum bucket if new sources support;
     lower if you found counter-evidence).
3. Move source to `_meta/inbox/archive/`.
4. Append `wiki/log.md`:
   ```
   - [HH:MM] updated  | wiki/<domain>/<existing-slug>.md | <what changed>
   ```

### merge (consolidate two inbox items into one wiki entry)

1. Combine the two sources in body.
2. `sources:` array contains both inbox file paths.
3. Move BOTH inbox files to archive.
4. Append two log lines (one per source).

### archive

1. Move source `_meta/inbox/to-process/X.md` → `_meta/inbox/archive/X.md`.
2. Do NOT touch `wiki/log.md` (this isn't a wiki action).

### reject

1. Move source to `_meta/inbox/archive/X.md` (we don't delete; archive is
   the recycle bin).
2. Append `wiki/log.md`:
   ```
   - [HH:MM] rejected | _meta/inbox/<original> | <one-line reason>
   ```
   (Yes, `wiki/log.md` records rejections too — it's the single activity
   timeline; rejections explain why a candidate didn't make it.)

### defer

1. Edit the source's frontmatter to add/update `defer_until: YYYY-MM-DD`
   (default: 2 weeks from today; user can override). If file has no
   frontmatter, prepend a minimal `---\ndefer_until: ...\n---\n` block.
2. Source stays in `to-process/`. Future `/inbox-process` runs will
   auto-skip it until defer date passes.
3. Do NOT touch `wiki/log.md` (deferred items aren't acted on yet).

## Step 6 · Update manifest

After all rows processed, rewrite `_meta/inbox/manifest.json`:

```json
{
  "seen": [
    "2026-05-01_stablecoin-b2b.md",
    "2026-04-29_random-link.md",
    "2026-04-28_methodology-update.md",
    "2026-04-27_pdf-notes.md",
    "2026-04-15_half-baked-idea.md"
  ],
  "last_run": "2026-05-02T14:23:00+09:00",
  "counts_by_run": {
    "2026-05-02T14:23:00+09:00": {
      "accepted": 1,
      "updated": 1,
      "merged": 0,
      "archived": 1,
      "rejected": 1,
      "deferred": 1
    }
  }
}
```

The manifest is what makes Δ-tracking possible across runs. Every item
processed at least once gets added to `seen`. Re-runs use this to mark
new items in the proposal table.

## Step 7 · Report

Output to user:

```
✅ /inbox-process complete

Counts (this run):
  accepted:  N (new wiki entries written)
  updated:   M (existing wiki entries amended)
  merged:    Q (multi-source wiki entries written)
  archived:  K (kept as raw, no wiki entry)
  rejected:  L (moved to archive with log entry)
  deferred:  P (left in to-process/ until <next defer date>)

Wiki log (last 10 lines):
  <tail of wiki/log.md>

Inbox state:
  to-process/: X items remaining (Y deferred, Z fresh)
  archive/:    W items total
  manifest:    Δ K new since last run · last_run = <ISO8601>
```

## Failure modes

- **wiki/log.md write fails** (permissions, disk full): rollback the
  current item's wiki write + source move; report failure for that item;
  continue to next item.
- **wiki/<domain>/ doesn't exist for an accept**: ask user — create
  domain or change disposition? Do NOT silently create new domain
  directories.
- **slug collision** (file already exists): suffix with `-2` (then `-3`,
  etc.) and tell user.
- **source frontmatter unparseable** for a defer: skip defer attempt,
  ask user to inspect manually.
- **manifest.json malformed**: back it up to
  `_meta/inbox/manifest.json.broken-<timestamp>` and start fresh with
  `{"seen": [], "last_run": null}`. Tell user.

## Templates (write these only when missing)

### `_meta/inbox/manifest.json`

```json
{
  "seen": [],
  "last_run": null,
  "counts_by_run": {}
}
```

### `_meta/inbox/README.md`

```markdown
# Inbox · drop-zone for unprocessed material

Drop any `.md` file into `to-process/`. Next `/inbox-process` (or natural
language "处理 inbox") run will scan, triage, and propose dispositions
(wiki / archive / reject / defer).

## Filename convention

`YYYY-MM-DD_<short-slug>.md` — date helps with chronological scanning;
slug is just for human readability.

## Content can be anything

- Web article copy-paste
- PDF → markdown conversion output
- Voice memo transcription
- Email forward
- Random thought you want triaged later

The triage step is where structure gets imposed. Don't over-format on
the way in.

## What gets where

- `to-process/`   — fresh drops + items deferred to a future date
- `archive/`      — everything that's been triaged; never deleted
- `manifest.json` — system-managed, tracks which items have been seen
- `notifications.md` — system-written; don't put your own drops there

See `wiki/SCHEMA.md` for the wiki frontmatter contract that accepted
items must conform to. See `wiki/log.md` for the activity timeline.
```

### `wiki/log.md` (created on first wiki write if missing)

```markdown
# Wiki · activity log

Append-only timeline of all wiki/ writes. Newest day at the bottom.

Schema source: `wiki/SCHEMA.md` (Logging convention section).

Action enum: `created` | `updated` | `merged` | `promoted` | `deprecated`
| `renamed` | `rejected` | `bulk` (batch operations summary)

Format: `- [HH:MM] <action> | <wiki-path> | <summary>`

---
```

(Then append the `## YYYY-MM-DD` header for today + the first action line.)
