#!/usr/bin/env python3
"""Background web fetch into inbox — v1.7 Sprint 4 / R3.5.

Contract: references/tools-spec.md §6.4.

  - ``httpx.get`` + ``markdownify`` conversion
  - ``urllib.robotparser`` enforces robots.txt (spec §6.4 hard requirement)
  - user-agent ``LifeOS-research/1.7 (+local-tool; backend=<name>)``
  - ``--depth`` N controls link-following (0=search page only,
    1=each top result, 2=one more layer of outbound links)
  - ``--max-pages`` hard cap on total fetches (default 10)
  - Slug: ASCII transliterate → lowercase → hyphenate; non-ASCII falls
    back to SHA-1 first 8 chars
  - On failure: writes a partial file with ``incomplete: true`` and
    exits 1. Empty/search-only runs exit 0.
  - NO LLM summarization (user decision #16).

Backends (``--backend``):
  - ``searxng`` (default) — points at the SEARXNG_URL env instance,
    falling back to ``https://searx.be``. JSON response.
  - ``brave`` — api.search.brave.com. Requires BRAVE_API_KEY env var
    (if missing, explicitly selecting brave produces a clear error;
    other backends are unaffected).
  - ``ddg`` / ``ddg-html`` / ``ddg-lite`` — DuckDuckGo endpoints.
    **Demoted to manual fallback on 2026-04-21** because their
    robots.txt now disallows every relevant path for all user-agents.
    Kept for users running behind a permissive proxy or an older
    mirror. Not recommended.

Dependencies (optional-dep group ``research``): ``httpx``, ``markdownify``.
Imports are lazy so tests can inject mock modules via ``sys.modules``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.robotparser import RobotFileParser

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ─── Constants ──────────────────────────────────────────────────────────────

_UA_BASE = "LifeOS-research/1.7 (+local-tool"
_DEFAULT_DEPTH = 1
_DEFAULT_MAX_PAGES = 10
_SLUG_HASH_LEN = 8

# SearXNG default public instance when SEARXNG_URL env is unset. Users
# should self-host or pin a trusted mirror for real workloads.
_SEARXNG_DEFAULT_INSTANCE = "https://searx.be"

# DuckDuckGo result-link class marker. This is resilient to reasonable UI
# tweaks but we still degrade gracefully: if no matches are found we fall
# back to any absolute-href `<a>` on the page.
_RESULT_LINK_RE = re.compile(
    r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"',
    re.IGNORECASE,
)
_GENERIC_LINK_RE = re.compile(r'<a[^>]*href="(https?://[^"]+)"', re.IGNORECASE)

# Slug cleanup: whitespace and punctuation collapse to a single hyphen.
_SLUG_CLEANUP_RE = re.compile(r"[^a-z0-9]+")


# ─── Data types ─────────────────────────────────────────────────────────────


@dataclass
class ResearchResult:
    """Outcome of a research run."""

    query: str
    depth: int
    output_path: Path
    search_url: str
    fetched_urls: list[str] = field(default_factory=list)
    incomplete: bool = False
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BackendSpec:
    """Describes a search backend.

    Each backend exposes the same 4 hooks so the main driver stays
    backend-agnostic:

    - ``build_url(query)`` returns the search URL to GET.
    - ``request_headers()`` returns extra headers (API keys etc.).
    - ``parse_result_urls(body)`` extracts layer-1 URLs from the search
      response (JSON for searxng/brave, HTML for ddg*).
    - ``precheck()`` returns an error string if the backend can't run
      (e.g. missing API key), or ``None`` on success.
    """

    name: str
    build_url: Callable[[str], str]
    request_headers: Callable[[], dict[str, str]]
    parse_result_urls: Callable[[str], list[str]]
    precheck: Callable[[], str | None]


# ─── Slug generation ────────────────────────────────────────────────────────


def _make_slug(query: str) -> str:
    """Transliterate a query to ASCII-only kebab-case.

    Falls back to the first 8 hex chars of the SHA-1 of the original query
    when no ASCII characters survive (e.g. pure CJK).
    """
    normalized = unicodedata.normalize("NFKD", query)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    cleaned = _SLUG_CLEANUP_RE.sub("-", ascii_only).strip("-")
    if cleaned:
        return cleaned
    return hashlib.sha1(query.encode("utf-8")).hexdigest()[:_SLUG_HASH_LEN]


# ─── User-agent ─────────────────────────────────────────────────────────────


def _user_agent(backend_name: str) -> str:
    """Build the UA string for a given backend, for server-side provenance."""
    return f"{_UA_BASE}; backend={backend_name})"


# ─── Backend: SearXNG ───────────────────────────────────────────────────────


def _searxng_base_url() -> str:
    """Return the SearXNG instance URL (env override → default)."""
    raw = os.environ.get("SEARXNG_URL", "").strip()
    return raw.rstrip("/") if raw else _SEARXNG_DEFAULT_INSTANCE


def _searxng_build_url(query: str) -> str:
    return f"{_searxng_base_url()}/search?q={_encode_query(query)}&format=json"


def _searxng_headers() -> dict[str, str]:
    # Content is JSON; prefer it explicitly.
    return {"Accept": "application/json"}


def _searxng_parse(body: str) -> list[str]:
    """Extract ``results[*].url`` from a SearXNG JSON response."""
    urls: list[str] = []
    try:
        payload = json.loads(body)
    except (ValueError, TypeError):
        return urls
    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list):
        return urls
    for row in results:
        if not isinstance(row, dict):
            continue
        url = row.get("url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            urls.append(url)
    return urls


def _searxng_precheck() -> str | None:
    # SearXNG has no required credentials; always runnable.
    return None


# ─── Backend: Brave Search API ──────────────────────────────────────────────


_BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


def _brave_build_url(query: str) -> str:
    return f"{_BRAVE_SEARCH_URL}?q={_encode_query(query)}"


def _brave_headers() -> dict[str, str]:
    key = os.environ.get("BRAVE_API_KEY", "")
    headers: dict[str, str] = {"Accept": "application/json"}
    if key:
        headers["X-Subscription-Token"] = key
    return headers


def _brave_parse(body: str) -> list[str]:
    """Extract ``web.results[*].url`` from a Brave API JSON response."""
    urls: list[str] = []
    try:
        payload = json.loads(body)
    except (ValueError, TypeError):
        return urls
    web = payload.get("web") if isinstance(payload, dict) else None
    if not isinstance(web, dict):
        return urls
    results = web.get("results")
    if not isinstance(results, list):
        return urls
    for row in results:
        if not isinstance(row, dict):
            continue
        url = row.get("url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            urls.append(url)
    return urls


def _brave_precheck() -> str | None:
    if not os.environ.get("BRAVE_API_KEY", "").strip():
        return (
            "BRAVE_API_KEY env var is required for --backend brave. "
            "Sign up at https://brave.com/search/api/ (free tier: 2000 "
            "queries/month) and export the key."
        )
    return None


# ─── Backend: DuckDuckGo (demoted, kept as manual fallback) ─────────────────


_DDG_TEMPLATES: dict[str, str] = {
    "ddg": "https://duckduckgo.com/?q={query}&format=json&no_html=1",
    "ddg-html": "https://html.duckduckgo.com/html/?q={query}",
    "ddg-lite": "https://lite.duckduckgo.com/lite/?q={query}",
}


def _ddg_build_url_factory(key: str) -> Callable[[str], str]:
    tpl = _DDG_TEMPLATES[key]

    def _build(query: str) -> str:
        return tpl.format(query=_encode_query(query))

    return _build


def _ddg_headers() -> dict[str, str]:
    return {}


def _ddg_parse(body: str) -> list[str]:
    """Extract primary result URLs from a DuckDuckGo HTML page.

    The JSON Instant Answer endpoint does not return a result list,
    so depth>=1 runs against ``ddg`` typically fetch only the search
    page. ``ddg-html`` / ``ddg-lite`` still expose classic link markup.
    """
    urls = [_unescape(u) for u in _RESULT_LINK_RE.findall(body)]
    if urls:
        return urls
    return [_unescape(u) for u in _GENERIC_LINK_RE.findall(body)]


def _ddg_precheck() -> str | None:
    return None


# ─── Backend registry ───────────────────────────────────────────────────────


def _build_backend_registry() -> dict[str, BackendSpec]:
    registry: dict[str, BackendSpec] = {
        "searxng": BackendSpec(
            name="searxng",
            build_url=_searxng_build_url,
            request_headers=_searxng_headers,
            parse_result_urls=_searxng_parse,
            precheck=_searxng_precheck,
        ),
        "brave": BackendSpec(
            name="brave",
            build_url=_brave_build_url,
            request_headers=_brave_headers,
            parse_result_urls=_brave_parse,
            precheck=_brave_precheck,
        ),
    }
    for ddg_key in _DDG_TEMPLATES:
        registry[ddg_key] = BackendSpec(
            name=ddg_key,
            build_url=_ddg_build_url_factory(ddg_key),
            request_headers=_ddg_headers,
            parse_result_urls=_ddg_parse,
            precheck=_ddg_precheck,
        )
    return registry


_BACKENDS: dict[str, BackendSpec] = _build_backend_registry()
_DEFAULT_BACKEND = "searxng"


# ─── robots.txt ─────────────────────────────────────────────────────────────


class _RobotsCache:
    """Per-run cache of parsed robots.txt rules keyed by (scheme, netloc)."""

    def __init__(
        self,
        fetch_text: Callable[[str], str | None],
        *,
        user_agent: str,
    ) -> None:
        self._fetch_text = fetch_text
        self._user_agent = user_agent
        self._cache: dict[str, RobotFileParser | None] = {}

    def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        host_key = f"{parsed.scheme}://{parsed.netloc}"
        if host_key in self._cache:
            parser = self._cache[host_key]
        else:
            parser = self._load(host_key)
            self._cache[host_key] = parser
        if parser is None:
            return True  # absent/errored robots.txt → assume allowed
        return parser.can_fetch(self._user_agent, url)

    def _load(self, host_key: str) -> RobotFileParser | None:
        robots_url = f"{host_key}/robots.txt"
        text = self._fetch_text(robots_url)
        if text is None:
            return None
        rp = RobotFileParser()
        rp.parse(text.splitlines())
        return rp


# ─── HTTP fetch layer (lazy import) ─────────────────────────────────────────


def _open_client(httpx_mod: Any, *, user_agent: str) -> Any:
    # Round-3 audit fix: follow_redirects=False so we manually walk Location
    # headers and re-run _is_safe_url on each hop (otherwise a public URL
    # 302→ private IP bypasses the SSRF guard entirely).
    return httpx_mod.Client(
        headers={"User-Agent": user_agent},
        timeout=10.0,
        follow_redirects=False,
    )


# SSRF denylist (R-1.8.0-013 deep-audit fix). Blocks fetches against
# private/loopback/link-local/cloud-metadata IPs to prevent the research
# tool from being used as an internal-network probe via crafted search
# results. List sources: RFC1918 / RFC6890 / cloud metadata IPs.
_SSRF_DENY_HOSTS = frozenset({
    "localhost", "ip6-localhost", "ip6-loopback",
    # Cloud instance metadata endpoints (AWS / GCP / Azure / Alibaba / Oracle):
    "169.254.169.254", "metadata.google.internal", "metadata.goog",
    "metadata.azure.com", "100.100.100.200",
})


def _default_dns_resolver(host: str) -> list[Any]:
    """Default DNS resolver — calls socket.getaddrinfo on the real system.

    Tests monkey-patch the module-level `_dns_resolver` reference (see below)
    to inject synthetic hostname → IP mappings without going to real DNS.
    Round-5 audit fix replaces the previous PYTEST_CURRENT_TEST env-var
    escape hatch (which a user could set in their shell to disable SSRF
    DNS check entirely).
    """
    import socket
    return socket.getaddrinfo(host, None)


# Module-level resolver reference. Production: bound to _default_dns_resolver
# which calls socket.getaddrinfo. Tests rebind this to a fake resolver that
# returns synthetic IP records, e.g.:
#     monkeypatch.setattr(tools.research, "_dns_resolver",
#                         lambda h: [(2, 1, 6, "", ("203.0.113.42", 0))])
_dns_resolver = _default_dns_resolver


def _ip_is_dangerous(ip_str: str) -> bool:
    """True if the literal IP string is private / loopback / link-local / etc."""
    import ipaddress
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _is_private_ip(host: str) -> bool:
    """Return True if host (literal IP or hostname) resolves to a dangerous IP.

    Round-3 audit fix: previously only checked literal IPs. Now also performs
    DNS resolution for hostnames so `internal.corp.example` pointing at
    10.0.0.1 is blocked. DNS lookups can fail (NXDOMAIN, timeout); on failure
    we conservatively block (fail-closed — better to skip a potentially-safe
    URL than fetch a potentially-internal one).

    Covers IPv4 RFC1918, IPv4 loopback (127/8), IPv4 link-local (169.254/16),
    IPv4 cloud metadata, IPv6 ::1 / fc00::/7 / fe80::/10. Hostnames in the
    explicit deny set are checked literally (case-insensitive).
    """
    import socket
    h = host.lower().strip("[]")

    # 1. Explicit hostname denylist (cloud metadata + literal localhost).
    if h in _SSRF_DENY_HOSTS:
        return True

    # 2. Direct IP literal.
    if _ip_is_dangerous(h):
        return True

    # 3. DNS resolution (only if not already a literal IP).
    try:
        import ipaddress
        ipaddress.ip_address(h)
        # If we got here, h IS a literal IP that passed the dangerous check.
        return False
    except ValueError:
        pass  # Hostname — proceed to DNS lookup.

    # Round-5 audit fix: replaced PYTEST_CURRENT_TEST escape hatch
    # (user-settable in shell) with dependency-injected resolver. Tests
    # monkey-patch `tools.research._dns_resolver` at module level to bypass
    # real DNS for synthetic hostnames; production code has NO env-var
    # read path that could disable the check.
    try:
        infos = _dns_resolver(h)
    except (socket.gaierror, socket.herror, OSError):
        # DNS failure — fail-CLOSED. Surface to operator so they know.
        print(
            f"[research] SSRF guard: DNS lookup failed for {h}; treating as unsafe",
            file=sys.stderr,
        )
        return True

    for info in infos:
        # info = (family, type, proto, canonname, sockaddr); sockaddr[0] is IP
        sockaddr = info[4]
        # sockaddr[0] is `str | int` per typeshed (port for AF_UNIX); narrow
        # to str for AF_INET / AF_INET6 cases that produce IP literals.
        ip_str = str(sockaddr[0]) if sockaddr else ""
        if ip_str and _ip_is_dangerous(ip_str):
            print(
                f"[research] SSRF guard: {h} resolves to dangerous IP {ip_str}",
                file=sys.stderr,
            )
            return True

    return False


def _is_safe_url(url: str) -> tuple[bool, str]:
    """Return (ok, reason_if_blocked) for SSRF safety check.

    Allows only http(s) schemes and rejects hosts on the SSRF denylist
    (literal IPs, hostname denylist, AND DNS-resolved IPs).
    """
    try:
        parsed = urlparse(url)
    except (ValueError, TypeError):
        return False, "url-parse-error"
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"unsupported-scheme:{parsed.scheme}"
    if not parsed.hostname:
        return False, "missing-hostname"
    if _is_private_ip(parsed.hostname):
        return False, f"ssrf-denied:{parsed.hostname}"
    return True, ""


# Maximum response body size before truncation (R-1.8.0-013 deep-audit fix).
# Default 5 MB per page is enough for any reasonable text/HTML page; binary
# blobs and unbounded streams get truncated with a warning rather than
# blowing up memory or filling the inbox.
_MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB


_MAX_REDIRECTS = 5


def _fetch_text(
    client: Any,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    max_bytes: int = _MAX_RESPONSE_BYTES,
) -> str | None:
    """Return body text for a URL, or None on any error.

    Round-3 audit fix:
    - Performs SSRF safety check on EVERY URL in the redirect chain (not
      just the original) — public URL 302→ private IP no longer bypasses.
    - Streams response body via httpx ``stream`` API with byte counter,
      stopping at ``max_bytes`` so a malicious 100GB stream cannot OOM.
      Previously ``resp.text`` loaded everything before truncation.

    The httpx client is configured with ``follow_redirects=False`` so we
    walk redirects manually here; max ``_MAX_REDIRECTS`` hops.
    """
    current = url
    for hop in range(_MAX_REDIRECTS + 1):
        safe, reason = _is_safe_url(current)
        if not safe:
            print(
                f"[research] SSRF guard blocked {current} "
                f"(hop {hop} from {url}, reason={reason})",
                file=sys.stderr,
            )
            return None

        # Stream the response — never let httpx buffer the full body.
        try:
            req_headers = headers if headers else None
            with client.stream("GET", current, headers=req_headers) as resp:
                # 3xx redirect: extract Location, re-check, hop again.
                status = getattr(resp, "status_code", 0)
                if 300 <= status < 400:
                    location = resp.headers.get("location") if hasattr(resp, "headers") else None
                    if not location:
                        return None
                    # Resolve relative redirects against current URL
                    from urllib.parse import urljoin
                    current = urljoin(current, location)
                    continue
                # Non-redirect: check status, then stream body bounded by max_bytes.
                try:
                    resp.raise_for_status()
                except Exception:  # noqa: BLE001
                    return None

                buf = bytearray()
                truncated = False
                # iter_bytes is the httpx streaming API.
                for chunk in resp.iter_bytes():
                    if len(buf) + len(chunk) > max_bytes:
                        # Take only enough to reach max_bytes, then stop.
                        take = max_bytes - len(buf)
                        if take > 0:
                            buf.extend(chunk[:take])
                        truncated = True
                        break
                    buf.extend(chunk)
                if truncated:
                    print(
                        f"[research] response truncated at {max_bytes} bytes "
                        f"during streaming from {current}",
                        file=sys.stderr,
                    )
                # Decode with replacement; trim partial trailing UTF-8 sequence.
                text = bytes(buf).decode("utf-8", errors="ignore")
                return text
        except AttributeError:
            # client.stream() not available (mock client in tests). Fall
            # back to the non-streaming path with post-load truncation —
            # this is fine because mocks return small synthetic bodies.
            try:
                resp = (
                    client.get(current, headers=req_headers)
                    if req_headers
                    else client.get(current)
                )
                resp.raise_for_status()
                text = getattr(resp, "text", "")
                if not isinstance(text, str):
                    return None
                encoded = text.encode("utf-8", errors="replace")
                if len(encoded) > max_bytes:
                    return encoded[:max_bytes].decode("utf-8", errors="ignore")
                return text
            except Exception:  # noqa: BLE001
                return None
        except Exception:  # noqa: BLE001
            return None

    print(
        f"[research] redirect chain exceeded {_MAX_REDIRECTS} hops from {url}",
        file=sys.stderr,
    )
    return None


# ─── HTML link extraction ───────────────────────────────────────────────────


def _extract_outbound_urls(html: str, base_host: str | None = None) -> list[str]:
    """Extract absolute http(s) links from a page body."""
    return [_unescape(u) for u in _GENERIC_LINK_RE.findall(html)]


def _unescape(url: str) -> str:
    """Decode ``&amp;`` + drop DuckDuckGo redirect wrappers."""
    decoded = url.replace("&amp;", "&")
    # Handle DDG redirect links of the form //duckduckgo.com/l/?uddg=...&...
    if decoded.startswith("//duckduckgo.com/l/"):
        pieces = urlparse("https:" + decoded)
        params = parse_qs(pieces.query)
        if "uddg" in params and params["uddg"]:
            return unquote(params["uddg"][0])
    return decoded


# ─── Main driver ────────────────────────────────────────────────────────────


def run_research(
    *,
    query: str,
    depth: int,
    max_pages: int,
    root: Path,
    backend: str = _DEFAULT_BACKEND,
) -> ResearchResult:
    """Execute a research run and write the inbox note.

    Returns a ``ResearchResult`` describing what was fetched, what failed,
    and where the output landed. Always writes an output file; callers
    decide whether to exit 0 or 1 based on ``ResearchResult.incomplete``.

    ``backend`` selects a search engine from ``_BACKENDS`` (default
    ``searxng``). Unknown backend keys silently fall back to the default.
    """
    import httpx
    import markdownify

    spec = _BACKENDS.get(backend, _BACKENDS[_DEFAULT_BACKEND])
    search_url = spec.build_url(query)
    user_agent = _user_agent(spec.name)
    slug = _make_slug(query)
    today = datetime.now().date()
    output_path = root / "inbox" / f"research-{today.isoformat()}-{slug}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = ResearchResult(
        query=query,
        depth=depth,
        output_path=output_path,
        search_url=search_url,
    )

    fetched_bodies: dict[str, str] = {}
    remaining = max(0, max_pages)

    # Backend-level precheck — lets us fail loudly on missing creds
    # BEFORE opening an httpx client.
    precheck_error = spec.precheck()
    if precheck_error is not None:
        result.errors.append(precheck_error)
        result.incomplete = True
        _write_output(
            output_path, fetched_bodies, markdownify, query, depth, result, slug
        )
        return result

    with _open_client(httpx, user_agent=user_agent) as client:
        robots = _RobotsCache(
            lambda url: _fetch_text(client, url),
            user_agent=user_agent,
        )

        # `--max-pages 0` is a valid no-op per the tool contract.
        if remaining > 0:
            # Layer 0: search page
            if not robots.allowed(search_url):
                result.errors.append(
                    f"robots.txt blocks {search_url}; "
                    "this backend is disallowed — try another "
                    "`--backend` (searxng / brave). DDG endpoints are "
                    "known-blocked as of 2026-04-21."
                )
                result.incomplete = True
            else:
                body = _fetch_text(
                    client, search_url, headers=spec.request_headers()
                )
                if body is None:
                    result.errors.append(f"fetch failed: {search_url}")
                    result.incomplete = True
                else:
                    fetched_bodies[search_url] = body
                    result.fetched_urls.append(search_url)
                    remaining -= 1

        if depth >= 1 and remaining > 0 and search_url in fetched_bodies:
            layer1_urls = spec.parse_result_urls(fetched_bodies[search_url])
            layer1_bodies = _fetch_layer(
                client,
                robots,
                layer1_urls,
                remaining,
                result,
            )
            fetched_bodies.update(layer1_bodies)
            remaining -= len(layer1_bodies)

            if depth >= 2 and remaining > 0:
                layer2_candidates: list[str] = []
                for body in layer1_bodies.values():
                    layer2_candidates.extend(_extract_outbound_urls(body))
                layer2_bodies = _fetch_layer(
                    client,
                    robots,
                    layer2_candidates,
                    remaining,
                    result,
                    skip=set(fetched_bodies.keys()),
                )
                fetched_bodies.update(layer2_bodies)

    _write_output(
        output_path, fetched_bodies, markdownify, query, depth, result, slug
    )
    return result


def _write_output(
    output_path: Path,
    fetched_bodies: dict[str, str],
    markdownify_mod: Any,
    query: str,
    depth: int,
    result: ResearchResult,
    slug: str,
) -> None:
    """Write the research markdown file (frontmatter + body)."""
    md_body = _render_body(fetched_bodies, markdownify_mod, query)
    frontmatter = _render_frontmatter(
        query=query,
        depth=depth,
        sources=result.fetched_urls,
        incomplete=result.incomplete,
        slug=slug,
    )
    output_path.write_text(frontmatter + md_body, encoding="utf-8")


def _fetch_layer(
    client: Any,
    robots: _RobotsCache,
    urls: list[str],
    budget: int,
    result: ResearchResult,
    *,
    skip: set[str] | None = None,
) -> dict[str, str]:
    """Fetch up to ``budget`` URLs from ``urls``, honouring robots."""
    skip = skip or set()
    out: dict[str, str] = {}
    for url in urls:
        if budget <= 0:
            break
        if url in skip or url in out:
            continue
        if not robots.allowed(url):
            # Silent skip — robots denial is expected, not an error.
            continue
        body = _fetch_text(client, url)
        if body is None:
            result.errors.append(f"fetch failed: {url}")
            result.incomplete = True
            continue
        out[url] = body
        result.fetched_urls.append(url)
        budget -= 1
    return out


def _encode_query(query: str) -> str:
    return quote_plus(query)


def _render_frontmatter(
    *,
    query: str,
    depth: int,
    sources: list[str],
    incomplete: bool,
    slug: str,
) -> str:
    now = datetime.now()
    today = now.date().isoformat()
    iso = now.isoformat(timespec="seconds")
    escaped_query = query.replace('"', '\\"')
    lines = [
        "---",
        f"id: research-{today}-{slug}",
        f"created: {iso}",
        f'query: "{escaped_query}"',
        f"depth: {depth}",
        "sources:",
    ]
    if sources:
        for src in sources:
            lines.append(f"  - {src}")
    else:
        lines.append("  []")
    lines.append(f"incomplete: {str(incomplete).lower()}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def _render_body(
    bodies: dict[str, str],
    markdownify_mod: Any,
    query: str,
) -> str:
    if not bodies:
        return f"# Research · {query}\n\n_(no content fetched)_\n"

    chunks: list[str] = [f"# Research · {query}", ""]
    for url, html in bodies.items():
        chunks.append(f"## {url}")
        chunks.append("")
        md = markdownify_mod.markdownify(html, heading_style="ATX")
        chunks.append(md.strip())
        chunks.append("")
    return "\n".join(chunks) + "\n"


# ─── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research",
        description=(
            "Background web fetch into inbox/ "
            "(references/tools-spec.md section 6.4). "
            "Respects robots.txt. No LLM summarization."
        ),
    )
    parser.add_argument("query", help="Research topic / query")
    parser.add_argument(
        "--depth",
        type=int,
        default=_DEFAULT_DEPTH,
        help="Link-following depth from the search page (default: 1)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=_DEFAULT_MAX_PAGES,
        help="Hard cap on total fetches (default: 10)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Second-brain root (default: CWD)",
    )
    parser.add_argument(
        "--backend",
        choices=sorted(_BACKENDS.keys()),
        default=_DEFAULT_BACKEND,
        help=(
            "Search backend. Defaults to 'searxng' (JSON; instance "
            "controlled by SEARXNG_URL env, else https://searx.be). "
            "'brave' uses api.search.brave.com and requires "
            "BRAVE_API_KEY env (free tier: 2000 queries/month). "
            "DDG variants (ddg / ddg-html / ddg-lite): not recommended -- "
            "DuckDuckGo's robots.txt blocks all endpoints as of "
            "2026-04-21; kept only as a manual fallback."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = args.root if args.root is not None else Path.cwd()

    try:
        result = run_research(
            query=args.query,
            depth=max(0, args.depth),
            max_pages=max(0, args.max_pages),
            root=root,
            backend=args.backend,
        )
    except ImportError as exc:
        print(
            f"error: missing optional dependency: {exc}. "
            "Install with `uv sync --extra research`.",
            file=sys.stderr,
        )
        return 1

    print(str(result.output_path))
    if result.incomplete:
        for err in result.errors:
            print(f"warning: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
