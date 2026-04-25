# Narrator 引用与 Trace · 防编造机制

> 面包屑: [← Cortex 总览](./overview.md) · [← 产品入口:用户指南首页](../index.md)

> 升级到 v1.7 之后,奏折里会出现 `[S:claude-20260419-1238]` 或 `[SOUL:risk-tolerance-v3]` 这样的方括号标注。这不是装饰,也不是强制要求你阅读。它是系统对自己的**诚实承诺**:每一个实质性的断言都指向一个可追溯的 signal,而不是凭空编出来。你随时可以说"trace 这句话",系统会把原始 session / SOUL 维度 / concept 文件的具体内容给你看。这一层叫 **Narrator**。

## 一句话概述

Narrator 是 ROUTER 的**输出阶段**——负责把内部信号翻译成用户可读的 Summary Report,同时**给每个实质性断言加 citation**。Narrator 生成完后,一个独立的 **narrator-validator subagent** 会逐句检查:每个 substantive claim 是不是真的指向了 signal registry 里的某条记录?引用的内容是不是真的支持这个断言?不过关就让 Narrator 重写。最多 3 次,超过就退化到"无引用版本"。

这个机制存在的目的只有一个:**防止 AI 编造貌似合理的历史**。

---

## 为什么要加这一层

### 被发现的问题: Gazzaniga 左脑解释器 (Left-Brain Interpreter)

神经科学家 **Michael Gazzaniga** 做过一个著名实验:把癫痫病人的胼胝体切断(分离左右脑),然后给右脑看一张图(比如"雪地"),给左脑看另一张图(比如"鸡爪")。让病人用左手(受右脑控制)和右手(受左脑控制)各选一张图配对。

结果: 右手选了"鸡",左手选了"铲子"——对应两张看过的图。但当你问病人"你为什么选铲子?"——**左脑语言区会当场编一个完美合理的故事**:"因为要铲鸡粪啊。"

它**不知道**自己没看过雪地。它用它能看到的信息(鸡)去**倒推**一个合理的解释,而且**真心相信这个解释**。

**这是 AI 的核心失败模式**。语言模型不分"我知道"和"我编的",一个流畅自信的叙述可以完全是编造的。在 Life OS 的决策引擎场景里,如果系统说:

> "你上次做类似决策时考虑过这个风险,最终选择了保守路线。"

而实际上:
- 没有上一次决策
- 或有,但考虑的不是这个风险
- 或考虑了但选的不是保守路线

**你信了**,然后基于这个"伪历史"做了新决策。这就是系统性污染。

### Narrator 的结构性回答

**解法不是"让 AI 更努力别编"**——那是靠不住的。解法是把 Narrator 的输出阶段拆成:

1. **Narrator 写**——每个 substantive claim 必须带 `[signal_id]` 引用
2. **Validator 审**——一个独立的 subagent(只有 `Read` 权限)去 signal registry 里查:这个 ID 存不存在?引用的内容支不支持这个断言?
3. **不合格就重写**——最多 3 次。超了就 fall back 到"无引用的原始 Summary Report"并给 AUDITOR 记一笔

**Narrator 不能绕过 Validator**——没有"trust me 模式",没有用户标志可以关掉 Validator。这是 Cortex 的结构性防线,不是软约定。

---

## 用户端看到什么

### 场景 A: 奏折里的引用

ROUTER 在 Step 7 写 Summary Report,Step 7.5 Narrator 重写加 citation。你最终看到的:

```markdown
## 推荐方向

基于你过去的"passpay-v06-refinement"session [S:claude-20260419-1238],
本次决策呈现类似的 5 轮迭代模式,GOVERNANCE 当时打 5/10
[D:passpay-governance-score]。

这个方向与你的"风险承受度"维度(confidence 0.72)[SOUL:risk-tolerance-v3]
一致,但挑战了"家庭优先于事业"(core, confidence 0.82)
[SOUL:family-over-career-v2]——REVIEWER 已标记为 tier_1_conflict。

Finance 和 Execution 分差 4 分 [D:finance-score-6][D:execution-score-2],
触发了 COUNCIL 辩论。
```

