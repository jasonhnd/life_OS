# Life OS 文档

> **受众边界**：`docs/` 默认是**公开**的，全部 tracked 到 GitHub，作为用户和开发者的文档入口。作者的内部工作文档（脑暴、调研报告、已 deprecated 的架构文档、内部规则）在 `devdocs/`，由 `.gitignore` 屏蔽、不 push。READMEs（`/README.md` 和 `/i18n/{zh,ja}/README.md`）是最外层公开入口。
>
> 即：`docs/**` = 公开，默认 tracked；`devdocs/**` = 私有，默认 gitignored。新写 doc 要问清楚是「给用户/开发者看」还是「给未来的自己参考」，前者进 `docs/`，后者进 `devdocs/`。

---

## 文档怎么组织

`docs/` 下分六个顶层目录，每个目录的职责不重叠：

| 目录 | 放什么 | 何时读 |
|------|-------|-------|
| `getting-started/` | 新用户第一次接触系统需要看的 4 篇 | 刚装完，或者推荐给别人 |
| `user-guide/` | 系统各个功能模块的用法（SOUL、DREAM、Wiki、主题、六部、战略地图、存储、会话生命周期、智库 Hall of Wisdom） | 想深入用某个功能 |
| `guides/` | 场景化操作手册（年度规划、职业决策、建 wiki、映射战略等） | 遇到具体场景想抄作业 |
| `architecture/` | 引擎内部设计（multiple agents、编排协议、状态机、信息隔离、HARD RULE 目录、多平台编排） | 想改代码、想写 subagent、想调试流程 |
| `reference/` | 规格和字典类文档（9 主题 × multiple agents 的完整映射、触发词、适配器、FAQ、版本历史、token 估算） | 查具体名字、参数、数据结构 |
| `evals/` | 评估脚本与场景 | 长期演化系统时的参考 |

内部文档（不在 `docs/` 里，在仓库根部的 `devdocs/` 下，gitignored）：

| 目录 | 放什么 |
|------|-------|
| `devdocs/brainstorm/` | 头脑风暴记录，时间戳命名 |
| `devdocs/research/` | 调研报告，时间戳命名 |
| `devdocs/architecture/` | 已 deprecated 的架构文档、内部规则 |

`docs/installation.md` 是公开入口，不要和 `getting-started/` 重复。安装流程只写在 installation.md 里；`getting-started/` 讲的是装完之后该做什么。

---

## 根据你是谁，挑一条路径

### 新用户 — 我刚装好，第一次用

按顺序读 4 篇，一次到位：

1. `getting-started/what-is-life-os.md` — 系统是什么，解决什么问题，不做什么
2. `getting-started/choose-your-platform.md` — 确认你在对的平台上（Claude Code / Gemini CLI / Codex CLI）
3. `getting-started/quickstart.md` — 5 分钟跑通第一次会话
4. `getting-started/first-session.md` — 展开讲「上朝」之后系统做的所有事

读完这 4 篇，你就能独立用。再想深入，去 `user-guide/`。

### 老用户 — 我想用某个具体功能

先看 [`user-guide/index.md`](user-guide/index.md) 拿到全部功能模块的统一入口，或直接去 `user-guide/` 下的对应子目录：

- 想管理 SOUL → `user-guide/soul/`
- 想理解晨报里的 DREAM 块 → `user-guide/dream/`
- 想切主题或加新主题 → `user-guide/themes/`
- 想调通 Notion 双向同步 → `user-guide/storage-and-sync/`
- 想用 Hall of Wisdom 和苏格拉底聊 → `user-guide/hall-of-wisdom/`
- 想理解 v1.7 Cortex 认知层（跨会话记忆 / 概念图 / 方法库 / GWT 仲裁 / Narrator 引用 / AUDITOR 自反馈）→ `user-guide/cortex/`

场景化的操作手册在 `guides/` — 比如「年度规划会怎么开」「职业决策怎么走完整流程」，这些是 user-guide 的实战补充。

### 开发者 — 我想改系统 / 排查流程 bug

架构细节全在 `architecture/`：

- `architecture/16-agents.md` — 每个 agent 的功能边界
- `architecture/orchestration-protocol.md` — 11 步编排协议的完整逻辑
- `architecture/workflow-state-machine.md` — 状态机定义，违反哪一步会被 AUDITOR 标记
- `architecture/hard-rules-catalog.md` — 33 条 HARD RULE 的完整清单
- `architecture/information-isolation.md` — 哪些信息传哪些角色，为什么要隔开
- `architecture/multi-platform-orchestration.md` — Claude / Gemini / Codex 三个 orchestrator 的差别

改完代码必做：同步 3 份 README + 3 份 CHANGELOG + SKILL.md 的 `version:` 字段。这个在 `.claude/CLAUDE.md` 里有详细清单。

### 我只是想查一个具体名字

去 `reference/`：

