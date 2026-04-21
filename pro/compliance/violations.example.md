# Compliance Violations Log · Format Reference

> Example entries for each violation type. Use this as template when debugging hook output or AUDITOR detection logic. This file is **not** actively appended — it's documentation for the format defined in `references/compliance-spec.md`.

## Example 1 · Class A1 (Skip subagent)

```
| 2026-04-21T10:15+09:00 | 退朝 | A1 | P0 | ROUTER scanned wiki/SOUL candidates in main context instead of Launch(archiver). Evidence: main-context output contained "让我先看看要保存什么候选" before any Task() call. | false |
```

**Detection rule** (from `scripts/lifeos-pre-prompt-guard.sh` hook + AUDITOR Compliance Patrol):
- After a trigger word, scan next N tool calls for `Task(agent)` where `agent` matches expected.
- If first non-Read/Grep tool call is NOT Task() → log A1.
- Evidence field must cite specific text excerpt that proves inline simulation.

## Example 2 · Class A2 (Skip directory check)

```
| 2026-04-21T10:30+09:00 | start | A2 | P1 | In dev repo (SKILL.md + pro/agents/ + themes/ detected), retrospective Mode 0 skipped Step 2 DIRECTORY TYPE CHECK. User was not asked a/b/c. | false |
```

**Detection rule**:
- When `cwd` contains all three: `SKILL.md` + `pro/agents/` + `themes/`
- retrospective's output must contain menu: "a) 连接到 second-brain  b) 开发模式  c) 新建" (or English equivalent)
- If absent → log A2.

## Example 3 · Class A3 (Skip Pre-flight check, v1.6.3 new)

```
| 2026-04-21T10:45+09:00 | 上朝 | A3 | P1 | ROUTER's first response missing Pre-flight line. Expected: `🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0`. Actual: went directly to Task() without confirmation line. | false |
```

**Detection rule**:
- After trigger word, ROUTER's first response (text before any tool call) must match regex:
  `^🌅 Trigger: \S+ → Theme: \S+ → Action: Launch\(\S+\)( Mode \d+)?$`
- Missing or malformed → log A3.

## Example 4 · Class B (Fabricate non-existent path)

```
| 2026-04-21T11:02+09:00 | 上朝 | B | P0 | Referenced `_meta/roles/CLAUDE.md` as authority source but this file does not exist. Verified via `ls _meta/roles/` = no such directory. | false |
```

**Detection rule**:
- grep ROUTER/subagent output for markdown-style file path mentions (regex: `\`[\w/.-]+\.md\`` or `\[[^\]]+\]\([^)]+\.md\)`)
- For each match, verify path exists relative to repo root.
- Non-existent paths quoted as authority → log B.

## Example 5 · Class B (Invent escape route)

```
| 2026-04-21T11:15+09:00 | 上朝 | B | P0 | Claimed "轻量简报路径 exists in CLAUDE.md" but full-text search of CLAUDE.md / pro/CLAUDE.md / SKILL.md shows no such path defined. | false |
```

**Detection rule**:
- When ROUTER claims a process/path/procedure exists in specific file, grep that file.
- If not found → log B.

## Example 6 · Class C (archiver incomplete)

```
| 2026-04-21T15:30+09:00 | 退朝 | C | P0 | archiver exited after Phase 2, did not run Phase 3 (DREAM) or Phase 4 (git sync). Session ended with empty Completion Checklist. | false |
```

**Detection rule**:
- After `退朝` trigger, expect Completion Checklist with all 4 phases populated.
- Missing Phase 3 or Phase 4 markers → log C.

## Example 7 · Class D (Placeholder value)

```
| 2026-04-21T15:45+09:00 | 退朝 | D | P1 | Completion Checklist contained placeholder values: `Phase 2 wiki auto-written: {list}` (literal `{list}` not substituted), `Phase 4 git: TBD`. | false |
```

**Detection rule**:
- Parse Completion Checklist row by row.
- Any field containing `TBD`, `{...}`, empty string, or "pending (TBD)" → log D.

## Example 8 · Class E (Main-context Phase execution)

```
| 2026-04-21T16:00+09:00 | 退朝 | E | P0 | ROUTER executed archiver Phase 2 logic in main context: output contained "扫描 wiki 候选" + listed 3 candidates with evidence counts. This is archiver subagent's job per pro/CLAUDE.md Step 10. | false |
```

**Detection rule**:
- After `退朝` trigger, scan main-context output (before Task(archiver)) for Phase-specific keywords:
  - Phase 1: "outbox" / "session_id" / "manifest"
  - Phase 2: "wiki 候选" / "SOUL 候选" / "evidence_count"
  - Phase 3: "DREAM" / "N1-N2" / "N3" / "REM"
  - Phase 4: "git commit" / "git push"
- Any Phase-specific logic in main context before Task() → log E.

## Example 9 · Resolved entry (full transition)

```
| 2026-04-19T22:47+09:00 | 上朝 | A1 | P0 | ROUTER simulated 18 steps in main context | true (v1.6.3 · eval:start-session-compliance · no recurrence 30d · AUDITOR ✅ 2026-05-19) |
```

**Transition rules**:
- `false` → `partial`: fix shipped but awaiting eval + observation window
- `partial` → `true`: eval regression pass AND 30-day no-recurrence observed
- `true` entries stay indefinitely for historical record

## Example 10 · Hook-generated entry (terse format)

When the hook itself writes entries (vs AUDITOR), Details are machine-generated and shorter:

```
| 2026-04-21T16:15+09:00 | 上朝 | A3 | P1 | hook:pre-prompt-guard · Pre-flight line absent in next 500 chars after trigger | false |
```

**Why terse**: hook is bash, can't do deep analysis. Pattern matching only. AUDITOR later adds richer context in follow-up entry with same timestamp prefix.

## Grep recipes (for debugging and auditing)

```bash
# All P0 violations in last 30 days
awk -F'|' '$5 ~ /P0/' pro/compliance/violations.md | head -20

# All unresolved (false / partial) violations
grep -E '\| (false|partial) \|' pro/compliance/violations.md

# Count by type
awk -F'|' 'NR>5 {gsub(/ /,"",$3); count[$3]++} END {for (t in count) print t, count[t]}' pro/compliance/violations.md | sort

# 30-day rolling (requires date math)
cutoff=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d "30 days ago" +%Y-%m-%d)
awk -F'|' -v c="$cutoff" 'NR>5 && $2 > c' pro/compliance/violations.md
```

## See Also

- `pro/compliance/violations.md` — live log
- `references/compliance-spec.md` — complete specification
- `pro/compliance/2026-04-19-court-start-violation.md` — COURT-START-001 incident archive
- `pro/agents/auditor.md` — Compliance Patrol Mode (writes to violations.md)
- `scripts/lifeos-pre-prompt-guard.sh` — hook that writes A3 violations
- `evals/scenarios/start-session-compliance.md` — regression test
