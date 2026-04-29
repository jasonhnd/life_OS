# People Page Spec (v1.8.0 R-1.8.0-013)

> Page taxonomy expansion borrowed from llm_wiki (entities → people).
> Defines `_meta/people/<id>.md` — persons relevant to user's decisions.

## Why a separate page type

Persons are first-class entities in life decisions but were previously mixed
into `wiki/`. Splitting them out:
- Clarifies routing for archiver Phase 2 (person → people/, idea → wiki/)
- Enables type affinity scoring in hippocampus 4-signal model
- Gives Obsidian graph view a distinct color for people
- Enforces stricter privacy filter on persons

## File path

```
_meta/people/<id>.md
```

`<id>` = slug from canonical_name (lowercase, hyphenated; SHA-1 hash fallback
for non-ASCII when transliteration unreliable). Same slug rule as concepts.

## Schema

```yaml
---
id: <slug>
canonical_name: <display name>
aliases: [<alt name 1>, <alt name 2>]
type: people
relationship: family | friend | colleague | partner | mentor | client | acquaintance | public-figure | other
first_mentioned: <YYYY-MM-DD of session_id where first appeared>
last_mentioned: <YYYY-MM-DD>
mention_count: <int, total sessions referencing>
concepts_linked: [[[concept-id-1]], [[concept-id-2]]]    # Obsidian wikilinks
soul_dimensions_linked: [<dimension-name>]
privacy_tier: low | medium | high                         # high = redact details
status: active | dormant | archived
created: <ISO8601>
updated: <ISO8601>
---

# {canonical_name}

## Identity
<one paragraph: who, relationship to user, time horizon>

## Notable interactions
- <YYYY-MM-DD>: <one-line>, see [[session-id]]
- ...

## Patterns observed
- <behavioral / collaboration / friction pattern>

## SOUL alignment
- <links to user's SOUL dimensions activated when interacting with this person>

## Open questions / decisions involving this person
- ...
```

## Privacy filter (HARD RULE)

archiver Phase 2 + knowledge-extractor MUST apply BEFORE writing:

1. **Strip exact addresses, phone numbers, financial account numbers, IDs**
   (legal name + city OK; "lives at <street>" NOT OK)
2. **Strip family member full names** unless `relationship: public-figure`
   (use first name + initial: "Jane S.")
3. **Strip date+location combinations** that uniquely identify
4. **Skip if stripping leaves entry meaningless** — privacy beats coverage

`privacy_tier: high` means **redact aggressively** in any future export.

## Routing rules (archiver Phase 2)

Candidate is person if:
- Has personal name (first + last, or single recognized name)
- Referenced as a relationship target (not just "Karpathy says..." citation)
- User has interacted with them (decisions about / with this person)

Candidate is NOT person (route elsewhere):
- Public figure cited only as concept source → mention in concept page,
  not own people page
- Group / organization → `_meta/people/<org-id>.md` with
  `relationship: organization` (or future `_meta/orgs/` if pattern emerges)
- Fictional / hypothetical → don't write at all

## Hebbian linking

When a session activates a person, add wikilinks `[[person-id]]` in:
- SessionSummary `concepts_linked` field (treats people as concepts for graph)
- Related concept pages' `outgoing_edges` if the person is closely linked to a concept

People pages participate in 4-signal relevance per `references/hippocampus-spec.md`.

## Migration from wiki/

Existing wiki/ entries that are about persons (judged by LLM during next
maintenance run via `scripts/prompts/migrate-to-wikilinks.md`) are migrated
to `_meta/people/`. Old wiki path becomes a redirect stub or is deleted.

## Status lifecycle

- `active` — referenced in last 90 days
- `dormant` — not referenced 90-365 days
- `archived` — not referenced > 365 days; pages stay (decisions reference them)

advisor-monthly may auto-flip status based on `last_mentioned` age.
