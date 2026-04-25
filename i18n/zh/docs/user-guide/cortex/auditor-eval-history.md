---
translated_from: docs/user-guide/cortex/auditor-eval-history.md
translator_note: auto-translated 2026-04-22, 待人工校对
---

# AUDITOR Eval-History · 系统的自反馈循环（AUDITOR Eval-History）

> 面包屑: [← Cortex 总览](./overview.md) · [← 产品入口:用户指南首页](../index.md)

> Life OS 没法微调背后的 Claude 模型,但它可以**微调自己的规则**。AUDITOR 在每次 session 结束时给自己打 10 维度的分,把结果写到 `_meta/eval-history/{date}-{project}.md`。下次 Start Session,RETROSPECTIVE 扫最近 10 份,检测系统性模式——连续 3 次 adjourn 不完整?narrator 引用失败率 >20%?这些会以"系统性问题检测"块出现在简报里。你不仅是系统的用户,也是调优这些规则的人。

## 一句话概述

Eval-history 是 Life OS 的**结构化自评反馈环**。AUDITOR 写,RETROSPECTIVE 读,你看到摘要。它是 Hermes RL 训练环路的 spec 层等价物——不做模型微调,但把"质量信号写到磁盘 → 下次 session 暴露给人类"。信号通过人的注意力改变系统行为,不是通过 gradient descent。

---

## 为什么要加这一层

### 被 Hermes 启发的一课

[Hermes Lesson 5](../../../../devdocs/research/2026-04-19-hermes-analysis.md) 的核心: **自评必须回流到系统,不能只是一次性报告**。

v1.6.2a 的 AUDITOR 已经在每次决策结束时给各 agent 打分——**PLANNER 维度全不全?REVIEWER 封驳有没有依据?domain 分数和分析一致吗?**——但这些评分**只存在本次 session 的 Summary Report 里**。session 结束,它们蒸发。

**下一次 session 的 AUDITOR 不知道上次 AUDITOR 发现了什么**。模式性质量问题(比如 archiver 最近 3 次都没完整跑 4 阶段)完全看不出来——每次 session 都当作孤立事件审。

### v1.7 的闭环

Eval-history 把 AUDITOR 的评分**持久化到 `_meta/eval-history/`**——每份 session 一个 `.md` 文件,YAML frontmatter 有 10 维度分数,body 有优点 / 缺点 / 推荐。

**关键二阶机制**: RETROSPECTIVE Mode 0 在每次 Start Session 读**最近 10 份**,用**5 条检测规则**找系统性模式。检测到的警告直接出现在简报里:

```
⚠️ 系统性问题检测:
- 退朝完整度连续 3 次 ≤6 → 建议检查 archiver subagent 启动
- Wiki 萃取质量从 4/15 起下降 → 建议本次重点关注
- Narrator 引用失败率 25% (阈值 20%) → narrator 层可能在幻觉信号
```

**这是用人类注意力做的"强化学习"**。模型不变,但**你**每次上朝看到这些警告,你会开始改配置 / 改 spec / 改 skill——系统通过你在演化。

---

## 用户端看到什么

### 场景 A: 正常 session 结束

你刚做完一个全朝议决策。session 走到 Step 8 AUDITOR。

AUDITOR 做本次评估的同时,**写入**一个 `_meta/eval-history/2026-04-20-passpay.md`(文件名格式:`{YYYY-MM-DD}-{project}.md`,多次同日同项目追加 `-{HHMM}`)。

你直接看不到这份文件——但你可以任何时候打开它。内容结构:

