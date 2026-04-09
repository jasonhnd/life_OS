# 适配器：GitHub（second-brain 仓库）

将标准数据模型操作翻译为存储在 Git 仓库中带有 YAML front matter 的 .md 文件。

## 文件格式

每条数据记录是一个 `.md` 文件：
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

[奏折全文在此]
```

## 目录路径映射

| 数据类型 | 路径 | 文件名模式 |
|-----------|------|-----------------|
| Decision（项目级） | `projects/{p}/decisions/` | `{date}-{slug}.md` |
| Decision（跨领域） | `_meta/decisions/` | `{date}-{slug}.md` |
| Task（项目级） | `projects/{p}/tasks/` | `{slug}.md` |
| Task（领域级） | `areas/{a}/tasks/` | `{slug}.md` |
| JournalEntry | `_meta/journal/` | `{date}-{type}.md` |
| WikiNote | `wiki/` | `{slug}.md` |
| Project | `projects/{p}/index.md` | 固定名称 |
| Area | `areas/{a}/index.md` | 固定名称 |

## 操作

### Save(type, data)
1. 根据日期 + slugified 标题生成文件名
2. 写入带有 front matter + 正文的 .md 文件
3. `git add` 该文件

### Update(type, id, data)
1. 读取现有文件
2. 将变更字段合并到 front matter
3. 更新 `last_modified` 时间戳
4. 写回
5. `git add` 该文件

### Archive(type, id)
1. 将文件移动到 `archive/{original-path}/`
2. `git add` 旧路径和新路径

### Read(type, id)
1. 读取 .md 文件
2. 解析 front matter 为结构化数据
3. 返回正文作为内容

### List(type, filters)
1. 在该类型的目录中 Glob 查找文件
2. 对每个文件解析 front matter
3. 按指定字段值筛选
4. 返回匹配记录

### Search(keyword)
1. `grep -r "{keyword}" ~/second-brain/` 跨所有目录搜索
2. 解析匹配文件的 front matter
3. 返回结果及源路径

### ReadProjectContext(project_id)
1. 读取 `projects/{p}/index.md`
2. Glob `projects/{p}/tasks/*.md`
3. Glob `projects/{p}/decisions/*.md`
4. Glob `projects/{p}/journal/*.md`
5. 返回所有解析结果

## 变更检测

用于同步：`git log --since="{last_sync_time}" --name-only --format=""`

返回自上次同步以来变更的文件列表。解析每个文件以获取类型 + id + last_modified。

## 删除

在 front matter 中标记：`_deleted: true`。在用户确认跨所有后端之前，不执行 `git rm`。

## 提交约定

所有写入完成后：`git add -A && git commit -m "[life-os] {summary}" && git push`
