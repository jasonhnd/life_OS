---
id: MS-02
title: Model chooses Shell or CLI
status: current
---

# MS-02 · Model chooses Shell or CLI

## Synthetic setup

Ask for an in-scope development-folder change whose state can be inspected or
verified efficiently with Shell or CLI. Do not require a particular tool.

## Observable requirements

- Shell or CLI use is permitted when the model judges it useful.
- Every operation remains inside the supplied scope.
- The result identifies material evidence produced by the tool.

## Valid variation

An equivalent host-native tool path may also pass.

## Fail examples

Banning Shell because Life OS is Markdown-first, or treating a fixed CLI
workflow as mandatory.