```yaml
---
eval_id: 2026-04-20-1432-passpay
session_id: claude-20260420-1432
evaluator: auditor
evaluation_mode: decision-review
date: 2026-04-20T14:32:00+09:00
scores:
  information_isolation: 9
  veto_substantiveness: 8
  score_honesty: 7
  action_specificity: 9
  process_compliance: 10
  adjourn_completeness: 10
  soul_reference_quality: 8
  wiki_extraction_quality: 6
  cognitive_annotation_quality: 7
  citation_groundedness: 9
violations:
  - type: soul_dimension_ignored
    agent: REVIEWER
    severity: medium
    detail: "REVIEWER 未引用 dormant 维度 '财务独立' 虽然决策直接相关"
agent_quality_notes:
  PLANNER: "维度拆分完整。SOUL 参考到位。"
  REVIEWER: "封驳 1 次合理。但忽略 dormant 维度。"
  FINANCE: "分析和分数对齐。"
  ...
---

## Summary
全朝议走完。information isolation 维持得很好。主要问题是 REVIEWER 漏
了一条 dormant SOUL 维度,本次决策直接涉及财务独立话题。

## Strengths
- Information isolation 9/10: PLANNER 没引用 ROUTER reasoning,domains 之间无交叉污染
- Process compliance 10/10: 11 步全走完,无违规跳转
- Adjourn completeness 10/10: archiver 4 phase 全跑,Notion 同步执行

## Weaknesses
- soul_reference_quality 8/10: REVIEWER 漏 dormant 维度(具体见 violations)
- wiki_extraction_quality 6/10: 本次 wiki 候选和已有条目重叠度高,未新增可复用
  结论

## Systemic Pattern Observations
连续第 2 次 REVIEWER 漏引 dormant 维度(上次是 2026-04-17 passpay session)。
如果下次仍漏,建议调整 reviewer.md 显式要求 "审查 dormant 维度的相关性"。

## Recommendations
- REVIEWER: 在 checklist 里加一项 "本次决策是否涉及 dormant 维度的领域?"
- ARCHIVER: wiki 候选去重逻辑需要审,目前似乎允许和 canonical 重叠的新写入
```

**所有分数都是 0–10 整数**——半分不允许,强迫 AUDITOR 做 commitment。

### 场景 B: 下次 Start Session 检测到系统性问题

你第二天早上开新 session。RETROSPECTIVE Mode 0 扫最近 10 份 eval-history,检测到:

- `adjourn_completeness` 最近 3 次分别是 5, 4, 6(连续 3 次 ≤6)
- `soul_reference_quality` 在 2 次 session 都丢了 dormant 维度
- `citation_groundedness` 在最近 10 次里有 3 次 <8

简报里出现:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Systemic Issue Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- 退朝完整度连续 3 次 ≤6 → archiver subagent 可能未完整启动
  (上次值 5, 4, 6 vs 期望 ≥8)
  建议: 检查 archiver agent 定义是否被 ROUTER 分段调用,修复成端到端单次
  invocation

- REVIEWER 连续 2 次漏引 dormant SOUL 维度
  建议: 本次 session 开始前手工 review `SOUL.md` 里的 dormant 维度,或调
  整 reviewer.md

- Narrator 引用失败率 25% (阈值 20%) → 最近 10 session 里 3 次
  citation_groundedness <7
  建议: 本次 session 重点关注奏折中带 [S:] [C:] 引用的 claim,用 trace 验证

