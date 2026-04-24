"""Skill Observability CLI for Life OS.

This round intentionally scans only ``~/.claude/skills/*/SKILL.md``. Plugin
sources and shadowed telemetry are represented by the output model, but plugin
discovery is left to the later plugin-source round.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from tools.lib.skills_scanner import (
    EXIT_DATA_SOURCE_ERROR,
    EXIT_OK,
    EXIT_STALE,
    EXIT_UPDATE_AVAILABLE,
    SkillRecord,
    scan_skills,
)
from tools.lib.skills_upstream import (
    UpstreamCacheCorruptError,
    UpstreamChecker,
    UpstreamCheckResult,
    default_cache_path,
    load_upstream_cache,
    parse_upstream_source,
)

COLUMNS: tuple[str, ...] = (
    "name",
    "version",
    "installed-at",
    "source",
    "upstream-latest",
    "status",
    "triggers-hint",
)

STATUS_CURRENT_LOCAL = "\U0001f7e2 current / local"
STATUS_UPDATE_AVAILABLE = "\U0001f7e1 update available"
STATUS_STALE = "\U0001f534 stale (>90 days)"
STATUS_CHECK_FAILED = "\u2753 check failed"

UNKNOWN_VALUE = "?"
UNKNOWN_INSTALLED_AT = "\u2753"
NO_UPSTREAM = "-"


@dataclass(frozen=True)
class NormalizedSkill:
    """Canonical CLI row shape shared by markdown and JSON output."""

    name: str
    version: str
    installed_at: str
    source: str
    upstream_latest: str
    status: str
    triggers_hint: str
    data_source_error: bool = False

    def as_json_object(self) -> dict[str, str]:
        """Return the spec's hyphen-keyed JSON object."""
        return {
            "name": self.name,
            "version": self.version,
            "installed-at": self.installed_at,
            "source": self.source,
            "upstream-latest": self.upstream_latest,
            "status": self.status,
            "triggers-hint": self.triggers_hint,
        }


