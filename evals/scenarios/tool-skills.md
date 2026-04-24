---
scenario: tool-skills
type: tool-invocation
tool: skills
requires_claude: false
docs_only: true
future_runner: true
# Life OS 1.7.1 Docs Round 2 D2.2: future machine-eval contract.
# Runner MUST NOT execute until the Skill Observability CLI is implemented.
setup_script: |
  set -eu
  export HOME="{tmp_dir}/home"
  export LIFE_OS_SKILLS_DIR="$HOME/.claude/skills"
  export LIFE_OS_PLUGINS_DIR="$HOME/.claude/plugins"
  mkdir -p "$LIFE_OS_SKILLS_DIR/imagegen"
  mkdir -p "$LIFE_OS_SKILLS_DIR/openai-docs"
  mkdir -p "$LIFE_OS_SKILLS_DIR/broken-skill"
  mkdir -p "$LIFE_OS_SKILLS_DIR/local-only"
  mkdir -p "$LIFE_OS_PLUGINS_DIR/imagegen"
  mkdir -p "$HOME/.cache/life-os"

  cat > "$LIFE_OS_SKILLS_DIR/imagegen/SKILL.md" <<'EOF'
  ---
  name: imagegen
  version: 1.2.0
  installed-at: 2026-04-20T10:00:00+09:00
  source: skills://imagegen
  description: Generate or edit raster images for Life OS work products.
  triggers:
    - image
    - edit picture
    - create illustration
    - mockup
  ---
  # imagegen
  EOF

  cat > "$LIFE_OS_SKILLS_DIR/openai-docs/SKILL.md" <<'EOF'
  ---
  name: openai-docs
  version: 0.9.0
  installed-at: 2026-04-10T10:00:00+09:00
  source: skills://openai-docs
  description: Use official OpenAI documentation for API and model questions.
  triggers:
    - OpenAI API
    - docs
    - model
    - prompt migration
  ---
  # openai-docs
  EOF

  cat > "$LIFE_OS_SKILLS_DIR/broken-skill/SKILL.md" <<'EOF'
  ---
  name: broken-skill
  version: 0.0.1
  installed-at: 2026-04-18T10:00:00+09:00
  source: registry://timeout.example/broken-skill
  description: Fixture whose upstream check times out gracefully.
  triggers:
    - broken
    - timeout
    - diagnose
    - recover
  ---
  # broken-skill
  EOF

  cat > "$LIFE_OS_SKILLS_DIR/local-only/SKILL.md" <<'EOF'
  ---
  name: local-only
  version: 0.1.0
  installed-at: 2025-12-15T10:00:00+09:00
  source: local
  description: Local-only fixture with no upstream cache entry.
  triggers:
    - start
    - 上朝
    - begin
    - local ceremony
  ---
  # local-only
  EOF

  # Duplicate plugin fixture exercises source priority shadowing.
  cat > "$LIFE_OS_PLUGINS_DIR/imagegen/SKILL.md" <<'EOF'
  ---
  name: imagegen
  version: 0.8.0
  installed-at: 2026-04-01T10:00:00+09:00
  source: plugins://imagegen
  description: Shadowed plugin copy that must not override skills://imagegen.
  triggers:
    - plugin image
    - legacy image
    - raster
  ---
  # imagegen plugin copy
  EOF

  cat > "$HOME/.cache/life-os/skills-upstream.json" <<'EOF'
  {
    "cache_path": "~/.cache/life-os/skills-upstream.json",
    "generated_at": "2026-04-22T10:00:00+09:00",
    "skills": {
      "imagegen": {
        "latest": "1.2.0",
        "fetched_at": "2026-04-22T10:00:00+09:00",
        "result": "success"
      },
      "openai-docs": {
        "latest": "1.0.0",
        "fetched_at": "2026-04-22T10:00:00+09:00",
        "result": "success"
      },
      "broken-skill": {
        "latest": null,
        "fetched_at": "2026-01-14T10:00:00+09:00",
        "result": "expired",
        "last_error": "timeout"
      }
    }
  }
  EOF
invocation: "life-os-tool skills list --format markdown --offline"
expected_exit_code: 2
expected_stdout_contains:
  - "name | version | installed-at | source | upstream-latest | status | triggers-hint"
  - "imagegen | 1.2.0 | 2026-04-20T10:00:00+09:00 | github://alchaincyf/huashu-design | ? (cached 2d ago) | ❓ check failed | image, edit picture, create illustration"
  - "openai-docs | 0.9.0 | 2026-04-10T10:00:00+09:00 | npm://openai-docs | ? (cached 2d ago) | 🟡 update available | OpenAI API, docs, model"
  - "broken-skill | 0.0.1 | 2026-04-18T10:00:00+09:00 | pypi://broken-skill | ? (cached 100d ago) | ❓ check failed | broken, timeout, diagnose"
  - "local-only | 0.1.0 | 2025-12-15T10:00:00+09:00 | local | - | 🔴 stale (>90 days) | start, 上朝, begin"
