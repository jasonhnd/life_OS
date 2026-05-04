# User-invoked prompt · rebuild-session-index (v1.8.2 · Obsidian-style)

> Replaces deleted `tools/rebuild_session_index.py`. ROUTER reads this when user
> asks for manual session INDEX rebuild outside of retrospective Mode 0.
>
> **v1.8.2 HARD RULE #11**: Session INDEX renders in Obsidian. Apply
> `references/obsidian-style.md` — session rows use `[[sid]]` wikilinks,
> `> [!info]` summary callout, nested tags.

## Trigger keywords

- `重建 session 索引` / `rebuild session index`
- `刷新 sessions INDEX` / `refresh session index`
- `INDEX 不准了` / `session INDEX out of date`

## Goal

Rebuild `_meta/sessions/INDEX.md` from per-session markdown files. Idempotent —
re-running on same data produces byte-identical INDEX.

## Steps

1. `Glob _meta/sessions/*.md` (exclude `INDEX.md` itself)
2. For each path, Read frontmatter YAML and extract:
   - `session_id`, `date`, `project`, `subject`, `outcome_score`, `keywords` (top 3)
3. Sort by `date` desc, `started_at` desc as tie-break
4. Group by `YYYY-MM` (## headings, most recent month first)
5. Format each line: `{date} | {project} | {subject:80} | {score}/10 | [{keywords-top3}] | {session_id}`
6. Write `_meta/sessions/INDEX.md` with header `# Sessions index · auto-rebuilt {ISO8601}`

## Failure handling

- Malformed YAML in a session file → log filename to `_meta/sync-log.md`, skip,
  do not block rebuild
- No `_meta/sessions/` dir → tell user "no sessions, did you seed the brain?",
  exit
- No write permission → tell user explicitly, do not silent-fail

## Report to user

```
✅ session INDEX rebuilt · {N} sessions · {M} months
   _meta/sessions/INDEX.md
```
