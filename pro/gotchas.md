<!--
=============================================================================
pro/gotchas.md — lifeos project-level technical gotcha knowledge base
=============================================================================

Format spec: references/gotchas-spec.md
Sole writer: pro/agents/memory-keeper.md (do NOT hand-edit; bypasses dedup)
Invoked from: pro/agents/archiver.md wrap-up phase 5

Each entry under a `## <topic>` heading:

- **<short title 5-10 words>** — <behavior>. <file:line if applicable>. Fix: <workaround>. (#<ref>)

What goes here:
  ✅ Non-obvious lifeos agent/command/spec behaviors
  ✅ File-specific bugs + fixes
  ✅ "Looks X but actually Y" surprises in lifeos code/spec
  ✅ Strict invariants user emphasized
  ✅ Cross-version migration gotchas

What does NOT go here:
  ❌ Process violations → pro/compliance/violations.md
  ❌ Reusable world knowledge → _meta/wiki/
  ❌ Per-session content → _meta/sessions/
  ❌ User PII → SOUL.md (identity) or sessions/ (transient)
  ❌ Anything already in pro/CLAUDE.md / SKILL.md

Target size: ≤500 lines. Soft split threshold: 800 lines.
Initial seed (v1.8.7 ship): ≥10 entries extracted by memory-keeper seed mode
from _meta/rfc/v1.8.4-*.md, v1.8.5-cleanup-and-hardening.md, v1.8.6-*.md,
pro/compliance/violations.md (technical-root-cause subset).
=============================================================================
-->

# Project Gotchas

> Status: **awaiting first memory-keeper seed run** (v1.8.7 release session)
>
> After memory-keeper seed mode completes, this section will be replaced with topical
> `##` headings (likely: archiver, retrospective, verify-release, version-check, memory
> tree, themes, i18n, compliance, releases) each containing relevant gotcha entries.
>
> See `references/gotchas-spec.md` for entry format and `pro/agents/memory-keeper.md`
> for write protocol.
