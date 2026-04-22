---
scenario: tool-research
type: tool-invocation
tool: research
requires_claude: false
# R4.5 machine-eval fields.
# Runner MUST skip when httpx or markdownify is unavailable — research is a
# network-optional tool and we do not want CI in offline Git-Bash to fail here.
skip_if_missing_python_module:
  - httpx
  - markdownify
setup_script: |
  mkdir -p {tmp_dir}/inbox/research
invocation: "python3 -m tools.research 'test query' --max-pages 0 --root {tmp_dir}"
expected_exit_code: 0
expected_stdout_contains: []
expected_stderr_contains: []
expected_files: []
---

# Tool Scenario · research

**Contract**: references/tools-spec.md §6.4 · Background web fetch → inbox with markdownify + robots.txt enforcement.

## User Message

```
帮我研究一下 "async queue backpressure patterns"，把前 3 条结果抓到 inbox/research/，我等会儿自己读。
```

(English equivalent: "Research 'async queue backpressure patterns'; fetch top 3 results to inbox/research/ for me to read later.")

## Scenario

User kicks off background research. The tool queries a search backend
(SearXNG default, Brave with API key, or demoted DDG fallback), fetches
the top results, converts HTML to markdown via `markdownify`, and writes
to `inbox/research/<slug>-YYYY-MM-DD.md` with provenance frontmatter.
Mock backends are injected via `sys.modules` in tests — this scenario
describes the contract, not the mock shape.

Key contract points per spec §6.4:
- User-agent: `LifeOS-research/1.7 (+local-tool; backend=<name>)`
- `urllib.robotparser` enforces robots.txt (hard requirement)
- `--depth 0` = search page only, `--depth 1` = each top result,
  `--depth 2` = one more outbound-link layer.
- `--max-pages` caps total fetches (default 10).
- Slug = ASCII transliterate → lowercase → hyphenate; non-ASCII → SHA-1[:8].
- Partial/failed fetch → writes file with `incomplete: true`, exit 1.
- **NO LLM summarization** (user decision #16) — raw markdown only.

## Success Criteria

- [ ] `uv run tools/research.py "async queue backpressure patterns" --depth 1 --max-pages 3 --backend searxng` (with mock SearXNG) exits 0
- [ ] 3 files created under `inbox/research/` with today's date in filename
- [ ] Each file has frontmatter with keys: `url`, `fetched_at`, `backend`, `source_rank`, `incomplete`
- [ ] Body is markdown (converted from HTML), no script tags, no style blocks
- [ ] Robots-disallowed URL → skipped, log notice, NOT counted against `--max-pages`
- [ ] `--backend brave` with no `BRAVE_API_KEY` env → clear error, exit 2
- [ ] `--backend ddg` prints demotion notice (2026-04-21 robots change)
- [ ] Network failure mid-fetch → partial file written with `incomplete: true`, exit 1
- [ ] Non-ASCII query (e.g., "量子退火") → slug falls back to SHA-1[:8], exit 0
- [ ] `--max-pages 0` → empty fetch, exit 0 (valid no-op)

## Input Fixture

Mock SearXNG JSON response (synthetic, example.org per RFC 2606):

```json
{
  "results": [
    {"url": "https://example.org/backpressure-patterns", "title": "Async queue patterns"},
    {"url": "https://example.org/reactive-streams", "title": "Reactive streams intro"},
    {"url": "https://example.org/queue-design", "title": "Queue design tradeoffs"}
  ]
}
```

Each example.org URL is mocked with a simple HTML body containing one
`<h1>` + two `<p>` paragraphs.

## Expected Output

```
$ uv run tools/research.py "async queue backpressure patterns" --depth 1 --max-pages 3 \
    --backend searxng
INFO: Querying searxng: "async queue backpressure patterns"
INFO: 3 results → fetching with depth=1
INFO: robots.txt allowed: https://example.org/backpressure-patterns
INFO: Wrote inbox/research/async-queue-backpressure-patterns-2026-04-22.md
INFO: Wrote inbox/research/reactive-streams-intro-2026-04-22.md
INFO: Wrote inbox/research/queue-design-tradeoffs-2026-04-22.md
Exit 0

$ head -5 inbox/research/async-queue-backpressure-patterns-2026-04-22.md
---
url: https://example.org/backpressure-patterns
fetched_at: 2026-04-22T09:00:00Z
backend: searxng
source_rank: 1
incomplete: false
---
```

## Failure Modes

- All 3 URLs disallowed by robots.txt → 0 files written, exit 0 + log notice
- `markdownify` import fails (not installed) → exit 2 with install hint for `research` optional-dep group
- Slug collision (same day, same slug) → append `-1`, `-2` suffix

## Linked Documents

- `references/tools-spec.md` §6.4
- `tools/research.py`
- `tests/test_research.py` (includes @pytest.mark.integration smoke test)
- `pyproject.toml` optional-dep group `research`
