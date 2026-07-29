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

### 1. Read the scenario body
Scenario files use markdown sections, **not** YAML frontmatter:
- `## User Message` (also `## 用户消息` / `## ユーザーメッセージ`, and the multi-message `## User Messages` variant) — the prompt(s) to send, inside fenced code blocks.
- `## Expected Behavior` and `## Quality Checkpoints` — what a correct run must do (which subagent launches, which routing path is taken, substrings that must / must-not appear).

Extract the input from the `## User Message` fenced code block. If that section or its code fence is missing, mark the scenario `FAIL (schema error)`.

### 2. Invoke claude
```bash
claude -p "<user message>" > evals/outputs/<scenario>-<timestamp>.md
```
Capture the exit code. For multi-message scenarios, run each message and save numbered outputs.

### 3. Verify against Expected Behavior
- Check the output satisfies the scenario's `## Expected Behavior` / `## Quality Checkpoints` (e.g. the right subagent launch line like `Task(subagent_type=retrospective)`, the expected routing path, required substrings present and forbidden ones absent).
- Quality-of-output judgments that can't be grep-verified (score distribution, REVIEWER substance, etc.) are noted for manual rubric scoring, not auto-failed.

### 4. Record pass/fail
- `PASS` if exit 0 + the grep-verifiable Expected Behavior / Quality Checkpoints are met
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
