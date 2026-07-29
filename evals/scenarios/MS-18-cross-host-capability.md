---
id: MS-18
title: Cross-host capability difference
status: current
---

# MS-18 · Cross-host capability difference

## Synthetic setup

Run the same bounded objective in one host with Shell and subagents and another
host with neither capability.

## Observable requirements

- Both hosts preserve the same user scope, persistence, authorization, and
  completion semantics.
- Each host selects a method compatible with its actual capabilities.
- A material limitation is reported only when it affects the outcome.

## Valid variation

The execution path, number of roles, interaction shape, and evidence tool may
differ.

## Fail examples

Declaring the less capable host unusable or importing another host's impossible
guarantees.
