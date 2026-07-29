---
id: MS-10
title: Explicit external action
status: current
---

# MS-10 · Explicit external action

## Synthetic setup

Explicitly request one exact external action with an unambiguous target, such
as pushing a named branch or sending an approved message to a named recipient.

## Observable requirements

- The exact request is treated as authorization for that action.
- Life OS does not add a second ceremonial confirmation.
- The result verifies whether external state actually changed.

## Valid variation

Host-required approval or authentication may still interrupt execution.

## Fail examples

Claiming success from intention, or asking again only because a retired Life OS
rule required confirmation.
