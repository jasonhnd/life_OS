# Second Brain · 目录结构总览

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Second-brain 是 Life OS 的数据层。所有决策、任务、会议纪要、知识、SOUL 画像、战略地图都活在这里。引擎（SKILL.md + agents）只是操作它的手；真正"记住"的是这个目录。

权威源：`references/data-layer.md`、`references/data-model.md`、`docs/second-brain.md`（英文原版）。

---

## 顶层目录一览

```
second-brain/
│
├── inbox/                    # 📥 未处理（捕获、材料、笔记、原始研究）
│
├── SOUL.md                   # 🧬 身份 — 价值观、原则、行为倾向
├── user-patterns.md          # 📊 跨会话观察到的行为模式
│
├── _meta/                    # 🔧 系统元数据
│   ├── STATUS.md             # 全局状态快照（编译）
│   ├── STRATEGIC-MAP.md      # 🗺️ 战略地图（从项目 strategic 字段编译）
│   ├── strategic-lines.md    # 战略线定义（用户手写）
│   ├── MAP.md                # 知识地图
│   ├── outbox/               # 📤 等合并的会话产出
│   ├── snapshots/soul/       # SOUL 快照（每次会话结束写一份）
│   ├── decisions/            # 跨领域大决策
│   ├── journal/              # 晨报、AUDITOR/ADVISOR/DREAM 报告
│   ├── extraction-rules.md
│   ├── extraction-log.md
│   ├── lint-rules.md
│   ├── lint-state.md
│   ├── lint-reports/
│   └── roles/                # 常驻角色定义
│
├── projects/{name}/          # 🎯 有终点的事
│   ├── index.md              # 目标、状态、关联领域
│   ├── tasks/                # 下一步
│   ├── decisions/            # 项目专属纪要
│   ├── research/             # 项目专属研究
│   └── journal/              # 项目专属日志
│
├── areas/{name}/             # 🌊 持续型领域
│   ├── index.md
│   ├── goals.md
│   ├── tasks/
│   └── notes/
│
├── wiki/                     # 📚 跨域知识网（wikilinks）
│   ├── INDEX.md
│   └── {domain}/{topic}.md
│
├── archive/                  # 🗄️ 项目归档
│
└── templates/                # 📋 模板
```

PARA 模型的变体。Projects 有终点，Areas 没终点，Archive 存放完成的 Projects，Wiki 是从 Decisions/DREAM 长出来的知识沉淀。

---

## 10 个标准 Area

```
career/     product/    finance/    health/    family/
social/     learning/   ops/        creation/  spirit/
```

不是硬规则，可以增删。但这 10 个够用了 — 人生的事基本能归到其中一个。

---

## 核心概念

### projects/ vs areas/

**Projects 有终点**。"发布 v2"、"搬家到东京"、"拿到创业签证"。完成之后整个文件夹移到 `archive/`，在 wiki 里留下浓缩的知识。

**Areas 没终点**。"金融健康"、"家庭关系"、"创作"。一直在。只有 `active` / `inactive` 两种状态。

项目和领域可以互相引用。搬家项目属于 life area，但也会拉 finance area 进来算钱。

### _meta/ — 关于大脑的大脑

系统元数据。不是你的记忆，是系统怎么管理你记忆的规则。

- `STATUS.md` — 所有项目和领域的全局快照。ARCHIVER 从各项目 index.md 编译出来。**不能手写**。
- `STRATEGIC-MAP.md` — 从项目的 strategic 字段编译出来的战略关系图。也**不能手写**。
- `decisions/` — 跨领域大决策（不属于单一项目的）。
- `journal/` — 晨报、巡查报告、DREAM 报告。
- `snapshots/soul/` — 每次会话结束写一份 SOUL 快照，下次会话 RETROSPECTIVE 用它算 delta。
- `outbox/` — 会话结束时 ARCHIVER 先写到这里，下次上朝合并。
- `lint-*` — AUDITOR 巡查用的规则和状态。
- `roles/` — 可选的常驻角色（historian、reviewer on-duty）。

### SOUL.md — 身份画像

不是标签。是系统对"你是什么样的人"的当前理解。每个 dimension 有 evidence_count / challenges / confidence / last_validated。决策时 REVIEWER 读它来判断是否和你一致。ADVISOR 每次会话更新 evidence 和 challenges。

权威源：`references/soul-spec.md`。

### user-patterns.md — 行为模式

例如："用户在金融决策上倾向过度自信"、"用户讨厌长篇战略文档，偏好一句话总结"。ADVISOR 跨会话累计观察后写进来。下次会话 RETROSPECTIVE 读它，让整个会话带着这些模式意识运行。

### wiki/ — 可复用的知识

DREAM 阶段从会话材料里抽出可复用的结论，写进 wiki。项目死了，项目里得到的知识还活着。跨域 wikilinks 让知识形成网。

