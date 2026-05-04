# User-invoked prompt · wiki-decay (v1.8.1)

> Replaces the deleted `tools/wiki_decay.py`. ROUTER reads this when the
> user wants to scan the wiki for stale entries.

## Trigger keywords

- `扫一下 wiki` / `wiki decay` / `查 wiki 过期`
- `wiki 哪些过时了`
- session-start-inbox hook reports `wiki-decay Nd` and user says "跑一下"

## Goal

Classify every entry in `wiki/` as `stale` / `due-for-review` /
`borderline` / `active` based on `last_tended` + `review_by` +
`confidence` (5-bucket enum), so the user knows what knowledge needs
review.

## v1.8.1 schema notes

The wiki templates added `last_tended` and `review_by` fields:

- `last_tended` — last time the user *actively reviewed* the entry (not
  cosmetic edit). Falls back to `last_updated` for legacy entries.
- `review_by` — explicit "re-surface this entry on or after" date set by
  the user or `/inbox-process`. Default = `last_tended` + 180 days.
- `confidence` — 5-bucket enum: `impossible | unlikely | possible |
  likely | certain`. Legacy float values 0.0–1.0 should be migrated via
  `scripts/prompts/migrate-confidence.md`. Map legacy floats during this
  scan as: `< 0.3 → unlikely`, `0.3-0.6 → possible`, `0.6-0.85 → likely`,
  `>= 0.85 → certain`.

## Steps

### 1. Scan wiki/

Glob `wiki/**/*.md` (recursive). For each file, Read frontmatter:

```yaml
title: "..."
confidence: likely        # 5-bucket enum (or legacy float)
last_updated: 2026-03-15
last_tended: 2026-03-15   # may be missing on legacy entries
review_by: 2026-09-15     # may be missing on legacy entries
sources: [...]            # may be `source: ...` on legacy entries
```

If frontmatter unparseable, mark `borderline` with reason "yaml-error".
Skip `INDEX.md` / `SCHEMA.md` / `OBSIDIAN-SETUP.md` / `log.md` /
`.templates/*` (those aren't knowledge entries).

### 2. Classify

For each entry, compute:
- `age_tended = today - (last_tended || last_updated)`
- `due = (review_by exists AND review_by <= today)`

Then bucket:

```
due-for-review: due == true                        (highest priority — user explicitly flagged)
stale:          age_tended > 180 AND confidence in {impossible, unlikely, possible}
borderline:     age_tended > 90 OR confidence in {unlikely, possible} OR no last_tended
active:         everything else
```

A `due-for-review` entry takes precedence over `stale`/`borderline` even
if other criteria also match — this is what the user asked the system to
remind them of.

### 3. Write report (v1.8.2 Obsidian-style)

Write `_meta/eval-history/wiki-decay-{YYYY-MM-DD}.md` per `references/obsidian-style.md` (rule #11):

```markdown
---
title: "Wiki decay scan · {YYYY-MM-DD}"
tags: [eval-history/wiki-decay]
created: {YYYY-MM-DD}
---

# Wiki decay scan · {YYYY-MM-DD}

> [!info] Summary
> - Total entries:    {N}
> - Due for review:   {D}  (you set review_by; date passed)
> - Stale:            {S}  (180+ days untouched + low confidence)
> - Borderline:       {B}  (90-180 days OR low confidence OR missing last_tended)
> - Active:           {A}  (no action)

## Due for review ({D}) — HIGHEST PRIORITY

> [!important] You explicitly flagged these for re-surfacing
> Set `review_by` arrived. Each one needs a decision: keep / update / deprecate.

- [[{entry-name}]] · review_by={date} · confidence={enum} · age_tended={age}d
  hint: {1-line from TL;DR}
- [[{entry-name}]] · ...

## Stale ({S})

> [!warning] 180+ days untouched + low confidence
> System didn't flag these explicitly (no review_by set), but they're old AND low-confidence — most benefit from revalidation or deprecation.

- [[{entry-name}]] · last_tended={date} ({age}d ago) · confidence={enum}
- [[{entry-name}]] · ...

## Borderline ({B})

> [!note] Maintenance tier
> 90-180 days OR low confidence OR missing `last_tended`. Quick scan; if still trustworthy, bump `last_tended` for free freshness signal.

- [[{entry-name}]] · last_tended={date or "missing"} · confidence={enum}
  reason: {age 90-180d | low confidence | no last_tended}
- [[{entry-name}]] · ...

## Active ({A})

(omit list — just count, user doesn't need to see them)

## Recommended actions

> [!tip] Decision tree
> - **Due for review** → re-read, then: keep-as-is (bump `last_tended` + push `review_by` +180d) / update-content (bump both, adjust `confidence`) / deprecate (`status: deprecated`, archive sources)
> - **Stale** → same options but you weren't expecting it; default action is revalidation or deprecation
> - **Borderline** → quick scan; if still trustworthy just bump `last_tended` (free freshness signal); if `last_tended` is missing, backfill it
```

### Obsidian-readability HARD RULE (v1.8.2)

This report renders in Obsidian. Apply `references/obsidian-style.md`:

- Use `[[wikilink]]` for entry references (NOT `[name](path/to/entry.md)`)
- Use `> [!info|warning|important|note|tip]` callouts for semantic blocks
- Use nested tags `eval-history/wiki-decay` (not flat `[eval-history, wiki-decay]`)

### 4. Optional · Link audit (replaces deleted `scripts/wiki/wiki-link-audit.sh`)

If the user added `+ link audit` / `+ 链接审计` to the request, also:

1. Glob all `wiki/**/*.md`. Build a map `{entry_path → [outbound wikilinks]}`
   by `Grep`-ing for `\[\[([^\]]+)\]\]` patterns.
2. For each link target, check whether the target file exists. Track
   `broken_links: [(source_entry, target)]`.
3. For each entry, count inbound wikilinks (how many other entries link
   here). Mark `orphans` (zero inbound + zero outbound).
4. Append a "Link audit" section to the report:

```markdown
## Link audit (optional · {YYYY-MM-DD})

- Total entries scanned:  {N}
- Total wikilinks:        {L}
- Broken links:           {K}
- Orphan entries:         {O} (no inbound + no outbound)

### Broken links ({K})
- {source_entry}: link → `[[{target}]]` (target file not found)
...

### Orphan entries ({O}) — candidates for either better integration or deprecation
- {orphan_entry_path}
...
```

This replaces the v1.7-era `scripts/wiki/wiki-link-audit.sh` (deleted in
v1.8.1; see `scripts/prompts/wiki-link-audit.md` for the standalone
prompt that does only this audit).

### 5. Report to user

```
🌱 wiki-decay done · {N} entries scanned
   ⏰ {D} due for review (you set review_by) · {S} stale · {B} borderline · {A} active
   {if link audit ran:} 🔗 {K} broken links · {O} orphans
   _meta/eval-history/wiki-decay-{date}.md
```

## Output path

- `_meta/eval-history/wiki-decay-{YYYY-MM-DD}.md`

## Notes

- This is read-only on `wiki/`. No file is modified or deleted by this scan.
- The "borderline" bucket catches frontmatter-incomplete entries — user
  might want to backfill `last_tended` after the scan.
- Thresholds (180d, 90d, confidence buckets) are conservative defaults;
  user can override by saying "用 60/120 天阈值" etc.
- Legacy entries with `confidence: <float>` instead of enum still work —
  this scan auto-maps. For permanent migration, run
  `/migrate-confidence` (see `scripts/prompts/migrate-confidence.md`).
