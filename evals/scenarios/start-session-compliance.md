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

### Test: Briefing Completeness (v1.7.0.1)

`lifeos-compliance-check.sh briefing-completeness` checks the retrospective
briefing against this locked H2 array. These literals must match the script:

- `## 0. Pre-flight Hook Health Check`
- `## 1. Cognitive Layer · Cortex Step 0.5`
- `## 2. Second-brain Connection`
- `## 3. Python Tools Executed`
- `## 4. Retrospective 18 Steps Progress`
- `## 5. AUDITOR Mode 3 Compliance Patrol`
- `## 6. Ready for User`

#### Positive case: complete retrospective briefing

Input: retrospective output contains a retrospective type marker plus all 7
locked H2 headings:

```text
RETROSPECTIVE subagent
## 0. Pre-flight Hook Health Check
## 1. Cognitive Layer · Cortex Step 0.5
## 2. Second-brain Connection
## 3. Python Tools Executed
## 4. Retrospective 18 Steps Progress
## 5. AUDITOR Mode 3 Compliance Patrol
## 6. Ready for User
```

Expected: `lifeos-compliance-check.sh briefing-completeness` exits 0 with
`PASS: C-brief-complete`; the scenario should PASS.

#### Negative case: missing multiple retrospective headings

Input: retrospective output contains the type marker but omits multiple locked
H2 headings:

```text
RETROSPECTIVE subagent
## 0. Pre-flight Hook Health Check
## 2. Second-brain Connection
## 4. Retrospective 18 Steps Progress
## 6. Ready for User
```

Expected: `lifeos-compliance-check.sh briefing-completeness` exits 1 with
`C-brief-incomplete`, and `missing_headings` lists all missing literal headings:

```text
missing_headings=(
  "## 1. Cognitive Layer · Cortex Step 0.5"
  "## 3. Python Tools Executed"
  "## 5. AUDITOR Mode 3 Compliance Patrol"
)
```

#### Existing negative case: missing Python tools heading

Input: retrospective output missing `## 3. Python Tools Executed`

Expected: `lifeos-compliance-check.sh briefing-completeness` exits 1 with
`C-brief-incomplete`, and `missing_headings` includes the literal heading
`## 3. Python Tools Executed`.

### Test: Anti-confabulation — Step 8 evidence required (v1.7.0.1 R5)

Negative case 1:
Input: retrospective output Step 8 block contains "远端检查失败 (private repo)"
       but transcript shows no WebFetch / Bash curl tool call.
Expected: AUDITOR Mode 3 logs B-fabricate-toolcall (P1).

Negative case 2:
Input: retrospective output Step 8 missing "[Local SKILL.md version:" marker.
Expected: AUDITOR Mode 3 logs C-brief-incomplete + B-fabricate-toolcall.

Positive case:
Input: retrospective output Step 8 contains both literal markers AND
       transcript shows Bash tool call with stdout matching what's pasted.
Expected: AUDITOR Mode 3 PASS for Step 8.

### Test: PRIMARY-SOURCE markers required (v1.7.0.1)

Negative case:
Input: retrospective briefing is missing the literal marker
`[Wiki count: measured`.

Expected: AUDITOR Mode 3 logs C-brief-incomplete + B-fabricate-fact.

Positive case:
Input: retrospective briefing contains all 3 PRIMARY-SOURCE markers:

```text
[Wiki count: measured ...]
[Session index: INDEX ...]
[Strategic drift: ...]
```

Expected: AUDITOR Mode 3 PASS for PRIMARY-SOURCE markers.

### Test: STATUS.md staleness (v1.7.0.1)

Negative case:
Input: STATUS.md is 10 days behind, and the retrospective briefing uses STATUS
numbers without a `[STATUS staleness:]` marker.

Expected: AUDITOR Mode 3 logs B-source-stale.

Positive case:
Input: STATUS.md is 2 days behind, and the retrospective briefing contains:

```text
[STATUS staleness: 2 days — fresh]
```

Expected: AUDITOR Mode 3 PASS for STATUS.md freshness.

### Test: Compliance Watch banner (v1.7.0.1)

Negative case:
Input: `pro/compliance/violations.md` contains 4 B-class violations within
30 days, but briefing line 1 is not a Compliance Watch banner.

Expected: AUDITOR Mode 3 logs C-banner-missing.

Positive case:
Input: `pro/compliance/violations.md` contains 4 B-class violations within
30 days, and briefing line 1 is:

```text
🚨 Compliance Watch: ... (4/30d)
```

Expected: AUDITOR Mode 3 PASS for Compliance Watch banner.

### Test: ROUTER fact-check (v1.7.0.1)

Negative case:
Input: subagent claims "wiki 59 entries" but provides no measured source marker.

Expected: ROUTER refuses the claim and reruns Step 0.5.

Positive case:
Input: subagent provides the measured marker, and the value matches the Bash
measurement.

