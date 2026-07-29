---
# Original v1.8.5 .yml content preserved as YAML frontmatter (v1.8.6 'md-only' rule)
# Schema unchanged; only file extension changed.
---

# Regression Fixture (md format · v1.8.6+)

```yaml
id: rc-wiki-no-hypothesis
description: |
  Negative fixture: wiki entry missing the v2 required `operating_hypothesis`
  field (or has it too short / not in Given/can/within form). AUDITOR Mode 5
  W1 check MUST FAIL on this. If W1 reports PASS, validator has regressed
  and a structurally incomplete entry has slipped through.
expected_verdict: FAIL
expected_failure_class: F3_SCHEMA_FAILURE
expected_check: W1 (every entry has 7 v2 required field groups)
introduced_in: v1.8.5 Stage 5
related_spec: references/wiki-spec.md v2 §"v2 HARD Schema Constraints §1"

input_wiki_entry:
  path: wiki/wn-example-no-hypothesis.md
  content: |
    ---
    id: wn-example-no-hypothesis
    name: "Example knowledge entry without hypothesis"
    version: "0.1.0"
    classification:
      function: validate
      target_object: "trust structure choice for inheritance"
      automation_mode: human_executed
      authority_level: suggest_only
      risk_level: high
      lifecycle_stage: active
    # MISSING operating_hypothesis field — regression bait
    context_manifest:
      source_of_truth: ["Japan civil code book 5"]
      supporting: []
      forbidden: []
    reference_set:
      aspirational: []
      anti_reference: []
      boundary_case: []
      mainstream_baseline: []
      outlier:
        - ref: "Alice's family used a simple will, which I dislike for its rigidity"
          why: "but it worked fine for 30 years with no contested distribution"
    failure_modes:
      known: []
      warning_signs: []
      repair_actions: []
    arguments_against: |
      This entry might be wrong if Japanese trust law changes after 2026.
      Counter-evidence: any 2027+ amendment to 豌第ｳ・887 affecting trust eligibility.
    confidence: 0.6
    evidence_count: 3
    challenges: 0
    created: 2026-01-10
    last_validated: 2026-04-15
    source: archiver
    ---

    # Trust structures favor inheritance flexibility over fee minimization in Japan

    Body content here ...

expected_finding: |
  F3 SCHEMA_FAILURE: wiki/wn-example-no-hypothesis.md missing v2 field: operating_hypothesis

```