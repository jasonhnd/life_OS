---
translated_from: docs/user-guide/cortex/concept-graph-and-methods.md
translator_note: auto-translated 2026-04-22, 待人工校对
---

# 概念图谱 + 方法库 · 系统怎么"攒智慧"（Concept Graph & Method Library）

> 面包屑: [← Cortex 总览](./overview.md) · [← 产品入口:用户指南首页](../index.md)

> 每次 adjourn 之后,系统不只是把 session 归档——它还会扫一遍本次对话,抽出**候选概念**和**候选方法**。下次 Start Session,retrospective 会在简报里问你:"这两个候选看起来合理吗?确认、拒绝、还是编辑?"你用得越多,这些节点的**边权越强**(赫布式强化);长时间不用,按 permanence 分级慢慢衰退。这就是 Cortex 的"长期记忆"维度。

## 一句话概述

**概念图谱**(`_meta/concepts/`)是 Cortex 的神经元网络——每个 concept 是一个 `.md` 文件,**边**(synapses)直接存在 concept 自己的 YAML frontmatter 里。**方法库**(`_meta/methods/`)是"你怎么工作"的程序化记忆——可复用的多步工作流。两个目录都遵循 `tentative → confirmed → canonical` 的成熟度阶梯,archiver 自动抽候选,用户确认晋级。

---

## 为什么要加这两个

### 痛点 1: 你每次解释"这个东西是什么"

你说:"我们上次讨论过的那个 MVP 验证流程——你还记得吗?"

v1.6.2a 的系统:不记得(或者从 wiki 里翻出一条"MVP Validation"的静态条目,但**不知道它和你具体项目的关联**)。

你只能每次开头花 2 分钟复述这个流程。

### 痛点 2: 你反复重走同一个决策流程

你每次做"是否引入新合作方"的决定,都要:
1. 列需求维度(×5 次)
2. 设评分权重(×5 次,每次权重都不太一样)
3. 走一遍尽调清单(每次自己摸索一遍)
4. 事后反思"下次应该先问什么"(反思后没地方记)

第 6 次你终于说:"我是不是应该有个**固定**的合作方评估方法?"——这时 v1.6.2a 的系统没地方存这个方法,只能在某个 journal 里写成自由文本,下次用又要自己找。

### 概念图谱的承诺

Cortex 扫你每次的对话,发现"MVP 验证"这个概念反复出现 + 有多处独立证据 → 自动在 `_meta/concepts/method/mvp-validation.md` 创建一个 **tentative** 节点。下次你再聊到类似话题,hippocampus Wave 2 沿这个 concept 的强边扩散 → 把相关的历史 session 也拉出来。

**随着你用得越多,它的 activation_count +1,相关边的 weight +1**。用到第 10 次,它晋级到 **canonical**。你未来任何时候 ROUTER 在 `[COGNITIVE CONTEXT]` 里都会自动带上它。

### 方法库的承诺

同样,Cortex 扫你的对话,如果发现:
- **5+ 步**连贯的工作流
- **2+ 个独立 session** 里出现同样模式
- 你用语"approach / pattern / framework / 流れ / やり方 / 手順"

archiver Phase 2 自动写一个 **tentative method** 到 `_meta/methods/_tentative/{method_id}.md`,下次 Start Session 问你:"新检测到方法 'Iterative Document Refinement',确认吗?"

你一旦确认,**DISPATCHER 在未来每次相关决策中都会主动把这个方法的完整 body 注入六领域**——六领域不再从零重走,而是基于你已经打磨过的方法起步。

---

## 用户端看到什么

### 场景 A: adjourn 后的候选检测

你刚结束一次关于"产品文档重构"的决策。archiver Phase 2 扫对话,发现:

- "iterative-refinement" 这个概念在本次对话里激活了 3 次(Wave 1 检测)
- 对话中描述了 **5 轮升级式质量打磨**(新方法候选)

archiver 在 session 的 Completion Checklist 里记下:

