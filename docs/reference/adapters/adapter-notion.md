# Adapter：Notion

通过 Notion MCP 把标准数据模型操作翻译成 Notion 数据库和页面。

## Notion 结构

Notion 同时支持两种用法：作为完整存储后端（单独选 Notion 时）和作为传输层（与 GitHub/GDrive 并用时）。

### 作为完整后端（仅 Notion）

全部 6 种数据类型映射到 Notion 数据库：

| 数据类型 | Notion 数据库 |
|---------|--------------|
| Decision | 🤔 Decisions |
| Task | ✅ Tasks |
| JournalEntry | 📓 Journal |
| WikiNote | 📚 Wiki |
| Project | 🎯 Projects |
| Area | 🌊 Areas |

### 作为传输层（与 GitHub/GDrive 并用）

仅使用 3 个组件：
- 📬 Inbox（数据库）：设备间消息队列
- 🧠 Status Dashboard（页面）：`_meta/STATUS.md` 的镜像
- 🗄️ Archive：只读归档访问

**重要**：在传输模式下，Notion **没有** Task/Decision/Journal 数据库。若用户在 Notion 里直接编辑 inbox 之外的内容，这些变更对同步协议**不可见**。RETROSPECTIVE 应在首次设置时提醒用户："在传输模式下，所有移动端捕获都走 📬 Inbox。Inbox 之外的 Notion 页面直接编辑不会同步到 GitHub/GDrive。"

## 字段映射

### Decision → 🤔 Decisions

| 标准字段 | Notion Property | Notion Type |
|---------|----------------|-------------|
| title | Title | Title |
| type | 流程类型 | Select：简单决策 / 三省六部 |
| ministries | 启用部门 | Multi-select |
| score | 综合评分 | Number |
| veto_count | 封驳次数 | Number |
| status | Status | Select：Considering / Decided / Reversed |
| category | Category | Select |
| outcome | Outcome | Select：Good / Neutral / Bad / TBD |
| date | Date | Date |
| area | Area | Relation → Areas |
| content | 页面正文 | Page content |

### Task → ✅ Tasks

| 标准字段 | Notion Property | Notion Type |
|---------|----------------|-------------|
| title | Title | Title |
| status | Status | Select：To Do / In Progress / Waiting / Done / Cancelled |
| priority | Priority | Select：P0 / P1 / P2 / P3 |
| due_date | Due Date | Date |
| context | Context | Select |
| energy | Energy | Select |
| project | Project | Relation → Projects |
| area | Area | Relation → Areas |

### JournalEntry → 📓 Journal

| 标准字段 | Notion Property | Notion Type |
|---------|----------------|-------------|
| title | Title | Title |
| date | Date | Date |
| type | Tags | Multi-select |
| mood | Mood | Select |
| energy | Energy | Select |
| content | 页面正文 | Page content |

### WikiNote → 📚 Wiki

| 标准字段 | Notion Property | Notion Type |
|---------|----------------|-------------|
| title | Title | Title |
| tags | Tags | Multi-select |
| content | 页面正文 | Page content |

### Project → 🎯 Projects

| 标准字段 | Notion Property | Notion Type |
|---------|----------------|-------------|
| name | Name | Title |
| status | Status | Select |
| priority | Priority | Select |
| deadline | Deadline | Date |
| area | Area | Relation → Areas |

### Area → 🌊 Areas

| 标准字段 | Notion Property | Notion Type |
|---------|----------------|-------------|
| name | Name | Title |
| description | Description | Text |
| status | Status | Select |
| review_cycle | Review Cycle | Select |

## 标准操作

所有操作使用 Notion MCP 工具。

### Save(type, data)
1. 按上面的映射表把字段映射为 Notion property
2. `notion-create-pages`，parent = 对应数据库
3. 正文内容 → 页面内容

### Update(type, id, data)
1. `notion-update-page`，传入 page_id 和变更的 property
2. 正文变更 → `update_content` 命令

### Archive(type, id)
1. 把 status 改为 archived/done
2. 或通过 `notion-move-pages` 把页面移到 Archive 数据库

### Read(type, id)
1. `notion-fetch` 传入 page ID
2. 把 Notion property 映射回标准字段

### List(type, filters)
1. `notion-search` 或 `notion-query-database-view` 查询对应数据库
2. 把结果映射回标准字段

### Search(keyword)
1. `notion-search`，query = keyword
2. 把结果映射回标准字段，标注来源数据库

### ReadProjectContext(project_id)
1. 读项目页面
2. 查询 project relation 过滤的 tasks
3. 查询 project 过滤的 decisions
4. 查询 project 过滤的 journal

## 变更检测

用于同步：`notion-search` 或 `notion-query-database-view` 按 `last_edited_time > last_sync_time` 过滤

## 删除

同样原则：软删除——通过修改 status。在用户确认前不使用 `notion-move-pages` 移至垃圾桶。

## 初次设置

用户需要：
1. 连接 Notion MCP
   - Claude.ai：Settings → Connected Apps → Notion
   - Claude Code / Gemini CLI / Codex CLI：MCP 配置
2. 在 Notion 中创建所需数据库（或使用提供的模板）
3. 数据库 ID 在运行时通过 `notion-search` 按名称发现——**不硬编码**

## Notion MCP 的特殊性：在主上下文而非 subagent 中运行（v1.6.2a）

Notion MCP 工具是**环境特定**的——它们在 subagent 里**不可用**。因此：

- archiver subagent 的 Phase 4 只做 git 同步
- Notion 同步被移出 archiver，由编排器（orchestrator，即主上下文）执行，因为主上下文有 MCP 访问权
- 见 `pro/CLAUDE.md` 的 Step 10a：archiver 返回后，主上下文执行 Notion 同步

这是 v1.6.2a 的关键修复——此前 archiver 在 subagent 中尝试 Notion 同步，始终报"Notion MCP not connected"。

## 与其他后端同时使用

- Notion 通常作为 sync（传输层），primary 是 GitHub 或 GDrive
- 若 Notion 是唯一后端，它自动成为 primary，承担完整读写
- `GitHub + Notion` 是最常见的组合：GitHub 作权威源，Notion 供移动端查看和 inbox 写入
- 详见 `references/data-model.md` 的 Multi-Backend Rules

## 已知限制

- Notion API 有速率限制（每集成每秒 3 请求），批量写入时需要节流
- Notion 对 markdown 支持有限（代码块、数学公式、复杂表格可能渲染不完美）
- 数据库 schema 变更需要管理员手动更新，adapter 不自动修改 Notion 端 schema
- Notion 没有版本历史 API——想"回滚"变更只能从 Notion 内置历史中手动恢复
