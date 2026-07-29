---
host: codex
status: capability-adapter
authoritative: false
runtime_authority: SKILL.md
---

# Codex Host Adapter

This file describes possible OpenAI Codex host capabilities. It does not define
a Life OS workflow or require Pro Mode.

## Capability Discovery

Use only tools available in the current Codex surface. They may include:

- local file reading and editing;
- Shell and CLI execution;
- web, browser, or application connectors;
- independent collaborating agents.

The repository-level `AGENTS.md` provides contributor guidance when working on
Life OS source. `SKILL.md` remains the only universal runtime authority.

## Adaptation

- Use zero, one, or multiple agents according to the task.
- Create a task-specific agent when useful; do not require a closed registry.
- Continue directly when collaboration tools are unavailable.
- Do not expose hidden reasoning or claim isolation guarantees the host does not
  provide.
- Respect Codex permission boundaries and report material capability gaps.
- Use natural language for ordinary Life OS operation.

## Persistence

Full Mode depends on an explicitly bound local Markdown second-brain. Codex
subagents, Shell, Git, and remote services are optional methods.
