---
scenario: tool-export
type: tool-invocation
tool: export
requires_claude: false
# R4.5 machine-eval fields — pick JSON sub-scenario (stdlib only, no external deps).
# PDF / HTML / Anki require optional deps (pandoc / markdown-it-py / genanki);
# runner skips those via skip_if_missing when the dep is unavailable.
setup_script: |
  mkdir -p {tmp_dir}/wiki {tmp_dir}/exports
  cat > {tmp_dir}/wiki/sample-one.md <<'EOF'
  ---
  title: Sample page one
  ---
  # Body
  Paragraph one.
  EOF
  cat > {tmp_dir}/wiki/sample-two.md <<'EOF'
  ---
  title: Sample page two
  ---
  # Body
  Paragraph two.
  EOF
invocation: "python3 -m tools.export --format json --scope {tmp_dir}/wiki --output-dir {tmp_dir}/exports"
expected_exit_code: 0
expected_stdout_contains: []
expected_stderr_contains: []
# The exact filename includes today's date; runner matches by prefix glob
expected_files_glob:
  - "{tmp_dir}/exports/wiki-*.json"
---

# Tool Scenario · export

**Contract**: references/tools-spec.md §6.9 · Format conversion (pdf / html / json / anki).

## User Message

```
把 wiki/ 目录导出成 4 种格式：pdf（pandoc）、html（带 CSS）、json（扁平数组）、anki（.apkg 卡片），输出到 exports/。
```

(English equivalent: "Export wiki/ directory in all 4 formats: pdf (pandoc), html (inline CSS), json (flat array), anki (.apkg cards). Output under exports/.")

## Scenario

Reads every `*.md` under `--scope`, emits a single
`exports/{scope-slug}-YYYY-MM-DD.{ext}` file per format. Each format
has its own implementation dispatched by `--format`:

| Format | Dependency | Output |
|--------|------------|--------|
| pdf    | pandoc ≥3.0 binary | `exports/wiki-2026-04-22.pdf` |
| html   | markdown-it-py + plugins | `exports/wiki-2026-04-22.html` (self-contained, inline CSS) |
| json   | stdlib | `exports/wiki-2026-04-22.json` (flat array of {frontmatter, body}) |
| anki   | genanki | `exports/wiki-2026-04-22.apkg` |

Per-type Anki field mapping (§6.9):

| Type | Front | Back |
|------|-------|------|
| concept | canonical_name + aliases | body + outgoing_edges table (top 5 by weight) |
| method  | name | summary + ## Steps section |
| wiki    | title (conclusion) | Reasoning + Applicable-When sections |
| session | subject | Key Decisions + Outcome |

Runtime budget: < 30 seconds per 100 files.

## Success Criteria (4 sub-scenarios)

**Sub-scenario A · json**
- [ ] `uv run tools/export.py --format json --scope wiki/` with 5 wiki files → `exports/wiki-YYYY-MM-DD.json` created
- [ ] JSON is a flat array of 5 elements
- [ ] Each element has `frontmatter: {...}` object and `body: "..."` string
- [ ] JSON parses cleanly via `python -m json.tool`
- [ ] Exit 0

**Sub-scenario B · html**
- [ ] `uv run tools/export.py --format html --scope wiki/` → `exports/wiki-YYYY-MM-DD.html` created
- [ ] Output is self-contained (inline CSS in `<style>`)
- [ ] Tables and footnotes from source markdown render correctly
- [ ] Exit 0

**Sub-scenario C · anki**
- [ ] `uv run tools/export.py --format anki --scope concepts/` → `exports/concepts-YYYY-MM-DD.apkg` created
- [ ] genanki produces valid SQLite-backed .apkg (size > 0 bytes)
- [ ] Deck name = scope slug ("concepts")
- [ ] Front/back mapping matches the type table above
- [ ] genanki not installed → exit 1 with clear install hint
- [ ] Exit 0 when genanki available

**Sub-scenario D · pdf**
- [ ] `uv run tools/export.py --format pdf --scope wiki/` with pandoc on PATH → `exports/wiki-YYYY-MM-DD.pdf` created (non-zero size)
- [ ] pandoc missing → exit 1 with install hint (https://pandoc.org/installing.html)
- [ ] Exit 0 when pandoc available

**Cross-format**
- [ ] Empty `--scope` path → exit 1 with "no files found under scope"
- [ ] `--output-dir` overrides default `exports/`
- [ ] Unknown format → exit 1

## Input Fixture

```
fixture/wiki/
├── negotiation-jp.md        # title: "Offer-counteroffer pattern"
├── runway-formula.md        # title: "Monthly burn × 1.3 safety margin"
└── decision-matrices.md     # title: "5-axis matrix for big decisions"

fixture/concepts/
├── autonomy-vs-stability.md # canonical_name, aliases, outgoing_edges in frontmatter
└── risk-tolerance.md        # same shape
```

Synthetic wiki file:
```markdown
---
title: Offer-counteroffer pattern
applicable_when: negotiating salary in Japan
---
# Reasoning
...
# Applicable-When
...
```

## Expected Output

```
$ uv run tools/export.py --format json --scope fixture/wiki/
Wrote exports/wiki-2026-04-22.json (3 entries, 12 KB)
Exit 0

$ python -m json.tool exports/wiki-2026-04-22.json | head -10
[
  {
    "frontmatter": {
      "title": "Offer-counteroffer pattern",
      "applicable_when": "negotiating salary in Japan"
    },
    "body": "# Reasoning\n..."
  },
  ...
```

## Failure Modes

- File with no frontmatter → include in JSON with `frontmatter: {}`, don't crash
- Filename collision (same slug + same date) → append `-1`, `-2` suffix
- Anki type auto-detected from path: `concepts/` → concept mapping, `methods/` → method mapping, etc.

## Linked Documents

- `references/tools-spec.md` §6.9
- `tools/export.py`
- `tests/test_export.py`
- External: https://pandoc.org/installing.html, https://github.com/kerrickstaley/genanki
