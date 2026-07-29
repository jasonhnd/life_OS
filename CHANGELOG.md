# Changelog

Current release history begins with the v1.11 model-sovereignty architecture.
Earlier entries are preserved in
[`docs/history/CHANGELOG-v1.10-and-earlier.md`](docs/history/CHANGELOG-v1.10-and-earlier.md).

## [1.11.0] - 2026-07-29 - Model Sovereignty & Conformance

### Breaking changes

- `SKILL.md` is the sole universal runtime authority.
- Fixed agent chains, lifecycle stages, clarification counts, status lines,
  audit-file rituals, and command-first operation are retired.
- Existing agents are optional templates; the model may omit, combine, adapt,
  or replace them with a task-specific role.
- Retired commands, prompt workflows, ritual specifications, process evals, and
  superseded user documentation are preserved under `docs/history/`.

### Model sovereignty

- The runtime model may choose any available in-scope method, including direct
  reasoning, filesystem tools, Shell, CLI, applications, connectors, and
  optional subagents.
- Clear in-scope requests proceed without redundant Life OS confirmation.
  Material ambiguity and unrequested consequential external actions still
  require a pause.
- Verification method and depth follow risk and claim strength rather than a
  required runner or validator.

### Persistence

- Full Mode requires one explicitly bound local Markdown second-brain.
- Git is an optional history and synchronization adapter, not a readiness
  requirement.
- Conversation-Only Mode remains useful without a binding but does not claim
  durable memory.
- Start and end phrases never imply pull, commit, push, publication, deletion,
  or bulk migration.

### Compatibility and conformance

- Existing v1.9 and v1.10 Markdown remains readable without automatic
  normalization.
- Bulk migration requires explicit intent, an exact target, preview,
  preservation evidence, and verification.
- MS-01 through MS-18 replace process-prescriptive evaluation with observable
  behavioral conformance.
- English, Chinese, and Japanese current documentation describe the same
  authority, persistence, and Git-optional model.
- The complete Apache License 2.0 text is included.

Publication, tagging, and release creation remain separate explicitly
authorized actions.