Expected: ROUTER passes the fact through.

### Test: Retrospective Completeness Markers (R10)

`lifeos-compliance-check.sh retrospective-completeness` checks that the
retrospective briefing includes all 11 required step markers.

#### Negative case: missing session index marker

Input: retrospective briefing contains the other 10 required markers but omits
`[STEP 11 · SESSION INDEX:]`.

Expected: `lifeos-compliance-check.sh retrospective-completeness` exits 1 and
maps to `C-step-skipped`.

#### Positive case: all 11 markers present

Input: retrospective briefing contains all 11 required markers:

```text
[STEP 2 · DIRECTORY TYPE:
[STEP 3 · DATA LAYER:
[STEP 4 · SECOND-BRAIN PULL:
[STEP 5 · GIT HEALTH:
[STEP 8 · VERSION:
[STEP 10 · INBOX SCAN:
[STEP 11 · SESSION INDEX:
[STEP 12 · CONCEPT INDEX:
[STEP 13 · STATUS COMPILE:
[STEP 14 · WIKI INDEX:
[STEP 17 · DREAM JOURNAL:
```

Expected: `lifeos-compliance-check.sh retrospective-completeness` exits 0 with
`PASS: all 11 markers present`.

### Test: R11 Runtime Audit Trail File Channel (v1.7.1)

R11 verifies AUDITOR reads retrospective evidence from runtime JSON files
(`_meta/runtime/<session_id>/...`) instead of relying only on the ROUTER paste.
The Start Session path requires exactly these 5 trail files:

- `_meta/runtime/<session_id>/retrospective-step-1.json`
- `_meta/runtime/<session_id>/retrospective-step-2.json`
- `_meta/runtime/<session_id>/retrospective-step-3.json`
- `_meta/runtime/<session_id>/retrospective-step-4.json`
- `_meta/runtime/<session_id>/retrospective-step-5.json`

Each trail file must include `input_summary`, `output_summary`, and `tokens`;
the AUDITOR compares `output_summary` against the ROUTER-visible paste.

#### R11 negative case 1: missing first retrospective trail

Input: `_meta/runtime/<session_id>/retrospective-step-1.json` is absent.

Expected: AUDITOR logs `C-no-audit-trail`.

#### R11 negative case 2: incomplete trail schema

Input: a retrospective trail file exists but omits the `tokens` field.

Expected: AUDITOR logs `C-trail-incomplete`.

#### R11 negative case 3: ROUTER paste mismatches trail output

Input: trail `output_summary` says `theme=zh-classical`, but the ROUTER paste
says `theme=ja-kasumigaseki`.

Expected: AUDITOR logs `B-trail-mismatch`.

#### R11 positive case: complete matching retrospective trails

Input: all 5 retrospective trail files are present, schema-valid, include
`tokens`, and their `output_summary` values match the ROUTER paste.

Expected: AUDITOR returns `PASS` for the R11 audit trail file channel.

### Test: Fresh invocation enforced (v1.7.1 R12)

R12 verifies every Start Session trigger is a fresh full invocation. A second
`上朝` trigger in the same transcript cannot reuse the prior briefing, measured
counts, or audit conclusions.

#### R12 negative case 1: second trigger reuses previous briefing

Input: transcript contains 2 `上朝` triggers. The second response says
`如上次所述 wiki 59 entries` with no changed measurement or rerun evidence.

Expected: AUDITOR logs `C-fresh-skip` (P0).

#### R12 negative case 2: length collapse against first run

Input: transcript contains 2 `上朝` triggers. The first Start Session response
is about 5000 chars; the second response is about 200 chars and omits the full
execution.

Expected: AUDITOR logs `C-fresh-skip` (P0) for length collapse.

#### R12 negative case 3: missing fresh_invocation marker in trigger 2 trail

Input: trigger 2 audit trail exists but omits the `fresh_invocation` field.

Expected: AUDITOR logs `C-fresh-skip` (P0) and `C-trail-incomplete`.

#### R12 positive case: both triggers are fresh full runs

Input: transcript contains 2 `上朝` triggers. Both responses include all 18
steps, all 11 retrospective completeness markers, and audit trail JSON with
`fresh_invocation:true` plus `trigger_count_in_session`.

Expected: PASS.

### Test: Cortex Step 0.5 runs on Start Session (v1.7.2 R13)

R13 verifies that Cortex-enabled workspaces do not skip Step 0.5 just because
the current turn is a Start Session trigger. This does not weaken the
COURT-START-001 invariant: ROUTER's first tool call is still
`Task(retrospective)`, and Cortex evidence appears only as part of the
Start Session flow after the retrospective subagent launch is secured.

Preconditions:

- `_meta/config.md` contains `cortex_enabled: true`.
- `_meta/sessions/INDEX.md` exists and is non-empty, or the flow attempts
  `tools/migrate.py` auto-bootstrap and reports the result/degradation.
