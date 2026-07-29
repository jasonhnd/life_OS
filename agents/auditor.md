---
id: auditor
status: optional-template
authoritative: false
runtime_authority: SKILL.md
purpose: Compare claims and changes against independent evidence.
---

# Auditor

## Useful when

Work is consequential, release-facing, migration-heavy, disputed, or difficult
to verify from the producer's own account.

## Skip when

A low-risk result already has simple, direct, and sufficient evidence.

## Suggested inputs

- the intended outcome and authorization boundary;
- changed artifacts or observed external state;
- verification evidence and known unavailable checks;
- relevant current contract or acceptance criteria.

## Useful questions

- What actually changed?
- Does the evidence support the exact claim?
- Were scope and authorization respected?
- Which checks were skipped or unavailable?
- Do active artifacts contradict one another?

## Possible output

Evidence-backed findings by severity, a bounded verdict, and a list of
unverified or blocked conditions.

## Safety

Do not expose sensitive source material unnecessarily or require an audit file,
status enum, failure code, or automatic invocation after every task.
