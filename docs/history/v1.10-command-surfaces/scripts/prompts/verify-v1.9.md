# User-invoked prompt · verify-v1.9

> ROUTER reads this when user runs `/verify-v1.9` after `/migrate-v1.9`.
> Validates 8 acceptance criteria from `_meta/rfc/v1.9-second-brain-structure-optimization.md` §3.
> md-only — ROUTER executes inline via Bash / Read / Glob / Grep. No .sh helpers.

## Trigger keywords

- `/verify-v1.9`
- `验证 v1.9` / `verify v1.9 migration`

## Goal

Run 8 validation checks corresponding to Opt #1-#8 acceptance criteria from the v1.9 RFC. Output a per-check ✅/❌ table with details. Exit code 0 only if all 8 pass.

---

## Check #1 · Opt #1 透明化 + 去下划线

### Sub-checks

```bash
check_1a=$(test ! -d "_meta" && echo "PASS" || echo "FAIL: _meta/ still exists (should be renamed to meta/)")
check_1b=$(test ! -d "meta/.system" && echo "PASS" || echo "FAIL: meta/.system/ exists (should be removed)")
check_1c=$(grep -q "Understanding.*meta" docs/second-brain.md 2>/dev/null && echo "PASS" || echo "WARN: docs/second-brain.md missing 5-class section")
check_1d=$(test -d "meta/runtime" && echo "PASS" || echo "WARN: meta/runtime/ missing — agents may not have run yet")
```

### Report

```
Opt #1 (meta 透明化 + 去下划线):
  1a. _meta/ 目录不存在（已重命名）: <check_1a>
  1b. meta/.system/ 目录不存在: <check_1b>
  1c. docs/second-brain.md 含 5 类心智模型: <check_1c>
  1d. meta/runtime/ 存在（audit trail 可见）: <check_1d>
```

Pass if 1a AND 1b are PASS (1c/1d are WARN, not blocking).

---

## Check #2 · Opt #2 queue 重命名

### Sub-checks

```bash
check_2a=$(test -d "inbox" && echo "PASS" || echo "FAIL: vault-root inbox/ missing")
check_2b=$(test -d "meta/queue" && echo "PASS" || echo "FAIL: meta/queue/ missing")
check_2c=$(test ! -d "meta/inbox" && echo "PASS" || echo "FAIL: meta/inbox/ still exists (should be renamed to queue/)")
check_2d=$(test -f "meta/queue/README.md" && echo "PASS" || echo "FAIL: meta/queue/README.md missing")
check_2e=$(test -d "meta/queue/to-process" && echo "PASS" || echo "FAIL: meta/queue/to-process/ missing")
```

### Report

```
Opt #2 (queue 重命名):
  2a. vault-root inbox/ 存在: <check_2a>
  2b. meta/queue/ 存在: <check_2b>
  2c. meta/inbox/ 不存在: <check_2c>
  2d. meta/queue/README.md 存在: <check_2d>
  2e. meta/queue/to-process/ 存在: <check_2e>
```

Pass if all 5 are PASS.

---

## Check #3 · Opt #3 decisions 合一

### Sub-checks

