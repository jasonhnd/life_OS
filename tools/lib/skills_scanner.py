"""Local skill inventory scanner for Life OS skill observability.

Code Round 1 intentionally scans only ``~/.claude/skills/*/SKILL.md``.
Plugin metadata and upstream checks are implemented by later rounds.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Literal

STATUS_CURRENT_LOCAL = "✅ current / local"
STATUS_UPDATE_AVAILABLE = "⬆️ update available"
STATUS_STALE = "⚠️ stale (>90 days)"
STATUS_CHECK_FAILED = "❓ check failed"

EXIT_OK = 0
EXIT_UPDATE_AVAILABLE = 1
EXIT_STALE = 2
EXIT_DATA_SOURCE_ERROR = 3

STALE_AFTER_DAYS = 90
UNKNOWN_INSTALLED_AT = "?"

BaselineSource = Literal["frontmatter", "mtime", "unknown"]
FrontmatterValue = str | tuple[str, ...] | None


class SkillScanError(ValueError):
    """Raised when one SKILL.md file cannot be parsed into known metadata."""


@dataclass(frozen=True)
class SkillRecord:
    """Normalized view of one local ``SKILL.md`` record."""

    id: str
    name: str
    version: str
    description: str
    triggers: tuple[str, ...]
    installed_at: str | None
    source: str
    path: Path
    status: str
    error: str | None
    mtime: datetime | None
    baseline_at: datetime | None
    baseline_source: BaselineSource
    data_source_error: bool = False

    @property
    def triggers_hint(self) -> str:
        """Return the canonical comma-separated first-three trigger hint."""
        return triggers_hint(self.triggers)

    @property
    def installed_at_display(self) -> str:
        """Return display-safe installed-at text for CLI table output."""
        return self.installed_at or UNKNOWN_INSTALLED_AT


def default_skills_root(home: Path | None = None) -> Path:
    """Return the Code Round 1 skill root under ``~/.claude/skills``."""
    base = home if home is not None else Path.home()
    return base / ".claude" / "skills"


def scan_skills(
    skills_root: Path | None = None,
    *,
    home: Path | None = None,
    today: date | None = None,
) -> list[SkillRecord]:
    """Scan local ``SKILL.md`` files and return normalized records.

    ``skills_root`` is the direct ``~/.claude/skills`` directory. Passing it
    in tests avoids touching a real user home directory.
    """
    root = skills_root if skills_root is not None else default_skills_root(home)
    if not root.exists():
        return []
    current_day = today or date.today()
    return [read_skill_record(path, today=current_day) for path in iter_skill_paths(root)]


def iter_skill_paths(skills_root: Path) -> list[Path]:
    """Return ``*/SKILL.md`` paths in stable skill-id order."""
    if not skills_root.exists():
        return []
    return sorted(
        (path for path in skills_root.glob("*/SKILL.md") if path.is_file()),
        key=lambda path: path.parent.name.casefold(),
    )


def read_skill_record(path: Path, *, today: date | None = None) -> SkillRecord:
    """Read one ``SKILL.md`` and convert parse errors into a failed record."""
    current_day = today or date.today()
    try:
        content = path.read_text(encoding="utf-8")
        frontmatter = parse_skill_frontmatter(content, source_path=path)
        return record_from_frontmatter(path, frontmatter, today=current_day)
    except (OSError, SkillScanError, ValueError) as exc:
        return failed_skill_record(path, str(exc))


def parse_skill_frontmatter(
    content: str, *, source_path: Path | None = None
) -> dict[str, FrontmatterValue]:
    """Parse the small YAML-ish frontmatter subset used by skill metadata."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SkillScanError(_with_source("missing frontmatter", source_path))

    closing_index = _find_frontmatter_close(lines)
    if closing_index is None:
        raise SkillScanError(_with_source("missing closing frontmatter marker", source_path))

    frontmatter_lines = lines[1:closing_index]
    parsed: dict[str, FrontmatterValue] = {}
    index = 0
    while index < len(frontmatter_lines):
        raw_line = frontmatter_lines[index]
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if raw_line[:1].isspace():
            raise SkillScanError(_with_source(f"unexpected indented line: {stripped}", source_path))
        if ":" not in raw_line:
            raise SkillScanError(_with_source(f"invalid frontmatter line: {stripped}", source_path))

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        if not key:
            raise SkillScanError(_with_source("empty frontmatter key", source_path))
        if key in parsed:
            raise SkillScanError(_with_source(f"duplicate frontmatter key: {key}", source_path))

        value = _strip_inline_comment(raw_value.strip())
        if value == "":
            block_values, index = _parse_indented_list(frontmatter_lines, index + 1, source_path)
            parsed[key] = block_values
            continue
        if value in {"|", ">"}:
            block_text, index = _parse_block_scalar(
                frontmatter_lines,
                index + 1,
                folded=value == ">",
            )
            parsed[key] = block_text
            continue
        if value.startswith("["):
            parsed[key] = tuple(_parse_inline_list(value, source_path))
        else:
            parsed[key] = _parse_scalar(value, source_path)
        index += 1

    return parsed


