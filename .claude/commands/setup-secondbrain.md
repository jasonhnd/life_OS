---
description: Bootstrap a user's second-brain vault with the v1.8.1+ scaffolding (wiki/log.md, OBSIDIAN-SETUP.md, .templates/, meta/queue/). Idempotent — never overwrites existing files. Replaces v1.8.4 scripts/wiki/setup-secondbrain.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[--silent]  (silent: only print 'wrote N files' if anything changed)"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
---

# /setup-secondbrain

Bootstrap a user vault with the canonical v1.8.5 scaffolding. Idempotent — files are created **only if missing**, never overwritten. Run from the vault directory (i.e. cwd is the user's second-brain root, e.g. `~/SecondBrain/`).

## Pre-flight

```bash
pwd       # should be the vault root, e.g. /Users/owner/SecondBrain
ls -la    # should look like a vault (may have wiki/, meta/, projects/, areas/, etc.)
```

If cwd doesn't look like a vault root (no `wiki/`, `meta/`, `projects/`, `areas/` and no `.git`) → emit warning `⚠️ cwd does not look like a vault root; abort and cd into vault first`.

## Files to create (only if missing)

### F1: wiki/log.md (activity timeline)
Path: `wiki/log.md`
Content (heredoc):
```markdown
# Wiki Activity Log

> Append-only timeline of wiki additions and changes. Auto-written by archiver Phase 2 and DREAM N3. Users can also manually append.

## YYYY-MM-DD

- (no entries yet)
```

### F2: wiki/OBSIDIAN-SETUP.md (vault setup guide)
Path: `wiki/OBSIDIAN-SETUP.md`
Content: Read the canonical template from the installed skill at `$HOME/.claude/skills/life_OS/scripts/wiki/templates/OBSIDIAN-SETUP.template.md` if it exists, otherwise emit a minimal stub with these sections:
- Wikilinks setting
- Graph view color groups (wiki/, projects/, areas/, meta/)
- Templates directory configuration
- Daily notes location
- Recommended plugins

### F3: wiki/.templates/wiki-entry-template.md (new-entry stub)
Path: `wiki/.templates/wiki-entry-template.md`
Content (v1.8.5 wiki schema v2 frontmatter):
```markdown
---
id: wn-<slug>
name: <human readable name>
version: "0.1.0"
classification:
  function: specify
  target_object: <what this entry is about>
  automation_mode: human_executed
  authority_level: write_candidate
  risk_level: low
  lifecycle_stage: candidate
operating_hypothesis: |
  Given <input/trigger>, this entry should produce <output/effect> within risk <r>.
reference_set:
  aspirational: []
  anti_reference: []
  boundary_case: []
  mainstream_baseline: []
  outlier: []          # mandatory: "I dislike this but it succeeds"
failure_modes:
  known: []
  warning_signs: []
  repair_actions: []
arguments_against: |
  This entry might be wrong because ...
---

# <entry title>

<body>
```

### F4: meta/queue/to-process/.gitkeep
Path: `meta/queue/to-process/.gitkeep`
Content: empty file.

### F5: meta/queue/README.md
Path: `meta/queue/README.md`
Content:
```markdown
# Queue

System processing queue + agent-to-user notifications (v1.9 Opt #2 — renamed from `meta/inbox/` to avoid confusion with the vault-root `inbox/` user drop-zone). archiver Phase 1 processes new files at every Adjourn.

- `to-process/` — drop files here; archiver moves processed → `processed/`
- `notifications.md` — system-generated notifications (maintenance overdue, etc.)

Note: this is NOT the user material drop-zone. For raw captures/research, use the vault-root `inbox/`.
```

## .obsidian/graph.json wiki color group (conditional)

If ALL three hold:
1. `.obsidian/graph.json` exists (Obsidian is configured)
2. The file is parseable JSON
3. No existing colorGroup already targets `path:wiki/`

Then merge a new color group entry (let LLM compute the merged JSON via Read → modify → Write). v1.8.4 used `python3` — v1.8.5 LLM does JSON merge directly via `Read` + `Write`.

If `python3` was the trigger gate in v1.8.4, drop that gate — LLM can parse/emit JSON natively.

## Procedure

For each F1-F5:
1. Check if path exists (`Glob`)
2. If exists → skip silently (or in non-silent mode emit `· skipped existing: <path>`)
3. If missing → create via `Write` tool

Track `WROTE` count and `SKIPPED` count.

## Output

### Non-silent mode (default)
```
── /setup-secondbrain · vault=<pwd> ──
✓ wrote wiki/log.md  (or · already exists)
✓ wrote wiki/OBSIDIAN-SETUP.md
✓ wrote wiki/.templates/wiki-entry-template.md
✓ wrote meta/queue/to-process/.gitkeep
✓ wrote meta/queue/README.md
✓ added wiki/ color group to .obsidian/graph.json  (or · skipped: no Obsidian config)

Summary: WROTE N, SKIPPED M
```

### Silent mode (--silent / --quiet)
- If anything was written: `wrote N files`
- If nothing was written: emit nothing

## When to invoke

- Manual: user runs `/setup-secondbrain` from their vault root to initialize
- Automatic: retrospective Mode 0 may invoke this on first session in a vault that lacks v1.8.5 scaffolding (replaces v1.8.4 session-start-inbox.sh auto-bootstrap behavior). retrospective MUST `cd` into vault before invoking.

## v1.8.5 changes vs v1.8.4 scripts/wiki/setup-secondbrain.sh

- v1.8.4: 887-line bash with heredoc-embedded file content, python3-based JSON merge gate, --silent flag handling
- v1.8.5: LLM Write tool for each file, LLM-native JSON merge (no python3 dep), simpler --silent logic
- v1.8.5 NEW: wiki-entry-template.md uses Stage 5 v2 schema (operating_hypothesis / reference_set 5 role slots / outlier required / arguments_against)