- `reference/all-9-themes/` — 9 个主题每个角色叫什么、什么 tone
- `reference/all-16-agents/` — 16 个 engine ID 到角色定义的索引
- `reference/trigger-words.md` — 所有触发词一览
- `reference/adapters/` — GitHub / Google Drive / Notion 的适配器规格
- `reference/specifications/` — SOUL / DREAM / Wiki / Strategic Map 的数据结构

---

## 权威文件在哪

这些是系统的「源」，文档是「说明」。改文档改不了行为，改源才算数：

| 文件 | 地位 |
|------|------|
| `SKILL.md` | 路由文件，Claude / Gemini / Codex 都会先读这个 |
| `pro/CLAUDE.md` | Claude 平台的 11 步编排协议 |
| `pro/GEMINI.md` | Gemini 平台同等地位的编排文件 |
| `pro/AGENTS.md` | Codex 平台的编排文件 |
| `pro/agents/*.md` | 多个 subagent 的定义 |
| `themes/*.md` | 9 个主题的显示名映射 |
| `references/*.md` | 数据模型、适配器、SOUL / DREAM / Wiki spec |

`docs/` 是解释这些源的副产物。如果发现 `docs/` 和源有矛盾，以源为准。

---

## 快速链接

最常看的几篇：

- [什么是 Life OS](getting-started/what-is-life-os.md)
- [5 分钟 quickstart](getting-started/quickstart.md)
- [第一次上朝全流程](getting-started/first-session.md)
- [平台选择](getting-started/choose-your-platform.md)
- [公开安装指南](installation.md)
- [multiple agents](architecture/16-agents.md)
- [编排协议](architecture/orchestration-protocol.md)
- [HARD RULE 目录](architecture/hard-rules-catalog.md)
- [FAQ](reference/faq.md)

---

## 维护守则

1. **这里的每一篇都是给未来的自己看的**。写的时候假设读者是 6 个月后忘了细节的你。
2. **不复制源文件内容**。doc 只讲「为什么」和「怎么用」，具体定义一律指向源文件。
3. **改了引擎必须回来改 doc**。三语 README+CHANGELOG 同步是 HARD RULE；docs/ 的同步是软规则，但发现过时就立刻修。
4. **不写营销话术**。这里不是 README。说「Finance 5/10」就行，不用包装成「金融智能评分系统」。

---

## 各目录的具体约定

### getting-started/
4 篇固定：`what-is-life-os.md` / `choose-your-platform.md` / `quickstart.md` / `first-session.md`。不要新增。想加场景去 guides/，想加细节去 user-guide/。

### user-guide/
每个功能一个子目录。子目录里一般 1-3 篇：`overview.md`（是什么）、`how-to.md`（怎么用）、`troubleshooting.md`（卡住了怎么办，如果这个功能有常见坑）。不是所有功能都需要三篇 —— 功能简单的只写 overview。

### guides/
操作手册，解决特定场景。每篇独立、可单独读。命名直接用场景名（`annual-planning-session.md`、`career-decision-playbook.md`）。

### architecture/
每篇对应一个架构议题。改系统前必读的顺序是：`system-overview` → `16-agents` → `orchestration-protocol` → 按需看其他。

### reference/
查表用。不讲故事，只列条目。如果某个条目需要解释，在条目里留一行链接到 user-guide 或 architecture。

### evals/
评估脚本与场景，长期跑的。

### devdocs/ (不在 docs/ 下)
`devdocs/brainstorm/`、`devdocs/research/`、`devdocs/architecture/` 里的文件是时间戳命名的内部记录（如 `2026-04-19-hermes-analysis.md`）。一次性文档 —— 写完就放那。不要回去改 —— 历史视角的价值就在于它是当时的想法。想更新就新写一篇。这些不 push 到 GitHub。

---

## 不属于 docs/ 的内容

这些东西不要放到 docs/，虽然看起来可能合理：

- **公开的安装说明**：放在 `docs/installation.md`（根部的那份），不在 `getting-started/`
- **三语 README**：在 `/README.md` 和 `/i18n/zh/README.md`、`/i18n/ja/README.md`
- **CHANGELOG**：在 `/CHANGELOG.md` 和三语版本
- **SKILL.md**：在项目根目录，是路由文件，不是 doc
- **scene configs、domain details、data model**：这些是「源」，在 `/references/` 里（注意不是 `/docs/reference/`），engine 直接读
- **agent 定义**：在 `/pro/agents/`，doc 里只能引用，不能复述

`docs/reference/` 和 `/references/` 是两个不同的地方，别混淆：
- `/references/` —— 引擎读的权威规格（`domains.md`、`soul-spec.md`、`wiki-spec.md`、`dream-spec.md`、`data-model.md`、`adapter-*.md` 等）
- `docs/reference/` —— 给人看的查表目录（9 主题字典、agent 索引、触发词表、FAQ）
