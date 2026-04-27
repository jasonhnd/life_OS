# User-invoked prompt · reindex (v1.8.0)

> Replaces the deleted `tools/reindex.py`. ROUTER reads this when the user
> asks for an index rebuild, then performs the steps directly using
> Read/Write/Glob/Grep tools.

## Trigger keywords

When the user says any of these in a session, ROUTER reads this prompt and
executes:

- `重建索引` / `rebuild index` / `reindex`
- `刷新 INDEX` / `refresh index`
- `INDEX 不准了` / `index out of date`
- session-start-inbox hook reports `reindex Nd` and user says "跑一下" or "全部跑"

## Goal

Rebuild `_meta/sessions/INDEX.md` and `_meta/concepts/INDEX.md` from the
actual session and concept files on disk so ROUTER's later lookups are
correct.

## Steps

### 1. Sessions index

```
- Glob _meta/sessions/*.md (exclude INDEX.md and .gitkeep)
- For each session file: Read frontmatter (id, created, title,
  outcome_score, domain, tags)
- Sort by created descending
- Write _meta/sessions/INDEX.md as a markdown table:
    | sid | date | title | score | domain | tags |
- Header: "# Sessions index · auto-rebuilt {ISO8601}"
```

### 2. Concepts index + synapses

```
- Glob _meta/concepts/*.md
- For each concept file: Read frontmatter (id, name, weight,
  last_coactivation, related_concepts)
- Build _meta/concepts/INDEX.md (sorted by weight desc)
- Build _meta/concepts/SYNAPSES-INDEX.md from `related_concepts` edges
  (one row per (source, target, weight) triple)
```

### 3. Report to user

Show a one-line summary:
```
✅ reindex done · {N} sessions · {M} concepts · {K} synapse edges
   sessions:  _meta/sessions/INDEX.md
   concepts:  _meta/concepts/INDEX.md
   synapses:  _meta/concepts/SYNAPSES-INDEX.md
```

## Output paths

- `_meta/sessions/INDEX.md`
- `_meta/concepts/INDEX.md`
- `_meta/concepts/SYNAPSES-INDEX.md`

## Error handling

- Missing `_meta/sessions/` → tell user "no sessions dir, did you seed?", exit
- Empty session file or malformed frontmatter → skip, log to user
- No write permission → tell user, do not silently fail

## Notes

- This is a deterministic rebuild. Re-running on the same data produces the
  same INDEX. No git push (user commits when they want to).
- For very large repos (>500 sessions), suggest user run `/compress` first
  or run reindex in chunks.
