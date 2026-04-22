---
scenario: tool-migrate
type: tool-invocation
tool: migrate
requires_claude: false
# R4.5 machine-eval fields — empty journal => no-op migration, exit 0.
setup_script: |
  mkdir -p {tmp_dir}/_meta/journal
invocation: "python3 -m tools.migrate --from v1.6.2a --to v1.7 --dry-run --root {tmp_dir}"
expected_exit_code: 0
expected_stdout_contains: []
expected_stderr_contains: []
expected_files: []
---

# Tool Scenario · migrate

**Contract**: references/tools-spec.md §6.7 · v1.6.2a → v1.7 one-shot schema backfill (3-month window).

## User Message

```
我的 second-brain 还是 v1.6.2a，请把最近 3 个月的 journal 迁移到 v1.7 Cortex 四件套（sessions / concepts / snapshots / methods），先 --dry-run。
```

(English equivalent: "My second-brain is still v1.6.2a; please migrate the last 3 months of journal entries into v1.7 Cortex 4-artefact layout; dry-run first.")

## Scenario

One-time migration from the legacy v1.6.2a journal layout (all entries in
`_meta/journal/YYYY-MM-DD.md`) to the v1.7 Cortex layout of 4 artefacts:

1. `_meta/sessions/{session_id}.md` + `INDEX.md` (per session-index-spec §9)
2. `_meta/concepts/**` (concept-spec §Migration)
3. `_meta/snapshots/soul/**` (snapshot-spec §Migration)
4. `_meta/methods/_tentative/**` (method-library-spec §15)

Bounded to last 3 months (user decision #7). LLM-free — pure rule-based
extraction. Idempotent. Does NOT touch `SOUL.md`, `wiki/`, or
`user-patterns.md` (read-only inputs). Does NOT backfill `eval-history/`
(starts fresh at v1.7 day one).

Writes `_meta/cortex/bootstrap-status.md` with run summary + any files
that failed to parse.

## Success Criteria

- [ ] `uv run tools/migrate.py --from v1.6.2a --to v1.7 --dry-run --root <fixture>` exits 0, no files created
- [ ] Actual run with 90 journal entries (spanning 3 months) produces:
  - [ ] ≥ 50 session files under `_meta/sessions/` (one per distinct session)
  - [ ] `_meta/sessions/INDEX.md` with correct row count
  - [ ] ≥ 10 concept files under `_meta/concepts/`
  - [ ] `_meta/concepts/INDEX.md` + `_meta/concepts/SYNAPSES-INDEX.md`
  - [ ] At least one snapshot under `_meta/snapshots/soul/`
  - [ ] `_meta/methods/_tentative/` populated
  - [ ] `_meta/cortex/bootstrap-status.md` written with summary
- [ ] Journal entry older than 3 months NOT migrated
- [ ] `SOUL.md` / `wiki/**` / `user-patterns.md` unchanged (byte-identical before/after)
- [ ] `_meta/eval-history/` NOT created
- [ ] Idempotent: second run produces same INDEX, no duplicate session files
- [ ] At least one parse failure → logged in `bootstrap-status.md`, exit 1, other files still migrated

## Input Fixture

```
fixture-brain-v162a/
├── _meta/journal/
│   ├── 2026-04-20.md              # in-window
│   ├── 2026-03-15.md              # in-window
│   ├── 2026-01-20.md              # out-of-window (> 3 months)
│   └── ... 90 entries total
├── SOUL.md                         # unchanged after migration
├── wiki/                           # unchanged
└── user-patterns.md                # unchanged
```

Synthetic journal entry:
```markdown
---
date: 2026-04-20
session-id: 2026-04-20-0900-plan-ab-decision
subject: Plan A vs Plan B decision
domains: [career, finance]
---
# Plan A vs B decision
Discussed runway trade-offs. Decided Plan B after 3 hours.
Concepts touched: runway-calculation, autonomy-vs-stability.
```

## Expected Output

```
$ uv run tools/migrate.py --from v1.6.2a --to v1.7 --dry-run --root ./fixture-brain-v162a
DRY-RUN — no files created.
Would migrate 60 journal entries (within 3-month window, 30 skipped as too old)
Would emit: 60 sessions, 18 concepts, 4 snapshots, 9 tentative methods
Exit 0

$ uv run tools/migrate.py --from v1.6.2a --to v1.7 --root ./fixture-brain-v162a
Processed 60 journal entries
Wrote 60 sessions + INDEX.md
Wrote 18 concepts + INDEX.md + SYNAPSES-INDEX.md
Wrote 4 soul snapshots
Wrote 9 tentative methods
Wrote _meta/cortex/bootstrap-status.md
Exit 0
```

## Failure Modes

- Journal entry with missing frontmatter → log to bootstrap-status, skip entry, continue; final exit 1 if any file failed
- Target `_meta/sessions/` already has content (partial prior migration) → merge, don't overwrite existing session files with same id
- `--from` != `v1.6.2a` → exit 2 with "only v1.6.2a → v1.7 supported"
- Journal entry beyond 3 months → silently skip, count in dry-run report

## Linked Documents

- `references/tools-spec.md` §6.7
- `references/session-index-spec.md` §9
- `references/concept-spec.md` §Migration
- `references/snapshot-spec.md` §Migration
- `references/method-library-spec.md` §15
- `tools/migrate.py`
- `tests/test_migrate.py`
