# Life OS — 三省六部制个人内阁系统

> 用运行了 1400 年的治国架构，管理你的人生。

Life OS 把 AI 变成你的私人朝廷 —— 丞相（大管家）+ 三省（规划/审议/执行）+ 六部（人/钱/学习/行动/规则/基建）+ 御史台（查官员）+ 谏官（查你自己）+ 翰林院（战略顾问），全方位管理生活、工作、学习、财务、健康和人际关系。

**这不是角色扮演。这是分权制衡。** 门下省有权否决不合格的方案。御史台监察所有"官员"的工作质量。谏官直言不讳地指出你自己的行为盲区。

---

## 快速开始

### Claude Code（推荐，Pro 模式）

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

14 个 subagent 自动就绪，独立进程、独立 context window，六部可并行执行。门下省审查时看不到中书省的思考过程 —— 真正的分权制衡。

### Claude.ai（Lite 模式）

**方法 1：Project Knowledge（推荐）**
1. 创建 Project → Settings → Add to project knowledge
2. 上传 `SKILL.md` 文件
3. 该 Project 下每个新对话都自带三省六部能力

**方法 2：单次对话** — 直接把 `SKILL.md` 拖入对话窗口，仅当前对话有效。

### 其他平台

Life OS 遵循 [Agent Skills 开放标准](https://agentskills.io/)，兼容 30+ 个 AI agent 产品。

| 平台 | 安装方式 | 模式 |
|------|---------|------|
| **Claude Code** | `/install-skill` GitHub URL | Pro（14 subagent 并行） |
| **Claude.ai** | 上传 SKILL.md 到 Project Knowledge | Lite（单 context） |
| **Cursor** | `npx skills add jasonhnd/life_OS` | Lite |
| **Gemini CLI** | `npx skills add jasonhnd/life_OS` | Lite |
| **OpenAI Codex CLI** | `npx skills add jasonhnd/life_OS` | Lite |
| **VS Code Copilot** | `npx skills add jasonhnd/life_OS` | Lite |
| **Roo Code** | `npx skills add jasonhnd/life_OS` | Lite |
| **ChatGPT** | 把 SKILL.md 内容粘贴到 GPT Instructions | Lite |
| **Gemini (Web)** | 把 SKILL.md 内容粘贴到 Gem Instructions | Lite |
| **其他兼容 Agent** | 参考 [agentskills.io](https://agentskills.io/) | Lite |

> **Pro vs Lite**：Pro 模式是 Claude Code 专属，利用 Agent tool 启动独立子进程实现真正的信息隔离和并行执行。其他平台使用 Lite 模式，在单个 context 内模拟所有角色，功能完整但没有进程级隔离。

---

## 为什么用唐朝的架构

大多数 AI 工具的模式是"一个人想完就交"。你问一个问题，AI 给一个答案。没有审查，没有制衡，没有人说"等一下，这个方案有问题"。

唐朝三省六部制解决的就是这个问题：**想（中书省）→ 查（门下省）→ 做（尚书省+六部）**。没有任何一个环节能跳过审查直接执行。

六部按**人类行为的基本类型**分工 —— 管人、管钱、管标准、管行动、管规则、管基建。不管做的是软件开发、投资、内容创作还是日常生活，都可以自然分解到六部中。

---

## 系统架构

```
👑 你（皇上）
  │
  ├── 🏛️ 丞相（大管家）
  │     ├── 简单事 → 直接处理
  │     └── 大事 → 启动三省六部
  │
  ├── 📜 中书省 → 🔍 门下省 → 📨 尚书省 → 六部
  │     规划       审查(可否决)    派发      执行
  │   → 🔍 门下省终审 → 📋 奏折
  │   → 🔱 御史台(查官员) → 💬 谏官(查你)
  │
  │   六部：👥吏(人) 💰户(钱) 📖礼(学习) ⚔️兵(行动) ⚖️刑(规则) 🏗️工(基建)
  │
  ├── 🏛️ 政事堂 — 跨部门辩论（3轮）
  ├── 🌅 早朝官 — 定期复盘
  └── 🎋 翰林院 — 私人战略对话
```

### 15 个角色

| 角色 | 职能 | 触发方式 |
|------|------|---------|
| 🏛️ 丞相 | 百官之首，日常入口 | 所有消息 |
| 📜 中书省 | 规划拆解 | 丞相上报 |
| 🔍 门下省 | 审议+封驳+感性审查 | 规划后+执行后 |
| 📨 尚书省 | 派发指令 | 准奏后 |
| 👥 吏部 | 人：关系、团队、社交 | 按需 |
| 💰 户部 | 钱：收入、投资、预算 | 按需 |
| 📖 礼部 | 学习与表达：教育、品牌、创作 | 按需 |
| ⚔️ 兵部 | 行动：项目、执行、调研 | 按需 |
| ⚖️ 刑部 | 规则：风控、合规、复盘 | 按需 |
| 🏗️ 工部 | 基建与健康：身体、环境、系统 | 按需 |
| 🔱 御史台 | 监察官员工作质量 | 每次自动 |
| 💬 谏官 | 监督你的行为模式 | 每次自动 |
| 🏛️ 政事堂 | 跨部门辩论 | 结论矛盾时 |
| 🌅 早朝官 | 定期复盘 | 说"复盘" |
| 🎋 翰林院 | 战略对话 | 问你是否需要 |

### 六部详解

六部不是按行业分的，而是按**行为类型**分的。任何事情都可以分解到这六种行为中：

| 部门 | 唐朝原职 | Life OS 职责 | 四司 |
|------|---------|-------------|------|
| 👥 吏部 | 官员任免考核 | 人际关系、团队、合作伙伴 | 选贤·考功·封赏·调配 |
| 💰 户部 | 财政税收户籍 | 收入、投资、预算、资产 | 收入·度支·资产·储备 |
| 📖 礼部 | 科举外交祭祀 | 学习、品牌、创作、沟通 | 科举·典仪·文翰·外交 |
| ⚔️ 兵部 | 军事武官兵籍 | 项目执行、调研、工具、精力 | 军令·装备·情报·后勤 |
| ⚖️ 刑部 | 刑律断狱审计 | 风控、合规、复盘、自律 | 律法·审计·纠察·防御 |
| 🏗️ 工部 | 工程水利交通 | 健康、居住、数字基建、routine | 体健·营建·数造·水利 |

---

## 独特机制

### 门下省封驳 + 感性审查

门下省不只做理性分析。对**所有决策**（包括工作决策），它都会额外审查：
- **情绪因素**：当前情绪是否影响了判断
- **关系影响**：家人/重要关系人怎么看
- **价值观一致性**：符合长期价值观吗
- **后悔测试**：五年后回看会不会后悔

### 御史台 — 查官员

每次流程结束后自动运行。不看事情本身，只看"这些官员干活的质量"：门下省是不是走形式、六部报告有没有实质内容、评分是不是都给高分。

### 谏官 — 查你自己

每次流程结束后自动运行。直言不讳地指出你的行为盲区：决策风格是不是突然变了、有没有在回避某些问题、有没有说到没做到的承诺。

### 政事堂 — 朝堂议政

当各部结论矛盾时（户部说"钱不够"，兵部说"可以分阶段"），启动 3 轮辩论，让各部直接对话。

### 翰林院 — 战略对话

有些问题不需要走流程，比如"我最近很迷茫"。翰林院是你的私人战略顾问，不出奏折、不评分，就是陪你深度思考。

---

## 使用示例

**日常对话** — 丞相直接处理
```
你：帮我翻译一段日语
丞相：[直接翻译]
```

**复杂决策** — 全流程
```
你：我在考虑要不要辞职创业

丞相 → 上报朝廷
中书省 → 拆解（财务/能力/人脉/执行/风险/生活）
门下省 → 审查（"遗漏了家庭因素，封驳"）→ 中书省修正 → 准奏
尚书省 → 派发各部 → 六部各自出报告
门下省终审 → 奏折（综合评分 6.8/10）
御史台 → "兵部报告缺少具体执行时间线"
谏官 → "你最近连续三周都在看创业内容，注意确认偏差"
```

**定期复盘**
```
你：早朝
早朝官 → 汇总六部信息，出简报
```

**深度思考**
```
你：我最近在想人生的方向
丞相：要不要启动翰林院深度对话？
```

---

## 10 个标准场景

| # | 场景 | 启用部门 |
|---|------|---------|
| 1 | 职业转型 | 全六部 |
| 2 | 投资决策 | 户部+兵部+刑部+吏部 |
| 3 | 搬家/移居 | 全六部 |
| 4 | 年度目标 | 全六部 |
| 5 | 创业决策 | 全六部 |
| 6 | 大额消费 | 户部+兵部+刑部 |
| 7 | 人际关系 | 吏部+工部+刑部+礼部 |
| 8 | 定期复盘 | 早朝官 |
| 9 | 健康管理 | 工部+兵部+户部+刑部 |
| 10 | 学习规划 | 礼部+兵部+户部+吏部 |

---

## Notion 集成 — 第二大脑

Life OS 把 Notion 当作朝廷的档案馆。AI 负责决策和执行，Notion 负责持久化存储。每次对话可以是新开的，但通过 Notion 保持连续性 —— 丞相开场就会去 Notion 翻历史档案，流程结束自动存档。

### 第一步：连接 Notion

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

### 第二步：建立第二大脑

在 Notion 中创建一个顶层页面 **🧠 第二大脑**，然后在下面建立以下数据库：

```
🧠 第二大脑
├── 🏛️ 六部            ← Database，6个固定条目（核心锚点）
├── 🎯 项目            ← Database
├── ✅ 任务            ← Database
├── 🎯 目标            ← Database
├── 🤔 决策            ← Database
├── 📓 日志            ← Database
└── （可选：📥 收件箱、👥 人脉、💰 财务、🏥 健康、📚 资源库、📌 书签）
```

#### 🏛️ 六部（必建，其他数据库的关联锚点）

创建一个 Database，添加 6 个条目：

| Name | Description | Status |
|------|-------------|--------|
| 👥 吏部 · 人 | 人际关系、团队、社交 | Active |
| 💰 户部 · 钱 | 财务、投资、预算 | Active |
| 📖 礼部 · 学习与表达 | 教育、品牌、创作 | Active |
| ⚔️ 兵部 · 行动 | 项目、执行、调研 | Active |
| ⚖️ 刑部 · 规则 | 风控、合规、自律 | Active |
| 🏗️ 工部 · 基建与健康 | 健康、环境、数字基建 | Active |

这是整个系统的骨架 —— 任务、目标、决策都会关联到六部。

#### ✅ 任务

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 任务名称 |
| Status | Select | To Do / In Progress / Waiting / Done / Cancelled |
| Priority | Select | P0 / P1 / P2 / P3 |
| Due Date | Date | 截止日期 |
| Energy | Select | High / Medium / Low |
| Context | Select | Computer / Phone / Home / Office / Call / Errand |
| Area | Relation → 六部 | 关联到哪个部门 |
| Project | Relation → 项目 | 关联到哪个项目 |

#### 🤔 决策

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 旨意 |
| 流程类型 | Select | 简单决策 / 三省六部 |
| 启用部门 | Multi-select | 吏部 / 户部 / 礼部 / 兵部 / 刑部 / 工部 |
| 综合评分 | Number | 1-10 |
| 封驳次数 | Number | 门下省封驳了几次 |
| Status | Select | Considering / Decided / Reversed |
| Category | Select | Career / Finance / Product / Tech / Family / Life / Health |
| Outcome | Select | Good / Neutral / Bad / TBD |
| Date | Date | 决策日期 |
| Area | Relation → 六部 | 主要相关部门 |
| Actions | Relation → 任务 | 产出的行动项 |

页面正文存奏折全文。建一个 **📜 朝政记录** 视图：过滤 `流程类型 = 三省六部`，按日期倒序。

#### 📓 日志

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 日志标题 |
| Date | Date | 日期 |
| Mood | Select | Great / Good / Neutral / Low / Bad |
| Energy | Select | High / Medium / Low |
| Highlight | Text | 亮点摘要 |
| Tags | Multi-select | 自定义标签（御史台 / 谏官 / 早朝简报等） |

页面正文存报告全文。

#### 🎯 目标

| 属性 | 类型 | 说明 |
|------|------|------|
| Title | Title | 目标名称 |
| Status | Select | Not Started / In Progress / Achieved / Missed / Revised |
| Timeframe | Select | 2026-Q1 / Q2 / Q3 / Q4 / Annual / Long-term |
| Progress | Number | 0-100 |
| Key Results | Text | 关键结果 |
| Area | Relation → 六部 | 关联部门 |
| Projects | Relation → 项目 | 关联项目 |

#### 🎯 项目

| 属性 | 类型 | 说明 |
|------|------|------|
| Name | Title | 项目名称 |
| Status | Select | Planning / Active / On Hold / Done / Dropped |
| Priority | Select | P0 / P1 / P2 / P3 |
| Owner | Select | Me / Shared |
| Deadline | Date | 截止日期 |
| Area | Relation → 六部 | 关联部门 |

### 数据流转

三省六部流程结束后，产出自动存入对应数据库：

| 产出 | 存入 | 说明 |
|------|------|------|
| 奏折 | 🤔 决策 | 流程类型=三省六部，奏折全文存页面正文 |
| 行动项 | ✅ 任务 | 逐条创建，关联六部 Area 和决策 |
| 御史台报告 | 📓 日志 | Tags=御史台 |
| 谏官报告 | 📓 日志 | Tags=谏官 |
| 早朝简报 | 📓 日志 | Tags=早朝简报 |
| 新目标 | 🎯 目标 | 关联六部 Area |

### 跨会话连续性

```
新对话 → 丞相听意图 → 搜索 Notion 历史决策 → 带上下文处理 → 产出存回 Notion
```

不依赖对话长度，不怕上下文丢失。你说"上次分析搬家的事怎么样了"，丞相去决策库搜"搬家"，把上次奏折结论拉回来。

### 不连接 Notion 也能用

Notion 是可选的数据层。不连接时，Life OS 所有决策和分析功能照常工作，只是不会自动存档。流程结束会标注"⚠️ Notion 未连接，本次产出未存档"。

---

## Lite vs Pro

| | Lite | Pro（Claude Code） |
|--|------|-------------------|
| 角色隔离 | 同一 context | 独立进程 |
| 门下省审查 | 能看到前面推理 | 真正独立 |
| 六部执行 | 串行 | 并行 |
| 模型 | 当前模型 | 所有角色 opus |

## Token 消耗

| 模式 | 每次流程 | 费用估算 |
|------|---------|---------|
| Lite 标准流程 | ~15k tokens | ~$0.30-0.50 |
| Pro 标准流程 | ~38k tokens | ~$0.80-1.20 |
| Pro + 封驳 + 政事堂 | ~55k tokens | ~$1.50-2.00 |

> Claude Max/Pro 订阅用户不按 token 计费，以上仅供 API 用户参考。

**省 Token 策略**：简单事不上朝 / 快速模式跳过丞相 / 按需启用部门 / 日常复盘单独跑早朝官

---

## 文件结构

```
life-os/
├── SKILL.md                    # 主入口（Lite+Pro 双模式）
├── references/
│   ├── departments.md          # 六部×四司详细职能
│   └── scene-configs.md        # 10个标准场景配置
├── pro/
│   ├── CLAUDE.md               # Claude Code 编排协议
│   └── agents/                 # 14个 subagent
│       ├── chengxiang.md       # 🏛️ 丞相
│       ├── zhongshu.md         # 📜 中书省
│       ├── menxia.md           # 🔍 门下省
│       ├── shangshu.md         # 📨 尚书省
│       ├── libu_hr.md          # 👥 吏部
│       ├── hubu.md             # 💰 户部
│       ├── libu.md             # 📖 礼部
│       ├── bingbu.md           # ⚔️ 兵部
│       ├── xingbu.md           # ⚖️ 刑部
│       ├── gongbu.md           # 🏗️ 工部
│       ├── yushitai.md         # 🔱 御史台
│       ├── jianguan.md         # 💬 谏官
│       ├── zaochao.md          # 🌅 早朝官
│       └── hanlin.md           # 🎋 翰林院
└── README.md
```

## 设计理念

唐朝三省六部制的核心不是"很多人"，而是**分权制衡**：中书省只管想、门下省只管查、六部只管做、御史台查官员、谏官查皇帝。没有任何一个角色能跳过审查直接行动。

唐太宗 1300 年前就想明白了 —— 不受约束的权力必然产生错误。Life OS 把这个智慧应用到你的个人决策中。

## 灵感来源

本项目的三省六部 AI 多 Agent 编排概念受 [Edict](https://github.com/cft0808/edict) 项目启发。Life OS 在此基础上将六部从软件开发场景扩展到个人生活全领域，新增了御史台、谏官、政事堂、翰林院等唐朝治国机构的完整映射。

## License

Apache-2.0
