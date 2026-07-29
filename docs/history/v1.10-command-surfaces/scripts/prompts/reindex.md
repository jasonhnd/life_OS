# User-invoked prompt · reindex (v1.8.2 · Obsidian-style)

> Replaces the deleted `tools/reindex.py`. ROUTER reads this when the user
> asks for an index rebuild, then performs the steps directly using
> Read/Write/Glob/Grep tools.
>
> **v1.8.2 HARD RULE #11**: Rebuilt INDEX.md files render in Obsidian. Apply
> `references/obsidian-style.md` — entry rows use `[[wikilinks]]`, optional
> `> [!info]` summary callout at top, nested tags.

## Trigger keywords

When the user says any of these in a session, ROUTER reads this prompt and
executes:

- `重建索引` / `rebuild index` / `reindex`
- `刷新 INDEX` / `refresh index`
- `INDEX 不准了` / `index out of date`
- retrospective Mode 0 Conscious Patrol reports `reindex Nd` overdue and user says "跑一下" or "全部跑"

## Goal

Rebuild `meta/sessions/INDEX.md` and `meta/concepts/INDEX.md` from the
actual session and concept files on disk so ROUTER's later lookups are
correct.

## Steps

### 1. Sessions index

```
- Glob meta/sessions/*.md (exclude INDEX.md and .gitkeep)
- For each session file: Read frontmatter (id, created, title,
  outcome_score, domain, tags)
- Sort by created descending
- Write meta/sessions/INDEX.md as a markdown table:
    | sid | date | title | score | domain | tags |
- Header: "# Sessions index · auto-rebuilt {ISO8601}"
```

### 2. Concepts index + synapses

```
- Glob meta/concepts/*.md
- For each concept file: Read frontmatter (id, name, weight,
  last_coactivation, related_concepts)
- Build meta/concepts/INDEX.md (sorted by weight desc)
- Build meta/concepts/SYNAPSES-INDEX.md from `related_concepts` edges
  (one row per (source, target, weight) triple)
```

### 3. Report to user

Show a one-line summary:
```
✅ reindex done · {N} sessions · {M} concepts · {K} synapse edges
   sessions:  meta/sessions/INDEX.md
   concepts:  meta/concepts/INDEX.md
   synapses:  meta/concepts/SYNAPSES-INDEX.md
```

## Output paths

- `meta/sessions/INDEX.md`
- `meta/concepts/INDEX.md`
- `meta/concepts/SYNAPSES-INDEX.md`

## Error handling

- Missing `meta/sessions/` → tell user "no sessions dir, did you seed?", exit
- Empty session file or malformed frontmatter → skip, log to user
- No write permission → tell user, do not silently fail

## Notes

- This is a deterministic rebuild. Re-running on the same data produces the
  same INDEX. No git push (user commits when they want to).
- For very large repos (>500 sessions), suggest user run `/compress` first
  or run reindex in chunks.

## Final step · Maintenance ledger stamp (v1.10.0)

Per `references/maintenance-ledger-spec.md`: upsert this job's row in
`meta/maintenance-ledger.md` — create the file with its standard header if
missing; if a row for this job exists, replace it in place, otherwise insert
keeping alphabetical order. Never duplicate a row.

`| reindex | 7d | <today YYYY-MM-DD, from a real date command — no fabrication> |`
