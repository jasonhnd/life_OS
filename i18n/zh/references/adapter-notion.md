# 适配器：Notion

通过 Notion MCP 将标准数据模型操作翻译为 Notion 数据库和页面。

## Notion 结构

Notion 既可作为完整的存储后端（当被选择时），也可作为传输层（与 GitHub/GDrive 并用时）。

### 作为完整后端（仅 Notion）

所有 6 种数据类型映射到 Notion 数据库：

| 数据类型 | Notion 数据库 |
|-----------|----------------|
| Decision | 🤔 Decisions |
| Task | ✅ Tasks |
| JournalEntry | 📓 Journal |
| WikiNote | 📚 Wiki |
| Project | 🎯 Projects |
| Area | 🌊 Areas |

### 作为传输层（与 GitHub/GDrive 并用）

仅使用 3 个组件：
- 📬 Inbox（数据库）：设备间的消息队列
- 🧠 Status Dashboard（页面）：`_meta/STATUS.md` 的镜像
- 🗄️ Archive：只读归档访问

## 字段映射

### Decision → 🤔 Decisions

| 标准字段 | Notion 属性 | Notion 类型 |
|---------------|----------------|-------------|
| title | Title | Title |
| type | 流程类型 | Select: 简单决策 / 三省六部 |
| ministries | 启用部门 | Multi-select |
| score | 综合评分 | Number |
| veto_count | 封驳次数 | Number |
| status | Status | Select: Considering / Decided / Reversed |
| category | Category | Select |
| outcome | Outcome | Select: Good / Neutral / Bad / TBD |
| date | Date | Date |
| area | Area | Relation → Areas |
| content | 页面正文 | Page content |

### Task → ✅ Tasks

| 标准字段 | Notion 属性 | Notion 类型 |
|---------------|----------------|-------------|
| title | Title | Title |
| status | Status | Select: To Do / In Progress / Waiting / Done / Cancelled |
| priority | Priority | Select: P0 / P1 / P2 / P3 |
| due_date | Due Date | Date |
| context | Context | Select |
| energy | Energy | Select |
| project | Project | Relation → Projects |
| area | Area | Relation → Areas |

### JournalEntry → 📓 Journal

| 标准字段 | Notion 属性 | Notion 类型 |
|---------------|----------------|-------------|
| title | Title | Title |
| date | Date | Date |
| type | Tags | Multi-select |
| mood | Mood | Select |
| energy | Energy | Select |
| content | 页面正文 | Page content |

### WikiNote → 📚 Wiki

| 标准字段 | Notion 属性 | Notion 类型 |
|---------------|----------------|-------------|
| title | Title | Title |
| tags | Tags | Multi-select |
| content | 页面正文 | Page content |

### Project → 🎯 Projects

| 标准字段 | Notion 属性 | Notion 类型 |
|---------------|----------------|-------------|
| name | Name | Title |
| status | Status | Select |
| priority | Priority | Select |
| deadline | Deadline | Date |
| area | Area | Relation → Areas |

### Area → 🌊 Areas

| 标准字段 | Notion 属性 | Notion 类型 |
|---------------|----------------|-------------|
| name | Name | Title |
| description | Description | Text |
| status | Status | Select |
| review_cycle | Review Cycle | Select |

## 操作

所有操作使用 Notion MCP 工具。

### Save(type, data)
1. 按上方映射表将字段映射到 Notion 属性
2. `notion-create-pages`，parent = 对应的数据库
3. 正文内容 → 页面内容

### Update(type, id, data)
1. `notion-update-page`，传入 page_id 和变更属性
2. 正文内容变更 → `update_content` 命令

### Archive(type, id)
1. 将状态更新为 archived/done
2. 或通过 `notion-move-pages` 将页面移至 Archive 数据库

### Read(type, id)
1. `notion-fetch`，传入 page ID
2. 将 Notion 属性映射回标准字段

### List(type, filters)
1. 在对应数据库上执行 `notion-search` 或 `notion-query-database-view`
2. 将结果映射回标准字段

### Search(keyword)
1. `notion-search`，query = keyword
2. 将结果映射回标准字段，标注来源数据库

### ReadProjectContext(project_id)
1. 读取项目页面
2. 按项目关系筛选查询任务
3. 按项目筛选查询决策
4. 按项目筛选查询日志

## 变更检测

用于同步：`notion-search` 或 `notion-query-database-view` 筛选 `last_edited_time > last_sync_time`

## 删除

相同原则：通过更改状态实现软删除。在用户确认之前不使用 `notion-move-pages` 移至回收站。

## 设置

用户需要：
1. 连接 Notion MCP（Claude.ai：设置 → 已连接应用 → Notion。Claude Code：MCP 配置）
2. 在 Notion 中创建所需数据库（或使用提供的模板）
3. 数据库 ID 在运行时通过 `notion-search` 按名称发现——无需硬编码
