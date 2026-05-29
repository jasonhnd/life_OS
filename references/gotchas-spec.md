---
spec_id: gotchas-spec.v1
description: Specification for `pro/gotchas.md` — the project-level technical gotcha knowledge base. Each entry records "踩过的坑 + 文件路径 + 修复方法" so ROUTER and downstream agents can short-circuit known issues. Distinct from `pro/compliance/violations.md` (process violations) and `meta/sessions/` (per-session record). Pattern borrowed from tinyhumansai/openhuman `.claude/memory.md`; lifeos adaptation is md-only and writes by `memory-keeper` agent.
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, .claude/memory.md (259 lines flat single file with topical grouping)
introduced_in: v1.8.7
referenced_by:
  - pro/agents/memory-keeper.md
  - pro/agents/archiver.md (wrap-up phase 5)
  - SKILL.md (ROUTER pre-task scan, future)
---

# Gotchas Specification v1

`pro/gotchas.md` is lifeos's **project-level technical gotcha knowledge base** — a single flat file collecting non-obvious behaviors, file-specific bugs, and corrective workarounds that any new session should know before acting.

## Positioning vs other knowledge stores

| Store | What it records | Lifecycle |
|-------|----------------|-----------|
| `meta/sessions/<sid>.md` | Per-session timeline + decisions made | One file per session, archived |
| `pro/compliance/violations.md` | Process violations (A1/A2/A3/B/C/D/E/F + F1-F17) | Append-only audit log |
| `meta/wiki/<topic>.md` | Reusable world knowledge ("NPO lending has no 貸金業法 exemption") | Manually curated |
| `meta/concepts/<concept>.md` | Synaptic graph nodes (Cortex) | Hippocampus activates them |
| **`pro/gotchas.md`** | **Project technical坑 + file path + fix** | **Continuously extracted by memory-keeper** |

Gotchas are **not** violations (those go to `compliance/violations.md`). Gotchas are **not** reusable world knowledge (that goes to `meta/wiki/`). Gotchas are **dev-internal short-circuit memory**: "next time we touch X, here's what to know first".

## File location and scope

- **Path**: `pro/gotchas.md` (single file, dev repo root area)
- **Language**: English single-language (project-internal dev knowledge base — three-language mirroring not applied per DR-03 in v1.8.7 RFC)
- **Size budget**: target ≤500 lines; soft threshold for sub-file split is 800 lines
- **Audience**: ROUTER + memory-keeper + any agent before major task on a known-touched area

## Entry format

Each gotcha is a single bullet under a topical `##` section:

```markdown
## <Topic / Component>

- **<Short title (5-10 words)>** — <Behavior description>. <File path:line> if applicable. Fix: <workaround or correct approach>. (#<ref: PR/issue/RFC>)
```

### Field rules

| Field | Required | Notes |
|-------|----------|-------|
| Short title | ✅ | First 5-10 words; grep-friendly |
| Behavior description | ✅ | What surprises / what fails / what's non-obvious |
| File path:line | when applicable | Use `src/path:LN` format; omit if cross-cutting |
| Fix | ✅ | The workaround OR "no workaround, escalate to X" |
| Reference | ✅ | PR / issue / RFC / commit sha — must point to durable artifact |

### Example entries

```markdown
## archiver

- **archiver Phase 2 candidate scan blocks on missing wiki** — When `meta/wiki/` directory doesn't exist, Phase 2 hangs instead of skipping. Fix: archiver first creates the directory if missing. (#v1.8.7-C6-task-2d)

- **archiver wrap-up phase 5 (memory-keeper) is mandatory after v1.8.7** — Skipping phase 5 = missing gotchas extraction. Fix: archiver Mode 0 enforces phase 5 even on short sessions; gotchas table can be empty but phase must run. (#RFC-v1.8.7)
```

## What to capture (memory-keeper input rules)

Capture:
- ✅ Non-obvious behaviors of lifeos's own agents / commands / spec interactions
- ✅ File-specific bugs and their workarounds
- ✅ "Looked X but actually Y" surprises in the codebase or runtime
- ✅ Strict invariants user explicitly emphasized
- ✅ Cross-version migration gotchas

Do NOT capture:
- ❌ One-off session content (use sessions/ for that)
- ❌ Process violations (use compliance/violations.md)
- ❌ Reusable world knowledge unrelated to lifeos itself (use meta/wiki/)
- ❌ User personal information (use SOUL.md if it's identity-level; sessions/ if it's transient)
- ❌ Anything already documented in pro/CLAUDE.md or other authoritative source

## How to update

memory-keeper agent is the **sole writer** of `pro/gotchas.md`. Direct human edits are allowed but discouraged — they bypass dedup and may create entries that don't follow format.

Update flow (memory-keeper invoked from archiver wrap-up phase 5):

1. memory-keeper reads current `pro/gotchas.md`
2. Scans current session for new gotcha candidates
3. For each candidate:
   - Dedup against existing entries (substring match on short title)
   - Verify entry format compliance
   - Append to appropriate `##` section (create section if needed)
4. Outputs report: N candidates found, M deduplicated, K appended
5. Returns to archiver phase 5 completion

## Initial seed (v1.8.7 ship requirement)

Per RFC §7 退出标准, memory-keeper's first run on v1.8.7 release session must produce ≥10 seed entries by scanning:

- `_meta/rfc/v1.8.5-cleanup-and-hardening.md`
- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md`
- `_meta/rfc/v1.9-second-brain-structure-optimization.md`
- `pro/compliance/violations.md` (filter: entries where root cause is technical, not pure process)

Seed entries are still gotchas (technical), not process violations.

## Dedup and retention

- **Dedup**: substring match on short title — if new candidate's short title is a substring of existing, merge into existing (extend behavior description or add new file path) rather than create duplicate
- **Retention**: gotchas don't auto-expire. They get removed only when the underlying issue is permanently fixed in the codebase AND the fix is verified
- **Removal procedure**: memory-keeper marks entry as `<!-- removed v1.X.Y: fixed in <ref> -->` (keep in file as comment for audit), or moves to a future `pro/gotchas-resolved.md` archive

## Failure modes

| Failure | Detection | Recovery |
|---------|-----------|----------|
| memory-keeper writes duplicate entry | AUDITOR Mode 7 M7-1 (existence check + dedup integrity check) | memory-keeper rerun with dedup-strict flag |
| Entry has no `(#<ref>)` reference | AUDITOR Mode 7 M7-1 | memory-keeper rejects entry; archiver phase 5 fails |
| File grows beyond 800 lines | manual review | split by section into sub-files (rare; expected to happen v1.9+ at earliest) |
| Format drift (entry not matching schema) | AUDITOR Mode 7 M7-1 | memory-keeper reformats on next run |

## Related specs

- `pro/agents/memory-keeper.md` — agent definition
- `references/compliance-spec.md` — distinguish gotchas from violations
- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.1 C6 — origin of this spec
