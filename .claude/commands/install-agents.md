---
description: Generate Claude Code native Task() agent wrappers in ~/.claude/agents/ from agents/*.md source files, and install slash command specs to ~/.claude/commands/. Replaces v1.8.4 scripts/register-claude-agents.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[--refresh]  (re-install agents + slash commands; idempotent, run after git pull)"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
---

# /install-agents

Generate wrapper agent files in `~/.claude/agents/` so Claude Code's native Task() tool can discover and launch Life OS subagents (router, retrospective, archiver, planner, reviewer, dispatcher, advisor, auditor, strategist, monitor, council, hippocampus, gwt-arbitrator, concept-lookup, soul-check + 6 domain agents). (narrator-validator was removed in v1.8.0 R-1.8.0-011 — citation discipline is now inline in narrator; the `ls agents/*.md` glob below never emits it.)

## Procedure

### 1. Locate source skill root
Check in order:
- `$CLAUDE_PLUGIN_ROOT` env var
- `./agents/router.md` (current dir is repo root)
- `$HOME/.claude/skills/life_OS/agents/router.md` (installed skill)
- `$HOME/.claude/skills/life-os/agents/router.md` (alt name)

If none found, abort with `ERROR: Cannot locate life_OS skill root`.

### 2. Create target dir
```bash
mkdir -p "$HOME/.claude/agents"
```

### 3. For each `agents/*.md` source file

```bash
ls agents/*.md
```

For each file:
- Base name without extension: e.g. `router`, `archiver`
- Wrapper file path: `$HOME/.claude/agents/lifeos-<base>.md`

**Skip rule (per agents/narrator.md design):**

If source file frontmatter contains `type: router-internal-template`, skip it (it's a ROUTER-internal template, not a Task-spawnable subagent). Emit `skip <base> (ROUTER-internal template, not Task-spawnable)`.

**Wrapper content:**

The wrapper is a thin import that points at the source file. Format:

```markdown
---
name: lifeos-<base>
description: <copy 'description:' from source file frontmatter, or use base name if absent>
---

@<absolute path to source file>
```

The `@` import lets Claude Code load the full source content at Task() launch time.

### 4. Install slash command specs (to `~/.claude/commands/`)

So `/run-eval`, `/check-spec-drift`, `/verify-release`, `/verify-release-and-watch`, `/version-check`, etc. are discoverable:
```bash
mkdir -p "$HOME/.claude/commands"
```
For each `*.md` under `.claude/commands/` AND `scripts/commands/` (e.g. `compress.md`, `monitor.md`) in the skill root, copy it to `$HOME/.claude/commands/<base>.md` (overwrite — install is idempotent).

**`--refresh`**: if `$ARGUMENTS` contains `--refresh`, this is a re-install — regenerate ALL agent wrappers (step 3) and re-copy ALL slash command specs (this step), overwriting existing ones. Run it after `git pull` to pick up new or changed agents and commands.

### 4.5 Legacy hook cleanup (v1.10.0 · retire-for-real, issue #2)

The bash hook layer was retired in v1.8.5, but machines that upgraded from ≤v1.8.4 may still carry live hook files and `settings.json` registrations — sometimes the SAME hook registered at two paths (legacy + current), causing double execution or divergent guard versions. This step makes the retirement real on installed machines. It runs on EVERY invocation (with or without `--refresh`) and is idempotent.

1. **Enumerate**: Read `$HOME/.claude/settings.json`. Collect every hook registration (under `hooks.PreToolUse` / `hooks.PostToolUse` / `hooks.UserPromptSubmit` / `hooks.SessionStart` / `hooks.Stop`) whose command string matches any of:
   - `lifeos-` (e.g. `lifeos-pre-prompt-guard.sh`, `lifeos-version-check.sh`)
   - `scripts/hooks/` under `.claude/` or `skills/life_OS/` (e.g. `pre-bash-approval.sh`, `session-start-inbox.sh`, `post-task-audit-trail.sh`)
   - `setup-hooks.sh`
2. **Correct end state is ZERO lifeos hook registrations** — the layer is retired, not relocated. There is no "keep one canonical copy" path.
3. If any registrations found:
   - Print the full list (event, matcher, command path) — never remove silently.
   - Ask ONE confirmation: "Remove these N legacy lifeos hook registrations + their script files? (y/n)"
   - On yes: rewrite `settings.json` without those entries (preserve all non-lifeos hooks byte-for-byte), then delete the orphaned script files: `$HOME/.claude/scripts/hooks/*` lifeos-originated scripts, `$HOME/.claude/scripts/lifeos-*.sh`, `$HOME/.claude/skills/life_OS/scripts/hooks/` leftovers. Only delete files that are actually referenced by the removed registrations or match `lifeos-*.sh` — do NOT touch user-authored hooks.
   - On no: report `⚠️ legacy hooks left in place (user choice) — /version-check will keep warning` and continue with installation.
4. **Report removals explicitly** in the step 5 report (see below): one line per removed registration + one line per deleted file. Silent removal is a violation of this spec.
5. Remind the user: settings.json changes take effect on the next Claude Code session restart.
6. Idempotency check: re-running this command immediately after cleanup MUST report `0 legacy hook registrations found`.

### 5. Report
```
✅ Registered N lifeos-* wrappers in ~/.claude/agents/
   installed K slash commands in ~/.claude/commands/
   skipped M ROUTER-internal templates
   legacy hooks: removed R registrations + F script files (listed below) / 0 found ✅ / left in place (user choice) ⚠️
   [one line per removed registration: <event> · <command path>]
   [one line per deleted file: <path>]
   source: <skill root path>
```

## v1.8.5 v2 frontmatter compatibility

Per Stage 6 (subagent frontmatter standardization), each `agents/*.md` source file gets a v2 standard frontmatter with `authority_level`, `automation_mode`, `blast_radius`, `failure_modes`, etc. This slash command MUST preserve those fields when generating wrappers (just copy frontmatter verbatim, then add the `@import` line). Do NOT strip v2 fields.

## v1.8.5 changes vs v1.8.4 scripts/register-claude-agents.sh

- v1.8.4: bash awk script generates wrappers from source frontmatter
- v1.8.5: LLM reads each source via Read tool, emits wrapper via Write tool. Same output, zero bash.
