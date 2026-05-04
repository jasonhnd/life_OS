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

## Recommended plugin set (v1.8.2 expanded)

| Plugin | Why | Source |
|---|---|---|
| **Dataview** | Query frontmatter: list all entries where `confidence` is `unlikely` or `possible`, sort by `last_tended`, group by `kind`. **The single biggest UX win for the wiki.** | Community Plugins → "Dataview" |
| **Templater** | Spawn new wiki entries from one of the 5 templates in `wiki/.templates/` with one keystroke. Bind each template (knowledge/method/decision/lesson/config) to a separate hotkey. | Community Plugins → "Templater" |
| **Graph Analysis** | Find hub entries (high in-degree) and orphan entries (zero links). Use to plan link-density improvements. | Community Plugins → "Graph Analysis" |
| **Linter** | Auto-format wiki entries on save: enforce frontmatter field order, blank lines around headings, list indentation. Stops "is the YAML valid?" friction. | Community Plugins → "Linter" |
| **Iconize** (formerly Obsidian Icon Folder) | Per-folder icons in file explorer (e.g. 📚 for `wiki/`, 🧠 for `_meta/`, 📥 for `_meta/inbox/`). Tiny but noticeable readability win. | Community Plugins → "Iconize" |
| **Periodic Notes** | If you also keep daily/weekly notes alongside wiki, this manages them. Optional. | Community Plugins → "Periodic Notes" |
| **Tag Wrangler** | Rename a tag across all entries safely (e.g. `fintech` → `fintech/stablecoin`). Pairs with the v1.8.2 nested-tag style. | Community Plugins → "Tag Wrangler" |
| **MetaEdit** (or built-in Properties view) | Edit frontmatter via UI rather than YAML hand-editing. Obsidian 1.4+ has a native Properties view that handles this; MetaEdit is the older alternative. | Community Plugins → "MetaEdit" |
| **Excalidraw** (optional) | Hand-drawn diagrams attached to wiki entries. Use when text alone won't carry the model. | Community Plugins → "Excalidraw" |

Install via Settings → Community Plugins → Browse → search the name.

## v1.8.2 readability features (in templates by default)

The wiki entry templates use these Obsidian-native features for human readability:

### 1. Callouts (admonitions)

```markdown
> [!info] TL;DR
> Short summary as a styled box.

> [!warning] Mandatory section
> Counter-bias HARD RULE...

> [!tip] When to use
> Trigger condition...

> [!question]
> Open questions

> [!important]
> The decision in plain language

> [!quote] One-line lesson
> Imperative form
```

Available types: `note`, `info`, `tip`, `success`, `question`, `warning`, `failure`,
`danger`, `bug`, `example`, `quote`, `important`. Each renders with a distinct
icon and color in Obsidian's reading view.

### 2. Wikilinks (preferred over markdown links inside the vault)

| Style | Use when |
|---|---|
| `[[entry-name]]` | Standard intra-vault link; counts toward graph |
| `[[entry-name\|display]]` | Alias display text |
| `[[entry-name#Section]]` | Link to specific H2 section |
| `[[entry-name#^block-id]]` | Link to specific block (Obsidian native) |
| `![[entry-name]]` | **Embed** the other entry inline |
| `![[image.png]]` | Embed image stored in the vault |
| `[Anthropic blog](https://...)` | External URL — keep markdown style |

### 3. Mermaid diagrams (native in Obsidian)

````markdown
```mermaid
flowchart LR
    A[Decision] --> B{Confidence?}
    B -->|likely| C[Execute]
    B -->|possible| D[Verify first]
    B -->|unlikely| E[Defer]
```
````

### 4. Nested tags

```yaml
tags: [fintech/stablecoin, fintech/b2b]
```

Obsidian renders nested tags as a tree in the tag pane and `#fintech/*`
queries them all. Better than flat `[fintech, stablecoin, b2b]` because
the hierarchy survives.

### 5. Footnotes

```markdown
This claim was originally proposed in 1972[^einstein-72] but later refined[^bell-90].

[^einstein-72]: Einstein, A. (1972). *Title*. Source URL.
[^bell-90]: Bell, J. (1990). *Title*. Source URL.
```

### 6. CSS classes (advanced)

