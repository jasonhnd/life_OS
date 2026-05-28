# 适配器：GitHub（second-brain 仓库）

将标准数据模型操作翻译为存储在 Git 仓库中带有 YAML front matter 的 .md 文件。

## 文件格式

每条数据记录是一个 `.md` 文件：
- **Front matter**（`---` 标记之间的 YAML）：结构化字段
- **正文**：内容/文本字段

```yaml
---
type: decision
title: "职业转型可行性"
status: decided
score: 6.8
date: 2026-04-08
project: career-transition
last_modified: "2026-04-08T15:30:00Z"
---

[奏折正文]
```

## 目录路径映射

| 数据类型 | 路径 | 文件名规则 |
|---------|------|-----------|
| Decision（v1.9 统一） | `meta/decisions/{YYYY-MM}/` | `dec-{YYYY-MM-DD}-{NNN}.md` |
| Task（项目） | `projects/{p}/tasks/` | `{slug}.md` |
| Task（领域） | `areas/{a}/tasks/` | `{slug}.md` |
| JournalEntry（v1.9 时间轴） | `meta/journal/` | `{YYYY-MM-DD}.md`（每日单文件，多条追加） |
| WikiNote | `wiki/` | `{slug}.md` |
| Project | `projects/{p}/index.md` | 固定名称（含 lifecycle_stage frontmatter；archived 项目留此处） |
| Area | `areas/{a}/index.md` | 固定名称 |
| UserPatterns（v1.9） | `meta/user-patterns.md` | 固定名称（v1.9 从 root 移入） |

> **v1.9 变化**：决策统一到 `meta/decisions/{YYYY-MM}/`（不再 `projects/*/decisions/` 分裂）；journal 时间轴 canonical（不再 `projects/*/journal/`）；archived 项目靠 frontmatter 留在 `projects/`（无 `archive/` 目录）；`user-patterns.md` 移入 `meta/`。

## 操作

### Save(type, data)
1. 从日期 + slug 化标题生成文件名
2. 写入带有 front matter + 正文的 .md 文件
3. `git add` 该文件

### Update(type, id, data)
1. 读取现有文件
2. 将变更字段合并到 front matter
3. 更新 `last_modified` 时间戳
4. 写回文件
5. `git add` 该文件

### Archive(type, id)

**v1.9 语义拆分**（DR-1.9.4）：
- **项目**：不移动。在 `projects/{id}/index.md` frontmatter 设 `lifecycle_stage: archived` + `archived_at` + `archived_at_source`，项目留在 `projects/` 保护 wikilinks。`git add projects/{id}/index.md`。
- **其他类型**（sessions、eval 等）：在各自树内 legacy 子归档（如 `meta/eval-history/_archive/`），非项目 archive，仍有效。

### Read(type, id)
1. 读取 .md 文件
2. 将 front matter 解析为结构化数据
3. 返回正文作为 content

### List(type, filters)
1. 在类型对应目录中 Glob 文件
2. 对每个文件解析 front matter
3. 按指定字段值过滤
4. 返回匹配记录

### Search(keyword)
1. `grep -r "{keyword}" ~/second-brain/` 跨所有目录
2. 解析匹配文件的 front matter
3. 返回带有源路径的结果

### ReadProjectContext(project_id)
1. 读取 `projects/{p}/index.md`
2. Glob `projects/{p}/tasks/*.md`
3. Glob `meta/decisions/*/*.md`（v1.9，按 projects frontmatter 过滤）
4. Glob `meta/journal/*.md`（v1.9，按 projects frontmatter 过滤）
5. 返回所有已解析内容

## 变更检测

用于同步：`git log --since="{last_sync_time}" --name-only --format=""`

返回自上次同步以来变更的文件列表。解析每个文件获取 type + id + last_modified。

## 删除

在 front matter 中标记：`_deleted: true`。在用户确认跨所有后端删除前，不执行 `git rm`。

## Commit 规范

### 退朝时（写入 outbox）

```bash
git add meta/outbox/{session-id}/
git commit -m "[life-os] session {session-id} output"
git push
```

只暂存 outbox 目录。退朝时不修改主文件（projects/、STATUS.md、meta/user-patterns.md）。

### 上朝时（合并 outbox）

```bash
# 将 outbox 内容合并到主目录后（v1.9 路径）：
git add projects/ areas/ meta/decisions/ meta/journal/ meta/methods/ meta/STATUS.md meta/user-patterns.md SOUL.md
git rm -r meta/outbox/{merged-session-ids}/
git commit -m "[life-os] merge {N} outbox sessions"
git push
```

### 通用规则

**绝不使用 `git add -A` 或 `git add .`** —— 这会意外提交敏感文件（.env、.claude/、凭据、临时文件）。只暂存 Life OS 明确写入的文件。

## Worktree 维护

Claude Code 在 `.claude/worktrees/` 下创建临时 worktree。这可能导致以下问题：

1. **跨平台干扰**：Gemini / Antigravity 可能因大量 worktree 目录涌入上下文而崩溃
2. **仓库迁移后路径失效**：若仓库位置变更（如 Dropbox → iCloud），worktree 的 `.git` 文件指向旧路径，导致所有 git 操作失败

### 预防措施

- 将 `.claude/worktrees/` 加入 `.gitignore`
- Claude Code worktree session 结束后，选择**移除**（而非保留）
- 迁移仓库位置前，先清理（在终端中手动执行以下命令）：

```text
# 用户手动恢复命令 — 禁止自动执行；需要人工确认
git worktree prune
rm -rf .claude/worktrees/
git config --unset core.hooksPath   # 若已设置旧路径
```

### 恢复

若 git 报告 `fatal: not a git repository: /old/path/.git/worktrees/...`，请**在终端中手动执行**以下命令（agent 未经用户明确确认不得执行这些命令 — 参见 GLOBAL.md 安全边界 #1）：

```text
# 用户手动恢复命令 — 禁止自动执行；需要人工确认
git worktree prune                  # 清理 git 级别引用
rm -rf .claude/worktrees/           # 删除旧 worktree 目录
git config --unset core.hooksPath   # 移除损坏的 hooks 路径
git config --unset extensions.worktreeConfig  # 移除 worktree 扩展标志
```