每个方括号就是一个 citation。前缀含义:

| 前缀 | 含义 | 示例 |
|------|------|------|
| `S:` | session_id(单次 session) | `S:claude-20260419-1238` |
| `D:` | 具体 domain 打分或字段 | `D:passpay-governance-score` |
| `SOUL:` | SOUL 维度 | `SOUL:risk-tolerance-v3` |
| `C:` | 概念节点 | `C:method:iterative-document-refinement` |
| `W:` | Wiki 条目 | `W:finance/compound-interest` |
| `P:` | user-patterns.md 模式 | `P:avoids-family-topic-on-weekends` |

**前缀是固定的**——Narrator 不允许发明新前缀。如果某个信号源没法映射到这 6 个之一,它**就不能被引用**,因此这个 substantive claim **也不能说出来**。

### 场景 B: Trace UX · 你怀疑某句话

你看到:

> "基于你过去的'passpay-v06-refinement'session [S:claude-20260419-1238],本次决策呈现类似的 5 轮迭代模式"

你想确认。直接说:

> trace [S:claude-20260419-1238]

或用自然语:

> 这句话怎么来的?

或

> 根拠は?

系统回:

```
📎 Trace for: "Your past passpay-v06-refinement session shows a similar 5-round iteration pattern"

Cited signals:
1. S:claude-20260419-1238
   Source: _meta/sessions/claude-20260419-1238.md
   Content match: "Session ran 5 revision rounds on payment gateway spec.
     Each round tightened governance controls. Final GOVERNANCE score
     5/10 due to incomplete fraud-response plan."
   Produced by: hippocampus (Step 0.5 Wave 1)

2. D:passpay-governance-score
   Source: session D-scores extracted by ROUTER at Step 7
   Value: 5 (threshold for flag: < 6)
   Produced by: governance_agent

Confidence: groundedness_score = 1.0 (both citations resolve, content supports claim)
```

**Trace 里没有 LLM 重新生成**——只有"literal excerpt + metadata"。否则就会变成"trace 解释 trace,trace 解释 trace 解释 trace……"的递归 confabulation loop。

### 场景 C: 类别概览 Trace

你想知道**某一类 signal 在本次决策里的全貌**:

> 这次 Summary Report 引用了哪些 SOUL 维度?

系统回:

```
📎 Category trace: SOUL dimensions that influenced this Summary Report

1. SOUL:risk-tolerance-v3 (core, confidence 0.82)
   Referenced by: narrator (×2), governance_agent (×1)
   Source text: SOUL.md § Risk attitude

2. SOUL:family-over-career-v2 (core, confidence 0.82)
   Referenced by: narrator (×1), reviewer (×1)
   Source text: SOUL.md § Family priority

3. SOUL:evidence-discipline (secondary, confidence 0.61)
   Referenced by: narrator (×1), execution_agent (×1)
   Source text: SOUL.md § Evidence discipline
```

### 场景 D: 你问 connective tissue 的 trace

某些句子是**连接组织**(discourse glue)——转折、开场、框架式陈述——不带事实内容,Validator 会跳过它们(§3 §Substantive vs Connective 详见)。如果你 trace 这类句子:

> trace "Let me walk through this"

系统回:

```
That sentence is connective tissue (a transition / framing / rephrasing),
not a grounded claim. No signal stands behind it. If you want to trace a
substantive claim in the same report, let me know which one.
```

这防止"系统为了回应 trace 请求反向编造一个 signal 来支撑一个本来就没事实内容的句子"——那才是真正的 Gazzaniga 环。

---

## Substantive vs Connective · 什么需要引用

Narrator 输出的每一句都会被分类:

