# Regression Fixture (md format · v1.8.6+)

```yaml
id: rc-nested-fanout-stall
description: |
  Negative fixture: during a bulk batch job, a parent subagent spawned its own child
  subagents (grandchildren of the main loop). On the Claude Code host, grandchild
  completion notifications are delivered ONLY to the main loop — never to the
  intermediate parent — so the parent waited indefinitely on children that had
  already finished, stalling the run until manual operator intervention
  (production near-meltdown, issue #3 C3). v1.10.0 forbids the pattern:
  agents/dispatcher.md §"Flat Fan-Out for Bulk Work" — bulk fan-out MUST be flat
  (main loop → workers, depth 1), serial small waves preferred, would-be nesting
  restructured into sequential flat waves. If a validator run over a transcript
  showing this pattern reports PASS, the rule has been silently re-permitted.
expected_verdict: FAIL
expected_failure_class: F11_LIFECYCLE_FAILURE
expected_check: AUDITOR Mode 3 workflow-state-machine review + agents/dispatcher.md §Flat Fan-Out for Bulk Work
introduced_in: v1.10.0
related_spec: agents/dispatcher.md §Flat Fan-Out for Bulk Work + hosts/CLAUDE.md §"Bulk fan-out is flat"

input_transcript_excerpt: |
  [main loop] Task(subagent_type=knowledge-extractor) launched for 400-file batch
  [knowledge-extractor] Batch too large for inline processing. Spawning 4 category
    workers via Task tool: worker-wiki, worker-projects, worker-concepts, worker-inbox
  [worker-wiki] ...completed (notification delivered to MAIN LOOP only)
  [worker-projects] ...completed (notification delivered to MAIN LOOP only)
  [knowledge-extractor] Waiting for workers to report back...
  [knowledge-extractor] Still waiting... (workers finished 40 minutes ago)
  [operator] manual kill + restart required

expected_finding: |
  F11 LIFECYCLE_FAILURE: intermediate subagent (knowledge-extractor) spawned child
  subagents during bulk work — nested fan-out depth 2. Grandchild completion
  notifications route only to the main loop on this host; the parent stalled
  indefinitely on already-finished children.
  Per agents/dispatcher.md §Flat Fan-Out for Bulk Work (v1.10.0):
    - bulk fan-out MUST be flat (main loop spawns workers directly)
    - workers are FORBIDDEN from spawning further subagents
    - the correct restructure is sequential flat waves (3-4 workers per wave,
      main loop collects each wave before launching the next)
  Severity: HIGH (whole-run stall requiring manual intervention).
```