Add `cssclasses: [lesson, important]` to frontmatter and define styles in
`.obsidian/snippets/lifeos.css` to make lesson entries visually distinct
from knowledge entries. Optional — most users skip this.

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

### Low-confidence candidates (most useful daily query)

```dataview
TABLE kind, confidence, last_tended, status
FROM "wiki"
WHERE (confidence = "unlikely" OR confidence = "possible") AND status = "candidate"
SORT last_tended DESC
```

### Orphan entries

```dataview
TABLE length(file.outlinks) as outlinks, length(file.inlinks) as inlinks, kind
FROM "wiki"
WHERE length(file.outlinks) = 0 AND length(file.inlinks) = 0
SORT kind ASC
```
(no incoming or outgoing wikilinks — candidates for either better integration
or deprecation)

### Due for review (priority queue)

```dataview
TABLE kind, last_tended, review_by
FROM "wiki"
WHERE review_by != null AND date(review_by) <= date(today)
SORT review_by ASC
```
(entries flagged for review — `/wiki-decay` re-surfaces these on next run.
Empty result = nothing currently due.)

### Stale entries (180+ days untouched)

```dataview
TABLE kind, last_tended
FROM "wiki"
WHERE date(today) - date(last_tended) > dur(180 days)
SORT last_tended ASC
```

### v1.8.2 — All open decisions awaiting outcome

```dataview
TABLE decision_date, outcome_review_date
FROM "wiki"
WHERE kind = "decision" AND status = "open"
SORT outcome_review_date ASC
```
(every decision that hasn't been closed-with-outcome — review when its
`outcome_review_date` arrives to log what actually happened vs the
Counterpoints raised at decision time)

### v1.8.2 — Method usage trail

```dataview
TABLE times_used, last_used, status
FROM "wiki"
WHERE kind = "method"
SORT times_used DESC
```
(see which methods you actually rely on; `times_used: 0` after 6 months =
candidate for deprecation; high `times_used` candidates for `status: proven`)

### v1.8.2 — Lesson recurrence (which mistakes you keep almost-making)

```dataview
TABLE recurrence, trigger_event
FROM "wiki"
WHERE kind = "lesson" AND recurrence > 1
SORT recurrence DESC
```
(if a lesson keeps re-occurring, you haven't internalized it yet — escalate)

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
- Doesn't change your `.obsidian/app.json` or `.obsidian/appearance.json`
- Doesn't install plugins for you (Obsidian community plugins are user-
  consent only; you decide what runs in your vault)
- Doesn't auto-rewrite legacy entries to use callouts/wikilinks/nested-tags
  — for batch upgrade run `/wiki-obsidian-upgrade` (v1.8.2)

## v1.8.2 readability conventions (preferred but not enforced)

- **Wikilinks over markdown links** for in-vault navigation
  (`[[entry]]` not `[name](path.md)`) — for graph traversal
- **Callouts** (`> [!info]`, `> [!warning]`, etc.) for TL;DR / Counterpoints / Open questions
- **Nested tags** (`fintech/stablecoin`) over flat tags — for tag tree
- **Mermaid blocks** for mechanism diagrams
- **Footnotes** for fine-grained citations inside paragraphs
- **`kind:` frontmatter field** to classify entries (knowledge / method / decision / lesson / config)
EOF
emit ""

write_if_missing "wiki/.templates/wiki-entry-template.md" "new-entry stub · knowledge kind (Templater target)" <<'EOF'
---
title: "<one-line title; max 80 chars>"
aliases: []                # alternative names — Obsidian uses these for [[wikilink]] resolution
domain: <domain-from-existing-list>
kind: knowledge            # knowledge | method | decision | lesson | config (v1.8.2 — drives wiki-decay categorization)
created: <%+ tp.date.now("YYYY-MM-DD") %>
last_updated: <%+ tp.date.now("YYYY-MM-DD") %>
last_tended: <%+ tp.date.now("YYYY-MM-DD") %>   # last time you actively reviewed this entry (vs cosmetic edit)
review_by: <%+ tp.date.now("YYYY-MM-DD") %>     # when wiki-decay should re-surface this entry; default = +180d
confidence: possible       # enum: impossible | unlikely | possible | likely | certain
tags: [<domain>/<sub-topic>]   # nested-tag style for Obsidian tag tree (e.g. fintech/stablecoin)
status: candidate          # candidate | confirmed | deprecated
sources: []                # plural array — list every URL / citation / conversation that contributed
cssclasses: []             # optional Obsidian CSS classes for per-entry styling
---