def record_from_frontmatter(
    path: Path,
    frontmatter: dict[str, FrontmatterValue],
    *,
    today: date | None = None,
) -> SkillRecord:
    """Normalize parsed frontmatter into a ``SkillRecord``."""
    current_day = today or date.today()
    skill_id = path.parent.name
    errors: list[str] = []
    mtime = file_mtime(path)

    name = _string_field(frontmatter, "name", errors) or skill_id
    raw_source = _string_field(frontmatter, "source", errors)
    source = raw_source or f"skills://{skill_id}"

    raw_version = _string_field(frontmatter, "version", errors)
    version = raw_version or "local"
    description = _string_field(frontmatter, "description", errors) or ""
    triggers = _triggers_field(frontmatter, errors)

    raw_installed_at = _string_field(frontmatter, "installed-at", errors)
    baseline_at: datetime | None = None
    baseline_source: BaselineSource = "unknown"
    installed_at: str | None = None
    if raw_installed_at:
        try:
            baseline_at = parse_installed_at(raw_installed_at)
            baseline_source = "frontmatter"
            installed_at = raw_installed_at
        except ValueError as exc:
            errors.append(str(exc))
    elif mtime is not None:
        baseline_at = mtime
        baseline_source = "mtime"
        installed_at = mtime.date().isoformat()

    data_source_error = bool(errors)
    if data_source_error:
        status = STATUS_CHECK_FAILED
    elif is_stale(baseline_at, today=current_day):
        status = STATUS_STALE
    else:
        status = STATUS_CURRENT_LOCAL

    return SkillRecord(
        id=skill_id,
        name=name,
        version=version,
        description=description,
        triggers=triggers,
        installed_at=installed_at,
        source=source,
        path=path,
        status=status,
        error="; ".join(errors) if errors else None,
        mtime=mtime,
        baseline_at=baseline_at,
        baseline_source=baseline_source,
        data_source_error=data_source_error,
    )


def failed_skill_record(path: Path, error: str) -> SkillRecord:
    """Build a failed record for one unreadable or unparseable skill file."""
    skill_id = path.parent.name
    mtime = file_mtime(path)
    return SkillRecord(
        id=skill_id,
        name=skill_id,
        version="?",
        description="",
        triggers=(),
        installed_at=mtime.date().isoformat() if mtime is not None else None,
        source=f"skills://{skill_id}",
        path=path,
        status=STATUS_CHECK_FAILED,
        error=error,
        mtime=mtime,
        baseline_at=mtime,
        baseline_source="mtime" if mtime is not None else "unknown",
        data_source_error=True,
    )


def file_mtime(path: Path) -> datetime | None:
    """Return file mtime as a timezone-aware UTC datetime, or ``None``."""
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    except OSError:
        return None


def parse_installed_at(value: str) -> datetime:
    """Parse a frontmatter ``installed-at`` value as date or ISO datetime."""
    clean_value = value.strip()
    if not clean_value:
        raise ValueError("installed-at is empty")

    try:
        date_value = date.fromisoformat(clean_value)
    except ValueError:
        date_value = None
    if date_value is not None:
        return datetime.combine(date_value, time.min, tzinfo=UTC)

    iso_value = clean_value[:-1] + "+00:00" if clean_value.endswith("Z") else clean_value
    try:
        parsed = datetime.fromisoformat(iso_value)
    except ValueError as exc:
        raise ValueError(f"invalid installed-at value: {value}") from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def staleness_baseline(
    installed_at: str | None, mtime: datetime | None
) -> datetime | None:
    """Return installed-at first, mtime fallback second, else ``None``."""
    if installed_at:
        return parse_installed_at(installed_at)
    return mtime