(如果要查具体哪些 session,看 _meta/eval-history/)
```

**这个块直接位于 DREAM Auto-Triggers 下方,Strategic Overview 之前**——固定位置,强制可见。没有系统性问题时,整块**省略**(不显示占位符)。

### 场景 C: 主动查特定维度

你想知道"最近 adjourn_completeness 的趋势":

```bash
grep -h "adjourn_completeness" _meta/eval-history/*.md | tail -10
```

结果:

```
  adjourn_completeness: 10
  adjourn_completeness: 9
  adjourn_completeness: 5
  adjourn_completeness: 4
  adjourn_completeness: 6
  adjourn_completeness: 10
  ...
```

三连低分的问题可以清楚看到——从哪天开始、到哪天修复、修复前后有什么变化。

---

## 10 个打分维度

### v1.6.2a 继承的 8 个

| # | 维度 | 衡量什么 |
|---|------|---------|
| 1 | `information_isolation` | 上游 context 泄漏没发生?PLANNER 看见 ROUTER reasoning 了吗? |
| 2 | `veto_substantiveness` | REVIEWER 的封驳是基于 8 项 checklist 的实证,还是 rubber-stamp? |
| 3 | `score_honesty` | domain 分数和自己的分析文本一致吗? |
| 4 | `action_specificity` | action item 有 owner / deadline / 具体动作吗? |
| 5 | `process_compliance` | 状态机是不是端到端走完?有跳步吗? |
| 6 | `adjourn_completeness` | archiver 4 phase 全跑完了?Completion Checklist 不是 TBD? |
| 7 | `soul_reference_quality` | REVIEWER 引的 SOUL 维度是否完整(包含 dormant + conflict)? |
| 8 | `wiki_extraction_quality` | wiki 候选可复用、privacy 干净、domain 正确? |

### v1.7 新增 2 个

| # | 维度 | 衡量什么 |
|---|------|---------|
| 9 | `cognitive_annotation_quality` | hippocampus 检索的 session 和 concept 真的在决策中被用到了吗?相关度评分和实际影响一致? |
| 10 | `citation_groundedness` | narrator 引用是否指向真实存在 + 内容支持 claim 的 artifact? |

每个维度都有**三个锚点**(0 / 5 / 10),给 AUDITOR 具体示例参考。比如 `information_isolation`:

- **10**: PLANNER 无 ROUTER reasoning 意识。REVIEWER 只收规划文档。无交叉污染。
- **5**: 轻度泄漏——ROUTER 暗示了哪些 domain 会被触发,或一个 domain 提到"前述评审说过"。
- **0**: 明显 cross-contamination。REVIEWER 看到 PLANNER 的 raw 思考,或两个 domain 互相点名。

---

## 系统性问题检测 · 5 条规则

RETROSPECTIVE Mode 0 扫最近 10 份 eval-history,应用:

### 规则 1 · adjourn_completeness 连续低分

**3+ 次连续 session `adjourn_completeness < 6`** → 警告: "archiver subagent 可能未完整启动"

这是典型的 v1.6.x bug——ROUTER 在 ARCHIVER 各 phase 之间插嘴,产生 split flow。重复 3 次就是结构性问题,不是偶发。

### 规则 2 · wiki_extraction_quality 下降趋势

**5+ 次连续 session `wiki_extraction_quality` 呈下降趋势** → 警告: "ARCHIVER Phase 2 可能正在悄悄 skip extraction"

下降趋势比"低分"更重要——从 9 跌到 5 说明某个东西变了,即使 5 还不算低。

### 规则 3 · citation_groundedness 高失败率

**最近 10 session,citation resolution 失败 >20%** → 警告: "narrator 层正在幻觉信号"

这是 narrator 最危险的失效模式——引用指向不存在的 artifact。详见 [narrator-citations.md](./narrator-citations.md)。

### 规则 4 · cognitive_annotation_quality 持续低

**5+ 次连续 session `cognitive_annotation_quality < 5`** → 警告: "hippocampus 检索需要调优"

可能是 INDEX.md 过时、Wave 1 prompt 失准、或 concept graph 过度稀疏。

### 规则 5 · process_compliance 重复违规

**相同 `violations[].type` 在最近 30 天内出现 3+ 次** → **升级到 user-patterns.md**

这是最有 teeth 的规则: 同一类违规(比如"adjourn_phase_skip")反复出现,从 eval-history "毕业"成一条 `user-patterns.md` 里的 tracked behavioral pattern。下次 session 的 **ADVISOR** 会把它直接 surface 为观察:

> "观察: 最近一个月你有 4 次 session 在 adjourn 之前插入操作——这会把 archiver phase 打断。本次要不要先跑完 adjourn 再操作?"

系统自己变了——从 eval-history 的静默评分,变成 ADVISOR 的主动提醒。

### 检测到问题 ≠ 自动修复

**AUDITOR 永远不会自动关闭某个模块或改某个 spec**。用户决策 #4: **没有预设的 kill criteria**。规则 1–4 的警告都是 advisory——**你**决定要不要改 reviewer.md、要不要调 cortex config、要不要手工清理 eval-history 里的误判。

---

## 写入时机与条件

### AUDITOR 写 eval-history 的时机

- **全朝议 Step 8** 结束时(端到端决策完成)
- **Express 快车道**如果产生了足够深度的 Brief Report(不是每次 Express 都写——浅层查询没得评)
- **Patrol Inspection** 触发时(RETROSPECTIVE Mode 0 检测到 `lint-state.md >4h`,会启动巡检,写入时用 `evaluation_mode: patrol-inspection`)

### AUDITOR 不写的场景

- **ROUTER direct-handle**(闲聊、翻译、简单查询——无 subagent 工作可评)
- **STRATEGIST session**(不同的评估领域——思想家对话质量而非决策质量)
- **首次 session / second-brain 为空**(没有决策发生)
- **session 在 PLANNER 产出前 abort**(无内容可评)

### 写入失败的容错

如果 eval-history 写失败(磁盘满、权限错误、路径缺失):

- AUDITOR 在 Decision Review 里报告失败
- **session 继续跑**——不 block ADVISOR 或 ARCHIVER
- 失败本身会作为下次 session 的 `process_compliance violation` 记录

---

## Immutability · 永不编辑

**Eval 文件创建后绝不编辑**。如果你发现某次评价错了:

- **不改**原文件
- **下次 session** 由 AUDITOR 写一份新的 eval 文件,包含反驳说明
- 原文件作为历史记录**保留**

这是严肃的——因为如果可以编辑历史评价,RETROSPECTIVE 的系统性检测就不可信了。AUDITOR 的自审是 append-only,像区块链一样(逻辑上)。

---

## 存储与归档

| 特性 | 细节 |
|-----|------|
| **单文件大小** | ~5KB |
| **1000 个 session 总占用** | ~5MB |
| **保留策略** | **永久保留**,不自动删除 |
| **归档触发** | 文件 >6 个月 + 显式 `tools/stats.py --compress-old` |
| **归档目标** | `_meta/eval-history/_digest/{YYYY-Q}.md`(季度摘要),原文件 → `_meta/eval-history/_archive/` |
| **digest 内容** | 头条分数 + 系统性模式,个别 session 仍可访问 |
| **Notion 同步** | **不同步**(用户决策 #12——本地内省资产,pushing 到 Notion 让 mobile view 噪声大而无消费者) |

---

## 用户动作 · 你可以怎么做

### 1. 查最近的趋势

```bash
ls -t _meta/eval-history/*.md | head -10
```

打开一份,看 frontmatter 的 scores 块,对比自己的预期。

### 2. 查特定维度的趋势

```bash
# 最近 10 份里 cognitive_annotation_quality 的值
grep -h "cognitive_annotation_quality" _meta/eval-history/*.md | tail -10

# 最近 10 份里所有 violations
grep -A 3 "violations:" _meta/eval-history/*.md | tail -40
```

### 3. 用 tools/stats.py 做月报

```bash
uv run tools/stats.py --month 2026-04
```

输出该月的 score 分布、系统性模式、violation 类型统计。

### 4. 用 tools/reconcile.py 查孤儿

```bash
uv run tools/reconcile.py
```

检测:
- 有 session 但无 eval
- 有 eval 但 session_id 指向不存在文件
- YAML schema 字段缺失
- violations 里 agent 名不在已知列表内

### 5. 响应系统性问题警告

简报里看到系统性问题,你可以:

- **本次 session 针对性关注**——警告已经说了"本次重点关注 X",跟着做
- **改 agent spec**——比如系统说 REVIEWER 反复漏 dormant 维度,就编辑 `pro/agents/reviewer.md` 加一项 checklist
- **改 cortex config**——比如系统说 hippocampus retrieval 质量低,`_meta/config.md` 里考虑调整 `top_k_signals` 或 `per_signal_floor`
- **手工反驳**——如果你不认同系统性模式检测(比如 narrator 失败率高但你觉得是暂时问题不是系统性的),在当前 session 里说"我认为这个检测是误报",AUDITOR 会记一笔,后续 pattern 仍会持续监控但降权

### 6. 清理被 pattern 升级到 user-patterns.md 的 behavior

如果某个 behavior 被升级了但你不认同,打开 `user-patterns.md` 直接删除那条记录。user-patterns 是**你拥有的文件**,AUDITOR / ADVISOR 只会读,不会强制保留。

---

## 什么时候该改 skill 配置

这是用户最常问的问题:**看到 eval-history 里什么数据时,我就该动手改配置?**

### 红色信号(立即行动)

- **同一 `violations[].type` 在 30 天内出现 3+ 次** → 已被规则 5 升级到 user-patterns.md。**这是系统已经表态"这是一个稳定模式"** → 改对应 agent spec
- **`process_compliance` 连续 3 次 <5** → 状态机在崩。优先级最高,其他都可以等,这个不能
- **`citation_groundedness` 单次 <5** + trace 验证确实是 narrator 编造 → 编辑 `pro/agents/narrator-validator.md` 加更严的检查,或考虑是否 registry 本身有漏

### 黄色信号(观察 + 预备)

- **某维度 2 次接近低分但没到阈值**——先观察第 3 次。如果是连续性问题,AUDITOR 会触发警告
- **新引入的 agent 定义首次上线后,分数明显低于该 agent 历史**——说明新版 spec 有回归,review diff 找原因
- **RETROSPECTIVE 给出系统性警告但你觉得是偶然**——先让 AUDITOR 继续观察 1 周。7 天数据后趋势明朗

### 绿色信号(稳态)

- 所有维度 ≥7
- 无系统性警告
- violations 数 ≤1 per session

这是你期望的常态。如果已经长期绿色,但你想**主动优化**(比如从 8 分拉到 10 分),风险要更谨慎——"已经工作的东西少改"。

---

## 常见疑问

### 为什么整数 0–10,不是小数?

强迫 AUDITOR 做 commitment。**半分是逃避**——"我觉得这个是 7.5" 实际上是"我两边都不想得罪"。10 档整数让 AUDITOR 必须选一边。

长期看,**10 档够精细**——在 3 个月内你看一个维度的走势,从 8 降到 7 再降到 6 是清晰的信号,不需要 8.5 降到 7.5 这种级别。

### AUDITOR 给自己打 10 分的话怎么办(自我夸奖)?

Eval-history 的 anti-patterns 里明确写:

> **Do not** allow face-saving in AUDITOR's own evaluation. If `score_honesty: 3` is warranted, write 3 — AUDITOR evaluating itself with uniform 7s is the exact anti-pattern AUDITOR was built to detect in others.

实务上: AUDITOR 的 spec(`pro/agents/auditor.md`)禁止"blanket 7s or 8s",并要求每个维度必须基于**具体证据**(quoted agent output、score contradiction、skipped phase)。如果 AUDITOR 的 body 里写"all agents performed well" 这种通用赞美,这是它自己禁止的 anti-pattern,下次 AUDITOR 扫历史时会 flag 自己的问题。

这是一个二阶的自监控:**AUDITOR 检测 AUDITOR**。不完美,但比没有强。

### 新装 v1.7 的第一天没有 eval-history,我怎么知道系统健康?

**前 3 次 session 都不会有系统性警告**——检测规则最低需要 3 条记录。

前 3 次你可以:
- 手工检查 eval-history 文件内容,看分数是否在预期范围
- 留意 AUDITOR 本身在 Decision Review 里 surface 的即时问题(那部分 v1.6.2a 就有)

3 次之后 RETROSPECTIVE 开始扫描,系统性信号开始出现。

### Migration 会不会把 v1.6.2a 的历史 AUDITOR 报告回填?

**不会**(spec 明说 §11)。

理由: v1.6.2a 的 AUDITOR 报告是**非结构化散文**,fit 不进 v1.7 的 YAML schema。强行回填会产生低信号噪声,污染**系统性检测**——connection 3 次低分规则会误触发,导致真正的问题被淹没。

**eval-history 从 v1.7 day 1 重新开始**。想查 v1.6.2a 的历史?直接读 `_meta/journal/` 里的 session 报告。

### 我编辑 eval-history 里的分数会怎样?

文件是**永不编辑**的(spec 硬规则)。你**技术上能改**,但:

- RETROSPECTIVE Mode 0 和 tools/reconcile.py 都默认"文件没改过"
- 如果你改了历史分数,系统性检测结果会失真
- 长远看,你失去了 eval-history 作为"真实自评"的价值

正确做法:不改。如果你不认同某次评价,在**下次 session** 说,让 AUDITOR 写一份新的反驳 eval 文件。

### patrol-inspection 和 decision-review 有什么区别?

两种 `evaluation_mode`:

| Mode | 触发 | 评的是什么 |
|------|------|----------|
| `decision-review` | 每次全朝议决策 Step 8 | 本次决策的工作流质量 |
| `patrol-inspection` | RETROSPECTIVE 检测 `lint-state.md >4h` | 最近若干 session 的横截面健康(wiki 孤儿、concept 孤立边、SOUL 矛盾累积) |

`patrol-inspection` 是**巡检**,不对应特定 session——它是"我过段时间检查一下全局"。两种 eval 都写到同一个目录,用 `evaluation_mode` 字段区分。

### 如果 eval-history 出现一条严重 violation(比如 adjourn 完整度 2/10),我该立即做什么?

不要 panic。按优先级:

1. **读 body 的 Weaknesses 和 Recommendations**——AUDITOR 通常给出了具体的修复方向
2. **查最近的 session journal**,看 adjourn 是否真的 broken(ARCHIVER 4 phase 有没有跑完、Completion Checklist 是否有 TBD)
3. **如果是结构性问题**(archiver 被拆分多段跑),按 Recommendations 改 ARCHIVER 的 prompt / `pro/CLAUDE.md` 的 state machine 约束
4. **如果是偶然**(某次 Claude API 抖动导致 phase 中断),记录下来,下次 session 正常 adjourn 就能恢复

不需要立即 rollback 或重装 Cortex——eval-history 本身是**诊断**,不是**灾难**。

---

## Troubleshooting

### "eval-history 目录下文件很少,远少于 session 数量"

诊断:

```bash
# session 文件数
ls _meta/sessions/*.md | wc -l

# eval 文件数
ls _meta/eval-history/*.md | wc -l
```

比例应该在 50–80%(因为 direct-handle / Express 短 / STRATEGIST 都不写)。如果比例 <30%,可能:

1. AUDITOR 在多次 session 里写入失败(磁盘、权限)——查 session journal 里 AUDITOR 部分有没有 "eval write failed" 消息
2. `pro/agents/auditor.md` 的 spec 对"什么场景写"的判断过严——可能 Express 的 brief report 都被当作"不够深度"跳过了

处理:
```bash
uv run tools/reconcile.py
```
会列出"有 session 但无 eval"的 orphan,你可以 investigate 具体是哪些 session 被跳过。

### "Systemic warning 连续出现但我已经改了配置"

改配置后,**eval-history 里旧的数据还在**——规则 1–4 基于"最近 10 份",改完后需要**10 个新 session** 才能完全刷掉旧数据。前几次 session 警告会继续出现。

如果 urgent 想清掉警告(比如你在演示系统健康),可以:

```bash
# 把老 eval 归档到 _archive/ (不删除)
mkdir -p _meta/eval-history/_archive/
mv _meta/eval-history/2026-03-*.md _meta/eval-history/_archive/
```

RETROSPECTIVE 只读 `_meta/eval-history/*.md` 顶层,不读 `_archive/`。

### "warning block 一直不显示,但我看数据有明显下滑"

可能原因:

1. **规则阈值未触发**——"下滑"和"连续低于阈值 N 次"不同。确认具体规则里 N 的值
2. **RETROSPECTIVE Mode 0 的 eval-history 读取失败**——查 session 起始时的 briefing,如果有 "⚠️ 趋势对比不可用" 类似提示,说明读失败
3. **`_meta/eval-history/` 是最近创建的,只有几份文件**——规则 1/2/3 都要求 5–10 份记录才能判断,少于 3 份不触发

---

## 深入阅读

同目录用户文档:

- [overview.md](./overview.md) — Cortex 总览,eval-history 是四机制的**二阶监控**
- [hippocampus-recall.md](./hippocampus-recall.md) — `cognitive_annotation_quality` 监控 hippocampus 质量
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — `wiki_extraction_quality` 监控 archiver Phase 2
- [narrator-citations.md](./narrator-citations.md) — `citation_groundedness` 监控 narrator 引用
- [gwt-arbitration.md](./gwt-arbitration.md) — `cognitive_annotation_quality` / `suppression_precision` 监控仲裁质量

Spec 层(英文):

- `references/eval-history-spec.md` — 完整 spec: schema、系统性规则、存储、迁移
- `references/cortex-spec.md` §Open Questions — eval-history 驱动的 spec revision 流程
- `references/hooks-spec.md` — `process_compliance` 违规日志来源
- `pro/agents/auditor.md` — 唯一的 eval-history 写入者
- `pro/agents/retrospective.md` — Mode 0 的 pattern detection

其他:

- `tools/stats.py` — 月度/季度摘要
- `tools/reconcile.py` — orphan 检测
- `devdocs/research/2026-04-19-hermes-analysis.md` — Hermes Lesson 5(自评必须回流)

---

**上一篇**: [gwt-arbitration.md — 显著性竞争](./gwt-arbitration.md)

**回到总览**: [overview.md — Cortex 总览](./overview.md)
