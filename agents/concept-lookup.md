---
id: concept-lookup
status: optional-template
authoritative: false
runtime_authority: SKILL.md
purpose: Find concepts and relationships relevant to the current question.
---

# Concept Lookup

## Useful when

Existing concepts, notes, or links in the authorized scope could materially
improve the answer.

## Skip when

The term is self-contained, the current context is sufficient, or no relevant
persistent scope is bound.

## Suggested inputs

- the current question and candidate subject;
- authorized concept or wiki scope;
- known aliases, tags, or related terms;
- desired level of recall.

## Useful questions

- Which match is lexical, linked, or semantically inferred?
- What source supports the relationship?
- Is the concept current or superseded?
- Which result would actually change the current task?

## Possible output

Ranked matches with provenance, relationship type, confidence, and relevance.

## Safety

Do not scan unbound directories, treat similarity as proof, or require a
prebuilt index when focused reading is sufficient.
