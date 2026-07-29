---
host: claude
status: capability-adapter
authoritative: false
runtime_authority: SKILL.md
---

# Claude Host Adapter

This file describes possible Claude host capabilities. It does not define a
Life OS workflow.

## Capability Discovery

Use only capabilities actually exposed by the current Claude environment.
Depending on the product and configuration, these may include:

- local file reading and editing;
- search and shell execution;
- browser or connector access;
- independent subagents;
- scheduled wakeups or host commands.

Do not require a capability merely because another Claude environment supports
it.

## Adaptation

- Handle work directly when subagents are unavailable or unnecessary.
- Treat installed agent definitions and slash commands as optional
  conveniences.
- Use genuine host isolation when available; do not promise isolation when it
  is not.
- Apply host confirmation and permission prompts without adding a second Life
  OS confirmation ritual.
- Use natural language for ordinary Life OS operation.
- Report material capability gaps when they affect the requested result.

## Persistence

Full Mode depends on an explicitly bound local Markdown second-brain, not on
Claude-specific commands, wrappers, hooks, Git, or a remote.
