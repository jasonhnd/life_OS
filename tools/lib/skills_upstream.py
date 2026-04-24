"""Skill upstream lookup helpers for Life OS Skill Observability.

This module is intentionally CLI-agnostic: callers get structured status data
that can be rendered into the fixed skills table vocabulary later.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast

DEFAULT_CACHE_TTL_SECONDS = 24 * 60 * 60
DEFAULT_TIMEOUT_SECONDS = 5.0
ENV_CACHE_PATH = "LIFE_OS_SKILLS_UPSTREAM_CACHE"

SourceKind = Literal["github", "npm", "pypi", "local", "unsupported"]
CheckStatus = Literal["ok", "local", "check_failed"]
CacheState = Literal["none", "fresh", "stale"]


class UpstreamCacheCorruptError(Exception):
    """Raised when the upstream cache cannot be parsed as trusted data."""


class UpstreamResponseError(Exception):
    """Raised internally for malformed live upstream responses."""


@dataclass(frozen=True)
class UpstreamSource:
    """Parsed representation of a source URL."""

    raw: str
    kind: SourceKind
    url: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class CacheEntry:
    """One persisted upstream evidence record."""

    latest_version: str
    fetched_at: datetime
    url: str

    def age_seconds(self, now: datetime) -> float:
        """Return cache age in seconds relative to ``now``."""
        return max(0.0, (_as_utc(now) - _as_utc(self.fetched_at)).total_seconds())

    def is_fresh(
        self,
        now: datetime,
        *,
        ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    ) -> bool:
        """Return whether this cache entry is within the configured TTL."""
        return self.age_seconds(now) <= ttl_seconds


@dataclass(frozen=True)
class UpstreamCache:
    """In-memory upstream cache."""

    entries: dict[str, CacheEntry]

    def get(self, source: str) -> CacheEntry | None:
        return self.entries.get(source)

    def with_entry(self, source: str, entry: CacheEntry) -> UpstreamCache:
        entries = dict(self.entries)
        entries[source] = entry
        return UpstreamCache(entries=entries)


@dataclass(frozen=True)
class UpstreamCheckResult:
    """Structured outcome for one source lookup."""

    source: str
    kind: SourceKind
    status: CheckStatus
    latest_version: str | None = None
    url: str | None = None
    cache_state: CacheState = "none"
    cache_age_seconds: float | None = None
    from_cache: bool = False
    reliable: bool = False
    used_network: bool = False
    error: str | None = None


def default_cache_path(env: Mapping[str, str] | None = None) -> Path:
    """Return the configured upstream cache path."""
    source_env = os.environ if env is None else env
    override = source_env.get(ENV_CACHE_PATH)
    if override:
        return Path(override).expanduser()
    return Path.home() / ".cache" / "life-os" / "skills-upstream.json"


def parse_upstream_source(source: str) -> UpstreamSource:
    """Parse a supported Skill Observability upstream source URL."""
    if source.startswith("github://"):
        repo_path = source.removeprefix("github://").strip("/")
        parts = repo_path.split("/")
        if len(parts) != 2 or not all(parts):
            return UpstreamSource(source, "unsupported", error="invalid github source")
        owner = urllib.parse.quote(parts[0], safe="")
        repo = urllib.parse.quote(parts[1], safe="")
        return UpstreamSource(
            raw=source,
            kind="github",
            url=f"https://api.github.com/repos/{owner}/{repo}/releases/latest",
        )

    if source.startswith("npm://"):
        package_name = source.removeprefix("npm://").strip()
        if not package_name:
            return UpstreamSource(source, "unsupported", error="invalid npm source")
        package_path = urllib.parse.quote(package_name, safe="@")
        return UpstreamSource(
            raw=source,
            kind="npm",
            url=f"https://registry.npmjs.org/{package_path}/latest",
        )

    if source.startswith("pypi://"):
        package_name = source.removeprefix("pypi://").strip()
        if not package_name or "/" in package_name:
            return UpstreamSource(source, "unsupported", error="invalid pypi source")
        package_path = urllib.parse.quote(package_name, safe="")
        return UpstreamSource(
            raw=source,
            kind="pypi",
            url=f"https://pypi.org/pypi/{package_path}/json",
        )

    if source.startswith("local://"):
        return UpstreamSource(raw=source, kind="local")

    return UpstreamSource(raw=source, kind="unsupported", error="unsupported source")


def load_upstream_cache(
    cache_path: Path | str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> UpstreamCache:
    """Load the upstream cache, raising if the cache exists but is corrupt."""
    path = _resolve_cache_path(cache_path, env=env)
    if not path.exists():
        return UpstreamCache(entries={})

    try:
        raw = path.read_text(encoding="utf-8")
        parsed: object = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise UpstreamCacheCorruptError(f"Cannot parse upstream cache at {path}") from exc

    if not isinstance(parsed, dict):
        raise UpstreamCacheCorruptError(f"Upstream cache at {path} must be an object")

    entries_obj = parsed.get("entries")
    if not isinstance(entries_obj, dict):
        raise UpstreamCacheCorruptError(f"Upstream cache at {path} must contain an entries object")

    entries: dict[str, CacheEntry] = {}
    for key_obj, value_obj in entries_obj.items():
        if not isinstance(key_obj, str) or not isinstance(value_obj, dict):
            raise UpstreamCacheCorruptError(f"Upstream cache at {path} contains an invalid entry")
        value = cast(dict[str, object], value_obj)
        entries[key_obj] = _cache_entry_from_json(value, path=path)

    return UpstreamCache(entries=entries)


def write_upstream_cache(
    cache: UpstreamCache,
    cache_path: Path | str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> None:
    """Persist the upstream cache as JSON."""
    path = _resolve_cache_path(cache_path, env=env)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": 1,
        "entries": {
            source: {
                "latest_version": entry.latest_version,
                "fetched_at": _as_utc(entry.fetched_at).isoformat(),
                "url": entry.url,
            }
            for source, entry in sorted(cache.entries.items())
        },
    }
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_path.replace(path)


class UpstreamChecker:
    """Perform cached, anonymous upstream version checks."""

    def __init__(
        self,
        *,
        cache_path: Path | str | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
        now: datetime | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self.cache_path = _resolve_cache_path(cache_path, env=env)
        self.timeout_seconds = timeout_seconds
        self.ttl_seconds = ttl_seconds
        self._fixed_now = _as_utc(now) if now is not None else None

    def check(self, source: str, *, offline: bool = False) -> UpstreamCheckResult:
        """Check one upstream source.

        Runtime upstream failures are returned as ``check_failed``. Corrupt cache
        data raises ``UpstreamCacheCorruptError`` so the CLI can map it to exit 3.
        """
        parsed_source = parse_upstream_source(source)
        if parsed_source.kind == "local":
            return UpstreamCheckResult(
                source=source,
                kind="local",
                status="local",
                reliable=True,
            )
        if parsed_source.kind == "unsupported":
            return UpstreamCheckResult(
                source=source,
                kind="unsupported",
                status="check_failed",
                error=parsed_source.error,
            )

        now = self._now()
        cache = load_upstream_cache(self.cache_path)
        cache_entry = cache.get(source)
        cache_state, cache_age = _cache_state(cache_entry, now, self.ttl_seconds)

        if offline:
            return UpstreamCheckResult(
                source=source,
                kind=parsed_source.kind,
                status="check_failed",
                latest_version=cache_entry.latest_version if cache_entry else None,
                url=parsed_source.url,
                cache_state=cache_state,
                cache_age_seconds=cache_age,
                from_cache=cache_entry is not None,
                reliable=False,
                used_network=False,
                error="offline",
            )

        if cache_entry is not None and cache_state == "fresh":
            return UpstreamCheckResult(
                source=source,
                kind=parsed_source.kind,
                status="ok",
                latest_version=cache_entry.latest_version,
                url=cache_entry.url,
                cache_state="fresh",
                cache_age_seconds=cache_age,
                from_cache=True,
                reliable=True,
                used_network=False,
            )

        if parsed_source.url is None:
            return UpstreamCheckResult(
                source=source,
                kind=parsed_source.kind,
                status="check_failed",
                cache_state=cache_state,
                cache_age_seconds=cache_age,
                from_cache=cache_entry is not None,
                error="missing upstream URL",
            )

        try:
            latest_version = self._fetch_latest_version(parsed_source)
        except (
            OSError,
            TimeoutError,
            UnicodeDecodeError,
            urllib.error.URLError,
            json.JSONDecodeError,
            UpstreamResponseError,
        ) as exc:
            return UpstreamCheckResult(
                source=source,
                kind=parsed_source.kind,
                status="check_failed",
                latest_version=cache_entry.latest_version if cache_entry else None,
                url=parsed_source.url,
                cache_state=cache_state,
                cache_age_seconds=cache_age,
                from_cache=cache_entry is not None,
                reliable=False,
                used_network=True,
                error=f"{type(exc).__name__}: {exc}",
            )

        new_entry = CacheEntry(
            latest_version=latest_version,
            fetched_at=now,
            url=parsed_source.url,
        )
        write_upstream_cache(cache.with_entry(source, new_entry), self.cache_path)
        return UpstreamCheckResult(
            source=source,
            kind=parsed_source.kind,
            status="ok",
            latest_version=latest_version,
            url=parsed_source.url,
            cache_state="fresh",
            cache_age_seconds=0.0,
            from_cache=False,
            reliable=True,
            used_network=True,
        )

    def check_many(
        self,
        sources: list[str],
        *,
        offline: bool = False,
    ) -> list[UpstreamCheckResult]:
        """Check multiple sources, preserving order."""
        return [self.check(source, offline=offline) for source in sources]

    def _fetch_latest_version(self, source: UpstreamSource) -> str:
        if source.url is None:
            raise UpstreamResponseError("missing upstream URL")

        request = urllib.request.Request(
            source.url,
            headers={
                "Accept": "application/json",
                "User-Agent": "life-os-skills-upstream/1.7.1",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = _json_object_from_bytes(response.read())

        if source.kind == "github":
            return _required_string(payload, ["tag_name"], source=source.raw)
        if source.kind == "npm":
            return _required_string(payload, ["version"], source=source.raw)
        if source.kind == "pypi":
            return _required_string(payload, ["info", "version"], source=source.raw)

        raise UpstreamResponseError(f"unsupported source kind: {source.kind}")

    def _now(self) -> datetime:
        if self._fixed_now is not None:
            return self._fixed_now
        return datetime.now(UTC)


def _resolve_cache_path(
    cache_path: Path | str | None,
    *,
    env: Mapping[str, str] | None = None,
) -> Path:
    if cache_path is not None:
        return Path(cache_path).expanduser()
    return default_cache_path(env)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _parse_datetime(value: object, *, path: Path) -> datetime:
    if not isinstance(value, str):
        raise UpstreamCacheCorruptError(f"Upstream cache at {path} has a non-string fetched_at")
    try:
        return _as_utc(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError as exc:
        raise UpstreamCacheCorruptError(
            f"Upstream cache at {path} has an invalid fetched_at"
        ) from exc


def _cache_entry_from_json(value: dict[str, object], *, path: Path) -> CacheEntry:
    latest_version = value.get("latest_version")
    url = value.get("url")
    if not isinstance(latest_version, str) or not latest_version:
        raise UpstreamCacheCorruptError(f"Upstream cache at {path} has an invalid latest_version")
    if not isinstance(url, str) or not url:
        raise UpstreamCacheCorruptError(f"Upstream cache at {path} has an invalid url")
    fetched_at = _parse_datetime(value.get("fetched_at"), path=path)
    return CacheEntry(latest_version=latest_version, fetched_at=fetched_at, url=url)


def _cache_state(
    entry: CacheEntry | None,
    now: datetime,
    ttl_seconds: int,
) -> tuple[CacheState, float | None]:
    if entry is None:
        return "none", None
    age = entry.age_seconds(now)
    if age <= ttl_seconds:
        return "fresh", age
    return "stale", age


def _json_object_from_bytes(raw: bytes) -> dict[str, Any]:
    parsed: object = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise UpstreamResponseError("upstream response must be a JSON object")
    return cast(dict[str, Any], parsed)


def _required_string(
    payload: dict[str, Any],
    path: list[str],
    *,
    source: str,
) -> str:
    current: object = payload
    for key in path:
        if not isinstance(current, dict):
            raise UpstreamResponseError(f"{source} response missing {'.'.join(path)}")
        current = cast(dict[str, object], current).get(key)
    if not isinstance(current, str) or not current:
        raise UpstreamResponseError(f"{source} response missing {'.'.join(path)}")
    return current


__all__ = [
    "CacheEntry",
    "CacheState",
    "CheckStatus",
    "DEFAULT_CACHE_TTL_SECONDS",
    "DEFAULT_TIMEOUT_SECONDS",
    "ENV_CACHE_PATH",
    "SourceKind",
    "UpstreamCache",
    "UpstreamCacheCorruptError",
    "UpstreamCheckResult",
    "UpstreamChecker",
    "UpstreamSource",
    "default_cache_path",
    "load_upstream_cache",
    "parse_upstream_source",
    "write_upstream_cache",
]
