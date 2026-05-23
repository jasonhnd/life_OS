---
description: Generate Claude Code native Task() agent wrappers in ~/.claude/agents/ from pro/agents/*.md source files. Replaces v1.8.4 scripts/register-claude-agents.sh as part of v1.8.5 hook layer retirement.
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
---

# /install-agents

Generate wrapper agent files in `~/.claude/agents/` so Claude Code's native Task() tool can discover and launch Life OS subagents (router, retrospective, archiver, planner, reviewer, dispatcher, advisor, auditor, strategist, monitor, council, hippocampus, gwt-arbitrator, concept-lookup, soul-check, narrator-validator + 6 domain agents).

## Procedure

### 1. Locate source skill root
Check in order:
- `$CLAUDE_PLUGIN_ROOT` env var
- `./pro/agents/router.md` (current dir is repo root)
- `$HOME/.claude/skills/life_OS/pro/agents/router.md` (installed skill)
- `$HOME/.claude/skills/life-os/pro/agents/router.md` (alt name)

If none found, abort with `ERROR: Cannot locate life_OS skill root`.

### 2. Create target dir
```bash
mkdir -p "$HOME/.claude/agents"
```

### 3. For each `pro/agents/*.md` source file

```bash
ls pro/agents/*.md
```

For each file:
- Base name without extension: e.g. `router`, `archiver`
- Wrapper file path: `$HOME/.claude/agents/lifeos-<base>.md`

**Skip rule (per pro/agents/narrator.md design):**

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

### 4. Report
```
✅ Registered N lifeos-* wrappers in ~/.claude/agents/
   skipped M ROUTER-internal templates
   source: <skill root path>
```

## v1.8.5 v2 frontmatter compatibility

Per Stage 6 (21 subagent standardization), each `pro/agents/*.md` source file gets a v2 standard frontmatter with `authority_level`, `automation_mode`, `blast_radius`, `failure_modes`, etc. This slash command MUST preserve those fields when generating wrappers (just copy frontmatter verbatim, then add the `@import` line). Do NOT strip v2 fields.

## v1.8.5 changes vs v1.8.4 scripts/register-claude-agents.sh

- v1.8.4: bash awk script generates wrappers from source frontmatter
- v1.8.5: LLM reads each source via Read tool, emits wrapper via Write tool. Same output, zero bash.
