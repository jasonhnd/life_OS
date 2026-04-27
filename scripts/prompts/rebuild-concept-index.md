# User-invoked prompt · rebuild-concept-index (v1.8.0 Option A)

> Replaces deleted `tools/rebuild_concept_index.py`. ROUTER reads this when
> user asks for manual concept INDEX rebuild.

## Trigger keywords

- `重建概念索引` / `rebuild concept index`
- `刷新 concepts INDEX` / `refresh concept index`
- `concept INDEX 不准了`

## Goal

Rebuild `_meta/concepts/INDEX.md` (sorted by weight) and
`_meta/concepts/SYNAPSES-INDEX.md` (one row per synapse edge) from per-concept
markdown files.

## Steps

### 1. Concept index

1. `Glob _meta/concepts/**/*.md` (exclude INDEX.md and SYNAPSES-INDEX.md)
2. For each file, Read frontmatter:
   - `id`, `name`, `domain`, `weight`, `last_coactivation`, `activation_count`,
     `status`, `aliases[]`
3. Sort by `weight` desc, `last_coactivation` desc tie-break
4. Group by `domain` (## headings)
5. Format each line: `{id} | {name} | weight={weight} | last={last_coactivation} | status={status}`
6. Write `_meta/concepts/INDEX.md` with header `# Concepts index · auto-rebuilt {ISO8601}`

### 2. Synapses index

1. For each concept file, Read `outgoing_edges:` array
2. Each edge has: `target`, `weight`, `last_co_activated`
3. Emit row: `{source_id} → {target} | weight={weight} | last={last_co_activated}`
4. Sort by weight desc
5. Write `_meta/concepts/SYNAPSES-INDEX.md`

## Failure handling

- Malformed YAML → log to `_meta/sync-log.md`, skip
- Edge target doesn't exist as concept file → keep edge but flag in INDEX as `(orphan target)`

## Report to user

```
✅ concept INDEX rebuilt · {N} concepts · {M} synapse edges · {D} domains
   _meta/concepts/INDEX.md
   _meta/concepts/SYNAPSES-INDEX.md
```
