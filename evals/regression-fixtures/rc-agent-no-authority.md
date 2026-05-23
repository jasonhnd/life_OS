---
# Original v1.8.5 .yml content preserved as YAML frontmatter (v1.8.6 'md-only' rule)
# Schema unchanged; only file extension changed.
---

# Regression Fixture (md format · v1.8.6+)

```yaml
id: rc-agent-no-authority
description: |
  Negative fixture: pro/agents/*.md file missing v2 required `classification.authority_level`
  field (one of the 6 facets). AUDITOR Mode 6 A1 check MUST FAIL on this. If A1 reports
  PASS, validator has regressed and an agent without declared authority has slipped through.
expected_verdict: FAIL
expected_failure_class: F3_SCHEMA_FAILURE
expected_check: A1 (every agent has all v2 required fields)
introduced_in: v1.8.5 Stage 6
related_spec: references/agent-spec.md v2 ﾂｧ"Required v2 Fields"

input_agent_file:
  path: pro/agents/example-no-authority.md
  content: |
    ---
    name: example-no-authority
    description: "Example agent for regression testing 窶・missing authority_level"
    tools: Read, Grep, Glob
    model: opus
    id: agent-example-no-authority
    version: "1.0.0"
    classification:
      function: validate
      target_object: "regression test artifact"
      automation_mode: LLM_assisted
      # MISSING authority_level 窶・regression bait
      risk_level: low
      lifecycle_stage: candidate
    operating_hypothesis: |
      Given a regression test invocation, this agent should produce a verdict
      within low risk of test infrastructure leakage.
    context_manifest:
      source_of_truth:
        - evals/regression-fixtures/
      supporting: []
      forbidden:
        - pro/agents/reviewer.md
    blast_radius:
      allowed_scope:
        - _meta/runtime/<sid>/example-no-authority-*.json
      forbidden_scope:
        - SOUL.md
        - pro/agents/
    failure_modes:
      known: []
      warning_signs: []
      repair_actions: []
    ---

    Body of agent definition...

expected_finding: |
  F3 SCHEMA_FAILURE: pro/agents/example-no-authority.md missing v2 field:
  classification.authority_level (one of 6 facets required per agent-spec.md v2)

```