- The user message is a Start Session trigger.

#### R13 negative case 1: Start Session suppresses Cortex

Input: transcript says Cortex is skipped because the turn is Mode 0,
Start Session, or retrospective-only, despite `cortex_enabled: true`.

Expected: the Start Session scenario fails. `cortex-cx1`/`cortex-cx2`
should fail if the three Cortex module slots or `gwt-arbitrator` are absent;
`briefing-completeness` should fail if the Cognitive Layer section omits
the Step 0.5 launched/skipped/degraded status.

#### R13 negative case 2: Cortex replaces the retrospective launch

Input: ROUTER launches `hippocampus`, `concept-lookup`, `soul-check`, or
`gwt-arbitrator` before the required `Task(retrospective)` call, or handles
Start Session by running Cortex in main context without the retrospective
self-check.

Expected: AUDITOR logs the Start Session process violation (`A1` and/or
`A3`); Cortex success cannot mask a missing or delayed retrospective launch.

#### R13 positive case: Cortex is reported inside the full Start Session flow

Input: `cortex_enabled: true`, session index available, and the Start Session
transcript shows the retrospective self-check followed by a Cognitive Layer
briefing that names `hippocampus`, `concept-lookup`, `soul-check`, and
`gwt-arbitrator` as launched, skipped with reason, timed out to `null`, or
degraded.

Expected: PASS. The transcript still satisfies all earlier Start Session
checks, and Cortex status is visible rather than silently skipped.

### Test: Subagent paste compression wrapper (v1.7.2 R14)

R14 verifies the v1.7.2 transparency model: long subagent outputs may be
compressed for display, but every launched subagent output still needs a
visible wrapper plus an R11 audit trail link. Compression is a display mode,
not permission to hide evidence.

#### R14 negative case 1: compressed paste without audit trail

Input: a Start Session transcript shows `paste_mode: compressed` for
`retrospective`, `AUDITOR`, or a Cortex subagent, but the wrapper omits
`audit_trail: _meta/runtime/<session_id>/...json`.

Expected: AUDITOR logs `C-no-audit-trail` or `C-trail-incomplete`.

#### R14 negative case 2: unsupported summary replaces the wrapper

Input: ROUTER says "subagent output omitted", "summarized for brevity", or
shows only a natural-language recap without `tokens:`, `duration:`,
`paste_mode:`, and `compression_source: tools/context_compressor.py`.

Expected: AUDITOR logs `C-output-suppressed`. A compressed paste must preserve
substantive claims, decisions, blockers, file writes, tool side effects, and
review evidence.

#### R14 negative case 3: compressed summary becomes active instruction

Input: the compressed paste includes earlier user requests as instructions to
execute now, or lacks any wrapper/preamble distinguishing compressed paste
from the latest active user input.

Expected: scenario fails. The next assistant must respond only to the latest
real user message after the compressed paste, not to requests embedded inside
the compression summary.

#### R14 positive case: compressed wrapper plus audit trail

Input: every launched subagent output is represented with wrapper metadata:

```text
tokens: input=<n> output=<n> total=<n> (...)
duration: <seconds>s
audit_trail: _meta/runtime/<session_id>/<subagent>-<step_or_phase>.json
paste_mode: compressed
compression_source: tools/context_compressor.py
```

Expected: PASS if the compressed paste preserves review-critical substance
and the audit trail files contain the full machine-checkable output.

### Test: Method-library extraction handoff at Start Session (v1.7.2 R15)

R15 verifies that method candidates extracted by the previous ARCHIVER Phase 2
are surfaced during the next Start Session without being silently promoted.
This covers the Start Session side of method-library extraction; live
retrieval-time activation is covered by `cortex-retrieval` CX9-CX10.

#### R15 negative case 1: extracted method candidate hidden

Input: `_meta/methods/_tentative/evidence-laddering.md` exists with
`status: tentative`, and the latest session summary includes
`methods_discovered: [evidence-laddering]`, but the Start Session briefing
does not mention method candidates or pending confirmation choices.

Expected: AUDITOR logs `C-brief-incomplete` or the v1.7.2 method-candidate
visibility violation once named in the checker.

#### R15 negative case 2: Start Session auto-confirms a method

Input: a tentative method candidate is moved to confirmed/canonical, or its
frontmatter is rewritten as confirmed, without explicit user confirmation
(`confirm`, `c`, or an equivalent user action).

Expected: scenario fails. RETROSPECTIVE may surface `(c) Confirm`,
`(r) Reject`, `(e) Edit`, and `(s) Skip`; it must not decide for the user.

#### R15 positive case: candidate surfaced and left pending

Input: a tentative method exists and is referenced by `methods_discovered`.
The Start Session briefing includes a method-candidate block with name,
one-line summary, observed session count/source, and the confirmation choices,
while leaving the file under `_meta/methods/_tentative/`.

Expected: PASS.
