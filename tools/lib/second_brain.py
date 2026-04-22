"""Life OS second-brain data model — v1.7 Phase 1.

Pure dataclass representations of every type stored in the user's
second-brain markdown files. Each type maps to a file format defined in
``references/data-model.md`` and ``references/adapter-github.md``.

Frontmatter parsing uses pyyaml. All file IO uses pathlib.

Type catalogue (existing + v1.7 new):

Existing (since v1.0):
    - WikiNote          — wiki/{domain}/{slug}.md

v1.7 new (Cortex layer):
    - SessionSummary    — _meta/sessions/{session_id}.md
    - Concept           — _meta/concepts/{domain}/{concept_id}.md
    - SoulSnapshot      — _meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md
    - EvalEntry         — _meta/eval-history/{YYYY-MM-DD}-{project}.md
    - Method            — _meta/methods/{domain}/{method_id}.md

Authoritative specs:
    - references/session-index-spec.md
    - references/concept-spec.md
    - references/snapshot-spec.md
    - references/eval-history-spec.md
    - references/method-library-spec.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, ClassVar

import yaml  # type: ignore[import-untyped]

# ─── Frontmatter parsing ────────────────────────────────────────────────────


@dataclass
class ParsedMarkdown:
    """Result of parsing a markdown file with optional YAML frontmatter."""

    frontmatter: dict[str, Any]
    body: str
    source_path: Path | None = None

    @property
    def has_frontmatter(self) -> bool:
        return bool(self.frontmatter)


def parse_frontmatter(content: str, source_path: Path | None = None) -> ParsedMarkdown:
    """Parse a markdown string into frontmatter dict + body string.

    Frontmatter must be delimited by ``---`` lines at the very top of the file.
    If no frontmatter is present, returns an empty dict and the full content as body.
    """
    if not content.startswith("---\n"):
        return ParsedMarkdown(frontmatter={}, body=content, source_path=source_path)

    # Find the closing ---
    end_marker = content.find("\n---\n", 4)
    if end_marker == -1:
        # Malformed — no closing marker. Treat as no frontmatter.
        return ParsedMarkdown(frontmatter={}, body=content, source_path=source_path)

    fm_text = content[4:end_marker]
    body = content[end_marker + 5 :]

    try:
        fm_dict = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Invalid YAML frontmatter in {source_path or '<string>'}: {exc}"
        ) from exc

    if not isinstance(fm_dict, dict):
        raise ValueError(
            f"Frontmatter must be a dict, got {type(fm_dict).__name__} "
            f"in {source_path or '<string>'}"
        )

    return ParsedMarkdown(frontmatter=fm_dict, body=body, source_path=source_path)


def dump_frontmatter(frontmatter: dict[str, Any], body: str) -> str:
    """Serialise a dict + body back to markdown-with-frontmatter format."""
    fm_text = yaml.safe_dump(
        frontmatter,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    return f"---\n{fm_text}---\n{body}"


def load_markdown(path: Path) -> ParsedMarkdown:
    """Read and parse a markdown file from disk."""
    content = path.read_text(encoding="utf-8")
    return parse_frontmatter(content, source_path=path)


# ─── Common dataclass base ───────────────────────────────────────────────────


@dataclass
class SecondBrainEntity:
    """Base class for every type stored as one markdown file in the second-brain."""

    # Subclasses set this — used by file-path conventions.
    _path_template: ClassVar[str] = ""

    @classmethod
    def from_markdown(cls, parsed: ParsedMarkdown) -> SecondBrainEntity:
        """Construct from a ParsedMarkdown. Subclasses override."""
        raise NotImplementedError

    def to_markdown(self) -> str:
        """Serialise to markdown-with-frontmatter format. Subclasses override."""
        raise NotImplementedError


# ─── Existing v1.x types ─────────────────────────────────────────────────────


@dataclass
class WikiNote(SecondBrainEntity):
    """A wiki entry — reusable, world-facing knowledge.

    File: ``wiki/{domain}/{slug}.md``
    Spec: ``references/wiki-spec.md``
    """

    slug: str
    domain: str
    title: str
    confidence: float
    evidence_count: int
    challenges: int
    created: datetime
    last_updated: datetime
    body: str
    aliases: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    _path_template: ClassVar[str] = "wiki/{domain}/{slug}.md"


# ─── v1.7 Cortex types ──────────────────────────────────────────────────────


@dataclass
class ActionItem:
    """One action item embedded in a SessionSummary."""

    text: str
    deadline: date | None = None
    status: str = "pending"  # pending | completed | dropped


@dataclass
class SessionSummary(SecondBrainEntity):
    """One file per completed session.

    Written by archiver Phase 1. Immutable after write.
    File: ``_meta/sessions/{session_id}.md``
    Spec: ``references/session-index-spec.md`` §3.
    """

    session_id: str
    date: date
    started_at: datetime
    ended_at: datetime
    duration_minutes: int
    platform: str  # claude | gemini | codex
    theme: str  # en-roman | zh-classical | ja-kasumigaseki | ...
    project: str
    workflow: str  # full_deliberation | express_analysis | direct_handle | strategist | review
    subject: str
    overall_score: float
    veto_count: int
    council_triggered: bool
    compliance_violations: int
    body: str
    domains_activated: list[str] = field(default_factory=list)
    domain_scores: dict[str, float] = field(default_factory=dict)
    soul_dimensions_touched: list[str] = field(default_factory=list)
    wiki_written: list[str] = field(default_factory=list)
    methods_used: list[str] = field(default_factory=list)
    methods_discovered: list[str] = field(default_factory=list)
    concepts_activated: list[str] = field(default_factory=list)
    concepts_discovered: list[str] = field(default_factory=list)
    dream_triggers: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)

    _path_template: ClassVar[str] = "_meta/sessions/{session_id}.md"


@dataclass
class ConceptEdge:
    """One outgoing synapse edge from a concept to another concept."""

    target: str  # target concept_id
    weight: int  # synapse weight (Hebbian-updated)
    last_co_activated: datetime | None = None
    relation: str | None = None  # optional human-readable label


@dataclass
class ConceptProvenance:
    """Where a concept was activated or discovered."""

    source_sessions: list[str] = field(default_factory=list)
    discovered_at: datetime | None = None


@dataclass
class Concept(SecondBrainEntity):
    """One node in the synaptic concept graph.

    File: ``_meta/concepts/{domain}/{concept_id}.md``
    Spec: ``references/concept-spec.md``
    """

    concept_id: str  # unique across network
    canonical_name: str
    domain: str
    status: str  # tentative | confirmed | canonical
    permanence: str  # identity | skill | fact | transient
    activation_count: int
    last_activated: datetime
    created: datetime
    body: str
    aliases: list[str] = field(default_factory=list)
    outgoing_edges: list[ConceptEdge] = field(default_factory=list)
    provenance: ConceptProvenance = field(default_factory=ConceptProvenance)

    _path_template: ClassVar[str] = "_meta/concepts/{domain}/{concept_id}.md"


@dataclass
class SnapshotDimension:
    """One SOUL dimension captured in a snapshot."""

    name: str
    confidence: float
    evidence_count: int
    challenges: int
    tier: str  # core | secondary | emerging (dormant excluded)

    @classmethod
    def derive_tier(cls, confidence: float) -> str:
        """Map confidence to tier per snapshot-spec.md Tier Mapping."""
        if confidence >= 0.7:
            return "core"
        if confidence >= 0.3:
            return "secondary"
        if confidence >= 0.2:
            return "emerging"
        return "dormant"  # excluded from snapshots


@dataclass
class SoulSnapshot(SecondBrainEntity):
    """Immutable metadata dump of SOUL state at session close.

    File: ``_meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md``
    Spec: ``references/snapshot-spec.md``
    """

    snapshot_id: str  # matches filename stem (YYYY-MM-DD-HHMM)
    captured_at: datetime
    session_id: str
    previous_snapshot: str | None
    dimensions: list[SnapshotDimension] = field(default_factory=list)

    _path_template: ClassVar[str] = "_meta/snapshots/soul/{snapshot_id}.md"

    def __post_init__(self) -> None:
        # Enforce snapshot-spec invariant: only confidence > 0.2 included
        self.dimensions = [d for d in self.dimensions if d.confidence > 0.2]


@dataclass
class EvalEntry(SecondBrainEntity):
    """One eval-history record, per session per project.

    File: ``_meta/eval-history/{YYYY-MM-DD}-{project}.md``
    Spec: ``references/eval-history-spec.md``
    """

    date: date
    project: str
    session_id: str
    overall_score: float
    body: str
    metrics: dict[str, float] = field(default_factory=dict)

    _path_template: ClassVar[str] = "_meta/eval-history/{date}-{project}.md"


@dataclass
class Method(SecondBrainEntity):
    """One reusable method/workflow in the procedural memory layer.

    File: ``_meta/methods/{domain}/{method_id}.md``
    Spec: ``references/method-library-spec.md``
    """

    method_id: str
    canonical_name: str
    domain: str
    status: str  # tentative | confirmed | canonical
    use_count: int
    last_used: datetime
    created: datetime
    body: str
    applicable_to: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)

    _path_template: ClassVar[str] = "_meta/methods/{domain}/{method_id}.md"


# ─── Path helpers ────────────────────────────────────────────────────────────


def resolve_path(entity: SecondBrainEntity, second_brain_root: Path) -> Path:
    """Resolve the on-disk path for an entity, given the second-brain root.

    Uses ``entity._path_template`` formatted with the entity's dataclass fields.
    """
    template = entity._path_template
    if not template:
        raise ValueError(f"No _path_template defined for {type(entity).__name__}")

    # Build a dict of all dataclass field values (handle date/str distinction)
    values: dict[str, Any] = {}
    for fname in entity.__dataclass_fields__:
        if fname.startswith("_"):
            continue
        val = getattr(entity, fname)
        if isinstance(val, date) and not isinstance(val, datetime):
            values[fname] = val.isoformat()
        else:
            values[fname] = val

    relative = template.format(**values)
    return second_brain_root / relative
