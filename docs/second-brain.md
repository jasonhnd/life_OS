---
title: Second Brain
version: 1.11.0
status: current
---

# Second Brain

A Life OS second-brain is a user-approved local directory containing persistent
Markdown data.

It can hold decisions, projects, areas, journals, tasks, research, reusable
knowledge, values, and any other Markdown structure useful to the user.

## Binding

Full Mode requires an explicit binding. The binding identifies:

- the exact local directory;
- whether access is read-only or read/write;
- whether approval lasts for the current session or is remembered by the host.

Life OS does not infer a binding from directory names, Git, familiar files,
filesystem proximity, or recent screen context.

## Git

Git is optional. It may add history, diffing, synchronization, and recovery
evidence, but local Markdown persistence works without it. Pull, commit, and
push are separate actions and are never triggered by start or end phrases.

## Conversation-only fallback

Without a binding, Life OS can still help in the current conversation. It cannot
claim persistent memory or durable archiving.

## Existing data

Life OS reads the structures already present before writing. Existing v1.9 and
v1.10 Markdown does not need automatic normalization. Any bulk migration
requires an explicit request, an exact target, a preview, preservation
evidence, and post-change verification.
