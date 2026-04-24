#!/usr/bin/env python3
"""Translate root English docs into zh/ja i18n copies via Anthropic Claude."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_PATH = REPO_ROOT / "scripts" / "i18n-glossary.yaml"
SUPPORTED_SOURCES = ("README.md", "CHANGELOG.md")
LANGUAGES = {
    "zh": "Simplified Chinese",
    "ja": "Japanese",
}
DEFAULT_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_TIMEOUT_SECONDS = 120.0
DEFAULT_MAX_TOKENS = 8192
CHUNK_MAX_CHARS = 12_000

Glossary = dict[str, dict[str, str]]


class TranslationError(RuntimeError):
    """Raised when a translation request cannot produce usable Markdown."""


class TranslationClient(Protocol):
    def translate_chunk(
        self,
        *,
        source_name: str,
        chunk: str,
        target_language: str,
        glossary: Glossary,
        chunk_number: int,
        chunk_count: int,
    ) -> str:
        """Translate one Markdown chunk."""


class ClientFactory(Protocol):
    def __call__(self, env: Mapping[str, str]) -> TranslationClient:
        """Build a translation client from environment settings."""


@dataclass(frozen=True)
class AnthropicClient:
    api_key: str
    model: str
    timeout_seconds: float
    max_tokens: int
    api_url: str = DEFAULT_API_URL

    def translate_chunk(
        self,
        *,
        source_name: str,
        chunk: str,
        target_language: str,
        glossary: Glossary,
        chunk_number: int,
        chunk_count: int,
    ) -> str:
        prompt = build_user_prompt(
            source_name=source_name,
            chunk=chunk,
            target_language=target_language,
            glossary=glossary,
            chunk_number=chunk_number,
            chunk_count=chunk_count,
        )
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": 0,
            "system": (
                "You are a precise technical documentation translator for Life OS. "
                "Return only translated Markdown. Preserve Markdown structure, code fences, "
                "links, anchors, front matter, placeholders, and glossary terms exactly."
            ),
            "messages": [{"role": "user", "content": prompt}],
        }
        request = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "x-api-key": self.api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except TimeoutError as exc:
            raise TranslationError("Anthropic API request timed out") from exc
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise TranslationError(
                f"Anthropic API returned HTTP {exc.code}: {truncate_error(detail)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise TranslationError(f"Anthropic API request failed: {exc.reason}") from exc

        try:
            parsed = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise TranslationError("Anthropic API returned invalid JSON") from exc

        translated = extract_text_response(parsed)
        if not translated.strip():
            raise TranslationError("Anthropic API returned an empty translation")
        return translated


def truncate_error(message: str, limit: int = 500) -> str:
    if len(message) <= limit:
        return message
    return f"{message[:limit]}..."


def extract_text_response(parsed: object) -> str:
    if not isinstance(parsed, dict):
        raise TranslationError("Anthropic API response was not an object")
    content = parsed.get("content")
    if not isinstance(content, list):
        raise TranslationError("Anthropic API response did not include content")

    text_parts: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str):
                text_parts.append(text)
    if not text_parts:
        raise TranslationError("Anthropic API response did not include text content")
    return "".join(text_parts)


def load_glossary(path: Path = GLOSSARY_PATH) -> Glossary:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise TranslationError(f"Could not read glossary {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise TranslationError(f"Could not parse glossary {path}: {exc}") from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("terms"), dict):
        raise TranslationError(f"Glossary {path} must contain a 'terms' mapping")

    terms: Glossary = {}
    for source_term, translations in raw["terms"].items():
        if not isinstance(source_term, str) or not isinstance(translations, dict):
            raise TranslationError(f"Invalid glossary entry in {path}: {source_term!r}")
        normalized: dict[str, str] = {}
        for language_code, preserved_term in translations.items():
            if not isinstance(language_code, str) or not isinstance(preserved_term, str):
                raise TranslationError(f"Invalid glossary translation for {source_term!r}")
            normalized[language_code] = preserved_term
        terms[source_term] = normalized
    return terms


def build_user_prompt(
    *,
    source_name: str,
    chunk: str,
    target_language: str,
    glossary: Glossary,
    chunk_number: int,
    chunk_count: int,
) -> str:
    glossary_lines = format_glossary(glossary)
    return (
        f"Translate this Markdown from English into {target_language}.\n"
        f"Source file: {source_name}\n"
        f"Chunk: {chunk_number} of {chunk_count}\n\n"
        "Rules:\n"
        "- Preserve Markdown formatting and heading hierarchy.\n"
        "- Preserve code blocks, inline code, URLs, paths, CLI commands, and placeholders.\n"
        "- Preserve glossary terms exactly as specified.\n"
        "- Do not add commentary, wrappers, or explanations.\n\n"
        "<glossary>\n"
        f"{glossary_lines}\n"
        "</glossary>\n\n"
        "<markdown>\n"
        f"{chunk}"
        "\n</markdown>\n"
    )


def format_glossary(glossary: Glossary) -> str:
    lines: list[str] = []
    for source_term in sorted(glossary):
        translations = glossary[source_term]
        rendered = ", ".join(f"{code}: {value}" for code, value in sorted(translations.items()))
        lines.append(f"- {source_term} => {rendered}")
    return "\n".join(lines)


def split_markdown(text: str, max_chars: int = CHUNK_MAX_CHARS) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    in_fence = False
    fence_marker = ""

    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in {"```", "~~~"}:
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""

        is_heading = stripped.startswith("#")
        should_split_before_line = (
            not in_fence
            and current
            and is_heading
            and current_len >= max_chars // 2
        )
        should_split_after_blank = (
            not in_fence
            and current
            and stripped.strip() == ""
            and current_len >= max_chars
        )

        if should_split_before_line or should_split_after_blank:
            chunks.append("".join(current))
            current = []
            current_len = 0

        current.append(line)
        current_len += len(line)

    if current:
        chunks.append("".join(current))
    return chunks


def translate_document(
    *,
    client: TranslationClient,
    source_name: str,
    markdown: str,
    target_language: str,
    glossary: Glossary,
) -> str:
    chunks = split_markdown(markdown)
    translated_chunks: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        translated_chunks.append(
            client.translate_chunk(
                source_name=source_name,
                chunk=chunk,
                target_language=target_language,
                glossary=glossary,
                chunk_number=index,
                chunk_count=len(chunks),
            )
        )
    return "".join(translated_chunks)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate README.md and/or CHANGELOG.md into i18n/zh and i18n/ja."
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="Source English doc to translate: README.md or CHANGELOG.md.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Translate both README.md and CHANGELOG.md.",
    )
    args = parser.parse_args(argv)
    if args.all and args.source:
        parser.error("pass either --all or one source file, not both")
    if not args.all and not args.source:
        parser.error("pass README.md, CHANGELOG.md, or --all")
    if args.source and args.source not in SUPPORTED_SOURCES:
        parser.error("source must be README.md or CHANGELOG.md")
    return args


def parse_float_env(env: Mapping[str, str], name: str, default: float) -> float:
    value = env.get(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise TranslationError(f"{name} must be a number") from exc


def parse_int_env(env: Mapping[str, str], name: str, default: int) -> int:
    value = env.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise TranslationError(f"{name} must be an integer") from exc


def make_anthropic_client(env: Mapping[str, str]) -> AnthropicClient:
    api_key = env["CLAUDE_API_KEY"]
    return AnthropicClient(
        api_key=api_key,
        model=env.get("CLAUDE_MODEL", DEFAULT_MODEL),
        timeout_seconds=parse_float_env(env, "CLAUDE_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS),
        max_tokens=parse_int_env(env, "CLAUDE_MAX_TOKENS", DEFAULT_MAX_TOKENS),
        api_url=env.get("CLAUDE_API_URL", DEFAULT_API_URL),
    )


def requested_sources(args: argparse.Namespace) -> tuple[str, ...]:
    if args.all:
        return SUPPORTED_SOURCES
    return (cast(str, args.source),)


def run(
    argv: Sequence[str],
    *,
    root: Path = REPO_ROOT,
    env: Mapping[str, str] | None = None,
    client_factory: ClientFactory = make_anthropic_client,
) -> int:
    env = os.environ if env is None else env
    args = parse_args(argv)

    if not env.get("CLAUDE_API_KEY"):
        print(
            "CLAUDE_API_KEY is required to translate docs; no i18n files were modified.",
            file=sys.stderr,
        )
        return 2

    try:
        glossary = load_glossary(root / "scripts" / "i18n-glossary.yaml")
        client = client_factory(env)
        pending_writes: dict[Path, str] = {}

        for source_name in requested_sources(args):
            source_path = root / source_name
            source_markdown = source_path.read_text(encoding="utf-8")
            for language_code, target_language in LANGUAGES.items():
                translated = translate_document(
                    client=client,
                    source_name=source_name,
                    markdown=source_markdown,
                    target_language=target_language,
                    glossary=glossary,
                )
                pending_writes[root / "i18n" / language_code / source_name] = translated

        for output_path, translated in pending_writes.items():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(translated, encoding="utf-8")
    except OSError as exc:
        print(f"Translation failed before writing i18n files: {exc}", file=sys.stderr)
        return 1
    except TranslationError as exc:
        print(f"Translation failed; no i18n files were modified: {exc}", file=sys.stderr)
        return 1

    print(f"Translated {', '.join(requested_sources(args))} into i18n/zh and i18n/ja.")
    return 0


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
