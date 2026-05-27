# WHEN NOT TO ADD to `pro/agents/`

> **Intentionally near-empty principle**: this directory is for **subagent definitions** only. Each `*.md` here defines a Task-spawnable role with v2 agent-spec frontmatter. Adding non-agent files dilutes the directory and misleads ROUTER's role discovery.

## What does NOT belong here

1. **Generic helpers / utility prompts** — e.g. "a markdown that helps me draft commit messages". → Goes to: `.claude/commands/` (slash commands) or `scripts/prompts/` (maintenance prompts).
2. **Spec / schema documents** — e.g. "definition of what an audit trail file looks like". → Goes to: `references/<topic>-spec.md`.
3. **Reference docs for users** — e.g. "how to use the auditor agent". → Goes to: `docs/` or `gitbooks/` (when reintroduced).
4. **Per-session state, audit trails, gotchas** — e.g. "this session's archiver output". → Goes to: `meta/runtime/<sid>/` (audit trails) or `pro/gotchas.md` (lessons learned).
5. **Theme files (display names / emoji / tone)** — e.g. "a new theme for medieval setting". → Goes to: `themes/<name>.md`.
6. **An agent without v2 agent-spec frontmatter** — even if it's a legitimate role, it MUST conform to `references/agent-spec.md` v2 (6 facets + operating_hypothesis + context_manifest + blast_radius + failure_modes) before landing here.

## What DOES belong here

A subagent definition that is:
- Task-spawnable (Claude Code can launch via `Task(<name>)`)
- Has a unique, non-overlapping responsibility (check against existing 22 agents in this directory)
- Has v2 agent-spec frontmatter complete
- Has clear blast radius (declares what files it may and may NOT write)
- Has documented failure modes + recovery actions

## Before adding a new agent — Minimality Rule check

Per `pro/CLAUDE.md` Minimality Rule (v1.8.5 Stage 7), ask the 6 questions first:

1. Could a **rule** (in `pro/CLAUDE.md`) accomplish this?
2. Could a **schema field** (in `references/*-spec.md` frontmatter) accomplish this?
3. Could a **validator** (slash command or AUDITOR mode) accomplish this?
4. Could a **regression case** (`evals/scenarios/*.md`) accomplish this?
5. Could a **stop condition** (in an existing agent's execution flow) accomplish this?
6. Could a **human checklist** (added to relevant doc) accomplish this?

If ANY answer is yes, prefer that lower-cost option. New agent = expensive (forever maintenance, AUDITOR target, theme name in 9 themes, three-language spec, audit trail schema, blast radius enforcement). The cost-benefit threshold is high.

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- Pattern source: `tinyhumansai/openhuman` `.claude/rules/README.md` ("This directory is intentionally near-empty. Stale rules actively mislead agents.")
- Companion spec: `references/agent-spec.md` (v2 frontmatter standard)
