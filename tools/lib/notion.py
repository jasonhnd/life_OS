"""Life OS tools — Notion REST API wrapper (v1.7 Sprint 2).

Thin wrapper over ``notion-client`` used by ``tools/sync_notion.py``
(per references/tools-spec.md §6.11) and any future archiver fallback
path that runs outside an active Claude Code session.

Clarification on user decision #16 ("no external API in v1.7"): that
decision scopes to **LLM provider** APIs. Notion is a user-data storage
platform already in use since v1.6.2a via MCP during active sessions.
This wrapper speaks the same underlying HTTP API directly so batch
tools can run without a live session.

Token resolution (highest-priority first):
    1. ``cli_token`` argument (e.g. ``--notion-token <t>`` on CLI)
    2. ``NOTION_TOKEN`` env var
    3. Env var named by ``config.notion_token_env_var``
    4. → :class:`NotionAuthError` ("token not found")
"""

from __future__ import annotations

import os
from datetime import UTC
from typing import Any

from tools.lib.config import LifeOSConfig

__all__ = [
    "NotionAuthError",
    "NotionClient",
    "NotionError",
    "NotionRateLimitError",
    "resolve_token",
]


# ─── Exception taxonomy ────────────────────────────────────────────────────


class NotionError(Exception):
    """Base class for all Notion-layer failures."""


class NotionAuthError(NotionError):
    """Missing / invalid Notion token."""


class NotionRateLimitError(NotionError):
    """Notion API returned HTTP 429 / code=rate_limited."""


# ─── Token resolution ──────────────────────────────────────────────────────


_LIFE_OS_ID_PROPERTY = "life_os_id"
_SYNCED_AT_PROPERTY = "synced_at"


def resolve_token(*, cli_token: str | None, config: LifeOSConfig) -> str:
    """Resolve a Notion integration token.

    Precedence: CLI > ``NOTION_TOKEN`` env > env var named in config.
    Empty strings are treated as "not provided" so callers can safely
    pass ``args.notion_token or None`` directly.

    :raises NotionAuthError: if no token source yields a value.
    """
    if cli_token:
        return cli_token

    env_default = os.environ.get("NOTION_TOKEN")
    if env_default:
        return env_default

    custom_var = config.notion_token_env_var
    if custom_var:
        custom_val = os.environ.get(custom_var)
        if custom_val:
            return custom_val

    raise NotionAuthError(
        "Notion token not found: pass --notion-token, set NOTION_TOKEN in "
        "the environment, or configure [notion] token_env_var in "
        ".life-os.toml."
    )


# ─── Client wrapper ────────────────────────────────────────────────────────


def _load_notion_client() -> tuple[Any, Any]:
    """Import ``notion_client`` lazily, translating ModuleNotFoundError to
    a friendly :class:`NotionError`.

    Returns ``(Client, errors_module)``.
    """
    try:
        from notion_client import Client
        from notion_client import errors as notion_errors
    except ModuleNotFoundError as exc:
        raise NotionError(
            "notion-client is not installed; run `uv sync --extra notion` "
            "(or `pip install notion-client>=2.2`)."
        ) from exc
    return Client, notion_errors


