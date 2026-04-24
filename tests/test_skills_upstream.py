"""Tests for tools.lib.skills_upstream."""

from __future__ import annotations

import json
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import TracebackType
from typing import Any

import pytest

from tools.lib import skills_upstream as upstream

NOW = datetime(2026, 4, 24, 12, 0, tzinfo=UTC)


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_github_latest_release_is_parsed_and_cached(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "skills-upstream.json"
    captured: dict[str, Any] = {}

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        assert isinstance(request, urllib.request.Request)
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return FakeResponse({"tag_name": "v1.2.3"})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = upstream.UpstreamChecker(cache_path=cache_path, now=NOW).check("github://octo/demo")

    assert result.status == "ok"
    assert result.kind == "github"
    assert result.latest_version == "v1.2.3"
    assert result.used_network is True
    assert result.reliable is True
    assert captured == {
        "url": "https://api.github.com/repos/octo/demo/releases/latest",
        "timeout": 5.0,
    }
    saved = upstream.load_upstream_cache(cache_path)
    assert saved.entries["github://octo/demo"].latest_version == "v1.2.3"


def test_npm_latest_version_is_parsed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, str] = {}

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        assert isinstance(request, urllib.request.Request)
        captured["url"] = request.full_url
        return FakeResponse({"version": "2.0.0"})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = upstream.UpstreamChecker(cache_path=tmp_path / "cache.json", now=NOW).check(
        "npm://life-os-skill"
    )

    assert result.status == "ok"
    assert result.kind == "npm"
    assert result.latest_version == "2.0.0"
    assert captured["url"] == "https://registry.npmjs.org/life-os-skill/latest"


def test_pypi_latest_version_is_parsed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, str] = {}

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        assert isinstance(request, urllib.request.Request)
        captured["url"] = request.full_url
        return FakeResponse({"info": {"version": "3.1.4"}})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = upstream.UpstreamChecker(cache_path=tmp_path / "cache.json", now=NOW).check(
        "pypi://life-os-skill"
    )

    assert result.status == "ok"
    assert result.kind == "pypi"
    assert result.latest_version == "3.1.4"
    assert captured["url"] == "https://pypi.org/pypi/life-os-skill/json"


def test_local_source_does_not_use_network(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fail_urlopen(request: object, timeout: float) -> FakeResponse:
        raise AssertionError("local sources must not use network")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    result = upstream.UpstreamChecker(cache_path=tmp_path / "cache.json", now=NOW).check(
        "local://scratchpad"
    )

    assert result.status == "local"
    assert result.kind == "local"
    assert result.latest_version is None
    assert result.used_network is False
    assert result.reliable is True


def test_fresh_cache_is_used_without_network(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "cache.json"
    upstream.write_upstream_cache(
        upstream.UpstreamCache(
            entries={
                "npm://cached-skill": upstream.CacheEntry(
                    latest_version="1.4.0",
                    fetched_at=NOW - timedelta(hours=1),
                    url="https://registry.npmjs.org/cached-skill/latest",
                )
            }
        ),
        cache_path,
    )

    def fail_urlopen(request: object, timeout: float) -> FakeResponse:
        raise AssertionError("fresh cache should avoid network")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    result = upstream.UpstreamChecker(cache_path=cache_path, now=NOW).check("npm://cached-skill")

    assert result.status == "ok"
    assert result.latest_version == "1.4.0"
    assert result.cache_state == "fresh"
    assert result.cache_age_seconds == 3600.0
    assert result.from_cache is True
    assert result.used_network is False
    assert result.reliable is True


def test_stale_cache_is_returned_as_evidence_when_live_check_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "cache.json"
    upstream.write_upstream_cache(
        upstream.UpstreamCache(
            entries={
                "github://octo/stale": upstream.CacheEntry(
                    latest_version="v9.9.9",
                    fetched_at=NOW - timedelta(days=2),
                    url="https://api.github.com/repos/octo/stale/releases/latest",
                )
            }
        ),
        cache_path,
    )

    def timeout_urlopen(request: object, timeout: float) -> FakeResponse:
        raise TimeoutError("slow upstream")

    monkeypatch.setattr(urllib.request, "urlopen", timeout_urlopen)

    result = upstream.UpstreamChecker(cache_path=cache_path, now=NOW).check("github://octo/stale")

    assert result.status == "check_failed"
    assert result.latest_version == "v9.9.9"
    assert result.cache_state == "stale"
    assert result.cache_age_seconds == 172800.0
    assert result.from_cache is True
    assert result.used_network is True
    assert result.reliable is False
    assert "TimeoutError" in str(result.error)


def test_timeout_without_cache_is_graceful_check_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def timeout_urlopen(request: object, timeout: float) -> FakeResponse:
        raise TimeoutError("slow upstream")

    monkeypatch.setattr(urllib.request, "urlopen", timeout_urlopen)

    result = upstream.UpstreamChecker(cache_path=tmp_path / "cache.json", now=NOW).check(
        "pypi://slow-skill"
    )

    assert result.status == "check_failed"
    assert result.latest_version is None
    assert result.cache_state == "none"
    assert result.from_cache is False
    assert result.used_network is True
    assert result.reliable is False


def test_offline_uses_cache_evidence_without_network(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "cache.json"
    upstream.write_upstream_cache(
        upstream.UpstreamCache(
            entries={
                "npm://offline-skill": upstream.CacheEntry(
                    latest_version="4.0.0",
                    fetched_at=NOW - timedelta(days=3),
                    url="https://registry.npmjs.org/offline-skill/latest",
                )
            }
        ),
        cache_path,
    )

    def fail_urlopen(request: object, timeout: float) -> FakeResponse:
        raise AssertionError("offline checks must not use network")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    result = upstream.UpstreamChecker(cache_path=cache_path, now=NOW).check(
        "npm://offline-skill",
        offline=True,
    )

    assert result.status == "check_failed"
    assert result.latest_version == "4.0.0"
    assert result.cache_state == "stale"
    assert result.from_cache is True
    assert result.used_network is False
    assert result.error == "offline"


def test_corrupt_cache_is_detectable_as_data_source_corruption(tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.json"
    cache_path.write_text("{not-json", encoding="utf-8")

    checker = upstream.UpstreamChecker(cache_path=cache_path, now=NOW)
    with pytest.raises(upstream.UpstreamCacheCorruptError):
        checker.check("npm://any-skill")


def test_cache_path_can_be_overridden_by_env(tmp_path: Path) -> None:
    cache_path = tmp_path / "custom-cache.json"
    env = {upstream.ENV_CACHE_PATH: str(cache_path)}

    assert upstream.default_cache_path(env) == cache_path
    assert upstream.UpstreamChecker(env=env).cache_path == cache_path
