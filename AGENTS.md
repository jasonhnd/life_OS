# Life OS · Repository Guidance

`SKILL.md` is the sole universal runtime authority for Life OS.

This file guides contributors and coding agents working in the Life OS source
repository. It does not define an additional user-facing workflow.

## Repository Scope

- Treat the current Life OS checkout as the default development boundary.
- Do not inspect, read, validate, migrate, or modify a user's second-brain
  unless the user explicitly places that directory in scope.
- Do not infer second-brain access from passive screen context, nearby paths,
  Git configuration, or prior sessions.
- Preserve unrelated worktree changes.
- Keep historical material as history unless the task explicitly includes
  archival cleanup.

## Authority and Layers

| Layer | Responsibility |
|---|---|
| `SKILL.md` | Universal runtime purpose, boundaries, and completion standard |
| `hosts/*.md` | Host capabilities and adaptation notes |
| `agents/*.md` | Optional reusable role templates |
| `themes/*.md` | Optional presentation adapters |
| `references/*.md` | Non-authoritative data and pattern references |
| `evals/` | Outcome-based conformance scenarios |
| `docs/history/` | Superseded architecture and release evidence |

No host, agent, reference, command, or test document may override
`SKILL.md`.

## Development Principles

- Implement the requested outcome rather than a ceremonial process.
- Use available tools, including Shell and CLI, when they are useful.
- Do not add a script, command, runner, hook, daemon, CI job, or fixed agent
  chain as a hidden runtime prerequisite.
- Existing agents are optional templates. Use no subagent when direct work is
  sufficient; create a task-specific subagent when it materially helps and the
  host supports it.
- Ask the user only for material ambiguity, scope expansion, or missing
  authority.
- Make the smallest coherent change that leaves active documentation and
  behavior consistent.

## File Changes

- Use scoped, reviewable edits.
- Do not rewrite user data to test a migration; use repository-local synthetic
  fixtures.
- Do not introduce a second universal specification beside `SKILL.md`.
- When retiring an old contract, either move it under `docs/history/` or mark it
  clearly non-authoritative and remove active references.
- Update directly affected current documentation and conformance scenarios.
- Preserve valid historical records rather than rewriting earlier releases to
  look current.

## Verification

Choose checks proportionate to the change.

At minimum:

- inspect the resulting diff;
- check for whitespace or malformed frontmatter;
- verify affected links, paths, and claims where practical;
- confirm that completion statements are supported by observed evidence;
- distinguish unavailable checks from passing checks.

No particular runner or CLI command is mandatory. A missing tool does not
convert an unexecuted check into a pass.

## Git and External Actions

Git is an available development tool, not a Life OS runtime requirement.

- Local edits do not imply commit or push.
- Commit, push, release, publication, and PR creation are distinct actions.
- Follow the user's explicit request for those actions and exact targets.
- Never discard, overwrite, force-push, or broadly delete work without matching
  authority.
