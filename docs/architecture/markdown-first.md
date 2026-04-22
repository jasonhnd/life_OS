---
title: "Markdown-First 架构"
scope: 本地参考文档
audience: 作者本人
status: authoritative
last_updated: 2026-04-20
related:
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - references/data-layer.md
  - references/data-model.md
---

# Markdown-First 架构

> Life OS 的真理源永远是 markdown 文件。这不是"暂时方案"，是**根本哲学**。
>
> 本文档记录这个决定的理由、对照、替代方案、失败模式。Cortex 阶段的任何实现都要回来对照这份文档。

---

## 1. 核心原则

1. **Markdown 是唯一真理源** — SOUL.md / wiki / concept / snapshot / session 归档全是 `.md` + YAML frontmatter
2. **iCloud + GitHub 做多设备同步和备份** — 写入 iCloud 路径，自动在多设备同步；git push 是永久备份
3. **不引入任何数据库作为真理源** — 没有 SQLite、没有 Postgres、没有 Supabase、没有 vector DB
4. **云端服务是可选的，且可互换** — 若需自动化或公网入口，可选 launchd / crontab / GitHub Actions / Cloudflare Workers / Vercel Cron 等任意一种；无任何一项是 Life OS 架构的一部分
5. **所有"智能"都在 session 内执行** — Claude 读 markdown，推理，写 markdown。不需要 runtime
6. **任何 LLM 都能运行** — 切模型 = 改 CLAUDE.md 里的路径引用，其他文件不动
7. **没 AI 也能用** — 打开 Obsidian，直接读写 markdown。LLM 是加速器，不是依赖

---

## 2. 为什么 Life OS 不需要 Hermes 的 SQLite

Hermes（参考的另一个 agent 框架）用 SQLite + FTS5 存每一条消息、每一次工具调用、每一段 trajectory。理由：**通用 agent**。用户可能回头问"上周二下午 3 点我们聊过什么"，必须能全文搜原文。

Life OS 不是这个形态。

### 产出形态的根本不同

| 维度 | Hermes | Life OS |
|------|--------|---------|
| 产出目标 | 保留原对话供检索 | 提炼结构化摘要 |
| 单元 | 每条消息 | 每次 session |
| 存储形式 | raw messages + FTS5 索引 | wiki / SOUL update / decision / journal |
| 回溯方式 | "给我原文" | "给我当时的结论" |
| 类比 | 录音笔 | 会议纪要 |

Hermes 的口号是"**记住每一句**"。Life OS 的口号是"**提炼每一次**"。

### 数字对比

假设用户每天 2 个 session，5 年连续使用：

```
session 数 = 2 × 365 × 5 = 3650
每个 session summary 约 200 中文字 = 约 400 字节
全部 session summary 总大小 = 3650 × 400 字节 ≈ 1.5 MB
```

INDEX.md（每个 session 一行摘要 + YAML 元数据）：

```
3650 行 × 每行 ~150 字节 ≈ 550 KB
```

这个量级对 `ripgrep` / `grep` 是小菜——扫完整个 INDEX **<10ms**。扫全部 session summary **<100ms**。

让 LLM 读这 1.5 MB ≈ 50 万 token。Opus 4.7 1M context 一次吞得下，成本 $0.5 左右。**实际不会这么蠢**——先让 ripgrep / INDEX 筛到相关的 20 个 session（约 8KB），再让 LLM 读，成本 <$0.01。

### 结论

Hermes 需要 SQLite 是因为它不知道用户要什么，必须全留。Life OS 知道自己要什么——**只要提炼后的结构化产物**，这些本来就是 markdown 友好的。用 SQLite 是解一个 Life OS 没有的问题。

---

## 3. Hermes 功能对照表

Hermes 的 14 个核心能力，Life OS 在 markdown 架构下的对应方式：

