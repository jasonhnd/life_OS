#!/usr/bin/env python3
# Forked from NousResearch/hermes-agent (MIT License) commit 59b56d445c34e1d4bf797f5345b802c7b5986c72
# Adapted for Life OS v1.7.2
"""Prompt cache helpers for Life OS v1.7.2.

Implements the ``system_and_3`` strategy for Anthropic-style prompt caching:
one cache_control breakpoint on the system prompt plus three rolling
breakpoints on the most recent non-system messages, for four total breakpoints.
The helpers are pure functions and do not perform API calls.
"""

from __future__ import annotations

import copy
from typing import Any

Message = dict[str, Any]

MAX_SYSTEM_BREAKPOINTS = 1
MAX_ROLLING_MESSAGE_BREAKPOINTS = 3
MAX_CACHE_BREAKPOINTS = MAX_SYSTEM_BREAKPOINTS + MAX_ROLLING_MESSAGE_BREAKPOINTS

__all__ = [
    "MAX_CACHE_BREAKPOINTS",
    "MAX_ROLLING_MESSAGE_BREAKPOINTS",
    "MAX_SYSTEM_BREAKPOINTS",
    "apply_anthropic_cache_control",
    "apply_system_and_3_cache_control",
]


def _cache_marker(cache_ttl: str) -> dict[str, str]:
    """Return an Anthropic ephemeral cache_control marker."""
    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"
    return marker


def _apply_cache_marker(
    message: Message,
    cache_marker: dict[str, str],
    *,
    native_anthropic: bool = False,
) -> None:
    """Add cache_control to one message, handling common adapter formats."""
    role = message.get("role", "")
    content = message.get("content")

    if role == "tool":
        if native_anthropic:
            message["cache_control"] = cache_marker
        return

    if content is None or content == "":
        message["cache_control"] = cache_marker
        return

    if isinstance(content, str):
        message["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return

    if isinstance(content, list) and content:
        last_block = content[-1]
        if isinstance(last_block, dict):
            last_block["cache_control"] = cache_marker


def apply_anthropic_cache_control(
    api_messages: list[Message],
    cache_ttl: str = "5m",
    native_anthropic: bool = False,
) -> list[Message]:
    """Apply Life OS's ``system_and_3`` prompt cache strategy.

    Args:
        api_messages: Chat-style messages ready for a provider adapter.
        cache_ttl: Anthropic cache TTL. ``"5m"`` uses the provider default;
            ``"1h"`` adds an explicit one-hour TTL marker.
        native_anthropic: If true, allow top-level cache_control on tool
            messages for native Anthropic message payloads.

    Returns:
        A deep copy of ``api_messages`` with up to four cache_control
        breakpoints: first system message, plus the last three non-system
        messages. The input list is never mutated.
    """
    messages = copy.deepcopy(api_messages)
    if not messages:
        return messages

    marker = _cache_marker(cache_ttl)

    if messages[0].get("role") == "system":
        _apply_cache_marker(messages[0], marker, native_anthropic=native_anthropic)

    non_system_indexes = [
        index for index, message in enumerate(messages) if message.get("role") != "system"
    ]
    for index in non_system_indexes[-MAX_ROLLING_MESSAGE_BREAKPOINTS:]:
        _apply_cache_marker(messages[index], marker, native_anthropic=native_anthropic)

    return messages


def apply_system_and_3_cache_control(
    api_messages: list[Message],
    cache_ttl: str = "5m",
    native_anthropic: bool = False,
) -> list[Message]:
    """Alias that names the concrete strategy used by Life OS v1.7.2."""
    return apply_anthropic_cache_control(
        api_messages,
        cache_ttl=cache_ttl,
        native_anthropic=native_anthropic,
    )