```
## Cortex artefacts this session
- Concept candidates (2): iterative-refinement, quality-escalation
- Method candidate (1): Iterative Document Refinement (5-round)
- Activated concepts: [iterative-refinement, passpay-white-paper]
- Hebbian updates: 8 edges reinforced, 2 new edges
```

然后 session 正常结束,Cortex artefacts 留在 `_meta/concepts/_tentative/` 和 `_meta/methods/_tentative/` 等下次确认。

### 场景 B: 下次 Start Session 的候选确认块

你下次开 session,RETROSPECTIVE 在简报里加一块:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧬 Concept & Method Candidates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Method candidates detected (1):
  "Iterative Document Refinement"(在 2 次 session 中观察到)
  Summary: 5 轮升级式质量打磨(structure → content → precision → polish → release audit)
  (c) Confirm — 移到 confirmed,开始应用
  (r) Reject — 删除
  (e) Edit — 打开文件编辑
  (s) Skip — 下次再决定

Concept candidates (tentative, silently promoted):
  · iterative-refinement (activation 3, 边权 2)
  · quality-escalation (activation 2, 边权 1)
```

### 场景 C: 用户响应

你回:**"c"** 或 **"confirm Iterative Document Refinement"**。

系统:
- 把 `_meta/methods/_tentative/iterative-document-refinement.md` 移到 `_meta/methods/method/iterative-document-refinement.md`
- 翻转 `status: tentative → confirmed`,`confidence` 从 0.3 跳到 0.5(或 0.6 如果已有 3+ source_sessions)
- 下次 DISPATCHER 在相关主题的 dispatch 里会**自动注入**这个方法

### 场景 D: 方法被 DISPATCHER 自动应用

几天后,你开 session 问:"帮我重构这份商业白皮书。"

DISPATCHER 在 Step 4 做 method lookup,检测到 `iterative-document-refinement` 的 `applicable_when` 条件匹配("document refinement" + "多轮打磨需求")。它在 growth / execution 两个领域的 brief 里注入:

```
Known Method 'Iterative Document Refinement' applies — here is the
established approach, use it unless the subject contradicts:

[方法完整 body]
```

六领域分析时**不再重新发明流程**——它直接应用 5 轮方法、报告每轮的输出、标注"这一轮匹配 step 3 (precision pass)"。ROUTER 的奏折里会说:"基于你的既定方法,本次 refinement 的建议是……"

---

## 概念文件长什么样

每个 concept 是一个独立文件(strict: 一个 concept = 一个文件,不允许拼装),格式:

```yaml
---
concept_id: iterative-document-refinement
canonical_name: "Iterative Document Refinement"
aliases: ["5-round refinement", "升级打磨", "品質4段階"]
domain: method
status: canonical                 # tentative → confirmed → canonical
permanence: skill                 # identity / skill / fact / transient
activation_count: 14
last_activated: 2026-04-20T10:32:00+09:00
created: 2026-03-12T14:20:00+09:00
outgoing_edges:
  - to: mvp-validation
    weight: 8
    via: [cross-project-method]
    last_reinforced: 2026-04-20
  - to: passpay-white-paper
    weight: 5
    via: [applied-in-project]
    last_reinforced: 2026-04-18
provenance:
  source_sessions:
    - claude-20260312-1420
    - claude-20260321-0945
    - claude-20260412-1830
  extracted_by: archiver
decay_policy: skill               # 对应 permanence,不能错配
---

# Iterative Document Refinement

5 轮升级式质量打磨流程:
1. Structure — 骨架
2. Content — 肉
3. Precision — 术语、数据、引用
4. Polish — 语言、节奏
5. Release audit — 最后一遍法务/合规/品牌检查

## Evidence / Examples
- [[claude-20260312-1420]] 商业白皮书 v0.6
- [[claude-20260321-0945]] 技术白皮书 v0.4

