#!/bin/bash
# scripts/wiki/setup-secondbrain.sh — v1.8.1 F1+F2+F3 deployment
# ─────────────────────────────────────────────────────────────────────────────
# One-time bootstrap for a user's second-brain repo (the vault, NOT this
# Life OS dev repo). Idempotent — safe to re-run; only writes files that
# don't exist, never overwrites.
#
# Run from inside your second-brain vault:
#
#     cd ~/path/to/SecondBrain
#     bash ~/.claude/skills/life_OS/scripts/wiki/setup-secondbrain.sh
#
# What this creates (only if missing):
#
#   wiki/log.md                       (F1: activity timeline)
#   wiki/OBSIDIAN-SETUP.md            (F2: vault setup advice)
#   wiki/.templates/wiki-entry-template.md  (F2: new-entry stub)
#   _meta/inbox/to-process/.gitkeep   (F3: drop-zone)
#   _meta/inbox/README.md             (F3: usage doc)
#
# What this DOES NOT touch:
#   - existing wiki/SCHEMA.md         (your contract; we only suggest
#                                      a "Logging convention" section to
#                                      append; we don't edit your file)
#   - existing wiki/INDEX.md          (your manual structure)
#   - existing .obsidian/             (your customizations)
#   - any existing wiki/<domain>/<entry>.md
#
# After running, you should manually:
#   - Append the "Logging convention" section to wiki/SCHEMA.md (template
#     printed at end of run)
#   - Open .obsidian/graph.json and apply the color group suggestion
#     printed at end of run (or skip if you don't use graph view)
# ─────────────────────────────────────────────────────────────────────────────

set -u

# ─── Sanity: must run inside a vault ────────────────────────────────────────
if [ ! -d "wiki" ] || [ ! -d "_meta" ]; then
  echo "ERROR: cwd doesn't look like a second-brain vault (no wiki/ or _meta/ dirs)." >&2
  echo "       cd into your vault root first, then re-run." >&2
  exit 1
fi

if [ -d ".git" ] && [ -d "scripts/hooks" ] && [ -f "SKILL.md" ]; then
  echo "ERROR: this looks like the Life OS DEV repo, not a user vault." >&2
  echo "       setup-secondbrain.sh should only run inside your second-brain vault." >&2
  exit 1
fi

VAULT_ROOT="$(pwd)"
echo "🪴 setup-secondbrain v1.8.1 — vault: $VAULT_ROOT"
echo ""

CHANGED=0
SKIPPED=0

write_if_missing() {
  local path="$1"
  local desc="$2"
  if [ -e "$path" ]; then
    echo "  skip  $path ($desc — already exists, not overwriting)"
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi
  mkdir -p "$(dirname "$path")"
  cat > "$path"
  echo "  wrote $path ($desc)"
  CHANGED=$((CHANGED + 1))
}

# ─── F1: wiki/log.md ────────────────────────────────────────────────────────
echo "── F1 · wiki activity log ──"
TODAY="$(date +%Y-%m-%d)"
NOW="$(date +%H:%M)"

write_if_missing "wiki/log.md" "wiki activity timeline" <<EOF
# Wiki · activity log

Append-only timeline of all wiki/ writes. Newest day at the bottom.

