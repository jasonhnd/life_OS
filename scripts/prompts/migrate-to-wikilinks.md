# User-invoked prompt · migrate existing content to wikilinks (v1.8.0 R-1.8.0-013)

> One-time migration of legacy content to Obsidian-style `[[wikilinks]]`.
> User chose "4 (全, 完整)" — full migration of all existing content, not
> just new writes.

## Trigger keywords

- `迁移 wikilinks` / `migrate to wikilinks` / `跑迁移`
- `把老内容都改成 wikilinks` / `link migration`

## Context

Before R-1.8.0-013, lifeos used:
- Plain text references (e.g., "see CONCEPT-FOO" or "wiki entry bar")
- Frontmatter id strings (e.g., `concepts: [foo, bar]`)
- Cross-doc references via `references/wiki-spec.md` "No cross-references" rule

After R-1.8.0-013:
- Body uses `[[id]]` or `[[id|Display]]` for any concept/wiki/people/comparison/method reference
- Frontmatter stays YAML strings for machine parsing
- BUT `provenance.source_sessions` and `outgoing_edges.target` are exceptions —
  they use `[[]]` even in frontmatter (per `references/concept-spec.md`)

This prompt rewrites legacy content to match the new convention.

## Required actions

### Phase 0: Inventory

Read these directories and count files needing migration:

```
wiki/                                  # all .md (look for legacy refs in body)
_meta/concepts/*.md                    # check provenance, outgoing_edges fields
_meta/sessions/202*-*-*.md             # session journals — body refs
_meta/methods/*.md                     # method body refs
_meta/people/*.md                      # if any pre-existing
_meta/comparisons/*.md                 # if any pre-existing
SOUL.md                                # snapshots may reference concepts
_meta/STRATEGIC-MAP.md                 # likely references projects/concepts
```

Report inventory:

```
📋 Migration inventory
- wiki/ — 12 files
- _meta/concepts/ — 47 files (provenance + outgoing_edges to update)
- _meta/sessions/ — 89 files (90 days)
- _meta/methods/ — 5 files
- _meta/people/ — 0 files
- _meta/comparisons/ — 0 files
- SOUL.md — 1 file
- _meta/STRATEGIC-MAP.md — 1 file

Total: 155 files. Estimated 800+ wikilinks to insert.

Proceed? (Y/N)
```

If user says N, exit silently.

### Phase 1: Build identifier index

Scan all of `_meta/concepts/`, `wiki/`, `_meta/people/`, `_meta/comparisons/`,
`_meta/methods/`. Build map:

```python
identifier_map = {
    "foo": "concept-foo",          # canonical id, slug from filename
    "Decision Engine": "wiki-decision-engine",
    "Jason": "person-jason",
    ...
}
```

Strategy:
- Filename slug = canonical id (strip `.md`)
- Add aliases from frontmatter (`canonical_name`, `aliases` for people/concepts)
- For long names, generate display variant: `[[concept-decision-engine|Decision Engine]]`

### Phase 2: Body migration (per file)

For each file in inventory:

1. Read file.
2. Identify legacy reference patterns. **WORD-BOUNDARY MATCHING IS MANDATORY**
   — match only on whitespace / punctuation / line boundaries, never substring.
   Example of what to avoid: name "Al" must NOT match inside "Algorithm" →
   `[[person-al]]gorithm`. Use regex like `\bAl\b` (or markdown-aware
   equivalent).
   - `concept "foo"` / `wiki "bar"` → `[[foo]]` / `[[bar]]`
   - Bare ID mentions like `(see CONCEPT-FOO)` → `(see [[foo]])`
   - Stylized cross-refs like `→ wiki/decision-engine.md` → `→ [[wiki-decision-engine]]`
   - Names matching people/canonical_name → `[[person-jason]]` etc.
   **DO NOT** create wikilinks-inside-wikilinks: if the target text already
   sits inside an existing `[[...]]` or `[[...|...]]` display alias, skip
   that occurrence (Obsidian renders only the outer link; nested becomes
   broken literal text).

3. Apply edits via Edit tool, one canonical text replacement per pattern.