| Hermes 功能 | Life OS 做法 | 依赖 |
|-------------|--------------|------|
| MEMORY.md / USER.md / SOUL.md | 已经是 markdown | 无 |
| Skills 系统 | markdown + YAML frontmatter | 无 |
| Subagent 委派 | 纯 runtime（Claude Code 原生） | 无 |
| 47 工具 dispatch | 纯 runtime | 无 |
| 并行工具执行 | 纯 runtime | 无 |
| 上下文压缩 | 纯 runtime | 无 |
| 上下文压缩算法 | 纯 runtime | 无 |
| Gateway 平台路由 | `_meta/config.md` 的 YAML | 无 |
| Cron 定时任务 | 可选调度器（launchd / cron / GitHub Actions / Cloudflare Workers / Vercel Cron 等）+ 脚本 | 调度器之一（可选，非必须） |
| Trajectory 记录 | `_meta/journal/{date}.md` | 无 |
| 凭证池 | `_meta/config.md` + env | 无 |
| OAuth 刷新 | 适配器自管（Notion/GDrive） | 各 MCP |
| 插件记忆提供者 | 各插件自管 | 无 |
| **Cross-session 搜索** | **INDEX.md + LLM 筛选** | **见 §4.1** |

14 项里只有**最后一项**需要单独设计。其余全是"已经 markdown"或"纯 runtime，和存储无关"。

---

## 4. 各"数据库功能"的 markdown 实现方案

### 4.1 跨 session 搜索

**需求**：用户问"我之前关于白皮书的决策有哪些？"

**文件结构**：

```
_meta/
├── sessions/
│   ├── INDEX.md                              ← 编译产物，一行一条
│   ├── claude-20260412-1700.md               ← 完整摘要
│   ├── claude-20260415-1430.md
│   └── gemini-20260418-0900.md
```

INDEX.md 每行格式：

```markdown
- 2026-04-12 17:00 [claude] [whitepaper] 白皮书 v5.4 deployed,决定延后 v5.5,争议点:章节3 :: claude-20260412-1700.md
- 2026-04-15 14:30 [claude] [whitepaper] 章节3 拆分方案,REVIEWER 一票否决,rebuttal 1/2 :: claude-20260415-1430.md
- 2026-04-18 09:00 [gemini] [career] 日本入管签证延长风险评估,GOVERNANCE 建议提前半年启动 :: gemini-20260418-0900.md
```

YAML frontmatter（INDEX.md 顶部）：

```yaml
---
compiled_at: 2026-04-20T08:00:00+09:00
total_sessions: 182
platforms: [claude, gemini, codex]
projects: [whitepaper, career, life-os, startup-x]
---
```

**搜索流程**：

```
User: "我之前关于白皮书的决策"
   ↓
RETROSPECTIVE (海马体子 agent) 读 INDEX.md
   ↓
ripgrep "whitepaper" → 15 行
   ↓
LLM 读这 15 行,筛出与"决策"相关的 5 条 (≈ 3000 token, <$0.01)
   ↓
读这 5 个完整 session md (≈ 5 KB × 5 = 25 KB)
   ↓
合成答案
```

**性能**：

| 步骤 | 时间 | 成本 |
|------|------|------|
| ripgrep 扫 INDEX | <10ms | $0 |
| LLM 筛 15 行 → 5 条 | ~1s | <$0.01 |
| 读 5 个完整 session md | <50ms | $0 |
| LLM 合成答案 | ~2s | ~$0.05 |
| **总计** | **~3s** | **~$0.06** |

对比 Hermes FTS5：大概 1-2s。差 1-2 秒，但成本差不多（Hermes 还是要 LLM 合成答案）。对个人使用，**3 秒完全可接受**。

**何时撑不住**：INDEX.md 超过 5000 行时 ripgrep 还能扫，但 LLM 筛选要分批。按每天 2 session 算，够用 **5-10 年**。

---

### 4.2 概念图 + 突触权重

**需求**：Cortex 架构的突触层——每个 concept 有向外连接的边，边有权重（赫布强化）。

**文件结构**：

```
_meta/concepts/
├── INDEX.md                                  ← 所有 concept 的 one-liner
├── SYNAPSES-INDEX.md                         ← 反向索引（编译产物）
├── finance/
│   ├── company-a-holding.md
│   └── company-b-finance.md
├── career/
│   └── whitepaper-submission.md
└── _tentative/                               ← 待确认
    └── 2026-04-20-unknown-entity.md
```

**单个 concept 文件**：