class NotionClient:
    """Upsert-by-life_os_id Notion helper.

    Operations are idempotent: each call to :meth:`upsert_page` looks up
    the target database for an existing page whose ``life_os_id``
    matches, then either creates a new page or updates the existing one.
    """

    def __init__(self, token: str, workspace_id: str | None = None) -> None:
        self._client_class, self._errors = _load_notion_client()
        self._client = self._client_class(auth=token)
        self.workspace_id = workspace_id

    # ─── Public API ──────────────────────────────────────────────────

    def upsert_page(
        self,
        *,
        database_id: str,
        life_os_id: str,
        properties: dict[str, Any],
        body: str | None = None,
    ) -> dict[str, Any]:
        """Create or update a Notion page keyed by ``life_os_id``.

        ``properties`` should already follow Notion's property-value
        shapes (e.g. ``{"Title": {"title": [{"text": {"content": ...}}]}}``).
        A ``life_os_id`` property is injected / overwritten so later
        upserts are idempotent.
        """
        properties = {
            **properties,
            _LIFE_OS_ID_PROPERTY: {
                "rich_text": [{"text": {"content": life_os_id}}]
            },
        }
        existing_id = self._find_existing_page_id(
            database_id=database_id, life_os_id=life_os_id
        )
        children = self._body_to_children(body) if body else None

        try:
            if existing_id is None:
                kwargs: dict[str, Any] = {
                    "parent": {"database_id": database_id},
                    "properties": properties,
                }
                if children:
                    kwargs["children"] = children
                page: dict[str, Any] = self._client.pages.create(**kwargs)
            else:
                page = self._client.pages.update(
                    page_id=existing_id, properties=properties
                )
                if children:
                    self._client.blocks.children.append(
                        block_id=existing_id, children=children
                    )
        except Exception as exc:
            self._translate(exc)
            raise  # pragma: no cover — _translate always raises
        return page

    def mark_synced(self, page_id: str) -> None:
        """Patch the ``synced_at`` property on ``page_id`` to the current
        UTC timestamp (Notion date property format).
        """
        from datetime import datetime

        now_iso = datetime.now(UTC).isoformat()
        try:
            self._client.pages.update(
                page_id=page_id,
                properties={
                    _SYNCED_AT_PROPERTY: {"date": {"start": now_iso}}
                },
            )
        except Exception as exc:
            self._translate(exc)
            raise  # pragma: no cover

    # ─── Internal helpers ────────────────────────────────────────────

    def _find_existing_page_id(
        self, *, database_id: str, life_os_id: str
    ) -> str | None:
        try:
            response = self._client.databases.query(
                database_id=database_id,
                filter={
                    "property": _LIFE_OS_ID_PROPERTY,
                    "rich_text": {"equals": life_os_id},
                },
                page_size=1,
            )
        except Exception as exc:
            self._translate(exc)
            raise  # pragma: no cover

        results = response.get("results") or []
        if not results:
            return None
        first: dict[str, Any] = results[0]
        page_id = first.get("id")
        return page_id if isinstance(page_id, str) else None

    # Notion's API rejects rich_text.content > 2000 chars per object.
    # We chunk at 1900 to leave headroom for any per-block metadata.
    _NOTION_RICH_TEXT_MAX = 1900

    @staticmethod
    def _body_to_children(body: str) -> list[dict[str, Any]]:
        """Convert a plain-text body into one or more paragraph blocks.

        Round-3 audit fix: previously wrapped the entire body in a single
        rich_text object. Notion API limits rich_text.content to 2000 chars,
        so any body longer than that silently failed to sync. Now chunks
        the body at paragraph boundaries (or hard-splits at the chunk size
        when a single paragraph is itself too long) and emits one paragraph
        block per chunk.
        """
        max_chunk = NotionClient._NOTION_RICH_TEXT_MAX
        chunks: list[str] = []

        # Empty body → emit one empty paragraph (matches old behavior).
        if not body:
            chunks = [""]
        else:
            # First split on existing paragraph breaks to keep semantic units
            # together when possible.
            for paragraph in body.split("\n\n"):
                if len(paragraph) <= max_chunk:
                    chunks.append(paragraph)
                else:
                    # Hard-split: walk the paragraph in max_chunk-sized slices.
                    for i in range(0, len(paragraph), max_chunk):
                        chunks.append(paragraph[i : i + max_chunk])

        return [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                },
            }
            for chunk in chunks
        ]

    def _translate(self, exc: BaseException) -> None:
        """Translate ``notion_client`` exceptions into our own taxonomy.

        Always raises — return type is ``None`` only to satisfy mypy for
        callers that do ``self._translate(exc); raise``.
        """
        api_err_cls = getattr(self._errors, "APIResponseError", None)
        timeout_cls = getattr(self._errors, "RequestTimeoutError", None)

        if api_err_cls is not None and isinstance(exc, api_err_cls):
            code = getattr(exc, "code", "") or ""
            message = str(exc)
            if code == "unauthorized":
                raise NotionAuthError(f"Notion auth failed: {message}") from exc
            if code == "rate_limited":
                raise NotionRateLimitError(
                    f"Notion rate-limit hit: {message}"
                ) from exc
            raise NotionError(f"Notion API error ({code}): {message}") from exc

        if timeout_cls is not None and isinstance(exc, timeout_cls):
            raise NotionError(f"Notion request timed out: {exc}") from exc

        # Already one of ours
        if isinstance(exc, NotionError):
            raise exc

        raise NotionError(f"Unexpected error talking to Notion: {exc}") from exc
