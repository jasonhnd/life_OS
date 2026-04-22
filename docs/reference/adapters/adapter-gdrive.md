# Adapter：Google Drive

把标准数据模型操作翻译成 `.md` 文件 + YAML front matter，存于 Google Drive。

## 文件格式

**与 GitHub adapter 完全一致**：`.md` 文件 + YAML front matter。格式相同、结构相同。这意味着文件在 GitHub 和 Google Drive 之间**可迁移**——直接复制/移动，无需转换。

## 目录结构

Google Drive 中的文件夹层级镜像 GitHub second-brain 结构：

```
second-brain/          ← Google Drive 中的根文件夹
├── inbox/
├── _meta/
├── projects/{name}/
├── areas/{name}/
├── wiki/
├── archive/
└── templates/
```

## 标准操作

所有操作使用 Google Drive MCP 工具。

### Save(type, data)
1. 从日期 + slug 化的标题生成文件名
2. 创建 `.md` 内容（front matter + 正文）
3. 通过 Google Drive MCP 上传到正确的文件夹路径

### Update(type, id, data)
1. 通过 Google Drive MCP 读取既有文件
2. 解析 front matter，合并变更
3. 更新 `last_modified` 时间戳
4. 上传覆盖

### Archive(type, id)
1. 通过 Google Drive MCP 把文件移到 `archive/{original-path}/`

### Read(type, id)
1. 通过 Google Drive MCP 下载文件
2. 解析 front matter + 正文
3. 返回结构化数据

### List(type, filters)
1. 通过 Google Drive MCP 列出该类型文件夹的文件
2. 下载并解析每个文件的 front matter
3. 按指定字段值过滤

### Search(keyword)
1. 使用 Google Drive MCP 搜索（`fullText contains '{keyword}'`）
2. 下载并解析匹配文件

### ReadProjectContext(project_id)
1. 列出并下载 `projects/{project}/` 下所有文件

## 变更检测

用于同步：Google Drive MCP 查询 `modifiedTime > '{last_sync_time}'`

返回自上次同步以来修改的文件列表。下载并解析每个。

## 删除

与 GitHub 相同：在 front matter 中标记 `_deleted: true`。在用户确认前**不**真正从 Drive 删除。

## 无 Git 历史

Google Drive 没有 git 历史。变更检测完全依赖 `modifiedTime`。Drive 内置的版本历史提供一定的恢复能力。

## 初次设置

用户需要：
1. 连接 Google Drive MCP
2. 在 Drive 根目录下创建 `second-brain` 文件夹
3. 创建目录结构（RETROSPECTIVE 首次运行时可自动创建）

## 与 GitHub adapter 的对比

| 维度 | GitHub | Google Drive |
|------|--------|-------------|
| 文件格式 | .md + front matter | 完全相同 |
| 目录结构 | 本地 repo | Drive 文件夹 |
| 变更检测 | git log --since | modifiedTime > last_sync |
| 版本历史 | 完整 git 历史 | Drive 内置版本 |
| 协作 | git 多分支 | Drive 共享 |
| 搜索 | grep | Google Drive fullText 搜索 |
| 适合人群 | 技术用户 | 非技术用户 |

## 移动端考虑

- Google Drive 的移动端 App 可以直接查看 .md 文件（需第三方渲染器或文本查看器）
- 不像 GitHub，Drive 不需要 "git clone" 就能同步——所有变更通过 MCP 透明完成
- Drive 的离线模式允许在无网络时查看已缓存文件

## 与其他后端同时使用

- GDrive 可以作为 primary，也可以作为 sync
- `GitHub + GDrive`：GitHub primary，GDrive sync（文件格式完全一致，同步简单）
- `GDrive + Notion`：GDrive primary，Notion sync（Notion 仅作 transport 层）
- 详见 `references/data-model.md` 的 Multi-Backend Rules

## 已知限制

- `modifiedTime` 粒度为秒级，并发写入可能导致时间戳冲突
- Drive 没有"原子合并"能力——多个后端同步变化时，需要在应用层做冲突解决
- 大量文件（数千个）时 `list files` 可能分页，需要 adapter 层循环拉取
