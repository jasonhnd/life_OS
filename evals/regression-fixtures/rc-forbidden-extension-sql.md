---
# v1.8.7 regression fixture (md format · DR-10 ontological constraint)
# Tests verify-release check 8 (full-repo) AND check 10 (diff-scoped) detect SQL files.
---

# Regression Fixture (v1.8.7)

```yaml
id: rc-forbidden-extension-sql
description: |
  Negative fixture: repo contains a `.sql` file outside the gitignored exception list.
  This violates v1.8.7 DR-10 (md-only ontological constraint) — lifeos has NO database
  layer, so `.sql` files have no legitimate purpose. /verify-release check 8 (full-repo
  scan) AND check 10 (diff-scoped scan since last tag) MUST both FAIL on this.

  Even if a developer thinks they need SQL for "memory tree backend" or "session search
  index", the answer is: re-design as md per DR-10. This fixture verifies the check
  catches the file before release.
expected_verdict: FAIL
expected_failure_class: F4_SCOPE_FAILURE
expected_checks:
  - /verify-release check 8 (full-repo forbidden extensions)
  - /verify-release check 10 (diff-scoped forbidden extensions)
  - AUDITOR Mode 7 M7-7 (md-only constraint not bypassed in proposals)
introduced_in: v1.8.7
related_spec: SKILL.md HARD RULE "md-only is lifeos's ontological constraint" (DR-10)

input_filesystem_state:
  files_in_repo:
    - path: _meta/cortex/schema.sql
      contents_excerpt: |
        -- attempt to introduce SQLite schema for hippocampus retrieval
        CREATE TABLE sessions (
          id TEXT PRIMARY KEY,
          timestamp DATETIME,
          summary TEXT
        );
      provenance: synthetic — represents the most likely SQL re-introduction path (Cortex backend)

expected_check_output_excerpt: |
  ❌ check 8 (forbidden extensions): _meta/cortex/schema.sql found
  ❌ check 10 (diff-scoped forbidden extensions): _meta/cortex/schema.sql introduced since v<prev-tag>

negative_case_for: |
  This is a *negative* fixture: if it produces PASS, the v1.8.7 md-only constraint has
  regressed and SQL has re-infiltrated the repo. AUDITOR Mode 7 M7-7 must flag.
```

## How to verify this fixture

1. Create a temporary `.sql` file at the path above
2. Run `/verify-release` (or check 8/10 manually)
3. Confirm both checks output ❌ FAIL
4. Confirm AUDITOR Mode 7 M7-7 logs the violation
5. Delete the `.sql` file before continuing

## Related fixtures

- `rc-forbidden-extension-sh.md` (v1.8.5) — sibling for `.sh`
- `rc-forbidden-extension-json.md` (v1.8.7) — sibling for `.json`
- `rc-forbidden-extension-db.md` (v1.8.7) — sibling for `.db` / `.sqlite`
