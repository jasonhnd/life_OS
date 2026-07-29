---
# Original v1.8.5 .yml content preserved as YAML frontmatter (v1.8.6 'md-only' rule)
# Schema unchanged; only file extension changed.
---

# Regression Fixture (md format · v1.8.6+)

```yaml
id: rc-soul-no-outlier
description: |
  Negative fixture: SOUL.md soul_reference_set missing `outlier` key.
  AUDITOR Mode 4 C5 check MUST FAIL on this. If C5 reports PASS, validator
  has regressed.
expected_verdict: FAIL
expected_failure_class: F3_SCHEMA_FAILURE
expected_check: C5 (reference_set 5 role slots present)
introduced_in: v1.8.5 Stage 4
related_spec: references/soul-spec.md v2 §"Required Schema Constraints §5"

input_soul_md: |
  soul_reference_set:
    aspirational: ["alice author of X"]
    anti_reference: ["bob influencer of Y"]
    boundary_case: ["case Z"]
    mainstream_baseline: ["typical tech worker"]
    # MISSING outlier key — this is the regression bait

  ---
  - id: dv-truth-over-comfort
    formulation: "Truth over comfort"
    priority: 1
    canonical_or_personal: canonical
    lifecycle_stage: confirmed
    inclusion_test:
      failure_prevented: "prevents self-deception"
    confidence: 0.8
    evidence_count: 6
    challenges: 0

  - id: dv-clarity-over-cleverness
    formulation: "Clarity over cleverness"
    priority: 2
    canonical_or_personal: canonical
    lifecycle_stage: confirmed
    inclusion_test:
      failure_prevented: "prevents over-engineering"
    confidence: 0.7
    evidence_count: 5
    challenges: 1

  - id: dv-action-over-perfection
    formulation: "Action over perfection"
    priority: 3
    canonical_or_personal: personal
    lifecycle_stage: confirmed
    inclusion_test:
      failure_prevented: "prevents analysis paralysis"
    confidence: 0.65
    evidence_count: 4
    challenges: 1
  ---

expected_finding: |
  F3 SCHEMA_FAILURE: soul_reference_set missing key 'outlier'

```