def is_stale(baseline_at: datetime | None, *, today: date | None = None) -> bool:
    """Return whether a baseline is older than the 90-day stale threshold."""
    if baseline_at is None:
        return False
    current_day = today or date.today()
    return (current_day - baseline_at.date()).days > STALE_AFTER_DAYS


def triggers_hint(triggers: Iterable[str]) -> str:
    """Return comma-separated first three triggers, or ``-`` when absent."""
    first_three: list[str] = []
    for trigger in triggers:
        clean_trigger = trigger.strip()
        if not clean_trigger:
            continue
        first_three.append(clean_trigger)
        if len(first_three) == 3:
            break
    return ", ".join(first_three) if first_three else "-"


def has_data_source_errors(records: Iterable[SkillRecord]) -> bool:
    """Return whether any record should make CLI exit with code 3."""
    return any(record.data_source_error for record in records)


def exit_code_for_records(records: Iterable[SkillRecord]) -> int:
    """Compute aggregate skill-observability exit code priority."""
    records_list = list(records)
    if has_data_source_errors(records_list):
        return EXIT_DATA_SOURCE_ERROR
    if any(record.status == STATUS_STALE for record in records_list):
        return EXIT_STALE
    if any(record.status == STATUS_UPDATE_AVAILABLE for record in records_list):
        return EXIT_UPDATE_AVAILABLE
    return EXIT_OK


def _find_frontmatter_close(lines: list[str]) -> int | None:
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return index
    return None


def _with_source(message: str, source_path: Path | None) -> str:
    if source_path is None:
        return message
    return f"{message} in {source_path}"


def _parse_indented_list(
    lines: list[str], start_index: int, source_path: Path | None
) -> tuple[tuple[str, ...] | None, int]:
    values: list[str] = []
    index = start_index
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if not raw_line[:1].isspace():
            break
        if not stripped.startswith("- "):
            raise SkillScanError(_with_source(f"unsupported nested value: {stripped}", source_path))
        scalar = _parse_scalar(stripped[2:].strip(), source_path)
        if scalar is not None and scalar:
            values.append(scalar)
        index += 1
    return (tuple(values) if values else None), index


def _parse_block_scalar(
    lines: list[str],
    start_index: int,
    *,
    folded: bool,
) -> tuple[str, int]:
    values: list[str] = []
    index = start_index
    while index < len(lines):
        raw_line = lines[index]
        if raw_line.strip() and not raw_line[:1].isspace():
            break
        values.append(raw_line.strip())
        index += 1
    if folded:
        return " ".join(value for value in values if value).strip(), index
    return "\n".join(values).strip(), index


def _parse_inline_list(value: str, source_path: Path | None) -> list[str]:
    if not value.endswith("]"):
        raise SkillScanError(_with_source(f"unterminated inline list: {value}", source_path))
    body = value[1:-1].strip()
    if not body:
        return []
    items: list[str] = []
    for item in _split_comma_values(body):
        scalar = _parse_scalar(item.strip(), source_path)
        if scalar is not None and scalar:
            items.append(scalar)
    return items


def _parse_scalar(value: str, source_path: Path | None) -> str | None:
    stripped = _strip_inline_comment(value.strip())
    if stripped == "" or stripped in {"~", "null", "Null", "NULL"}:
        return None
    if stripped.startswith(":"):
        raise SkillScanError(_with_source(f"invalid scalar value: {value}", source_path))
    if (
        len(stripped) >= 2
        and stripped[0] == stripped[-1]
        and stripped[0] in {"'", '"'}
    ):
        return stripped[1:-1]
    return stripped


def _split_comma_values(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    for char in value:
        if char in {"'", '"'}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
            current.append(char)
            continue
        if char == "," and quote is None:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return parts


def _strip_inline_comment(value: str) -> str:
    quote: str | None = None
    for index, char in enumerate(value):
        if char in {"'", '"'}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
            continue
        if char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value


def _string_field(
    frontmatter: dict[str, FrontmatterValue],
    key: str,
    errors: list[str],
) -> str | None:
    value = frontmatter.get(key)
    if value is None:
        return None
    if isinstance(value, tuple):
        errors.append(f"{key} must be a string")
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _triggers_field(
    frontmatter: dict[str, FrontmatterValue], errors: list[str]
) -> tuple[str, ...]:
    value = frontmatter.get("triggers")
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(trigger.strip() for trigger in value if trigger.strip())
    if isinstance(value, str):
        return tuple(
            part.strip()
            for part in _split_comma_values(value)
            if part.strip()
        )
    errors.append("triggers must be a string or list")
    return ()