### Substantive(需要引用)—— 移除这句会丢失事实信息

- 历史性陈述: "上次你做过 X……"
- 模式性陈述: "你倾向于……"
- SOUL: "这和你的 Y 价值观一致"
- 决策含义: "GOVERNANCE 的担忧是……"
- 跨 session 关联: "这和你 Z 项目的决策相关"
- 数值或分数断言: "Finance 给了 6/10"
- 角色归因: "ADVISOR 标记了情绪权重"

### Connective(不需要引用)—— 只是 discourse glue

- 过渡: "让我一步步说……"
- 框架: "从分析来看……"
- 元评论: "我简单总结一下……"
- 开场/收尾: "好,看看这件事……"
- 纯粹的改写: "换句话说……"

**判断规则**: 删掉这句话,剩下的文字是否丢失了事实内容?丢了 → substantive,必须有 citation。没丢 → connective,跳过。

---

## Validator 怎么工作

narrator-validator 是一个独立的 Claude Code subagent(**不是 Anthropic Haiku 外部 API**),只有 `Read` 权限,用 sonnet 模型。

### 输入
- Narrator 输出的完整 markdown
- Signal source registry(本次 session 积累的所有 signal)

### 逐句流程

对每一句:
1. **分类**: substantive 还是 connective?用 §3 规则
2. connective → skip
3. substantive:
   1. 提取所有 `[signal_id]`
   2. 对每个 citation:
      - 前缀是否在 6 个合法前缀之内? 否 → `format_error`
      - `signal_id` 是否在 registry 里? 否 → `missing_signal`
      - 读引用目标的文件/字段,验证**断言是否得到内容支持**?否 → `unsupported_claim`
   3. 如果是 substantive 但**零 citation** → `missing_signal`(tagged "no citation")

### 输出 · 评分

```yaml
validation:
  total_citations: 12
  valid: 11
  invalid:
    - position: 842
      citation: "[SOUL:something-else]"
      reason: unsupported_claim
      claim_text: "This aligns with your value of X"
  groundedness_score: 0.92
```

### 阈值

**`groundedness_score ≥ 0.9`** 才放行。低于 0.9 → narrator 重写(**最多 3 次**),带上 validator 的错误反馈和建议引用。

### 规定 3 次重写都没过怎么办?

退化到 **un-cited Summary Report**(Step 7 的原始输出,不走 Narrator 重写层),AUDITOR 记一个 `narrator_failed_after_3_attempts` 的 flag 写进 eval-history。**用户仍然会收到奏折**——只是不带引用。

---

## Signal Source Registry

这是 Narrator 和 Validator 共同依赖的"真相之源":本次 session 所有信号的 id 和指向。

**registry 由 ROUTER 在 Step 7.5 前组装**:

| 时机 | 加进来的信号 |
|------|------------|
| Step 0.5 | hippocampus / SOUL check / concept lookup 的信号 |
| Step 5(六领域并行) | 每个领域报告产生的 domain score |
| Step 6(如触发 COUNCIL) | COUNCIL 辩论的信号 |
| Step 4(DISPATCHER) | 作为"已知前提"注入的 wiki / pattern 引用 |

**registry 是 append-only**——session 中途不删除任何 signal。

格式示例:

```yaml
signal_sources:
  - id: S:claude-20260419-1238
    type: session
    file: _meta/sessions/claude-20260419-1238.md
    producer: hippocampus
  - id: SOUL:risk-tolerance-v3
    type: soul_dimension
    ref: SOUL.md#risk-tolerance
    producer: soul_check
  - id: C:method:iterative-document-refinement
    type: concept
    file: _meta/concepts/method/iterative-document-refinement.md
    producer: concept_lookup
  - id: D:GOVERNANCE-score-5
    type: domain_score
    value: 5
    producer: governance_agent
  - id: W:finance/compound-interest
    type: wiki
    file: wiki/finance/compound-interest.md
    producer: wiki_index
  - id: P:avoids-family-topic-on-weekends
    type: pattern
    ref: _meta/user-patterns.md#avoids-family-topic-on-weekends
    producer: retrospective
```

