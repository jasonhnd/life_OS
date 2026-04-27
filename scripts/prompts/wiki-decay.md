# User-invoked prompt · wiki-decay (v1.8.0)

> Replaces the deleted `tools/wiki_decay.py`. ROUTER reads this when the
> user wants to scan the wiki for stale entries.

## Trigger keywords

- `扫一下 wiki` / `wiki decay` / `查 wiki 过期`
- `wiki 哪些过时了`
- session-start-inbox hook reports `wiki-decay Nd` and user says "跑一下"

## Goal

Classify every entry in `wiki/` as `stale` / `borderline` / `active` based
on age + confidence, so the user knows what knowledge needs review.

## Steps

### 1. Scan wiki/

Glob `wiki/*.md`. For each file, Read frontmatter:

```yaml
confidence: 0.42        # float 0-1
last_updated: 2026-03-15  # ISO date
source_count: 2         # int (optional)
```

If `last_updated` missing or unparseable, mark as `borderline` with reason
"missing/invalid last_updated".

### 2. Classify

For each entry, compute `age_days = today - last_updated`:

```
stale:      age > 90  AND confidence < 0.4
borderline: (age 45-90) OR (confidence 0.4-0.6) OR (no last_updated)
active:     age < 45 AND confidence >= 0.6
```

### 3. Write report

Write `_meta/eval-history/wiki-decay-{YYYY-MM-DD}.md`:

```markdown
# Wiki decay scan · {YYYY-MM-DD}

## Summary
- Total entries: {N}
- Stale:         {S}  (review or delete)
- Borderline:    {B}  (re-validate or update)
- Active:        {A}  (no action)

## Stale ({S})
- {entry_path} · age {age}d · confidence {c}
  reason: {short reason from frontmatter context}
...

## Borderline ({B})
- {entry_path} · age {age}d · confidence {c} · {reason if any}
...

## Active ({A})
(omit list — just count, user doesn't need to see)

## Recommended actions
- For stale: review the topic, either re-validate (update last_updated +
  bump confidence) or delete the entry.
- For borderline: quick scan, update last_updated if still relevant.
```

### 4. Report to user

```
🌱 wiki-decay done · {N} entries scanned
   {S} stale · {B} borderline · {A} active
   _meta/eval-history/wiki-decay-{date}.md
```

## Output path

- `_meta/eval-history/wiki-decay-{YYYY-MM-DD}.md`

## Notes

- This is read-only on `wiki/`. No file is modified or deleted by this scan.
- The "borderline" bucket catches frontmatter-incomplete entries — user
  might want to backfill `last_updated` after the scan.
- Thresholds (90d, 45d, 0.4, 0.6) are conservative defaults; user can
  override by saying "用 30/60 天阈值" etc.