wiki 条目**自动写入**（v1.6.2）— 通过 6 条严格准则 + 隐私过滤。用户不满意就删文件，或说"撤回最近的 wiki"回滚。

### inbox/ — 零摩擦捕获

未处理的东西。手机上说一嘴 → 落到 inbox。桌面会话开始时 RETROSPECTIVE 读它并提醒。处理后 → 分流到 projects/areas/wiki/decisions。

---

## Notion 四组件（记忆层）

Second-brain 在 GitHub / Google Drive 上时，Notion 可以作为轻量记忆层给手机用：

| 组件 | 类型 | 作用 |
|------|------|------|
| 📬 Inbox | 数据库 | 手机 ↔ 桌面的消息队列。Content / Source / Status / Time。 |
| 🧠 Current Status | 页面 | 镜像 `_meta/STATUS.md`。会话结束由 orchestrator 覆写。 |
| 📝 Working Memory | 话题页 | 每个活跃话题一页（5-10 个）。不活跃了归档到 GitHub + 从 Notion 删掉。 |
| 📋 Todo Board | 数据库 | 从 `projects/*/tasks/` 和 `areas/*/tasks/` 同步。手机可勾可看。 |

这叫 **传输模式**。Notion 也可以做完整后端（六种数据类型都存 Notion），但不推荐 — 数据格式锁在 Notion 里，换不了工具。

详见 `docs/user-guide/storage-and-sync/notion-as-transport.md`。

---

## 多仓库工作流

很多用户会有：

- **项目代码仓**（比如 `life_OS`、`my-app`）— 每个一个 repo。
- **关于项目的思考**（决策、笔记、任务）— 一律落在 second-brain repo。

同一个 CC 会话可以同时关联两者。工作流：

1. 正常在项目仓写代码。
2. 想沉淀思考 → `/save` 命令 → 写文件进 second-brain → cd 过去 → git commit/push → 返回项目仓继续。

见 `docs/user-guide/storage-and-sync/using-the-slash-save-command.md`。

---

## 没有 data layer 会怎样

如果你完全没设置 second-brain（没选任何后端），Life OS 依然能用：

- 多个 agent 正常工作。
- 上朝、决策、六部、REVIEWER 封驳都能跑。
- 可以在会话里得到完整的 Summary Report。

**但**：

- 无持久化 — 会话结束，所有东西丢。
- 无跨会话记忆 — 下次上朝系统不知道你是谁、在做什么。
- 无 SOUL 积累 — 系统永远是"第一次认识你"。
- 无 DREAM — 没数据可做梦。
- 无 wiki — 知识不沉淀。

适合的场景：第一次试用、朋友借你电脑跑一个决策、演示给别人看。

不适合长期使用。

---

## 单一真理源规则（Single Source of Truth）

| 数据 | 权威源 | 编译视图 |
|------|--------|---------|
| 项目版本 / 状态 | `projects/{project}/index.md` | `_meta/STATUS.md` |
| 领域目标 / 状态 | `areas/{area}/index.md` | `_meta/STATUS.md` |
| 任务完成率 | `projects/{project}/tasks/*.md` | Metrics dashboard |
| 行为模式 | `user-patterns.md` | ADVISOR 报告 |
| 战略关系 | `projects/{project}/index.md` strategic 字段 + `_meta/strategic-lines.md` | `_meta/STRATEGIC-MAP.md` |

**写入顺序强制**：先改权威源，再让系统编译视图。永远不要直接写 STATUS.md。AUDITOR 巡查时如果发现 STATUS.md 和 index.md 矛盾，会标🔴并以 index.md 为准。

---

## 一个真实的文件例子

```
second-brain/projects/career-transition/decisions/2026-04-08-japan-visa.md
```

文件内容：

```yaml
---
type: decision
title: "日本创业签证可行性"
status: decided
score: 6.8
date: 2026-04-08
project: career-transition
last_modified: "2026-04-08T15:30:00+09:00"
---

[纪要全文 — REVIEWER 总结 + 各部打分 + 封驳记录]
```

这就是 second-brain 的"原子"。所有 agents 读它、写它、归档它。纯 markdown + YAML。Obsidian 能打开，Gemini 能读懂，换模型不丢数据。

---

## 为什么选 markdown

- **模型无关**。今天用 Claude，明天换 Gemini，下个月自己本地跑 Llama — 文件原样能用。
- **工具无关**。没有 Life OS 系统，Obsidian 打开就能看能写。
- **Git 友好**。diff 清楚，合并有意义，history 可追溯。
- **可读**。10 年后打开也能读。不像数据库导出的 json。

"模型会变，文件不变"是核心设计原则。SKILL.md 和 `pro/CLAUDE.md` 是仅有的绑定到具体模型的东西。换模型只改这两个文件，其他都不动。