# <title>

> [!info] TL;DR
> <2-3 sentence summary — Obsidian renders this as a callout box>

## Key facts

> [!note] Provenance tagging
> Each fact bullet may carry one marker:
> - `^[extracted]` — quoted/paraphrased from a `sources[]` entry
> - `^[inferred]` — your synthesis, not directly stated
> - `^[ambiguous]` — sources disagree or evidence is mixed
> Untagged claims default to `^[extracted]`.

- <fact-1> ^[extracted]
- <fact-2> ^[inferred]
- <fact-3> ^[ambiguous]

## Mechanism / How it works

<paragraph explaining how the thing works>

<!-- Optional: Obsidian renders mermaid blocks natively. Delete if not needed. -->

```mermaid
flowchart LR
    A[Input] --> B[Process]
    B --> C[Output]
```

## Origin & evolution

<1-2 paragraphs on history; who invented this, when, why it matters>

## Counterpoints

> [!warning] Mandatory section — even if "none found"
> Counter-confirmation-bias HARD RULE. If all sources converge, write that
> explicitly: "No substantive opposition found in this run; re-test in 3 months."

- <counterpoint-1>
- <counterpoint-2>

## Open questions

> [!question]
> - <question-1 the entry can't answer>
> - <question-2 the entry can't answer>

## Related

