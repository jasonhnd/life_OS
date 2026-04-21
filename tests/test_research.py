"""Tests for tools.research — v1.7 Sprint 4.

Contract: references/tools-spec.md §6.4.

Scope:
  - ``httpx.get`` + ``markdownify`` conversion
  - ``urllib.robotparser`` robots.txt compliance
  - user-agent ``LifeOS-research/1.7 (+local-tool)``
  - --depth 0/1/2 + --max-pages cap
  - slug: ASCII transliterate -> SHA-1 fallback
  - Failure: partial file + ``incomplete: true`` + exit 1
  - NO LLM summarization (user decision #16)

All tests mock httpx + urllib.robotparser — no real network.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest

# ─── Fake httpx injection ────────────────────────────────────────────────────


def _install_fake_httpx(
    monkeypatch: pytest.MonkeyPatch,
    url_map: dict[str, tuple[int, str]],
) -> MagicMock:
    """Install a fake httpx module. ``url_map``: {url: (status, text)}.

    Missing URLs raise a fake RequestError. Returns the Client mock for
    assertion purposes.
    """
    fake = ModuleType("httpx")

    class FakeResponse:
        def __init__(self, status_code: int, text: str) -> None:
            self.status_code = status_code
            self.text = text

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise fake.HTTPStatusError(  # type: ignore[attr-defined]
                    f"{self.status_code}", request=None, response=self
                )

    class FakeRequestError(Exception):
        pass

    class FakeHTTPStatusError(Exception):
        def __init__(self, *args, request=None, response=None):
            super().__init__(*args)
            self.request = request
            self.response = response

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            self.headers = kwargs.get("headers", {})
            FakeClient.last_headers = self.headers

        def __enter__(self):
            return self

        def __exit__(self, *a, **kw):
            return False

        def get(self, url: str, **kwargs) -> FakeResponse:
            if url in url_map:
                status, text = url_map[url]
                return FakeResponse(status, text)
            raise fake.RequestError(f"no mock for {url}")  # type: ignore[attr-defined]

    FakeClient.last_headers = {}

    fake.Client = FakeClient  # type: ignore[attr-defined]
    fake.RequestError = FakeRequestError  # type: ignore[attr-defined]
    fake.HTTPStatusError = FakeHTTPStatusError  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "httpx", fake)
    # Force reload so tools.research's lazy import picks up fake.
    sys.modules.pop("tools.research", None)
    return FakeClient  # type: ignore[return-value]


def _install_fake_markdownify(
    monkeypatch: pytest.MonkeyPatch, *, prefix: str = "MD:"
) -> None:
    """Install a fake markdownify module that just wraps input."""
    fake = ModuleType("markdownify")

    def markdownify(html: str, **kwargs) -> str:
        return f"{prefix}{html}"

    fake.markdownify = markdownify  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "markdownify", fake)
    sys.modules.pop("tools.research", None)


@pytest.fixture
def brain_root(tmp_path: Path) -> Path:
    """Second-brain root with inbox ready."""
    root = tmp_path / "brain"
    (root / "inbox").mkdir(parents=True)
    return root


# ─── Slug generation ─────────────────────────────────────────────────────────


class TestSlug:
    def test_ascii_query_lowercased_hyphenated(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        _install_fake_markdownify(monkeypatch)
        from tools.research import _make_slug

        assert _make_slug("Hello World Topic") == "hello-world-topic"

    def test_punctuation_stripped(self, monkeypatch: pytest.MonkeyPatch):
        _install_fake_markdownify(monkeypatch)
        from tools.research import _make_slug

        assert _make_slug("hello, world!") == "hello-world"

    def test_unicode_cjk_fallback_to_sha1(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        _install_fake_markdownify(monkeypatch)
        from tools.research import _make_slug

        slug = _make_slug("日本永驻新政策")
        # SHA-1 prefix: lowercase hex, exactly 8 chars
        assert len(slug) == 8
        assert all(c in "0123456789abcdef" for c in slug)

    def test_deterministic_sha1(self, monkeypatch: pytest.MonkeyPatch):
        _install_fake_markdownify(monkeypatch)
        from tools.research import _make_slug

        s1 = _make_slug("日本永驻新政策")
        s2 = _make_slug("日本永驻新政策")
        assert s1 == s2


# ─── User-agent ──────────────────────────────────────────────────────────────


class TestUserAgent:
    def test_user_agent_set(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Default backend is ddg JSON (verified by TestBackends below).
        search_url = (
            "https://duckduckgo.com/?q=foo&format=json&no_html=1"
        )
        fake_client = _install_fake_httpx(
            monkeypatch,
            {
                search_url: (200, '{"RelatedTopics": []}'),
                "https://example.com/robots.txt": (404, ""),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        run_research(
            query="foo",
            depth=0,
            max_pages=5,
            root=brain_root,
        )
        ua = fake_client.last_headers.get("User-Agent", "")
        assert ua.startswith("LifeOS-research/1.7")


# ─── robots.txt enforcement ─────────────────────────────────────────────────


class TestRobots:
    def test_disallowed_page_skipped(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """A page blocked by robots.txt must not be fetched."""
        search_url = "https://html.duckduckgo.com/html/?q=foo"
        # Search returns a page linking example.com/blocked
        search_html = (
            '<html><body><a class="result__a" href="https://example.com/blocked">'
            "r</a></body></html>"
        )
        _install_fake_httpx(
            monkeypatch,
            {
                search_url: (200, search_html),
                # robots.txt disallows everything
                "https://example.com/robots.txt": (
                    200,
                    "User-agent: *\nDisallow: /\n",
                ),
                # even if fetched, would return 200 — but expected to be skipped
                "https://example.com/blocked": (200, "<html>body</html>"),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="foo",
            depth=1,
            max_pages=5,
            root=brain_root,
            backend="ddg-html",
        )
        # The fetched_urls list should not contain the blocked URL
        assert "https://example.com/blocked" not in result.fetched_urls
        # But search page itself was fetched (duckduckgo robots allowed)
        assert result.search_url in result.fetched_urls


# ─── Depth + max-pages ──────────────────────────────────────────────────────


class TestDepth:
    def test_depth_zero_fetches_search_only(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        search_url = "https://html.duckduckgo.com/html/?q=foo"
        _install_fake_httpx(
            monkeypatch,
            {
                search_url: (
                    200,
                    '<html><body><a class="result__a" href="https://ex.com/a">a</a></body></html>',
                ),
                "https://ex.com/robots.txt": (404, ""),
                "https://ex.com/a": (200, "<html>body</html>"),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="foo",
            depth=0,
            max_pages=5,
            root=brain_root,
            backend="ddg-html",
        )
        # Only the search URL should be fetched.
        assert result.fetched_urls == [search_url]
        assert result.incomplete is False

    def test_depth_one_fetches_each_top_result(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        search_url = "https://html.duckduckgo.com/html/?q=foo"
        search_html = (
            '<html><body>'
            '<a class="result__a" href="https://ex.com/a">a</a>'
            '<a class="result__a" href="https://ex.com/b">b</a>'
            "</body></html>"
        )
        _install_fake_httpx(
            monkeypatch,
            {
                search_url: (200, search_html),
                "https://ex.com/robots.txt": (404, ""),
                "https://ex.com/a": (200, "<html>body A</html>"),
                "https://ex.com/b": (200, "<html>body B</html>"),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="foo",
            depth=1,
            max_pages=5,
            root=brain_root,
            backend="ddg-html",
        )
        assert "https://ex.com/a" in result.fetched_urls
        assert "https://ex.com/b" in result.fetched_urls
        assert result.incomplete is False

    def test_depth_two_follows_outbound_link(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        search_url = "https://html.duckduckgo.com/html/?q=foo"
        search_html = (
            '<html><body><a class="result__a" href="https://ex.com/a">a</a></body></html>'
        )
        page_a_html = '<html><body><a href="https://ex.com/b">next</a></body></html>'
        _install_fake_httpx(
            monkeypatch,
            {
                search_url: (200, search_html),
                "https://ex.com/robots.txt": (404, ""),
                "https://ex.com/a": (200, page_a_html),
                "https://ex.com/b": (200, "<html>body B</html>"),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="foo",
            depth=2,
            max_pages=5,
            root=brain_root,
            backend="ddg-html",
        )
        assert "https://ex.com/b" in result.fetched_urls

    def test_max_pages_hard_cap(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        search_url = "https://html.duckduckgo.com/html/?q=foo"
        links = "".join(
            f'<a class="result__a" href="https://ex.com/p{i}">p{i}</a>'
            for i in range(10)
        )
        urls = {
            search_url: (200, f"<html><body>{links}</body></html>"),
            "https://ex.com/robots.txt": (404, ""),
        }
        for i in range(10):
            urls[f"https://ex.com/p{i}"] = (200, "<html>body</html>")
        _install_fake_httpx(monkeypatch, urls)
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="foo",
            depth=1,
            max_pages=3,
            root=brain_root,
            backend="ddg-html",
        )
        # max-pages caps total fetches (search + pages <= max_pages)
        assert len(result.fetched_urls) <= 3


# ─── Output file + frontmatter ──────────────────────────────────────────────


class TestOutput:
    def test_output_path_in_inbox(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Use default ddg (JSON API) backend.
        search_url = (
            "https://duckduckgo.com/?q=foo+bar&format=json&no_html=1"
        )
        _install_fake_httpx(
            monkeypatch,
            {
                search_url: (200, '{"RelatedTopics": []}'),
                "https://ex.com/robots.txt": (404, ""),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="foo bar",
            depth=0,
            max_pages=5,
            root=brain_root,
        )
        assert result.output_path.parent == brain_root / "inbox"
        assert result.output_path.name.startswith("research-")
        assert result.output_path.name.endswith(".md")
        assert "foo-bar" in result.output_path.name

    def test_output_contains_yaml_frontmatter(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        search_url = (
            "https://duckduckgo.com/?q=hello&format=json&no_html=1"
        )
        _install_fake_httpx(
            monkeypatch,
            {search_url: (200, '{"RelatedTopics": []}'),
             "https://ex.com/robots.txt": (404, "")},
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="hello",
            depth=0,
            max_pages=5,
            root=brain_root,
        )
        content = result.output_path.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "query:" in content
        assert "depth:" in content
        assert "sources:" in content
        assert "incomplete: false" in content


# ─── Failure path ───────────────────────────────────────────────────────────


class TestFailure:
    def test_network_failure_sets_incomplete_and_exit_one(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        search_url = "https://html.duckduckgo.com/html/?q=foo"
        search_html = (
            '<html><body><a class="result__a" href="https://ex.com/a">a</a></body></html>'
        )
        _install_fake_httpx(
            monkeypatch,
            {
                search_url: (200, search_html),
                "https://ex.com/robots.txt": (404, ""),
                # ex.com/a missing from map -> fake raises RequestError
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import main

        rc = main(
            [
                "foo",
                "--depth",
                "1",
                "--max-pages",
                "5",
                "--root",
                str(brain_root),
                "--backend",
                "ddg-html",
            ]
        )
        assert rc == 1
        # Output file was still written
        produced = list((brain_root / "inbox").glob("research-*.md"))
        assert produced, "partial file must still be written on failure"
        content = produced[0].read_text(encoding="utf-8")
        assert "incomplete: true" in content

    def test_total_search_failure_exits_one_with_incomplete(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        search_url = (
            "https://duckduckgo.com/?q=foo&format=json&no_html=1"
        )
        _install_fake_httpx(
            monkeypatch,
            {
                # search itself returns 500
                search_url: (500, ""),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import main

        rc = main(
            [
                "foo",
                "--depth",
                "0",
                "--root",
                str(brain_root),
            ]
        )
        assert rc == 1
        produced = list((brain_root / "inbox").glob("research-*.md"))
        assert produced
        assert "incomplete: true" in produced[0].read_text(encoding="utf-8")


# ─── CLI smoke ──────────────────────────────────────────────────────────────


class TestCLI:
    def test_main_success_exit_zero(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Default backend = ddg JSON API.
        search_url = (
            "https://duckduckgo.com/?q=foo&format=json&no_html=1"
        )
        _install_fake_httpx(
            monkeypatch,
            {
                search_url: (200, '{"RelatedTopics": []}'),
                "https://ex.com/robots.txt": (404, ""),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import main

        rc = main(
            ["foo", "--depth", "0", "--root", str(brain_root)]
        )
        assert rc == 0

    def test_default_depth_and_max_pages(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Defaults: depth=1, max-pages=10 (per spec §6.4)."""
        from tools import research

        parser = research._build_parser()
        args = parser.parse_args(["foo"])
        assert args.depth == 1
        assert args.max_pages == 10


