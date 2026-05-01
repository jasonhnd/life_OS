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
4. List wiki domains (`ls wiki/` excluding `INDEX.md`, `SCHEMA.md`,
   `log.md`, `OBSIDIAN-SETUP.md`, `.templates/`). Cache this list — every
   `accept` proposal must place the new entry under one of these existing
   domains (or explicitly create a new one with user approval).

## Step 1 · Scan

```bash
ls -1 _meta/inbox/to-process/*.md 2>/dev/null
```

For each file, capture:
- filename + size + mtime
- first 30 lines (read via Read tool with limit=30)
- existing frontmatter `defer_until:` (skip if defer date is in future)

If zero files: tell user "Inbox empty — nothing to process" and exit
clean. Do NOT invent items.

## Step 2 · Triage (per item)

For each item, judge along three axes:

**A. Domain fit**
- Which `wiki/<domain>/` does the topic belong to? Use the cached domain
  list. If the topic spans multiple domains, pick the dominant one.
- If no existing domain fits, candidate disposition is `archive` or
  `reject` (do NOT invent new domains without explicit user approval).

**B. Persistence value**
- Does this content carry value for a future decision/lookup?
  - YES + adds new ground = candidate `accept` (new wiki entry)
  - YES + duplicates an existing entry = candidate `update` (search
    `wiki/<domain>/` for similar slug; if a match within ~70% topic
    overlap exists, propose `update` instead of `accept`)
  - NO but worth keeping the raw artifact = candidate `archive`
  - NO and no need to keep = candidate `reject`

**C. Confidence**
- Source clearly cited and verifiable → confidence 0.7-0.85
- Single source, plausible → 0.55-0.65
- User's own draft / opinion → 0.4-0.55
- Multi-source convergent → 0.85+ (rare for inbox drops)

## Step 3 · Propose to user

Output a single table:

```
📥 Inbox triage proposal — N items

| # | filename | domain | disposition | confidence | summary |
|---|----------|--------|-------------|------------|---------|
| 1 | 2026-05-01_stablecoin-b2b.md | fintech | accept | 0.65 | 稳定币 B2B 跨境支付现状 |
| 2 | 2026-04-29_random-link.md | — | reject | — | 一次性 HN 链接，无持久价值 |
| 3 | 2026-04-28_methodology-update.md | methodology | update wiki/methodology/decision-frameworks.md | 0.70 | 给 decision-frameworks 加 5W2H 分支 |
| 4 | 2026-04-27_pdf-notes.md | — | archive | — | 有参考价值但散乱，留 archive 备查 |
| 5 | 2026-04-15_half-baked-idea.md | — | defer | — | 想法未成熟，defer_until: 2026-05-15 |

Confirm? Type "all" to accept all, "1,3" to accept rows, "edit 1
disposition=archive" to override, "skip" to abort.
```

Wait for explicit user confirmation. **Do NOT execute on assumed
agreement.** If user says "looks good but 5 reject not defer" → re-emit
table with the override applied + ask again.

## Step 4 · Execute

For each confirmed row, in order:

### accept (new wiki entry)

1. Compute slug: lowercase, kebab-case, ≤ 50 chars, derived from filename
   topic (strip date prefix).
2. Build frontmatter per `wiki/SCHEMA.md`:
   ```yaml
   ---
   title: "<one-line title>"
   domain: <domain>
   created: <YYYY-MM-DD>            # today
   last_updated: <YYYY-MM-DD>       # same as created
   confidence: <0.0-1.0>
   tags: [<domain>, inbox-ingested]
   status: candidate
   source: _meta/inbox/archive/<original-filename>
   ---
   ```
3. Body: rewrite source content to wiki style (no first-person, no
   ephemeral framing, no "I read this today"). Preserve URLs, citations,
   numbers verbatim. Keep ≤ 800 words for first version.
4. Write `wiki/<domain>/<slug>.md`.
5. Move `_meta/inbox/to-process/<original>.md` →
   `_meta/inbox/archive/<original>.md` via `mv` (Bash tool).
6. Append one line to `wiki/log.md`:
   ```
   - [HH:MM] created  | wiki/<domain>/<slug>.md | <one-line summary>
   ```
   (If `wiki/log.md` doesn't exist, create it with the H1 header from the
   `wiki/log.md` template — see end of this prompt.)
7. Update `wiki/INDEX.md` to add the new entry under its domain section.

### update (existing wiki entry)

1. Read the target `wiki/<domain>/<existing-slug>.md`.
2. Apply changes: add new sub-section, append a paragraph, refresh `key
   facts`, etc. Preserve existing frontmatter except bump `last_updated`
   to today and re-evaluate `confidence` (raise if new sources support).
3. Move source to `_meta/inbox/archive/`.
4. Append `wiki/log.md`:
   ```
   - [HH:MM] updated  | wiki/<domain>/<existing-slug>.md | <what changed>
   ```

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

## Step 5 · Report

Output to user:

```
✅ /inbox-process complete

Counts:
  accepted:  N (new wiki entries written)
  updated:   M (existing wiki entries amended)
  archived:  K (kept as raw, no wiki entry)
  rejected:  L (moved to archive with log entry)
  deferred:  P (left in to-process/ until <next defer date>)

Wiki log (last 10 lines):
  <tail of wiki/log.md>

Inbox state:
  to-process/: X items remaining (Y deferred, Z fresh)
  archive/:    W items total
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

## Templates (write these only when missing)

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

- `to-process/` — fresh drops + items deferred to a future date
- `archive/`    — everything that's been triaged (accepted-into-wiki or
                  archived raw or rejected); never deleted, just dormant
- `notifications.md` — system-written; don't put your own drops there

See `wiki/SCHEMA.md` for the wiki frontmatter contract that accepted
items must conform to. See `wiki/log.md` for the activity timeline.
```

### `wiki/log.md` (created on first wiki write if missing)

```markdown
# Wiki · activity log

Append-only timeline of all wiki/ writes. Newest day at the bottom.

Schema source: `wiki/SCHEMA.md` (Logging convention section).

Action enum: `created` | `updated` | `promoted` | `deprecated` | `merged`
| `renamed` | `rejected` | `bulk` (batch operations summary)

Format: `- [HH:MM] <action> | <wiki-path> | <summary>`

---

```

(Then append the `## YYYY-MM-DD` header for today + the first action line.)
