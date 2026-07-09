# User-invoked prompt · bulk-ingest (v1.10.0 · issue #3 C1)

> Governed bulk import path. The normal ingestion pipeline (inbox/queue →
> extraction → index registration) is designed for a trickle of items;
> production evidence showed a several-hundred-file archive import landing
> directly in the vault left ~400 files outside the governance chain —
> present on disk, absent from indexes, invisible to patrol entry-count
> reconciliation — and cost multiple repo-wide cleanup sweeps. This job
> closes the gap at WRITE time, not detection time.

## Trigger keywords

- `批量导入` / `导入这批文件` / `bulk import` / `bulk ingest` / `import this archive`
- ROUTER MUST route here (not the normal inbox path) whenever a single import
  batch exceeds **20 files** — per `hosts/CLAUDE.md` §Maintenance jobs routing note.

## HARD RULES

1. **Never land batch files directly into live trees** (`wiki/`, `projects/`, `areas/`, `meta/`). Everything stages first.
2. **Manifest before routing** — no file is routed until the batch manifest exists.
3. **Bounded waves with per-wave index registration** — unregistered drift can never exceed one wave (30 files).
4. **Completion is mechanical** — manifest diff shows zero unrouted files; "looks done" is not a completion state.
5. **Flat fan-out only** — if waves are parallelized with subagents, workers MUST NOT spawn further subagents (per `agents/dispatcher.md` §Flat Fan-Out for Bulk Work). Serial waves are the default.

## Step 1 · Quarantine staging

1. Generate `batch-id` = `ingest-<YYYYMMDD>-<HHMM>` (real `date` command).
2. Create `sources/<batch-id>/` and move/copy the entire incoming batch there. Nothing else touches the vault yet.
3. Count files: `find sources/<batch-id> -type f | wc -l`. If ≤ 20, tell the user the normal inbox path also works, but continuing here is fine.

## Step 2 · Batch manifest (before ANY routing)

Write `sources/<batch-id>/MANIFEST.md`:

```markdown
---
batch_id: <batch-id>
source: <where this batch came from — export name, device, URL>
imported_at: <ISO8601>
total_files: <N>
routed_files: 0
---

| # | file | proposed_target | wave | status |
|---|------|------------------|------|--------|
| 1 | notes/foo.md | wiki/<domain>/foo.md | 1 | staged |
```

- One row per file. `proposed_target` may be `TBD` at this point; `status` starts `staged`.
- The manifest is the reconciliation source of truth for this batch — patrols compare `total_files` vs `routed_files`.

## Step 3 · Route in bounded waves (30 files per wave)

For each wave of ≤30 files:

1. **Classify** each file (wiki entry / project doc / area doc / inbox item / discard). Keyword rules tuned on single items misclassify at scale — when classification confidence is low, route to `inbox/` for later human triage instead of guessing a live-tree location.
2. **Move** each file to its target; update its manifest row (`status: routed`, final target).
3. **Register in indexes IMMEDIATELY (per-wave, not at batch end)**: new wiki entries → `wiki/INDEX.md`; project/area docs → the owning `index.md`; concepts → `meta/concepts/INDEX.md`. A wave is not complete until its files are index-registered.
4. Update manifest frontmatter `routed_files` count.
5. Emit one progress line: `📦 wave K/N: 30 routed, 30 registered, 0 pending`.

Wave N+1 starts only after wave N's registration is confirmed.

## Step 4 · Mechanical completion check

```bash
# zero unrouted rows required
grep -c '| staged |' sources/<batch-id>/MANIFEST.md   # MUST be 0
```

- Also verify `routed_files == total_files` in manifest frontmatter.
- Any residue → report the exact rows, keep the batch open. Do NOT declare done.
- When zero: mark manifest frontmatter `status: complete`, leave `sources/<batch-id>/` in place as provenance (manifest + empty staging), report:

```
📦 bulk-ingest complete · <batch-id>
   files: <N> routed in <K> waves · index-registered per wave
   misrouted-to-inbox (low confidence): <M>
   manifest: sources/<batch-id>/MANIFEST.md (0 unrouted)
```

## Final step · Maintenance ledger stamp (v1.10.0)

Per `references/maintenance-ledger-spec.md`: upsert this job's row in
`meta/maintenance-ledger.md` — create the file with its standard header if
missing; if a row for this job exists, replace it in place, otherwise insert
keeping alphabetical order. Never duplicate a row.

`| bulk-ingest | on-demand | <today YYYY-MM-DD, from a real date command — no fabrication> |`