---

## 什么时候 Narrator 不介入

三种场景,**Narrator 完全跳过**:

| 场景 | Narrator 行为 |
|------|-------------|
| **ROUTER 直接处理**(闲聊、翻译、简单查询) | **不介入**——signal registry 空,ROUTER 直接回 |
| **Express 快车道**(域级分析,无决策) | **只验证 hippocampus / SOUL / concept 引用**,因为 registry 里没有 domain score |
| **STRATEGIST 群贤堂**(哲学对话,无决策) | **不介入**——STRATEGIST 的输出是思想家的独立叙述,不重写、不加引用 |

理由: 这些场景不产生可验证的"事实性断言"——闲聊没 signal,Express 没全套 domain 分析,STRATEGIST 是开放性对话。强上 citation 只会产生 noise。

---

## 用户动作 · 你可以怎么干预

### 1. Trace 任何带方括号的引用

```
trace [S:claude-20260419-1238]
这句话怎么来的?
根拠は?
```

系统返回原始引用和内容片段,**不做 LLM 解释**——trace 是"反编造"的最后防线,也必须是有据的。

### 2. 不认同引用? 直接反驳

你 trace 完发现系统引用的那段 session summary 其实是**误读**(比如 GOVERNANCE 打 5/10 的原因在另一个问题上,不是 fraud-response):

> 这个 trace 错了。S:claude-20260419-1238 里 GOVERNANCE 的 5/10 是因为 X,不是 fraud-response

ROUTER 会:
- 把你的反驳记入本次 session 的 Summary Report 修正段
- 在 session 结束的 archiver Phase 2 阶段,把"用户反驳引用"这个事件打进 AUDITOR 的 `citation_groundedness` 维度
- 如果同一个 signal 被反驳多次,AUDITOR 会在 eval-history 里 flag:"这条 session summary 可能需要重写"

### 3. 要求无引用版本

极少数情况下你觉得方括号标注太吵、想要干净的叙述:

> 给我一版不带 citation 的奏折

ROUTER 会输出 Step 7 的原始 Summary Report(未经 Narrator 重写)。但注意: **这是一次性请求,不是持久配置**。下一次决策 Narrator 仍会工作——因为 Narrator 的核心价值在于结构性防编造,不是可选美化。

### 4. 不能绕过 Validator

Narrator 和 Validator 之间**没有用户标志**可以关闭。原因:

- 安全模型: 用户想关掉 Validator 的动机 99% 是"我不喜欢看方括号"——这不应该威胁 Cortex 的事实守门
- 如果你真的不喜欢方括号,解法是前一条(一次性拿 un-cited 版本),不是永久关 Validator

**唯一的永久关闭**: 编辑 `_meta/config.md`,`narrator_validator_enabled: false`。这会让 Narrator 输出的 citation **不被验证**——你仍然看到方括号,但它们可能是错的。**不推荐**。

---

## 常见疑问

### Citation 失败率多少算正常?

- **`citation_groundedness ≥ 9/10`**:稳定状态的目标
- **`regeneration_count = 0`**: 全朝议 session 里超过 80% 应该一次通过
- 任一 session `citation_groundedness < 7/10`: AUDITOR 标为质量事件
- 每周 `regeneration_count > 1` 的趋势: AUDITOR 标为 "narrator drift"

这些指标会出现在 `_meta/eval-history/{date}-{project}.md` 里,并被 RETROSPECTIVE Mode 0 扫描(详见 [auditor-eval-history.md](./auditor-eval-history.md))。

### Validator 为什么用 sonnet 不用 haiku?

用户决策 #9 的明确结论:**用 Claude Code subagent,不用外部 Anthropic Haiku API**。