def build_parser() -> argparse.ArgumentParser:
    """Build the standalone skills CLI parser."""
    parser = argparse.ArgumentParser(
        prog="skills",
        description="Inspect installed Life OS skills.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("list", "check", "stale"):
        command_parser = subparsers.add_parser(command, help=f"{command} skills")
        _add_common_args(command_parser)

    info_parser = subparsers.add_parser("info", help="show one skill")
    info_parser.add_argument("name", help="skill name or id")
    _add_common_args(info_parser)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point used by both ``python -m`` and the unified dispatcher."""
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    command = _namespace_string(args, "command")
    output_format = _namespace_string(args, "format")
    offline = _namespace_bool(args, "offline")

    try:
        normalized = collect_skills(offline=offline)
    except UpstreamCacheCorruptError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_DATA_SOURCE_ERROR

    if command == "info":
        requested_name = _namespace_string(args, "name")
        return _handle_info(normalized, requested_name, output_format)

    if command == "stale":
        stale_rows = [skill for skill in normalized if skill.status == STATUS_STALE]
        print(render_output(stale_rows, output_format))
        if any(skill.data_source_error for skill in normalized):
            return EXIT_DATA_SOURCE_ERROR
        return EXIT_STALE if stale_rows else EXIT_OK

    if command in {"list", "check"}:
        print(render_output(normalized, output_format))
        return exit_code_for_normalized(normalized)

    parser.error(f"unknown command: {command}")
    return EXIT_DATA_SOURCE_ERROR


def collect_skills(*, offline: bool) -> list[NormalizedSkill]:
    """Scan local skills and enrich them with upstream/cache evidence."""
    cache_path = default_cache_path()
    load_upstream_cache(cache_path)
    checker = UpstreamChecker(cache_path=cache_path)
    records = scan_skills()
    return [normalize_record(record, checker=checker, offline=offline) for record in records]


def normalize_record(
    record: SkillRecord,
    *,
    checker: UpstreamChecker,
    offline: bool,
) -> NormalizedSkill:
    """Convert one scanner record into the canonical CLI row."""
    if record.data_source_error:
        return NormalizedSkill(
            name=record.name,
            version=record.version,
            installed_at=_installed_at_display(record),
            source=record.source,
            upstream_latest=UNKNOWN_VALUE,
            status=STATUS_CHECK_FAILED,
            triggers_hint=record.triggers_hint,
            data_source_error=True,
        )

    if _is_local_only_source(record.source):
        return NormalizedSkill(
            name=record.name,
            version=record.version,
            installed_at=_installed_at_display(record),
            source=record.source,
            upstream_latest=NO_UPSTREAM,
            status=_age_status(record),
            triggers_hint=record.triggers_hint,
        )

    upstream = _check_upstream(record.source, checker=checker, offline=offline)
    status = _status_from_upstream(record, upstream)
    return NormalizedSkill(
        name=record.name,
        version=record.version,
        installed_at=_installed_at_display(record),
        source=record.source,
        upstream_latest=_upstream_latest_display(upstream, offline=offline),
        status=status,
        triggers_hint=record.triggers_hint,
    )


def render_output(rows: Sequence[NormalizedSkill], output_format: str) -> str:
    """Render rows as markdown or JSON with the same semantic columns."""
    if output_format == "json":
        return json.dumps(
            [row.as_json_object() for row in rows],
            ensure_ascii=False,
            indent=2,
        )
    if output_format == "markdown":
        return render_markdown(rows)
    raise ValueError(f"unknown output format: {output_format}")


def render_markdown(rows: Sequence[NormalizedSkill]) -> str:
    """Render a stable markdown table."""
    rendered_rows = [
        "| " + " | ".join(COLUMNS) + " |",
        "|---|---:|---|---|---:|---|---|",
    ]
    rendered_rows.extend(
        "| "
        + " | ".join(
            (
                _escape_markdown_cell(row.name),
                _escape_markdown_cell(row.version),
                _escape_markdown_cell(row.installed_at),
                _escape_markdown_cell(row.source),
                _escape_markdown_cell(row.upstream_latest),
                _escape_markdown_cell(row.status),
                _escape_markdown_cell(row.triggers_hint),
            )
        )
        + " |"
        for row in rows
    )
    return "\n".join(rendered_rows)


def exit_code_for_normalized(rows: Iterable[NormalizedSkill]) -> int:
    """Compute aggregate exit code using the required priority order."""
    rows_list = list(rows)
    if any(row.data_source_error for row in rows_list):
        return EXIT_DATA_SOURCE_ERROR
    if any(row.status == STATUS_STALE for row in rows_list):
        return EXIT_STALE
    if any(row.status == STATUS_UPDATE_AVAILABLE for row in rows_list):
        return EXIT_UPDATE_AVAILABLE
    return EXIT_OK


def _handle_info(rows: Sequence[NormalizedSkill], name: str, output_format: str) -> int:
    match = _find_skill(rows, name)
    if match is None:
        print(f"Skill not found: {name}", file=sys.stderr)
        return EXIT_OK

    if output_format == "json":
        print(json.dumps(match.as_json_object(), ensure_ascii=False, indent=2))
    else:
        print(render_markdown([match]))
    return exit_code_for_normalized([match])


def _find_skill(rows: Sequence[NormalizedSkill], name: str) -> NormalizedSkill | None:
    normalized_name = name.casefold()
    for row in rows:
        if row.name.casefold() == normalized_name:
            return row
    for row in rows:
        if _source_id(row.source).casefold() == normalized_name:
            return row
    return None


def _source_id(source: str) -> str:
    if "://" not in source:
        return source
    return source.rsplit("/", maxsplit=1)[-1]


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="output format",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="use only local metadata and cache evidence",
    )


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _namespace_string(namespace: argparse.Namespace, name: str) -> str:
    value = getattr(namespace, name)
    if not isinstance(value, str):
        raise TypeError(f"expected {name} to be a string")
    return value


def _namespace_bool(namespace: argparse.Namespace, name: str) -> bool:
    value = getattr(namespace, name)
    if not isinstance(value, bool):
        raise TypeError(f"expected {name} to be a bool")
    return value


def _is_local_only_source(source: str) -> bool:
    parsed = parse_upstream_source(source)
    return parsed.kind == "local" or source == "local" or source.startswith("skills://")


def _check_upstream(
    source: str,
    *,
    checker: UpstreamChecker,
    offline: bool,
) -> UpstreamCheckResult:
    try:
        return checker.check(source, offline=offline)
    except UpstreamCacheCorruptError:
        raise
    except OSError as exc:
        parsed = parse_upstream_source(source)
        return UpstreamCheckResult(
            source=source,
            kind=parsed.kind,
            status="check_failed",
            url=parsed.url,
            reliable=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def _installed_at_display(record: SkillRecord) -> str:
    if record.installed_at is None:
        return UNKNOWN_INSTALLED_AT
    return record.installed_at


def _age_status(record: SkillRecord) -> str:
    if record.baseline_at is not None and _is_stale(record.baseline_at):
        return STATUS_STALE
    return STATUS_CURRENT_LOCAL


def _status_from_upstream(record: SkillRecord, upstream: UpstreamCheckResult) -> str:
    if record.baseline_at is not None and _is_stale(record.baseline_at):
        return STATUS_STALE

    if (
        upstream.latest_version is not None
        and _is_newer_version(upstream.latest_version, record.version)
    ):
        return STATUS_UPDATE_AVAILABLE

    if upstream.status in {"local", "ok"} and upstream.reliable:
        return STATUS_CURRENT_LOCAL

    return STATUS_CHECK_FAILED


def _upstream_latest_display(upstream: UpstreamCheckResult, *, offline: bool) -> str:
    if upstream.status == "local":
        return NO_UPSTREAM

    if offline:
        if upstream.from_cache:
            return f"{UNKNOWN_VALUE} ({_cache_age_label(upstream)})"
        return f"{UNKNOWN_VALUE} (no cache)"

    if upstream.latest_version is not None:
        if upstream.from_cache:
            return f"{upstream.latest_version} ({_cache_age_label(upstream)})"
        return upstream.latest_version

    if upstream.from_cache:
        return f"{UNKNOWN_VALUE} ({_cache_age_label(upstream)})"
    return f"{UNKNOWN_VALUE} (no cache)"


def _cache_age_label(upstream: UpstreamCheckResult) -> str:
    if upstream.cache_age_seconds is None:
        return "cached ?d ago"
    days = int(upstream.cache_age_seconds // 86_400)
    return f"cached {days}d ago"


def _is_stale(baseline_at: datetime) -> bool:
    current_day = datetime.now(UTC).date()
    return (current_day - baseline_at.date()).days > 90


def _is_newer_version(latest: str, installed: str) -> bool:
    """Return whether ``latest`` is newer using a small dependency-free parser."""
    latest_clean = _clean_version(latest)
    installed_clean = _clean_version(installed)
    if latest_clean == installed_clean:
        return False
    latest_parts = _version_parts(latest_clean)
    installed_parts = _version_parts(installed_clean)
    if not latest_parts or not installed_parts:
        return latest_clean.casefold() > installed_clean.casefold()
    return latest_parts > installed_parts


def _clean_version(value: str) -> str:
    clean_value = value.strip()
    if clean_value[:1].casefold() == "v" and len(clean_value) > 1:
        return clean_value[1:]
    return clean_value


def _version_parts(value: str) -> tuple[str, ...]:
    parts: list[str] = []
    for token in re.findall(r"[0-9]+|[A-Za-z]+", value):
        if token.isdigit():
            parts.append(f"0{int(token):020d}")
        else:
            parts.append(f"1{token.casefold()}")
    zero_part = f"0{0:020d}"
    while parts and parts[-1] == zero_part:
        parts.pop()
    return tuple(parts)


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
