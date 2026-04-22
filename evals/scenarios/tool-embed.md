---
scenario: tool-embed
type: tool-invocation
tool: embed
requires_claude: false
# R4.5 machine-eval fields
setup_script: |
  # embed.py is argv-ignoring; no fixture needed.
  mkdir -p {tmp_dir}
invocation: "python3 -m tools.embed"
expected_exit_code: 0
expected_stdout_contains:
  - "not implemented"
  - "out of scope"
  - "v1.7"
  - "hippocampus"
  - "search.py"
expected_stderr_contains: []
expected_files: []
---

# Tool Scenario · embed

**Contract**: references/tools-spec.md §6.12 · Placeholder stub — semantic embeddings are OUT of scope for v1.7 (user decision #3).

## User Message

```
帮我跑一下 embed，看看它是不是真的按照"v1.7 不做语义 embedding"的决策做了占位符返回。
```

(English equivalent: "Run embed and confirm it behaves as the 'v1.7 no semantic embedding' decision mandates — placeholder output + exit 0.")

## Scenario

Per user decision #3 (markdown-first, LLM-judgment-only for v1.7),
semantic embeddings are explicitly out of scope. `tools/embed.py`
exists only so the CLI dispatcher (`tools/cli.py`) has a valid target
for the `embed` subcommand — invocation must emit a clear notice
explaining the decision and exit 0 (not an error).

This scenario locks in that contract so a future contributor doesn't
accidentally turn it into a real embedding tool without a spec update.

The notice (from `tools/embed.py:_NOTICE`):
- Redirects for in-session retrieval → hippocampus subagent
  (`references/hippocampus-spec.md`)
- Redirects for batch search → `tools/search.py` (metadata + grep ranking)
- Cites the decision (user decision #3)

## Success Criteria

- [ ] `uv run tools/embed.py` prints the notice
- [ ] Notice contains the string "not implemented"
- [ ] Notice contains the string "out of scope" AND references v1.7
- [ ] Notice references the hippocampus subagent by name
- [ ] Notice references `search.py`
- [ ] Exit code is 0 (NOT an error — this is the intended behavior)
- [ ] Invocation via `uv run tools/cli.py embed` produces the same notice + exit 0
- [ ] Passing arbitrary args (e.g., `embed foo bar`) still exits 0 (args are ignored)
- [ ] Notice is printed to stdout (not stderr) so pipelines can capture it

## Input Fixture

N/A — no fixture needed. The tool is argv-ignoring and has no file I/O.

## Expected Output

```
$ uv run tools/embed.py
embed.py -- not implemented. Semantic embeddings are out of scope for v1.7 (user decision #3: markdown-first, LLM-judgment-only).

For retrieval inside a session: use the hippocampus subagent (references/hippocampus-spec.md).
For batch search: use search.py (metadata + grep ranking).

$ echo $?
0

$ uv run tools/cli.py embed some extra args
# ...same notice...
$ echo $?
0
```

## Failure Modes

- A future PR replaces the notice with a real embedding implementation WITHOUT updating `references/tools-spec.md` §6.12 and user decision #3 — this scenario should fail (missing "not implemented" string) and force the author to cite the spec change
- Notice is silenced / moved to stderr → CI should catch (stdout capture empty)
- Exit code changes to 1 → CI should catch

## Linked Documents

- `references/tools-spec.md` §6.12
- `tools/embed.py`
- `tests/test_embed.py`
- `references/hippocampus-spec.md` (the in-session retrieval path)
- `tools/search.py` (the batch-search path)
- Decision source: user decision #3 in `references/user-decisions.md`
