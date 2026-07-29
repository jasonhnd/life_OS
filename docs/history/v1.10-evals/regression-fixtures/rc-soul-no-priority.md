---
# Original v1.8.5 .yml content preserved as YAML frontmatter (v1.8.6 'md-only' rule)
# Schema unchanged; only file extension changed.
---

# Regression Fixture (md format · v1.8.6+)

```yaml
id: rc-soul-no-priority
description: |
  Negative fixture: SOUL.md dim missing required `priority` field.
  AUDITOR Mode 4 C2 check MUST FAIL on this. If C2 reports PASS, validator
  has regressed and this regression case has caught it.
expected_verdict: FAIL
expected_failure_class: F3_SCHEMA_FAILURE
expected_check: C2 (Priority total order {1..N} no gaps no ties)
introduced_in: v1.8.5 Stage 4
related_spec: references/soul-spec.md v2 §"Required Schema Constraints §2"

input_soul_md: |
  soul_reference_set:
    aspirational: []
    anti_reference: []
    boundary_case: []
    mainstream_baseline: []
    outlier: []

  ---
  - id: dv-truth-over-comfort
    formulation: "Truth over comfort"
    priority: 1
    canonical_or_personal: canonical
    lifecycle_stage: confirmed
    inclusion_test:
      failure_prevented: "prevents self-deception in important decisions"
    confidence: 0.85
    evidence_count: 8
    challenges: 1

  - id: dv-long-term-over-short-term
    formulation: "Long-term flourishing over short-term comfort"
    # MISSING priority field — this is the regression bait
    canonical_or_personal: canonical
    lifecycle_stage: confirmed
    inclusion_test:
      failure_prevented: "prevents impulsive choices"
    confidence: 0.7
    evidence_count: 5
    challenges: 0

  - id: dv-clarity-over-cleverness
    formulation: "Clarity over cleverness"
    priority: 3
    canonical_or_personal: canonical
    lifecycle_stage: confirmed
    inclusion_test:
      failure_prevented: "prevents over-engineering"
    confidence: 0.6
    evidence_count: 4
    challenges: 1
  ---

expected_finding: |
  F3 SCHEMA_FAILURE: dim 'dv-long-term-over-short-term' missing priority field

```