"""Tests for tools/lib/notion.py — v1.7 Sprint 2.

Per references/tools-spec.md §6.11:
 - Notion REST API via `notion-client` (NOT an LLM API; user decision #16
   scope is LLM provider APIs, not data storage APIs).
 - Token resolution: CLI > NOTION_TOKEN env var > config.notion_token_env_var
   → env var named in config > error.
 - Upsert by life_os_id property; idempotent on re-run.

All tests mock the Notion Client — no network, no real tokens.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest

from tools.lib.config import LifeOSConfig

# ─── Fake LifeOSConfig helper ───────────────────────────────────────────────


def _make_config(
    *,
    token_env_var: str | None = None,
    workspace_id: str | None = None,
) -> LifeOSConfig:
    return LifeOSConfig(
        second_brain_root=Path("/tmp/sb"),
        backup_dest=Path("/tmp/sb-back"),
        reconcile_auto_fix=False,
        search_recency_boost_days=90,
        export_default_format="pdf",
        notion_token_env_var=token_env_var,
        notion_workspace_id=workspace_id,
    )


# ─── Fake notion_client module, injected into sys.modules ───────────────────


@pytest.fixture
def fake_notion_module(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Install a fake `notion_client` package exposing a Mock Client class."""
    fake_client_class = MagicMock(name="FakeClient")
    fake_module = ModuleType("notion_client")
    fake_module.Client = fake_client_class  # type: ignore[attr-defined]

    # Also create an `errors` submodule with the exception classes the
    # production code catches.
    errors_module = ModuleType("notion_client.errors")

    class APIResponseError(Exception):
        def __init__(self, message: str = "", code: str = "") -> None:
            super().__init__(message)
            self.code = code

    class HTTPResponseError(Exception):
        pass

    class RequestTimeoutError(Exception):
        pass

    errors_module.APIResponseError = APIResponseError  # type: ignore[attr-defined]
    errors_module.HTTPResponseError = HTTPResponseError  # type: ignore[attr-defined]
    errors_module.RequestTimeoutError = RequestTimeoutError  # type: ignore[attr-defined]
    fake_module.errors = errors_module  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "notion_client", fake_module)
    monkeypatch.setitem(sys.modules, "notion_client.errors", errors_module)

    # Make sure notion.py reloads with the fake module if it was imported
    # earlier in another test.
    sys.modules.pop("tools.lib.notion", None)

    return fake_client_class


# ─── resolve_token() ────────────────────────────────────────────────────────


def test_resolve_token_cli_wins(
    monkeypatch: pytest.MonkeyPatch, fake_notion_module: MagicMock
) -> None:
    from tools.lib.notion import resolve_token

    monkeypatch.setenv("NOTION_TOKEN", "env-token")
    cfg = _make_config(token_env_var="NOTION_TOKEN")
    assert resolve_token(cli_token="cli-token", config=cfg) == "cli-token"


def test_resolve_token_falls_back_to_notion_token_env(
    monkeypatch: pytest.MonkeyPatch, fake_notion_module: MagicMock
) -> None:
    from tools.lib.notion import resolve_token

    monkeypatch.setenv("NOTION_TOKEN", "env-fallback")
    cfg = _make_config()  # no token_env_var in config
    assert resolve_token(cli_token=None, config=cfg) == "env-fallback"


def test_resolve_token_uses_config_specified_env_var(
    monkeypatch: pytest.MonkeyPatch, fake_notion_module: MagicMock
) -> None:
    from tools.lib.notion import resolve_token

    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.setenv("CUSTOM_NOTION_ENV", "custom-token")
    cfg = _make_config(token_env_var="CUSTOM_NOTION_ENV")
    assert resolve_token(cli_token=None, config=cfg) == "custom-token"


def test_resolve_token_no_sources_raises(
    monkeypatch: pytest.MonkeyPatch, fake_notion_module: MagicMock
) -> None:
    from tools.lib.notion import NotionAuthError, resolve_token

    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("CUSTOM_NOTION_ENV", raising=False)
    cfg = _make_config(token_env_var="CUSTOM_NOTION_ENV")
    with pytest.raises(NotionAuthError, match="token"):
        resolve_token(cli_token=None, config=cfg)


