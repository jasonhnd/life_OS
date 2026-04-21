"""Concept-graph helpers — read concept files, compile INDEX, Hebbian update.

Used by:
- archiver Phase 2 (Hebbian co-activation, concept extraction)
- retrospective Mode 0 (compile _meta/concepts/INDEX.md)
- concept-lookup subagent (read INDEX, scan candidates)
- tools/rebuild_concept_index.py CLI

Per references/concept-spec.md.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tools.lib.second_brain import (
    Concept,
    ConceptEdge,
    ConceptProvenance,
    ParsedMarkdown,
    dump_frontmatter,
    load_markdown,
)

__all__ = [
    "concept_to_markdown",
    "write_concept",
    "read_concept",
    "compile_concept_index_line",
    "compile_concept_index",
    "rebuild_concept_index",
    "compile_synapses_index",
    "hebbian_update",
]


# ─── Concept IO ──────────────────────────────────────────────────────────────


def _concept_to_frontmatter(c: Concept) -> dict:
    """Convert Concept dataclass to YAML-serialisable frontmatter dict."""
    fm: dict = {
        "concept_id": c.concept_id,
        "canonical_name": c.canonical_name,
        "domain": c.domain,
        "status": c.status,
        "permanence": c.permanence,
        "activation_count": c.activation_count,
        "last_activated": c.last_activated.isoformat(),
        "created": c.created.isoformat(),
    }
    if c.aliases:
        fm["aliases"] = c.aliases
    if c.outgoing_edges:
        fm["outgoing_edges"] = [
            {
                "target": e.target,
                "weight": e.weight,
                **(
                    {"last_co_activated": e.last_co_activated.isoformat()}
                    if e.last_co_activated
                    else {}
                ),
                **({"relation": e.relation} if e.relation else {}),
            }
            for e in c.outgoing_edges
        ]
    if c.provenance.source_sessions or c.provenance.discovered_at:
        prov: dict = {}
        if c.provenance.source_sessions:
            prov["source_sessions"] = c.provenance.source_sessions
        if c.provenance.discovered_at:
            prov["discovered_at"] = c.provenance.discovered_at.isoformat()
        fm["provenance"] = prov
    return fm


def concept_to_markdown(c: Concept) -> str:
    """Serialise Concept to markdown (frontmatter + body)."""
    return dump_frontmatter(_concept_to_frontmatter(c), c.body)


def write_concept(c: Concept, concepts_root: Path) -> Path:
    """Write Concept to ``<concepts_root>/{domain}/{concept_id}.md``.

    Creates domain directory if missing. Overwrites existing file (concepts
    are mutable — Hebbian updates change activation_count, last_activated,
    edge weights).
    """
    domain_dir = concepts_root / c.domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    target = domain_dir / f"{c.concept_id}.md"
    target.write_text(concept_to_markdown(c), encoding="utf-8")
    return target


def read_concept(concept_path: Path) -> Concept | None:
    """Parse a concept file into Concept dataclass. Returns None on error."""
    try:
        parsed = load_markdown(concept_path)
    except (ValueError, OSError):
        return None
    fm = parsed.frontmatter
    try:
        edges_raw = fm.get("outgoing_edges") or []
        edges = [
            ConceptEdge(
                target=e["target"],
                weight=int(e["weight"]),
                last_co_activated=(
                    datetime.fromisoformat(e["last_co_activated"])
                    if e.get("last_co_activated")
                    else None
                ),
                relation=e.get("relation"),
            )
            for e in edges_raw
        ]
        prov_raw = fm.get("provenance") or {}
        prov = ConceptProvenance(
            source_sessions=prov_raw.get("source_sessions") or [],
            discovered_at=(
                datetime.fromisoformat(prov_raw["discovered_at"])
                if prov_raw.get("discovered_at")
                else None
            ),
        )
        last_activated = fm["last_activated"]
        if isinstance(last_activated, str):
            last_activated = datetime.fromisoformat(last_activated)
        created = fm["created"]
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        return Concept(
            concept_id=fm["concept_id"],
            canonical_name=fm["canonical_name"],
            domain=fm["domain"],
            status=fm["status"],
            permanence=fm["permanence"],
            activation_count=int(fm["activation_count"]),
            last_activated=last_activated,
            created=created,
            body=parsed.body,
            aliases=fm.get("aliases") or [],
            outgoing_edges=edges,
            provenance=prov,
        )
    except (KeyError, TypeError, ValueError):
        return None


# ─── INDEX.md compilation ────────────────────────────────────────────────────


def compile_concept_index_line(c: Concept) -> str:
    """Format one INDEX.md line for a concept.

    Format: ``{concept_id} | {canonical_name} | {domain} | {status} | {permanence} | {activation_count} | {last_activated}``
    """
    last_activated_str = c.last_activated.date().isoformat()
    return (
        f"{c.concept_id} | {c.canonical_name} | {c.domain} | "
        f"{c.status} | {c.permanence} | {c.activation_count} | {last_activated_str}"
    )


def compile_concept_index(concepts_root: Path) -> str:
    """Scan all concept files under ``concepts_root/{domain}/*.md``, return INDEX.md content.

    Excludes INDEX.md, SYNAPSES-INDEX.md, _tentative/, _archive/.
    Sorted by activation_count desc, then last_activated desc.
    Grouped by domain.
    """
    if not concepts_root.exists():
        return _empty_concept_index()

    concepts: list[Concept] = []
    for path in sorted(concepts_root.rglob("*.md")):
        # Skip reserved paths
        if path.name in ("INDEX.md", "SYNAPSES-INDEX.md"):
            continue
        if "_tentative" in path.parts or "_archive" in path.parts:
            continue
        c = read_concept(path)
        if c is not None:
            concepts.append(c)

    if not concepts:
        return _empty_concept_index()

    # Sort by activation_count desc, then last_activated desc
    concepts.sort(
        key=lambda c: (c.activation_count, c.last_activated),
        reverse=True,
    )

    # Group by domain (alphabetical for stable output)
    by_domain: dict[str, list[Concept]] = {}
    for c in concepts:
        by_domain.setdefault(c.domain, []).append(c)

    out_lines = ["# Concept Index", ""]
    for domain in sorted(by_domain.keys()):
        out_lines.append(f"## {domain}")
        out_lines.append("")
        for c in by_domain[domain]:
            out_lines.append(compile_concept_index_line(c))
        out_lines.append("")

    return "\n".join(out_lines).rstrip() + "\n"


def _empty_concept_index() -> str:
    """Minimal INDEX.md content for an empty / first-concept state."""
    return "# Concept Index\n\n_(no concepts yet)_\n"


def rebuild_concept_index(second_brain_root: Path) -> tuple[Path, int]:
    """Recompile INDEX.md from all concept files.

    Returns ``(path_written, concept_count)``.
    """
    concepts_root = second_brain_root / "_meta" / "concepts"
    content = compile_concept_index(concepts_root)
    concepts_root.mkdir(parents=True, exist_ok=True)
    target = concepts_root / "INDEX.md"
    tmp = target.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)
    line_count = sum(
        1 for line in content.splitlines() if " | " in line and not line.startswith("#")
    )
    return target, line_count


# ─── SYNAPSES-INDEX.md compilation (reverse edge index) ─────────────────────


def compile_synapses_index(concepts_root: Path) -> str:
    """Compile reverse-edge index from all concept outgoing_edges.

    For each concept C with outgoing edge to T (weight W), emit:
        T | C | W | last_co_activated

    Used by hippocampus Wave 2/3 to look up "what concepts point to me".
    """
    if not concepts_root.exists():
        return "# Synapses Index\n\n_(no concepts yet)_\n"

    edges: list[tuple[str, str, int, str]] = []  # (target, source, weight, last_str)
    for path in sorted(concepts_root.rglob("*.md")):
        if path.name in ("INDEX.md", "SYNAPSES-INDEX.md"):
            continue
        if "_tentative" in path.parts or "_archive" in path.parts:
            continue
        c = read_concept(path)
        if c is None:
            continue
        for edge in c.outgoing_edges:
            last_str = (
                edge.last_co_activated.date().isoformat()
                if edge.last_co_activated
                else "n/a"
            )
            edges.append((edge.target, c.concept_id, edge.weight, last_str))

    if not edges:
        return "# Synapses Index\n\n_(no synapse edges yet)_\n"

    # Group by target, sort by weight desc within group
    by_target: dict[str, list[tuple[str, int, str]]] = {}
    for target, source, weight, last_str in edges:
        by_target.setdefault(target, []).append((source, weight, last_str))
    for target in by_target:
        by_target[target].sort(key=lambda x: x[1], reverse=True)

    out_lines = [
        "# Synapses Index",
        "",
        "_Reverse edge index: for each target concept, list all sources pointing to it._",
        "",
    ]
    for target in sorted(by_target.keys()):
        out_lines.append(f"## {target}")
        out_lines.append("")
        for source, weight, last_str in by_target[target]:
            out_lines.append(f"{source} | weight={weight} | last_co={last_str}")
        out_lines.append("")

    return "\n".join(out_lines).rstrip() + "\n"


# ─── Hebbian update ─────────────────────────────────────────────────────────


def hebbian_update(
    concepts: list[Concept],
    co_activated_pairs: list[tuple[str, str]],
    now: datetime | None = None,
) -> list[Concept]:
    """Apply Hebbian +1 increment for each co-activated pair.

    Per concept-spec.md: "co-activation increases edge weight by +1 (Hebbian
    rule); long unused edges decay" (decay handled separately).

    Args:
        concepts: list of Concept objects (mutated in place; also returned)
        co_activated_pairs: list of (source_concept_id, target_concept_id)
        now: timestamp to set on edge.last_co_activated (defaults to now)

    Returns the (possibly mutated) concepts list.
    """
    now = now or datetime.now()
    by_id = {c.concept_id: c for c in concepts}

    for source_id, target_id in co_activated_pairs:
        source = by_id.get(source_id)
        if source is None:
            continue
        # Find existing edge or create new
        existing = next(
            (e for e in source.outgoing_edges if e.target == target_id), None
        )
        if existing is not None:
            existing.weight += 1
            existing.last_co_activated = now
        else:
            source.outgoing_edges.append(
                ConceptEdge(target=target_id, weight=1, last_co_activated=now)
            )
        # Increment activation_count + last_activated on source
        source.activation_count += 1
        source.last_activated = now

    return concepts
