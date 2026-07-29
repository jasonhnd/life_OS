---
# Original v1.8.5 .yml content preserved as YAML frontmatter (v1.8.6 'md-only' rule)
# Schema unchanged; only file extension changed.
---

# Regression Fixture (md format · v1.8.6+)

```yaml
id: rc-wiki-no-outlier
description: |
  Negative fixture: wiki entry at lifecycle_stage:active has empty `outlier`
  list in reference_set. AUDITOR Mode 5 W2 check MUST FAIL on this. If W2
  reports PASS, validator has regressed and an active entry without
  anti-confirmation-bias defense has slipped through.
expected_verdict: FAIL
expected_failure_class: F11_LIFECYCLE_FAILURE
expected_check: W2 (outlier non-empty for active+ entries)
introduced_in: v1.8.5 Stage 5
related_spec: references/wiki-spec.md v2 §"v2 HARD Schema Constraints §2"

input_wiki_entry:
  path: wiki/wn-example-no-outlier.md
  content: |
    ---
    id: wn-example-no-outlier
    name: "Example knowledge entry"
    version: "0.1.0"
    classification:
      function: validate
      target_object: "Japanese NPO lending regulations"
      automation_mode: human_executed
      authority_level: suggest_only
      risk_level: medium
      lifecycle_stage: active        # active but outlier empty — regression bait
    operating_hypothesis: |
      Given a Japanese NPO considering a lending product, this entry warns
      that the Money Lending Business Act has no NPO exemption, within risk of regulatory penalty.
    context_manifest:
      source_of_truth: ["e-gov Money Lending Business Act article 2"]
      supporting: []
      forbidden: []
    reference_set:
      aspirational: []
      anti_reference: []
      boundary_case: []
      mainstream_baseline: []
      outlier: []                    # EMPTY for active entry — regression bait
    failure_modes:
      known: []
      warning_signs: []
      repair_actions: []
    arguments_against: |
      This entry might be wrong if Money Lending Business Act article 2 is amended to add NPO
      exemption. Counter-evidence: any post-amendment ruling citing NPO carve-out.
    confidence: 0.7
    evidence_count: 4
    challenges: 0
    created: 2025-09-15
    last_validated: 2026-04-10
    source: archiver
    ---

    # Japanese NPO lending has no Money Lending Business Act exemption

    Body content here ...

expected_finding: |
  F11 LIFECYCLE_FAILURE: wiki/wn-example-no-outlier.md at lifecycle_stage:active
  has empty outlier slot (anti-confirmation-bias defense missing; v2 spec
  requires non-empty for active+)

```