def test_resolve_token_empty_string_cli_falls_through(
    monkeypatch: pytest.MonkeyPatch, fake_notion_module: MagicMock
) -> None:
    """An empty CLI token must not be treated as 'provided'."""
    from tools.lib.notion import resolve_token

    monkeypatch.setenv("NOTION_TOKEN", "env-token")
    cfg = _make_config()
    assert resolve_token(cli_token="", config=cfg) == "env-token"


# ─── NotionClient construction ─────────────────────────────────────────────


def test_client_constructs_with_token(fake_notion_module: MagicMock) -> None:
    from tools.lib.notion import NotionClient

    NotionClient(token="secret-xyz")
    fake_notion_module.assert_called_once_with(auth="secret-xyz")


def test_client_passes_workspace_id(fake_notion_module: MagicMock) -> None:
    from tools.lib.notion import NotionClient

    client = NotionClient(token="t", workspace_id="ws-42")
    assert client.workspace_id == "ws-42"


# ─── Missing notion-client library ─────────────────────────────────────────


def test_notion_client_missing_raises_friendly_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When notion-client is NOT installed, constructor must raise
    NotionError (not ImportError) with an install hint."""
    monkeypatch.delitem(sys.modules, "notion_client", raising=False)
    monkeypatch.delitem(sys.modules, "notion_client.errors", raising=False)
    sys.modules.pop("tools.lib.notion", None)

    # Block the import at import-machinery level.
    real_find_spec = sys.meta_path  # noqa: F841

    class _Blocker:
        def find_spec(
            self, name: str, path: object = None, target: object = None
        ) -> None:
            if name == "notion_client" or name.startswith("notion_client."):
                raise ModuleNotFoundError(f"No module named {name!r}")
            return None

    monkeypatch.setattr(sys, "meta_path", [_Blocker(), *sys.meta_path])

    from tools.lib.notion import NotionClient, NotionError

    with pytest.raises(NotionError, match="notion-client"):
        NotionClient(token="t")


# ─── upsert_page ────────────────────────────────────────────────────────────


def test_upsert_creates_when_no_match(fake_notion_module: MagicMock) -> None:
    from tools.lib.notion import NotionClient

    # Configure the fake Client instance: .databases.query returns empty,
    # .pages.create returns the new page.
    fake_client_instance = MagicMock()
    fake_client_instance.databases.query.return_value = {"results": []}
    fake_client_instance.pages.create.return_value = {
        "id": "new-page-id",
        "properties": {},
    }
    fake_notion_module.return_value = fake_client_instance

    client = NotionClient(token="t")
    page = client.upsert_page(
        database_id="db-1",
        life_os_id="sess-42",
        properties={"Title": {"title": [{"text": {"content": "hi"}}]}},
    )

    assert page["id"] == "new-page-id"
    fake_client_instance.pages.create.assert_called_once()
    fake_client_instance.pages.update.assert_not_called()


def test_upsert_updates_when_life_os_id_matches(
    fake_notion_module: MagicMock,
) -> None:
    from tools.lib.notion import NotionClient

    fake_client_instance = MagicMock()
    fake_client_instance.databases.query.return_value = {
        "results": [{"id": "existing-page-id"}]
    }
    fake_client_instance.pages.update.return_value = {
        "id": "existing-page-id",
        "properties": {},
    }
    fake_notion_module.return_value = fake_client_instance

    client = NotionClient(token="t")
    page = client.upsert_page(
        database_id="db-1",
        life_os_id="sess-42",
        properties={},
    )

    assert page["id"] == "existing-page-id"
    fake_client_instance.pages.update.assert_called_once()
    fake_client_instance.pages.create.assert_not_called()


def test_upsert_with_body_appends_children(fake_notion_module: MagicMock) -> None:
    """When body is provided, upsert should also append a paragraph block."""
    from tools.lib.notion import NotionClient

    fake_client_instance = MagicMock()
    fake_client_instance.databases.query.return_value = {"results": []}
    fake_client_instance.pages.create.return_value = {"id": "p1"}
    fake_notion_module.return_value = fake_client_instance

    client = NotionClient(token="t")
    client.upsert_page(
        database_id="db-1",
        life_os_id="sess-1",
        properties={},
        body="Hello from Life OS",
    )
    # Expect blocks.children.append OR children passed to create
    called_with_children = (
        fake_client_instance.blocks.children.append.called
        or "children" in fake_client_instance.pages.create.call_args.kwargs
    )
    assert called_with_children


# ─── Error mapping ──────────────────────────────────────────────────────────


def test_auth_failure_mapped(fake_notion_module: MagicMock) -> None:
    from tools.lib.notion import NotionAuthError, NotionClient

    # Build a fake APIResponseError with code="unauthorized"
    errors_module = sys.modules["notion_client.errors"]
    api_err = errors_module.APIResponseError("bad token")
    api_err.code = "unauthorized"

    fake_client_instance = MagicMock()
    fake_client_instance.databases.query.side_effect = api_err
    fake_notion_module.return_value = fake_client_instance

    client = NotionClient(token="bad")
    with pytest.raises(NotionAuthError):
        client.upsert_page(database_id="db", life_os_id="x", properties={})


def test_rate_limit_mapped(fake_notion_module: MagicMock) -> None:
    from tools.lib.notion import NotionClient, NotionRateLimitError

    errors_module = sys.modules["notion_client.errors"]
    api_err = errors_module.APIResponseError("429")
    api_err.code = "rate_limited"

    fake_client_instance = MagicMock()
    fake_client_instance.databases.query.side_effect = api_err
    fake_notion_module.return_value = fake_client_instance

    client = NotionClient(token="t")
    with pytest.raises(NotionRateLimitError):
        client.upsert_page(database_id="db", life_os_id="x", properties={})


def test_generic_api_error_mapped_to_notion_error(
    fake_notion_module: MagicMock,
) -> None:
    from tools.lib.notion import NotionClient, NotionError

    errors_module = sys.modules["notion_client.errors"]
    api_err = errors_module.APIResponseError("boom")
    api_err.code = "internal_server_error"

    fake_client_instance = MagicMock()
    fake_client_instance.databases.query.side_effect = api_err
    fake_notion_module.return_value = fake_client_instance

    client = NotionClient(token="t")
    with pytest.raises(NotionError):
        client.upsert_page(database_id="db", life_os_id="x", properties={})


# ─── mark_synced ────────────────────────────────────────────────────────────


def test_mark_synced_patches_page(fake_notion_module: MagicMock) -> None:
    from tools.lib.notion import NotionClient

    fake_client_instance = MagicMock()
    fake_client_instance.pages.update.return_value = {"id": "p"}
    fake_notion_module.return_value = fake_client_instance

    client = NotionClient(token="t")
    client.mark_synced("p1")
    fake_client_instance.pages.update.assert_called_once()
    _args, kwargs = fake_client_instance.pages.update.call_args
    assert kwargs.get("page_id") == "p1" or "p1" in str(kwargs)


# ─── Exception taxonomy ────────────────────────────────────────────────────


def test_exception_hierarchy(fake_notion_module: MagicMock) -> None:
    from tools.lib.notion import NotionAuthError, NotionError, NotionRateLimitError

    assert issubclass(NotionAuthError, NotionError)
    assert issubclass(NotionRateLimitError, NotionError)
    assert NotionError is not NotionAuthError


# ─── Sanity: query uses life_os_id filter ──────────────────────────────────


def test_upsert_queries_with_life_os_id_filter(
    fake_notion_module: MagicMock,
) -> None:
    from tools.lib.notion import NotionClient

    fake_client_instance = MagicMock()
    fake_client_instance.databases.query.return_value = {"results": []}
    fake_client_instance.pages.create.return_value = {"id": "p"}
    fake_notion_module.return_value = fake_client_instance

    client = NotionClient(token="t")
    client.upsert_page(
        database_id="db-xyz", life_os_id="evidence-001", properties={}
    )
    _args, kwargs = fake_client_instance.databases.query.call_args
    # Query should target our db_id and filter by life_os_id
    assert "db-xyz" in str(kwargs) or kwargs.get("database_id") == "db-xyz"
    assert "evidence-001" in str(kwargs)


# ─── Silence unused imports ────────────────────────────────────────────────

_ = SimpleNamespace  # keep import if not used directly above