理由:
- **零外部成本**——subagent 跑在你已付的 Claude 计划额度里,不是另一个 Haiku API 账号
- **无 API key 管理**——没有外部密钥、rotation、预算
- **符合 Life OS 立场**——一切智能都在 session 内,不引入外部依赖
- **sonnet 够用**——citation 验证不需要 Opus,也不需要 Haiku 那么便宜的判断力。latency 预算里有(validator 一轮 1–3 秒)

### Validator 能不能自己作弊?

Validator 只有 `Read` 权限,无法改 signal registry。它的失败只能是"说某个 valid 的 claim 是 invalid"(过度警惕)或"说某个 invalid 的 claim 是 valid"(漏网)。两者都留有痕迹:

- 过度警惕 → Narrator 被迫进入重写循环,如果最终 3 次都没过,AUDITOR 标 `narrator_failed_after_3_attempts`
- 漏网 → 用户 trace 时看到 "⚠️ signal no longer resolvable" 或 trace 内容明显不支持断言,用户反驳 → AUDITOR 标 `citation_groundedness` 低

长期看,AUDITOR 对 Validator 本身有二阶监控——这是 eval-history 的价值(详见 [auditor-eval-history.md](./auditor-eval-history.md))。

### 如果系统真的想说一件事但没有 signal,怎么办?

**那就不说**。

Narrator 的 invariant 是: "没有 signal → 没有 substantive claim"。这不是一条软约定——Validator 会把"零 citation 的 substantive sentence"直接标为 `missing_signal`,Narrator 必须重写,要么**删掉那句**,要么**找到支持的 signal 并引用**。

如果真心找不到支持的 signal,那这句话本来就不该说——那是 AI 在填充它不知道的地方。

### Narrator 会不会为了过 Validator 就给随便一个不相关的 signal 贴上去?

Validator 不只检查 **"signal 存在"**,还检查 **"content 支持 claim"**。不支持就返回 `unsupported_claim` 错误,Narrator 继续被迫重写。

贴假 signal 不是偷懒的路径,是**更重的惩罚**。

### 这个层会增加多少 latency?

| 阶段 | 预算 |
|------|------|
| Narrator 生成(ROUTER 内部的重写阶段) | 2–5 秒 |
| Validator 扫描(单次) | 1–3 秒 |
| 重写 + 重验证循环 | 每轮 +2–5 秒 |
| **最坏 3 次重试总和** | **15 秒** |

全朝议一次决策本来要跑六领域 + 审计 + 归档,多 15 秒在噪音里。Express 和 direct-handle 不走 Narrator,不受影响。

### Citation 密度太高导致奏折读起来像法律文书怎么办?

**v1.7 Phase 2** 用的是 per-substantive-claim 粒度——每句 substantive 都需要至少一个 citation。如果产出在实际使用中 **"感觉被 stamp 过"**,用户决策预留了调整路径: 把粒度**粗化到 per-paragraph**(每段一个 citation 就行)——**不削弱防编造保证,因为 registry 仍然完整**。

这个调整会在 v1.7 投入使用后 3 个月左右基于实际用户反馈决定。Spec 里是 open question,不是固定契约。

---

## Troubleshooting

### "Trace 显示 '⚠️ signal no longer resolvable'"

某个 `signal_id` 指向的文件被删除或改名了。常见原因:

- 你手工在 `_meta/sessions/` 里删了某个历史 session 文件
- Git 分支切换后索引不一致
- 概念被 retire 到 `_meta/concepts/_archive/`
- SOUL 维度被重命名或删除

**trace 的原始 citation 仍保留**——你知道它**原本指向哪**,只是那个文件暂时/永久没了。如果是意外删除,从 git 历史恢复;如果是归档,内容仍在 `_archive/` 里手动查。

### "Narrator 经常触发重写,session 感觉变慢"

查 eval-history:

