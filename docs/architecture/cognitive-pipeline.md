---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# 7 阶段认知管线

Life OS 的数据流从「感知」到「涌现」经过 7 个阶段, 每阶段对应一种方法论、一个 storage 位置、一个 agent。

源: `references/data-layer.md` 之 "Cognitive Pipeline" 章节。

---

## 全图

```
Perceive → Capture → Judge → Settle → Associate → Strategize → Emerge
   ↑         ↑        ↑      ↓   ↘        ↑           ↑           ↑
 Phone      GTD      3D6M  SOUL  Wiki   ROUTER+Wiki  Strategic   DREAM REM
 Experience  inbox/  Desktop (人)(知识)   INDEX匹配   MAP         跨域连接
```

7 个阶段对应的方法论:

| 阶段 | 方法论 | 主要载体 |
|-----|-------|---------|
| Perceive | 现象学 | 手机/传感器 |
| Capture | GTD (Getting Things Done) | inbox/ |
| Judge | 三省六部 (Draft-Review-Execute) | 决策流程 |
| Settle | SOUL (人) + Wiki (世界) | SOUL.md + wiki/ |
| Associate | ROUTER 读 Wiki INDEX | wiki/INDEX.md |
| Strategize | Strategic Map | _meta/STRATEGIC-MAP.md |
| Emerge | DREAM REM | dream journal |

---

## Stage 1: Perceive (感知)

**做什么**: 用户在日常生活中产生原始观察、想法、情绪信号。

**载体**: 用户自己(大脑)+ 手机 AI 实时捕捉 (通过 Notion 移动端 / Apple Shortcuts / macOS 语音备忘录等**已有工具**, 不搭建独立 bot / agent)。

**这不是系统的一部分**, 但系统依赖它。用户如果没把观察说出来或写下来, 系统无法工作。

---

## Stage 2: Capture (捕获)

**方法论**: GTD 的 "Collection basket"。

**做什么**: 零摩擦把原始想法扔进 inbox。不分类、不判断、不决定。

**载体**: `inbox/` 目录 (每个用户的二脑都有一个)。

**通道**:
- 桌面端: 用户直接说话, 系统写入 inbox
- 手机端: 通过 Notion inbox (Notion 移动端 / Apple Shortcuts 写入, 桌面端 RETROSPECTIVE 从 Notion pull)

**不需要**: 结构、层级、标签。这阶段的核心是**降低捕获成本**, 让想法不会在分类决策前就消失。

**谁执行**: 手机端用户 / 手机 AI 直接写 Notion inbox。桌面端 RETROSPECTIVE 在 start session 时 pull。

---

## Stage 3: Judge (判断)

**方法论**: Draft-Review-Execute 的三省六部制 (规划 → 审议 → 执行)。

**做什么**: 不是所有 inbox 的内容都需要决策。只有涉及**主要资源分配、多选权衡、不可逆结果**时, 才启动完整决策流程。

**条件**: ROUTER 分诊时识别出来:
- 直接回 → 不进 Judge 阶段 (Stage 2 就结束了)
- Express → 轻量 Judge (无评分无审计, 只做专业分析)
- 完整决策 → 全链路 Judge (PLANNER → REVIEWER → DISPATCHER → 六部 → REVIEWER 终审 → Summary Report → AUDITOR → ADVISOR)

**载体**: 决策过程在对话里, 产出落盘在:
- `projects/{project}/decisions/{YYYYMMDD-slug}.md`
- `projects/{project}/tasks/`
- `_meta/journal/`

**谁执行**: 所有 13 个 agent (除 retrospective/archiver/strategist) 都参与 Judge 阶段。

---

## Stage 4: Settle (沉淀)

**方法论**: SOUL (关于人) + Wiki (关于世界)。

**做什么**: 决策的结论沉淀到两个 pool:
- **SOUL** (关于用户本人): values / personality / behavioral patterns
- **Wiki** (关于世界): 可复用知识 / 已确立结论

**触发时机**: ARCHIVER 在 Phase 2 和 DREAM 的 N3 / REM 阶段做 auto-write。

**载体**:
- `SOUL.md` — 单文件, 人格档案
- `wiki/{domain}/{topic}.md` — 按领域分类的知识点
- `user-patterns.md` — 行为模式 (ADVISOR 维护)