<!--
v1.8.2 — Prefer Obsidian wikilinks over markdown links for in-vault navigation:
  ✅  [[wiki-entry-name]]                  ← Obsidian native, graph-aware
  ✅  [[wiki-entry-name|display label]]    ← with custom display text
  ✅  [[wiki-entry-name#Section heading]]  ← link to section
  ❌  [text](path/to/wiki-entry-name.md)   ← works but no graph traversal

External URLs use standard markdown:
  ✅  [Anthropic blog post](https://www.anthropic.com/research/...)
-->

- [[<other-wiki-entry>]]
- [[<other-wiki-entry>|alternative display name]]

## Sources

<!-- Mirror the sources[] frontmatter array as a human-readable list. -->

1. <full URL or citation>
2. <full URL or citation>

## Footnotes

<!-- Obsidian renders [^1]-style footnotes natively. Useful for fine-grained citations inside paragraphs. -->

[^1]: <footnote text>
EOF
emit ""

# ─── v1.8.2 · 4 specialized templates by `kind:` ────────────────────────────
# Different wiki entry kinds need different shapes. Templater can bind each
# template to its own hotkey, or you can copy-paste manually.

write_if_missing "wiki/.templates/method-template.md" "method/SOP template" <<'EOF'
---
title: "<method name>"
aliases: []
domain: <domain>
kind: method                       # v1.8.2 kind enum
created: <%+ tp.date.now("YYYY-MM-DD") %>
last_updated: <%+ tp.date.now("YYYY-MM-DD") %>
last_tended: <%+ tp.date.now("YYYY-MM-DD") %>
review_by: <%+ tp.date.now("YYYY-MM-DD") %>
confidence: possible
tags: [<domain>/method]
status: tentative                  # tentative | proven | deprecated
sources: []
times_used: 0                      # increment each time you actually run this method
last_used: null                    # ISO date of last application
inputs: []                         # what you need before starting
outputs: []                        # what you get when done
---

# <method name>

> [!tip] When to use
> <2-3 lines on the trigger condition — what situation does this method fit?>

## Steps

1. <step-1>
2. <step-2>
3. <step-3>

## Failure modes

> [!warning]
> - <failure-1: when this method does NOT work>
> - <failure-2>

## Variants

- <variant-1>
- <variant-2>

## Related methods

- [[<other-method>]]
- [[<other-method>]]

## Sources

1. <citation>
EOF
emit ""

write_if_missing "wiki/.templates/decision-template.md" "decision template (with Counterpoint trail)" <<'EOF'
---
title: "<decision title — what was decided>"
aliases: []
domain: <domain>
kind: decision                     # v1.8.2 kind enum
created: <%+ tp.date.now("YYYY-MM-DD") %>
last_updated: <%+ tp.date.now("YYYY-MM-DD") %>
last_tended: <%+ tp.date.now("YYYY-MM-DD") %>
review_by: <%+ tp.date.now("YYYY-MM-DD") %>     # set deliberately for outcome-review (e.g. +90d for medium decisions)
confidence: possible
tags: [<domain>/decision]
status: open                       # open | closed-with-outcome | reversed
sources: []
decision_date: <%+ tp.date.now("YYYY-MM-DD") %>
outcome_review_date: null          # set when status moves to closed-with-outcome
---

# <decision title>

> [!important] What was decided
> <one paragraph: the decision in plain language>

## Context at decision time

<what was true / known / believed when this was decided>

## Options considered

| Option | Pros | Cons | Score |
|---|---|---|---|
| <option-A> | ... | ... | <0-10> |
| <option-B> | ... | ... | <0-10> |
| <option-C> | ... | ... | <0-10> |

## Counterpoints raised

<!--
v1.8.2 outcome-trail: every Counterpoint here gets revisited at outcome_review_date.
Did it actually materialize? Was it a real risk or paranoia? This is how Life OS
learns whether your worry-mode is calibrated.
-->

- <counterpoint-1>: <how serious it seemed at decision time>
- <counterpoint-2>: <how serious it seemed at decision time>

## Decision rationale

<why option X was chosen despite the counterpoints>

## Outcome (filled in at review time)

> [!info] Status: open
> Fill this in when `outcome_review_date` arrives or `status` flips to `closed-with-outcome`.

- **What actually happened**: <to fill>
- **Counterpoints that materialized**: <which ones from above came true>
- **Counterpoints that didn't**: <which ones were paranoia>
- **Calibration note**: <was the original confidence right? Lower? Higher?>

## Related decisions

- [[<other-decision>]]

## Sources

1. <citation>
EOF
emit ""

write_if_missing "wiki/.templates/lesson-template.md" "lesson template (post-mortem)" <<'EOF'
---
title: "<lesson — short imperative phrase>"
aliases: []
domain: <domain>
kind: lesson                       # v1.8.2 kind enum
created: <%+ tp.date.now("YYYY-MM-DD") %>
last_updated: <%+ tp.date.now("YYYY-MM-DD") %>
last_tended: <%+ tp.date.now("YYYY-MM-DD") %>
review_by: <%+ tp.date.now("YYYY-MM-DD") %>
confidence: likely                 # lessons usually start "likely" — proven by experience
tags: [<domain>/lesson]
status: candidate
sources: []
trigger_event: ""                  # what specific event triggered this lesson
recurrence: 1                      # how many times this lesson reappeared (bump on repeat)
---

# <lesson>

> [!quote] One-line lesson
> <imperative form — "Always check X before Y", "Never trust Z without W">

## Trigger event

<what specifically happened that crystallized this lesson>

## Why it matters

<the cost of forgetting this lesson — concrete consequence>

## How to apply

- <action-1: when you see signal X, do Y>
- <action-2>

## Related lessons / methods

- [[<related-lesson>]]
- [[<related-method>]]

## Recurrence log

<!-- Each time this lesson re-applies (i.e. you almost forgot it), append a line here. -->

- <YYYY-MM-DD>: first observed
EOF
emit ""

write_if_missing "wiki/.templates/config-template.md" "config/reference template" <<'EOF'
---
title: "<config or reference name>"
aliases: []
domain: <domain>
kind: config                       # v1.8.2 kind enum
created: <%+ tp.date.now("YYYY-MM-DD") %>
last_updated: <%+ tp.date.now("YYYY-MM-DD") %>
last_tended: <%+ tp.date.now("YYYY-MM-DD") %>
review_by: <%+ tp.date.now("YYYY-MM-DD") %>
confidence: certain                # configs are usually verifiable
tags: [<domain>/config]
status: confirmed
sources: []
---

# <config name>

> [!info] What this is
> <one paragraph — what this config controls / where it lives>

## Current value

```yaml
<verbatim config snippet>
```

## Where it's set

- File: `<path>`
- Format: <yaml | json | env | ...>

## Why it's set this way

<rationale — why this value vs alternatives>

## How to change it

1. <step>
2. <step>

## Side effects

> [!warning] Changing this affects
> - <downstream-1>
> - <downstream-2>

## Related configs

- [[<other-config>]]
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
