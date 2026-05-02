#!/bin/bash
# scripts/wiki/setup-secondbrain.sh — v1.8.1 vault auto-bootstrap
# ─────────────────────────────────────────────────────────────────────────────
# Idempotent vault bootstrap. Normally invoked AUTOMATICALLY by the
# session-start-inbox.sh hook on the user's first session in a vault that
# lacks the v1.8.1 scaffolding. Users do not need to run this manually.
#
# Manual invocation (if you want to re-bootstrap or test):
#
#     cd ~/path/to/SecondBrain
#     bash ~/.claude/skills/life_OS/scripts/wiki/setup-secondbrain.sh
#
# Flags:
#   --silent   — suppress all banner / instructional output; only print
#                "wrote N files" if anything changed; emit nothing if all
#                files already exist. Used by the auto-bootstrap hook path.
#   --quiet    — alias for --silent
#
# What this creates (only if missing — never overwrites):
#   wiki/log.md                               (F1: activity timeline)
#   wiki/OBSIDIAN-SETUP.md                    (F2: vault setup guide)
#   wiki/.templates/wiki-entry-template.md    (F2: new-entry stub)
#   _meta/inbox/to-process/.gitkeep           (F3: drop-zone marker)
#   _meta/inbox/README.md                     (F3: usage doc)
#
# What this also does (only if applicable):
#   .obsidian/graph.json — adds a wiki/ color group if and only if:
#     (1) .obsidian/graph.json exists (Obsidian is configured), AND
#     (2) python3 is available (we use json module to safely parse), AND
#     (3) no existing colorGroup already targets path:wiki/
#   Behavior: backs up to .obsidian/graph.json.lifeos-backup-<ts>, applies
#   patch, validates resulting JSON; on any failure restores backup.
#
# What this DOES NOT touch:
#   - existing wiki/SCHEMA.md   (your contract; v1.8.1 log convention is
#                                self-contained inside wiki/log.md header)
#   - existing wiki/INDEX.md    (your manual structure)
#   - existing wiki/<domain>/<entry>.md (your data)
#   - .obsidian/ files OTHER than graph.json
# ─────────────────────────────────────────────────────────────────────────────

set -u

# ─── Argument parsing ──────────────────────────────────────────────────────
SILENT=0
for arg in "$@"; do
  case "$arg" in
    --silent|--quiet) SILENT=1 ;;
    --help|-h)
      sed -n '2,40p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
  esac
done

emit() { [ "$SILENT" -eq 1 ] || echo "$@"; }

# ─── Sanity: must run inside a vault ────────────────────────────────────────
# Vault = has wiki/ AND _meta/. Dev repo of Life OS = also has scripts/hooks/
# AND SKILL.md, so we refuse to bootstrap inside dev repo.
if [ ! -d "wiki" ] || [ ! -d "_meta" ]; then
  if [ "$SILENT" -eq 1 ]; then
    # Silent mode: hook called us in a non-vault dir; just return cleanly.
    exit 0
  fi
  echo "ERROR: cwd doesn't look like a second-brain vault (no wiki/ or _meta/ dirs)." >&2
  echo "       cd into your vault root first, then re-run." >&2
  exit 1
fi

if [ -d ".git" ] && [ -d "scripts/hooks" ] && [ -f "SKILL.md" ]; then
  if [ "$SILENT" -eq 1 ]; then
    exit 0
  fi
  echo "ERROR: this looks like the Life OS DEV repo, not a user vault." >&2
  echo "       setup-secondbrain.sh should only run inside your second-brain vault." >&2
  exit 1
fi

VAULT_ROOT="$(pwd)"
emit "🪴 setup-secondbrain v1.8.1 — vault: $VAULT_ROOT"
emit ""

CHANGED=0
SKIPPED=0

write_if_missing() {
  local path="$1"
  local desc="$2"
  if [ -e "$path" ]; then
    emit "  skip  $path ($desc — already exists, not overwriting)"
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi
  mkdir -p "$(dirname "$path")"
  cat > "$path"
  emit "  wrote $path ($desc)"
  CHANGED=$((CHANGED + 1))
}

# ─── F1: wiki/log.md ────────────────────────────────────────────────────────
emit "── F1 · wiki activity log ──"
TODAY="$(date +%Y-%m-%d)"
NOW="$(date +%H:%M)"

