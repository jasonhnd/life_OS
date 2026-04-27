# User-invoked prompt · migrate-from-v1.6 (v1.8.0 Option A)

> Replaces deleted `tools/migrate.py` (903 lines). ROUTER reads this when user
> upgrades from a v1.6.x second-brain to v1.7+ schema.

## Trigger keywords

- `从 v1.6 升级` / `migrate from v1.6`
- `v1.6 → v1.7 数据迁移` / `legacy migration`
- `升级第二大脑数据`

## Goal

Migrate a pre-v1.7 second-brain layout to the v1.7+ schema. **Read-heavy +
careful — wrong migration can corrupt years of decision history.** Always
backup before starting.

## Pre-flight checks

1. **Confirm with user before any write**: "I'm about to migrate {path}. This
   will create new `_meta/sessions/`, `_meta/concepts/`, `_meta/snapshots/`
   directories. Existing files will be preserved. OK?"
2. Verify `git status` is clean. If not: tell user to commit first.
3. Create branch: `git checkout -b migrate-v1.6-to-v1.7-{date}`
4. `cp -r .` of the entire repo to `/tmp/lifeos-backup-{date}` as belt-and-suspenders.

## Migration steps

### 1. Detect v1.6 schema markers

- v1.6 has `_meta/journal/` with date-named markdown files (one per session)
- v1.6 has `_meta/index.md` (single flat index file)
- v1.6 lacks `_meta/concepts/` and `_meta/snapshots/`

If markers absent → tell user "this brain is already v1.7+, no migration needed".

### 2. Migrate sessions

For each `_meta/journal/{YYYY-MM-DD}-*.md`:
- Parse frontmatter (v1.6 fields: `id`, `subject`, `decisions`, `outcome`)
- Generate v1.7 session_id: `{YYYY-MM-DD}T{HHMM}Z` from filename + frontmatter timestamp
- Map v1.6 → v1.7 frontmatter fields:
  - `subject` → `subject`
  - `decisions[]` → `Key Decisions` body section
  - `outcome` → `Outcome` body section + estimate `outcome_score` from sentiment
  - Add new required fields with defaults: `duration_minutes: 0`, `platform: claude-code`,
    `theme: zh-classical`, `workflow: full`, `veto_count: 0`, `council_triggered: false`,
    `compliance_violations: 0`
- Write to `_meta/sessions/{session_id}.md` matching the v1.7 schema in
  `pro/agents/archiver.md` (SessionSummary block)

### 3. Initialize empty cortex graph

- `mkdir -p _meta/concepts/`
- Write empty `_meta/concepts/INDEX.md` (concept extraction happens at next archiver run)
- `mkdir -p _meta/snapshots/soul/`
- If `SOUL.md` exists, write initial snapshot at `_meta/snapshots/soul/{date}-0000.md`
  using current SOUL.md state (per Snapshot Schema in archiver.md)

### 4. Verify

- Run `scripts/prompts/rebuild-session-index.md` to compile sessions INDEX
- Spot-check 3 random sessions: open old `_meta/journal/{file}` and new
  `_meta/sessions/{sid}.md` side-by-side, confirm content preserved
- Tell user to manually inspect: `_meta/journal/` is preserved (not deleted)
  for 30 days; user can `rm -rf` it after confidence builds

## Report to user

```
✅ Migration complete · v1.6 → v1.7
   - {N} sessions migrated to _meta/sessions/
   - 1 SOUL snapshot created at _meta/snapshots/soul/
   - Empty concepts graph at _meta/concepts/ (will populate on next archiver)
   - Old _meta/journal/ preserved for 30 days
   - Branch: migrate-v1.6-to-v1.7-{date}
   - Backup: /tmp/lifeos-backup-{date}
   
   Review the diff, then merge to main when satisfied.
```

## Critical notes

- This is a **destructive-feeling migration** (creates new files structure).
  Backup is mandatory.
- LLM doing data migration is risky. If user has > 100 sessions, suggest
  doing in batches of 20 with verification between batches.
- If any step fails midway, the partial state is in the migration branch —
  user can `git reset --hard main` to abandon.
