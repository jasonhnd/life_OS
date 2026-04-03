# Notion 数据库 Schema

各 agent 读写 Notion 时参考本文件。使用 Notion MCP 工具操作。

## Data Source ID 索引

| 数据库 | Data Source ID |
|--------|---------------|
| 🤔 决策 | `collection://037e10d0-c176-4a45-9b4d-be5e1c4f4b8e` |
| ✅ 任务 | `collection://d831ca0d-d9e0-44db-a6d1-cf354446a5d1` |
| 📓 日志 | `collection://98f3ae3b-9e14-4b35-b065-38b72207aff3` |
| 🎯 目标 | `collection://2a3360f0-ae8b-4803-9bb0-ffbff1e5c0f7` |
| 🏛️ 六部 | `collection://e7a34f51-278d-4051-96bf-b46a687c0bf3` |
| 🎯 项目 | `collection://f56da00c-7b49-44fb-b011-149f23d62750` |

## 六部 Area 页面 URL

创建任务/决策时关联到六部 Area 使用以下 URL：

| 部门 | Page URL |
|------|----------|
| 👥 吏部 · 人 | `3372254edbf881259dc1d405c262aef4` |
| 💰 户部 · 钱 | `3372254edbf881e696e3ec5676814e32` |
| 📖 礼部 · 学习与表达 | `3372254edbf8812ba45be59362a13dc5` |
| ⚔️ 兵部 · 行动 | `3372254edbf8813a93a6c37ed6ea9f59` |
| ⚖️ 刑部 · 规则 | `3372254edbf88155a799d1eaf8abd89d` |
| 🏗️ 工部 · 基建与健康 | `3372254edbf881d5a074e78f0670cc75` |

## 数据库字段（实际属性名）

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
Area         — 关联六部
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
Area         — 关联六部
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
Area         — 关联六部
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
Area         — 关联六部
```

## Orchestrator 存档操作

流程结束后，Orchestrator 按以下顺序存档：

### 1. 创建决策页面

```
data_source_id: collection://037e10d0-c176-4a45-9b4d-be5e1c4f4b8e
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
  Area: [主要相关的六部 page URL]
content: 奏折全文
```

### 2. 创建任务（逐条）

```
data_source_id: collection://d831ca0d-d9e0-44db-a6d1-cf354446a5d1
properties:
  Title: [行动项名称]
  Status: "To Do"
  Priority: [P0/P1/P2/P3]
  date:Due Date:start: [时限日期]
  Area: [负责部门的 page URL]
```

### 3. 创建日志（御史台报告）

```
data_source_id: collection://98f3ae3b-9e14-4b35-b065-38b72207aff3
properties:
  Title: "🔱 御史台 · [旨意] · [日期]"
  date:Date:start: [当天日期]
  Tags: ["御史台"]
content: 御史台报告全文
```

### 4. 创建日志（谏官报告）

```
data_source_id: collection://98f3ae3b-9e14-4b35-b065-38b72207aff3
properties:
  Title: "💬 谏官 · [旨意] · [日期]"
  date:Date:start: [当天日期]
  Tags: ["谏官"]
content: 谏官报告全文
```

## 丞相：查询历史决策

对话开始时，根据用户话题搜索相关历史：

```
1. notion-search: query=[用户话题关键词], data_source_url=collection://037e10d0-c176-4a45-9b4d-be5e1c4f4b8e
2. 如果找到相关决策，用 notion-fetch 读取奏折内容
3. 在上报时附上历史上下文
```

## 早朝官：拉取复盘数据

```
1. notion-search: 查询任务数据库，关键词=当前周期
   data_source_url=collection://d831ca0d-d9e0-44db-a6d1-cf354446a5d1
2. notion-search: 查询目标数据库
   data_source_url=collection://2a3360f0-ae8b-4803-9bb0-ffbff1e5c0f7
3. notion-search: 查询最近日志
   data_source_url=collection://98f3ae3b-9e14-4b35-b065-38b72207aff3
4. 汇总为早朝简报
```

Notion MCP 不可用时，在输出末尾标注"⚠️ Notion 未连接，本次产出未存档"。
