#!/usr/bin/env python3
# Forked from NousResearch/hermes-agent (MIT License) commit 59b56d445c34e1d4bf797f5345b802c7b5986c72
# Adapted for Life OS v1.7.2
"""Life OS method manager.

Creates and updates Life OS methods, the procedural memory layer for reusable
decision workflows. Methods are stored locally under:

    _meta/methods/{method_id}/{method_id}.md
    _meta/methods/{method_id}/evolution.log

The schema follows references/method-library-spec.md when that file exists.
If the spec is not present, this tool still requires YAML frontmatter plus a
markdown body.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import tempfile
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - exercised only in incomplete envs
    yaml = None

logger = logging.getLogger(__name__)

METHODS_ROOT = Path("_meta") / "methods"
METHOD_FILE_SUFFIX = ".md"
EVOLUTION_LOG = "evolution.log"
METHOD_SPEC_PATH = Path("references") / "method-library-spec.md"

MAX_METHOD_ID_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_METHOD_CONTENT_CHARS = 100_000

VALID_METHOD_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
VALID_DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9_-]{0,62}[a-z0-9])?$")
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n(.*)\Z", re.DOTALL)

METHOD_STATUSES = {"tentative", "confirmed", "canonical"}

SPEC_REQUIRED_FIELDS = (
    "method_id",
    "name",
    "description",
    "domain",
    "status",
    "confidence",
    "times_used",
    "last_used",
    "applicable_when",
    "not_applicable_when",
    "source_sessions",
    "evidence_count",
    "challenges",
    "related_concepts",
    "related_methods",
)

FALLBACK_REQUIRED_FIELDS = (
    "method_id",
    "name",
    "description",
)


class MethodManagerError(ValueError):
    """Raised when a requested method operation is invalid."""


def _now_iso() -> str:
    """Return an ISO 8601 timestamp suitable for method frontmatter."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def _require_yaml() -> None:
    if yaml is None:
        raise MethodManagerError(
            "PyYAML is required to parse method frontmatter. Install project "
            "dependencies with `uv sync`."
        )


def _schema_required_fields(root: Path) -> tuple[str, ...]:
    """Return strict schema fields when the method spec exists."""
    return SPEC_REQUIRED_FIELDS if (root / METHOD_SPEC_PATH).exists() else FALLBACK_REQUIRED_FIELDS


def validate_method_id(method_id: str) -> None:
    """Validate Life OS method_id format."""
    if not method_id:
        raise MethodManagerError("method_id is required.")
    if len(method_id) > MAX_METHOD_ID_LENGTH:
        raise MethodManagerError(f"method_id exceeds {MAX_METHOD_ID_LENGTH} characters.")
    if not VALID_METHOD_ID_RE.match(method_id):
        raise MethodManagerError(
            "Invalid method_id. Use lowercase letters, numbers, and hyphens; "
            "start and end with a letter or digit."
        )


def _validate_domain(domain: str) -> None:
    if not domain:
        raise MethodManagerError("domain is required.")
    if not VALID_DOMAIN_RE.match(domain):
        raise MethodManagerError(
            "Invalid domain. Use lowercase letters, numbers, hyphens, and underscores; "
            "start and end with a letter or digit."
        )


def _ensure_root(root: Path | str | None) -> Path:
    return Path.cwd().resolve() if root is None else Path(root).expanduser().resolve()


def method_dir(root: Path | str | None, method_id: str) -> Path:
    """Return _meta/methods/{method_id} for a validated method_id."""
    validate_method_id(method_id)
    resolved_root = _ensure_root(root)
    return resolved_root / METHODS_ROOT / method_id


def method_path(root: Path | str | None, method_id: str) -> Path:
    """Return _meta/methods/{method_id}/{method_id}.md."""
    return method_dir(root, method_id) / f"{method_id}{METHOD_FILE_SUFFIX}"


def evolution_log_path(root: Path | str | None, method_id: str) -> Path:
    """Return _meta/methods/{method_id}/evolution.log."""
    return method_dir(root, method_id) / EVOLUTION_LOG


