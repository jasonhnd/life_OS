---
id: MS-11
title: Bound Markdown second-brain without Git
status: current
---

# MS-11 · Bound Markdown second-brain without Git

## Synthetic setup

Create an isolated temporary directory containing Markdown and no `.git`
directory. Explicitly bind it for the scenario and request one local save.

## Observable requirements

- The binding is recognized as Full Mode.
- The requested Markdown write succeeds inside the bound directory.
- Missing Git, remote, or network access is reported separately and does not
  block persistence.
- No remote operation occurs.

## Valid variation

Any proportionate local filesystem method may establish the write.

## Fail examples

Requiring repository initialization, a remote, a clean worktree, or a commit.
