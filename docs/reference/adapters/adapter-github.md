# Adapter：GitHub（second-brain repo）

把标准数据模型操作翻译成 `.md` 文件 + YAML front matter，存于 Git 仓库。

## 文件格式

每条数据记录都是一个 `.md` 文件：
- **Front matter**（`---` 标记之间的 YAML）：结构化字段
- **正文**：内容/文本字段

```yaml
---
type: decision
title: "Career change feasibility"
status: decided
score: 6.8
date: 2026-04-08
project: career-transition
last_modified: "2026-04-08T15:30:00Z"
---

[奏折全文写在这里]
```

## 目录路径映射

| 数据类型 | 路径 | 文件名模式 |
|---------|------|-----------|
| Decision（项目） | `projects/{project}/decisions/` | `{date}-{slug}.md` |
| Decision（跨域） | `_meta/decisions/` | `{date}-{slug}.md` |
| Task（项目） | `projects/{project}/tasks/` | `{slug}.md` |
| Task（area） | `areas/{area}/tasks/` | `{slug}.md` |
| JournalEntry | `_meta/journal/` | `{date}-{type}.md` |
| WikiNote | `wiki/` | `{slug}.md` |
| Project | `projects/{project}/index.md` | 固定名 |
| Area | `areas/{area}/index.md` | 固定名 |

## 标准操作

### Save(type, data)
1. 从日期 + slug 化的标题生成文件名
2. 写 `.md` 文件（front matter + 正文）
3. `git add` 该文件

### Update(type, id, data)
1. 读取既有文件
2. 把变更字段合并到 front matter
3. 更新 `last_modified` 时间戳
4. 写回
5. `git add` 该文件

### Archive(type, id)
1. 文件移到 `archive/{original-path}/`
2. `git add` 两端路径

### Read(type, id)
1. 读取 `.md` 文件
2. 把 front matter 解析成结构化数据
3. 把正文作为 content 返回

### List(type, filters)
1. Glob 匹配该类型目录中的文件
2. 每个文件解析 front matter
3. 按指定字段值过滤
4. 返回匹配记录

### Search(keyword)
1. `grep -r "{keyword}" ~/second-brain/` 跨所有目录
2. 解析匹配文件的 front matter
3. 返回结果带源路径

### ReadProjectContext(project_id)
1. 读 `projects/{project}/index.md`
2. Glob `projects/{project}/tasks/*.md`
3. Glob `projects/{project}/decisions/*.md`
4. Glob `projects/{project}/journal/*.md`
5. 全部解析后返回

## 变更检测

用于同步：`git log --since="{last_sync_time}" --name-only --format=""`

返回自上次同步以来变化的文件列表。逐个解析，得到 type + id + last_modified。

## 删除

在 front matter 中标记：`_deleted: true`。在用户跨后端确认前**不**执行 `git rm`。

## 提交约定

### Adjourn 时（写入 outbox）

```bash
git add _meta/outbox/{session_id}/
git commit -m "[life-os] session {session_id} output"
git push
```

**只** stage outbox 目录。Adjourn 期间绝不碰主文件（projects/、STATUS.md、user-patterns.md）。

### Start Court 时（合并 outbox）

```bash
# 把 outbox 内容合并到主目录之后：
git add projects/ areas/ _meta/journal/ _meta/STATUS.md user-patterns.md SOUL.md
git rm -r _meta/outbox/{merged-session-ids}/
git commit -m "[life-os] merge {N} outbox sessions"
git push
```

### 通用规则

**绝不使用 `git add -A` 或 `git add .`** —— 这些命令会误提交敏感文件（.env、.claude/、凭证、临时文件）。只 stage Life OS 明确写入的文件。

## Worktree 维护

Claude Code 会在 `.claude/worktrees/` 下创建临时 worktree。这些可能引发问题：

1. **跨平台干扰**：Gemini / Antigravity 可能被大量的 worktree 目录淹没上下文
2. **仓库迁移后路径断裂**：repo 搬家（例如 Dropbox → iCloud）后，worktree 的 `.git` 文件指向旧路径，所有 git 操作失败

### 预防

- 把 `.claude/worktrees/` 加到 `.gitignore`
- Claude Code worktree 会话结束后，选择 **remove**（不是 keep）
- 迁移 repo 前先清理

> ⚠️ **手动恢复手册（仅限人工执行）** —— 以下命令涉及破坏性操作（`rm -rf`、`git config --unset`）。Agent 不得自动执行，必须由用户在自己终端中手动运行。GLOBAL.md 安全边界 #1 禁止 agent 未经确认执行破坏性命令。

```text
# HUMAN ONLY — DO NOT auto-execute
git worktree prune
rm -rf .claude/worktrees/
git config --unset core.hooksPath   # 若指向旧路径
```

### 恢复

若 git 报错 `fatal: not a git repository: /old/path/.git/worktrees/...`：

> ⚠️ **手动恢复手册（仅限人工执行）** —— 以下命令涉及破坏性操作（`rm -rf`、`git config --unset`）。Agent 不得自动执行，必须由用户在自己终端中手动运行。GLOBAL.md 安全边界 #1 禁止 agent 未经确认执行破坏性命令。

```text
# HUMAN ONLY — DO NOT auto-execute
git worktree prune                  # 清理 git 级引用
rm -rf .claude/worktrees/           # 移除陈旧 worktree 目录
git config --unset core.hooksPath   # 移除破损的 hooks path
git config --unset extensions.worktreeConfig  # 移除 worktree 扩展标志
```
