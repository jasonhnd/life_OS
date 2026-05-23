---
description: Run all tool-*.md evaluator scenarios (machine-verifiable harness checks for tool-adjacent operations). Replaces v1.8.4 evals/run-tool-eval.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[scenario-glob]  (default: tool-*.md)"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Write
---

# /run-tool-eval

Execute every machine-verifiable tool scenario under `evals/scenarios/tool-*.md`. Each scenario asserts on exit code, stdout substrings, and created files — unlike `/run-eval` which exercises the claude CLI on routing scenarios.

## Pre-flight

```bash
export PYTHONIOENCODING=utf-8  # Windows cp932 dodge
```

List scenarios:
```bash
ls evals/scenarios/tool-*.md 2>/dev/null
```

If empty → emit `ℹ️ no tool-* scenarios found` and exit 0.

## For each scenario

Read scenario frontmatter. Required fields:

| Field | Type | Meaning |
|---|---|---|
| `setup_script` | multiline bash | `{tmp_dir}` placeholder replaced with `mktemp -d` result |
| `invocation` | shell command | `{tmp_dir}` placeholder replaced |
| `expected_exit_code` | integer | required exit code |
| `expected_stdout_contains` | list of strings | each checked via `grep -F` |
| `expected_stderr_contains` | list | optional |
| `expected_files` | list of paths | (after substitution) must exist |
| `expected_files_glob` | list of glob patterns | each must match ≥1 file |
| `env` | map | optional env vars to set per scenario |
| `skip_if_missing_python_module` | list of import names | if any missing → SKIP |
| `skip_if_missing_binary` | list of PATH names | if any missing → SKIP |

### Procedure per scenario

1. Check skip conditions → if any → emit `SKIP <scenario> (reason)` and continue
2. `tmp_dir=$(mktemp -d)` — fresh per scenario
3. Substitute `{tmp_dir}` in setup_script and invocation
4. Run setup_script
5. Run invocation, capture exit code, stdout, stderr
6. Verify:
   - exit code == expected_exit_code
   - each expected_stdout_contains substring is in stdout
   - (optional) each expected_stderr_contains is in stderr
   - each expected_files path exists
   - each expected_files_glob matches ≥1 file
7. Record `PASS` / `FAIL <reason>` / `SKIP <reason>`
8. Cleanup: `rm -rf "$tmp_dir"`

## Final report

```
── /run-tool-eval · TIMESTAMP ──
Total tool scenarios: N
PASS: X
SKIP: Y
FAIL: Z

[per-FAIL one-liner with reason]

Exit codes:
  0 — all PASS or gracefully SKIP
  1 — ≥1 FAIL
  2 — harness error (python/yaml unavailable)
```

## v1.8.5 changes vs v1.8.4 evals/run-tool-eval.sh

- v1.8.4: 406-line bash harness with YAML parser, python module checks, glob expansion
- v1.8.5: LLM iterates scenarios, runs bash commands inline, uses python only if scenario invocation requires it. Same assertion coverage, zero bash harness.

## v1.8.5 NEW: integrates with regression-fixtures

Per Stage 9, `evals/regression-fixtures/*.yml` (28 cases) are negative cases — they MUST FAIL when run through validators. `/run-regression` slash command (separate) handles those. `/run-tool-eval` covers POSITIVE tool scenarios only.