```bash
check_3a=$(find projects/*/decisions/ -name '*.md' -type f 2>/dev/null | head -1 | grep -q . && echo "FAIL: projects/*/decisions/ still has files" || echo "PASS")
check_3b=$(find meta/incidents/ -name '*.yml' -type f 2>/dev/null | head -1 | grep -q . && echo "FAIL: meta/incidents/*.yml still exists" || echo "PASS")
check_3c=$(find meta/decisions/ -mindepth 2 -name '*.md' -type f 2>/dev/null | head -1 | grep -q . && echo "PASS" || echo "WARN: meta/decisions/<YYYY-MM>/*.md empty (no decisions yet?)")

# Check month subdirectory format (YYYY-MM)
check_3d="PASS"
for dir in meta/decisions/*/; do
  [ -d "$dir" ] || continue
  base=$(basename "$dir")
  if ! echo "$base" | grep -qE '^[0-9]{4}-[0-9]{2}$'; then
    check_3d="FAIL: meta/decisions/$base does not match YYYY-MM format"
    break
  fi
done

# Spot-check domains field uses 6 functional IDs
sample_decision=$(find meta/decisions/ -name '*.md' -type f 2>/dev/null | head -1)
check_3e="PASS"
if [ -n "$sample_decision" ]; then
  domains_line=$(grep '^domains:' "$sample_decision" 2>/dev/null)
  if [ -n "$domains_line" ]; then
    invalid_domains=$(echo "$domains_line" | grep -vE '\[(governance|execution|finance|infra|people|growth|[,\s])*\]' | head -1)
    if [ -n "$invalid_domains" ]; then
      check_3e="WARN: decision $sample_decision has domains outside 6 functional IDs: $invalid_domains"
    fi
  fi
fi

# Spot-check applied_methods is list (not string)
# Old schema (pre-v1.9) had `applied_method:` (singular string); v1.9 requires `applied_methods:` (list)
check_3f="PASS"
if [ -n "$sample_decision" ]; then
  # FAIL if singular form exists AND plural form does not (i.e. only old schema)
  if grep -qE '^applied_method:[ ]' "$sample_decision" 2>/dev/null && ! grep -q '^applied_methods:' "$sample_decision" 2>/dev/null; then
    check_3f="FAIL: $sample_decision has old 'applied_method:' (singular); should be 'applied_methods:' (list)"
  fi
fi
```

### Report

```
Opt #3 (decisions 合一):
  3a. projects/*/decisions/ 空: <check_3a>
  3b. meta/incidents/*.yml 空: <check_3b>
  3c. meta/decisions/<YYYY-MM>/*.md 存在: <check_3c>
  3d. 月子目录格式正确（YYYY-MM）: <check_3d>
  3e. 决策 domains 字段在 6 functional IDs 内: <check_3e>
  3f. 决策 applied_methods 是 list（非单值）: <check_3f>
```

Pass if 3a/3b/3d/3f are PASS (3c/3e are WARN-level).

---

## Check #4 · Opt #4 archive frontmatter

### Sub-checks

```bash
check_4a=$(test ! -d "archive" && echo "PASS" || echo "FAIL: archive/ still exists")

# Check archived projects have proper frontmatter
check_4b="PASS"
check_4c="PASS"
for proj_idx in projects/*/index.md; do
  [ -f "$proj_idx" ] || continue
  stage=$(grep '^lifecycle_stage:' "$proj_idx" | awk '{print $2}')
  if [ -z "$stage" ]; then
    continue  # Not all projects need lifecycle_stage if pre-v1.9 didn't set
  fi
  
  # 4b: lifecycle_stage in 4 values
  case "$stage" in
    candidate|active|archived|superseded) ;;
    dormant) check_4b="FAIL: $proj_idx has lifecycle_stage: dormant (should be 4 values + paused_until)" ;;
    *) check_4b="FAIL: $proj_idx has unknown lifecycle_stage: $stage" ;;
  esac
  
  # 4c: archived projects have archived_at_source
  if [ "$stage" = "archived" ]; then
    src=$(grep '^archived_at_source:' "$proj_idx" | awk '{print $2}')
    case "$src" in
      git-log|migrated-unknown|manual|auto) ;;
      *) check_4c="FAIL: archived project $proj_idx has invalid archived_at_source: $src" ;;
    esac
  fi
done
```

### Report

```
Opt #4 (archive frontmatter):
  4a. archive/ 目录不存在: <check_4a>
  4b. 所有项目 lifecycle_stage 在 4 值内: <check_4b>
  4c. archived 项目有合法 archived_at_source: <check_4c>
```

Pass if 4a/4b/4c are PASS.

---

## Check #5 · Opt #5 journal 时间轴

### Sub-checks

