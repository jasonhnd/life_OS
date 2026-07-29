---
title: Life OS Behavioral Conformance
status: developer-doc
authoritative: false
runtime_authority: SKILL.md
version: 1.11.0
---

# Behavioral Conformance

These evaluations check observable Life OS behavior. They do not prescribe the
model's private reasoning, tool sequence, agent names, step count, status line,
or orchestration shape.

## How to Review

A reviewer may run a scenario manually or with any available host capability:

1. use only the synthetic setup described by the scenario;
2. observe the answer, writes, tool effects, and external effects that are
   material to the scenario;
3. compare them with the observable requirements and rubric;
4. record concrete evidence, including limitations;
5. mark missing evidence as `not verified`, never as a pass.

No CLI, runner, CI system, external evaluator, or specific model is required.
Different internal paths may pass when their observable outcomes satisfy the
same contract.

## Layout

- `scenarios/` — MS-01 through MS-18 behavioral cases;
- `regression-fixtures/` — synthetic failure prompts and workspace descriptions;
- `rubrics/model-sovereignty.md` — shared judgment criteria;
- `evidence/` — dated candidate review records.

Historical process-prescriptive evaluations are preserved under
`docs/history/v1.10-evals/`.

Never run these scenarios against a real second-brain.