```markdown
---
concept_id: company-a-holding
status: canonical
canonical_name: Company-A
aliases: [Company-A Holdings, A 社ホールディング]
domain: finance
permanence: fact
activation_count: 47
last_activated: 2026-04-18
created: 2025-11-03
outgoing_edges:
  - to: company-b-finance
    weight: 8
    via: [authentication-reuse, shared-board]
    last_reinforced: 2026-04-15
  - to: tokyo-office-lease
    weight: 3
    via: [capital-allocation]
    last_reinforced: 2026-03-20
---

# Company-A

控股母体，持有 Company-B 多数股权。认证流程共享,董事会有 3 名共同成员。

## Related
- [[company-b-finance]] (subsidiary)
- [[tokyo-office-lease]] (lessee)
```

**突触更新（archiver Phase 2）**：

session 结束时，如果 company-a-holding 和 company-b-finance 都被激活过 →

```python
# 伪代码：archiver 的 subagent 执行
for edge in concept["outgoing_edges"]:
    if edge["to"] in activated_this_session:
        edge["weight"] += 1
        edge["last_reinforced"] = today
```

具体实现是 agent 用 Edit 工具改 YAML frontmatter——不是脚本。

**反向查询（谁指向我）**：

```bash
rg "to: company-a-holding" _meta/concepts/ --type md -l
```

结果：

```
_meta/concepts/finance/subsidiary-holdings.md
_meta/concepts/career/board-overlap.md
```

或查预编译的 `SYNAPSES-INDEX.md`：

```markdown
## company-a-holding (incoming)
- subsidiary-holdings (weight 5)
- board-overlap (weight 2)
```

SYNAPSES-INDEX.md 在 archiver Phase 2 末尾重新生成——遍历所有 concept md，反转边，写入。

**性能**：3000 个 concept 的反向索引重建约 5 秒。不是每次都跑，是 session 结束跑一次。

---

### 4.3 SOUL 快照（趋势箭头）

**需求**：RETROSPECTIVE 在 Start Session 显示 SOUL Health Report，包含每个维度的趋势箭头（↗ ↘ →）。

**文件结构**：

```
_meta/snapshots/soul/
├── 2026-04-12-1700.md
├── 2026-04-15-1430.md
├── 2026-04-18-0900.md
├── 2026-04-20-0800.md
└── _archive/                                 ← >30 天
    └── 2026-03/
        └── 2026-03-05-1000.md
```

**单个快照**：

```yaml
---
session_id: claude-20260420-0800
timestamp: 2026-04-20T08:00:00+09:00
dimensions:
  integrity:
    confidence: 0.92
    evidence_count: 47
    challenges: 2
    note: "4 月新增 3 条证据,2 次拒绝 shortcut"
  risk_tolerance:
    confidence: 0.68
    evidence_count: 18
    challenges: 7
    note: "近期 3 次回避大额投注,confidence 下降"
  family_first:
    confidence: 0.81
    evidence_count: 22
    challenges: 1
    note: "推掉两次出差,强支持信号"
  # ... 其他维度
new_dimensions: []
soul_conflicts: []
---

# SOUL Snapshot 2026-04-20 08:00

本次 session 无 SOUL 维度冲突。
risk_tolerance 连续两次 session 下降,AUDITOR 建议观察。
```

**趋势计算（RETROSPECTIVE Mode 0）**：

```
1. 读取 _meta/snapshots/soul/ 下最近两个文件
2. 对齐每个 dimension,diff confidence
3. Δ > +0.05 → ↗
   Δ < -0.05 → ↘
   |Δ| ≤ 0.05 → →
4. 合成 SOUL Health Report 显示在 briefing 顶部
```

**归档策略**：

- \>30 天 → `_archive/{YYYY-MM}/`（保留，不删）
- \>90 天 → 从 iCloud 删除，仅保留 git 历史 + Notion 存档
- 永不彻底删（git log 永久）

---

### 4.4 评估历史（系统性问题检测）

**需求**：连续几次 adjourn 检测到 completeness <6 → 触发告警"你最近一直没完整走 adjourn 流程"。

**文件结构**：

```
_meta/eval-history/
├── 2026-04-12-whitepaper.md
├── 2026-04-15-whitepaper.md
├── 2026-04-18-career.md
└── 2026-04-20-whitepaper.md
```

**单个评估**：