## Related Concepts
- [[mvp-validation]]
- [[passpay-white-paper]]
```

**关键要点**:

- **一个概念一个文件**——不能在同一个文件里写多个 concept(anti-pattern,archiver 会拒写)
- **outgoing_edges 属于这个节点自己的 frontmatter**——不是独立的 graph 数据库。想看反向索引?`_meta/concepts/SYNAPSES-INDEX.md`(archiver 自动重建,**不要手改**)
- **activation_count 是单调递增的**——每激活一次 +1(在活跃生命周期里)
- **weight 上限 100**——防止 runaway 强化
- **permanence 和 decay_policy 必须一致**——identity 不衰退、skill 对数衰退、fact 指数衰退、transient cliff

---

## 方法文件长什么样

方法(`_meta/methods/{domain}/{method_id}.md`)是**程序化记忆**——可复用的决策工作流,和 wiki(事实性结论)并列。

```yaml
---
method_id: iterative-document-refinement
name: "Iterative Document Refinement"
description: "5 轮升级式质量打磨"
domain: method
status: canonical
confidence: 0.82
times_used: 7
last_used: 2026-04-20T10:32:00+09:00
applicable_when:
  - condition: "需要打磨文档质量到可发布级别"
    signal: "用户提到'refine / 打磨 / 推敲'且目标是外部发布"
  - condition: "多轮反馈周期允许"
    signal: "时间线 ≥ 3 天"
not_applicable_when:
  - condition: "一次性快速产出"
    signal: "用户明确说 'quick draft / 快速版本'"
source_sessions:
  - claude-20260312-1420
  - claude-20260321-0945
evidence_count: 5
challenges: 1
related_concepts:
  - iterative-refinement
  - quality-escalation
related_methods:
  - mvp-validation-methodology
---

# Iterative Document Refinement

## Summary
5 轮升级式质量打磨:每轮聚焦一个焦点,不允许跨层修改。
作用:防止"每次都在低层级纠结、高层级从未到位"的反复横跳。

## Steps
1. Structure — 只改骨架和段落顺序。不碰措辞。
2. Content — 只补内容。不碰结构。
3. Precision — 只校术语、数据、引用。
4. Polish — 只改措辞、节奏、冗余。
5. Release audit — 最后法务/合规/品牌过一遍,不再改大的。

## When to Use
- 文档将对外发布(白皮书、PR、提案)
- 多轮反馈周期允许
- 需要多角度检查(法务、技术、商业)

## When NOT to Use
- 时间紧、一次性起草
- 文档定位本身未明确(先定位再启动,不然 step 1 的骨架会反复重做)

## Evolution Log
- 2026-03-12: 首次观察到 4 轮流程
- 2026-03-21: 添加第 5 步 (release audit)
- 2026-04-20: 加入"每轮不跨层"的 anti-pattern 规则

