---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

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
- **CX8 positive (v1.7.2)**: Hippocampus Wave 1 uses the Hermes Local
  `session_search` integration through the INDEX-only helper, with
  `source_scope: _meta/sessions/INDEX.md`.
- **CX9 positive (v1.7.2)**: Hippocampus returns no more than 3
  `activated_methods`, only from confirmed/canonical method records, and
  does not paste full method bodies into `[COGNITIVE CONTEXT]`.
- **CX10 positive (v1.7.2)**: Method extraction evidence flows through
  `methods_used` / `methods_discovered` session frontmatter; retrieval agents
  may consume it but may not create, promote, or edit method files.
- **CX11 positive (v1.7.3)**: Cortex subagent outputs may be display-compressed
  inline by ROUTER, but wrappers include audit-trail links and preserve signal
  IDs, method activations, blockers, and side effects. The Hermes-vendored
  `tools/context_compressor.py` was removed in v1.7.3 (0 callers); ROUTER does
  the compression in-context.

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

## v1.7.2 Extended Negative Cases

These cases extend CX1-CX7 for Wave 4.F. They are scenario requirements even
if the shell checker has not yet grown individual `cortex-cx8` through
`cortex-cx11` entry points.

### CX8 Negative: Hermes session_search integration missing

```text
cortex_enabled: true
hippocampus Wave 1 read _meta/sessions/INDEX.md and used grep/LLM scanning only.
No scripts/lib/cortex/hippocampus_wave1_search.py call.
No tools/session_search.py / SQLite FTS5 integration evidence.
```

Expected: fail CX8 because v1.7.2 requires the Hermes Local `session_search`
path for Wave 1 candidate retrieval.

### CX8 Negative: session_search scope breach

```yaml
cortex_enabled: true
hippocampus_wave1_search:
  source_scope: "_meta/journal/*.md"
  db_path: "_meta/cache/session-search.db"
hippocampus_output:
  retrieved_sessions:
    - session_id: s1
```

Expected: fail CX8 and CX6. Hippocampus Wave 1 may use only
`_meta/sessions/INDEX.md` through the in-memory INDEX-only helper; raw journal
content and persistent FTS caches belong to general tooling, not the isolated
retrieval subagent.

### CX8 Positive: INDEX-only FTS5 candidate retrieval

```yaml
cortex_enabled: true
hippocampus tool_call:
  command: python scripts/lib/cortex/hippocampus_wave1_search.py --query "architecture Plan B" --limit 50 --json
hippocampus_wave1_search:
  db_path: ":memory:"
  source_scope: "_meta/sessions/INDEX.md"
  sources_indexed: 42
  count: 9
hippocampus_output:
  retrieved_sessions:
    - session_id: codex-20260420-1403
      wave: 1
```

Expected: PASS for CX8.

### CX9 Negative: Method activation cap exceeded

```yaml
cortex_enabled: true
hippocampus_output:
  activated_methods:
    - method_id: m1
    - method_id: m2
    - method_id: m3
    - method_id: m4
```

Expected: fail CX9 because the cap is 3 activated methods.

### CX9 Negative: Tentative or full method body leaked

```yaml
cortex_enabled: true
hippocampus_output:
  activated_methods:
    - method_id: evidence-laddering
      status: tentative
      full_body: "## Steps..."
[COGNITIVE CONTEXT]
Known Method full text: ...
[END COGNITIVE CONTEXT]
```

Expected: fail CX9 and CX6. Cortex retrieval may emit concise method signals,
but tentative methods and full method bodies are not allowed in the cognitive
context; DISPATCHER performs full method injection later.

### CX9 Positive: Confirmed method co-activation

```yaml
cortex_enabled: true
hippocampus_output:
  retrieved_sessions:
    - session_id: s1
      applicable_signals:
        - signal_type: method_match
          detail: "evidence-laddering applied in a prior similar decision"
  activated_methods:
    - method_id: evidence-laddering
      name: Evidence Laddering
      activation_strength: 0.78
      reason: "Matched retrieved session methods_used and related concepts."
      source: session_frontmatter
[COGNITIVE CONTEXT]
- signal_id: m1
  type: method_match
  summary: "Evidence Laddering may apply; dispatcher should evaluate fit."
[END COGNITIVE CONTEXT]
```

