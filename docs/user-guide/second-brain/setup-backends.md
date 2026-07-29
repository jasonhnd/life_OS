---
title: Bind a Local Markdown Directory
version: 1.11.0
status: current
---

# Bind a Local Markdown Directory

Life OS v1.11 has one persistence backend: an explicitly approved local
Markdown directory.

## Bind

Select the directory through your host or name the exact local directory in a
way the host can resolve. Then state:

- that it is the Life OS second-brain;
- whether access is read-only or read/write;
- whether the binding is for this session or may be remembered.

A prior explicit persistent binding may be reused without confirmation on every
turn. If it becomes unavailable or ambiguous, Life OS reports that state rather
than selecting another directory.

## Do not infer

Life OS does not infer a binding from:

- `.git`;
- a `SOUL.md` file;
- `projects/`, `wiki/`, or `meta/` directory names;
- a recent screen or path;
- the Life OS development repository.

Cloud-synchronized folders may be used only when they resolve to the selected
local directory. The cloud service does not become universal Life OS authority.