```bash
check_5a=$(find projects/*/journal/ -type d 2>/dev/null | head -1 | grep -q . && echo "FAIL: projects/*/journal/ still exists" || echo "PASS")

# Check journal files use YYYY-MM-DD.md naming
check_5b="PASS"
for jf in meta/journal/*.md; do
  [ -f "$jf" ] || continue
  [ "$(basename "$jf")" = "INDEX.md" ] && continue  # Skip INDEX if exists
  base=$(basename "$jf" .md)
  if ! echo "$base" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
    check_5b="FAIL: meta/journal/$base does not match YYYY-MM-DD"
    break
  fi
done

# Check sample project index has ## Journal section with Dataview block
check_5c="PASS"
sample_proj=$(ls -d projects/*/ 2>/dev/null | head -1)
if [ -n "$sample_proj" ]; then
  if ! grep -q "## Journal" "$sample_proj/index.md" 2>/dev/null; then
    check_5c="WARN: $sample_proj/index.md missing ## Journal section (might be newly-migrated, archiver will add)"
  fi
fi
```

### Report

```
Opt #5 (journal 时间轴):
  5a. projects/*/journal/ 空: <check_5a>
  5b. meta/journal/*.md 用 YYYY-MM-DD 命名: <check_5b>
  5c. 项目 index.md 含 ## Journal 段: <check_5c>
```

Pass if 5a/5b are PASS.

---

## Check #6 · Opt #6 areas 种子化

### Sub-checks

```bash
check_6a=$(grep -q "Recommended seed" docs/second-brain.md 2>/dev/null && echo "PASS" || echo "WARN: docs/second-brain.md missing 'Recommended seed' wording")
check_6b=$(test -f "areas/README.md" && echo "PASS" || echo "FAIL: areas/README.md missing")

# Check no truly empty areas remain
check_6c="PASS"
for dir in areas/*/; do
  [ -d "$dir" ] || continue
  file_count=$(find "$dir" -type f | wc -l | tr -d ' ')
  if [ "$file_count" -eq 0 ]; then
    check_6c="FAIL: empty area $dir still exists (should have been cleaned)"
    break
  fi
done
```

### Report

```
Opt #6 (areas 种子化):
  6a. docs/second-brain.md 含 "Recommended seed" 措辞: <check_6a>
  6b. areas/README.md 存在: <check_6b>
  6c. 真空 areas 已清理: <check_6c>
```

Pass if 6b/6c are PASS.

---

## Check #7 · Opt #7 user-patterns 移位

### Sub-checks

```bash
check_7a=$(test ! -f "user-patterns.md" && echo "PASS" || echo "FAIL: vault-root user-patterns.md still exists")
check_7b=$(test -f "meta/user-patterns.md" && echo "PASS" || echo "WARN: meta/user-patterns.md missing (might not have been generated yet by advisor)")
```

### Report

```
Opt #7 (user-patterns 移位):
  7a. vault-root user-patterns.md 不存在: <check_7a>
  7b. meta/user-patterns.md 存在: <check_7b>
```

Pass if 7a is PASS.

---

## Check #8 · Opt #8 互引字段

### Sub-checks

