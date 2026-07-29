---
title: Installation
version: 1.11.0
status: current
---

# Installation

Installation has one product requirement: your AI host must be able to read the
repository-root `SKILL.md`.

## Choose a host mechanism

Depending on the host, you may:

- register the repository as a local skill;
- copy the Markdown package into the host's skill location;
- work from a repository checkout and explicitly ask the host to use
  `SKILL.md`.

Host-specific registration is setup plumbing, not runtime authority. Life OS
does not require Shell, Git, slash commands, hooks, installed agent wrappers, or
a particular model vendor.

## Verify

Ask in natural language:

> Check whether Life OS is available in this current workspace. Do not inspect
> any other directory and do not make repairs.

A useful answer identifies the current directory type, skill availability, and
second-brain binding separately. A missing binding means Conversation-Only
Mode, not a failed installation.

## Enable Full Mode

Select a local directory containing, or intended to contain, your Markdown
second-brain. Then explicitly bind it:

> Bind the local directory I selected as my read/write Life OS second-brain for
> this session.

The target does not need Git. Life OS must not search for or create a
second-brain without clear user intent.

See [First session](getting-started/first-session.md) and
[Second-brain setup](user-guide/second-brain/setup-backends.md).
