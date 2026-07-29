---
title: Behavioral Conformance
version: 1.11.0
status: current
---

# Behavioral Conformance

Life OS conformance evaluates observable results, boundaries, side effects, and
evidence. It does not grade private reasoning or require a specific tool,
agent, status line, or sequence.

The current suite is under `evals/` and covers MS-01 through MS-18.

Scenarios may be reviewed manually or with any available host capability.
Synthetic fixtures must be used; a real second-brain must never be used for
development evaluation.

Missing evidence produces `not verified`, never `pass`.