```bash
# Check methods have born_from_decisions, NOT applied_in_decisions
check_8a="PASS"
check_8b="PASS"
check_8c="PASS"
for mf in meta/methods/*.md; do
  [ -f "$mf" ] || continue
  
  # 8a: each method has born_from_decisions field
  if ! grep -q '^born_from_decisions:' "$mf"; then
    check_8a="FAIL: $mf missing born_from_decisions field"
    break
  fi
  
  # 8b: no method has applied_in_decisions field (Q-11 砍除)
  if grep -q '^applied_in_decisions:' "$mf"; then
    check_8b="FAIL: $mf still has applied_in_decisions field (should be removed per DR-1.9.24)"
    break
  fi
  
  # 8c: each method has ## Applied in decisions section
  if ! grep -q "## Applied in decisions" "$mf"; then
    check_8c="WARN: $mf missing ## Applied in decisions section"
  fi
done

# Check decisions have applied_methods + journal_date
check_8d="PASS"
for df in meta/decisions/*/*.md; do
  [ -f "$df" ] || continue
  if ! grep -q '^applied_methods:' "$df"; then
    check_8d="FAIL: $df missing applied_methods field"
    break
  fi
  if ! grep -q '^journal_date:' "$df"; then
    check_8d="FAIL: $df missing journal_date field"
    break
  fi
done

# Check journal has referenced_decisions + referenced_methods
check_8e="PASS"
for jf in meta/journal/*.md; do
  [ -f "$jf" ] || continue
  [ "$(basename "$jf")" = "INDEX.md" ] && continue
  if ! grep -q '^referenced_decisions:' "$jf"; then
    check_8e="WARN: $jf missing referenced_decisions field (may be pre-Opt #8 entry)"
    break
  fi
done
```

### Report

```
Opt #8 (互引字段):
  8a. 所有 method 含 born_from_decisions: <check_8a>
  8b. 所有 method 不含 applied_in_decisions（已砍）: <check_8b>
  8c. 所有 method 含 ## Applied in decisions 段: <check_8c>
  8d. 所有 decision 含 applied_methods + journal_date: <check_8d>
  8e. 所有 journal 含 referenced_decisions + referenced_methods: <check_8e>
```

Pass if 8a/8b/8d are PASS (8c/8e are WARN).

---

## Final report

```
══════════════════════════════════════════════════
 /verify-v1.9 Acceptance Report
══════════════════════════════════════════════════

| Check | Status |
|-------|--------|
| Opt #1 (meta 透明化 + 去下划线) | <PASS/FAIL> |
| Opt #2 (queue 重命名) | <PASS/FAIL> |
| Opt #3 (decisions 合一) | <PASS/FAIL> |
| Opt #4 (archive frontmatter) | <PASS/FAIL> |
| Opt #5 (journal 时间轴) | <PASS/FAIL> |
| Opt #6 (areas 种子化) | <PASS/FAIL> |
| Opt #7 (user-patterns 移位) | <PASS/FAIL> |
| Opt #8 (互引字段) | <PASS/FAIL> |

<if all PASS>
✅ All 8 acceptance criteria met. v1.9 migration verified.

Next steps:
- Resume normal lifeos usage (上朝 / 退朝 work as before)
- Next session-close `git push` propagates the v1.9 layout to your GitHub remote
- Optional: Run /audit-mode-3 to baseline post-migration vault health

</if>

<if any FAIL>
❌ <N> criteria failed. See details above.

Failure recovery options:
- git reset --hard <pre-migration-commit-sha> to fully revert
- Or hand-fix specific issues and re-run /verify-v1.9
- For schema fixes (frontmatter fields): edit relevant files manually

Do NOT proceed with v1.9 release until all 8 are PASS.

</if>

══════════════════════════════════════════════════
```

Exit code: 0 if all 8 PASS, 1 if any FAIL (WARN does not fail).

---

## What this command does NOT do

- Repair issues (only reports them)
- Run /migrate-v1.9 again (idempotency is /migrate-v1.9's job)
- Touch git (verify only reads)
- Validate user content (e.g., decision body quality, method docstring presence)

---

**Spec authority**: This prompt implements `_meta/rfc/v1.9-second-brain-structure-optimization.md` §4.2. Any discrepancy → RFC wins.

## Final step · Maintenance ledger stamp (v1.10.0)

Per `references/maintenance-ledger-spec.md`: upsert this job's row in
`meta/maintenance-ledger.md` — create the file with its standard header if
missing; if a row for this job exists, replace it in place, otherwise insert
keeping alphabetical order. Never duplicate a row.

`| verify-v1.9 | once | <today YYYY-MM-DD, from a real date command — no fabrication> |`
