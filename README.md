<div align="center">

# Life OS

### A model-sovereign personal operating system with user-owned Markdown memory

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.11.0-brightgreen.svg)](CHANGELOG.md)

[English](README.md) · [中文](i18n/zh/README.md) · [日本語](i18n/ja/README.md)

</div>

Life OS helps with decisions, planning, reflection, research, knowledge, and
long-term personal context. It gives a capable runtime model freedom to choose
the method while the user keeps control of the objective, workspace, data, and
consequential actions.

`SKILL.md` is the sole universal runtime authority.

## What model sovereignty means

For each request, the model may decide:

- whether to answer directly or inspect more context;
- whether tools, Shell, CLI, applications, or connectors are useful;
- whether no agent, an existing agent template, or an ad hoc specialist is
  useful;
- how to divide work and how deeply to verify it;
- how much structure and explanation the result needs.

Life OS does not require a fixed ROUTER → PLANNER → REVIEWER pipeline, a slash
command, a status line, an audit file, or one validation runner.

This freedom applies to method, not scope. The model may not invent permission
to inspect another workspace, expose private data, publish, push, send, delete,
purchase, or perform another consequential action the user did not request.

## Persistent and conversation-only use

Full Life OS uses one explicitly bound local directory containing the user's
Markdown second-brain.

The directory does not need Git, a remote, a clean worktree, network access, or
a prescribed folder tree. Git is an optional versioning and synchronization
adapter.

Without a binding, Life OS can still analyze, plan, research, and answer in the
current conversation. It must describe that state honestly as
conversation-only and must not claim durable memory.

The Life OS development repository is not a second-brain. Neither is an
ordinary project repository merely because it uses Git.

## Start in natural language

1. Make this repository and its root `SKILL.md` available to your AI host.
2. If you want persistent work, select a local Markdown directory and state
   clearly that Life OS may bind it, including whether access is read-only or
   read/write.
3. Say what you want to accomplish.

Example:

> Use Life OS to help me compare these two options. Work only with the material
> I provide in this conversation.

Persistent example:

> Bind the local Markdown directory I selected as my read/write second-brain
> for this session. Review the project note I name and save the decision there.

The second example authorizes that scoped local persistence. It does not
authorize Git synchronization or publication.

## Agents and themes

Files under `agents/` are optional analytical templates. A model may use,
combine, adapt, or omit them, and may create a task-specific role. A simple
request should stay simple.

Files under `themes/` are optional presentation adapters. They can change
display names, tone, language, and headings. They do not change authority,
workflow, privacy, persistence, or safety.

## Evidence and completion

Verification is proportional to risk and to the claim being made. A small local
documentation edit may need a focused diff review. A migration, external
mutation, high-stakes recommendation, or release needs stronger evidence.

When material, a completion report distinguishes:

- what was observed;
- what changed;
- what was verified;
- what was not verified;
- what remains blocked or outside scope.

Generated prose, intention, or a status label is not proof of completion.

## Host support

Life OS is host-agnostic. Host adapters under `hosts/` describe available
capabilities and fallbacks; they do not change product semantics.

| Host capability | Behavior |
|---|---|
| Filesystem available | Use it for authorized local Markdown work |
| Shell or CLI available | The model may use it when useful |
| Subagents available | The model may delegate when it adds real value |
| Capability unavailable | Use another method or report the material limit |
| Host approval required | Respect the host approval without adding a second Life OS ritual |

## Repository map

| Path | Purpose |
|---|---|
| `SKILL.md` | Sole universal runtime contract |
| `hosts/` | Host capability adapters |
| `agents/` | Optional reusable perspectives |
| `themes/` | Optional presentation adapters |
| `references/` | Non-authoritative data and implementation references |
| `evals/` | Observable behavioral conformance scenarios |
| `docs/` | Current user and developer documentation |
| `docs/history/` | Superseded architecture and release evidence |

Start with [the documentation index](docs/index.md), the
[installation guide](docs/installation.md), or the
[first-session guide](docs/getting-started/first-session.md).

Existing v1.9 and v1.10 Markdown remains user-owned and readable by default.
See [MIGRATION.md](MIGRATION.md) before requesting structural changes.

## License

Life OS is licensed under the [Apache License 2.0](LICENSE).
