---
method_id: example-method-id
canonical_name: "Example Method Name"
domain: method
status: tentative
use_count: 1
last_used: 2026-04-21T14:30:00
created: 2026-04-21T14:30:00
applicable_to:
  - "decision-type-1"
  - "project-type-2"
related_concepts:
  - concept-id-1
  - concept-id-2
---

# Example Method Name

## When to use

One paragraph: what kind of decision / situation calls for this method?

## Steps

1. **Step 1 name** — what to do, how to know it's done
2. **Step 2 name** — ...
3. **Step 3 name** — ...

## Inputs needed

- Data: {what info you need before starting}
- Context: {what context the method assumes}
- Time: {rough budget}

## Outputs produced

- Decision: {what kind of decision the method produces}
- Artifact: {what gets written to second-brain — wiki entry / strategic line update / etc.}

## When NOT to use

- Anti-pattern 1: {situation where this method fails}
- Anti-pattern 2: ...

## Examples from past sessions

- {session_id} — {one-line outcome of applying this method}

## Notes

Free-form notes.

---

**Template usage**: copy to `_meta/methods/{domain}/{your-method-id}.md`, fill in real values. Method library is the procedural-memory layer (vs concepts = entity-memory, SOUL = identity-memory).

Path conventions per `references/method-library-spec.md`:
- `method_id`: lowercase, hyphenated, unique
- `domain`: one of method / finance / etc. (mirrors concept domains)
- `status`: tentative → confirmed → canonical
- `use_count`: increments each time the method is applied
