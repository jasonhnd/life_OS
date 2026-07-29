---
host: gemini
status: capability-adapter
authoritative: false
runtime_authority: SKILL.md
---

# Gemini Host Adapter

This file describes possible Gemini or Antigravity host capabilities. It does
not define a Life OS workflow.

## Capability Discovery

Use only capabilities exposed by the current environment. These may include:

- local file reading and editing;
- search and shell execution;
- browser or workspace tools;
- agent or task delegation.

Do not assume parity with Claude, Codex, or another Gemini installation.

## Adaptation

- Perform work directly when delegation is unavailable or unnecessary.
- Adapt optional agent templates to the host's native mechanism.
- Do not simulate process isolation or tool evidence the host did not provide.
- Respect host permissions and surface material limitations.
- Keep natural language as the primary Life OS interface.

## Persistence

Full Mode depends on an explicitly bound local Markdown second-brain. Gemini
commands, Git, a remote, and subagents are optional capabilities.