def _atomic_write_text(file_path: Path, content: str, encoding: str = "utf-8") -> None:
    """Atomically write text using a temp file in the target directory."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        dir=str(file_path.parent),
        prefix=f".{file_path.name}.tmp.",
        suffix="",
    )
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as handle:
            handle.write(content)
        Path(temp_path).replace(file_path)
    except Exception:
        try:
            Path(temp_path).unlink()
        except OSError:
            logger.error("Failed to remove temporary file %s", temp_path, exc_info=True)
        raise


def _append_evolution_log(path: Path, entry: str) -> None:
    """Append one timestamped line to evolution.log."""
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = " ".join(entry.strip().split())
    if not normalized:
        return
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{_now_iso()} | {normalized}\n")


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse markdown with YAML frontmatter."""
    _require_yaml()
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise MethodManagerError(
            "Method markdown must start with YAML frontmatter delimited by ---."
        )

    try:
        parsed = yaml.safe_load(match.group(1)) or {}
    except Exception as exc:
        raise MethodManagerError(f"YAML frontmatter parse error: {exc}") from exc

    if not isinstance(parsed, dict):
        raise MethodManagerError("Frontmatter must be a YAML mapping.")
    return parsed, match.group(2)


def _dump_frontmatter(frontmatter: Mapping[str, Any], body: str) -> str:
    """Serialize frontmatter plus body to markdown."""
    _require_yaml()
    fm_text = yaml.safe_dump(
        dict(frontmatter),
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    normalized_body = body.strip() + "\n"
    return f"---\n{fm_text}---\n{normalized_body}"


def _validate_content_size(content: str, label: str = "method markdown") -> None:
    if len(content) > MAX_METHOD_CONTENT_CHARS:
        raise MethodManagerError(
            f"{label} is {len(content):,} characters "
            f"(limit: {MAX_METHOD_CONTENT_CHARS:,}). Split the method."
        )


def _is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _validate_condition_list(value: Any, *, field_name: str, require_signal: bool) -> None:
    if not isinstance(value, list):
        raise MethodManagerError(f"{field_name} must be a list.")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise MethodManagerError(f"{field_name}[{index}] must be a mapping.")
        if not isinstance(item.get("condition"), str) or not item["condition"].strip():
            raise MethodManagerError(f"{field_name}[{index}].condition must be a non-empty string.")
        if require_signal and (
            not isinstance(item.get("signal"), str) or not item["signal"].strip()
        ):
            raise MethodManagerError(f"{field_name}[{index}].signal must be a non-empty string.")


def _validate_string_list(value: Any, *, field_name: str) -> None:
    if not isinstance(value, list):
        raise MethodManagerError(f"{field_name} must be a list.")
    if not all(isinstance(item, str) for item in value):
        raise MethodManagerError(f"{field_name} must contain only strings.")


def validate_method_markdown(content: str, *, root: Path | str | None = None) -> dict[str, Any]:
    """Validate method markdown and return parsed frontmatter."""
    resolved_root = _ensure_root(root)
    _validate_content_size(content)

    frontmatter, body = _parse_frontmatter(content)
    if not body.strip():
        raise MethodManagerError("Method markdown must include a body after frontmatter.")

    required_fields = _schema_required_fields(resolved_root)
    missing = [field for field in required_fields if field not in frontmatter]
    if missing:
        raise MethodManagerError(f"Method frontmatter missing required field(s): {', '.join(missing)}.")

    method_id = str(frontmatter.get("method_id", ""))
    validate_method_id(method_id)

    for key in ("name", "description"):
        if not isinstance(frontmatter.get(key), str) or not frontmatter[key].strip():
            raise MethodManagerError(f"{key} must be a non-empty string.")

    if len(str(frontmatter["description"])) > MAX_DESCRIPTION_LENGTH:
        raise MethodManagerError(f"description exceeds {MAX_DESCRIPTION_LENGTH} characters.")

    if "domain" in frontmatter:
        if not isinstance(frontmatter["domain"], str):
            raise MethodManagerError("domain must be a string.")
        _validate_domain(frontmatter["domain"])

    if "status" in frontmatter and frontmatter["status"] not in METHOD_STATUSES:
        allowed = ", ".join(sorted(METHOD_STATUSES))
        raise MethodManagerError(f"status must be one of: {allowed}.")

    if "confidence" in frontmatter:
        if not _is_number(frontmatter["confidence"]):
            raise MethodManagerError("confidence must be a number between 0 and 1.")
        if float(frontmatter["confidence"]) < 0 or float(frontmatter["confidence"]) > 1:
            raise MethodManagerError("confidence must be between 0 and 1.")

    for field_name in ("times_used", "evidence_count", "challenges"):
        if field_name in frontmatter and not _is_non_negative_int(frontmatter[field_name]):
            raise MethodManagerError(f"{field_name} must be a non-negative integer.")

    if "last_used" in frontmatter and not isinstance(frontmatter["last_used"], str):
        raise MethodManagerError("last_used must be an ISO 8601 string.")

    if "applicable_when" in frontmatter:
        _validate_condition_list(
            frontmatter["applicable_when"],
            field_name="applicable_when",
            require_signal=True,
        )
    if "not_applicable_when" in frontmatter:
        _validate_condition_list(
            frontmatter["not_applicable_when"],
            field_name="not_applicable_when",
            require_signal=False,
        )

    for field_name in ("source_sessions", "related_concepts", "related_methods"):
        if field_name in frontmatter:
            _validate_string_list(frontmatter[field_name], field_name=field_name)

    return frontmatter


def compute_confidence(evidence_count: int, challenges: int) -> float:
    """Compute confidence using the Life OS method-library formula."""
    if evidence_count < 0 or challenges < 0:
        raise MethodManagerError("evidence_count and challenges must be non-negative.")
    denominator = evidence_count + challenges * 2
    if denominator == 0:
        return 0.0
    return round(max(0.0, min(1.0, evidence_count / denominator)), 3)


def _default_confidence(status: str, evidence_count: int, challenges: int) -> float:
    if status == "tentative":
        return 0.3
    return compute_confidence(evidence_count, challenges)


def _normalize_string_list(values: Sequence[str] | None) -> list[str]:
    if not values:
        return []
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _default_body(name: str, description: str) -> str:
    return (
        f"# {name}\n\n"
        "## Summary\n"
        f"{description}\n\n"
        "## Steps\n"
        "1. Describe the reusable workflow step.\n\n"
        "## When to Use\n"
        "- Add conditions that indicate this method applies.\n\n"
        "## When NOT to Use\n"
        "- Add anti-conditions where this method fails or misleads.\n\n"
        "## Evolution Log\n"
        f"See {EVOLUTION_LOG}.\n\n"
        "## Warnings\n"
        "- Add common pitfalls and failure modes.\n\n"
        "## Related\n"
        "- Add related concepts or methods.\n"
    )


def build_method_markdown(
    *,
    method_id: str,
    name: str,
    description: str,
    domain: str = "method",
    status: str = "tentative",
    confidence: float | None = None,
    times_used: int = 1,
    last_used: str | None = None,
    applicable_when: list[dict[str, str]] | None = None,
    not_applicable_when: list[dict[str, str]] | None = None,
    source_sessions: Sequence[str] | None = None,
    evidence_count: int = 1,
    challenges: int = 0,
    related_concepts: Sequence[str] | None = None,
    related_methods: Sequence[str] | None = None,
    body: str | None = None,
    root: Path | str | None = None,
) -> str:
    """Build a schema-aligned method markdown document."""
    validate_method_id(method_id)
    _validate_domain(domain)
    if status not in METHOD_STATUSES:
        raise MethodManagerError(f"status must be one of: {', '.join(sorted(METHOD_STATUSES))}.")
    if not _is_non_negative_int(times_used):
        raise MethodManagerError("times_used must be a non-negative integer.")
    if not _is_non_negative_int(evidence_count):
        raise MethodManagerError("evidence_count must be a non-negative integer.")
    if not _is_non_negative_int(challenges):
        raise MethodManagerError("challenges must be a non-negative integer.")

    confidence_value = (
        _default_confidence(status, evidence_count, challenges)
        if confidence is None
        else float(confidence)
    )

    frontmatter: dict[str, Any] = {
        "method_id": method_id,
        "name": name,
        "description": description,
        "domain": domain,
        "status": status,
        "confidence": confidence_value,
        "times_used": times_used,
        "last_used": last_used or _now_iso(),
        "applicable_when": applicable_when or [],
        "not_applicable_when": not_applicable_when or [],
        "source_sessions": _normalize_string_list(source_sessions),
        "evidence_count": evidence_count,
        "challenges": challenges,
        "related_concepts": _normalize_string_list(related_concepts),
        "related_methods": _normalize_string_list(related_methods),
    }
    markdown = _dump_frontmatter(frontmatter, body or _default_body(name, description))
    validate_method_markdown(markdown, root=root)
    return markdown


def _ensure_content_method_id(content: str, method_id: str, *, root: Path) -> dict[str, Any]:
    frontmatter = validate_method_markdown(content, root=root)
    if frontmatter["method_id"] != method_id:
        raise MethodManagerError(
            f"Frontmatter method_id '{frontmatter['method_id']}' does not match '{method_id}'."
        )
    return frontmatter


def create_method(
    method_id: str,
    *,
    root: Path | str | None = None,
    content: str | None = None,
    name: str | None = None,
    description: str | None = None,
    domain: str = "method",
    status: str = "tentative",
    confidence: float | None = None,
    body: str | None = None,
    source_sessions: Sequence[str] | None = None,
    applicable_when: list[dict[str, str]] | None = None,
    not_applicable_when: list[dict[str, str]] | None = None,
    related_concepts: Sequence[str] | None = None,
    related_methods: Sequence[str] | None = None,
    overwrite: bool = False,
    evolution_entry: str | None = None,
) -> dict[str, Any]:
    """Create a Life OS method directory, method markdown, and evolution.log."""
    resolved_root = _ensure_root(root)
    validate_method_id(method_id)
    target = method_path(resolved_root, method_id)
    log_target = evolution_log_path(resolved_root, method_id)

    if target.exists() and not overwrite:
        raise MethodManagerError(f"Method '{method_id}' already exists at {target}.")

    if content is None:
        if not name:
            raise MethodManagerError("name is required when content is not provided.")
        if not description:
            raise MethodManagerError("description is required when content is not provided.")
        content = build_method_markdown(
            method_id=method_id,
            name=name,
            description=description,
            domain=domain,
            status=status,
            confidence=confidence,
            body=body,
            source_sessions=source_sessions,
            applicable_when=applicable_when,
            not_applicable_when=not_applicable_when,
            related_concepts=related_concepts,
            related_methods=related_methods,
            root=resolved_root,
        )
    else:
        _ensure_content_method_id(content, method_id, root=resolved_root)

    _atomic_write_text(target, content.strip() + "\n")
    _append_evolution_log(log_target, evolution_entry or "Created method.")

    return {
        "success": True,
        "action": "create",
        "method_id": method_id,
        "method_path": str(target),
        "evolution_log": str(log_target),
    }


def load_method(method_id: str, *, root: Path | str | None = None) -> dict[str, Any]:
    """Load an existing method and return path, frontmatter, and body."""
    resolved_root = _ensure_root(root)
    target = method_path(resolved_root, method_id)
    if not target.exists():
        raise MethodManagerError(f"Method '{method_id}' not found at {target}.")

    content = target.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(content)
    validate_method_markdown(content, root=resolved_root)
    return {
        "method_id": method_id,
        "method_path": str(target),
        "frontmatter": frontmatter,
        "body": body,
    }


def _merge_unique_strings(existing: list[str], additions: Sequence[str] | None) -> list[str]:
    result = list(existing)
    for item in additions or []:
        if item not in result:
            result.append(item)
    return result


def update_method(
    method_id: str,
    *,
    root: Path | str | None = None,
    content: str | None = None,
    body: str | None = None,
    frontmatter_updates: Mapping[str, Any] | None = None,
    source_sessions: Sequence[str] | None = None,
    append_evolution: str | None = None,
    outcome: str | None = None,
    increment_times_used: bool = False,
    recompute_confidence: bool = False,
) -> dict[str, Any]:
    """Update an existing Life OS method.

    When content is provided, it replaces the full method markdown after
    validation. Otherwise, provided frontmatter fields and/or body replace only
    those parts.
    """
    resolved_root = _ensure_root(root)
    validate_method_id(method_id)
    target = method_path(resolved_root, method_id)
    log_target = evolution_log_path(resolved_root, method_id)
    if not target.exists():
        raise MethodManagerError(f"Method '{method_id}' not found at {target}.")

    if content is not None and (body is not None or frontmatter_updates):
        raise MethodManagerError(
            "Provide either full content or partial updates, not both."
        )

    if content is not None:
        _ensure_content_method_id(content, method_id, root=resolved_root)
        new_content = content.strip() + "\n"
        log_entry = append_evolution or "Replaced method markdown."
    else:
        existing_content = target.read_text(encoding="utf-8")
        frontmatter, existing_body = _parse_frontmatter(existing_content)
        validate_method_markdown(existing_content, root=resolved_root)

        updates = dict(frontmatter_updates or {})
        for key, value in updates.items():
            if value is not None:
                frontmatter[key] = value

        if source_sessions:
            frontmatter["source_sessions"] = _merge_unique_strings(
                list(frontmatter.get("source_sessions", [])),
                source_sessions,
            )

        if outcome is not None:
            if outcome not in {"used", "worked", "failed", "revised"}:
                raise MethodManagerError("outcome must be one of: used, worked, failed, revised.")
            increment_times_used = increment_times_used or outcome in {"used", "worked", "failed"}
            if outcome == "worked":
                frontmatter["evidence_count"] = int(frontmatter.get("evidence_count", 0)) + 1
                recompute_confidence = True
            elif outcome == "failed":
                frontmatter["challenges"] = int(frontmatter.get("challenges", 0)) + 1
                recompute_confidence = True

        if increment_times_used:
            frontmatter["times_used"] = int(frontmatter.get("times_used", 0)) + 1
            frontmatter["last_used"] = _now_iso()

        if recompute_confidence:
            frontmatter["confidence"] = compute_confidence(
                int(frontmatter.get("evidence_count", 0)),
                int(frontmatter.get("challenges", 0)),
            )

        new_content = _dump_frontmatter(frontmatter, body if body is not None else existing_body)
        _ensure_content_method_id(new_content, method_id, root=resolved_root)
        log_entry = append_evolution or _default_update_log(updates, outcome, body is not None)

    _atomic_write_text(target, new_content)
    if log_entry:
        _append_evolution_log(log_target, log_entry)

    return {
        "success": True,
        "action": "update",
        "method_id": method_id,
        "method_path": str(target),
        "evolution_log": str(log_target),
    }


def _default_update_log(updates: Mapping[str, Any], outcome: str | None, body_changed: bool) -> str:
    details: list[str] = []
    if updates:
        details.append("frontmatter updated")
    if body_changed:
        details.append("body updated")
    if outcome:
        details.append(f"outcome recorded: {outcome}")
    return "Updated method: " + ", ".join(details) + "." if details else "Updated method."


def method_manage(action: str, method_id: str, **kwargs: Any) -> str:
    """JSON wrapper for create/update method operations."""
    try:
        if action == "create":
            result = create_method(method_id, **kwargs)
        elif action == "update":
            result = update_method(method_id, **kwargs)
        else:
            raise MethodManagerError("Unknown action. Use: create, update.")
    except MethodManagerError as exc:
        result = {"success": False, "error": str(exc)}
    except OSError as exc:
        result = {"success": False, "error": f"I/O error: {exc}"}
    return json.dumps(result, ensure_ascii=False)


METHOD_MANAGE_SCHEMA: dict[str, Any] = {
    "name": "method_manage",
    "description": (
        "Create or update Life OS methods, the reusable decision-workflow "
        "memory stored under _meta/methods/{method_id}/{method_id}.md with "
        "a sibling evolution.log."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "update"],
                "description": "The method operation to perform.",
            },
            "method_id": {
                "type": "string",
                "description": "Lowercase method id using hyphens, max 64 characters.",
            },
            "root": {
                "type": "string",
                "description": "Second-brain root. Defaults to current working directory.",
            },
            "content": {
                "type": "string",
                "description": "Full method markdown with YAML frontmatter and body.",
            },
            "name": {
                "type": "string",
                "description": "Display name for create when content is not supplied.",
            },
            "description": {
                "type": "string",
                "description": "One-line method description for create.",
            },
            "domain": {
                "type": "string",
                "description": "Life OS method domain, defaults to 'method'.",
            },
            "status": {
                "type": "string",
                "enum": ["tentative", "confirmed", "canonical"],
                "description": "Method maturity status.",
            },
            "body": {
                "type": "string",
                "description": "Markdown body for create or partial update.",
            },
            "append_evolution": {
                "type": "string",
                "description": "Line to append to evolution.log during update.",
            },
            "outcome": {
                "type": "string",
                "enum": ["used", "worked", "failed", "revised"],
                "description": "Outcome to record during update.",
            },
        },
        "required": ["action", "method_id"],
    },
}


