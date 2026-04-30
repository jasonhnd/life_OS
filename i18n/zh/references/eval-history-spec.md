---
translated_from: references/eval-history-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Eval History 规范（Eval History Specification · v1.7）

Eval history 是 Life OS 的结构化自我评估反馈回路。它是 Hermes RL 训练信号的 spec 层等价物——但不训练任何模型。AUDITOR 为每个 session 写入一条结构化评估；RETROSPECTIVE 在 Start Session 时扫描历史，浮现系统性的质量漂移。

---

## 1. 目的（Purpose）

Eval history 是 Life OS 随时间自我检视的机制。

单次 AUDITOR 报告已经会对每个 session 的 agent 表现打分，但在 session 结束后就蒸发了。它们对于*本次*审议是有用的；但它们不会告诉系统*最近十次审议*发生了什么。那个缺失的回路正是 eval history 要闭合的。

- **AUDITOR** 是写入者。每次完整审议或 express workflow 之后，它把自己的判断以结构化 YAML + markdown 形式序列化进 `_meta/eval-history/`。
- **RETROSPECTIVE Mode 0** 是主要读者。每次 Start Session 时它读最近 10 个 eval 文件，检测系统性模式——重复违规、分数下滑、伪造引用、跳过的 phase。
- **Tools**（stats、reconcile）读取历史用于月度汇总与 orphan 检测。

灵感来自 Hermes 的 RL 训练回路：Hermes 把 agent 轨迹压缩为训练信号，然后 fine-tune 模型。Life OS 没法 fine-tune 它的 host（Claude、Gemini、Codex），但它能 fine-tune 它的*规则*——把质量信号写到磁盘上，让 RETROSPECTIVE 在下一个 session 把它浮现出来。信号通过人类注意力改变系统行为，而非梯度下降。

这也是对 `devdocs/research/2026-04-19-hermes-analysis.md` 里 Hermes Lesson 5 的直接回答：自我评估必须反馈给系统，而不是仅仅累积成一次性报告。

---

## 2. 文件位置（File Location）

```
_meta/eval-history/
└── {YYYY-MM-DD}-{project}.md
```

每个经过 AUDITOR 的 session 一个文件。

- `{YYYY-MM-DD}` —— session 开始日期（ISO）。
- `{project}` —— 绑定项目的 slug（kebab-case、小写）。
- 同一项目同日多 session 追加 `-{HHMM}` 做消歧：`2026-04-20-career-change-1430.md`。

Eval 文件和其他 `_meta/` artifacts 并列（STATUS.md、STRATEGIC-MAP.md、lint-state.md），遵守同样的约定：由 agent 编译、给人类读、事后不得手动编辑。

---

## 3. YAML Frontmatter Schema（YAML 前置元数据模式）

每个 eval 文件以 YAML frontmatter 块开头。未知字段被读者忽略；缺失的必填字段会被 `tools/reconcile.py` 标出。

```yaml
---
eval_id: {YYYY-MM-DD-HHMM}-{project}
session_id: string                 # references _meta/sessions/{session_id}.md
evaluator: auditor | auditor-patrol
evaluation_mode: decision-review | patrol-inspection
date: ISO 8601 timestamp
scores:
  information_isolation: integer (0-10)
  veto_substantiveness: integer (0-10)
  score_honesty: integer (0-10)
  action_specificity: integer (0-10)
  process_compliance: integer (0-10)
  adjourn_completeness: integer (0-10)
  soul_reference_quality: integer (0-10)
  wiki_extraction_quality: integer (0-10)
  cognitive_annotation_quality: integer (0-10)    # v1.7: hippocampus output quality
  citation_groundedness: integer (0-10)           # v1.7: narrator citation validity
violations:
  - type: adjourn_phase_skip | notion_sync_skip | citation_missing | ...
    agent: ROUTER | ARCHIVER | ...
    severity: critical | high | medium | low
    detail: string
agent_quality_notes:
  PLANNER: string
  REVIEWER: string
  DISPATCHER: string
  FINANCE: string
  EXECUTION: string
  GROWTH: string
  INFRA: string
  PEOPLE: string
  GOVERNANCE: string
  AUDITOR: string
  ADVISOR: string
  ARCHIVER: string
---
```

