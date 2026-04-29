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
2. Identify legacy reference patterns:
   - `concept "foo"` / `wiki "bar"` → `[[foo]]` / `[[bar]]`
   - Bare ID mentions like `(see CONCEPT-FOO)` → `(see [[foo]])`
   - Stylized cross-refs like `→ wiki/decision-engine.md` → `→ [[wiki-decision-engine]]`
   - Names matching people/canonical_name → `[[person-jason]]` etc.

3. Apply edits via Edit tool, one canonical text replacement per pattern.

4. Skip code blocks, YAML frontmatter (except known exceptions), HTML comments.

5. After file done, verify with quick re-read.

### Phase 3: Frontmatter exceptions

For `_meta/concepts/*.md` only, also update:

```yaml
provenance:
  source_sessions:
    - "[[2026-04-29]]"             # was: "2026-04-29"
    - "[[2026-04-22]]"
outgoing_edges:
  - target: "[[concept-bar]]"      # was: target: "bar"
    weight: 0.7
    type: related
```

For all other frontmatter fields, KEEP as plain strings (machine-parseable).

### Phase 4: Validation

After all files migrated:

1. Check for broken wikilinks: extract all `[[...]]` patterns, verify target file exists.
2. Report broken links: `[[unknown-id]]` found in `_meta/sessions/2026-03-15.md` line 42.
3. User decides: create stub / fix typo / leave as TODO.

### Phase 5: Backup before write

BEFORE any Edit, create timestamped backup:

```bash
mkdir -p _meta/migration-backup/{ISO-DATE}
cp -r wiki/ _meta/concepts/ _meta/sessions/ _meta/methods/ \
       SOUL.md _meta/STRATEGIC-MAP.md \
       _meta/migration-backup/{ISO-DATE}/
```

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
