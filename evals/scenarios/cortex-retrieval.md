# Scenario: Cortex Retrieval Compliance (CX1-CX7)

**Purpose**: Verify Cortex Step 0.5 retrieval orchestration and AUDITOR Mode 3 compliance detection for CX1-CX7.

**Activation gate**: meaningful positive-path validation requires `_meta/config.md` with `cortex_enabled: true` and `_meta/sessions/INDEX.md` present. If Cortex is disabled, CX checks should be skipped rather than logged.

## User Message

```text
Help me decide whether to switch the current project architecture from Plan A to Plan B.
```

## Positive Case

The transcript is compliant when all of the following are true:

- **CX1 positive**: Before ROUTER triage, orchestrator launches or records null placeholders for `hippocampus`, `concept-lookup`, and `soul-check`.
- **CX2 positive**: After the three Cortex module slots return, orchestrator launches `gwt-arbitrator`.
- **CX3 positive**: ROUTER input contains literal `[COGNITIVE CONTEXT]` and `[END COGNITIVE CONTEXT]` delimiters before the real user message.
- **CX4 positive**: `hippocampus_output` returns no more than 7 `session_id` entries.
- **CX5 positive**: GWT emits no more than 5 signals in the cognitive context block.
- **CX6 positive**: No Cortex subagent output contains peer root keys such as `concept_lookup_output` inside `hippocampus_output`.
- **CX7 positive**: `hippocampus`, `concept-lookup`, `soul-check`, and `gwt-arbitrator` perform no Write/Edit/apply_patch operations.

## Negative Cases

Each negative case must be independently detectable by `scripts/lifeos-compliance-check.sh`.

### CX1 Negative: Missing Pre-Router Subagent

```text
cortex_enabled: true
hippocampus subagent returned
soul-check subagent returned
ROUTER triage begins
```

Expected: `bash scripts/lifeos-compliance-check.sh <output> cortex-cx1` exits non-zero because `concept-lookup` is missing.

### CX2 Negative: Missing GWT Arbitrator

```text
cortex_enabled: true
hippocampus subagent returned
concept-lookup subagent returned
soul-check subagent returned
[COGNITIVE CONTEXT]
- signal_id: h1
[END COGNITIVE CONTEXT]
```

Expected: `bash scripts/lifeos-compliance-check.sh <output> cortex-cx2` exits non-zero because `gwt-arbitrator` is missing.

### CX3 Negative: Missing Delimiters

```text
cortex_enabled: true
hippocampus subagent returned
concept-lookup subagent returned
soul-check subagent returned
gwt-arbitrator subagent returned
ROUTER received advisory memory, but no bracketed context block.
```

Expected: `bash scripts/lifeos-compliance-check.sh <output> cortex-cx3` exits non-zero because one or both delimiters are missing.

### CX4 Negative: Hippocampus Cap Exceeded

```yaml
cortex_enabled: true
hippocampus_output:
  retrieved_sessions:
    - session_id: s1
    - session_id: s2
    - session_id: s3
    - session_id: s4
    - session_id: s5
    - session_id: s6
    - session_id: s7
    - session_id: s8
concept_lookup_output: {}
```

Expected: `bash scripts/lifeos-compliance-check.sh <output> cortex-cx4` exits non-zero because the cap is 7.

### CX5 Negative: GWT Signal Cap Exceeded

```text
cortex_enabled: true
[COGNITIVE CONTEXT]
- signal_id: s1
- signal_id: s2
- signal_id: s3
- signal_id: s4
- signal_id: s5
- signal_id: s6
[END COGNITIVE CONTEXT]
```

Expected: `bash scripts/lifeos-compliance-check.sh <output> cortex-cx5` exits non-zero because the cap is 5.

### CX6 Negative: Isolation Breach

```text
cortex_enabled: true
hippocampus subagent input included concept_lookup_output from peer module.
```

Expected: `bash scripts/lifeos-compliance-check.sh <output> cortex-cx6` exits non-zero because a Cortex subagent received peer output.

### CX7 Negative: Read-Only Write Breach

```text
cortex_enabled: true
hippocampus subagent called Write(file_path="_meta/sessions/INDEX.md").
```

Expected: `bash scripts/lifeos-compliance-check.sh <output> cortex-cx7` exits non-zero because Cortex retrieval agents are read-only.

## Combined Check

Run the full suite against a captured transcript:

```bash
bash scripts/lifeos-compliance-check.sh evals/outputs/cortex-retrieval_<timestamp>.md cortex-retrieval
```

The combined `cortex-retrieval` scenario is equivalent to `cortex-cx1` through `cortex-cx7`.

## Linked Contracts

- `pro/AGENTS.md` Step 0.5
- `pro/agents/auditor.md` Mode 3 Programmatic Verification
- `references/compliance-spec.md` Canonical Type Legend
- `references/cortex-spec.md`