def _read_text_arg(value: str | None, file_path: str | None) -> str | None:
    if value is not None and file_path is not None:
        raise MethodManagerError("Provide inline text or file path, not both.")
    if value is not None:
        return value
    if file_path is None:
        return None
    if file_path == "-":
        return sys.stdin.read()
    return Path(file_path).read_text(encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill_manager.py",
        description="Create or update Life OS methods.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    create = subparsers.add_parser("create", help="Create a method.")
    create.add_argument("method_id")
    create.add_argument("--root", type=Path, default=Path.cwd())
    create.add_argument("--content", help="Full method markdown.")
    create.add_argument("--content-file", help="Path to full method markdown, or '-' for stdin.")
    create.add_argument("--name")
    create.add_argument("--description")
    create.add_argument("--domain", default="method")
    create.add_argument("--status", choices=sorted(METHOD_STATUSES), default="tentative")
    create.add_argument("--confidence", type=float)
    create.add_argument("--body")
    create.add_argument("--body-file", help="Path to markdown body, or '-' for stdin.")
    create.add_argument("--source-session", action="append", default=[])
    create.add_argument("--related-concept", action="append", default=[])
    create.add_argument("--related-method", action="append", default=[])
    create.add_argument("--evolution-entry")
    create.add_argument("--overwrite", action="store_true")

    update = subparsers.add_parser("update", help="Update a method.")
    update.add_argument("method_id")
    update.add_argument("--root", type=Path, default=Path.cwd())
    update.add_argument("--content", help="Full replacement method markdown.")
    update.add_argument("--content-file", help="Path to replacement markdown, or '-' for stdin.")
    update.add_argument("--name")
    update.add_argument("--description")
    update.add_argument("--domain")
    update.add_argument("--status", choices=sorted(METHOD_STATUSES))
    update.add_argument("--confidence", type=float)
    update.add_argument("--body")
    update.add_argument("--body-file", help="Path to replacement body, or '-' for stdin.")
    update.add_argument("--source-session", action="append", default=[])
    update.add_argument("--append-evolution")
    update.add_argument("--outcome", choices=["used", "worked", "failed", "revised"])
    update.add_argument("--increment-times-used", action="store_true")
    update.add_argument("--recompute-confidence", action="store_true")

    return parser


def _cli_create(args: argparse.Namespace) -> dict[str, Any]:
    content = _read_text_arg(args.content, args.content_file)
    body = _read_text_arg(args.body, args.body_file)
    return create_method(
        args.method_id,
        root=args.root,
        content=content,
        name=args.name,
        description=args.description,
        domain=args.domain,
        status=args.status,
        confidence=args.confidence,
        body=body,
        source_sessions=args.source_session,
        related_concepts=args.related_concept,
        related_methods=args.related_method,
        overwrite=args.overwrite,
        evolution_entry=args.evolution_entry,
    )


def _cli_update(args: argparse.Namespace) -> dict[str, Any]:
    content = _read_text_arg(args.content, args.content_file)
    body = _read_text_arg(args.body, args.body_file)
    frontmatter_updates = {
        "name": args.name,
        "description": args.description,
        "domain": args.domain,
        "status": args.status,
        "confidence": args.confidence,
    }
    frontmatter_updates = {
        key: value for key, value in frontmatter_updates.items() if value is not None
    }
    return update_method(
        args.method_id,
        root=args.root,
        content=content,
        body=body,
        frontmatter_updates=frontmatter_updates,
        source_sessions=args.source_session,
        append_evolution=args.append_evolution,
        outcome=args.outcome,
        increment_times_used=args.increment_times_used,
        recompute_confidence=args.recompute_confidence,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Prints JSON result and returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.action == "create":
            result = _cli_create(args)
        elif args.action == "update":
            result = _cli_update(args)
        else:
            raise MethodManagerError("Unknown action. Use: create, update.")
    except MethodManagerError as exc:
        result = {"success": False, "error": str(exc)}
    except OSError as exc:
        result = {"success": False, "error": f"I/O error: {exc}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
