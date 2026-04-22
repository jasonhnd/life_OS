---
title: "Life OS 系统总览"
scope: 架构权威文档
audience: 作者本人 + 后续 CC / Gemini / Codex session
status: authoritative
last_updated: 2026-04-20
related:
  - docs/architecture/markdown-first.md
  - docs/brainstorm/2026-04-19-cortex-architecture.md
  - SKILL.md
  - pro/CLAUDE.md
---

# Life OS 系统总览

> 一句话：Life OS = **第二大脑 + 决策引擎 + 认知执行智能体**（三合一），架构分 **4 层**。
>
> 本文是架构的权威入口。任何新模块落地前回来对照这份分层。

---

## 1. 4 层架构（一张图）

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 4 · Python 工具层（批量/自动化，可选）                   │
│   tools/*.py · CLI 脚本 · launchd / crontab / GH Actions      │
├──────────────────────────────────────────────────────────────┤
│ Layer 3 · Shell Hook 层（runtime 强制，纯本地）                │
│   scripts/hooks/*.sh · Claude Code hook 机制                  │
├──────────────────────────────────────────────────────────────┤
│ Layer 2 · Skill 层（核心逻辑）                                 │
│   SKILL.md · pro/CLAUDE.md / GEMINI.md / AGENTS.md            │
│   pro/agents/*.md (16 个) · themes/*.md (9 个)                │
│   Cortex 升级：Pre-Router 认知前置层（v1.7 计划）              │
├──────────────────────────────────────────────────────────────┤
│ Layer 1 · 数据层 / Second Brain（真理源）                      │
│   markdown + YAML frontmatter                                 │
│   同步：iCloud + GitHub + Notion（全部可替换）                 │
└──────────────────────────────────────────────────────────────┘
```

四层之间**单向依赖向下**：上层读下层、写下层，下层不知道上层存在。去掉任意上层，下层仍完整。

---

## 2. Layer 1 · 数据层 / Second Brain

**职责**：持久化一切用户数据，作为整个系统的真理源。

### 真理源

- 格式：`.md` + YAML frontmatter
- 位置：用户本地磁盘（iCloud Drive 路径 或 `~/` 下任意目录）
- 原则：**markdown 是唯一 source of truth**。任何其他形式（数据库、Notion 镜像、索引文件）都是派生物，可以重建。

详见 `docs/architecture/markdown-first.md`。

### 目录结构

```
second-brain/
├── SOUL.md                     ← 人格档案（who you are）
├── user-patterns.md            ← 行为模式
├── wiki/                       ← 跨领域知识网络（what you know）
├── projects/{name}/            ← 有终点的事（PARA-P）
├── areas/{name}/               ← 持续领域（PARA-A）
├── archive/                    ← 已归档项目
├── inbox/                      ← 未处理原料
└── _meta/                      ← 系统元数据
    ├── STATUS.md               ← 全局状态仪表盘（编译产物）
    ├── STRATEGIC-MAP.md        ← 战略地图（编译产物）
    ├── config.md               ← 存储后端配置
    ├── journal/                ← RETROSPECTIVE / AUDITOR / ADVISOR / DREAM
    ├── outbox/{session_id}/    ← 会话输出缓冲区
    └── snapshots/soul/         ← SOUL 快照（按分钟）
```

### Cortex 新增目录（v1.7 计划）

路径模板与 `references/cortex-spec.md` §Data Structures 和 §Cortex Runtime Files 对齐。session 按 `{platform}-{ts}` 单文件落，concept 按 domain 分片。

```
_meta/
├── concepts/                              ← 概念图节点（按 domain 分片）
│   ├── INDEX.md                           ← 编译一行索引
│   ├── SYNAPSES-INDEX.md                  ← 反向边索引（编译产物）
│   ├── _tentative/                        ← 待确认
│   ├── _archive/                          ← 已退役
│   └── {domain}/{concept_id}.md           ← 单个 concept（finance / career / personal / …）
├── sessions/                              ← 单 session 摘要（按 platform + 时间戳分片）
│   ├── INDEX.md                           ← 跨 session 检索入口（hippocampus Wave 1）
│   └── {platform}-{ts}.md                 ← 每 session 一个文件（ts = YYYYMMDD-HHMM）
├── methods/                               ← 方法库（procedural memory）
│   ├── INDEX.md
│   ├── _tentative/
│   ├── _archive/
│   └── {domain}/{method_id}.md
├── snapshots/
│   └── soul/                              ← SOUL 快照（v1.6.2 机制，Cortex 下保留）
├── eval-history/                          ← AUDITOR 评估历史
├── audit/                                 ← 元认知审计（meta-cognitive audit）
│   └── suspicious.md                      ← 滚动漂移候选名单（AUDITOR 每周写入，用户降级前确认）
├── cortex/                                ← Cortex runtime state
│   ├── config.md                          ← 阈值与开关（用户可编辑）
│   ├── bootstrap-status.md                ← 迁移状态（canonical，取代已废弃的 migration-log-*）
│   └── decay-log.md                       ← 概念衰减日志（每次 adjourn 追加）
├── ambiguous_corrections/                 ← 中置信度用户纠正（0.5–0.85）待下次激活确认
│   └── {correction_id}.md
└── briefings/                             ← daily_briefing.py 产物（Layer 4 派生，非 Cortex 核心 artifact）
    └── {date}.md
```

### 同步与备份

真理源在本地 markdown。以下全部是**同步层**，不是存储层：

| 层 | 作用 | 状态 |
|----|------|------|
| **iCloud Drive** | 多台 Mac 秒级同步 | 主要同步机制 |
| **GitHub** | 跨平台备份 + 版本历史 + 跨设备拉取 | 永久备份 |
| **Notion** | 手机端 inbox 速记 + 状态查看（镜像） | 明确不是真源 |

任何一层挂掉都不影响系统运转：iCloud 断了从 GitHub 拉；GitHub 挂了本地 markdown 还在；Notion 丢了重新 push 即可。

### 存储后端适配器

`references/adapter-github.md` / `adapter-gdrive.md` / `adapter-notion.md` 定义标准读写操作。用户在 `_meta/config.md` 选 1-3 个后端，多后端时写全部、读 primary。

---

## 3. Layer 2 · Skill 层（核心逻辑）

**职责**：所有"智能"都在这层编码。模型无关、纯 markdown。

### 当前稳定版（v1.6.2a）

| 文件/目录 | 作用 |
|----------|------|
| `SKILL.md` | skill 根入口，任何平台启动时第一个被 load |
| `pro/CLAUDE.md` | Claude 平台 11 步编排协议（**唯一绑 Claude 的文件**） |
| `pro/GEMINI.md` | Gemini CLI 等价编排 |
| `pro/AGENTS.md` | Codex CLI 等价编排 |
| `pro/GLOBAL.md` | 全部 agent 必须遵守的通用规则 |
| `pro/agents/*.md` | **16 个 subagent 定义**（跨平台共享） |
| `themes/*.md` | **9 个主题文件**（只定义显示名 + tone + 语言） |
| `references/*.md` | 跨 agent 复用的规格（数据模型、适配器、4 大 spec） |

### 16 个 subagent（功能 ID）

```
router / planner / reviewer / dispatcher
people / finance / growth / execution / governance / infra
auditor / advisor / council
retrospective / archiver / strategist
```

详见 `pro/agents/*.md` 和 `references/domains.md`。

### 9 个主题

```
en-roman · en-usgov · en-csuite
zh-classical · zh-gov · zh-corp
ja-meiji · ja-kasumigaseki · ja-corp
```

主题**每会话独立**，选了 zh-classical 就全程中文、全程三省六部。详见 `themes/*.md`。

### 三段式工作流

```
Pre-Session（RETROSPECTIVE）
  ↓
Router Triage → Express / 全议 / STRATEGIST / Review
  ↓
Draft (PLANNER) → Review (REVIEWER) → Dispatch → 六部并行 → Final Review → Summary
  ↓
AUDITOR → ADVISOR
  ↓
Adjourn（ARCHIVER 4 phases）→ Notion Sync
```

详细状态机见 `pro/CLAUDE.md`。

### Cortex 升级（v1.7 计划）

Cortex **不是新一层**。是 Layer 2 的架构升级——v1.7 在现有 16 agent 之前增加一个 **Pre-Router 认知前置层**（Step 0.5），并扩展 ARCHIVER Phase 2：

```
User message
  ↓
[Cortex Pre-Router · Step 0.5]  ← 三路并行信号源
  - hippocampus 子 agent（扫描 _meta/sessions/INDEX.md，返回 top 5-7 记忆信号）
  - concept lookup（扫描 _meta/concepts/，返回直接命中的 concept 节点 + 1-hop 邻居）
  - SOUL dimension check（复用 RETROSPECTIVE SOUL Health Report，发出 identity_check 信号）
  ↓
[GWT 仲裁]（salience 竞争 + top-K 广播）
  ↓
Annotated input → ROUTER（原 16 agent 流程不变）
  ↓
…Summary Report…
  ↓
[叙事层 · Step 7.5]（narrator-validator，仅 Full Deliberation）
  ↓
[ARCHIVER Phase 2]
  - wiki / SOUL 自动写（既有）
  - concept extraction（新）：候选分类 permanence tier，写入 _meta/concepts/{domain}/{concept_id}.md
  - Hebbian update（新）：共激活 concept 对边权 +1，新边 weight=1，重建 SYNAPSES-INDEX.md
  - 衰减 pass（新）：长期未用边按 permanence 衰减，追加 _meta/cortex/decay-log.md
  - session summary 写入 _meta/sessions/{platform}-{ts}.md
```

当前 v1.6.2a 的 ROUTER 直接收用户原 message；v1.7 Cortex 升级后 ROUTER 收的是"带记忆标注 + signal citation 的输入"。concept extraction 和 Hebbian 不在 Pre-Router，属于 ARCHIVER Phase 2 在 adjourn 单次调用内完成的独立机制（spec §Step 10）。

详见 `docs/brainstorm/2026-04-19-cortex-architecture.md`。v1.7 spec：`references/cortex-spec.md`。

---

## 4. Layer 3 · Shell Hook 层（runtime 强制）

**职责**：在 LLM session 之外、OS 层面强制执行不可违反的规则。纯本地，不依赖网络。

基于 Claude Code 原生 hook 机制（`settings.json` 里的 `hooks.*`）。Gemini / Codex 有等价机制但 API 不同。

### 已有

| 脚本 | 作用 |
|------|------|
| `scripts/setup-hooks.sh` | 一键安装全部 hook 到 `~/.claude/settings.json` |
| `scripts/lifeos-version-check.sh` | Start Session 时校验本地 version 和 remote 是否对齐 |

### v1.7 计划

| Hook 类型 | 脚本名 | 作用 |
|----------|-------|------|
| UserPromptSubmit | `pre-prompt-guard.sh` | 用户 message 进来前检查 trigger 词，强制 load 对应 agent 定义 |
| PreToolUse (Write\|Edit) | `pre-write-scan.sh` | Write/Edit 前扫描文件是否包含隐私敏感词，阻止违规写入 |
| PreToolUse (Read) | `pre-read-allowlist.sh` | Read 前检查 denylist（~/.ssh/**、~/.aws/**、/etc/passwd 等），阻止敏感路径读取 |
| PostToolUse | `post-response-verify.sh` | 每个 subagent 输出后校验格式（emoji 进度汇报、citation 引用） |
| Stop | `stop-session-verify.sh` | Session 结束时校验是否走完 adjourn 4 phases，缺失则报错 |

### 为什么需要 Layer 3

SKILL.md 和 pro/CLAUDE.md 里写了"HARD RULE"，但 LLM 可能忘记或绕过。Shell hook 在 runtime 层面**机械执行**：

- Layer 2 规则："adjourn 必须走 4 phases"——LLM 可能跳步
- Layer 3 hook："Stop 时如果没检测到 4 phases 标记 → 报错阻止会话结束"——无法绕过

Layer 3 是 Layer 2 的**兜底**。不是替代。

---

## 5. Layer 4 · Python 工具层（批量/自动化，可选）

**职责**：session 之外的批量任务、调度任务、重计算任务。**整层可选**，不装也能用。

纯 CLI 脚本。不绑定任何特定云服务。

### 当前与计划的脚本

> **Tool naming convention**: Python modules use `snake_case` (the on-disk filename
> under `tools/`, e.g., `tools/daily_briefing.py`). CLI subcommands use `kebab-case`
> (e.g., `uv run life-os-tool daily-briefing`). Both refer to the same tool. This is
> standard Python-vs-CLI convention — Python imports require underscores; CLI args
> conventionally use hyphens.

```
tools/
├── reindex.py              ← 重建 wiki/INDEX + _meta/STATUS.md + sessions/INDEX.md + SYNAPSES-INDEX.md(concept 反向索引,concept 层产物)
├── reconcile.py            ← 多后端一致性检查
├── stats.py                ← 使用统计（agent 调用次数 / 成本 / 决策数）
├── research.py             ← 后台研究（读 inbox 的 research 任务，抓网、生草稿）
├── embed.py                ← 为 session / concept 生成 embedding（可选）
└── daily_briefing.py       ← 基于 STATUS.md + 日历生成每日简报
```

### 运行方式（任选）

| 触发 | 适用 |
|------|------|
| **手动** | `python tools/reindex.py`，用户想跑就跑 |
| **macOS launchd** | 本机定时（每天 8:00 跑 daily-briefing） |
| **crontab** | 同上，另一种实现 |
| **GitHub Actions** | 跨设备调度（仅限架构可选，v1.7 不做远程调度——用户决策 #1） |
| **任意云服务（Vercel / Railway / Fly.io / …）** | 如果用户想要公网入口，可选 |

**关键**：Layer 4 scheduler 可以是 **launchd / cron / GH Actions / Vercel / 零**。Life OS 不预设任何一种。

### Layer 4 做什么 / 不做什么

| 做 | 不做 |
|----|------|
| I/O + 模式匹配 | LLM 推理 |
| 文件索引重建 | 决策生成 |
| 状态聚合 | 替代 session |
| 推送通知 | 存储真源数据 |

复杂推理永远在 session 里的 LLM，Layer 4 只做"提醒用户打开 session"级别的任务。

---

## 6. 三个方向 → 4 层映射

| 方向 | 主要在哪层 | 辅助层 |
|------|-----------|--------|
| **第二大脑**（知识持久化） | Layer 1 | — |
| **决策引擎**（16 agent 工作流） | Layer 2 | — |
| **认知执行智能体**（Cortex + runtime + 自动化） | Layer 2 (Cortex) + Layer 3 (Hook) + Layer 4 (Python) | Layer 1（新增 concepts / sessions / methods / cortex / eval-history / audit / ambiguous_corrections 7 个目录） |

第二大脑和决策引擎是 **v1.6.2a 已交付** 的能力。认知执行智能体是 **v1.7 计划** 的演化方向。

---

## 7. 双重独立性原则

Life OS 的"不绑定"有**两条独立的腿**，缺一条都不行。

### 模型独立

- **绑模型的文件**：仅 `pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` 三份编排协议
- **不绑模型的文件**：`SKILL.md`、`pro/GLOBAL.md`、`pro/agents/*.md`、`themes/*.md`、`references/*.md`、second-brain 全部
- **换模型成本**：新平台写一份 `pro/{NEW}.md` 照 CLAUDE.md 改工具名映射，其他 0 改动

### 存储独立

- **真理源**：本地 markdown 文件
- **派生层**（全部可替换、可丢弃）：
  - iCloud / GitHub / Notion（同步与备份）
  - SQLite / Turso / Supabase / pgvector（可选索引层）
  - Vercel / Railway / Fly.io / GH Actions（可选调度层）
  - 任何 SaaS（Life OS 不绑定任何一家）
- **换存储成本**：iCloud 换路径 / GitHub 换 repo / Notion 换 workspace，真源文件位置是配置项

这两条合起来是 Life OS 的"**可迁移性保证**"：换模型不迁数据，换存储不改 agent，断网也能本地跑。

---

## 8. 数据流示例（完整 session）

真实走一遍"我要不要辞职"：

```
【0 · Layer 3】
用户输入 "我要不要辞职 （complex 决策 trigger）"
  pre-prompt-guard.sh 检测到高优先级 trigger
  → 确保 SKILL.md + pro/CLAUDE.md 已 load

【1 · Layer 2 · Cortex Pre-Router】（v1.7）
  海马体子 agent 扩散激活 → 检索 projects/career/ + SOUL "risk_tolerance" + wiki
  返回带记忆标注的输入给 ROUTER

【2 · Layer 2 · 16 agent 工作流】
  ROUTER 识别为全议 → 2-3 轮意图澄清
  PLANNER 起草 → REVIEWER 审议（可能 veto 回送）
  DISPATCHER 调度 → FINANCE / PEOPLE / GOVERNANCE / INFRA 并行分析
  REVIEWER 终审 → COUNCIL（如果分歧 > 3 分）
  ROUTER 产出 Summary Report
  AUDITOR → ADVISOR

【3 · Layer 2 · Cortex 叙事层】（v1.7）
  Summary Report 每条 substantive claim 带 signal_id citation
  Sonnet Claude Code subagent（narrator-validator）校验 citation 合法性 → 不合格则 Opus 重生成

【4 · Layer 2 · ARCHIVER（adjourn 4 phases）】
  Phase 1：决策/任务/日志 → outbox
  Phase 2：wiki/SOUL 候选自动写 + Hebbian 更新 concept 权重（v1.7）
  Phase 3：DREAM（3 天回溯 + REM 连接）
  Phase 4：git push + 返回 Completion Checklist

【5 · Layer 1】
  文件落盘到 second-brain（iCloud 自动多设备同步）
  outbox 等待下次 RETROSPECTIVE 合并

【6 · Orchestrator (main context)】
  调用 Notion MCP → 同步到 Current Status / Todo Board / Working Memory / Inbox

【7 · Layer 3】
  stop-session-verify.sh 校验 Completion Checklist 完整
  若缺 phase → 报错阻止会话结束

【8 · Layer 4（可选）】
  launchd 凌晨跑 reindex.py → 重建 wiki/INDEX.md + sessions/INDEX.md + SYNAPSES-INDEX.md（concept 反向索引，concept 层 reindex 产物）
  launchd 早 8:00 跑 daily_briefing.py → 写入 `_meta/briefings/{date}.md`（不做独立 bot / 跨平台推送）
```

每一步都**只读写本地文件**。网络可用是 enhancement，不是 requirement。

---

## 9. 跨平台一致性

| 平台 | Layer 1 | Layer 2 | Layer 3 | Layer 4 |
|------|---------|---------|---------|---------|
| **Claude Code** | 完整 | 完整 | 完整（原生 hook） | 完整 |
| **Gemini CLI / Antigravity** | 完整 | 完整 | 部分（hook 机制不同） | 完整 |
| **OpenAI Codex CLI** | 完整 | 完整 | 部分（AGENTS.md open standard） | 完整 |

### 差异所在

- **Layer 1**：纯文件，三平台 100% 共用
- **Layer 2**：16 agent + 9 theme + GLOBAL.md 三平台共用；唯一差异在编排文件（CLAUDE.md / GEMINI.md / AGENTS.md）
- **Layer 3**：Claude Code 的 hook 是一等公民；Gemini / Codex 需要自行实现等价机制（Gemini / Codex 的 hook API 稳定后在后续版本打平）
- **Layer 4**：纯 Python，三平台 100% 共用

换句话说：**Layer 2 的差异只在 3 份编排文件**，其他 99% 跨平台通用。

---

## 10. Life OS 不做什么

明确边界。任何未来扩展都不应跨越下面任何一条：

- ❌ **不引入中心化数据库作为真理源** — 没有 Postgres / SQLite / Supabase 承担主存储。数据库可以做索引或缓存，**不能是 source of truth**
- ❌ **不依赖任何云服务做核心状态** — iCloud / GitHub / Notion / Vercel / 任意 SaaS 挂掉，系统仍基于本地 markdown 完整运行
- ❌ **不假设网络可用** — 所有决策路径必须在纯离线环境跑通
- ❌ **不做多租户** — 单人工具。没有共享账号、权限矩阵、team workspace。团队版是不同的产品
- ❌ **不做实时协作** — 跨设备冲突用文件锁 + 顺序 merge，不走 CRDT / OT
- ❌ **不绑定 Vercel 或任何特定 SaaS** — Vercel 只是 Layer 4 的一种**可能实现**，和 launchd / crontab / GH Actions / 纯手动并列
- ❌ **云服务是可选、可替换、可零化** — 完全本地也能运转

这些"不做"共同保证了 Life OS 的两个根本特性：**你的数据永远是你的**，**断电断网你的系统还在**。

---

## 11. 相关架构文档

| 文档 | 内容 | 状态 |
|------|------|------|
| `docs/architecture/markdown-first.md` | markdown 作为真理源的哲学详解、frontmatter 规范、派生物重建规则、Hermes 对照 | ✅ 已写 |
| `docs/architecture/cortex-integration.md` | Cortex 认知升级如何融入 Layer 2 | ✅ 已写 |
| `docs/architecture/execution-layer.md` | Layer 3 Shell Hook + Layer 4 Python 工具的完整规格 | ✅ 已写 |
| `docs/architecture/roadmap.md` | v1.6.2a → v1.7 的版本推进计划 | ✅ 已写 |
| `docs/research/2026-04-20-storage-decision.md` | 存储决策的完整 ADR（为什么选 markdown、哪些方案被否决） | ✅ 已写 |
| `docs/brainstorm/2026-04-19-cortex-architecture.md` | Cortex 架构的完整思考轨迹（辩论、re-frame、共识） | ✅ 已写 |

---

## 12. 扩展点

| 想加什么 | 改哪里 | 举例 |
|---------|-------|------|
| 新主题 | `themes/` 加文件 | 加 `themes/en-silicon-valley.md` |
| 新 agent | `pro/agents/` 加文件 + SKILL.md 角色表加一行 | 加 `pro/agents/therapist.md` |
| 新平台 | 复制 `pro/CLAUDE.md` 改工具名映射 | 加 `pro/CURSOR.md` |
| 新 Shell hook | `scripts/hooks/` 加脚本 + setup-hooks.sh 注册 | 加 `scripts/hooks/no-commit-secrets.sh` |
| 新 Python 工具 | `tools/` 加脚本 | 加 `tools/weekly_review.py` |
| 新存储后端 | `references/adapter-{name}.md` 加标准数据操作 | 加 `adapter-obsidian.md` |
| 新 Cortex 模块（v1.7） | `pro/agents/` 加子 agent + `_meta/concepts/` 加新字段 | 加 `pro/agents/amygdala.md` |

**核心扩展哲学**：加东西不应该改其他层。加新主题不动 agent；加新 agent 不动主题；加新 hook 不动 Python 工具。

---

**最后更新**：2026-04-20，v1.6.2a 稳定版 + v1.7 Cortex 设计中。
