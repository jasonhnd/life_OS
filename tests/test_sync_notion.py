"""Tests for tools.sync_notion — v1.7 Sprint 5.

Spec: references/tools-spec.md §6.11.

Covers:
 - 3-level token resolution (CLI > NOTION_TOKEN env > config env var)
 - --since filter on the sync log
 - per-page try/except -- one failure does not abort others
 - exit codes: 0 all-synced / 1 any-failed / 2 auth-error / 3 network-unreachable
 - sync log append with timestamp + per-page result

All tests mock ``tools.lib.notion.NotionClient`` -- no real HTTP.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# ``tools.lib.notion`` can be reloaded by other test modules (they stub
# out ``notion_client`` via ``sys.modules.pop(...)``). Importing the
# exception classes at module scope would capture a stale class object
# that no longer matches the one ``tools.sync_notion._classify_failure``
# sees at call time. Resolve them lazily inside each test instead.


def _auth_error_cls() -> type[Exception]:
    from tools.lib import notion

    return notion.NotionAuthError


def _notion_error_cls() -> type[Exception]:
    from tools.lib import notion

    return notion.NotionError


def _write_log(root: Path, content: str) -> Path:
    meta = root / "_meta"
    meta.mkdir(parents=True, exist_ok=True)
    log = meta / "notion-sync-log.md"
    log.write_text(content, encoding="utf-8")
    return log


# ─── parse_pending_entries ──────────────────────────────────────────────────


class TestParsePendingEntries:
    def test_empty_log_returns_empty(self, tmp_path: Path) -> None:
        from tools.sync_notion import parse_pending_entries

        assert parse_pending_entries(tmp_path / "nope.md") == []

    def test_parses_pending_entries(self, tmp_path: Path) -> None:
        from tools.sync_notion import parse_pending_entries

        log = _write_log(
            tmp_path,
            "# Notion sync log\n"
            "\n"
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | session-001 | db-sessions | pending |\n"
            "| 2026-04-20 | session-002 | db-sessions | failed |\n"
            "| 2026-04-19 | session-003 | db-sessions | synced |\n",
        )
        entries = parse_pending_entries(log)
        # synced entries excluded; pending + failed included.
        ids = [e.life_os_id for e in entries]
        assert ids == ["session-001", "session-002"]

    def test_filters_by_since(self, tmp_path: Path) -> None:
        from tools.sync_notion import parse_pending_entries

        log = _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-18 | old | db | pending |\n"
            "| 2026-04-20 | new | db | pending |\n",
        )
        entries = parse_pending_entries(log, since=date(2026, 4, 19))
        ids = [e.life_os_id for e in entries]
        assert ids == ["new"]


# ─── append_log_result ──────────────────────────────────────────────────────


class TestAppendLogResult:
    def test_appends_success_row(self, tmp_path: Path) -> None:
        from tools.sync_notion import SyncEntry, append_log_result

        log = _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n",
        )
        append_log_result(
            log,
            SyncEntry(
                date=date(2026, 4, 20),
                life_os_id="s1",
                database_id="db",
                status="pending",
            ),
            new_status="synced",
            message="",
        )
        content = log.read_text(encoding="utf-8")
        assert "synced" in content
        assert "s1" in content

    def test_appends_failure_reason(self, tmp_path: Path) -> None:
        from tools.sync_notion import SyncEntry, append_log_result

        log = _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n",
        )
        append_log_result(
            log,
            SyncEntry(
                date=date(2026, 4, 20),
                life_os_id="s1",
                database_id="db",
                status="pending",
            ),
            new_status="failed",
            message="rate_limited",
        )
        content = log.read_text(encoding="utf-8")
        assert "failed" in content
        assert "rate_limited" in content


# ─── run() — exit codes ─────────────────────────────────────────────────────


class _FakeClient:
    """Minimal stand-in for NotionClient used by sync_notion tests."""

    def __init__(self, *, behaviors: dict[str, Any] | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self._behaviors = behaviors or {}

    def upsert_page(
        self,
        *,
        database_id: str,
        life_os_id: str,
        properties: dict[str, Any],
        body: str | None = None,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "database_id": database_id,
                "life_os_id": life_os_id,
                "properties": properties,
                "body": body,
            }
        )
        behavior = self._behaviors.get(life_os_id)
        if isinstance(behavior, Exception):
            raise behavior
        return {"id": f"notion-{life_os_id}"}


class TestRun:
    def test_all_synced_exit_zero(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools import sync_notion

        _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n"
            "| 2026-04-20 | s2 | db | pending |\n",
        )
        fake = _FakeClient()
        monkeypatch.setenv("NOTION_TOKEN", "stub")
        with patch.object(sync_notion, "_build_client", return_value=fake):
            rc = sync_notion.run(
                root=tmp_path,
                cli_token=None,
                since=None,
                verbose=False,
            )
        assert rc == 0
        assert len(fake.calls) == 2

    def test_any_page_failed_exit_one(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools import sync_notion

        _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n"
            "| 2026-04-20 | s2 | db | pending |\n",
        )
        fake = _FakeClient(
            behaviors={"s2": _notion_error_cls()("transient API error")}
        )
        monkeypatch.setenv("NOTION_TOKEN", "stub")
        with patch.object(sync_notion, "_build_client", return_value=fake):
            rc = sync_notion.run(
                root=tmp_path,
                cli_token=None,
                since=None,
                verbose=False,
            )
        assert rc == 1
        # Both pages were tried (per-page try/except is independent).
        assert len(fake.calls) == 2

    def test_auth_failure_exit_two(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools import sync_notion

        _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n",
        )
        monkeypatch.delenv("NOTION_TOKEN", raising=False)
        # No token source → NotionAuthError inside resolve_token.
        rc = sync_notion.run(
            root=tmp_path,
            cli_token=None,
            since=None,
            verbose=False,
        )
        assert rc == 2

    def test_auth_failure_from_notion_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools import sync_notion

        _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n",
        )
        fake = _FakeClient(
            behaviors={"s1": _auth_error_cls()("bad token")}
        )
        monkeypatch.setenv("NOTION_TOKEN", "stub")
        with patch.object(sync_notion, "_build_client", return_value=fake):
            rc = sync_notion.run(
                root=tmp_path,
                cli_token=None,
                since=None,
                verbose=False,
            )
        assert rc == 2

    def test_network_failure_exit_three(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools import sync_notion

        _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n",
        )
        fake = _FakeClient(
            behaviors={"s1": OSError("network unreachable")}
        )
        monkeypatch.setenv("NOTION_TOKEN", "stub")
        with patch.object(sync_notion, "_build_client", return_value=fake):
            rc = sync_notion.run(
                root=tmp_path,
                cli_token=None,
                since=None,
                verbose=False,
            )
        assert rc == 3

    def test_no_log_exit_zero(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Nothing to sync = clean success; do not hit the network."""
        from tools import sync_notion

        monkeypatch.setenv("NOTION_TOKEN", "stub")
        fake = _FakeClient()
        with patch.object(sync_notion, "_build_client", return_value=fake):
            rc = sync_notion.run(
                root=tmp_path,
                cli_token=None,
                since=None,
                verbose=False,
            )
        assert rc == 0
        assert fake.calls == []


