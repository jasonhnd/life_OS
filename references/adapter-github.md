---
title: Optional Git Adapter
status: reference
authoritative: false
runtime_authority: SKILL.md
introduced_in: v1.11.0
---

# Optional Git Adapter

> [!info] Optional capability
> A local Markdown second-brain is complete without Git. This reference applies
> only when the user has explicitly bound a local directory and Git is relevant
> to the authorized task.

## Purpose

Git may provide:

- version history;
- human-readable diffs;
- rollback evidence;
- synchronization through a user-selected remote;
- conflict detection across devices or work sessions.

Git is not:

- the identity of a second-brain;
- a Full Mode prerequisite;
- an automatic session-start or session-end action;
- proof that a local write succeeded;
- permission to send local data to a remote.

## Activation

Use this adapter only when at least one is true:

- the user explicitly requests a Git action;
- the current development task clearly includes normal repository operations;
- the user has previously approved Git-based synchronization for the bound
  second-brain and the current request includes synchronization.

Do not infer remote-sync authorization from `start`, `save`, `done`, `end`, or
`adjourn`.

## Local Operations

The model may inspect or use Git with available host tools. It chooses the
specific commands based on repository state and the requested outcome.

Useful evidence may include:

- current branch and worktree state;
- scoped diff;
- exact files changed;
- commit identity;
- ahead/behind state;
- remote operation result.

No fixed command sequence is required.

## Scoped Changes

- Keep Git actions inside the authorized repository.
- Resolve exact targets before destructive operations.
- Do not stage unrelated user files.
- Do not use a broad staging operation when it could include unrelated or
  sensitive content.
- Preserve pre-existing worktree changes.
- Do not rewrite history, force-push, delete branches, or discard changes
  unless that exact action is authorized.

## Commits

A local commit is a distinct action from a local file write.

- Create a commit when the request includes committing or when it is clearly
  part of the authorized development workflow.
- Describe the actual change.
- Include only reviewed, in-scope files.
- Do not treat a commit as remote publication.

## Remotes

A remote operation can transmit local content outside the machine.

- Push, publish, fork, release, and remote creation require matching user
  intent.
- Use the exact approved repository and branch.
- Report whether the remote mutation actually succeeded.
- A failed or unavailable remote does not invalidate local Markdown
  persistence.

## Conflicts

When Git exposes a conflict:

- inspect the conflicting content;
- preserve both sides until the intended result is understood;
- resolve directly when evidence is sufficient and the resolution is in scope;
- ask the user when the semantic choice is material or ambiguous;
- verify the repository no longer contains unresolved conflict markers before
  claiming completion.

## Non-Git Fallback

When Git is absent or irrelevant:

- continue using the bound local Markdown directory;
- use proportionate filesystem evidence for writes and migrations;
- report that Git history or remote synchronization was not used;
- do not label Life OS as degraded solely for that reason.
