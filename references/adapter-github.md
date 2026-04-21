# Adapter: GitHub (second-brain repo)

Translates standard data model operations into .md files with YAML front matter stored in a Git repository.

## File Format

Every data record is a `.md` file:
- **Front matter** (YAML between `---` markers): structured fields
- **Body**: content/text fields

```yaml
---
type: decision
title: "Career change feasibility"
status: decided
score: 6.8
date: 2026-04-08
project: career-transition
last_modified: "2026-04-08T15:30:00Z"
---

[Memorial full text here]
```

## Directory Path Mapping

| Data Type | Path | Filename Pattern |
|-----------|------|-----------------|
| Decision (project) | `projects/{project}/decisions/` | `{date}-{slug}.md` |
| Decision (cross-domain) | `_meta/decisions/` | `{date}-{slug}.md` |
| Task (project) | `projects/{project}/tasks/` | `{slug}.md` |
| Task (area) | `areas/{area}/tasks/` | `{slug}.md` |
| JournalEntry | `_meta/journal/` | `{date}-{type}.md` |
| WikiNote | `wiki/{domain}/` | `{slug}.md` |
| Project | `projects/{project}/index.md` | Fixed name |
| Area | `areas/{area}/index.md` | Fixed name |
| SessionSummary (v1.7) | `_meta/sessions/` | `{session_id}.md` |
| Concept (v1.7) | `_meta/concepts/{domain}/` | `{concept_id}.md` |
| SoulSnapshot (v1.7) | `_meta/snapshots/soul/` | `{YYYY-MM-DD-HHMM}.md` |
| EvalEntry (v1.7) | `_meta/eval-history/` | `{YYYY-MM-DD}-{project}.md` |
| Method (v1.7) | `_meta/methods/{domain}/` | `{method_id}.md` |

## Operations

### Save(type, data)
1. Generate filename from date + slugified title
2. Write .md file with front matter + body
3. `git add` the file

### Update(type, id, data)
1. Read existing file
2. Merge changed fields into front matter
3. Update `last_modified` timestamp
4. Write back
5. `git add` the file

### Archive(type, id)
1. Move file to `archive/{original-path}/`
2. `git add` both old and new paths

### Read(type, id)
1. Read the .md file
2. Parse front matter into structured data
3. Return body as content

### List(type, filters)
1. Glob for files in the type's directory
2. For each file, parse front matter
3. Filter by specified field values
4. Return matching records

### Search(keyword)
1. `grep -r "{keyword}" ~/second-brain/` across all directories
2. Parse matching files' front matter
3. Return results with source paths

### ReadProjectContext(project_id)
1. Read `projects/{project}/index.md`
2. Glob `projects/{project}/tasks/*.md`
3. Glob `projects/{project}/decisions/*.md`
4. Glob `projects/{project}/journal/*.md`
5. Return all parsed

## Change Detection

For sync: `git log --since="{last_sync_time}" --name-only --format=""`

Returns list of files changed since last sync. Parse each to get type + id + last_modified.

## Deletion

Mark in front matter: `_deleted: true`. Do not `git rm` until user confirms across all backends.

## Commit Convention

### On Adjourn (write to outbox)

```bash
git add _meta/outbox/{session_id}/
git commit -m "[life-os] session {session_id} output"
git push
```

Only stage the outbox directory. Never touch main files (projects/, STATUS.md, user-patterns.md) during adjourn.

### On Start Court (merge outboxes)

```bash
# After merging outbox contents into main directories:
git add projects/ areas/ _meta/journal/ _meta/STATUS.md user-patterns.md SOUL.md
git rm -r _meta/outbox/{merged-session-ids}/
git commit -m "[life-os] merge {N} outbox sessions"
git push
```

### General Rules

**Never use `git add -A` or `git add .`** — these can accidentally commit sensitive files (.env, .claude/, credentials, temporary files). Only stage files that Life OS explicitly wrote.

## Worktree Maintenance

Claude Code creates temporary worktrees under `.claude/worktrees/`. These can cause problems:

1. **Cross-platform interference**: Gemini / Antigravity may choke on large worktree directories flooding its context
2. **Path breakage after repo migration**: If the repo moves (e.g., Dropbox → iCloud), worktree `.git` files point to the old path, breaking all git operations

### Prevention

- Add `.claude/worktrees/` to `.gitignore`
- After finishing a Claude Code worktree session, choose **remove** (not keep)
- Before migrating a repo to a different location, clean up first (run these manually in your terminal):

```text
# USER MANUAL RECOVERY — do NOT execute automatically; requires human confirmation
git worktree prune
rm -rf .claude/worktrees/
git config --unset core.hooksPath   # if set to the old path
```

### Recovery

If git reports `fatal: not a git repository: /old/path/.git/worktrees/...`, run these commands **manually in your terminal** (agents must not execute these without explicit user confirmation — see GLOBAL.md Security Boundary #1):

```text
# USER MANUAL RECOVERY — do NOT execute automatically; requires human confirmation
git worktree prune                  # clean git-level references
rm -rf .claude/worktrees/           # remove stale worktree directories
git config --unset core.hooksPath   # remove broken hooks path
git config --unset extensions.worktreeConfig  # remove worktree extension flag
```
