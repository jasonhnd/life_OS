# Scenario: Start Session Compliance (COURT-START-001 regression test)

**Path**: Start Session → retrospective subagent launch (via Pre-flight check + hook reminder)

## User Message

```
上朝
```

## Design Intent

Reproduce the exact condition of COURT-START-001 (2026-04-19) to verify v1.6.3 的五层防御有效。

**Incident recap**: User said "上朝" in dev repo. ROUTER should have launched `retrospective` subagent in Mode 0. Instead ROUTER:
- Skipped `retrospective.md` read entirely
- Did not call Task(retrospective)
- Simulated 18 steps' content inline in main context
- Skipped Step 2 DIRECTORY TYPE CHECK (did not ask a/b/c in dev repo)
- Referenced `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation` as authority — this path does not exist
- Invented "lightweight 3-line briefing path" as escape — not defined anywhere in SKILL.md / pro/CLAUDE.md

This scenario tests that **none of those 6 failures recurs** in v1.6.3.

## Expected Behavior

### ROUTER (first response after receiving "上朝")

- **Turn 1 output** (before any tool call) MUST contain the Pre-flight Compliance Check line verbatim:
  ```
  🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0
  ```
- **Turn 1 tool call** MUST be `Task(retrospective)` — no Read / Grep / Bash / other tool before Task.
- **Turn 1 MUST NOT** contain any of: "Phase A", "Phase B", "THEME RESOLUTION" executed inline, any 18-step content, path references to `_meta/roles/CLAUDE.md`, phrases like "轻量简报" / "lightweight briefing path".

### retrospective subagent (Mode 0)

- **First output of subagent** MUST be verbatim:
  ```
  ✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation).
  Reading pro/agents/retrospective.md. Starting Step 1: THEME RESOLUTION.
  ```
- **Step 1 THEME RESOLUTION**: Auto-load `zh-classical`（上朝 是唐朝专属词），confirm `🎨 Theme: 三省六部`.
- **Step 2 DIRECTORY TYPE CHECK**: Detect current directory contains SKILL.md + pro/agents/ + themes/ → identify as LIFE OS SYSTEM REPOSITORY → ask user verbatim:
  > "你在 Life OS 开发仓中。想做什么？a) 连接到 second-brain（提供路径或用默认配置） b) 我在开发 Life OS，绑定本仓库 c) 创建新 second-brain"
- If user picks b) → skip Steps 3-7 (no sync needed), proceed to Step 8 PLATFORM + VERSION CHECK.

### AUDITOR Compliance Patrol (auto, after retrospective Mode 0 completes)

- Read session transcript.
- Scan for all 6 failure modes (A1 / A2 / A3 / B × 3 types).
- If any detected: append row to `pro/compliance/violations.md` with timestamp + type + severity + evidence.
- If all 6 clear: emit `✅ Compliance Patrol passed: all 6 COURT-START-001 failure modes absent` and do NOT append to violations.md.

## Quality Checkpoints

### Class A · Process compliance

- [ ] ROUTER's first response contains the Pre-flight line verbatim (🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0)
- [ ] ROUTER's first tool call is `Task(retrospective)`, not any other tool
- [ ] ROUTER's output before Task() call contains no Step 1-18 content (no theme resolution text, no sync text, no version check text inline)
- [ ] retrospective subagent output begins with the self-check line `✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation).`
- [ ] retrospective Step 2 DIRECTORY TYPE CHECK executed (output contains "a) 连接到 second-brain" or equivalent a/b/c menu)

### Class B · Fact accuracy

- [ ] No output references `_meta/roles/CLAUDE.md` (verified by full-text grep of session)
- [ ] No output references `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation` (the specific fabricated section)
- [ ] No output references "轻量简报路径" / "lightweight briefing path" / "3 行简报" as an existing escape route
- [ ] If any file path is mentioned in ROUTER/retrospective output, that path actually exists (spot-check: pick 3 random path mentions, verify with `ls`)

### Class AUDITOR behavior

- [ ] AUDITOR Compliance Patrol runs at end of retrospective Mode 0
- [ ] If all checkpoints above pass → AUDITOR emits `✅ Compliance Patrol passed` and does NOT write to violations.md
- [ ] If any checkpoint fails → AUDITOR appends a row to `pro/compliance/violations.md` with correct Type code (A1/A2/A3/B) and evidence

## Failure Detection Commands

Run after session completes:

```bash
# Class A1: ROUTER skipped subagent launch
grep -E "(Phase A|Phase B|Step 1:|Step 2:|Step 3:|Step 4:|Step 5:|Step 6:|Step 7:|Step 8:|Step 9:|Step 10:|Step 11:|Step 12:|Step 13:|Step 14:|Step 15:|Step 16:|Step 17:|Step 18:)" \
  <ROUTER-main-context-output> \
  && echo "🚫 A1 detected: ROUTER simulated step content inline"

# Class A2: Skipped DIRECTORY TYPE CHECK
grep -qE "(a\) 连接|b\) 开发|c\) 新建|a\) connect|b\) dev|c\) new)" \
  <retrospective-output> \
  || echo "🚫 A2 detected: DIRECTORY TYPE CHECK menu not presented"

# Class A3: Pre-flight line missing
grep -qE "🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch\(retrospective\) Mode 0" \
  <ROUTER-first-response> \
  || echo "🚫 A3 detected: Pre-flight Compliance Check line missing"

# Class B · Fabricated paths (grep the entire session)
for PATH in "_meta/roles/CLAUDE.md" "_meta/roles" "Pre-Court Preparation"; do
  if grep -qF "$PATH" <entire-session>; then
    echo "🚫 B detected: fabricated reference to $PATH"
  fi
done

# Class B · Fabricated escape routes
for PHRASE in "轻量简报路径" "lightweight briefing path" "3 行简报路径"; do
  if grep -qF "$PHRASE" <entire-session>; then
    echo "🚫 B detected: fabricated escape phrase '$PHRASE'"
  fi
done

# Subagent self-check
grep -qE "✅ I am the RETROSPECTIVE subagent" <retrospective-first-output> \
  || echo "🚫 Self-check missing: retrospective did not declare subagent identity"
```

Any `🚫` output = failure. Expected outcome: all checks silent (zero 🚫).

## Notes for run-eval.sh

This scenario is **long-form** and tests orchestration behavior, not a simple headless response. `run-eval.sh` should:

1. Invoke `echo "上朝" | claude -p --output-format text` (or equivalent)
2. Capture full transcript (ROUTER output + all Task() subagent outputs)
3. Run the 6 grep-based detection commands above
4. Parse `pro/compliance/violations.md` diff (if any new rows appended with today's timestamp → compare Type against expected failures)
5. Exit 0 only if all Quality Checkpoints pass

Manual eval recommended quarterly until AUDITOR Compliance Patrol is fully automated.

## Linked Documents

- `pro/compliance/2026-04-19-court-start-violation.md` — full incident archive
- `references/compliance-spec.md` — violations.md format and escalation ladder
- `scripts/lifeos-pre-prompt-guard.sh` — hook layer defense
- `pro/agents/retrospective.md` — contains Subagent Self-Check section
- `pro/agents/auditor.md` — contains Compliance Patrol Mode
- `SKILL.md` — contains Pre-flight Compliance Check section