说明：

- `scores` 是 0–10 的整数。不允许半分——强迫 AUDITOR 下决断。
- `violations` 是列表；空列表表示"无违规"。
- `agent_quality_notes` 只包含本次 session 实际参与的 agent。Express path 会省略大多数条目。

---

## 4. 正文格式（Body Format）

markdown 正文接在 frontmatter 后，由人类读者与 RETROSPECTIVE Mode 0 的模式扫描共同消费。

```markdown
## Summary
{一段式高层评估——发生了什么、工作流是否保住、头条分数}

## Strengths
- {做得好的点，基于具体证据}

## Weaknesses
- {需要改进的点，基于具体证据}

## Systemic Pattern Observations
{如果本次 session 的模式与过往 session 一致，在此注明——例如"连续第三次 session 中 ARCHIVER Phase 2 产出零个 wiki 候选"}

## Recommendations
- {下次 session 的具体改进，点名 agent + 点名机制}
```

正文规则：

- Strengths 与 Weaknesses 必须引用具体证据（引用 agent 输出、分数矛盾、跳过的 phase）。"所有 agent 表现都不错"之类的泛泛赞扬是 AUDITOR 反模式，`pro/agents/auditor.md` 明令禁止。
- Systemic Pattern Observations 对单次 session 的异常是可选的；当最近 10 个 eval 中检测到重复模式时是必填的（RETROSPECTIVE 提供跨会话提示；AUDITOR 在此处复述）。
- Recommendations 必须指向具体 agent（PLANNER / REVIEWER / ARCHIVER / ...）与具体机制（分数校准 / 检查清单覆盖 / wiki 标准），不得是空泛的鞭策。

---

## 5. 分数维度（Score Dimensions）

十个维度，每个 0–10，各有三个校准锚点。每份 AUDITOR 评估必须填满十项——缺失维度会被 `tools/reconcile.py` 标出。

### 5.1 information_isolation (0–10)

上游上下文泄漏的 HARD RULES 是否在所有 agent 之间保持。

- **10**：PLANNER 完全不知道 ROUTER 的推理。REVIEWER 只收到 planning document。各 domain 不引用彼此的分数或结论。全程无污染。
- **5**：轻微泄漏——例如 ROUTER 暗示哪些 domain 会触发，或某 domain 说"正如另一份 review 所指出的"。
- **0**：明显的交叉污染。REVIEWER 看到 PLANNER 的原始思路，或两个 domain 相互点名引用。

### 5.2 veto_substantiveness (0–10)

REVIEWER 的批准/否决是否基于 8 项检查清单并附具体证据。

- **10**：每项检查清单都有具体观察。否决决定引用失败项与所需修正方向。
- **5**：检查清单套用了，但证据浅薄（"逻辑成立"但没说为什么）。
- **0**：橡皮图章式批准。没跑检查清单。否决理由含糊或缺失。

### 5.3 score_honesty (0–10)

各 domain 分数是否与其自身分析文本对应。

- **10**：每个 domain 的数值分数与其叙述的严重性匹配。无面子工程。当分析明显不同时，跨 domain 的标准差 > 1.0。
- **5**：有一两个可疑分数——例如一段写满严重担忧的段落配个 7 分。
- **0**：全是 7 分或 8 分，或者分数直接和它自己的风险评估矛盾。

### 5.4 action_specificity (0–10)

行动项是否具体、可执行、带时限、有 owner。

- **10**：每项行动都点名 domain owner、截止日期与具体第一步。
- **5**：行动具体但缺少截止日期或 owner。
- **0**：行动只是愿望（"想想看"、"考虑其影响"）。

### 5.5 process_compliance (0–10)

工作流状态机是否端到端被遵守。

