---
scenario: tool-reconcile
type: tool-invocation
tool: reconcile
requires_claude: false
# R4.5 machine-eval fields — clean empty tree => exit 0, report written.
setup_script: |
  mkdir -p {tmp_dir}/_meta/sessions {tmp_dir}/wiki {tmp_dir}/_meta/methods
invocation: "python3 -m tools.reconcile --root {tmp_dir}"
expected_exit_code: 0
expected_stdout_contains: []
expected_stderr_contains: []
expected_files_glob:
  - "{tmp_dir}/_meta/reconcile-report-*.md"
---

# Tool Scenario · reconcile

**Contract**: references/tools-spec.md §6.2 · Integrity checker (orphans, broken wikilinks, missing frontmatter, schema).

## User Message

```
请跑一下 reconcile，给我今天的完整性报告；如果有能自动修的，就加 --fix 补齐。
```

(English equivalent: "Run reconcile and give me today's integrity report; use --fix for auto-fixable cases.")

## Scenario

Second-brain in drift: user manually edited a few wiki pages, an orphan
migration left inbox items stranded, and the archiver in a past session
wrote a session file without `last_modified`. We want reconcile.py to
surface (and optionally repair) the four failure classes per spec §6.2.

User invokes from `~/second-brain`:

```bash
uv run tools/reconcile.py --verbose              # dry report
uv run tools/reconcile.py --fix                  # repair obvious cases
```

The tool MUST:
- Scan every `*.md` under the root (excluding `.git/`).
- Emit a dated `_meta/reconcile-report-{YYYY-MM-DD}.md` (same-day re-runs overwrite).
- Detect the 4 classes: orphans, broken wikilinks, missing frontmatter, schema violations.
- `--fix` handles only safe cases: insert missing `last_modified` (today), insert `id` (filename stem), move `inbox/*.md` with frontmatter to `archive/orphans/`. Never deletes.
- Exit 0 if clean or all issues fixed; exit 1 if unfixable issues remain after `--fix`.

## Success Criteria

- [ ] `uv run tools/reconcile.py --root <fixture>` with clean tree → exits 0, report has 4 sections all marked clean
- [ ] Fixture with 1 orphan + 1 broken wikilink + 1 missing frontmatter + 1 schema violation → exits 1 (unfixable remains), report lists all 4
- [ ] `--fix` on same fixture → orphan moved to `archive/orphans/`, missing `last_modified`/`id` inserted, broken wikilink still reported (cannot auto-fix), exits 1 (broken link unfixable)
- [ ] Report contains `_meta/reconcile-report-YYYY-MM-DD.md` with today's date
- [ ] Same-day re-run overwrites report (no `*-1.md` / `*-2.md` proliferation)
- [ ] No file deleted by `--fix`
- [ ] Report uses markdown table with columns: `file | issue | auto_fixable | details`

## Input Fixture

```
fixture-brain/
├── inbox/orphan-idea.md            # has frontmatter but never linked
├── wiki/negotiation-jp.md          # contains [[missing-target]] broken link
├── _meta/sessions/bad-session.md   # no last_modified field
└── _meta/methods/new-method.md     # frontmatter present but missing `id`
```

## Expected Output

```
$ uv run tools/reconcile.py --verbose --root ./fixture-brain
INFO: Scanning markdown files (4 discovered)
WARN: orphan: inbox/orphan-idea.md (has frontmatter, not linked from canonical location)
WARN: broken wikilink: wiki/negotiation-jp.md → [[missing-target]]
WARN: missing frontmatter key: _meta/sessions/bad-session.md (last_modified)
WARN: schema violation: _meta/methods/new-method.md (id required)
Wrote _meta/reconcile-report-2026-04-22.md
Exit 1 (4 issues, 0 auto-fixable without --fix)

$ uv run tools/reconcile.py --fix --root ./fixture-brain
INFO: Moved inbox/orphan-idea.md → archive/orphans/orphan-idea.md
INFO: Inserted last_modified=2026-04-22 into _meta/sessions/bad-session.md
INFO: Inserted id=new-method into _meta/methods/new-method.md
WARN: broken wikilink still unfixable: wiki/negotiation-jp.md → [[missing-target]]
Exit 1 (1 issue remaining: broken wikilink)
```

## Failure Modes

- `.git/` traversal would waste time → implementation must skip it
- Concurrent runs (e.g. user re-triggers) — second run reads first run's mid-write state → atomic write (tmp + rename)
- Non-UTF-8 file → log + skip that file, don't abort whole scan

## Linked Documents

- `references/tools-spec.md` §6.2
- `tools/reconcile.py`
- `tests/test_reconcile.py`