expected_stderr_contains: []
expected_files: []
---

# Tool Scenario: skills

**Contract**: Skill Observability CLI for Life OS 1.7.1 D2.2. This is a docs-only future-runner scenario until `life-os-tool skills` exists.

## User Message

```text
Show me installed Life OS skills, whether they are current, updateable, stale, or check-failed, and enough trigger hints to know when each skill should activate. Do this as a tool-only observability command, not through ROUTER or Cortex.
```

## Commands

The CLI exposes exactly these skill observability commands:

```bash
life-os-tool skills list
life-os-tool skills check
life-os-tool skills info <name>
life-os-tool skills stale
```

Common arguments for every command:

```bash
--format {markdown,json}   # default: markdown
--offline                  # never performs network calls
```

## Output Contract

Markdown list-like output MUST use this stable column set:

```markdown
name | version | installed-at | source | upstream-latest | status | triggers-hint
```

Required field semantics:

- `installed-at` comes from `SKILL.md` frontmatter. If missing, use file mtime. If neither is available, mark the baseline as `?`.
- `upstream-latest` uses `~/.cache/life-os/skills-upstream.json` as the only cache path.
- `--offline` preserves column parity with online output. When the latest version cannot be confirmed online, `upstream-latest` MUST show either `? (cached Xd ago)` or `? (no cache)`.
- `triggers-hint` is the comma-separated first 3 trigger strings from frontmatter, for example `start, 上朝, begin`.
- If the same skill exists in `~/.claude/skills/` and `~/.claude/plugins/`, the `skills/` copy wins. The plugin copy is still reported as `(shadowed by skills://<id>)`.

Status strings used by this scenario:

```text
🟢 current / local
🟡 update available
🔴 stale (>90 days)
❓ check failed
```

`❓ check failed` is an observability status, not a data-corruption exit code. A 5s-per-skill timeout marks only the affected skill as `❓ check failed` and the command continues gracefully.

## Exit Code Contract

Semantic exit codes are status-oriented and aggregate by priority `3 > 2 > 1 > 0`:

```text
0 ok/no update
1 update available
2 stale (>90 days)
3 data source corrupt/unparseable
```

Important negative contract:

- Exit `1` means update available only.
- Exit `2` means stale `>90 days` only.
- Exit `3` means corrupt or unparseable data source only.
- Timeout, missing cache, and offline uncertainty are represented in output status/columns, not by exit `3`.

## Reproducible Fixture

The `setup_script` creates four installed skill fixtures under `~/.claude/skills/`, each with `SKILL.md` frontmatter containing `name`, `version`, `installed-at`, `source`, `description`, and `triggers`:

