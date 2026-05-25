---
# v1.8.7 regression fixture (md format · DR-10 ontological constraint)
# Tests verify-release check 8 + check 10 detect .db / .sqlite files (binary databases).
---

# Regression Fixture (v1.8.7)

```yaml
id: rc-forbidden-extension-db
description: |
  Negative fixture: repo contains a `.db` or `.sqlite` file. Borrowing the OpenHuman
  Memory Tree pattern WITHOUT borrowing its SQLite implementation is the entire point
  of v1.8.7 DR-10. If someone tries to materialize the cascade seal proposal by adding
  a SQLite database file, this fixture catches it.

  Most likely re-introduction path: dev sees `_meta/cortex/` directory and thinks
  "let me add a fast-retrieval SQLite index here". The answer is: per A1 spec proposal,
  cascade seal materializes via md directory layout (`_meta/sessions/L0/` etc.), NOT
  a database file. The whole architecture would collapse if SQL slips in here.
expected_verdict: FAIL
expected_failure_class: F4_SCOPE_FAILURE
expected_checks:
  - /verify-release check 8 (full-repo forbidden extensions, .db/.sqlite)
  - /verify-release check 10 (diff-scoped forbidden extensions)
  - AUDITOR Mode 7 M7-7 (md-only constraint not bypassed in proposals)
introduced_in: v1.8.7
related_spec:
  - SKILL.md HARD RULE "md-only is lifeos's ontological constraint" (DR-10)
  - references/memory-tree-spec.md (A1 proposal — md directory layout, NOT SQLite)

input_filesystem_state:
  files_in_repo:
    - path: _meta/cortex/hippocampus-index.db
      contents_excerpt: |
        [binary SQLite file — header: "SQLite format 3"]
      provenance: synthetic — represents OpenHuman Memory Tree SQLite re-introduction attempt
    - path: _meta/sessions/chunks.sqlite
      contents_excerpt: |
        [binary SQLite file]
      provenance: synthetic — direct copy of OpenHuman's `memory_tree/chunks.db` pattern

expected_check_output_excerpt: |
  ❌ check 8 (forbidden extensions): _meta/cortex/hippocampus-index.db found
  ❌ check 8 (forbidden extensions): _meta/sessions/chunks.sqlite found
  ❌ check 10 (diff-scoped forbidden extensions): both files introduced since v<prev-tag>

negative_case_for: |
  v1.8.7's central architectural decision (DR-10) is that lifeos borrows OpenHuman's
  Memory Tree *pattern* but expresses it in md directories, not binary databases. This
  fixture protects that decision against the most likely future regression — a developer
  thinking "let me add SQLite for performance" without realizing it breaks the md-only
  ontological commitment.
```

## How to verify this fixture

1. Create a temporary `.db` or `.sqlite` file
2. Run `/verify-release` (or check 8/10 manually)
3. Confirm both checks output ❌ FAIL
4. Confirm AUDITOR Mode 7 M7-7 flags any associated spec/RFC proposing the introduction
5. Delete the file before continuing

## Related fixtures

- `rc-forbidden-extension-sh.md` (v1.8.5) — sibling for `.sh`
- `rc-forbidden-extension-sql.md` (v1.8.7) — sibling for `.sql`
- `rc-forbidden-extension-json.md` (v1.8.7) — sibling for `.json`
