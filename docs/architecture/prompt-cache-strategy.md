---
title: "Prompt Cache Strategy"
scope: "host adapter optimization"
audience: "maintainers"
status: "advisory"
last_updated: 2026-04-26
related:
  - tools/prompt_cache.py
  - SKILL.md
---

# Prompt Cache Strategy

Life OS v1.7.2 includes an optional prompt-cache helper at
`tools/prompt_cache.py`. It is an adapter-level cost optimization for providers
that support Anthropic-style `cache_control` breakpoints. It is not part of the
semantic protocol and must not block a workflow on hosts that do not expose
prompt caching.

Prompt caching is especially useful now that Cortex Step 0.5 is always-on in
v1.7.2, because stable system/orchestration text repeats across more turns. The
helper is still advisory: a provider that cannot cache prompts must receive the
same semantic request without cache markers.

## Source And Attribution

`tools/prompt_cache.py` is adapted from hermes-agent
`agent/prompt_caching.py` at commit
`59b56d445c34e1d4bf797f5345b802c7b5986c72`.

The Life OS adaptation keeps the `system_and_3` strategy:

1. Mark the first system message as the stable cache prefix.
2. Mark the three most recent non-system messages as the rolling conversation
   prefix.
3. Use at most four total `cache_control` breakpoints, matching Anthropic's
   documented maximum.

## When To Use

Use the helper only at the provider-adapter boundary, after ROUTER/subagent
messages have already been assembled and before sending the API request.

Good candidates:

- Claude / Anthropic-native adapters that accept `cache_control` on content
  blocks.
- Compatibility adapters that pass Anthropic-style `cache_control` through
  unchanged.
- Long-running multi-turn Life OS sessions where the system prompt, theme,
  orchestration rules, and recent conversational prefix are repeatedly sent.

Do not use it when:

- The provider ignores or rejects Anthropic `cache_control` fields.
- The host already performs its own prompt-cache placement.
- The request body is not a chat-message list.

## API

```python
from tools.prompt_cache import apply_anthropic_cache_control

cached_messages = apply_anthropic_cache_control(
    messages,
    cache_ttl="5m",
    native_anthropic=False,
)
```

Inputs are never mutated. The function returns a deep copy with cache markers
injected.

`cache_ttl="5m"` uses Anthropic's default ephemeral cache behavior.
`cache_ttl="1h"` adds an explicit one-hour TTL marker.

Set `native_anthropic=True` only when the final payload is native Anthropic
format and tool messages may receive top-level `cache_control`.

## Example

Input:

```python
messages = [
    {"role": "system", "content": "Life OS rules..."},
    {"role": "user", "content": "start"},
    {"role": "assistant", "content": "briefing..."},
    {"role": "user", "content": "analyze this decision"},
    {"role": "assistant", "content": "clarifying question..."},
]
```

Output placement:

- System message receives the stable breakpoint.
- The last three non-system messages receive rolling breakpoints.
- The oldest non-system message is left unmarked.

## Operational Guidance

This is a recommendation, not a HARD RULE. If prompt caching fails, the adapter
should retry without cache markers rather than fail the Life OS workflow.

ROUTER may recommend this helper to host implementations that support prompt
caching, but ROUTER must not require it for semantic correctness, subagent
isolation, audit trails, or compliance checks.

Prompt-cache settings do not create a Cortex config path. Cortex thresholds and
host settings stay in `_meta/config.md`; do not place a separate config file
under `_meta/cortex/`.
