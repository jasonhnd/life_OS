---
title: Reviewing Scenarios
version: 1.11.0
status: current
---

# Reviewing Scenarios

Choose a current file under `evals/scenarios/`, use its synthetic setup, and
observe the material result:

- answer quality;
- reads and writes;
- workspace boundaries;
- external side effects;
- persistence and Git behavior;
- verification evidence;
- limitations or blocked conditions.

Apply `evals/rubrics/model-sovereignty.md` and record concrete observations
under `evals/evidence/`.

No runner, CLI, CI, external evaluator, or fixed model is required. If the host
cannot expose evidence needed for a condition, record it as `not verified`.