```yaml
---
session_id: claude-20260420-0800
project: whitepaper
evaluator: AUDITOR
criteria:
  adjourn_completeness: 9
  intent_clarification_rounds: 7
  veto_respected: 10
  wiki_privacy_check: 10
  soul_update_grounded: 8
issues: []
severity: ok
---
```

**系统性问题检测（RETROSPECTIVE Mode 0）**：

```
1. ripgrep 最近 10 个 eval 文件
2. 按 criteria 分组,算最近 3 次的均值
3. 某个 criteria 连续 3 次 < 6 → 告警
4. 写入 briefing: "⚠️ adjourn_completeness 近 3 次均值 5.3,最近一次中途跳过了 DREAM"
```

这个告警写进 briefing——用户看到 → 自己调整，不需要 LLM 主动纠错。

---

### 4.5 语义搜索（可选增强）

**需求**：用户问"类似的权衡我之前做过吗？"——关键词不一定匹配（"白皮书 vs 产品"和"学术 vs 商业"是同一类权衡，但关键词不同）。

**方案 A：LLM 判断（推荐）**

```
RETROSPECTIVE 读 INDEX.md 全部
   ↓
LLM prompt:
  "用户问题: [q]
   以下是过去 182 个 session 摘要:
   [INDEX.md 全文]
   找出语义最相似的 5 个,按相似度排序,给出简短理由。"
   ↓
返回 5 个 session_id
   ↓
读这 5 个完整 session md
```

成本：每次查询约 $0.10-0.20（INDEX.md ≈ 60K token + query + output）。

**方案 B：embedding 存 YAML（更贵的一次性投入）**

每个 session md 首次生成时嵌入 1536 维向量，存在 YAML：

```yaml
---
session_id: claude-20260420-0800
embedding: [0.034, -0.012, 0.087, ...]   # 1536 float
embedding_model: text-embedding-3-small
embedding_generated_at: 2026-04-20T09:00:00+09:00
---
```

查询时：

```python
# Python 脚本(不是必须,可由 agent 调用)
query_vec = embed(query)
for session in all_sessions:
    score = cosine(query_vec, session.embedding)
best_5 = top(scores, 5)
```

**成本对比**：

| 方案 | 一次性成本 | 每次查询 | 延迟 |
|------|----------|----------|------|
| A（LLM 判断） | $0 | $0.10-0.20 | 3s |
| B（embedding） | $0.10（生成所有历史 embedding） | ~$0.001（只需 embed query） | 100ms |

**推荐路径**：

- **Phase 1**：方案 A。session 数 <1000 时完全够用，无额外依赖。
- **Phase 2**（session > 1000 或用户频繁跨 session 查询）：加方案 B 作为增量优化。主数据仍在 markdown，embedding 只是 YAML 额外字段。

---

## 5. 可选自动化（多种选项，Vercel 只是其一）

**自动化不是 Life OS 架构的一部分**，而是 Layer 4 Python 工具的一种**运行模式**。真理源永远是 markdown + iCloud + GitHub。

Life OS 的 markdown 系统默认是被动的——只有用户打开 session 才运行。若希望某些任务**主动触发**（如每日扫 stale commitment），可以让 Layer 4 的 Python 工具跑在任何调度器上。这是**实现选择**，不是架构依赖。

### 5.1 调度器选项（挑一种，或啥都不用）

| 方案 | 适合谁 | 成本 | 备注 |
|------|--------|------|------|
| **macOS launchd** | Mac 用户（最简单） | $0 | 本地 LaunchAgent plist，最低门槛 |
| **crontab** | Linux/Mac 传统方式 | $0 | 一行 cron 配置 |
| **GitHub Actions** | 需要免费 + 公开触发 | $0 | 公开仓库免费 2000 分钟/月 |
| **Cloudflare Workers cron** | 需要全球低延迟 | $0 起 | 有免费版，100k req/day |
| **Vercel Cron** | 已经在用 Vercel 的人 | 含在现有订阅 | 若你已经有账户才有意义 |
| **啥都不用** | 纯手动派 | $0 | session 里自己跑脚本 |

**关键**：这一层跑什么不影响 markdown 架构。换调度器 = 迁移一两个 cron 配置，其他文件不动。

### 5.2 自动化任务的典型场景

不管用哪种调度器，脚本做的事相同：

