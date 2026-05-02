# User-invoked prompt · migrate-confidence (v1.8.1)

> One-shot batch migration of legacy `confidence: <float>` (0.0–1.0) wiki
> frontmatter to the v1.8.1 5-bucket enum (`impossible | unlikely |
> possible | likely | certain`). ROUTER reads this when the user wants to
> upgrade a legacy second-brain to the v1.8.1 confidence schema.

## Trigger keywords

- `迁移 confidence` / `升级 confidence schema`
- `migrate confidence` / `convert wiki confidence`
- `/migrate-confidence` (slash command escape hatch)

## Why migrate

The pre-v1.8.1 wiki used `confidence: 0.65` (float). This produced
illusory precision — you can't actually distinguish `0.65` from `0.70`.
The 5-bucket enum forces honest calibration:

| Bucket | When to use |
|---|---|
| `certain` | multi-source convergent, primary verifiable, math/proof complete |
| `likely` | clearly cited, plausible, no known counter-evidence |
| `possible` | single source plausible, or your own draft you've thought through |
| `unlikely` | speculation, anecdote, or source you're not sure about |
| `impossible` | known-false claim being recorded for context only (use rarely) |

Mapping rule (applied by this migration):

| Legacy float | New enum |
|---|---|
| `>= 0.85` | `certain` |
| `0.6 – 0.85` | `likely` |
| `0.3 – 0.6` | `possible` |
| `0.05 – 0.3` | `unlikely` |
| `< 0.05` | `impossible` (rare; usually means "I'm tracking this false claim") |

Boundary cases (exactly 0.6, 0.3, etc.) round UP to the higher bucket.

## Pre-flight

1. Verify cwd is a second-brain repo (`_meta/` + `wiki/` exist). If not,
   refuse and tell user `/migrate-confidence` only runs in a second-brain
   vault.
2. Glob `wiki/**/*.md` (exclude `INDEX.md`, `SCHEMA.md`,
   `OBSIDIAN-SETUP.md`, `log.md`, `.templates/`).
3. For each file, Read frontmatter and detect the `confidence:` value
   shape:
   - already `enum` (one of the 5 strings) → skip
   - float in 0.0–1.0 → migration candidate
   - missing → add `confidence: possible` (sensible default)
   - other (e.g. `confidence: high`) → ask user how to map

## Plan preview

Output a single table BEFORE writing anything:

```
🔄 migrate-confidence plan — N entries scanned

| # | path | current | proposed | reason |
|---|------|---------|----------|--------|
| 1 | wiki/fintech/stablecoin-b2b.md | 0.65 | likely | float 0.6-0.85 |
| 2 | wiki/methodology/decision-frameworks.md | 0.85 | likely | exactly 0.85 boundary, rounds up to certain |
| 3 | wiki/biology/sleep-debt.md | 0.4 | possible | float 0.3-0.6 |
| 4 | wiki/finance/saas-models.md | (missing) | possible | default for missing |
| 5 | wiki/legacy/old-note.md | high | ? | unknown legacy string — please choose |
| ...

Total to migrate: K
Total skipped (already enum): J
Total needing user decision: U

Confirm? Type "yes" to apply all. Type "edit 5 confidence=possible" to
override one row. Type "skip 5" to leave one row unmigrated. Type "no"
to abort.
```

Wait for explicit confirmation. Do NOT write on assumed agreement.

## Execute

For each confirmed row:

1. Read the file (Read tool).
2. Edit the `confidence:` line in frontmatter to the new enum value (Edit
   tool with `old_string` = the entire line, `new_string` = new line).
3. Bump `last_tended` to today (this counts as a tending action).
4. Append one line to `wiki/log.md`:
   ```
   - [HH:MM] updated  | <path> | confidence schema migration: <old> → <new>
   ```

If file write fails for any row, log the failure but continue with the
rest. Surface failures cleanly at the end.

## Post-migration report

```
✅ migrate-confidence complete

  migrated:  K entries (legacy float → enum)
  defaulted: D entries (had no confidence → set to `possible`)
  skipped:   J entries (already enum)
  failed:    F entries (see paths below; retry manually)

Migration log appended to wiki/log.md (K + D entries).
```

## Failure modes

- **wiki/log.md write fails**: rollback that one entry's frontmatter
  edit; report; continue.
- **Frontmatter unparseable**: skip; report path; user must fix manually.
- **Unknown legacy string** (e.g. `confidence: medium`, `confidence:
  trustworthy`): in plan-preview phase, ask user to map each unknown
  value to one of the 5 buckets BEFORE the execute phase.

## Idempotency

Re-running this prompt is safe — entries already on the enum are
skipped. The only thing that changes on re-run is `last_tended` for
already-migrated entries (it does NOT re-bump them; the skip happens
before the tend bump).

## Rollback

This prompt does NOT save a backup. Before running, the user should:

```bash
git -C ~/path/to/second-brain status   # confirm clean tree
git -C ~/path/to/second-brain commit -am "pre-migrate-confidence snapshot"
```

If the migration produces unexpected mappings, `git checkout -- wiki/`
restores all entries.