# ─── Token resolution integration ───────────────────────────────────────────


class TestTokenResolutionIntegration:
    def test_cli_token_wins(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools import sync_notion

        _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n",
        )
        monkeypatch.setenv("NOTION_TOKEN", "env-token")
        captured_tokens: list[str] = []

        def spy_build_client(token: str, workspace_id: str | None) -> _FakeClient:
            captured_tokens.append(token)
            return _FakeClient()

        with patch.object(sync_notion, "_build_client", side_effect=spy_build_client):
            rc = sync_notion.run(
                root=tmp_path,
                cli_token="from-cli",
                since=None,
                verbose=False,
            )
        assert rc == 0
        assert captured_tokens == ["from-cli"]

    def test_falls_back_to_notion_token_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools import sync_notion

        _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-20 | s1 | db | pending |\n",
        )
        monkeypatch.setenv("NOTION_TOKEN", "env-token")
        captured: list[str] = []

        def spy_build_client(token: str, workspace_id: str | None) -> _FakeClient:
            captured.append(token)
            return _FakeClient()

        with patch.object(sync_notion, "_build_client", side_effect=spy_build_client):
            rc = sync_notion.run(
                root=tmp_path,
                cli_token=None,
                since=None,
                verbose=False,
            )
        assert rc == 0
        assert captured == ["env-token"]


# ─── --since filter ─────────────────────────────────────────────────────────


class TestSinceFilter:
    def test_since_filters_old_entries(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools import sync_notion

        _write_log(
            tmp_path,
            "| date | life_os_id | database_id | status |\n"
            "| --- | --- | --- | --- |\n"
            "| 2026-04-18 | old | db | pending |\n"
            "| 2026-04-20 | new | db | pending |\n",
        )
        fake = _FakeClient()
        monkeypatch.setenv("NOTION_TOKEN", "stub")
        with patch.object(sync_notion, "_build_client", return_value=fake):
            rc = sync_notion.run(
                root=tmp_path,
                cli_token=None,
                since=date(2026, 4, 19),
                verbose=False,
            )
        assert rc == 0
        synced_ids = [c["life_os_id"] for c in fake.calls]
        assert synced_ids == ["new"]
