---
title: Outcome and Failure Vocabulary
status: reference
authoritative: false
runtime_authority: SKILL.md
introduced_in: v1.11.0
---

# Outcome and Failure Vocabulary

Use plain descriptions that help the user understand what happened.

| State | Meaning |
|---|---|
| `completed` | The requested outcome was achieved and supported by relevant evidence |
| `partially completed` | Some in-scope work succeeded and the remainder is identified |
| `not verified` | Work may exist, but evidence is insufficient for the claim |
| `blocked` | A concrete dependency, permission, decision, or unavailable capability prevents progress |
| `declined` | The requested action cannot be performed within applicable safety or policy boundaries |
| `not attempted` | The action was outside scope or intentionally left for the user |

A host capability being unavailable is not automatically a product failure.
State what capability was missing, what fallback was used, and which result
remains unavailable.

Do not turn these labels into mandatory status-line syntax. Specific evidence
is more useful than a ceremonial verdict.
