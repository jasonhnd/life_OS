---
id: memory-keeper
status: optional-template
authoritative: false
runtime_authority: SKILL.md
purpose: Maintain the usefulness and compatibility of persistent Markdown.
---

# Memory Keeper

## Useful when

The user asks to repair links, reconcile duplicate records, improve retrieval,
or migrate part of an explicitly bound second-brain.

## Skip when

The user did not request maintenance, the target is unbound, or the issue can be
resolved with one ordinary scoped edit.

## Suggested inputs

- exact bound scope and requested maintenance outcome;
- current schema and representative records;
- duplicate, conflict, or link evidence;
- preservation and rollback needs.

## Useful questions

- Which records are actually inconsistent?
- What user-authored meaning must be preserved?
- Can the repair be smaller than a migration?
- What evidence will show that nothing was silently lost?

## Possible output

A scoped repair, reconciliation proposal, migration preview, or integrity
report with changed and unverified state.

## Safety

Do not confuse the Life OS development repository with a second-brain, perform
automatic migrations, or require Git for local persistence.
