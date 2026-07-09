---
description: Run all evals/scenarios/*.md routing scenarios via claude CLI, save outputs to evals/outputs/, report pass/fail. Supports --tier <judgment|execution|batch> for degradation-safety runs (v1.10.0). Replaces v1.8.4 evals/run-eval.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[scenario-name-glob] [--tier judgment|execution|batch]  (default: all scenarios, default tier)"
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

### 3. Tier selection (v1.10.0 · degradation-safety axis, issue #4 D2)

If `$ARGUMENTS` contains `--tier <judgment|execution|batch>`:

- Map the tier to its model via the ONE mapping table in `references/model-dispatch-policy.md` (judgment→`opus`, execution→`sonnet`, batch→`haiku`) and pass it to every invocation: `claude --model <mapped-model> -p "..."`.
- Scenarios MAY declare `min_model_tier: judgment|execution|batch` in YAML frontmatter (tiers per the same policy). Semantics: the weakest tier at which this scenario must still pass.
  - Requested tier is **below** a scenario's `min_model_tier` → run it anyway and record the result, but mark it `below-floor (informational)` — failure expected, not counted against the verdict.
  - Requested tier is **at or above** `min_model_tier` → result counts normally.
  - Scenario has no `min_model_tier` → treat as `judgment` (most conservative floor) and note `untiered` in the report.
- **Overall pass semantics**: a scenario passes overall ONLY if it passes at its declared minimum tier. Passing on frontier while failing at the declared tier is itself a spec bug — either the tier claim in the scenario is too optimistic (raise it) or the prompt needs simplification.
- Save outputs to `evals/outputs/<scenario>-tier-<tier>-<timestamp>.md`.
- After the run, **regenerate `docs/evals/tier-matrix.md`** from actual recorded results (see that file's header for the row format). The matrix is a generated artifact — never hand-edit rows; regenerate whenever scenarios or the tier→model mapping change.

Without `--tier`: run at the session default (frontier) as before.

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
── /run-eval · TIMESTAMP [· tier: <tier> → model <mapped>] ──
Total scenarios: N
PASS: X
FAIL: Y
Below-floor informational: B (tier runs only)
Compliance fails: Z (separate metric)

[per-scenario one-liner if FAIL]

VERDICT: <pass-rate>%
```

If any FAIL with non-zero exit → exit 1. For tier runs, a scenario failing AT its declared `min_model_tier` is a FAIL (spec bug — tier claim too optimistic or prompt needs simplification); `below-floor` failures are informational only.

## v1.8.5 changes vs v1.8.4 evals/run-eval.sh

- v1.8.4: bash for-loop, color codes, layered exit code tracking, calls compliance-check.sh
- v1.8.5: LLM iterates scenarios, calls `claude -p` via Bash, uses `/check-spec-drift` slash for compliance instead of bash script. Same coverage, zero bash dependency.
