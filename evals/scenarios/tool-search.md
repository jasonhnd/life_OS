---
scenario: tool-search
type: tool-invocation
tool: search
requires_claude: false
# R4.5 machine-eval fields — empty sessions dir: "no matches" + exit 0 (spec 6.8).
setup_script: |
  mkdir -p {tmp_dir}/_meta/sessions
invocation: "python3 -m tools.search 'nonexistent-term' --root {tmp_dir}"
expected_exit_code: 0
expected_stdout_contains:
  - "no matches"
expected_stderr_contains: []
expected_files: []
---

# Tool Scenario · search

**Contract**: references/tools-spec.md §6.8 · Cross-session grep + metadata-weighted ranking (no LLM, no embeddings).

## User Message

```
在我的 second-brain 里搜一下 "runway"，按 subject / domains / keywords 加权排序，最近 30 天的再加点分，给我前 5 个结果。
```

(English equivalent: "Search 'runway' across my second-brain — weight subject / domains / keywords, boost recent (last 30d), give me top 5.")

## Scenario

Deterministic, LLM-free search across `_meta/sessions/*.md`. Semantic
search is the hippocampus subagent's job; this tool is for quick
grep-style recall with metadata weighting.

Ranking formula (per spec §6.8):

```
base_score = 4.0 * subject_hits
           + 2.0 * (domains_hits + keywords_hits)
           + 1.0 * min(body_paragraph_hits, 5)
recency_mult = 1.5 if days_since <= recency_boost_days else 1.0
final_score = base_score * recency_mult
```

Multi-word query → OR-matched across all surfaces.
Case-insensitive plain substring (no regex).
Tie-break: newer session first.
Empty result prints "no matches" and exits 0.
No dependency on INDEX.md — reads session files directly so tool works
when INDEX is stale/missing.

## Success Criteria

- [ ] Single-word query "runway" with 4 session files → returns top N sorted by final_score
- [ ] Hit in `subject` ranks higher than equivalent hit in body (weight 4× vs 1×)
- [ ] Recent session (last 30 days) ranks above older session with same base_score
- [ ] Multi-word query "runway equity" matches session with either term (OR semantics)
- [ ] Case-insensitive: query "Runway" matches session with "runway" in body
- [ ] `--top 5` returns at most 5 results
- [ ] Empty search result → prints "no matches", exit 0
- [ ] Works when `INDEX.md` absent or stale (reads `.md` files directly)
- [ ] Malformed frontmatter in one session → skip that file, other results unaffected
- [ ] Output includes snippet (max 80 chars) around each hit for context

## Input Fixture

4 session files under `_meta/sessions/` (synthetic):

```yaml
# Session A — subject hit, recent
---
session-id: 2026-04-18-1000-runway-math
subject: Runway calculation refresh
domains: [finance]
keywords: [burn-rate]
last_modified: 2026-04-18
---
Body paragraphs discussing runway at depth.
```

```yaml
# Session B — keyword hit, recent
---
session-id: 2026-04-15-0900-budget
subject: Monthly budget review
domains: [finance]
keywords: [runway, expenses]
last_modified: 2026-04-15
---
```

```yaml
# Session C — body hit only, old
---
session-id: 2025-11-10-1400-vision
subject: 2026 vision doc
domains: [strategy]
keywords: [direction]
last_modified: 2025-11-10
---
Body mentions runway once in passing.
```

```yaml
# Session D — no hit
---
session-id: 2026-04-01-1200-health
subject: Sleep routine review
domains: [health]
keywords: [recovery]
last_modified: 2026-04-01
---
```

## Expected Output

```
$ uv run tools/search.py "runway" --top 5
1. 2026-04-18-1000-runway-math  (score 6.0 × 1.5 = 9.0)
   subject: Runway calculation refresh
   ...mentions runway in body paragraphs 3 times...
2. 2026-04-15-0900-budget  (score 2.0 × 1.5 = 3.0)
   keyword match: runway
3. 2025-11-10-1400-vision  (score 1.0 × 1.0 = 1.0)
   body mention: "...mentions runway once in passing..."

3 matches. Exit 0

$ uv run tools/search.py "nonexistent-term"
no matches. Exit 0
```

## Failure Modes

- Non-UTF-8 session file → skip + log warn, other files still ranked
- Very large body (>1MB) → truncate snippet extraction, don't OOM
- `--top 0` → no results printed, exit 0

## Linked Documents

- `references/tools-spec.md` §6.8
- `tools/search.py`
- `tests/test_search.py`
- `pro/agents/hippocampus.md` (semantic counterpart)
