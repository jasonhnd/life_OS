---
scenario: tool-daily_briefing
type: tool-invocation
tool: daily_briefing
requires_claude: false
# R4.5 machine-eval fields
setup_script: |
  mkdir -p {tmp_dir}/_meta/sessions {tmp_dir}/_meta/dreams {tmp_dir}/_meta/projects {tmp_dir}/_meta/eval-history {tmp_dir}/inbox
env:
  PYTHONIOENCODING: "utf-8"
invocation: "python3 -m tools.daily_briefing --root {tmp_dir}"
expected_exit_code: 0
expected_stdout_contains:
  - "Today's Briefing"
  - "SOUL Core"
  - "Recent DREAMs"
  - "Active Projects"
  - "Inbox"
  - "Eval History"
expected_stderr_contains: []
expected_files: []
---

# Tool Scenario · daily_briefing

**Contract**: references/tools-spec.md §6.5 · Today's briefing — 5-section markdown snapshot from SOUL / DREAM / projects / inbox / eval history.

## User Message

```
给我今天的早报：SOUL 高权重维度、近 30 天 DREAM 摘要、活跃项目、收件箱、最近 3 次 eval。
```

(English equivalent: "Give me today's briefing: SOUL high-weight dimensions, 30-day DREAM summary, active projects, inbox, last 3 eval history entries.")

## Scenario

Retrospective subagent Mode 0 Step 13 (briefing assembly) calls
`daily_briefing.py` as a pure-data aggregator. No LLM, no network.
Runtime budget < 3 seconds. Always exits 0 (even empty brain).

The 5 sections and data sources per spec §6.5:

| Section | Source | Threshold |
|---------|--------|-----------|
| SOUL Core | `SOUL.md` dimensions | weight ≥ 0.7 |
| Recent DREAMs | `_meta/dreams/*-dream.md` | last 30 days |
| Active Projects | `_meta/projects/*.md` | modified ≤ 14 days |
| Inbox | `inbox/*.md` | count only, no body |
| Eval History | `_meta/eval-history/*.md` | last 3 by date |

## Success Criteria

- [ ] `uv run tools/daily_briefing.py --root <fixture>` exits 0
- [ ] Output begins with `# Today's Briefing — YYYY-MM-DD` (today's date)
- [ ] Output has all 5 sections in order (SOUL Core → DREAMs → Projects → Inbox → Eval History)
- [ ] SOUL dimensions with `weight < 0.7` NOT shown in SOUL Core section
- [ ] DREAM files older than 30 days NOT in Recent DREAMs
- [ ] Projects not modified in 14 days NOT in Active Projects
- [ ] Eval History shows exactly the 3 most recent by filename date (desc)
- [ ] Empty second-brain → all sections show "(none)" or "(0 entries)", exit 0
- [ ] Malformed SOUL.md dimension block → skip that block, log warn, finish other sections
- [ ] Runtime < 3 seconds for a 1000-file brain (perf target per spec)

## Input Fixture

**SOUL.md dimensions** (synthetic) — yaml block per dimension:

```
## Dimension: autonomy-vs-stability
```yaml
weight: 0.82
confidence: 0.65
evidence:
  - "Chose Plan B over A when Plan B had higher autonomy"
  - "Declined job offer for stability reasons"
```
```

**DREAM file**: `_meta/dreams/2026-04-10-dream.md` with 3 trigger evaluations.

**Eval history**: 5 files:
- `_meta/eval-history/2026-04-20-passpay.md`
- `_meta/eval-history/2026-04-15-startup.md`
- `_meta/eval-history/2026-04-10-runway.md`
- (2 older, should be excluded)

## Expected Output

```
$ uv run tools/daily_briefing.py --root ./fixture-brain
# Today's Briefing — 2026-04-22

## SOUL Core
- autonomy-vs-stability (weight 0.82, confidence 0.65)
- risk-tolerance (weight 0.71, confidence 0.55)

## Recent DREAMs (last 30 days: 3 reports)
- 2026-04-20: 2 REM triggers (stale-commitment, repeated-decision)
- 2026-04-15: 1 REM trigger (novelty-gap)
- 2026-04-10: 0 REM triggers

## Active Projects (2)
- passpay (last modified 2026-04-19)
- startup-side (last modified 2026-04-17)

## Inbox (7 pending)

## Eval History (last 3)
- 2026-04-20-passpay (overall 0.82)
- 2026-04-15-startup (overall 0.74)
- 2026-04-10-runway (overall 0.69)

Exit 0
```

## Failure Modes

- Missing SOUL.md → SOUL Core shows "(no SOUL.md found)", continue with other sections
- Corrupt YAML inside SOUL dimension → skip that dimension, log warn
- No permission on `_meta/` → exit 1 with clear error (this is rare, not a normal case)

## Linked Documents

- `references/tools-spec.md` §6.5
- `references/SOUL-template.md`
- `tools/daily_briefing.py`
- `tests/test_daily_briefing.py`
