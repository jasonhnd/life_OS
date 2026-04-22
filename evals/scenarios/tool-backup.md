---
scenario: tool-backup
type: tool-invocation
tool: backup
requires_claude: false
# R4.5 machine-eval fields
setup_script: |
  mkdir -p {tmp_dir}/_meta/snapshots/soul
invocation: "python3 -m tools.backup --dry-run --root {tmp_dir}"
expected_exit_code: 0
expected_stdout_contains:
  - "dry-run"
expected_stderr_contains: []
expected_files: []
---

# Tool Scenario · backup

**Contract**: references/tools-spec.md §6.6 + references/snapshot-spec.md + references/compliance-spec.md · Snapshot rotation + violations archive.

## User Message

```
帮我把老的 SOUL snapshot 挪到 _archive/，把 3 个月前的 violations 搬到季度归档文件；先 --dry-run 给我看要做什么。
```

(English equivalent: "Rotate old SOUL snapshots to _archive/ and move 3-month-old violations to quarterly archive; show with --dry-run first.")

## Scenario

Monthly maintenance task. The tool enforces two rotation policies:

**Snapshots** (per `references/snapshot-spec.md`):
- Active: ≤ 30 days → stay in `_meta/snapshots/soul/`
- Archived: 30-90 days → move to `_meta/snapshots/soul/_archive/`
- Deleted: > 90 days → removed from filesystem (git history retains)

**Violations log** (per `references/compliance-spec.md`):
- Active: rolling 90 days in `pro/compliance/violations.md`
- Archived: > 90 days → moved to `pro/compliance/archive/YYYY-QN.md`

`--dry-run` reports intended actions without touching files.
`--snapshots-only` / `--violations-only` limit scope.

## Success Criteria

- [ ] `uv run tools/backup.py --dry-run --root <fixture>` exits 0, no files moved, logs intended actions
- [ ] Actual run moves `_meta/snapshots/soul/2026-02-20-1500.md` (60 days old) → `_meta/snapshots/soul/_archive/2026-02-20-1500.md`
- [ ] Actual run deletes `_meta/snapshots/soul/_archive/2025-12-15-0900.md` (>90 days) from filesystem (still in git log)
- [ ] Active snapshot (today -10 days) NOT moved
- [ ] Violations row with timestamp > 90 days ago → moved to `pro/compliance/archive/2026-Q1.md`, removed from active `violations.md`
- [ ] Active violation (< 90 days) NOT moved
- [ ] `--snapshots-only` skips violations processing
- [ ] `--violations-only` skips snapshot processing
- [ ] Idempotent: second run is a no-op (exits 0, no moves)
- [ ] Quarter file format: `YYYY-QN.md` (e.g., `2026-Q1.md` for Jan-Mar)

## Input Fixture

```
fixture-brain/
├── _meta/snapshots/soul/
│   ├── 2026-04-12-1400.md        # 10 days old → stays active
│   ├── 2026-02-20-1500.md        # 60 days old → move to _archive/
│   └── _archive/
│       └── 2025-12-15-0900.md    # >90 days old → delete
└── pro/compliance/
    ├── violations.md              # contains rows from 2025-12 through 2026-04
    └── archive/                   # (empty initially)
```

Synthetic rows in violations.md:

```
| 2025-12-20T10:00:00Z | 上朝 | A1 | P0 | old violation | resolved |
| 2026-04-10T09:00:00Z | 上朝 | A1 | P0 | recent one    | no       |
```

## Expected Output

```
$ uv run tools/backup.py --dry-run --root ./fixture-brain
DRY-RUN — no files changed.
Would move: _meta/snapshots/soul/2026-02-20-1500.md → _archive/
Would delete: _meta/snapshots/soul/_archive/2025-12-15-0900.md
Would archive violations row from 2025-12-20T10:00:00Z → 2026-Q1.md (1 row)
Exit 0

$ uv run tools/backup.py --root ./fixture-brain
Moved 1 snapshot to _archive/
Deleted 1 snapshot older than 90 days
Archived 1 violation row to pro/compliance/archive/2026-Q1.md
Exit 0

$ uv run tools/backup.py --root ./fixture-brain     # second run
No rotations needed. Exit 0
```

## Failure Modes

- Target `_archive/` directory missing → create it, then move
- Destination file already exists in `_archive/` (rare same-minute snapshot) → overwrite (content is deterministic per snapshot policy)
- Cannot open `violations.md` → exit 1 with clear error
- Read-only `_meta/snapshots/soul/` directory → exit 1

## Linked Documents

- `references/tools-spec.md` §6.6
- `references/snapshot-spec.md` §Rotation Policy
- `references/compliance-spec.md` §Archive Policy
- `tools/backup.py`
- `tests/test_backup.py`
