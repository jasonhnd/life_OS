# User-invoked prompt · wiki-obsidian-upgrade (v1.8.2)

> One-shot batch upgrade of legacy wiki entries to v1.8.2 Obsidian-friendly
> format: callouts, wikilinks, nested tags, `kind:` field. ROUTER reads
> this when the user wants to upgrade a pre-v1.8.2 second-brain to use the
> Obsidian readability conventions defined in `references/obsidian-style.md`.

## Trigger keywords

- `升级 wiki Obsidian` / `wiki obsidian 改造` / `wiki obsidian 升级`
- `upgrade wiki to obsidian` / `convert wiki to obsidian style`
- `/wiki-obsidian-upgrade` (slash command escape hatch)

## Why upgrade

v1.8.2 introduces uniform Obsidian-friendly formatting per
`references/obsidian-style.md`:

| Field | Pre-v1.8.2 | v1.8.2 |
|---|---|---|
| Section markers | `## TL;DR` plain heading | `> [!info] TL;DR` callout |
| Counterpoints | `## Counterpoints` heading | `> [!warning]` callout (mandatory) |
| Open questions | `## Open questions` heading | `> [!question]` callout |
| Decision rationale | `## Why` heading | `> [!important]` callout |
| Lesson statement | `## One-line` heading | `> [!quote]` callout |
| Method "when to use" | `## When` heading | `> [!tip]` callout |
| In-vault references | `[stablecoin](../fintech/stablecoin-b2b.md)` | `[[stablecoin-b2b]]` |
| Tags | `tags: [fintech, stablecoin, b2b]` | `tags: [fintech/stablecoin, fintech/b2b]` |
| `kind:` field | (missing) | `kind: knowledge\|method\|decision\|lesson\|config` |

External URLs `[text](https://...)` stay as standard markdown — only
in-vault `[name](path.md)` links get rewritten to `[[wikilinks]]`.

## Pre-flight

1. Verify cwd is a second-brain repo (`_meta/` + `wiki/` exist). If not,
   refuse with "/wiki-obsidian-upgrade only runs in a second-brain vault."
2. `Glob` `wiki/**/*.md` (exclude `INDEX.md`, `SCHEMA.md`,
   `OBSIDIAN-SETUP.md`, `log.md`, `.templates/**`).
3. For each file, `Read` first 60 lines to detect:
   - Has `kind:` frontmatter? (already v1.8.2, skip)
   - Has any `> [!` callout? (partially upgraded — flag)
   - Uses `[name](path.md)` for in-vault links? (needs wikilink conversion)
   - Tags are flat (no `/`) ? (needs nesting)
   - Has H2 sections that should become callouts (TL;DR / Counterpoints /
     Open questions / etc.)?

## Plan preview (BEFORE writing anything)

Output a single proposal table:

```
🔄 wiki-obsidian-upgrade plan — N entries scanned

| # | path | needs | proposed kind | notes |
|---|------|-------|---------------|-------|
| 1 | wiki/fintech/stablecoin-b2b.md | callouts(3) + wikilinks(2) + nested-tags + kind | knowledge | ready to upgrade |
| 2 | wiki/methodology/decision-frameworks.md | callouts(2) + kind | method | already uses wikilinks |
| 3 | wiki/personal/2026-04-15-job-decision.md | callouts(2) + kind + outcome_review_date | decision | needs decision-template fields |
| 4 | wiki/lessons/dont-trust-fri-deploys.md | callouts(2) + kind + recurrence | lesson | needs lesson-template fields |
| 5 | wiki/system/openclaw-config.md | callouts(1) + kind | config | minimal change |
| ...

Total to upgrade: K
Total skipped (already v1.8.2): J
Total needing user input on `kind:`: U

Confirm? Type "all" / "1,3,5" / "edit 3 kind=knowledge" / "skip 2" / "no"
```

Wait for explicit user confirmation. **Do NOT execute on assumed
agreement.**

## Per-entry transformations

For each confirmed row, apply transformations in this order:

### A. Add `kind:` to frontmatter

Detect kind from existing content:
- Has "## Steps" / "## When to use" → `method`
- Has "## Options considered" / "## Decision rationale" → `decision`
- Has "## Trigger event" / "## Lesson" or filename starts with date → `lesson`
- Has "## Current value" + verbatim config snippet → `config`
- Default → `knowledge`

Ask user if ambiguous.

### B. Add v1.8.2 frontmatter fields (if missing)