Schema source: \`wiki/SCHEMA.md\` (Logging convention section).

Action enum: \`created\` | \`updated\` | \`promoted\` | \`deprecated\` | \`merged\` | \`renamed\` | \`rejected\` | \`bulk\` (batch operations summary)

Format: \`- [HH:MM] <action> | <wiki-path> | <summary>\`

Every wiki Write/Edit/Move operation must append one line here. The
\`/inbox-process\` and \`/research\` slash commands do this automatically.
Manual edits should also append (one line per operation).

---

## ${TODAY}

- [${NOW}] bulk     | wiki/                          | setup-secondbrain.sh deployed wiki/log.md, .templates/, OBSIDIAN-SETUP.md (v1.8.1 F1+F2)
EOF
echo ""

# ─── F2: Obsidian setup advice ──────────────────────────────────────────────
echo "── F2 · Obsidian setup advice ──"

write_if_missing "wiki/OBSIDIAN-SETUP.md" "Obsidian vault setup recommendations" <<'EOF'
# Obsidian setup for the wiki/ subtree

This file documents recommended Obsidian configuration to make the wiki/
subtree a first-class graph citizen alongside the rest of your second-brain.

## Status

The vault root has `.obsidian/` configured (5 files baseline). This doc
adds wiki-specific tuning that does NOT overwrite your existing config.

## Recommended plugin set

| Plugin | Why | Source |
|---|---|---|
| **Dataview** | Query frontmatter: list all `confidence < 0.7`, sort by `last_updated`, group by `status`. The single biggest UX win for the wiki. | Community Plugins → "Dataview" |
| **Graph Analysis** | Find hub entries (high in-degree) and orphan entries (zero links). Use to plan link-density improvements. | Community Plugins → "Graph Analysis" |
| **Templater** | Spawn new wiki entries from `wiki/.templates/wiki-entry-template.md` with one keystroke (vs hand-typing frontmatter every time). | Community Plugins → "Templater" |
| Excalidraw (optional) | Hand-drawn diagrams attached to wiki entries. Use when text alone won't carry the model. | Community Plugins → "Excalidraw" |

Install via Settings → Community Plugins → Browse → search the name.

## graph.json color group suggestion

To make wiki/ nodes visually distinct in graph view, add a color group:

```jsonc
// .obsidian/graph.json — add this object to the "colorGroups" array
{
  "query": "path:wiki/",
  "color": {
    "a": 1,
    "rgb": 4737228   // blue (#4842cc); pick whatever you prefer
  }
}
```

After saving, re-open graph view — wiki/ nodes will all show in the chosen
color while the rest of your vault keeps default coloring.

## Useful Dataview queries (paste into any note)

```dataview
TABLE confidence, last_updated, status
FROM "wiki"
WHERE confidence < 0.7 AND status = "candidate"
SORT last_updated DESC
```

```dataview
TABLE length(file.outlinks) as outlinks, length(file.inlinks) as inlinks
FROM "wiki"
WHERE length(file.outlinks) = 0 AND length(file.inlinks) = 0
```
(orphan entries — no incoming or outgoing wikilinks; candidates for either
better integration or deprecation)

```dataview
TABLE last_updated
FROM "wiki"
WHERE date(today) - date(last_updated) > dur(180 days)
SORT last_updated ASC
```
(stale entries — not touched in 180+ days; review for freshness)

## Template usage

The `wiki/.templates/wiki-entry-template.md` file contains a SCHEMA-
compliant frontmatter stub + standard H2 sections. With Templater
installed, bind it to a hotkey (Settings → Templater → Hotkey) and
inserting a new wiki entry becomes one keystroke.

## What this doesn't do

- Doesn't reorganize your existing wiki/ tree
- Doesn't enforce wikilinks (you can keep using markdown `[name](path.md)`
  if you prefer; Obsidian renders both)
- Doesn't change your `.obsidian/app.json` or `.obsidian/appearance.json`
- Doesn't install plugins for you (Obsidian community plugins are user-
  consent only; you decide what runs in your vault)

## Audit your link graph

Run `bash ~/.claude/skills/life_OS/scripts/wiki/wiki-link-audit.sh` from
the vault root to generate a report at
`_meta/eval-history/wiki-link-audit-YYYY-MM-DD.md` summarizing:
- wikilink usage count
- markdown-link usage count
- broken links (point to non-existent files)
- orphan entries

Run monthly or after large edits. Pure bash; no Python dependency.
EOF
echo ""

write_if_missing "wiki/.templates/wiki-entry-template.md" "new-entry stub (Templater target)" <<'EOF'
---
title: "<one-line title; max 80 chars>"
domain: <domain-from-existing-list>
created: <%+ tp.date.now("YYYY-MM-DD") %>
last_updated: <%+ tp.date.now("YYYY-MM-DD") %>
confidence: 0.5
tags: [<domain>, <topic-tag>]
status: candidate
source: |
  - <url-or-citation>
---

# <title>

## TL;DR
<2-3 sentences>

## Key facts
- <fact-1>
- <fact-2>

## Mechanism / How it works
<paragraph>

## Origin & evolution
<paragraph>

## Counterpoints
<2-4 bullets — what's the opposing view? Even if "none found", note that.>

## Open questions
<2-4 bullets — what this entry can't answer>

## Related
- [[<other-wiki-entry>]]
- [[<other-wiki-entry>]]

## Sources
- <full URL or citation>
EOF
echo ""

# ─── F3: inbox to-process drop-zone ─────────────────────────────────────────
echo "── F3 · inbox to-process drop-zone ──"

write_if_missing "_meta/inbox/to-process/.gitkeep" "empty marker so git tracks the dir" <<EOF
EOF

write_if_missing "_meta/inbox/README.md" "inbox usage documentation" <<'EOF'
# Inbox · drop-zone for unprocessed material

Drop any `.md` file into `to-process/`. Next `/inbox-process` (or
natural-language "处理 inbox") run will scan, triage, and propose
dispositions.

## Filename convention

`YYYY-MM-DD_<short-slug>.md` — date helps with chronological scanning;
slug is just for human readability. Date prefix is convention not
requirement (the triage flow handles any `.md` name).

## Content can be anything

- Web article copy-paste (with the URL at top)
- PDF → markdown conversion output
- Voice memo transcription
- Email forward
- Random thought you want triaged later

The triage step is where structure gets imposed. Don't over-format on
the way in — the wiki frontmatter contract only applies AFTER triage
accepts an item.

## Where things go after triage

| Disposition | Result |
|---|---|
| **accept** | New `wiki/<domain>/<slug>.md` written; source moved to `archive/`; `wiki/log.md` line appended |
| **update** | Existing `wiki/<domain>/<slug>.md` amended; source moved to `archive/`; `wiki/log.md` line appended |
| **archive** | Source moved to `archive/`; no wiki write |
| **reject** | Source moved to `archive/` + `wiki/log.md` records the rejection (with reason) so future you knows it was considered and declined |
| **defer** | Source stays in `to-process/`, gets `defer_until: YYYY-MM-DD` frontmatter; future runs skip until date passes |

Nothing is ever deleted. `archive/` is the recycle bin.

## Hook integration

If `~/.claude/skills/life_OS/scripts/hooks/session-start-inbox.sh` is
registered (Life OS v1.8.1+), every Claude Code session start surfaces:

```
📥 Inbox: N items waiting (+ M deferred). Run /inbox-process or say "处理 inbox".
```

The count includes only items past their `defer_until` date (or with no
defer set). Deferred items are listed separately so you know they're
parked, not forgotten.

## What's NOT here

- `notifications.md` is system-written; don't put your own drops there
- `archive/` is for processed items; don't drop new material there
- Subdirectories under `to-process/` are NOT scanned; flatten if needed

## See also

- `wiki/SCHEMA.md` — frontmatter contract for accepted entries
- `wiki/log.md` — activity timeline
- `wiki/OBSIDIAN-SETUP.md` — vault config recommendations
EOF
echo ""

# ─── Summary + post-run instructions ────────────────────────────────────────
echo "─────────────────────────────────────────────"
echo "✅ setup-secondbrain v1.8.1 done"
echo "   wrote:   $CHANGED files"
echo "   skipped: $SKIPPED files (already existed)"
echo ""

cat <<'POST'
── Manual follow-ups ────────────────────────────────────────────────────────

1. Append the following section to your existing wiki/SCHEMA.md (we
   don't edit your file directly to avoid clobbering your customizations):

   ## Logging convention (v1.8.1 F1)

   Every write to wiki/ MUST also append one line to `wiki/log.md`:

       - [HH:MM] <action> | <wiki-path> | <summary>

   Action enum: `created` | `updated` | `promoted` | `deprecated` |
   `merged` | `renamed` | `rejected` | `bulk`

   The `/inbox-process` and `/research` slash commands do this
   automatically. Manual edits should follow the same pattern.

   See `wiki/log.md` for current format + history.

   ### research-generated tag

   Entries with `tags: [..., research-generated]` were synthesized by
   the `/research` multi-agent pipeline (default 5 agents, 8 with
   --depth deep). Their default `confidence: 0.65` reflects multi-source
   convergence; bump or trim per your judgment after review.

2. (Optional) Open `.obsidian/graph.json` and add the wiki/ color group
   block shown in `wiki/OBSIDIAN-SETUP.md` so wiki nodes stand out in
   graph view.

3. Run `bash ~/.claude/skills/life_OS/scripts/wiki/wiki-link-audit.sh`
   to generate a baseline link audit. Report goes to
   `_meta/eval-history/wiki-link-audit-YYYY-MM-DD.md`.

4. Test the inbox flow:
   - Drop a test file: `echo "# test" > _meta/inbox/to-process/$(date +%Y-%m-%d)_test.md`
   - In a fresh Claude Code session, you should see "📥 Inbox: 1 items
     waiting" in the first response.
   - Say "处理 inbox" — Claude should invoke the /inbox-process flow.

POST
exit 0
