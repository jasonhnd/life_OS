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
| Decision (project) | `projects/{p}/decisions/` | `{date}-{slug}.md` |
| Decision (cross-domain) | `_meta/decisions/` | `{date}-{slug}.md` |
| Task (project) | `projects/{p}/tasks/` | `{slug}.md` |
| Task (area) | `areas/{a}/tasks/` | `{slug}.md` |
| JournalEntry | `_meta/journal/` | `{date}-{type}.md` |
| WikiNote | `wiki/` | `{slug}.md` |
| Project | `projects/{p}/index.md` | Fixed name |
| Area | `areas/{a}/index.md` | Fixed name |

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
1. Read `projects/{p}/index.md`
2. Glob `projects/{p}/tasks/*.md`
3. Glob `projects/{p}/decisions/*.md`
4. Glob `projects/{p}/journal/*.md`
5. Return all parsed

## Change Detection

For sync: `git log --since="{last_sync_time}" --name-only --format=""`

Returns list of files changed since last sync. Parse each to get type + id + last_modified.

## Deletion

Mark in front matter: `_deleted: true`. Do not `git rm` until user confirms across all backends.

## Commit Convention

After all writes: `git add -A && git commit -m "[life-os] {summary}" && git push`
