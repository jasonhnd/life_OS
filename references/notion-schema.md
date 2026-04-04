# Notion 数据库 Schema

各 agent 读写 Notion 时参考本文件。使用 Notion MCP 工具操作。

## 重要概念：六部 vs 领域

- **六部**是 AI 朝廷的分析框架（吏/户/礼/兵/刑/工），固定不变
- **领域**是用户生活的实际分区（职业发展/家庭/健康/财务...），由用户自定义
- 两者是独立的。一个决策可能由户部分析财务维度，但对应的领域是"产品与创业"
- Notion 中的 Area 字段关联的是 **🌊 领域**，不是六部

## 数据库发现协议

**所有 data source ID 和 page URL 必须在运行时动态获取，不得硬编码。**

### 初始化步骤（每次会话首次触发 Notion 操作时执行一次）

```
1. notion-search: query="决策" → 获取 ���� 决策 的 data source ID
2. notion-search: query="任务" → 获取 ✅ 任务 的 data source ID
3. notion-search: query="日志" → 获取 📓 日志 的 data source ID
4. notion-search: query="目标" → 获取 🎯 目标 的 data source ID
5. notion-search: query="领域" → 获取 🌊 领域 的 data source ID
6. notion-search: query="项目" → 获取 🎯 项目 的 data source ID
7. 缓存所有 ID，供后续操作使用
```

### 领域关联

存档时需要关联领域（Area 字段），通过名称搜索匹配：

```
notion-search: query=[领域名称], data_source_url=[领域 data source ID]
→ 获取对应领域的 page URL
```

### Notion 不可用时的降级

如果 Notion MCP 不可用或初始化失败：
- 跳过所有 Notion 读写操作
- 在输出末尾标注"⚠️ Notion 未连接，本次产出未存档"
- 系统其余功能正常运行

## 数据库字段（实际属性名）

### 🌊 领域

```
Name         — 领域名称
Description  — 描述
Status       — "Active" | "Inactive"
Review Cycle — "Weekly" | "Monthly" | "Quarterly"
上级领域      — 自关联（支持层级）
```

### 🤔 决策

```
Title        — 旨意
流程类型      — "简单决策" | "三省六部"
启用部门      — ["吏部", "户部", "礼部", "兵部", "刑部", "工部"]
综合评分      — 数字 (1-10)
封驳次数      — 数字
Status       — "Considering" | "Decided" | "Reversed"
Category     — "Career" | "Finance" | "Product" | "Tech" | "Family" | "Life" | "Health"
Outcome      — "Good" | "Neutral" | "Bad" | "TBD"
Date         — 日期（用 date:Date:start）
Tags         — 多选标签
Area         — 关联领域
Actions      — 关联任务
```

页面正文：奏折全文

### ✅ 任务

```
Title        — 任务名称
Status       — "To Do" | "In Progress" | "Waiting" | "Done" | "Cancelled"
Priority     — "P0" | "P1" | "P2" | "P3"
Due Date     — 截止日期（用 date:Due Date:start）
Context      — "Computer" | "Phone" | "Home" | "Office" | "Call" | "Errand"
Energy       — "High" | "Medium" | "Low"
Area         — 关联领域
Project      — 关联项目
Recurring    — 是否循环（"__YES__" / "__NO__"）
```

### 📓 日志

```
Title        — 日志标题
Date         — 日期（用 date:Date:start）
Mood         — "Great" | "Good" | "Neutral" | "Low" | "Bad"
Energy       — "High" | "Medium" | "Low"
Highlight    — 亮点摘要
Tags         — 多选标签
```

页面正文：报告全文

### 🎯 目标

```
Title        — 目标名称
Status       — "Not Started" | "In Progress" | "Achieved" | "Missed" | "Revised"
Timeframe    — "2026-Q1" | "2026-Q2" | "2026-Q3" | "2026-Q4" | "2026 Annual" | "Long-term"
Progress     — 数字 (0-100)
Key Results  — 关键结果描述
Review Notes — 复盘备注
Area         — 关联领域
Projects     — 关联项目
```

### 🎯 项目

```
Name         — 项目名称
Status       — "Planning" | "Active" | "On Hold" | "Done" | "Dropped"
Priority     — "P0" | "P1" | "P2" | "P3"
Owner        — "Me" | "Shared"
Deadline     — 截止日期（用 date:Deadline:start）
Outcome      — 成果描述
Tags         — 多选标签
Area         — 关联领域
```

## Orchestrator 存档操作

流程结束后，Orchestrator 按以下顺序存档（使用初始化时缓存的 data source ID）：

### 1. 创建决策页面

```
data_source_id: [决策库 ID]
properties:
  Title: [旨意]
  流程类型: "三省六部"
  启用部门: [参与的部门列表]
  综合评分: [总评分]
  封驳次数: [实际封驳次数]
  Status: "Decided"
  Category: [根据旨意判断]
  Outcome: "TBD"
  date:Date:start: [当天日期]
  Area: [搜索领域库，匹配最相关的领域]
content: 奏折全文
```

### 2. 创建任务（逐条）

```
data_source_id: [任务库 ID]
properties:
  Title: [行动项名称]
  Status: "To Do"
  Priority: [P0/P1/P2/P3]
  date:Due Date:start: [时限日期]
  Area: [搜索领域库，匹配最相关的领域]
```

### 3. 创建日志（御史台报告）

```
data_source_id: [日志库 ID]
properties:
  Title: "🔱 御史台 · [旨意] · [日期]"
  date:Date:start: [当天日期]
  Tags: ["御史台"]
content: 御史台报告全文
```

### 4. 创建日志（谏官报告）

```
data_source_id: [日志库 ID]
properties:
  Title: "💬 谏官 · [旨意] · [日期]"
  date:Date:start: [当天日期]
  Tags: ["谏官"]
content: 谏官报告全文
```

## 丞相：查询历史决策

对话开始时，根据用户话题搜索相关历史：

```
1. notion-search: query=[用户话题关键词], data_source_url=[决策库 ID]
2. 如果找到相关决策，用 notion-fetch 读取奏折内容
3. 在上报时附上历史上下文
```

## 早朝官：拉取复盘数据

```
1. notion-search: 查询任务数据库 data_source_url=[任务库 ID]
2. notion-search: 查询目标数据库 data_source_url=[目标库 ID]
3. notion-search: 查询最近日志 data_source_url=[日志库 ID]
4. notion-search: 查询领域库 data_source_url=[领域库 ID]，按 Review Cycle 筛选本周期需要复盘的领域
5. 按领域维度汇总为早朝简报
```