Expected: PASS for CX9.

### CX10 Negative: Method extraction performed during retrieval

```text
cortex_enabled: true
hippocampus wrote _meta/methods/_tentative/evidence-laddering.md
concept-lookup updated _meta/methods/INDEX.md
```

Expected: fail CX7 and CX10. Method extraction writes are ARCHIVER Phase 2
responsibility; retrieval agents may only read extraction evidence from
session frontmatter and existing confirmed/canonical method files.

### CX10 Negative: methods_discovered ignored as extraction evidence

```yaml
cortex_enabled: true
_meta/sessions/s1.md:
  methods_discovered: [evidence-laddering]
_meta/methods/INDEX.md:
  confirmed:
    - evidence-laddering
hippocampus_output:
  retrieved_sessions:
    - session_id: s1
  activated_methods: []
```

Expected: fail CX10 when the method index is present and the confirmed method
matches a retrieved session's `methods_discovered` frontmatter.

### CX10 Positive: extraction evidence consumed read-only

```yaml
cortex_enabled: true
hippocampus_output:
  retrieved_sessions:
    - session_id: s1
      summary: "Prior session discovered the Evidence Laddering method."
  activated_methods:
    - method_id: evidence-laddering
      source: session_frontmatter
  meta:
    degraded: false
```

Expected: PASS for CX10 if no Cortex retrieval agent writes under
`_meta/methods/`.

### CX11 Negative: Compressed paste drops Cortex evidence

```text
cortex_enabled: true
paste_mode: compressed
compression_source: tools/context_compressor.py
hippocampus paste: "Memory checked; some sessions were relevant."
No audit_trail link.
No retrieved session ids, activated_methods, degradation status, or signal ids.
```

Expected: fail CX11 and the R11 audit-trail checks. Compression may shrink the
display paste, but it must preserve review-critical Cortex evidence and link to
the full runtime JSON.

### CX11 Negative: Cognitive context replaces subagent wrappers

```text
cortex_enabled: true
[COGNITIVE CONTEXT]
- signal_id: s1
[END COGNITIVE CONTEXT]
ROUTER did not show wrapped hippocampus/concept-lookup/soul-check/gwt outputs.
```

Expected: fail CX11. The GWT block is downstream synthesis; it cannot replace
the subagent transparency wrappers.

### CX11 Positive: compressed wrappers plus grounded GWT block

```text
cortex_enabled: true
## subagent output - hippocampus
audit_trail: _meta/runtime/sid/hippocampus.json
paste_mode: compressed
compression_source: tools/context_compressor.py
retrieved_sessions: [s1, s2]
activated_methods: [evidence-laddering]

[COGNITIVE CONTEXT]
- signal_id: s1
  source: hippocampus_output
- signal_id: m1
  source: hippocampus_output.activated_methods
[END COGNITIVE CONTEXT]
```

Expected: PASS for CX11.

## Combined Check

Run the full suite against a captured transcript:

```bash
bash scripts/lifeos-compliance-check.sh evals/outputs/cortex-retrieval_<timestamp>.md cortex-retrieval
```

The base automated `cortex-retrieval` checker currently covers `cortex-cx1`
through `cortex-cx7`; Wave 4.F extends the scenario with CX8-CX11 above and
the checker should grow matching entry points when implementation ownership
moves beyond the scenario files.

## Linked Contracts

- `pro/AGENTS.md` Step 0.5
- `pro/agents/auditor.md` Mode 3 Programmatic Verification
- `pro/agents/hippocampus.md` Method Co-Activation and Wave 1 search
- `scripts/lib/cortex/hippocampus_wave1_search.py`
- `tools/session_search.py`
- `tools/context_compressor.py`
- `references/compliance-spec.md` Canonical Type Legend
- `references/cortex-spec.md`
- `references/method-library-spec.md`
