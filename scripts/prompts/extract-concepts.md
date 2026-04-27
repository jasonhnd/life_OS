# User-invoked prompt · extract-concepts (v1.8.0 Option A)

> Replaces deleted `tools/extract.py` and `tools/lib/cortex/extraction.py`
> helpers. ROUTER reads this when user manually wants to run concept candidate
> extraction outside of archiver Phase 2.

## Trigger keywords

- `抽取概念候选` / `extract concept candidates`
- `跑 concept extraction` / `concept extraction`

## Goal

Tokenize a corpus of session text, count noun-phrase candidates, filter
stopwords + low-frequency, generate canonical slugs. This is the deterministic
first pass — the human or archiver subagent does LLM judgment on top.

## Steps

1. **Input**: ask user for source — typically:
   - "current session transcript"
   - "session file at _meta/sessions/{sid}.md"
   - "all sessions in _meta/sessions/{YYYY-MM}-*.md"
2. **Read + concatenate** all source text
3. **Tokenize**: split into 1-3 word noun-phrase candidates (alphanumeric + Chinese chars)
4. **Filter stopwords** (中英日 common words):
   - 中文: 是 / 的 / 了 / 在 / 有 / 我 / 你 / 他 / 这 / 那 / 都 / 也 / 就 / 还 / 但 / 等
   - English: the / a / an / and / or / but / is / are / was / were / be / been / has / have / had / for / of / with / this / that / it / on / in / to / from
   - 日本語: です / ます / これ / それ / あれ / という / こと / もの / ため
5. **Count occurrences** per candidate
6. **Filter `count >= 2`** (single-mention items are too transient)
7. **Generate slug** per candidate (deterministic, must be reproducible):
   - Lowercase
   - Replace spaces / non-alphanumeric with `-`
   - Chinese: pinyin transliteration if reliable; **fallback to SHA-1 hash of canonical name (first 10 chars)** to guarantee same name → same slug across runs
8. Sort by count desc, take top 20

## Output (no file write — print to user)

```
🔍 Concept candidates · {N} found ≥ 2 mentions

Top 20:
   {count}× {name} → slug: {slug}
   {count}× {name} → slug: {slug}
   ...

Next: archiver Phase 2 LLM judgment will filter for criteria 2-6
(identity beyond session, person/value/procedure, privacy, domain).
```

## Notes

- This prompt is **mostly used inline by archiver** (the steps in `archiver.md`
  Phase 2 mid-step refer to this logic). Standalone invocation is for testing
  or one-off candidate extraction.
- No file write. Output is inline. If user wants to persist, they can copy the
  output into a working note.