## Warnings
- step 3 和 step 4 很容易混——严格区分:3 是事实性错误校对,4 是美感
- 跳过 step 5 常导致发布后发现品牌语调不统一
```

**关键要点**:

- 方法**从 tentative 开始**,必须用户 confirm 才能到 confirmed,canonical 自动(达到 `times_used ≥ 5 AND confidence ≥ 0.7 AND 最近 3 次无 challenge`)
- **evidence_count 是"方法用了、奏效"**,challenges 是"用了但 REVIEWER 否决或 AUDITOR 标了不匹配"
- 方法**不进 Notion 同步**——方法库是本地 `_meta/` 下的内省资产
- 方法**不能直接引用具体项目名、人名、金额**——隐私过滤器把这些从 body 里剥掉,否则"方法不是可复用的,只是一段笔记"

---

## 赫布式强化(Hebbian)

**"Neurons that fire together, wire together."** — 脑科学里的赫布法则。Cortex 的 synapse 强化规则严格对应:

### 每次 session 里:

- 如果 concept A 和 concept B **在同一个 frame 里**同时被激活 → 边 A→B 的 weight +1(上限 100)
- 新建边的话初始 weight = 1
- `last_reinforced = today`

### 每次 Adjourn 结束的 decay 通道:

按 permanence 分级:

| Permanence | Decay 形态 | 适用 |
|-----------|-----------|------|
| `identity` | **不衰退** | SOUL 核心价值、长期关系 |
| `skill` | **对数衰退**到一个底线(永远 ≠ 0) | "会写 Python"这种习得的技能 |
| `fact` | **指数衰退** | "Q2 那个项目预算是 X"这种时效性事实 |
| `transient` | **cliff 衰退**,到期清零 | 一次性的事件、临时引用 |

边权也和 concept 的 dormancy 一起衰退。`weight ≤ 0` 时,下次 Adjourn 这条边被**剪掉**。

### 晋级路径

**concept:**
| 从 → 到 | 触发 |
|---------|------|
| `tentative → confirmed` | 跨 ≥ 3 个独立 session 激活,文件从 `_tentative/` 挪到 `{domain}/` |
| `confirmed → canonical` | 用户 pin 或跨 ≥ 10 个独立 session 激活 |

**method:**
| 从 → 到 | 触发 |
|---------|------|
| `tentative → confirmed` | **用户必须 c / confirm**(**永不**自动) |
| `confirmed → canonical` | **自动**:`times_used ≥ 5 AND confidence ≥ 0.7 AND 最近 3 次无 challenge` |

### 为什么方法的晋级要求用户,而概念的不用?

- **概念**是描述性的(entity / 理念 / 模式)——系统检测到反复出现就可以自动成立
- **方法**是规定性的(你要系统**主动应用**这个流程)——不能没问过你就把它注入 DISPATCHER。所以 tentative → confirmed 永不自动

---

## 用户动作 · 你可以怎么干预

### 1. 回应候选确认块(c/r/e/s)

前面 "场景 B/C" 已展示。四种响应:

| 输入 | 行为 |
|------|------|
| `c` / "confirm X" | 移到 confirmed,开始应用 |
| `r` / "reject X" | 删除候选文件 |
| `e` / "edit X" | 打印文件路径,你手改,不触发状态迁移 |
| `s` / "skip" | 继续留在 `_tentative/`,下次 Start Session 再出现 |

连续 **5 次 Start Session 无响应** → archiver 自动 archive(沉默 ≠ 同意,但无限 pending 更糟)。

### 2. 手工新建概念/方法

你可以直接在 `_meta/concepts/{domain}/{concept_id}.md` 创建一个文件,frontmatter 填好 `status: canonical` + `permanence: identity`(或你觉得合适的)——archiver 下次跑会把它纳入图谱。

方法同理:`_meta/methods/{domain}/{method_id}.md`。

### 3. 手工 pin 到 canonical

编辑 frontmatter,改 `status: canonical`。archiver 尊重用户写入。

### 4. 撤销最近的 concept / method 自动写入

在 session 里说:

> 撤销最近的 concept

或

> 撤销最近的 method

archiver 下一次会 roll back 最近一批自动写入(和 wiki undo 同机制)。

### 5. 删除一个 concept / method

直接删除文件。下次 archiver 会重建 SYNAPSES-INDEX.md,剪掉所有悬挂边。**不要手工编辑 outgoing_edges**——archiver 会在下次 Adjourn 覆写你的改动。

### 6. 调 permanence(升级或降级)

编辑 frontmatter `permanence` 字段。注意:

- `permanence` 和 `decay_policy` 必须一致——不一致时 archiver 会在下次 AUDITOR 巡查时标红
- 升级(fact → skill)——合理的时候,比如你意识到某个东西不是一次性事实,而是真正的技能
- 降级(skill → fact)——你发现某个东西并没有你以为的那么稳定

### 7. 查看图谱健康

打开 `_meta/concepts/INDEX.md`——每次 Start Session 由 RETROSPECTIVE 编译,一行一个 concept 的 summary + status + activation + confidence。

健康信号:
- Canonical 数量稳步增长(不是一次性暴增)
- Dormant(>30 天未激活)concept 少且明确
- `_archive/` 里有被 retire 的 concept(说明 decay 机制在工作)

不健康信号:
- Canonical 数量每周暴增 5+(可能 archiver 过度抽取)
- 一个"hub" concept 有 40+ 条 outgoing_edges(可能图谱过度连接)
- `_tentative/` 里有几十个候选多次 Start Session 未清理(你一直 skip 没 confirm/reject)

---

## 常见疑问

### 我的"女朋友"能不能成为 concept?

**不能**。个人(任何具体的人)**明确禁止**成为 concept。那是 SOUL 的领地(SOUL 里可以有"和伴侣的关系"这种 **dimension**,但 dimension 不是 concept)。

`relationship/` 这个 domain 在 concepts 下**保留给组织和非个人关系实体**——比如"创投圈子"、"某集团"、"日本 NPO 圈"。

这个规则在 archiver Phase 2 的隐私过滤器里硬编码,对"人名类"的 concept 候选直接丢弃。

### 我手工改 outgoing_edges 会怎样?

下次 Adjourn 被 archiver 覆写。**archiver 拥有 edge 的写权限,用户不拥有**。

想要断开连接,正确的做法:
- 删除其中一个 concept 文件
- 或让那两个 concept 长时间不 co-activate(边权会自然衰退到 0 被剪掉)

### concept 的 edge weight 为什么上限 100?

防止 runaway 强化。假设一对 concept 每天同时激活,30 天 weight 就 ≥ 30,一年 ≥ 300——没有上限的话,这条边会"垄断"hippocampus Wave 2 的所有扩散预算,其他邻居全被压下来。100 是一个经验值,在 "有区分度"和 "不至于垄断"之间平衡。

### 方法可以组合吗?比如"先用方法 A 再用方法 B"?

v1.7 **仅支持软组合**——方法文件里的 `related_methods` 字段可以指向其他 method ID,DISPATCHER 匹配到多个 method 时会都注入并标注"多种方法可用,domain 自行判断适用性"。

**硬组合**(自动把 A → B 链式执行)**v1.7 out-of-scope**。想象一下: archiver 无法确保"方法 A 的输出"和"方法 B 的输入"在本次 session 里结构兼容——这个链式保证需要一个单独的执行框架,不是 v1.7 要做的事。

### 方法会和 Wiki 冲突吗?

不会——它们答的是不同问题:

| | Wiki | Method |
|---|------|--------|
| 回答 | "世界是什么样的?" | "你怎么工作最好?" |
| 例子 | "日本 NPO 不享受贷金业法豁免" | "5 轮打磨:结构 → 内容 → 精度 → 打磨 → 发布审计" |
| 形状 | **declarative**(事实陈述) | **sequential**(步骤序列) |

archiver Phase 2 有专门的 **routing decision tree**(详见 `references/cortex-spec.md` §Archiver Candidate Routing),按顺序判断:SOUL → user-patterns → method → concept → wiki → discard。一个候选**只能进入一个主 destination layer**,不能双写。

歧义场景(比如一段"最佳实践"读起来既像方法又像事实):
- 如果描述的是**用户的一连串动作** → method
- 如果描述的是**世界的属性** → wiki
- 确实模糊时,**默认 wiki**(方法需要更强证据:5+ 步 + 跨 2+ session 回响)

### Concept dormant 后会发生什么?

**超过 30 天未激活** → RETROSPECTIVE 在 Start Session 简报里 flag 为 dormant(💤)。

**canonical 概念的 activation_count 因长期 dormancy 被降到 0** → 归档到 `_meta/concepts/_archive/{domain}/{concept_id}.md`。归档后:
- git 历史里仍在(无数据丢失)
- hippocampus 在激活时**忽略** `_archive/` 下的 concept
- AUDITOR 在巡查时仍能看到

**完全删除**永远需要你手动——最强的自动动作就是归档。

### 方法也会归档吗?

会,但 timeline 更长:

| 距 last_used | 状态 | 动作 |
|------------|------|------|
| ≤ 6 个月 | Active | 无动作 |
| 6–12 个月 | Dormant | RETROSPECTIVE 在简报 flag "方法 'X' 已 N 个月未用" |
| ≥ 12 个月 | Archived | archiver 自动挪到 `_meta/methods/_archive/` |
| Archived + 用户删除 | Retired | 文件删除,即使模式再现也不会自动重建 |

**方法是挣来的——归档是系统对它最强的自动动作。最终删除永远归用户**。

---

## Troubleshooting

### "系统一直检测不出我明显在用的一个方法"

三个常见原因:

1. **跨 session 回响不够**——方法候选的 anti-heuristic 明确排除"只在一个 session 出现过的模式"。解决: 等 2–3 次 session 自然累积;或手工创建 method 文件。
2. **描述语言太碎**——如果你每次描述这个流程用完全不同的词(有时叫"5 轮",有时叫"迭代",有时叫"逐步打磨"),archiver 可能认为是三个独立模式。解决: 语言尽量一致,或手工 alias。
3. **模式小于 5 步**——heuristic 要求至少 5 个 sequential actions。4 步以内不会被抽成 method。解决: 如果真的只有 3-4 步,它可能更合适作为 wiki 的一条"best practice",或者作为 concept。

### "候选方法一直沉在 `_tentative/`,我忘了确认"

5 次连续 Start Session 无响应 → 自动 archive 到 `_meta/methods/_archive/`。**不会丢失**,但也不会自动再弹回确认队列。

恢复流程:
```bash
mv _meta/methods/_archive/{method_id}.md _meta/methods/_tentative/{method_id}.md
```
下次 Start Session 会重新出现在确认块里。

### "一个 concept 突然边权暴涨,几乎所有检索都围着它转"

Hub 问题。诊断:

```bash
# 查某个 concept 的 outgoing_edges 数量
grep -c '^  - to:' _meta/concepts/method/{concept_id}.md
```

超过 20 条 outgoing edges 就是 hub 征兆。处理:

1. **拆分**——这个 concept 可能其实是两三个概念被误合并。删掉原文件,手工建几个更细的 concept,让 archiver 在下次 session 自己重连。
2. **升级 permanence**——如果它就是核心且边就该多(比如"user-core-workflow"这种元方法),把 `permanence` 升到 `identity`,不再衰退。
3. **重启 migration**——极端情况,`uv run tools/migrate.py` 重扫。幂等,不会重复。

### "AUDITOR 巡查标红了'孤立边'"

Orphan edge = `outgoing_edges` 里的 `to:` 指向了一个不存在的 concept 文件(可能你手动删掉了目标 concept 但没同步更新源 concept)。

**正常情况下** archiver Phase 2 会在 SYNAPSES-INDEX 重建时自动剪掉这些边。如果 AUDITOR 还在 flag,说明 archiver 没跑到这一步——检查 adjourn_completeness 分数(详见 [auditor-eval-history.md](./auditor-eval-history.md))。

---

## 深入阅读

产品入口:

- [What is Life OS](../../getting-started/what-is-life-os.md) — Life OS 整体定位
- [Quickstart](../../getting-started/quickstart.md) — 首次上朝流程

同目录用户文档:

- [overview.md](./overview.md) — Cortex 总览
- [hippocampus-recall.md](./hippocampus-recall.md) — Wave 2/3 沿这里的边权扩散
- [gwt-arbitration.md](./gwt-arbitration.md) — concept 信号如何参与 salience 竞争
- [narrator-citations.md](./narrator-citations.md) — 奏折如何引用 concept(`C:domain:concept_id` 前缀)
- [auditor-eval-history.md](./auditor-eval-history.md) — archiver Phase 2 的质量监控

Spec 层(英文):

- `references/concept-spec.md` — schema、Hebbian 算法、spreading activation 规则
- `references/method-library-spec.md` — 方法 schema、promotion ladder、DISPATCHER 集成
- `references/cortex-spec.md` §Archiver Candidate Routing — 候选进哪个 layer 的决策树
- `references/hippocampus-spec.md` §Wave 2/3 — 怎么沿边权扩散
- `pro/agents/archiver.md` — Phase 2 实际的写入流程

---

**上一篇**: [hippocampus-recall.md — 跨 session 记忆检索](./hippocampus-recall.md)
**下一篇**: [narrator-citations.md — Narrator 引用与 trace](./narrator-citations.md)
