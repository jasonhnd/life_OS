# User-invoked prompt · migrate-v1.9

> ROUTER reads this when user runs `/migrate-v1.9` to migrate a v1.8.x vault to v1.9 layout.
> Per v1.9 RFC `_meta/rfc/v1.9-second-brain-structure-optimization.md` (24 locked decisions).
> md-only — ROUTER executes inline via Bash / Read / Write / Edit. No .sh helpers.

## Trigger keywords

- `/migrate-v1.9`
- `迁移 v1.9` / `升级到 v1.9` / `migrate to v1.9`

## Goal

Migrate vault from v1.8.x layout to v1.9 layout in one shot:

1. `_meta/` → `meta/` (去下划线，Opt #1)
2. `meta/inbox/` → `meta/queue/` (Opt #2)
3. `projects/*/decisions/` + `meta/incidents/*.yml` → `meta/decisions/<YYYY-MM>/*.md` (Opt #3)
4. `archive/*/` → `projects/*/` + frontmatter (Opt #4)
5. `projects/*/journal/` → `meta/journal/<date>.md` (Opt #5)
6. 空 areas 清理 + `areas/README.md` 写入 (Opt #6)
7. `user-patterns.md` → `meta/user-patterns.md` (Opt #7)
8. methods/decisions/journal frontmatter 加互引字段 (Opt #8)

**Path convention in this document**: pre-v1.9 paths use `_meta/` (underscore prefix); v1.9 paths use `meta/` (no underscore). After Stage 1 of execution, `_meta/` no longer exists; everything is `meta/`.

## HARD constraints (per RFC)

- **No escape hatch** for git working dir cleanliness (DR-1.9.7)
- **No concurrency lock** (DR-1.9.15)
- **No verbose output mode** (DR-1.9.16)
- **No cross-version chain** — detect < v1.8.0 vault and abort (DR-1.9.14)
- **Strict refuse** if `archive/` contains non-project content (DR-1.9.22)

---

## Stage 0 · Pre-flight HARD GATEs

### 0a. Git working dir clean check (DR-1.9.7)

```bash
status=$(git status --porcelain)
if [ -n "$status" ]; then
  cat <<EOF
❌ 检测到未提交改动。迁移前需要 working dir 干净。请先：
   git stash             # 临时改动想保留
   或
   git add . && git commit -m "wip: before v1.9 migration"

然后重跑 /migrate-v1.9。
EOF
  exit 1
fi
```

### 0b. Cross-version check (DR-1.9.14)

```bash
# config 可能在 _meta/config.md（pre-v1.9）或 meta/config.md（post-v1.9）
config_path=""
if [ -f "_meta/config.md" ]; then
  config_path="_meta/config.md"
elif [ -f "meta/config.md" ]; then
  config_path="meta/config.md"
fi

if [ -z "$config_path" ]; then
  echo "⚠️ 找不到 config.md — 这看起来不是一个 lifeos vault。中止。"
  exit 1
fi

current_version=$(grep -m1 'migrated_to:' "$config_path" | awk '{print $2}')
```

Cases:
- `migrated_to: v1.9` → 已是 v1.9，输出"已是 v1.9，跳过"退出 0
- `migrated_to:` 为空 / 缺失 / `v1.8.0`..`v1.8.7` → 继续到 Stage 0c
- `migrated_to: <X>` 中 X 比 v1.9 新 → "vault 比当前代码新，停止" 退出 1
- `migrated_to: v1.6` / `v1.7` / 早于 v1.8 → 中止：

```
❌ Vault 是 v<X> 版本（migrated_to: <X>）。

v1.9 迁移要求 vault 至少是 v1.8.0。请按顺序跑：

  1. /migrate-from-v1.6（如果是 v1.6）
  2. （若有其他中间代迁移工具，按顺序跑）
  3. 完成后再跑 /migrate-v1.9

参考 docs/history/v1.7-migration.md 和 docs/guides/cross-version-migration.md（v1.9 新增）。
```

### 0c. Archive non-project content check (DR-1.9.22)

```bash
if [ -d "archive" ]; then
  non_project_dirs=()
  for dir in archive/*/; do
    [ -d "$dir" ] || continue
    if [ ! -f "$dir/index.md" ]; then
      size_info=$(du -sh "$dir" 2>/dev/null | cut -f1)
      file_count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
      non_project_dirs+=("$dir ($file_count files, $size_info)")
    fi
  done

  if [ ${#non_project_dirs[@]} -gt 0 ]; then
    cat <<EOF
❌ 检测到 archive/ 含非项目内容，迁移无法继续。

非项目目录（无 index.md）：
$(printf -- "- %s\n" "${non_project_dirs[@]}")

请先手动决定这些目录的去向：
  - 移到 inbox/（让 archiver 重新分类）
  - 移到 meta/legacy-archive/（单独保留）
  - 删除（用 git rm，git 历史保留）
  - 其他位置

然后重跑 /migrate-v1.9。
EOF
    exit 1
  fi
fi
```

---

## Stage 1 · Dry-run scan + 用户确认 (DR-1.9.16)

扫描所有需要操作的文件 + 路径，**per-stage 摘要输出**（无 per-file 列表）。

### 1.1 收集统计（注意：pre-v1.9 vault 仍是 `_meta/`）

```bash
# Stage 1 stats: _meta/ → meta/ rename
old_meta_exists=$(test -d "_meta" && echo "yes" || echo "no")

# Stage 1.5 stats: inbox → queue (post-Stage-1，要看 _meta/inbox/)
inbox_files=$(find "_meta/inbox" -type f 2>/dev/null | wc -l | tr -d ' ')

# Stage 2 stats: decisions consolidation
project_decisions=$(find projects/*/decisions/ -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
yml_incidents=$(find "_meta/incidents" -name '*.yml' -type f 2>/dev/null | wc -l | tr -d ' ')

# Stage 3 stats: archive
archive_projects=$(find archive/ -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')

# Stage 4 stats: journal
project_journal_entries=$(find projects/*/journal/ -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')

# Stage 5 stats: areas
truly_empty=0
quasi_empty=0
for dir in areas/*/; do
  [ -d "$dir" ] || continue
  file_count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
  if [ "$file_count" -eq 0 ]; then
    truly_empty=$((truly_empty + 1))
  else
    total_size=$(find "$dir" -type f -exec wc -c {} + 2>/dev/null | tail -1 | awk '{print $1}')
    if [ -n "$total_size" ] && [ "$total_size" -lt 200 ]; then
      quasi_empty=$((quasi_empty + 1))
    fi
  fi
done

# Stage 6 stats: user-patterns
up_at_root=$(test -f "user-patterns.md" && echo "yes" || echo "no")

# Stage 7 stats: cross-reference fields (estimate count, no scan needed beyond Stage 2)
```

### 1.2 输出 dry-run 报告

```
── Dry-run · /migrate-v1.9 ──

Stage 1 (Opt #1): rename _meta/ → meta/
  · 1 directory rename (cascades to all sub-paths)

Stage 1.5 (Opt #2): rename meta/inbox/ → meta/queue/
  · <inbox_files> files affected

Stage 2 (Opt #3): consolidate decisions to meta/decisions/<YYYY-MM>/
  · <project_decisions + yml_incidents> decisions migrate
    - From projects/*/decisions/: <project_decisions> files
    - From _meta/incidents/ (pre-Stage-1): <yml_incidents> .yml → .md conversions
  · Will create YYYY-MM subdirs based on reviewed_at dates

Stage 3 (Opt #4): archive → frontmatter
  · <archive_projects> projects move from archive/ → projects/ + lifecycle_stage: archived
  · Time source: git-log preferred, "migrated-unknown" fallback
  · .obsidian/graph.json: 1 new colorGroup (if .obsidian/ exists)

Stage 4 (Opt #5): journal time-axis
  · <project_journal_entries> entries from projects/*/journal/ merge to meta/journal/<date>.md
  · Project index.md files get ## Journal section (Dataview + Recent 5)

Stage 5 (Opt #6): areas seeds
  · Truly empty areas to delete: <truly_empty>
  · Quasi-empty areas to keep + report: <quasi_empty>

Stage 6 (Opt #7): user-patterns.md → meta/
  · <up_at_root == yes ? "1 file move" : "skip (not at root)">

Stage 7 (Opt #8): frontmatter cross-references
  · All meta/decisions/**/*.md get applied_methods + journal_date fields
  · All meta/methods/*.md get born_from_decisions field + ## Applied in decisions section
  · All meta/journal/*.md get referenced_decisions + referenced_methods fields

── Summary ──
Estimated runtime: 30-60 seconds for typical vault
Vault file count: <N> before → <N> after (no net change, only moves + frontmatter edits)

Proceed? (回 "go" 继续 / "stop" 取消)
```

### 1.3 等待用户回复

- `go` / `继续` → 进入 Stage 1 execute
- `stop` / `取消` / 其他 → 退出

---

## Stage 1 · Execute: `_meta/` → `meta/` rename

```bash
if [ -d "_meta" ]; then
  git mv _meta meta
  echo "✓ Stage 1 complete: _meta/ → meta/"
fi
```

写 progress file（注意：此时 `meta/` 已经是新路径）:
```bash
mkdir -p meta
cat > meta/.migration-progress.md <<EOF
---
migration_id: mig-v1.9-$(date -u +%Y-%m-%dT%H%M%SZ)
started_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
current_stage: 1
completed_stages: [1]
---
EOF
```

**After Stage 1**: `_meta/` no longer exists; all subsequent stages use `meta/`.

---

## Stage 1.5 · Execute: `meta/inbox/` → `meta/queue/`

```bash
if [ -d "meta/inbox" ]; then
  git mv meta/inbox meta/queue
fi

# Rewrite README
cat > meta/queue/README.md <<'EOF'
# Queue

System processing queue + agent-to-user notifications. **Not** for raw user material (use vault root `inbox/` for that).

- `to-process/` — items archiver Phase 1 will pick up next adjourn
- `notifications.md` — system messages (overdue maintenance, alerts, etc.)
EOF

git add meta/queue/
echo "✓ Stage 1.5 complete: meta/inbox/ → meta/queue/"
```

Update progress:
```bash
# Update meta/.migration-progress.md current_stage to 1.5, completed_stages to [1, 1.5]
```

---

## Stage 2 · Execute: decisions consolidation

For each `projects/*/decisions/*.md`:

1. Read file + frontmatter
2. Extract `reviewed_at` → derive `<YYYY-MM>`
3. Build new frontmatter:
   - Add `id: dec-<YYYY-MM-DD>-<NNN>` if missing (use per-day sequence; check existing files in target dir for max NNN)
   - Add `title:` (from H1 or first sentence if missing)
   - Add `type: change` (default if missing)
   - Add `projects: [<project-name>]` (from parent dir)
   - Add `domains: []` (empty list — user fills later; archiver may auto-detect)
   - Add `applied_methods: []`
   - Add `journal_date: <YYYY-MM-DD>` (from reviewed_at)
   - Preserve all other existing fields
4. Write to `meta/decisions/<YYYY-MM>/<id>.md`
5. `git rm` old file

For each `meta/incidents/*.no-change.yml` (already at meta/ post-Stage-1):

1. Read YAML
2. Convert to `meta/decisions/<YYYY-MM>/<id>.md` with `type: no_change`
3. Preserve all 7 v1.8.5 Stage 7 fields as frontmatter
4. `git rm` original .yml

For each project index.md, append `## Decisions` section:

````markdown
## Decisions

```dataview
TABLE type, decision
FROM "meta/decisions"
WHERE contains(projects, this.file.parent.name)
SORT reviewed_at DESC
LIMIT 20
```

### Recent (auto-maintained, fallback for non-Dataview users)

<archiver inserts top 5 wikilinks here>
````

Then populate Recent 5 wikilinks by scanning all decisions where `projects` contains this project name, sort by reviewed_at desc, take top 5.

Delete empty dirs:
```bash
find projects/*/decisions/ -type d -empty -delete 2>/dev/null
rmdir meta/incidents/ 2>/dev/null
```

Update progress to completed_stages: [..., 2].

---

## Stage 3 · Execute: archive → frontmatter

```bash
if [ -d "archive" ]; then
  for archived_proj in archive/*/; do
    [ -d "$archived_proj" ] || continue
    proj_name=$(basename "$archived_proj")
    
    # Time source via git log
    ts=$(git log --follow --diff-filter=A --format=%aI -- "archive/$proj_name" 2>/dev/null | tail -1)
    if [ -z "$ts" ]; then
      ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
      archived_at_source="migrated-unknown"
    else
      archived_at_source="git-log"
    fi
    
    # Move
    git mv "archive/$proj_name" "projects/$proj_name"
    
    # Update frontmatter via Edit (preserving existing fields, adding lifecycle_stage + archived_at + archived_at_source)
    # Use Edit tool with replace_all to inject these 3 fields into the frontmatter block of projects/$proj_name/index.md
  done
  
  rmdir archive/ 2>/dev/null
fi
```

For each migrated project, edit `projects/<p>/index.md` frontmatter:

```yaml
---
project: <p>
lifecycle_stage: archived
archived_at: <ts>
archived_at_source: <source>
archived_reason: |
  Migrated from archive/ during v1.9 upgrade. Original archive reason unknown.
# ... preserve other existing fields ...
---
```

Update `.obsidian/graph.json` (if exists) to add archived colorGroup:

```json
{
  "colorGroups": [
    {
      "query": "path:projects/ AND tag:archived",
      "color": {"a": 1, "rgb": 11448499}
    }
    // ... preserve other groups
  ]
}
```

Update progress to completed_stages: [..., 3].

---

## Stage 4 · Execute: journal time-axis merge

For each `projects/*/journal/*.md`:

1. Read file
2. Determine date (from filename or frontmatter)
3. Target: `meta/journal/<YYYY-MM-DD>.md`
4. If target doesn't exist → create with frontmatter:
   ```yaml
   ---
   date: <YYYY-MM-DD>
   projects: [<project>]
   session_ids: []
   type_tags: [<inferred from content>]
   referenced_decisions: []
   referenced_methods: []
   ---
   ```
5. If target exists → append content + update frontmatter:
   - `projects:` add `<project>` if not present
   - `type_tags:` union with inferred tags
6. `git rm` source

For each project index.md, append `## Journal` section (Dataview + Recent 5 wikilinks, same pattern as Decisions section):

````markdown
## Journal

```dataview
TABLE date, type_tags
FROM "meta/journal"
WHERE contains(projects, this.file.parent.name)
SORT date DESC
LIMIT 20
```

### Recent (auto-maintained, fallback for non-Dataview users)

<archiver inserts top 5 wikilinks here>
````

Delete empty `projects/*/journal/` dirs.

Update progress to completed_stages: [..., 4].

---

## Stage 5 · Execute: areas cleanup + README

```bash
mkdir -p areas
truly_empty_deleted=()
quasi_empty_kept=()

for dir in areas/*/; do
  [ -d "$dir" ] || continue
  area_name=$(basename "$dir")
  file_count=$(find "$dir" -type f | wc -l | tr -d ' ')
  
  if [ "$file_count" -eq 0 ]; then
    rmdir "$dir"
    truly_empty_deleted+=("$area_name")
  else
    total_size=$(find "$dir" -type f -exec wc -c {} + 2>/dev/null | tail -1 | awk '{print $1}')
    if [ -n "$total_size" ] && [ "$total_size" -lt 200 ]; then
      quasi_empty_kept+=("$area_name (size: ${total_size}B)")
    fi
  fi
done
```

Write `areas/README.md`:

```markdown
# Areas

长期生活领域，无终点无 deadline。lifeos 不强制任何命名 — 推荐种子可参考下方列表，你可以删减、新增、重命名。

## 推荐种子（人皆有之）

- career  — 工作 / 事业方向
- product — 你在做的产品/项目
- finance — 收支、投资、税务、保险
- health  — 身体、睡眠、营养、运动
- family  — 家人、伴侣、孩子
- social  — 朋友、合作者、社群
- learning — 学习计划、技能升级、个人品牌
- ops     — 数字基建、生活流程、居住环境
- creation — 创作、内容、表达
- spirit  — 价值观、人生方向、精神世界

## 你的 area

<archiver / retrospective auto-maintains this list>
```

Update progress to completed_stages: [..., 5].

---

## Stage 6 · Execute: user-patterns.md → meta/

```bash
if [ -f "user-patterns.md" ]; then
  git mv user-patterns.md meta/user-patterns.md
fi
```

Update progress to completed_stages: [..., 6].

---

## Stage 7 · Execute: frontmatter cross-reference fields

For each `meta/methods/*.md`:
- Add `born_from_decisions: []` to frontmatter (empty list if missing)
- Append `## Applied in decisions` section with Dataview + Recent 5 pattern

For each `meta/decisions/<YYYY-MM>/*.md`:
- Ensure `applied_methods: []` and `journal_date: <YYYY-MM-DD>` (from reviewed_at) are present

For each `meta/journal/<date>.md`:
- Ensure `referenced_decisions: []` and `referenced_methods: []` are present

Best-effort backfill (skip if errors):
- Loop each decision, take `journal_date`, add decision ID to corresponding journal's `referenced_decisions`

Update progress to completed_stages: [..., 7].

---

## Stage 8 · Finalize

### 8.1 Update config.md

Edit `meta/config.md`:
```yaml
migrated_to: v1.9
```

### 8.2 Append migration report to today's journal (DR-1.9.28)

Compute today's date. Open or create `meta/journal/<today>.md`. Append:

```markdown
## HH:MM · v1.9 Migration

### Summary
- Migrated from: v1.8.x
- Started: <iso start>
- Completed: <iso end>
- Duration: <N>s
- Total file operations: <count>

### Per-stage results
- Stage 1 (_meta/→meta/): ✓
- Stage 1.5 (queue rename): ✓ <N> files
- Stage 2 (decisions consolidation): ✓ <N> decisions
- Stage 3 (archive frontmatter): ✓ <N> projects, <git-log count> via git log, <unknown count> migrated-unknown
- Stage 4 (journal time-axis): ✓ <N> entries merged
- Stage 5 (areas cleanup): ✓ <truly_empty> deleted, <quasi_empty> kept
- Stage 6 (user-patterns move): ✓
- Stage 7 (cross-references): ✓

### Warnings
<list any non-fatal issues; empty if none>

### Recommended manual cleanup
<list quasi-empty areas user should review>
```

Also add `migration` to type_tags in that journal's frontmatter.

### 8.3 Final commit

```bash
git add -A
git commit -m "chore(v1.9): migrate vault to v1.9 layout

- _meta/ → meta/ (Opt #1)
- meta/inbox/ → meta/queue/ (Opt #2)
- decisions consolidation to meta/decisions/<YYYY-MM>/ (Opt #3)
- archive frontmatter (Opt #4)
- journal time-axis canonical (Opt #5)
- areas seeds + cleanup (Opt #6)
- user-patterns.md → meta/ (Opt #7)
- cross-reference frontmatter fields (Opt #8)

See meta/journal/<today>.md for full migration report.
Run /verify-v1.9 to validate."
```

### 8.4 Delete progress file

```bash
rm meta/.migration-progress.md
```

### 8.5 Final report

```
✅ /migrate-v1.9 complete.

Duration: <N>s
Files affected: <count>
Git commit: <sha>

Migration report: meta/journal/<today>.md
Verify: /verify-v1.9

Recommended next steps:
1. Run /verify-v1.9 to confirm 8 acceptance criteria
2. If you have GDrive/Notion backends: pause them briefly, let next session-start
   sync push the v1.9 layout cleanly (avoids GDrive 400-op burst)
3. Review meta/journal/<today>.md for any warnings or cleanup recommendations
```

---

## Failure recovery

If any stage fails partway:

1. **Read `meta/.migration-progress.md`** (or `_meta/.migration-progress.md` if Stage 1 hadn't completed) to see completed_stages
2. Report which stage failed and what state the vault is in
3. Suggest `git status` + `git diff` for inspection
4. Suggest `git reset --hard origin/main` (or commit-pre-migration) to rollback
5. After fixing root cause, **re-run /migrate-v1.9** — Pre-flight will detect partial state via missing `migrated_to: v1.9` and resume

The progress file enables (limited) idempotent recovery: re-running won't re-do completed stages.

---

## What this command does NOT do

- Push to remote (user controls)
- Trigger Notion / GDrive sync (next session-start does it naturally)
- Run /verify-v1.9 automatically (user explicitly)
- Fix data quality issues beyond schema (e.g., missing decision rationale)
- Clean up `archive/` non-project content (Stage 0c refuses; user handles manually)

---

**Spec authority**: This prompt implements `_meta/rfc/v1.9-second-brain-structure-optimization.md` §4.1. Any discrepancy → RFC wins.

(Note: the RFC file itself lives at `_meta/rfc/...` because the lifeos dev repo has its own `_meta/` directory. User vaults migrate to `meta/`; the dev repo is a separate refactor decision.)