- **10**：每一步强制步骤按强制顺序执行。无跳过的 AUDITOR、无跳过的 ADVISOR、无跳过的 Notion sync。Adjourn 状态机保住。
- **5**：有一步被跳过但在 session 中被发现并补救。
- **0**：多个 phase 跳过，或非法转移（Summary Report → ARCHIVER 中途没经过 AUDITOR + ADVISOR）。

### 5.6 adjourn_completeness (0–10)

ARCHIVER 子 agent 是否执行了全部四个 phase（Archive、Knowledge Extraction、DREAM、Sync）并产出干净的 Completion Checklist。

- **10**：全部 4 个 phase 都跑了。Checklist 值是真的（不是 "TBD"）。Notion sync 回到 orchestrator 并已执行。
- **5**：4 个 phase 跑了 3 个，或 Phase 3 DREAM 没产出 journal entry。
- **0**：流程被切分。多消息 archiver。Checklist 里是占位值。

### 5.7 soul_reference_quality (0–10)

REVIEWER 是否引用了与被审决策相关的 SOUL 维度。

- **10**：每个与决策相关的 SOUL 维度（active + dormant + conflict zone）都被显式引用，带置信度和方向。
- **5**：SOUL 被引用但有选择性——例如只引用高置信度维度，忽略了重要的 dormant 维度。
- **0**：SOUL 完全未被引用，或被引用但未整合进 review。

### 5.8 wiki_extraction_quality (0–10)

ARCHIVER Phase 2 萃取的 wiki 候选是否通过全部 6 项准则 + 隐私过滤器，以及萃取是否可跨 session 复用。

- **10**：候选具体、可复用、隐私干净，落在正确的 domain。
- **5**：有些候选通过了但与现有条目冗余，或太窄无法复用。
- **0**：本该萃取却没萃取，或萃取通不过隐私过滤器却照样上线。

### 5.9 cognitive_annotation_quality (0–10) — v1.7

hippocampus 层检索是否浮现了正确的 wiki 条目，并附上与本次 session 实际效用对齐的相关性分数。

- **10**：检索到的条目被使用。相关性分数追踪到了对决策的实际影响。
- **5**：检索到的条目被使用但相关性评分粗糙。
- **0**：检索到的条目被忽略，或相关性是伪造的。

### 5.10 citation_groundedness (0–10) — v1.7

narrator 层引用（对过往 session、wiki 条目、SOUL 维度的引用）是否指向真实存在且与所声称内容相符的 artifact。

- **10**：每个引用都能解析到真实 artifact 且内容与声称一致。
- **5**：大多数引用能解析；少数对原文做了超出范围的改写。
- **0**：引用是伪造的或指向不存在的 session/条目。

---

## 6. 触发条件（Trigger Conditions）

### 6.1 AUDITOR 写入 eval-history 条目的时机

- 每次完整审议工作流之后（`pro/CLAUDE.md` Step 8）。
- 每次 express 分析工作流产出深度足以评估的 Brief Report 之后。
- RETROSPECTIVE Mode 0 触发的 Patrol Inspection 之后（lint-state > 4h）。Patrol 写入时 `evaluation_mode: patrol-inspection`。

### 6.2 AUDITOR 不写条目的时机

- ROUTER 直接处理请求（无子 agent 工作可供评估）。
- STRATEGIST session（评估域不同——评估的是 thinker 对话质量，而非审议质量）。
- 首次运行 / 空 second-brain 的 session，没有决策发生。
- 在 PLANNER 产出之前就中止的 session。

### 6.3 写入时机

AUDITOR 在 Step 8 末尾、ADVISOR 运行之前写 eval 文件。从 AUDITOR 视角这是同步写入，但它不阻塞 ROUTER——若写入失败，AUDITOR 报告失败，session 继续。

---

## 7. 系统性问题检测（Systemic Issue Detection）

RETROSPECTIVE Mode 0 在 Start Session 时读最近 10 个 eval 文件，并套用下列检测规则。检出的模式会出现在晨间简报的 systemic-issue 警告块中。

### 7.1 adjourn_completeness 趋势