| 任务 | 频率 | 做什么 |
|------|------|--------|
| stale commitment 扫描 | 每天 8:00 JST | ripgrep 所有 `projects/**/tasks/` 里 status=waiting 超过 30 天的,写入 `_meta/briefings/{date}.md` 供下次 session 读取 |
| 系统性问题扫描 | 每周日 20:00 | 读 `_meta/eval-history/` 近 10 条,检测连续劣化,写入 briefing |
| SOUL 趋势月报 | 每月 1 日 9:00 | 读 `_meta/snapshots/soul/` 月度对比,生成月报写入 `_meta/briefings/` |
| Notion inbox 拉取 | 每小时 | 拉 Notion inbox 未处理项 → 写入本地 `inbox/` (待用户下次 session 处理) |

**原则**：脚本只做 I/O 和模式匹配。复杂推理留给 session 里的 Claude——脚本写 briefing 文件说"你有 3 个 stale task"，下次 session 打开时 RETROSPECTIVE Mode 0 呈现给 Claude 处理。**不做独立 bot / 常驻 agent / 跨平台消息推送**——Life OS 是本地 Claude Code 内的决策引擎，不是独立 bot / agent 产品（v1.7 scope 明确剥离）。

### 5.3 移动端捕捉（通过 Notion）

如果需要从手机或其他设备捕捉 idea，使用用户已有的工具：

```
手机端 Notion app / Apple Shortcuts / 语音备忘录
                        ↓
                 Notion inbox database
                        ↓
         (下次 session) RETROSPECTIVE pull Notion inbox
                        ↓
                 写入本地 markdown inbox/
```

推荐路径：
- **Notion 移动端**：手机上直接在 Notion inbox database 新建条目
- **Apple Shortcuts**：一键从 iOS/macOS 推送文本到 Notion（Notion API）
- **macOS 语音备忘录**：碎片时间口述，Claude Code session 内 import

**不做**：专门搭建 Telegram bot / webhook / 独立 HTTPS 接收端 / Cloudflare Workers / Vercel Edge Function。所有移动端捕捉都通过用户现有工具（Notion / Apple 生态）完成——Life OS 不引入独立进程形态。

### 5.4 云端服务永远不做的事

| 不做 | 原因 |
|------|------|
| 存用户 markdown | 真理源是 iCloud + GitHub |
| 持久化数据库 | 引入就违反了架构 |
| 存 API key 以外的用户状态 | session 状态在 markdown |
| 做推理 | 推理在用户本地 session 的 Claude |

无论选哪个调度器或 webhook 入口，它们都不是存储层，也不是推理层。Life OS 不假设用户付任何订阅——包括 Vercel Pro。

---

## 6. 什么时候回来考虑数据库

> **提前声明**：本节是**假设性讨论**，不是当前或近期计划。Phase 1 Cortex 完全用 markdown，触发条件没满足就不迁移。

**触发条件**（任意一条满足都是 signal，不是立即迁移）：

- INDEX.md 超过 **5000 行**（约 5000 session）
- LLM 每月扫 INDEX 的 token 成本稳定 **>$20**
- 做**多用户公开产品**（不只自己用）
- 真的需要**毫秒级**查询（当前 3-5 秒完全够个人用）

**回来时的方案（大致等价的几个选项，无优先级）**：

各方案下 markdown 仍是真理源，数据库是派生索引。按自己的环境挑一个就行。

### 选项：本地 SQLite + FTS5（Hermes 模式）

```
优点: 零成本,完全本地,能随时重建索引
权衡: 每台设备独立一份索引,多设备要各自重建
做法: 每台设备首次用时跑一个 "indexer" 脚本扫 markdown → 建 SQLite,每次 session 结束增量更新
成本: $0
```

### 选项：Turso (libSQL 云同步)

```
优点: 本地优先 + 云端同步,兼顾性能和跨设备
权衡: 多了一个 vendor
做法: 同上,但 SQLite 文件放 Turso,自动多设备同步
成本: $0-9/月(小用量免费)
```

### 选项:Supabase (pgvector)

```
优点: 云原生,pgvector 原生支持 embedding 语义搜索
权衡: 完全云端,离线就废
做法: markdown 继续是真理源,每次 session 结束推一份到 Supabase 做索引
成本: $25/月(Pro)
```

### 选项：Vercel Postgres

