# Obsidian Vault Compatibility Spec (v1.8.0 R-1.8.0-013)

> Borrowed from llm_wiki — make every second-brain seeded by `tools/seed.py`
> simultaneously a valid Obsidian vault. User can navigate / search / graph
> the brain visually without any extra setup.

## Why

CLI conversation is the primary interface, but visual graph navigation and
mobile read access (Obsidian iOS / Android) are powerful complements. Adding
a minimal `.obsidian/` config makes this free.

## Layout

After `tools/seed.py` runs, second-brain root contains:

```
<second-brain-root>/
├── .obsidian/
│   ├── app.json              # vault settings (wikilink format, ignored paths)
│   ├── core-plugins.json     # enabled core plugins
│   └── .gitignore            # excludes per-device state
├── SOUL.md
├── _meta/
├── wiki/
├── projects/
├── inbox/
└── ...
```

## .obsidian/app.json (seeded)

Key settings written by `_write_obsidian_vault()`:

```json
{
  "alwaysUpdateLinks": true,
  "newLinkFormat": "shortest",
  "useMarkdownLinks": false,
  "showLineNumber": true,
  "spellcheck": false,
  "userIgnoreFilters": [
    "_meta/runtime/",
    "_meta/eval-history/recovery/",
    "_meta/eval-history/maintenance/",
    ".git/",
    "scripts/",
    "tools/",
    "evals/",
    "tests/"
  ]
}
```

- `useMarkdownLinks: false` — use `[[wikilinks]]`, not `[text](path)`
- `newLinkFormat: shortest` — `[[concept-id]]` not `[[_meta/concepts/foo/concept-id]]`
- `userIgnoreFilters` — runtime + cache + dev folders hidden in Obsidian UI

## .obsidian/core-plugins.json (seeded)

Enabled plugins:

- `file-explorer` — left sidebar tree
- `global-search` — content search
- `switcher` — Cmd+P file switcher
- `graph` — knowledge graph view (the killer feature)
- `backlink` — show pages that link to current page
- `outgoing-link` — show pages current page links to
- `tag-pane` — tag-based navigation
- `page-preview` — hover for preview
- `outline` — H1/H2/H3 outline
- `word-count`, `templates`, `note-composer`, `command-palette`,
  `markdown-importer`, `random-note`, `starred`, `file-recovery`

Community plugins NOT auto-enabled (user can install per device).

## .obsidian/.gitignore (seeded)

```
# Obsidian local state (per-device, do not sync)
workspace.json
workspace-mobile.json
appearance.json

# Obsidian sync conflicts
.trash/
```

`workspace.json` contains pane layout — varies per device. `appearance.json`
contains theme — user choice. These are gitignored to prevent sync churn.
`app.json` and `core-plugins.json` ARE tracked so all devices get the same
foundational config.

## Wikilink convention

All cross-references in body text use `[[]]`:

- `[[concept-id]]` — link to concept
- `[[wiki-entry-slug]]` — link to wiki entry
- `[[person-id]]` — link to person
- `[[comparison-id]]` — link to comparison
- `[[session-id]]` — link to session summary
- `[[concept-id|Display Name]]` — wikilink with display alias

Obsidian's `newLinkFormat: shortest` resolves these by filename match across
the vault, so no full path needed.

**Frontmatter arrays remain YAML** (machine-parseable):

```yaml
concepts_activated: [concept-1, concept-2]   # YAML strings, NOT wikilinks
related: [[[concept-1]], [[wiki-entry-1]]]   # exception: explicit wikilink arrays
```

When a frontmatter field semantically references another page (`source_session`,
`superseded_by`, `related`, `concepts_linked` in people/comparison pages), use
wikilink syntax for Obsidian navigability.

## Re-seeding existing vaults

`_write_obsidian_vault()` is idempotent + non-destructive:
- Creates `.obsidian/` if absent
- Writes each config file ONLY if absent
- Does NOT overwrite user's existing customization

To force re-seed, delete `.obsidian/` and re-run `tools/seed.py` (or the
`scripts/prompts/migrate-to-wikilinks.md` LLM migration prompt).

## Mobile use

Obsidian Mobile (iOS / Android) reads the same vault when synced via:
- iCloud (point Obsidian Mobile to iCloud-synced second-brain folder)
- Obsidian Sync (paid add-on)
- Git (Obsidian Mobile + working-copy or termux git)

User can read SOUL / wiki / sessions / decisions from phone. Writing from
Obsidian Mobile bypasses lifeos archiver — should be limited to quick notes
that Obsidian sync brings back to terminal where archiver picks up next session.

## Graph view colors (suggested user customization)

Recommend in user's per-device `.obsidian/graph.json` (not seeded):

| Page type | Color |
|-----------|-------|
| `_meta/concepts/` | blue |
| `_meta/people/` | green |
| `_meta/comparisons/` | orange |
| `_meta/methods/` | purple |
| `_meta/sessions/` | gray |
| `wiki/` | cyan |
| SOUL.md | gold (single node) |

Configurable via Obsidian UI: Graph view → Settings → Groups → add filters
based on path/tag.

## Anti-patterns

- Don't try to **edit** `.obsidian/` JSON files via lifeos prompts. They're
  Obsidian's internal state. seed.py writes the minimal viable; user
  customization happens through Obsidian UI.
- Don't add plugins to `core-plugins.json` aggressively — too many enabled
  cores slows Obsidian Mobile. Keep the list focused.
