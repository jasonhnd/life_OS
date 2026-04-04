# 第二大脑 — 搭建指南

Life OS 的 AI 朝廷负责决策和执行，但 AI 没有长期记忆。**第二大脑**是朝廷的档案馆 —— 让每次对话的产出持久化存储，让丞相在新对话中能查阅历史档案。

本文是搭建指南。关于 Notion 集成的概念和数据流，见 [README → Notion 集成](../README.md#notion-集成数据层)。

---

## PARA 与三省六部的关系

**六部只存在于 AI 内部逻辑（SKILL.md），不存在于数据结构中。**

- 数据层 = PARA（你组织信息的方式）：Areas = 生活领域（职业/家庭/健康…）
- SKILL.md = 三省六部（AI 处理事情的方式）
- 两层通过决策数据库的"启用部门"字段关联（流程日志），不混在一起

你在数据层看到的永远是生活领域，六部只出现在决策记录中。

---

## Notion 搭建

### 连接 Notion MCP

**Claude.ai** — Settings → Connected Apps → Notion，授权你的 workspace。

**Claude Code** — 在 MCP 配置中添加：

```json
{
  "mcpServers": {
    "notion": {
      "type": "url",
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

### 数据库结构

在 Notion 中创建一个顶层页面 **🧠 第二大脑**，按以下分组建立数据库：

```
🧠 第二大脑

── 📥 收件箱 ──
📥 收件箱

── ⚡ 行动 ──
✅ 任务
🎯 项目
📋 会议

── 🧭 方向 ──
🌊 领域（PARA Areas：职业发展、家庭、健康…）
🎯 目标
🤔 决策

── 📦 记录 ──
📓 日志
👥 人脉
💰 财务
🏥 健康

── 📚 知识 ──
📚 资源库
📌 书签

── 🗄️ 冷藏 ──
🗄️ 归档
```

### 核心数据库字段

#### 🌊 领域（先建这个，其他数据库 Relation 到它）

| 属性 | 类型 | 说明 |
|------|------|------|
| Name | Title | 领域名称 |
| Description | Text | 描述 |
| Status | Select | Active / Inactive |
| Review Cycle | Select | Weekly / Monthly / Quarterly |
| 上级领域 | Relation → 自身 | 支持层级结构 |

领域由你自定义，比如：

```
🌊 领域
├── 💼 职业发展 (Monthly)
│     └── 当前公司 (Weekly)
├── 🚀 产品与创业 (Weekly)
├── 💰 财务管理 (Monthly)
├── 👨‍👩‍👧‍👦 家庭 (Weekly)
├── 🤝 社交关系 (Monthly)
├── 🏥 健康 (Monthly)
├── 🏠 生活运营 (Monthly)
├── 📖 学习 (Weekly)
├── ✍️ 创作 (Weekly)
└── 🧘 精神 (Quarterly)
```

#### ✅ 任务

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 任务名称 |
| Status | Select | To Do / In Progress / Waiting / Done / Cancelled |
| Priority | Select | P0 / P1 / P2 / P3 |
| Due Date | Date | 截止日期 |
| Energy | Select | High / Medium / Low |
| Context | Select | Computer / Phone / Home / Office / Call / Errand |
| Area | Relation → 领域 | 关联到哪个领域 |
| Project | Relation → 项目 | 关联到哪个项目 |

#### 🤔 决策

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 旨意 |
| 流程类型 | Select | 简单决策 / 三省六部 |
| 启用部门 | Multi-select | 吏部 / 户部 / 礼部 / 兵部 / 刑部 / 工部 |
| 综合评分 | Number | 1-10 |
| 封驳次数 | Number | 门下省封驳次数 |
| Status | Select | Considering / Decided / Reversed |
| Category | Select | Career / Finance / Product / Tech / Family / Life / Health |
| Outcome | Select | Good / Neutral / Bad / TBD |
| Date | Date | 决策日期 |
| Area | Relation → 领域 | 主要相关领域 |
| Actions | Relation → 任务 | 产出的行动项 |

建议新建视图 **📜 朝政记录**：过滤 `流程类型 = 三省六部`，按 Date 倒序。

#### 📓 日志

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 日志标题 |
| Date | Date | 日期 |
| Mood | Select | Great / Good / Neutral / Low / Bad |
| Energy | Select | High / Medium / Low |
| Highlight | Text | 亮点摘要 |
| Tags | Multi-select | 御史台 / 谏官 / 早朝简报 / 手动记录 |

#### 🎯 目标

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 目标名称 |
| Status | Select | Not Started / In Progress / Achieved / Missed / Revised |
| Timeframe | Select | 2026-Q1 / Q2 / Q3 / Q4 / Annual / Long-term |
| Progress | Number | 0-100 |
| Key Results | Text | 关键结果 |
| Area | Relation → 领域 | 关联领域 |
| Projects | Relation → 项目 | 关联项目 |

#### 🎯 项目

| 属性 | 类型 | 说明 |
|------|------|------|
| Name | Title | 项目名称 |
| Status | Select | Planning / Active / On Hold / Done / Dropped |
| Priority | Select | P0 / P1 / P2 / P3 |
| Owner | Select | Me / Shared |
| Deadline | Date | 截止日期 |
| Area | Relation → 领域 | 关联领域 |

---

## 适配其他平台

第二大脑不绑定 Notion。核心是 **领域数据库 + 任务/决策/日志/目标的关联**。任何支持以下能力的平台都可以用：

| 需要的能力 | 说明 |
|-----------|------|
| 结构化数据库 | 能建表、有字段类型 |
| 关联/关系 | 数据库之间能互相引用 |
| 富文本页面 | 奏折和报告需要存长文 |
| API 或 MCP 访问 | AI 能读写数据 |

### 可选平台

| 平台 | MCP 支持 | 适合场景 |
|------|---------|---------|
| **Notion** | 官方 MCP | 最成熟，关系型数据库+富文本 |
| **Obsidian** | 社区 MCP | 偏好本地 Markdown，隐私优先 |
| **Google Sheets** | 官方 MCP | 简单表格，不需要富文本 |
| **Airtable** | 社区 MCP | 强关系型数据库，弱富文本 |
| **Linear** | 官方 MCP | 偏项目管理，任务追踪强 |
| **本地文件** | 内置 | 用 Markdown 文件+目录结构 |

### 适配要点

1. **领域是骨架** — 先建好领域分类作为关联锚点
2. **决策库最重要** — 跨会话连续性的核心，必须能搜索+读取全文
3. **任务库次之** — 早朝官复盘需要知道什么完成了、什么逾期了
4. **日志可以最简** — 最低限度是一个带日期和标签的富文本列表

---

## 不连接数据层

Life OS 不连接数据层时，所有决策和分析功能照常工作，只是：
- 没有跨会话记忆（每次对话从零开始）
- 没有自动存档（产出在对话结束后消失）
- 流程结束会标注"⚠️ 数据层未连接，本次产出未存档"