4. Skip:
   - YAML frontmatter (except known exceptions per Phase 3)
   - HTML comments `<!-- ... -->`
   - Fenced code blocks (between ``` lines)
   - Inline code (between single `backticks`)
   - URL paths (don't rewrite `[link](https://...)` text)

5. After file done, verify with quick re-read.

### Phase 3: Frontmatter exceptions

For `_meta/concepts/*.md` only, also update (see `references/concept-spec.md`
canonical schema):

```yaml
provenance:
  source_sessions:
    - "[[2026-04-29]]"             # was: "2026-04-29"
    - "[[2026-04-22]]"
outgoing_edges:
  - target: "[[concept-bar]]"      # was: to: bar  (renamed `to` → `target`)
    weight: 5                      # NON-NEGATIVE integer 1-100
    last_co_activated: 2026-04-29T10:00:00+09:00   # was: last_reinforced (renamed)
```

For all other frontmatter fields, KEEP as plain strings (machine-parseable).

### Phase 4: Validation

After all files migrated:

1. Check for broken wikilinks: extract all `[[...]]` patterns, verify target file exists.
2. Report broken links: `[[unknown-id]]` found in `_meta/sessions/2026-03-15.md` line 42.
3. User decides: create stub / fix typo / leave as TODO.

### Slug collision handling (Phase 1.5)

If `identifier_map` builder hits two pages with the same canonical slug
(e.g., concept "Foo" exists in both `wiki/finance/foo.md` and
`wiki/startup/foo.md` — both naive-slug to `foo`), apply the
double-hyphen-suffix rule from `references/concept-spec.md` § 4.2:
`foo`, `foo--2`, `foo--3`, etc. Surface the collision to the user as a
review-queue P1 item rather than silently mapping one to the other.

### Phase 5: ⚠️ MANDATORY BACKUP — RUN THIS BEFORE PHASE 2 EDITS

**Despite phase numbering, this MUST execute BEFORE Phase 2's first Edit
call. Do not begin Phase 2 until backup completes.** Phase numbering is
historical (followed inventory→index→migration→validation discovery flow);
execution order MUST be: 0 → 1 → 1.5 → 5 → 2 → 3 → 4 → 6.

```bash
# Cross-platform: prefer Python copier for Windows compatibility
mkdir -p _meta/migration-backup/{ISO-DATE}
# Bash:
cp -r wiki/ _meta/concepts/ _meta/sessions/ _meta/methods/ \
       _meta/people/ _meta/comparisons/ \
       SOUL.md _meta/STRATEGIC-MAP.md \
       _meta/migration-backup/{ISO-DATE}/  2>/dev/null || true
# Windows PowerShell equivalent:
# Copy-Item -Path wiki,_meta\concepts,_meta\sessions,_meta\methods,SOUL.md,_meta\STRATEGIC-MAP.md -Destination _meta\migration-backup\{ISO-DATE}\ -Recurse
```

Verify backup directory non-empty + has same file count as source dirs
BEFORE proceeding to Phase 2. If backup fails, ABORT migration entirely.

### Phase 6: Run report

After migration:

```
✅ Wikilink migration complete
- Files scanned: 155
- Files modified: 92
- Wikilinks inserted: 814
- Broken links found: 3 (see report below)
- Backup at: _meta/migration-backup/2026-04-29T10-30-00/

Broken links:
1. [[concept-undefined-foo]] in _meta/sessions/2026-03-15.md:42
2. [[person-bob]] in wiki/team-decisions.md:120 (typo? did you mean [[person-rob]]?)
3. [[wiki-old-name]] in SOUL.md:200 (file renamed to wiki-new-name?)

Suggested actions:
- Add 3 items to review queue (P1) for manual fix
- OR run `process queue` after this to walk through them
```

## HARD RULES

- **Backup before any write** (Phase 5 mandatory, no exceptions)
- **Use Edit tool, not Write** — preserves git diff readability per file
- **One Edit per pattern replacement** — atomic, easy to inspect/revert
- **Skip code blocks** — `wikilinks` inside ```...``` are content, not refs
- **Skip frontmatter (except known exceptions)** — YAML must stay parseable
- **Privacy filter** — if migrating creates a `_meta/people/<id>.md` reference
  with `privacy_tier: high`, ensure body context doesn't expose private info
- **Idempotent** — re-running on already-migrated content is a no-op
- **Audit trail**: write `_meta/runtime/{sid}/wikilink-migration.json`
  with file count, link count, broken link list

## Anti-patterns

- DON'T migrate without inventory step (user must see scope)
- DON'T silently fix broken links — surface them via review queue
- DON'T touch session files older than 90 days unless user explicitly asks
  (those are historical, low value to migrate)
- DON'T merge multiple files' edits into one commit — per-directory commits
  for clean rollback

## Recovery if something goes wrong

If user reports issue post-migration:

1. Restore from `_meta/migration-backup/{date}/` to affected paths
2. Investigate which pattern caused issue
3. Patch this prompt's Phase 2 logic
4. Re-run on remaining files

Backup retention: keep `_meta/migration-backup/` for 30 days, then delete
(only via explicit user instruction — never auto-delete).
