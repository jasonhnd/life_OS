"""Life OS · wiki_decay (v1.8.0).

Monthly cron: scan wiki/ for stale entries (low confidence + long no-update).
Generate review list; do NOT delete (user reviews via /monitor).

Run via:
    python -m tools.wiki_decay --root .

Output: _meta/eval-history/wiki-decay-{YYYY-MM-DD}.md
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

CONFIDENCE_RE = re.compile(r"^confidence:\s*([0-9]*\.?[0-9]+)\s*$", re.MULTILINE)
LAST_UPDATED_RE = re.compile(r"^last_updated:\s*(\S+)\s*$", re.MULTILINE)
TAGS_RE = re.compile(r"^tags:\s*\[(.*?)\]\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)


@dataclass
class WikiEntry:
    path: Path
    title: str
    confidence: float
    last_updated: datetime | None
    days_since_update: int | None
    tags: list[str]


def parse_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end < 0:
        return "", text
    return text[4:end], text[end + 5 :]


def parse_entry(path: Path) -> WikiEntry | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    fm, _body = parse_frontmatter(text)
    if not fm:
        return None

    conf_m = CONFIDENCE_RE.search(fm)
    confidence = float(conf_m.group(1)) if conf_m else 1.0

    upd_m = LAST_UPDATED_RE.search(fm)
    last_updated: datetime | None = None
    days_since: int | None = None
    if upd_m:
        try:
            ts_str = upd_m.group(1).strip().strip('"').strip("'")
            last_updated = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if last_updated.tzinfo is None:
                last_updated = last_updated.replace(tzinfo=timezone.utc)
            days_since = (datetime.now(tz=timezone.utc) - last_updated).days
        except (ValueError, AttributeError):
            pass

    tags_m = TAGS_RE.search(fm)
    tags: list[str] = []
    if tags_m:
        tags = [
            t.strip().strip('"').strip("'") for t in tags_m.group(1).split(",") if t.strip()
        ]

    title_m = TITLE_RE.search(fm)
    title = title_m.group(1).strip().strip('"').strip("'") if title_m else path.stem

    return WikiEntry(
        path=path,
        title=title,
        confidence=confidence,
        last_updated=last_updated,
        days_since_update=days_since,
        tags=tags,
    )


def scan_wiki(root: Path) -> list[WikiEntry]:
    wiki_dir = root / "wiki"
    if not wiki_dir.is_dir():
        return []
    entries: list[WikiEntry] = []
    for md in wiki_dir.rglob("*.md"):
        e = parse_entry(md)
        if e is not None:
            entries.append(e)
    return entries


def classify(
    entries: list[WikiEntry], confidence_threshold: float, days_threshold: int
) -> dict[str, list[WikiEntry]]:
    stale: list[WikiEntry] = []
    borderline: list[WikiEntry] = []
    fresh: list[WikiEntry] = []
    for e in entries:
        if e.days_since_update is None:
            borderline.append(e)
            continue
        old = e.days_since_update >= days_threshold
        low_conf = e.confidence < confidence_threshold
        if old and low_conf:
            stale.append(e)
        elif old or low_conf:
            borderline.append(e)
        else:
            fresh.append(e)
    return {"stale": stale, "borderline": borderline, "fresh": fresh}


def render_report(
    classified: dict[str, list[WikiEntry]],
    root: Path,
    out_path: Path,
    confidence_threshold: float,
    days_threshold: int,
) -> None:
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = []
    lines.append(f"# Wiki Decay Report · {today}")
    lines.append("")
    lines.append(
        f"Criteria: stale = confidence < {confidence_threshold} AND no update "
        f"in {days_threshold}+ days"
    )
    lines.append("")
    stale = classified["stale"]
    borderline = classified["borderline"]
    fresh = classified["fresh"]
    lines.append(
        f"- Total wiki entries: {len(stale) + len(borderline) + len(fresh)}"
    )
    lines.append(f"- Stale: {len(stale)} (review recommended)")
    lines.append(f"- Borderline: {len(borderline)} (one criterion only)")
    lines.append(f"- Fresh: {len(fresh)}")
    lines.append("")
    lines.append("## Stale entries (action items)")
    lines.append("")
    if not stale:
        lines.append("_None._")
    else:
        lines.append("| Entry | Confidence | Days since update | Tags |")
        lines.append("|-------|-----------|-------------------|------|")
        for e in sorted(stale, key=lambda x: (x.confidence, -(x.days_since_update or 0))):
            rel = e.path.relative_to(root)
            tags_str = ", ".join(e.tags[:3]) if e.tags else ""
            lines.append(
                f"| `{rel}` | {e.confidence:.2f} | {e.days_since_update} | {tags_str} |"
            )
    lines.append("")
    lines.append("## Borderline entries (top 20)")
    lines.append("")
    if not borderline:
        lines.append("_None._")
    else:
        for e in sorted(
            borderline, key=lambda x: (x.confidence, -(x.days_since_update or 0))
        )[:20]:
            rel = e.path.relative_to(root)
            d = e.days_since_update if e.days_since_update is not None else "?"
            lines.append(f"- `{rel}` (confidence={e.confidence:.2f}, days={d})")
    lines.append("")
    lines.append("## Recommended actions")
    lines.append("")
    lines.append("In Claude Code monitor session, run `/monitor` then say:")
    lines.append("  - 'show stale wiki entries' to walk through them")
    lines.append("  - For each: keep / delete / refresh confidence")
    lines.append("")
    lines.append(
        "This report does NOT delete files. All deletions/edits go through "
        "user review in the monitor session."
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Life OS wiki decay scanner")
    parser.add_argument("--root", default=".", help="Repo root")
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.3,
        help="Stale if confidence below this",
    )
    parser.add_argument(
        "--days-threshold",
        type=int,
        default=90,
        help="Stale if no update in this many days",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file (default: _meta/eval-history/wiki-decay-{date}.md)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "SKILL.md").is_file():
        print(
            f"Error: {root} does not look like a Life OS root (no SKILL.md)",
            file=sys.stderr,
        )
        return 2

    entries = scan_wiki(root)
    classified = classify(entries, args.confidence_threshold, args.days_threshold)

    if args.output:
        out = Path(args.output)
    else:
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        out = root / "_meta" / "eval-history" / f"wiki-decay-{today}.md"

    render_report(
        classified, root, out, args.confidence_threshold, args.days_threshold
    )

    stale_n = len(classified["stale"])
    border_n = len(classified["borderline"])
    print(f"Wiki decay scan: {stale_n} stale, {border_n} borderline")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
