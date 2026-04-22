---
scenario: tool-seed
type: tool-invocation
tool: seed
requires_claude: false
# R4.5 machine-eval fields — target path must NOT exist yet (seed creates it).
# --no-git lets this run in environments where git isn't configured.
setup_script: |
  # Target dir must NOT exist — seed will create it fresh.
  mkdir -p {tmp_dir}
invocation: "python3 -m tools.seed --path {tmp_dir}/newbrain --no-git"
expected_exit_code: 0
expected_stdout_contains: []
# seed.py logs to stderr (tools/seed.py:_configure_logging).
expected_stderr_contains:
  - "Seeded"
expected_files:
  - "{tmp_dir}/newbrain/SOUL.md"
  - "{tmp_dir}/newbrain/.life-os.toml"
  - "{tmp_dir}/newbrain/.gitignore"
---

# Tool Scenario · seed

**Contract**: references/tools-spec.md §6.10 · New-user second-brain bootstrap.

## User Message

```
帮新用户在 ~/second-brain 建一个空的 v1.7 second-brain：SOUL 骨架、.life-os.toml、.gitignore、_meta/ 树、git init，然后告诉我哪些文件创建了。
```

(English equivalent: "Bootstrap a new empty v1.7 second-brain at ~/second-brain: SOUL skeleton, .life-os.toml, .gitignore, _meta/ tree, git init; report which files were created.")

## Scenario

First-time setup for a new Life OS user. The tool creates an
empty-but-valid second-brain layout at the target path, then runs
`git init` + an initial commit so the user can start tracking from
day one.

Created files (per spec §6.10):
- `SOUL.md` skeleton with all v1.7 dimension placeholders
- `.life-os.toml` stub (minimal)
- `.gitignore` with recommended ignore list
- Example project under `projects/` to show the expected shape
- `_meta/` directory tree:
  - `sessions/`, `concepts/`, `snapshots/soul/`, `dreams/`,
    `eval-history/`, `methods/`, `projects/`, `outbox/`
  - each seeded with `.gitkeep` so git picks them up
- Initial git commit: "feat: initial Life OS v1.7 second-brain"

Idempotency: target path already exists AND non-empty → exit 1
(refuse to overwrite, no destructive behavior).

## Success Criteria

- [ ] `uv run tools/seed.py --path <empty-dir>` exits 0
- [ ] Target contains `SOUL.md`, `.life-os.toml`, `.gitignore` at root
- [ ] `_meta/` tree has all 8 subdirectories, each with `.gitkeep`
- [ ] `projects/example/` exists with skeleton files
- [ ] `git log` shows one initial commit
- [ ] `git status` shows a clean working tree
- [ ] Target path already has content → exits 1, nothing modified
- [ ] Target path does not exist → creates it, exits 0
- [ ] `--path` missing → exit 2 with "required flag"
- [ ] `.gitignore` includes `__pycache__/`, `.DS_Store`, `.venv/`, etc. per spec
- [ ] `SOUL.md` is minimal YAML (no fake evidence — empty dimensions)

## Input Fixture

N/A — the scenario creates everything from scratch. Test uses a
temporary directory via `tmp_path`.

Pre-conditions:
- `git` binary on PATH
- Target path empty or non-existent

## Expected Output

```
$ uv run tools/seed.py --path /tmp/new-brain
INFO: Creating /tmp/new-brain
INFO: Wrote SOUL.md
INFO: Wrote .life-os.toml
INFO: Wrote .gitignore
INFO: Wrote projects/example/ skeleton
INFO: Created _meta/ directory tree (8 subdirs × .gitkeep)
INFO: git init
INFO: git add .
INFO: git commit -m "feat: initial Life OS v1.7 second-brain"
Second-brain bootstrapped at /tmp/new-brain
Exit 0

$ cd /tmp/new-brain && ls -la
drwxr-xr-x  SOUL.md
drwxr-xr-x  .life-os.toml
drwxr-xr-x  .gitignore
drwxr-xr-x  projects/
drwxr-xr-x  _meta/

$ cd /tmp/new-brain && git log --oneline
1a2b3c4 feat: initial Life OS v1.7 second-brain
```

**Refuse to overwrite:**
```
$ echo "existing" > /tmp/not-empty/file.md
$ uv run tools/seed.py --path /tmp/not-empty
ERROR: target path /tmp/not-empty is not empty — refusing to overwrite
Exit 1
```

## Failure Modes

- `git` binary not on PATH → exit 1 with clear "git required" message
- Target path permission denied → exit 1 with OSError detail
- Disk full mid-write → partial tree left, exit 1; user can rm + retry
- `git init` succeeds but `git commit` fails (e.g., no user.email) → exit 1 with hint to run `git config`

## Linked Documents

- `references/tools-spec.md` §6.10
- `references/SOUL-template.md` (skeleton source)
- `tools/seed.py`
- `tests/test_seed.py`
