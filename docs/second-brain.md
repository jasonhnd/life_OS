# 第二大脑 — 数据持久化指南

Life OS 的 AI 朝廷负责决策和执行，但 AI 没有长期记忆。**第二大脑**是朝廷的档案馆 —— 让每次对话的产出持久化存储，让丞相在新对话中能查阅历史档案。

你可以用任何支持结构化数据的平台搭建第二大脑。本文以 Notion 为主要示例，并在文末说明如何适配其他平台。

---

## 重要概念：六部 vs 领域

- **六部**是 AI 朝廷的分析框架（吏/户/礼/兵/刑/工），按行为类型分工，固定不变
- **领域**是你生活的实际分区（职业发展/家庭/健康/财务/创作...），由你自定义
- 两者独立运作。一个决策可能由户部分析财务维度，但对应的领域是"产品与创业"
- Notion 中的 Area 字段关联的是 **🌊 领域**，不是六部

---

## 架构概览

```
Life OS（AI 朝廷）
  │
  │  决策、行动项、报告
  ▼
第二大脑（数据层）
  ├── 🌊 领域          ← 你的生活分区，支持层级（上级领域）
  ├── ✅ 任务          ← 行动项，关联到领域
  ├── 🤔 决策          ← 奏折存档，含评分和流程记录
  ├── 📓 日志          ← 复盘简报、御史台/谏官报告
  ├── 🎯 目标          ← 目标和进展，关联到领域
  ├── 🎯 项目          ← 项目库，关联到领域
  └── （可选：📥 收件箱、👥 人脉、💰 财务、🏥 健康、📚 资源库）
```

核心思路：**领域是骨架**。任务属于某个领域，目标属于某个领域，决策涉及某个领域。所有数据通过领域关联起来。

---

## Notion 搭建指南

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

### 数据库搭建

在 Notion 中创建一个顶层页面 **🧠 第二大脑**，在下面逐个建立数据库。

#### 1. 🌊 领域（先建这个）

这是整个系统的骨架，其他数据库都会 Relation 到它。

| 属性 | 类型 | 说明 |
|------|------|------|
| Name | Title | 领域名称 |
| Description | Text | 描述 |
| Status | Select | Active / Inactive |
| Review Cycle | Select | Weekly / Monthly / Quarterly |
| 上级领域 | Relation → 自身 | 支持层级结构 |

领域由你自定义，按你自己的生活维度划分。比如：

| 领域 | 复盘周期 | 说明 |
|------|---------|------|
| 💼 职业发展 | Monthly | 上级领域，下辖具体工作项目 |
| 🚀 产品与创业 | Weekly | 副业/创业项目 |
| 💰 财务管理 | Monthly | 收入、投资、预算 |
| 👨‍👩‍👧‍👦 家庭 | Weekly | 家庭事务 |
| 🤝 社交关系 | Monthly | 人脉、社交 |
| 🏥 健康 | Monthly | 身体、心理健康 |
| 🏠 生活运营 | Monthly | 居住、日常流程 |
| 📖 学习 | Weekly | 技能提升、阅读 |
| ✍️ 创作 | Weekly | 内容创作、写作 |
| 🧘 精神 | Quarterly | 价值观、人生方向 |

你可以随时增减领域，不需要跟六部一一对应。

#### 2. ✅ 任务

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

#### 3. 🤔 决策

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

页面正文存奏折全文。

建议新建一个视图 **📜 朝政记录**：过滤 `流程类型 = 三省六部`，按 Date 倒序排列。

#### 4. 📓 日志

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 日志标题 |
| Date | Date | 日期 |
| Mood | Select | Great / Good / Neutral / Low / Bad |
| Energy | Select | High / Medium / Low |
| Highlight | Text | 亮点摘要 |
| Tags | Multi-select | 御史台 / 谏官 / 早朝简报 / 手动记录 |

页面正文存报告全文。

#### 5. 🎯 目标

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 目标名称 |
| Status | Select | Not Started / In Progress / Achieved / Missed / Revised |
| Timeframe | Select | 2026-Q1 / Q2 / Q3 / Q4 / Annual / Long-term |
| Progress | Number | 0-100 |
| Key Results | Text | 关键结果 |
| Area | Relation → 领域 | 关联领域 |
| Projects | Relation → 项目 | 关联项目 |

#### 6. 🎯 项目

| 属性 | 类型 | 说明 |
|------|------|------|
| Name | Title | 项目名称 |
| Status | Select | Planning / Active / On Hold / Done / Dropped |
| Priority | Select | P0 / P1 / P2 / P3 |
| Owner | Select | Me / Shared |
| Deadline | Date | 截止日期 |
| Area | Relation → 领域 | 关联领域 |

---

## 数据流转

三省六部流程结束后，产出自动存入对应数据库：

```
三省六部流程
  │
  ├── 奏折全文 ──────→ 🤔 决策（流程类型=三省六部，Area=相关领域）
  ├── 行动项 ────────→ ✅ 任务（逐条创建，Area=相关领域）
  ├── 御史台报告 ────→ 📓 日志（Tags=御史台）
  ├── 谏官报告 ──────→ 📓 日志（Tags=谏官）
  └── 新目标 ────────→ 🎯 目标（Area=相关领域）

早朝官复盘
  └── 早朝简报 ──────→ 📓 日志（Tags=早朝简报）
```

存档时 Area 的关联方式：根据决策话题搜索领域库，匹配最相关的领域。比如"辞职创业"匹配"💼 职业发展"或"🚀 产品与创业"。

## 跨会话连续性

AI 对话是无状态的，但第二大脑让它有了记忆：

```
新对话 → 丞相听意图 → 搜索历史决策 → 带上下文处理 → 产出存回
```

你说"上次分析搬家的事怎么样了"，丞相去决策库搜"搬家"，把上次奏折结论拉回来继续。

---

## 适配其他平台

第二大脑的核心是 **领域数据库 + 任务/决策/日志/目标的关联**，不绑定 Notion。任何支持以下能力的平台都可以用：

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

1. **领域是骨架** — 不管用什么平台，先建好领域分类作为关联锚点
2. **决策库最重要** — 这是跨会话连续性的核心，必须能搜索+读取全文
3. **任务库次之** — 早朝官复盘需要知道什么任务完成了、什么逾期了
4. **日志可以最简** — 最低限度是一个带日期和标签的富文本列表

### 不用任何平台

Life OS 不连接数据层时，所有决策和分析功能照常工作，只是：
- 没有跨会话记忆（每次对话从零开始）
- 没有自动存档（产出在对话结束后消失）
- 流程结束会标注"⚠️ 数据层未连接，本次产出未存档"
