---
title: Concurrent Work Guidance
status: reference
authoritative: false
runtime_authority: SKILL.md
introduced_in: v1.11.0
---

# Concurrent Work Guidance

When several windows, agents, devices, or people may edit the same content, the
required outcome is preservation of user work and honest conflict reporting.

Useful practices include:

- identify the exact files or records each task owns;
- inspect current content immediately before overwriting;
- avoid broad rewrites when a scoped edit is enough;
- compare the intended base with the current file;
- merge independent changes when their meaning is compatible;
- preserve both versions when the correct semantic choice is unclear;
- verify that temporary conflict markers are absent before claiming success.

Git, filesystem metadata, atomic replacement, compare-and-swap behavior, or
host coordination may help. No one implementation is required, and Git is not
a prerequisite.

Do not create a lock, ledger, status file, or coordination ceremony merely to
prove that concurrency was considered.