```bash
grep -r "regeneration_count" _meta/eval-history/ | tail -20
```

如果 `regeneration_count > 1` 的比例高(超过 30%),可能原因:

1. **Signal registry 过小**——session 没有足够的 hippocampus / concept / SOUL 信号,Narrator 想说的事情超出 signal 能支持的范围。解决: 让 hippocampus 先工作得好(可能 migration 没跑全,或 INDEX 过时)
2. **Narrator prompt 需要调优**——连续 2 周 `regeneration_count` 趋势 > 1,AUDITOR 会标"narrator drift"(详见 [auditor-eval-history.md](./auditor-eval-history.md) §7.3)
3. **Validator 过严**——引用的 signal 在 registry 里确实存在但 Validator 觉得不够支持 claim。这类 case 会在 eval-history 里留下 `unsupported_claim` 的 violation type,帮助后续调优

### "我不想看到方括号,想要干净叙述"

- **一次性**: `给我一版不带 citation 的奏折`——ROUTER 返回 Step 7 原始输出
- **永久关闭引用显示但保留验证**: v1.7 不支持(方括号是 citation 的物理载体,没有就无法 trace)
- **永久关闭整个机制**: `_meta/config.md` 里 `narrator_validator_enabled: false`。**不推荐**——这相当于拿掉防编造的结构性保证

### "Citation 里显示 `SOUL:X` 但我 SOUL.md 里没有这个维度"

如果是 trace 出来的结果,检查:

1. **版本号不匹配**: citation 形如 `SOUL:risk-tolerance-v3` 的 `-v3` 后缀是 dimension 的修订版号。如果你重写了 SOUL 维度但 version 没更新,引用指向的是**旧版本**。解决: 在维度被重写时手工 bump version 号,或让 SOUL 的自动写入机制生成 v4
2. **registry stale**: signal registry 是 session-scoped 的,如果某次 session 的 registry 被写入磁盘但 SOUL 本身后续被改,trace 时会显示 "⚠️ signal no longer resolvable"——这是正常行为
3. **前缀错误**: Narrator 不应该发明新前缀,但如果真的出现了非标准前缀(如 `SOULS:` 或 `soul:`),Validator 会标为 `format_error` 并触发重写。如果你还是看到了,说明 Validator 被绕过——检查 `_meta/config.md` 是否被关闭

---

## 深入阅读

产品入口:

- [What is Life OS](../../getting-started/what-is-life-os.md) — Life OS 整体定位
- [Quickstart](../../getting-started/quickstart.md) — 首次上朝流程

同目录用户文档:

- [overview.md](./overview.md) — Cortex 总览
- [hippocampus-recall.md](./hippocampus-recall.md) — `S:` 前缀指向的 session summary 来源
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — `C:` 前缀指向的 concept 节点
- [gwt-arbitration.md](./gwt-arbitration.md) — signal registry 如何在 Step 0.5 积累 hippocampus/concept/SOUL 信号
- [auditor-eval-history.md](./auditor-eval-history.md) — `citation_groundedness` 维度的长期监控

Spec 层(英文):

- `references/narrator-spec.md` — 完整 spec: substantive/connective 规则、validator 算法、trace UX
- `references/eval-history-spec.md` §5.10 — `citation_groundedness` 计分标准
- `references/cortex-spec.md` §Grounded Generation — 为什么 Gazzaniga 是 Cortex 设计的核心隐患
- `pro/agents/narrator-validator.md` — validator subagent 定义

其他:

- `pro/agents/router.md` — Narrator 行为就住在 ROUTER 里(不是独立 agent)
- `devdocs/architecture/cortex-integration.md` — Step 7.5 插入的位置

---

**上一篇**: [concept-graph-and-methods.md — 概念图谱与方法库](./concept-graph-and-methods.md)
**下一篇**: [gwt-arbitration.md — 显著性竞争](./gwt-arbitration.md)
