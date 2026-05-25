---
# v1.8.7 regression fixture (md format · DR-10 ontological constraint)
# Tests verify-release check 8 + check 10 detect .json files (excluding gitignored .claude/settings*.json).
---

# Regression Fixture (v1.8.7)

```yaml
id: rc-forbidden-extension-json
description: |
  Negative fixture: repo contains a standalone `.json` file (not gitignored .claude/settings*.json).
  v1.8.6 already banned standalone `.json` files; v1.8.7 DR-10 makes this permanent
  per the ontological constraint. Common re-introduction path: dev adds a config file
  thinking "YAML frontmatter feels inconvenient, let me just use JSON". The answer is:
  re-express in md frontmatter or as a separate md file.

  Note: `.claude/settings.json` is gitignored (platform-required by Claude Code), NOT
  a violation. Test fixture targets git-tracked .json files only.
expected_verdict: FAIL
expected_failure_class: F4_SCOPE_FAILURE
expected_checks:
  - /verify-release check 8 (full-repo forbidden extensions)
  - /verify-release check 10 (diff-scoped forbidden extensions)
  - AUDITOR Mode 7 M7-7 (md-only constraint not bypassed)
introduced_in: v1.8.7 (v1.8.6 was the original `.json` ban, v1.8.7 fixture formalizes it)
related_spec: SKILL.md HARD RULE "md-only is lifeos's ontological constraint" (DR-10)

input_filesystem_state:
  files_in_repo:
    - path: pro/compress-rules/skip-files-modified.json
      contents_excerpt: |
        {
          "rule_name": "skip files modified",
          "applies_to": ["archiver", "router"],
          "pattern": "## Files Modified"
        }
      provenance: synthetic — represents D8 reintroduction attempt (cut from v1.8.7 per DR-08)

expected_check_output_excerpt: |
  ❌ check 8 (forbidden extensions): pro/compress-rules/skip-files-modified.json found
  ❌ check 10 (diff-scoped forbidden extensions): pro/compress-rules/skip-files-modified.json introduced since v<prev-tag>

negative_case_for: |
  D8 (three-layer compression rules) was cut from v1.8.7 per DR-08. If someone
  re-introduces it as JSON rules files, this fixture catches the regression.
  AUDITOR Mode 7 M7-7 must also flag at the proposal level (before the file is created).
```

## How to verify this fixture

1. Create a temporary `.json` file at a tracked path (NOT in `.claude/` gitignored area)
2. Run `/verify-release` (or check 8/10 manually)
3. Confirm both checks output ❌ FAIL
4. Delete the `.json` file before continuing

## Related fixtures

- `rc-forbidden-extension-sh.md` (v1.8.5) — sibling for `.sh`
- `rc-forbidden-extension-sql.md` (v1.8.7) — sibling for `.sql`
- `rc-forbidden-extension-db.md` (v1.8.7) — sibling for `.db` / `.sqlite`