若连续 3 次或以上 session 出现 `adjourn_completeness < 6` → 警告："archiver 子 agent 可能没有正常启动"。

这抓的是 v1.6.x 反复出现的 bug：ROUTER 插在 ARCHIVER 各 phase 之间，造成流程被切分。

### 7.2 wiki_extraction_quality 下降

若 `wiki_extraction_quality` 在 5 次或以上 session 中呈下降趋势 → 警告："ARCHIVER Phase 2 可能在静默跳过萃取"。

### 7.3 citation_groundedness 失败

若 narrator 引用在最近 10 次 session 中解析失败率 > 20% → 警告："narrator 层在幻觉信号"。

### 7.4 cognitive_annotation_quality 下限

若 `cognitive_annotation_quality < 5` 持续最近 5 次 session → 警告："需要调参 hippocampus 检索"。

### 7.5 process_compliance 复发

若同一 `violations[].type` 在最近 30 天内出现 3 次或以上 → 触发合规日志升级：该违规从 eval history 升格为 `user-patterns.md` 里被追踪的行为模式，下次 session 的 ADVISOR 会作为直接观察项浮现。

### 7.6 简报格式

警告出现在 Start Session 简报中 DREAM Auto-Triggers 块之后、Strategic Overview 之前。格式（按 active theme 语言本地化）：

```
⚠️ 系统性问题检测：
- 退朝完整度连续 3 次 ≤6 → 建议检查 archiver subagent 启动
- Wiki 萃取质量从 4/15 起下降 → 建议本次重点关注
```

若未检测到系统性问题，整块省略（无占位符）。

---

## 8. 归档策略（Archive Policy）

- Eval 文件永久保留。每个文件很小（~5 KB），1000 个 session 总计约 5 MB。
- 超过 6 个月的文件可被压缩为季度摘要 `_meta/eval-history/_digest/{YYYY-Q}.md`，原文件移到 `_meta/eval-history/_archive/`。摘要保留头条分数与系统性模式；单次 session 依然可读。
- 摘要由 `tools/stats.py` 在带 `--compress-old` 运行时写入，从不自动写。

---

## 9. 读流程（Read Flow）

多种消费者出于不同目的读 eval history。

| 消费者 | 频率 | 范围 | 目的 |
|----------|-----------|-------|---------|
| retrospective Mode 0 | 每次 Start Session | 最近 10 个文件 | 晨间简报的系统性模式检测 |
| auditor | 被调用时 | 同项目最近 5–10 个文件 | 评估本次 session 前的历史校准参考 |
| tools/stats.py | 按需 | 全部文件或日期范围 | 月度 / 季度质量报告 |
| tools/reconcile.py | 按需 | 全部文件 | Orphan 检测——有 eval 无对应 session、有 session 无对应 eval |

读者必须容忍缺字段（不同 Life OS 版本可能写过不同的 schema）。YAML schema 向前兼容：未知字段忽略，缺失-但-期望的字段触发 reconcile 警告而非硬失败。

---

## 10. 写流程（Write Flow）

- 触发：AUDITOR 在完整审议 Step 8 完成 Decision Review（或 express path 的 Brief-Report 等价物，或 Patrol Inspection）。
- 路径：`_meta/eval-history/{YYYY-MM-DD}-{project}.md`。
- 冲突解决：若文件已存在（同日期、同项目、当天第二次或以后 session），AUDITOR 在文件名后附 `-{HHMM}`：`2026-04-20-career-change-1430.md`。
- 失败处理：若写入失败（磁盘满、权限错误、路径缺失），AUDITOR 在其常规 Decision Review 输出中报告。session 继续。失败本身作为 process compliance 违规记入下次 session 的 eval。
- 不可变性：eval 文件创建之后永不编辑。若评估错了，下次 session 写一个新文件并附反转说明。旧文件作为历史记录留存。

---

## 11. 迁移（Migration）

v1.7 之前不存在 eval history。