# ─── Backend selection ──────────────────────────────────────────────────────


class TestBackends:
    def test_default_backend_is_ddg_json(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """Default backend is the DDG JSON Instant Answer endpoint."""
        from tools import research

        parser = research._build_parser()
        args = parser.parse_args(["foo"])
        assert args.backend == "ddg"
        template = research._BACKENDS[args.backend]
        assert template.startswith("https://duckduckgo.com/?q=")
        assert "format=json" in template

    def test_backend_choices_include_fallbacks(self):
        """Registry exposes html + lite fallbacks for when ddg JSON fails."""
        from tools.research import _BACKENDS

        assert "ddg" in _BACKENDS
        assert "ddg-html" in _BACKENDS
        assert "ddg-lite" in _BACKENDS

    def test_unknown_backend_falls_back_to_default(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Unknown backend key silently falls back to the default URL."""
        search_url = (
            "https://duckduckgo.com/?q=foo&format=json&no_html=1"
        )
        _install_fake_httpx(
            monkeypatch,
            {
                search_url: (200, '{"RelatedTopics": []}'),
                "https://ex.com/robots.txt": (404, ""),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="foo",
            depth=0,
            max_pages=5,
            root=brain_root,
            backend="does-not-exist",
        )
        # Falls back to default, so search_url should be the JSON endpoint
        assert result.search_url == search_url

    def test_robots_block_emits_backend_hint(
        self, brain_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When robots.txt blocks the search URL, the error message
        should guide users to try another `--backend`."""
        search_url = (
            "https://duckduckgo.com/?q=foo&format=json&no_html=1"
        )
        _install_fake_httpx(
            monkeypatch,
            {
                # robots.txt disallows everything on duckduckgo.com
                "https://duckduckgo.com/robots.txt": (
                    200,
                    "User-agent: *\nDisallow: /\n",
                ),
                # search itself would return 200 but must be skipped
                search_url: (200, '{"RelatedTopics": []}'),
            },
        )
        _install_fake_markdownify(monkeypatch)
        from tools.research import run_research

        result = run_research(
            query="foo",
            depth=0,
            max_pages=5,
            root=brain_root,
        )
        assert result.incomplete is True
        assert any("--backend" in err for err in result.errors)


# ─── Integration smoke (opt-in, real network) ───────────────────────────────


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("LIFEOS_INTEGRATION") != "1",
    reason=(
        "Online smoke test — hits real network. "
        "Enable with LIFEOS_INTEGRATION=1 (or `pytest -m integration`)."
    ),
)
def test_real_ddg_fetch_smoke(tmp_path: Path) -> None:
    """Online smoke test: actually hit DuckDuckGo.

    Skipped by default. Enable with:
        LIFEOS_INTEGRATION=1 pytest tests/test_research.py -v

    Exercises the full run_research stack (robots.txt fetch + search).
    Robots may block; the test only asserts we write an output file
    and exit cleanly without raising — not that content was fetched.
    """
    pytest.importorskip("httpx")
    pytest.importorskip("markdownify")
    brain_root = tmp_path / "brain"
    (brain_root / "inbox").mkdir(parents=True)
    from tools.research import run_research

    result = run_research(
        query="python",
        depth=0,
        max_pages=1,
        root=brain_root,
    )
    assert result.output_path.exists()
