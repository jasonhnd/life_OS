# User-invoked prompt · snapshot-cleanup (v1.8.2 · Obsidian-style)

> Replaces `tools/lib/cortex/snapshot.py:should_archive()` / `should_delete()`
> retention logic, deleted in Option A pivot. ROUTER reads this when user
> asks for SOUL snapshot cleanup, otherwise snapshots accumulate forever.
>
> **v1.8.2 HARD RULE #11**: Cleanup report renders in Obsidian. Apply
> `references/obsidian-style.md` — `> [!info]` for retention plan,
> `> [!success]` for cleanup result, nested tags.

## Trigger keywords

- `清理 SOUL snapshots` / `snapshot cleanup`
- `归档旧 snapshot` / `archive old snapshots`
- `_meta/snapshots/soul/ 太多了`

## Goal

Apply 30/90 day retention policy to `_meta/snapshots/soul/`:
- 30+ days old → move to `_meta/snapshots/soul/_archive/`
- 90+ days old → delete

## Steps

1. `Glob _meta/snapshots/soul/*.md` (exclude `_archive/`)
2. For each file, parse `captured_at` from frontmatter (ISO8601) OR fall back
   to filename `YYYY-MM-DD-HHMM` parsing
3. Compute age in days from current UTC date
4. Bucket:
   - `age < 30` → leave (active)
   - `30 <= age < 90` → move to `_meta/snapshots/soul/_archive/{file}`
     (use `Bash: mv` or Read+Write+Delete)
   - `age >= 90` → delete (`Bash: rm`)
5. Repeat the bucket pass on `_meta/snapshots/soul/_archive/` to delete files
   that are now > 90 days old (they were archived previously)

## Report to user

```
🧹 snapshot-cleanup done
   active:    {N} (< 30d)
   archived:  {M} (30-90d, moved to _archive/)
   deleted:   {K} (≥ 90d)
   total before: {N+M+K}, after: {N+M}
```

## Safety

- Confirm with user before deleting if K > 10
- Never touch files matching `latest.md` symlink target
- Dry-run mode: if user says "dry run" / "preview only", just list the
  buckets without moving/deleting
