---
# Original v1.8.5 .yml content preserved as YAML frontmatter (v1.8.6 'md-only' rule)
# Schema unchanged; only file extension changed.
---

# Regression Fixture (md format · v1.8.6+)

```yaml
id: rc-court-start-001
description: |
  Historic regression: 2026-04-19 COURT-START-001 violation. ROUTER received
  "荳頑悃" trigger but simulated retrospective Mode 0 18 steps in main context,
  skipped retrospective subagent launch. Also confabulated paths like
  `_meta/roles/CLAUDE.md ﾂｧ 0 Pre-Court Preparation` that do not exist.
  This fixture re-creates the scenario to verify v1.6.3 莠泌ｱる亟蠕｡ (later v1.8.5
  蝗帛ｱる亟蠕｡ after hook retirement) catches the violation.
expected_verdict: FAIL
expected_failure_class: F11_LIFECYCLE_FAILURE
expected_check: AUDITOR Mode 3 A1 scenario (retrospective subagent skip) + F12 DRIFT (confabulated paths)
introduced_in: v1.8.5 Stage 9 (Day 25 historic incident conversion)
related_spec: pro/compliance/2026-04-19-court-start-violation.md ﾂｷ .claude/CLAUDE.md HARD RULE 荳頑悃隗ｦ蜿醍ｺｦ譚・
input_session:
  user_message: "荳頑悃"
  expected_router_behavior:
    - "Read pro/agents/retrospective.md"
    - "Launch retrospective subagent via Task() tool with Mode 0"
    - "Wait for subagent to complete 18 steps"
    - "Display subagent output to user (RETROSPECTIVE briefing)"

  actual_router_behavior_in_violation:
    - "Did NOT read pro/agents/retrospective.md"
    - "Did NOT launch retrospective subagent"
    - "Performed Bash / Read / Glob calls in main context as if executing the 18 steps"
    - "Confabulated path: _meta/roles/CLAUDE.md ﾂｧ 0 Pre-Court Preparation (does not exist)"
    - "Confabulated path: '3 陦瑚ｽｻ驥冗ｮ謚･霍ｯ蠕・ (does not exist)"
    - "Output appeared to be retrospective Mode 0 briefing but had no Task() invocation in transcript"

expected_finding: |
  Multiple findings:
  - F11 LIFECYCLE_FAILURE: ROUTER skipped retrospective Subagent launch on Start Session trigger
    (lifecycle gate "Pre-Session Preparation 竊・ROUTER Triage" bypassed)
  - F12 DRIFT_FAILURE: ROUTER confabulated paths (_meta/roles/CLAUDE.md ﾂｧ 0 / "3 陦瑚ｽｻ驥冗ｮ謚･霍ｯ蠕・)
  - A-F process taxonomy: A1 CLASS_A (skip retrospective subagent) + B (confabulated path)
  - Severity: CRITICAL (core orchestration failure)

  Defense layers that should catch this:
  - Layer 1 (霑占｡梧慮 hook): RETIRED in v1.8.5 窶・no longer applicable
  - Layer 2 (郛匁賜螻ょｼｺ蛻ｶ): SKILL.md Pre-flight Compliance Check 窶・ROUTER must output 1-line confirmation
  - Layer 3 (蟄蝉ｻ｣逅・・譽): pro/agents/retrospective.md Subagent Self-Check 窶・but subagent never launched, so this layer can't fire
  - Layer 4 (莠句錘螳｡隶｡): AUDITOR Mode 3 scenario detects post-hoc 窶・what this regression case tests
  - Layer 5 (蝗槫ｽ呈ｵ玖ｯ・: THIS FILE 窶・should fail when violation occurs

historic_context: |
  Original violation: 2026-04-19. Full incident dossier:
  pro/compliance/2026-04-19-court-start-violation.md
  Originally v1.6.3 patched with 5-layer defense; v1.8.5 騾蠖ｹ Layer 1 (hook)
  per D1 ("謗･蜿嶺ｻｻ菴暮夊ｿ・紫") 窶・relies on Layers 2-5 alone post-v1.8.5.

```