---
description: Run all evals/scenarios/*.md routing scenarios via claude CLI, save outputs to evals/outputs/, report pass/fail. Replaces v1.8.4 evals/run-eval.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[scenario-name-glob]  (default: all scenarios)"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Write
---

# /run-eval

Execute every routing scenario under `evals/scenarios/` by invoking the `claude` CLI in batch mode (`claude -p`). Compare actual output against scenario expectations. Save outputs to `evals/outputs/<scenario>-<timestamp>.md` and report pass/fail.

## Pre-flight

### 1. claude CLI availability
```bash
command -v claude
```
If not found OR `LIFEOS_EVAL_SKIP_CLAUDE=1` is set → emit `⏭ skipping all eval scenarios (claude CLI unavailable)` and exit 0.

### 2. List scenarios
```bash
ls evals/scenarios/*.md
```
If `$ARGUMENTS` non-empty, filter by glob pattern.

## For each scenario

### 1. Read scenario frontmatter
The scenario file has YAML frontmatter with fields:
- `input`: prompt to send to claude
- `expected_subagent`: which Task() subagent must be called
- `expected_pattern_in_output`: regex/substring that must appear in claude's output
- `compliance_check`: optional name of a check to run via `/check-spec-drift` or AUDITOR Mode 3

### 2. Invoke claude
```bash
claude -p "<input>" > evals/outputs/<scenario>-<timestamp>.md
```
Capture exit code.

### 3. Verify expectations
- Check the output file contains the expected subagent launch line (e.g. `Task(subagent_type=retrospective)`)
- Check `expected_pattern_in_output` matches via grep
- If `compliance_check` set, invoke `/check-spec-drift` or relevant scenario-specific check

### 4. Record pass/fail
- `PASS` if exit 0 + all expectations met
- `FAIL <reason>` otherwise

## Final report

```
── /run-eval · TIMESTAMP ──
Total scenarios: N
PASS: X
FAIL: Y
Compliance fails: Z (separate metric)

[per-scenario one-liner if FAIL]

VERDICT: <pass-rate>%
```

If any FAIL with non-zero exit → exit 1.

## v1.8.5 changes vs v1.8.4 evals/run-eval.sh

- v1.8.4: bash for-loop, color codes, layered exit code tracking, calls compliance-check.sh
- v1.8.5: LLM iterates scenarios, calls `claude -p` via Bash, uses `/check-spec-drift` slash for compliance instead of bash script. Same coverage, zero bash dependency.