```
优点: 如果已经用 Vercel 做其他事,集成简单
权衡: 锁定 Vercel,性能不如 Supabase
做法: 同 Supabase 方案
成本: 随 Vercel 计划
```

**决策原则**：上述四个方案粗略等价，等到触发条件真的满足了再根据当时的上下文挑一个。Phase 1 Cortex 不为"可能要的规模"做准备，也不为任何一个 vendor 做准备。

---

## 7. 失败模式与兜底

每一层都有 fallback，零 vendor lock-in。

### 7.1 markdown 文件损坏

```
症状: 某个 session md 的 YAML frontmatter 破了,解析失败
兜底:
  1. git log <file> → 找到最后一个好版本
  2. git checkout HEAD~1 -- <file> → 恢复
  3. 如果 git 也坏 → Notion 存档是第三份备份
```

### 7.2 iCloud 同步出问题

```
症状: iPad 和 Mac 看到不同版本的 SOUL.md
兜底:
  1. RETROSPECTIVE Mode 0 首先读 _meta/config.md 的 last_sync_time
  2. 比对 git log,用 git 的时间戳为准
  3. 冲突时按 conflict resolution 规则(time diff < 1min → 保留两份,问用户)
  4. 最坏情况: 完全以 GitHub 的为准,iCloud 覆盖
```

### 7.3 GitHub 不可达

```
症状: push 失败,网络问题或 GH outage
兜底:
  1. 本地 markdown 继续工作,session 不受影响
  2. archiver Phase 4 的 git push 标记为失败,写 _meta/sync-log.md
  3. 下次 session 开始时 RETROSPECTIVE 重试
  4. 期间 iCloud 保证多设备还能同步
```

### 7.4 某个 agent 编造了 YAML frontmatter

```
症状: concept md 的 outgoing_edges 指向不存在的 concept
兜底:
  1. 周度 patrol(AUDITOR Mode 2) 检查引用完整性
  2. ripgrep 每个 "to: X" 验证 X 存在
  3. 不存在的边标红报告到 inbox
  4. 用户人工决定删边还是创建 X
```

### 7.5 Notion MCP 断连

```
症状: 无法同步移动端
兜底:
  1. RETROSPECTIVE Mode 0 探测时标记 SKIPPED
  2. 当前 session 继续,所有读写走 GitHub(primary)
  3. 用户知道 "移动端暂时看不到更新",不影响本次工作
  4. 下次 MCP 恢复自动续传 sync-log.md 里的积压
```

### 7.6 所有后端都不可达

```
症状: 无 GitHub / iCloud 同步,仅本地磁盘
兜底:
  1. 系统继续运行,session 照常进行
  2. 输出仅存在于对话,不持久化
  3. 提示 "⚠️ 数据未持久化,请尽快恢复同步"
  4. 用户至少能把关键结论复制到其他地方
```

---

## 8. 速查：新功能落地到 markdown 的设计 checklist

写任何 Cortex 新模块时，先对照这份 checklist：

- [ ] 这个功能的真理源能放在哪个 `.md` 文件里？
- [ ] 这个 `.md` 的 YAML frontmatter 需要哪些字段？
- [ ] 编译/聚合视图写在哪个 INDEX？什么时候重算？（archiver Phase 2 / RETROSPECTIVE Mode 0）
- [ ] 反向查询用 ripgrep 还是预编译索引？预估查询延迟？
- [ ] 这个功能需要 cron 吗？如果需要，cron 只做 I/O + 模式匹配，复杂推理留给 session。
- [ ] 失败模式：文件损坏 / 同步失败 / MCP 断连 的兜底分别是什么？
- [ ] 没 AI 的情况下，用户在 Obsidian 里还能读懂这个文件吗？

如果任何一条答不上来——这个功能还没准备好落地。

---

## 9. 历史与延伸阅读

- 完整推理过程：`devdocs/brainstorm/2026-04-19-cortex-architecture.md` §11（Markdown First）
- 数据模型定义：`references/data-model.md`
- 数据层协议：`references/data-layer.md`
- Cortex 整体架构决策：`devdocs/brainstorm/2026-04-19-cortex-architecture.md` §12 共识 #17

**最后更新**：2026-04-20，v1.6.2a 之后、Cortex Phase 1 设计之前。