**Auto-write 门槛**:
- Wiki: 6 criteria + 隐私过滤 (见 `docs/architecture/hard-rules-catalog.md` WK1)
- SOUL: ≥2 决策作为证据, 初始 confidence 0.3, What SHOULD BE 留空

**用户事后纠正**: 删掉不认同的文件, 或说「undo recent wiki」回滚最近的 auto-write。不需要事前确认。

**SOUL Snapshot**: archiver 在每次 session 结束时 dump 一份 SOUL 状态快照到 `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md`, 用于 RETROSPECTIVE 下次 start 时算 trend delta。

---

## Stage 5: Associate (关联)

**方法论**: ROUTER 读 wiki INDEX 做匹配。

**做什么**: 新请求到达时, 把**已有知识**和**当前话题**匹配起来。让沉淀的知识变成活的 context。

**触发时机**: ROUTER 在分诊时扫描 `wiki/INDEX.md`, 如果当前话题领域有 confidence ≥ 0.7 的高置信条目, 告知用户「这个领域已有 N 条已确立知识, 要从已知结论出发还是从头研究?」

**如果用户选「从已知结论出发」**: DISPATCHER 把相关 wiki 条目的全文作为「已知前提」注入领域 subagent 的 context。

**载体**: `wiki/INDEX.md` (每次 start session 时 RETROSPECTIVE 自动编译)。

**价值**: 让系统不用每次决策都重新推导基本事实。省 token, 更重要的是**积累复利**: 沉淀越多, 后续决策越快。

---

## Stage 6: Strategize (战略化)

**方法论**: Strategic Map — 让个体决策跟更大的战略线对齐。

**做什么**: 当请求涉及有战略关系的项目时, 系统自动浮现:
- 下游依赖
- 瓶颈状态
- 决策传播警告

把「单项目分析」升级为「战略线感知分析」。

**触发时机**:
1. 用户定义 `_meta/strategic-lines.md` (几条战略线的 driving_force, deadline, health_signals)
2. 在各项目 `projects/{project}/index.md` 的 frontmatter 里加 `strategic:` 字段 (role, flows_to, flows_from)
3. RETROSPECTIVE 在每次 start session 编译 `_meta/STRATEGIC-MAP.md`
4. ROUTER / PLANNER / REVIEWER 读这份编译产物

**载体**:
- `_meta/strategic-lines.md` (用户手写, 几条线定义)
- `projects/*/index.md` 的 `strategic:` frontmatter (每项目的关系定义)
- `_meta/STRATEGIC-MAP.md` (编译产物)

**跨层验证**: RETROSPECTIVE 在编译时做:
- SOUL × 战略: driving_force 和 SOUL 维度一致吗?
- wiki × flows: cognition flow 的领域有 wiki 条目吗?
- user-patterns × 角色: 行为模式和战略优先级匹配吗?

---

## Stage 7: Emerge (涌现)

**方法论**: DREAM REM — 基于全部沉淀的知识做跨域连接。

**做什么**: 当 wiki 条目和战略关系积累到一定程度, DREAM 的 REM 阶段能发现**用户自己都没意识到**的跨域连接。

**触发时机**: ARCHIVER 的 Phase 3 DREAM。

**REM 做的事**:
- 用 flow graph 作为脚手架
- 检查 SOUL × strategy 对齐
- 检查 wiki × flow 完整性
- 检查 behavioral patterns × 战略优先级一致性
- 10 个 auto-trigger 检测 (new project relationship / behavior-driving_force mismatch / wiki contradiction / SOUL dormancy / cognition unused / decision fatigue / value drift / stale commitments / emotional decisions / repeated decisions)

**价值**: 系统不只是「帮用户做决策」, 而是**主动发现用户的盲区**。用户越用系统, 它越能发现用户自己看不到的模式。

**载体**:
- `_meta/journal/{date}-dream.md` — DREAM 报告
- `triggered_actions` YAML 块 — auto-trigger 的记录
- 下次 start session 时 RETROSPECTIVE 在 "💤 DREAM Auto-Triggers" 块里展示

---

## 移动端 vs 桌面端分工

这是 Life OS 的一个核心设计决定: **不同设备做不同阶段的事**。