```text
~/.claude/skills/
|-- imagegen/SKILL.md       # current; upstream cache success
|-- openai-docs/SKILL.md    # update available; upstream cache success
|-- broken-skill/SKILL.md   # registry timeout; graceful check failed
`-- local-only/SKILL.md     # installed >90 days ago; no cache entry
```

The fixture also creates a duplicate plugin skill:

```text
~/.claude/plugins/imagegen/SKILL.md
```

Because `~/.claude/skills/imagegen/SKILL.md` also exists, the plugin copy MUST be marked `(shadowed by skills://imagegen)`.

The fake upstream cache is written to:

```text
~/.cache/life-os/skills-upstream.json
```

It covers:

- Success/current: `imagegen` latest `1.2.0`.
- Success/update available: `openai-docs` latest `1.0.0` while installed version is `0.9.0`.
- Expired check data: `broken-skill` has an old cached timeout result, producing `? (cached 100d ago)` and `❓ check failed`.
- Missing/no-cache: `local-only` is absent from the cache, producing `? (no cache)`.

## Expected Output Examples

```bash
$ life-os-tool skills list --format markdown --offline
cache: ~/.cache/life-os/skills-upstream.json
| name | version | installed-at | source | upstream-latest | status | triggers-hint |
|---|---:|---|---|---|---|---|
| imagegen | 1.2.0 | 2026-04-20T10:00:00+09:00 | skills://imagegen | 1.2.0 (cached 2d ago) | 🟢 current / local | image, edit picture, create illustration |
| openai-docs | 0.9.0 | 2026-04-10T10:00:00+09:00 | skills://openai-docs | 1.0.0 (cached 2d ago) | 🟡 update available | OpenAI API, docs, model |
| broken-skill | 0.0.1 | 2026-04-18T10:00:00+09:00 | registry://timeout.example/broken-skill | ? (cached 100d ago) | ❓ check failed | broken, timeout, diagnose |
| local-only | 0.1.0 | 2025-12-15T10:00:00+09:00 | local | ? (no cache) | 🔴 stale (>90 days) | start, 上朝, begin |
| imagegen | 0.8.0 | 2026-04-01T10:00:00+09:00 | plugins://imagegen | ? (no cache) | (shadowed by skills://imagegen) | plugin image, legacy image, raster |
Exit 2
```

```bash
$ life-os-tool skills check --format markdown
cache: ~/.cache/life-os/skills-upstream.json
imagegen: 🟢 current / local
openai-docs: 🟡 update available
broken-skill: ❓ check failed
local-only: 🔴 stale (>90 days)
Exit 2
```

```bash
$ life-os-tool skills info openai-docs --format json --offline
{
  "name": "openai-docs",
  "version": "0.9.0",
  "installed-at": "2026-04-10T10:00:00+09:00",
  "source": "skills://openai-docs",
  "upstream-latest": "1.0.0 (cached 2d ago)",
  "status": "🟡 update available",
  "triggers-hint": "OpenAI API, docs, model",
  "cache_path": "~/.cache/life-os/skills-upstream.json"
}
Exit 1
```

```bash
$ life-os-tool skills stale --format markdown --offline
cache: ~/.cache/life-os/skills-upstream.json
| name | version | installed-at | source | upstream-latest | status | triggers-hint |
|---|---:|---|---|---|---|---|
| local-only | 0.1.0 | 2025-12-15T10:00:00+09:00 | local | ? (no cache) | 🔴 stale (>90 days) | start, 上朝, begin |
Exit 2
```

## Success Criteria

- [ ] `life-os-tool skills list --format markdown --offline` exits `2` for this fixture because stale status outranks update status.
- [ ] `life-os-tool skills list --format json --offline` exits `2` and emits semantic equivalents of `name`, `version`, `installed-at`, `source`, `upstream-latest`, `status`, and `triggers-hint`.
- [ ] `life-os-tool skills check --format markdown` enforces the 5s-per-skill timeout and marks timeout results as `❓ check failed` without exiting `3`.
- [ ] `life-os-tool skills info imagegen --format markdown --offline` exits `0` and reports `🟢 current / local`.
- [ ] `life-os-tool skills info openai-docs --format markdown --offline` exits `1` and reports `🟡 update available`.
- [ ] `life-os-tool skills info local-only --format markdown --offline` exits `2` and reports `🔴 stale (>90 days)`.
- [ ] `life-os-tool skills stale --format markdown --offline` preserves the same columns as `list` and returns stale rows using offline cache semantics.
- [ ] A malformed `~/.cache/life-os/skills-upstream.json` exits `3` because the data source is corrupt/unparseable.
- [ ] A timeout or missing cache never exits `3`; it yields `❓ check failed`, `? (cached Xd ago)`, or `? (no cache)` as appropriate.
- [ ] Shadowing is deterministic: `~/.claude/skills/imagegen/SKILL.md` wins over `~/.claude/plugins/imagegen/SKILL.md`, and the plugin copy is marked `(shadowed by skills://imagegen)`.
- [ ] The CLI is observability-only: no ROUTER step is invoked, no Cortex Step 0.5 is invoked, no narrator Step 7.5 is invoked, and no subagent is spawned.
- [ ] The CLI does not read from or write to `_meta/sessions/`.

## Failure Modes

- Missing skill root directory: print an empty table, exit `0`.
- Missing `installed-at`: use `SKILL.md` file mtime as the staleness baseline.
- Missing `installed-at` and unavailable file mtime: mark the baseline `?`.
- Upstream request timeout: after 5s for that skill, mark `❓ check failed`, continue, and do not exit `3`.
- Missing upstream cache in `--offline`: preserve output columns and show `? (no cache)`.
- Corrupt or unparseable `SKILL.md` frontmatter or upstream cache JSON: exit `3`.

## Non-Integration Assertions

- [ ] No ROUTER, PLANNER, REVIEWER, DISPATCHER, domain agent, AUDITOR, ADVISOR, hippocampus, concept-lookup, soul-check, GWT, narrator, or narrator-validator component is invoked.
- [ ] No `[COGNITIVE CONTEXT]` block is constructed.
- [ ] No Start-Session, retrospective, archive, or summary flow is triggered.
- [ ] No files are written under `_meta/sessions/`.
- [ ] `_meta/sessions/INDEX.md` is not read as a dependency for skill status.

## Implementation Note

`evals/fixtures/skills-test-setup.sh` is a Round 10 implementation target for turning the `setup_script` into a reusable fixture. For Round 2 D2.2, this file is the docs contract only.

## Linked Documents

- `SKILL.md`
- `pro/AGENTS.md`
- `references/tools-spec.md` (future Skill Observability CLI section)
- `evals/scenarios/tool-*.md`