- `tools/migrate.py` **不**回填 `_meta/journal/` 里的历史 AUDITOR 报告。那些报告是无结构的散文，不匹配 schema；回填只会产生低信号噪声，污染系统性检测。
- Eval history 在 v1.7 第一天清零起步。v1.7 的第一次 Start Session 不会显示任何系统性警告（没有历史可扫）。警告会在至少 3 次连续 session 被记录后开始出现。
- 需要分析 v1.7 之前 session 历史的用户应直接使用已有的 `_meta/journal/` 报告；它们不被迁移。

---

## 12. 反模式（Anti-patterns）

这些是禁止的。RETROSPECTIVE 与 `tools/reconcile.py` 在检出时会标出。

- **不要**把完整的 Summary Report 嵌入 eval 文件。改为引用 `session_id`。Eval 文件是质量元数据，不是 session 内容副本。
- **不要**为"次要" session 跳过 eval 写入。模式通过量涌现——跳过简单的就毁掉了困难的那部分信号。
- **不要**在创建后编辑 eval 文件。若评估错了，下次 session 写新文件注明反转。旧文件不可变。
- **不要**让 AUDITOR 的 eval 写入阻塞用户侧工作流。从 AUDITOR 视角是同步的，但写入失败不得卡住 ADVISOR、ARCHIVER 或 session 收尾。
- **不要**把 eval 文件同步到 Notion（用户决策 #12）。Eval history 是本地内省 artifact；推到 Notion 会让移动端视图变噪，移动端也没有消费者。
- **不要**允许 AUDITOR 自己的评估出现面子工程。若 `score_honesty: 3` 是应得的，就写 3——AUDITOR 拿统一的 7 分评估自己正是 AUDITOR 当初被造出来揭露的那种反模式。
- **不要**为无法观察到的维度编造分数。若没有任何 SOUL 引用相关，把 `soul_reference_quality` 设为本 session 的默认值（通常是 10——"不适用，故无违规"），并在 `agent_quality_notes` 里说明理由。

---

## 13. 相关规范（Related Specs）

- `references/cortex-spec.md` —— 整体 Cortex 架构；eval-history 是 v1.7 五大核心 artifact 之一
- `references/session-index-spec.md` —— `session_id` 字段把每条 eval 条目链接回其 session 摘要
- `references/hippocampus-spec.md` —— 产出 AUDITOR 通过 `cognitive_annotation_quality`（§5.9）评分的信号
- `references/gwt-spec.md` —— 产出 AUDITOR 通过 `cognitive_annotation_quality` 评分的仲裁质量信号
- `references/narrator-spec.md` —— 产出 AUDITOR 通过 `citation_groundedness`（§5.10）评分的引用质量信号
- `references/hooks-spec.md` —— 违规日志喂给 `process_compliance` 维度（§5.5）与 §7.5 复发检测
- `references/tools-spec.md` —— `stats.py` 与 `reconcile.py` 消费 eval-history 做月度报告与 orphan 检测
- `references/soul-spec.md` —— `soul_reference_quality`（§5.7）评的是 REVIEWER 引用 SOUL 维度的质量
- `references/wiki-spec.md` —— `wiki_extraction_quality`（§5.8）评的是 ARCHIVER Phase 2 wiki 候选
- `pro/agents/auditor.md` —— eval-history 条目的唯一写入者（Step 8 末尾）
- `pro/agents/retrospective.md` —— Mode 0 读者，做系统性模式检测（最近 10 个文件）
- `devdocs/research/2026-04-19-hermes-analysis.md` —— Hermes Lesson 5（自我评估必须反馈）是本规范的动机

---

## 译注

- 本文档将 Hermes RL loop 作为灵感来源；翻译保留 `RL training signal` 原义。
- `veto / adjourn` 等朝廷隐喻术语在 Life OS 设定中已定义（否决 / 退朝），正文视上下文选用中文或英文。
- "面子工程"对应 "face-saving"，沿用中文 README 既有译法。
- Score dimensions 的英文字段名保留不译（如 `information_isolation`），以便与 YAML schema 对齐；每个维度标题下方用中文解释。