```yaml
---
title: <existing>
aliases: []                  # add empty array if missing
domain: <existing>
kind: <inferred>             # NEW
created: <existing or today>
last_updated: <existing or today>
last_tended: <existing last_updated>     # NEW · backfill from last_updated
review_by: <last_tended + 180d>          # NEW · default
confidence: <existing or "possible">      # if float, map per migrate-confidence
tags: <converted to nested style>
status: <existing or "candidate">
sources: <existing array, or wrap legacy `source:` scalar into array>
---
```

If `confidence` is still a float, suggest running `/migrate-confidence` afterward.

### C. Convert in-vault markdown links to wikilinks

For each `[name](relative/path.md)` where the target resolves to a
`wiki/**/*.md` file:

```
[stablecoin](../fintech/stablecoin-b2b.md)
↓
[[stablecoin-b2b]]
```

For `[name](relative/path.md#section)`:

```
[link](path.md#section)
↓
[[basename#section]]
```

External URLs `[text](https://...)` UNCHANGED.

### D. Wrap H2 sections in callouts

Detect well-known H2 headings and wrap their content in matching callouts:

| H2 heading | Callout |
|---|---|
| `## TL;DR` | `> [!info] TL;DR` |
| `## Counterpoints` | `> [!warning] Counterpoints` |
| `## Open questions` | `> [!question]` |
| `## Mandatory section` | `> [!warning]` |
| `## When to use` | `> [!tip] When to use` |
| `## Decision rationale` | `> [!important]` |
| `## Lesson` (one-line) | `> [!quote]` |
| `## Failure modes` | `> [!warning]` |
| `## Side effects` | `> [!warning]` |

For other H2 headings, keep as plain headings (`## Mechanism`, `## Sources`,
`## Related`, etc.).

### E. Convert flat tags to nested

If `tags: [fintech, stablecoin, b2b]`, ask user how to nest:
- `[fintech/stablecoin, fintech/b2b]`?
- Or `[fintech, fintech/stablecoin, fintech/b2b]`?

If `domain: fintech` is set in frontmatter, default to `<domain>/<topic>` style.

### F. Bump `last_tended` to today

This counts as a tending action (you actively reviewed the entry to
upgrade it). Bump `last_tended` and append a `wiki/log.md` line:

```
- [HH:MM] updated  | wiki/<domain>/<slug>.md | obsidian-upgrade: kind=<X>, +callouts, +wikilinks, +nested-tags
```

## Post-upgrade report

```
✅ wiki-obsidian-upgrade complete

  upgraded:    K entries
  skipped:     J entries (already v1.8.2)
  needs_help:  H entries (user couldn't decide kind / tag nesting)
  failed:      F entries (path / parse error; details below)

  Per-transform counts:
    + kind: field added:        K
    + wikilinks converted:      W (was [name](path.md))
    + callouts wrapped:         C (was plain ## headings)
    + nested tags adjusted:     T
    + last_tended bumped:       K

Migration log appended to wiki/log.md (K + H entries).

Recommended next steps:
  - If you have legacy float `confidence:`, run /migrate-confidence next
  - Open Obsidian and verify a few upgraded entries render properly
  - If a callout looks wrong, manually edit (transformation is best-effort)
```

## Failure modes

- **wiki/log.md write fails**: rollback that entry's edit; report; continue
- **frontmatter unparseable**: skip; ask user to fix manually first
- **Cannot resolve [name](path.md) target**: leave as-is; report as
  "broken link, fix manually"
- **Ambiguous kind**: defer to next run; mark with `kind: needs_review`
  + flag in `wiki/log.md`

## Idempotency

Re-running this prompt is safe:
- Entries already on v1.8.2 (have `kind:`) are skipped
- Already-converted callouts not re-wrapped
- Already-nested tags not double-nested
- The only thing that changes on re-run: `last_tended` is NOT re-bumped
  (skip happens before tend bump)

## Rollback

Before running, the user should commit the vault state:

```bash
git -C ~/path/to/second-brain status   # confirm clean tree
git -C ~/path/to/second-brain commit -am "pre-wiki-obsidian-upgrade snapshot"
```

If the upgrade produces unexpected transformations, `git checkout -- wiki/`
restores all entries.

## Companion prompts

- `/migrate-confidence` — float `confidence:` → 5-bucket enum
- `/migrate-to-wikilinks` — older v1.8.0 R-1.8.0-013 wikilink-only
  migration; this prompt supersedes it (does wikilinks + callouts +
  nested tags + kind in one pass)

## Out of scope

This prompt only upgrades wiki entries. Non-wiki files (sessions, SOUL
snapshots, DREAM entries, eval-history reports, compliance logs, method
library entries) follow Obsidian style for new writes (per HARD RULE
#11) but are not batch-upgraded — they migrate organically as the
user touches them.
