#!/usr/bin/env python3
"""Background web fetch into inbox — v1.7 Sprint 4.

Contract: references/tools-spec.md §6.4.

  - ``httpx.get`` + ``markdownify`` conversion
  - ``urllib.robotparser`` enforces robots.txt
  - user-agent ``LifeOS-research/1.7 (+local-tool)``
  - ``--depth`` N controls link-following (0=search page only,
    1=each top result, 2=one more layer of outbound links)
  - ``--max-pages`` hard cap on total fetches (default 10)
  - Slug: ASCII transliterate → lowercase → hyphenate; non-ASCII falls
    back to SHA-1 first 8 chars
  - On failure: writes a partial file with ``incomplete: true`` and
    exits 1. Empty/search-only runs exit 0.
  - NO LLM summarization (user decision #16).

Dependencies (optional-dep group ``research``): ``httpx``, ``markdownify``.
Imports are lazy so tests can inject mock modules via ``sys.modules``.
"""

from __future__ import annotations

import argparse
import hashlib
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

_USER_AGENT = "LifeOS-research/1.7 (+local-tool)"
_DEFAULT_DEPTH = 1
_DEFAULT_MAX_PAGES = 10
_SLUG_HASH_LEN = 8

# Search-backend registry. Each entry maps a backend key to a URL template
# whose single ``{query}`` placeholder receives the url-encoded query.
#
# Note on robots.txt (verified 2026-04-21): DuckDuckGo's public robots.txt
# disallows ``/html``, ``/lite``, and ``/*?`` (search URLs) on both
# ``duckduckgo.com`` and its API subdomains. The DDG JSON API at
# ``https://duckduckgo.com/?q=...&format=json`` is less aggressively
# blocked in practice but still listed. Since we respect robots.txt, DDG
# runs may legitimately fail — when that happens we emit a helpful
# ``--backend`` hint rather than a silent skip.
_BACKENDS: dict[str, str] = {
    "ddg": "https://duckduckgo.com/?q={query}&format=json&no_html=1",
    "ddg-html": "https://html.duckduckgo.com/html/?q={query}",
    "ddg-lite": "https://lite.duckduckgo.com/lite/?q={query}",
}
_DEFAULT_BACKEND = "ddg"
_SEARCH_URL_TEMPLATE = _BACKENDS[_DEFAULT_BACKEND]

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


# ─── robots.txt ─────────────────────────────────────────────────────────────


class _RobotsCache:
    """Per-run cache of parsed robots.txt rules keyed by (scheme, netloc)."""

    def __init__(self, fetch_text: Callable[[str], str | None]) -> None:
        self._fetch_text = fetch_text
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
        return parser.can_fetch(_USER_AGENT, url)

    def _load(self, host_key: str) -> RobotFileParser | None:
        robots_url = f"{host_key}/robots.txt"
        text = self._fetch_text(robots_url)
        if text is None:
            return None
        rp = RobotFileParser()
        rp.parse(text.splitlines())
        return rp


# ─── HTTP fetch layer (lazy import) ─────────────────────────────────────────


def _open_client(httpx_mod: Any) -> Any:
    return httpx_mod.Client(
        headers={"User-Agent": _USER_AGENT},
        timeout=10.0,
        follow_redirects=True,
    )


def _fetch_text(client: Any, url: str) -> str | None:
    """Return body text for a URL, or None on any error."""
    try:
        resp = client.get(url)
    except Exception:  # noqa: BLE001
        return None
    try:
        resp.raise_for_status()
    except Exception:  # noqa: BLE001
        return None
    text = getattr(resp, "text", "")
    return text if isinstance(text, str) else None


# ─── HTML link extraction ───────────────────────────────────────────────────


def _extract_result_urls(html: str) -> list[str]:
    """Extract primary result URLs from a DuckDuckGo HTML page."""
    urls = [_unescape(u) for u in _RESULT_LINK_RE.findall(html)]
    if urls:
        return urls
    # Fallback: any absolute <a href>
    return [_unescape(u) for u in _GENERIC_LINK_RE.findall(html)]


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

    ``backend`` selects a search endpoint from ``_BACKENDS`` (default
    ``ddg``). Unknown backends fall back to the default with a warning.
    """
    import httpx  # type: ignore[import-not-found]
    import markdownify  # type: ignore[import-not-found]

    template = _BACKENDS.get(backend, _SEARCH_URL_TEMPLATE)
    search_url = template.format(query=_encode_query(query))
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
    remaining = max(1, max_pages)

    with _open_client(httpx) as client:
        robots = _RobotsCache(lambda url: _fetch_text(client, url))

        # Layer 0: search page
        if not robots.allowed(search_url):
            result.errors.append(
                f"robots.txt blocks {search_url}; "
                "this backend is disallowed — try another "
                "`--backend` (e.g. ddg-lite, ddg-html) or point "
                "at a self-hosted SearXNG instance."
            )
            result.incomplete = True
        else:
            body = _fetch_text(client, search_url)
            if body is None:
                result.errors.append(f"fetch failed: {search_url}")
                result.incomplete = True
            else:
                fetched_bodies[search_url] = body
                result.fetched_urls.append(search_url)
                remaining -= 1

        if depth >= 1 and remaining > 0 and search_url in fetched_bodies:
            layer1_urls = _extract_result_urls(fetched_bodies[search_url])
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

    # Compose output
    md_body = _render_body(fetched_bodies, markdownify, query)
    frontmatter = _render_frontmatter(
        query=query,
        depth=depth,
        sources=result.fetched_urls,
        incomplete=result.incomplete,
        slug=slug,
    )
    output_path.write_text(frontmatter + md_body, encoding="utf-8")
    return result


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
            "(references/tools-spec.md §6.4). "
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
            "Search backend. Defaults to 'ddg' (JSON Instant Answer "
            "endpoint). Fallbacks: ddg-html, ddg-lite. Note: all DDG "
            "endpoints are robots.txt-restricted — runs that exit 1 with "
            "a 'blocked by robots' warning are expected, not bugs."
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
            max_pages=max(1, args.max_pages),
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
