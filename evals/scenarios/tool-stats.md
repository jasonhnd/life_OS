---
scenario: tool-stats
type: tool-invocation
tool: stats
requires_claude: false
# R4.5 machine-eval fields — empty root => "no data in window" + exit 0.
setup_script: |
  mkdir -p {tmp_dir}/_meta/sessions
invocation: "python3 -m tools.stats --root {tmp_dir}"
expected_exit_code: 0
expected_stdout_contains:
  - "no data"
expected_stderr_contains: []
expected_files: []
---

# Tool Scenario · stats

**Contract**: references/tools-spec.md §6.3 · Compliance violation escalation ladder + usage/quality aggregates.

## User Message

```
跑一下 stats：对 violations.md 打出累犯等级，对 sessions 打出过去一季的领域分布和平均 overall_score。
```

(English equivalent: "Run stats: escalation ladder on violations.md and quarterly domain distribution + average overall_score across sessions.")

## Scenario

Two modes must both work cleanly:

**Mode 1 · Compliance ladder** — reads `pro/compliance/violations.md`,
groups rows by `Type` within a 30-day window, emits escalation levels
per `references/compliance-spec.md`:
- `≥3 same type in 30d` → L1 (tighten hook strictness)
- `≥5 same type in 30d` → L2 (briefing warning line)
- `≥10 same type in 30d` → L3 (AUDITOR every Start Session)

**Mode 2 · v1.7 aggregates** — reads `_meta/sessions/*.md` frontmatter,
emits per-period: session_count, avg_overall_score, domain_distribution,
DREAM trigger frequency, top concept tags.

Edge case: empty violations.md (no rows) must NOT crash — must print
"no violations in window" and exit 0.

## Success Criteria

- [ ] Empty `violations.md` → exits 0, prints "no violations in window (30d)"
- [ ] 10 rows all `Type: A1` within 30d → output flags `escalation: L3 (≥10 A1)`
- [ ] 5 rows mix of A1/B/C → no escalation (none reach threshold)
- [ ] `--json` flag emits valid JSON matching the spec schema
- [ ] `--period quarter` computes aggregates for last 90 days
- [ ] `--since 2026-01-01` overrides period window start
- [ ] `--output report.md` writes markdown to file instead of stdout, exit 0
- [ ] Empty `_meta/sessions/` + no violations → "no data" notice, exit 0
- [ ] Legacy invocation (no v1.7 flags, no `--violations`) auto-detects and reports whichever is available

## Input Fixture

**violations.md fixture row format** (per compliance-spec §Entry Format):

```markdown
| Timestamp | Trigger | Type | Severity | Details | Resolved |
|-----------|---------|------|----------|---------|----------|
| 2026-04-01T09:30:00Z | 上朝 | A1 | P0 | ROUTER skipped Task(retrospective) | no |
| 2026-04-02T10:00:00Z | 上朝 | A1 | P0 | ROUTER simulated steps inline | no |
...10 rows total, all A1 within 30d...
```

**sessions fixture** — 30 session files with frontmatter:

```yaml
---
session-id: 2026-04-01-0900-example
subject: "Decide on Plan A vs B"
domains: [finance, career]
overall_score: 0.78
keywords: [runway, equity]
dream_triggered: false
last_modified: 2026-04-01
---
```

## Expected Output

```
$ uv run tools/stats.py --violations pro/compliance/violations.md
=== Escalation Ladder (30d window, ending 2026-04-22) ===
A1 · 10 occurrences · L3 escalation (AUDITOR runs every Start Session)
All other types: below threshold
Exit 0

$ uv run tools/stats.py --period quarter --root ./fixture-brain
=== Session Aggregates (2026-01-22 → 2026-04-22) ===
sessions: 30
avg_overall_score: 0.74
domains: finance=18, career=14, health=4, relationships=3
dream_triggered: 4 sessions (13%)
top_concepts: runway(12), equity(8), negotiation(7)
Exit 0
```

## Failure Modes

- Malformed markdown table row → log row number + skip, don't abort whole report
- `--since` after today → empty window, "no data", exit 0
- Non-existent `--violations` path → exit 2 with clear "file not found"

## Linked Documents

- `references/tools-spec.md` §6.3
- `references/compliance-spec.md` §Escalation Ladder
- `tools/stats.py`
- `tests/test_stats.py`
