---
concept_id: example-concept-id
canonical_name: "Example Concept Name"
domain: startup
status: tentative
permanence: fact
activation_count: 1
last_activated: 2026-04-21T14:30:00
created: 2026-04-21T14:30:00
aliases:
  - "Alternate Name 1"
  - "Alternate Name 2"
outgoing_edges:
  - target: another-concept-id
    weight: 1
    last_co_activated: 2026-04-21T14:30:00
    relation: "implies"
provenance:
  source_sessions:
    - claude-20260421-1430
  discovered_at: 2026-04-21T14:30:00
---

# Example Concept Name

## Definition

One paragraph defining what this concept is. Aim for clarity over completeness — enough that a future hippocampus retrieval can match it semantically.

## Why it matters

One paragraph on why this concept earned a spot in the graph. Examples: "appears in 5+ decisions on financial planning", "synonym for X across multiple sessions", "user-defined invariant for project Y".

## Cross-references

- Related concepts (informal — formal links live in YAML `outgoing_edges` above):
  - {concept-id-1} — relationship description
  - {concept-id-2} — relationship description

## Notes

Free-form notes that won't fit elsewhere. The hippocampus retrieves by INDEX line + frontmatter, not body text — but the body is what the user sees when the concept is referenced.

---

**Template usage**: copy this file to `_meta/concepts/{domain}/{your-concept-id}.md`, fill in real values, then run `life-os-tool rebuild-concept-index --root <your-second-brain>`.

Path conventions per `references/concept-spec.md`:
- `concept_id`: lowercase, hyphenated, unique across the network
- `domain`: one of finance / startup / personal / technical / method / relationship / health / legal (or new domain dir)
- `status`: tentative → confirmed → canonical (one-directional under normal use)
- `permanence`: identity / skill / fact / transient (decay curve depends on this)
