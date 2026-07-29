---
id: archiver
status: optional-template
authoritative: false
runtime_authority: SKILL.md
purpose: Persist requested material into an explicitly bound second-brain.
---

# Archiver

## Useful when

The user asks to save, remember, organize, or update durable Markdown in an
explicitly bound second-brain.

## Skip when

No persistence was requested, no writable binding exists, or the desired target
is materially ambiguous.

## Suggested inputs

- the exact bound root and access level;
- content to persist and its provenance;
- existing target record or local organization;
- desired relationship to other records.

## Useful questions

- What exact record best fits the request?
- Which existing structure should be preserved?
- What must remain marked as inference or uncertainty?
- Which write evidence will support completion?

## Possible output

A created or updated Markdown record plus a concise report of the exact write
and any unresolved conflict.

## Safety

Do not infer a second-brain from repository shape, write into an unbound
directory, or turn saving into an automatic Git, migration, or session-ending
ritual.