### 移动端

**做**: Perceive → Capture (+ 偶尔轻量 Associate 如网页搜索)。

**不做**: Judge / Settle / Emerge 的任何重活。

**为什么**:
- 手机屏幕小, 不适合长对话
- 移动场景碎片化, 不适合做需要全局 context 的决策
- 移动 AI 算力和 context window 都有限
- 最重要: **降低捕获摩擦**。如果每次都要想「这是不是决策」, 用户会放弃捕获

**技术**: Notion 移动端 / Apple Shortcuts / 语音备忘录 → Notion inbox。桌面端 RETROSPECTIVE 在 start session 时 pull。**不做**: 独立 bot (Telegram / Discord 等) / 常驻 agent。Life OS 是本地 Claude Code 内的决策引擎, 移动端只做"捕捉", 通过用户已有工具即可。

---

### 桌面端

**做**: Associate → Judge → Settle → Strategize → Emerge。全部重活。

**为什么**:
- 屏幕大, 能显示完整的 6 部报告和 Summary Report
- session 时长友好 (十几分钟到一小时的深度决策)
- 完整 MCP 工具链, 读写二脑、git、Notion sync 都在这里
- 需要调用多个 subagent 并行, 需要强模型 + 长 context window

---

## 数据流的方向性

```
  Perceive (用户/世界)
       ↓ write-only
     inbox/
       ↓ RETROSPECTIVE pulls at start
  ROUTER 分诊
       ↓ 有决策需求
  Judge (13 agents 参与)
       ↓ archiver 写
 outbox/{session_id}/
       ↓ 下次 start 合并
  projects/ + areas/ + wiki/ + SOUL.md
       ↓ 下次 ROUTER 读 INDEX
  Associate + Strategize
       ↓ 累积 → DREAM REM
  Emerge (跨域洞察)
       ↓ 写 dream journal
  下次 start briefing 展示
       ↓ 用户感知 → 调整行为
  Perceive (循环)
```

**数据不是单向的, 是闭环的**。Emerge 阶段的洞察会反过来影响用户的 Perceive, 于是下次 Capture 的内容会不一样, 于是 Judge 的输入不一样, 于是 Settle 的沉淀不一样。系统和用户共同演化。

---

## 各阶段映射到 agent 和 storage

| 阶段 | 主要 agent | Storage 读 | Storage 写 |
|-----|-----------|-----------|-----------|
| Perceive | — (用户) | — | — |
| Capture | (mobile app) | — | inbox/ |
| Judge | ROUTER / PLANNER / REVIEWER / DISPATCHER / 六部 / AUDITOR / ADVISOR | inbox/, projects/, areas/, SOUL.md, wiki/INDEX.md, STRATEGIC-MAP.md | outbox/{session_id}/ |
| Settle | ARCHIVER (Phase 2) | 会话材料 | outbox/{id}/wiki/, outbox/{id}/soul/ |
| Associate | ROUTER + DISPATCHER | wiki/INDEX.md | — |
| Strategize | RETROSPECTIVE + ROUTER + PLANNER + REVIEWER | strategic-lines.md, projects/*/index.md | STRATEGIC-MAP.md (编译) |
| Emerge | ARCHIVER Phase 3 (DREAM) | 最近 3 天变更 + 全部状态文件 | journal/*-dream.md |

---

## 为什么 7 阶段不是任意划分

每个阶段对应一类**认知行为**, 它们在时间上有依赖关系:

1. 不 Perceive 就不能 Capture (没有原始信号)
2. 不 Capture 就不能 Judge (没有输入材料)
3. 不 Judge 就不能 Settle (没有值得沉淀的结论)
4. 不 Settle 就不能 Associate (wiki/SOUL 是空的, 无可关联)
5. 不 Associate 就不能 Strategize (只看得到当前, 看不到全局)
6. 不 Strategize 就不能 Emerge (没有战略脚手架, REM 找不到规律)

系统能做的事取决于它「走到了哪个阶段」。新用户的系统只能做 Capture+Judge, 用半年后才开始出现真正的 Strategize, 用一年以上才出现有价值的 Emerge。**这是设计出来的, 不是 bug**。

早期用户不要期待系统能做战略化洞察 — 它还没有足够的沉淀。