write_if_missing "wiki/log.md" "wiki activity timeline" <<EOF
# Wiki · activity log

Append-only timeline of all wiki/ writes. Newest day at the bottom.

## Convention (self-contained — does NOT depend on wiki/SCHEMA.md)

Format:

\`\`\`
- [HH:MM] <action> | <wiki-path> | <summary>
\`\`\`

Action enum: \`created\` | \`updated\` | \`promoted\` | \`deprecated\` | \`merged\` | \`renamed\` | \`rejected\` | \`bulk\` (batch operations summary)

Every wiki Write/Edit/Move operation must append one line here. The
\`/inbox-process\` and \`/research\` slash commands do this automatically.
Manual edits should also append (one line per operation).

The \`research-generated\` tag (in any wiki entry's \`tags:\`) means the
entry was synthesized by the \`/research\` multi-agent pipeline. Default
\`confidence: possible\` (5-bucket enum, v1.8.1+) reflects multi-source
convergence; bump to \`likely\` after personal review, or to \`unlikely\`
if you find counter-evidence.

---

## ${TODAY}

- [${NOW}] bulk     | wiki/                          | v1.8.1 auto-bootstrap: created log.md / OBSIDIAN-SETUP.md / .templates/wiki-entry-template.md / _meta/inbox/to-process/ + README
EOF
emit ""

# ─── F2: Obsidian setup advice ──────────────────────────────────────────────
emit "── F2 · Obsidian setup advice ──"

write_if_missing "wiki/OBSIDIAN-SETUP.md" "Obsidian vault setup recommendations" <<'EOF'
# Obsidian setup for the wiki/ subtree

This file documents recommended Obsidian configuration to make the wiki/
subtree a first-class graph citizen alongside the rest of your second-brain.

> **Auto-applied by v1.8.1**: if `.obsidian/graph.json` existed when
> `setup-secondbrain.sh` ran (auto-invoked by SessionStart hook), a wiki/
> color group was added automatically. A backup was saved to
> `.obsidian/graph.json.lifeos-backup-<timestamp>` before any edit.
> If you don't use Obsidian's graph view, this is a no-op.

## Recommended plugin set

| Plugin | Why | Source |
|---|---|---|
| **Dataview** | Query frontmatter: list all entries where `confidence` is `unlikely` or `possible`, sort by `last_tended`, group by `status`. The single biggest UX win for the wiki. | Community Plugins → "Dataview" |
| **Graph Analysis** | Find hub entries (high in-degree) and orphan entries (zero links). Use to plan link-density improvements. | Community Plugins → "Graph Analysis" |
| **Templater** | Spawn new wiki entries from `wiki/.templates/wiki-entry-template.md` with one keystroke (vs hand-typing frontmatter every time). | Community Plugins → "Templater" |
| Excalidraw (optional) | Hand-drawn diagrams attached to wiki entries. Use when text alone won't carry the model. | Community Plugins → "Excalidraw" |

Install via Settings → Community Plugins → Browse → search the name.

## What the auto-applied graph color group does

The patched `.obsidian/graph.json` now has an entry like:

```jsonc
{
  "query": "path:wiki/",
  "color": { "a": 1, "rgb": 4737228 }
}
```

Result: every node under `wiki/` shows in blue (#4842cc) in graph view,
while the rest of your vault keeps default coloring. To customize the
color, edit the `rgb` value (decimal RGB integer; pick any color you
prefer) and reload the graph view.

To revert: restore the backup file `.obsidian/graph.json.lifeos-backup-*`.

## Useful Dataview queries (paste into any note)

```dataview
TABLE confidence, last_tended, status
FROM "wiki"
WHERE (confidence = "unlikely" OR confidence = "possible") AND status = "candidate"
SORT last_tended DESC
```

```dataview
TABLE length(file.outlinks) as outlinks, length(file.inlinks) as inlinks
FROM "wiki"
WHERE length(file.outlinks) = 0 AND length(file.inlinks) = 0
```
(orphan entries — no incoming or outgoing wikilinks; candidates for either
better integration or deprecation)

```dataview
TABLE last_tended, review_by
FROM "wiki"
WHERE review_by != null AND date(review_by) <= date(today)
SORT review_by ASC
```
(entries flagged for review — `wiki-decay` re-surfaces these on next run.
Empty result = nothing currently due.)

```dataview
TABLE last_tended
FROM "wiki"
WHERE date(today) - date(last_tended) > dur(180 days)
SORT last_tended ASC
```
(stale entries — not actively reviewed in 180+ days; consider re-tending or
deprecating.)

## Template usage

The `wiki/.templates/wiki-entry-template.md` file contains a SCHEMA-
compliant frontmatter stub + standard H2 sections. With Templater
installed, bind it to a hotkey (Settings → Templater → Hotkey) and
inserting a new wiki entry becomes one keystroke.

## Audit your link graph

The `/wiki-decay` slash command (or natural-language "扫一下 wiki") walks
your wiki and proposes deprecate / merge / refresh actions; add `+ link
audit` to also include link integrity (broken `[[wikilinks]]`, broken
`[t](path.md)` markdown links, orphan entries).

For a standalone link-only pass:

- Slash command: `/wiki-link-audit`
- Natural language: "wiki link audit" / "查 wiki 哪些链接断了"

Both write to `_meta/eval-history/wiki-link-audit-YYYY-MM-DD.md`. Pure
LLM (Glob + Grep + Read) — no Python, no fragile bash regex parsing.
Run monthly or after large edits.

## What this doesn't do

- Doesn't reorganize your existing wiki/ tree
- Doesn't enforce wikilinks (you can keep using markdown `[name](path.md)`
  if you prefer; Obsidian renders both)
- Doesn't change your `.obsidian/app.json` or `.obsidian/appearance.json`
- Doesn't install plugins for you (Obsidian community plugins are user-
  consent only; you decide what runs in your vault)
EOF
emit ""

write_if_missing "wiki/.templates/wiki-entry-template.md" "new-entry stub (Templater target)" <<'EOF'
---
title: "<one-line title; max 80 chars>"
aliases: []                # alternative names — Obsidian uses these for [[wikilink]] resolution
domain: <domain-from-existing-list>
created: <%+ tp.date.now("YYYY-MM-DD") %>
last_updated: <%+ tp.date.now("YYYY-MM-DD") %>
last_tended: <%+ tp.date.now("YYYY-MM-DD") %>   # last time you actively reviewed this entry (vs cosmetic edit)
review_by: <%+ tp.date.now("YYYY-MM-DD") %>     # when wiki-decay should re-surface this entry; default = +180d
confidence: possible       # enum: impossible | unlikely | possible | likely | certain  (was 0.0–1.0 float in v1.7)
tags: [<domain>, <topic-tag>]
status: candidate          # candidate | confirmed | deprecated
sources: []                # plural array — list every URL / citation / conversation that contributed
---

# <title>

## TL;DR
<2-3 sentences>

## Key facts
<!--
Each fact may be tagged with a provenance marker:
  ^[extracted]  — quoted/paraphrased verbatim from a sources[] entry
  ^[inferred]   — your synthesis, not directly stated in any source
  ^[ambiguous]  — sources disagree or evidence is mixed
Untagged claims default to ^[extracted].
-->
- <fact-1> ^[extracted]
- <fact-2> ^[inferred]

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
<!-- Mirror the sources[] frontmatter array as a human-readable list. -->
- <full URL or citation>
EOF
emit ""

# ─── F3: inbox to-process drop-zone ─────────────────────────────────────────
emit "── F3 · inbox to-process drop-zone ──"

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
| **reject** | Source moved to `archive/` + `wiki/log.md` records the rejection (with reason) |
| **defer** | Source stays in `to-process/`, gets `defer_until: YYYY-MM-DD` frontmatter; future runs skip until date passes |

Nothing is ever deleted. `archive/` is the recycle bin.

## Hook integration

The `session-start-inbox.sh` hook (Life OS v1.8.1+) surfaces:

```
📥 Inbox: N items waiting (+ M deferred). Run /inbox-process or say "处理 inbox".
```

The count includes only items past their `defer_until` date (or with no
defer set). Deferred items are listed separately so you know they're
parked, not forgotten.

## See also

- `wiki/log.md` — activity timeline (self-contained convention; no
  SCHEMA.md edit required)
- `wiki/OBSIDIAN-SETUP.md` — vault config recommendations
EOF
emit ""

# ─── F4: auto-patch .obsidian/graph.json (best-effort, with backup) ─────────
emit "── F4 · auto-patch .obsidian/graph.json (best-effort) ──"

GRAPH_JSON=".obsidian/graph.json"
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

if [ ! -f "$GRAPH_JSON" ]; then
  emit "  skip  $GRAPH_JSON does not exist (Obsidian graph not configured) — no patch needed"
elif [ -z "$PYTHON_BIN" ]; then
  emit "  skip  $GRAPH_JSON exists but no python3 available to safely parse — manual patch needed; see wiki/OBSIDIAN-SETUP.md"
else
  GRAPH_BACKUP="${GRAPH_JSON}.lifeos-backup-$(date +%Y%m%d-%H%M%S)"
  cp "$GRAPH_JSON" "$GRAPH_BACKUP" 2>/dev/null

  PATCH_RESULT="$("$PYTHON_BIN" - "$GRAPH_JSON" <<'PYEOF' 2>&1
import json, sys, os
path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print("PARSE_ERROR:" + str(e))
    sys.exit(1)

if not isinstance(data, dict):
    print("NOT_OBJECT")
    sys.exit(1)

groups = data.get("colorGroups", [])
if not isinstance(groups, list):
    print("COLORGROUPS_NOT_LIST")
    sys.exit(1)

# Already patched?
for g in groups:
    if isinstance(g, dict) and isinstance(g.get("query"), str) and "path:wiki/" in g["query"]:
        print("ALREADY_PATCHED")
        sys.exit(0)

# Append wiki color group (blue, #4842cc = decimal 4737228)
groups.append({
    "query": "path:wiki/",
    "color": {"a": 1, "rgb": 4737228}
})
data["colorGroups"] = groups

try:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    # Re-read to validate
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)
    print("PATCHED")
except Exception as e:
    print("WRITE_ERROR:" + str(e))
    sys.exit(1)
PYEOF
)"

  case "$PATCH_RESULT" in
    PATCHED)
      emit "  wrote $GRAPH_JSON (added wiki/ color group; backup at $GRAPH_BACKUP)"
      CHANGED=$((CHANGED + 1))
      ;;
    ALREADY_PATCHED)
      emit "  skip  $GRAPH_JSON already has a wiki/ color group — no change"
      SKIPPED=$((SKIPPED + 1))
      # No backup needed; remove the just-created one
      rm -f "$GRAPH_BACKUP" 2>/dev/null
      ;;
    *)
      # Anything else = failure; restore backup
      if [ -f "$GRAPH_BACKUP" ]; then
        mv "$GRAPH_BACKUP" "$GRAPH_JSON" 2>/dev/null
      fi
      emit "  skip  $GRAPH_JSON patch failed ($PATCH_RESULT) — original restored from backup, manual patch instructions in wiki/OBSIDIAN-SETUP.md"
      ;;
  esac
fi
emit ""

# ─── Summary ─────────────────────────────────────────────────────────────────
if [ "$SILENT" -eq 1 ]; then
  # Hook-invoked path: only emit if anything changed.
  if [ "$CHANGED" -gt 0 ]; then
    echo "✨ Life OS v1.8.1 vault auto-bootstrap: wrote $CHANGED files (skipped $SKIPPED already-existing)" >&2
  fi
  exit 0
fi

# Manual-invocation path: full status block.
emit "─────────────────────────────────────────────"
emit "✅ setup-secondbrain v1.8.1 done"
emit "   wrote:   $CHANGED files"
emit "   skipped: $SKIPPED files (already existed)"
emit ""
emit "Everything is now wired. No further manual steps required."
emit ""
emit "Quick verify:"
emit "  1. Open a NEW Claude Code session in this vault"
emit "  2. First response should mention what's overdue / inbox count if any"
emit "  3. Drop a test file: echo '# test' > _meta/inbox/to-process/\$(date +%Y-%m-%d)_test.md"
emit "  4. Reload session — should see '📥 Inbox: 1 items waiting'"
emit "  5. Say '处理 inbox' to test the /inbox-process flow"
emit ""

exit 0
