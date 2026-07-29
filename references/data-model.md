---
title: Life OS Local Markdown Data Model
status: reference
authoritative: false
runtime_authority: SKILL.md
introduced_in: v1.11.0
---

# Local Markdown Data Model

> [!info] Non-authoritative reference
> This file describes interoperable Markdown shapes. `SKILL.md` defines runtime
> behavior. Existing user data takes precedence over these examples.

## 1. Storage Identity

A Life OS second-brain is a **user-approved local directory containing
Markdown data**.

Full Mode requires an explicit binding to that directory. A binding is valid
when:

- the user has selected or previously approved the local directory;
- the current host can address that local directory;
- the requested operation is inside the approved scope;
- the model can read Markdown for read tasks and write Markdown for persistence
  tasks.

Git, a remote, network access, and a particular folder layout are not binding
requirements.

## 2. Binding Model

A binding is runtime context, not necessarily a file.

Conceptually it contains:

| Field | Meaning |
|---|---|
| `root` | User-approved local directory |
| `scope` | Session-scoped or persistently remembered by the host |
| `access` | Read-only or read/write |
| `approved_by_user` | Evidence that the user selected the target |

Hosts may represent this context differently. Life OS must not require a
universal config file merely to prove that a binding exists.

A previously explicit persistent binding may be reused. It does not need to be
reconfirmed on every turn. If the target becomes unavailable or ambiguous, the
model reports that state instead of silently selecting another directory.

## 3. Optional Directory Conventions

Existing second-brains may use these familiar directories:

```text
second-brain/
├── projects/
├── areas/
├── inbox/
├── wiki/
├── meta/
└── SOUL.md
```

None of these names alone authorizes a binding. A newly bound empty directory
may be initialized gradually as the user asks Life OS to persist information.

Do not create the complete tree pre-emptively unless the user requests it.

## 4. Common Markdown Records

These are compatibility shapes, not mandatory output for every session.

### Decision

Suggested path:

```text
meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md
```

Suggested frontmatter:

```yaml
---
id: dec-2026-07-29-001
title: Example decision
type: change
projects: []
reviewed_at: 2026-07-29
decision: One-line outcome
rationale: Why this outcome was selected
---
```

Useful optional fields include `domains`, `reviewed_by`, `reopen_condition`,
`supersedes`, `superseded_by`, `applied_methods`, and `journal_date`.

### Task

Suggested fields:

| Field | Example |
|---|---|
| `title` | Prepare proposal |
| `status` | `todo`, `in-progress`, `waiting`, `done`, or `cancelled` |
| `priority` | `p0` through `p3` |
| `due_date` | ISO date |
| `project` | Related project ID |

### Journal

Suggested path:

```text
meta/journal/<YYYY-MM-DD>.md
```

A daily file may append multiple entries. Useful optional fields include
`projects`, `session_ids`, `type_tags`, `referenced_decisions`, and
`referenced_methods`.

### Project

Suggested path:

```text
projects/<project-id>/index.md
```

Useful fields include `name`, `lifecycle_stage`, `status`, `priority`,
`deadline`, `outcome`, and optional strategic relationships.

### Area

Suggested path:

```text
areas/<area-id>/index.md
```

Areas represent ongoing responsibilities rather than endpoint-based projects.

### Wiki note

Suggested path:

```text
wiki/<topic>.md
```

Useful fields include `title`, `tags`, provenance, and Markdown links to related
notes.

### Identity and behavioral context

Existing second-brains may use `SOUL.md`, `meta/user-patterns.md`, snapshots,
concepts, methods, and strategic-line files. Treat these as sensitive
user-authored data. Read or update them only when relevant to the user's
request.

## 5. Operations

The model selects the concrete filesystem tools. The semantic operations are:

| Operation | Outcome |
|---|---|
| `Read` | Return the requested record without expanding scope |
| `Save` | Create a relevant Markdown record at an authorized target |
| `Update` | Change the identified record while preserving unrelated content |
| `List` | Enumerate records relevant to the current question |
| `Search` | Find relevant content inside the bound root |
| `Archive` | Mark or move a record according to the existing local convention |
| `Delete` | Remove the exact authorized target |
| `Link` | Add a meaningful Markdown or wikilink relationship |

Operations do not imply Git actions.

## 6. Write Rules

- Preserve the existing schema and style when editing an established
  second-brain.
- Create only the files and folders needed for the requested outcome.
- Keep writes inside the bound root.
- Do not stage, commit, push, publish, or export merely because a local write
  succeeded.
- Do not silently overwrite content that changed during the operation.
- Do not bulk-reformat user files as incidental cleanup.
- Do not persist sensitive inferences merely because they occurred in
  conversation.
- Report material writes and any unresolved conflicts.

## 7. Concurrency and Conflicts

Life OS does not require one locking implementation.

The required outcome is:

- concurrent work must not be silently lost;
- a model should inspect current content before overwriting a shared record;
- conflicting edits should be merged when the correct result is clear;
- material ambiguity should be surfaced to the user;
- temporary files or conflict artifacts must not be presented as completed
  user records.

Hosts may use atomic writes, compare-and-swap behavior, file metadata, Git, or
another available mechanism. The method is chosen dynamically.

## 8. Migration

Existing v1.9 and v1.10 Markdown data should remain readable.

A migration:

- requires a clear user request;
- identifies the exact local target;
- previews material structural changes;
- preserves user content;
- uses proportionate rollback or recovery evidence;
- does not require Git;
- reports what changed and what was not migrated.

Installation, update, start, review, save, and end do not implicitly authorize
bulk migration.

## 9. Git Relationship

Git is optional. When present, it can provide history, comparison,
synchronization, and recovery evidence.

The Git adapter is described in `references/adapter-github.md`. Its absence does
not reduce a valid local Markdown binding to Conversation-Only Mode.
