# Comparison Page Spec (v1.8.0 R-1.8.0-013)

> Page taxonomy expansion borrowed from llm_wiki (comparisons).
> Defines `_meta/comparisons/<id>.md` — explicit "X vs Y" decision artifacts.

## Why a separate page type

Comparison decisions ("Mac vs PC", "Tokyo vs Osaka", "Strategy A vs B") have
distinct structure from generic wiki notes:
- Multiple options being compared (≥ 2)
- Explicit criteria
- A decision (or "deferred")
- Reusable when similar comparison comes up later

Splitting them out enables:
- Hippocampus to surface past comparisons when current decision is similar
- Obsidian graph view to color comparison nodes distinctly
- Search "all my comparisons last quarter" trivially via Glob

## File path

```
_meta/comparisons/<id>.md
```

`<id>` = slug from title (lowercase, hyphenated, max 50 chars). Examples:
- `mac-vs-pc-2026-04`
- `freelance-vs-fulltime-2025-q3`
- `tokyo-vs-osaka-relocation`

## Schema

```yaml
---
id: <slug>
type: comparison
title: <one-line, max 80 chars>
options: [<option-A>, <option-B>, <option-C>]
criteria: [<criterion-1>, <criterion-2>, <criterion-3>]
decision: <chosen option or "deferred" or "none">
confidence: <0.0-1.0 float at decision time>
decided_at: <YYYY-MM-DD or null if deferred>
source_session: [[session-id]]                    # session that produced it
revisited: [[session-id-1], [session-id-2]]       # later sessions that referenced this
related: [[[concept-id]], [[wiki-entry]], [[person-id]]]
soul_dimensions_invoked: [<dim-1>, <dim-2>]
domains_consulted: [<finance>, <people>, <governance>]
status: active | superseded | retired
superseded_by: [[comparison-id]] | null
created: <ISO8601>
updated: <ISO8601>
---

# {title}

## Options

### {option-A}
- Pros: ...
- Cons: ...
- Score: <if scored>

### {option-B}
- Pros: ...
- Cons: ...
- Score: <if scored>

(repeat for each option)

## Criteria weights

| Criterion | Weight | A | B | ... |
|-----------|--------|---|---|-----|
| {c1} | <weight> | <score> | <score> | ... |
| ...   | ...      | ...     | ...     | ... |

## Reasoning

<paragraph: how the comparison was reasoned through, what tipped the scale,
which SOUL dimensions activated>

## Decision

**{chosen option}** at confidence {0.0-1.0}, decided <YYYY-MM-DD>.

OR

**Deferred** because <reason>. Re-evaluation trigger: <when to revisit>.

## Outcome (filled in later sessions)

- <YYYY-MM-DD>: <observed result>, see [[session-id]]
- ...

## Related comparisons / patterns

- [[comparison-id-1]] — similar pattern
- [[concept-id]] — underlying concept

## Audit trail

- Source session: [[session-id]]
- AUDITOR: <link to audit log if existed>
- ADVISOR commentary: <if any>
```

## Routing rules (archiver Phase 2)

A session becomes a comparison page if:
- User explicitly framed as "X vs Y" (or "A 还是 B")
- ≥ 2 distinct options weighed against shared criteria
- Decision (even "deferred") was made at session end

NOT a comparison:
- Single-option analysis ("should I do X" with binary yes/no) → wiki entry or
  SessionSummary only
- General research without choice ("what is X?") → wiki entry

## Hebbian linking

When a session activates a comparison page (user references past comparison),
add wikilink in:
- New SessionSummary `concepts_linked` field
- Target comparison's `revisited` list

When comparison is superseded by new comparison, set `status: superseded` +
`superseded_by: [[new-comparison-id]]` to preserve history.

## Outcome tracking

Comparisons differ from concepts by being **temporal**: the decision was
right or wrong as time passes. archiver should append to `## Outcome` section
when later sessions reference back to the decision with new evidence.

## advisor-monthly integration

advisor-monthly scans recent comparisons:
- Decisions made > 90 days ago without `## Outcome` entries → flag in
  review-queue as "outcome unmeasured, did this work?"
- Comparisons with `status: superseded` chains > 2 deep → flag as
  "thrashing, may indicate underlying SOUL conflict"
