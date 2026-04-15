# 适配器：Google Drive

将标准数据模型操作翻译为存储在 Google Drive 中带有 YAML front matter 的 .md 文件。

## 文件格式

**与 GitHub 适配器完全相同**：带有 YAML front matter 的 .md 文件。相同格式，相同结构。这意味着文件可在 GitHub 和 Google Drive 之间互相移植——复制/移动无需转换。

## 目录结构

GitHub second-brain 结构的镜像，以 Google Drive 文件夹层级形式存在：

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

## 操作

所有操作使用 Google Drive MCP 工具。

### Save(type, data)
1. 根据日期 + slugified 标题生成文件名
2. 创建 .md 内容（front matter + 正文）
3. 通过 Google Drive MCP 上传到正确的文件夹路径

### Update(type, id, data)
1. 通过 Google Drive MCP 读取现有文件
2. 解析 front matter，合并变更
3. 更新 `last_modified` 时间戳
4. 上传更新后的文件（覆盖）

### Archive(type, id)
1. 通过 Google Drive MCP 将文件移动到 `archive/{original-path}/`

### Read(type, id)
1. 通过 Google Drive MCP 下载文件
2. 解析 front matter + 正文
3. 返回结构化数据

### List(type, filters)
1. 通过 Google Drive MCP 列出该类型文件夹中的文件
2. 下载并解析每个文件的 front matter
3. 按指定字段值筛选

### Search(keyword)
1. 使用 Google Drive MCP 搜索（fullText contains '{keyword}'）
2. 下载并解析匹配文件

### ReadProjectContext(project_id)
1. 列出并下载 `projects/{p}/` 下的所有文件

## 变更检测

用于同步：Google Drive MCP 查询 `modifiedTime > '{last_sync_time}'`

返回自上次同步以来修改的文件列表。下载并解析每个文件。

## 删除

与 GitHub 相同：在 front matter 中标记 `_deleted: true`。在用户确认之前不从 Drive 实际删除。

## 无 Git 历史

Google Drive 没有 git 历史。变更检测完全依赖 `modifiedTime`。Drive 的内置版本历史提供一定的恢复能力。

## 设置

用户需要：
1. 连接 Google Drive MCP
2. 在 Drive 中创建一个 `second-brain` 根文件夹
3. 创建文件夹结构（可由RETROSPECTIVE在首次运行时完成）
