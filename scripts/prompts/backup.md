# User-invoked prompt · backup (v1.8.0)

> Replaces the deleted `tools/backup.py`. ROUTER reads this when the user
> wants to snapshot the second-brain.

## Trigger keywords

- `备份` / `backup` / `打包`
- `做一份快照` / `snapshot`
- session-start-inbox hook reports `backup Nd` and user says "跑一下"

## Goal

Create a tar.gz archive of the user's second-brain state and write a small
log entry. This is local snapshot only — git push is the user's call.

## Steps

### 1. Determine target paths

```
TS=$(date -u +%Y-%m-%d-%H%M)
ARCHIVE=_meta/snapshots/backup-${TS}.tar.gz
LOG=_meta/eval-history/backup-$(date -u +%Y-%m-%d).md
```

### 2. Build archive (Bash)

```bash
mkdir -p _meta/snapshots
tar czf "$ARCHIVE" \
  --exclude='_meta/snapshots/*.tar.gz' \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  _meta/ wiki/ SOUL.md projects/ areas/ inbox/
```

If a directory doesn't exist, omit it from the tar list and continue.

### 3. Compute report

```
- file_count: $(tar tzf "$ARCHIVE" | wc -l)
- archive_size: $(du -h "$ARCHIVE" | cut -f1)
```

### 4. Write log

Write `$LOG` (Write tool):

```markdown
# Backup · {YYYY-MM-DD}

- archive: _meta/snapshots/backup-{TS}.tar.gz
- size: {archive_size}
- files: {file_count}
- created: {ISO8601}
```

### 5. Report to user

```
💾 backup done
   archive: _meta/snapshots/backup-{TS}.tar.gz ({size}, {files} files)
   log:     _meta/eval-history/backup-{date}.md
```

## Output paths

- `_meta/snapshots/backup-{YYYY-MM-DD-HHMM}.tar.gz`
- `_meta/eval-history/backup-{YYYY-MM-DD}.md`

## Notes

- Archive size for typical second-brain: 1-50 MB. Warn user if > 200 MB
  (might mean they need to prune).
- Old backups are NOT auto-pruned. User decides when to delete.
- No git push (snapshots are gitignored).
