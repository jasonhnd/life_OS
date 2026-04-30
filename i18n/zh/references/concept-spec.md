---
translated_from: references/concept-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Concept 规范（Concept Specification）

Concept 文件是 Cortex 突触网络（synaptic network）中的节点。每个文件代表一个可跨会话激活的可复用想法、实体或模式。概念之间的 synapse 边（synapse edges）保存在 concept 文件自身的 YAML frontmatter 中，而不是独立的图数据库。这使得整个网络可以用文本编辑器检视，并通过纯 git 便携可移植。

## 定位（Positioning）

| 存储 | 记录什么 | 示例 |
|---------|----------------|---------|
| `decisions/` | 你决定了什么（具体、带时间戳） | "2026-04-01: 选择了信托结构" |
| `user-patterns.md` | 你做什么（行为模式） | "倾向于回避财务维度" |
| `SOUL.md` | 你是谁（价值观、人格） | "风险偏好：中高" |
| `wiki/` | 你知道什么（可复用的世界结论） | "NPO lending has no 貸金業法 exemption" |
| `_meta/concepts/` | **什么连接什么（synaptic graph）** | "company-a-holding" 节点 + 通往其他概念的边 |

SOUL 管理人。Wiki 管理知识。Concepts 管理让系统知道"如果 A 被激活，还应该点亮什么"的图。它们不得混用。

---

## 原则（Principles）

1. **从零生长**（Grows from zero）—— `_meta/concepts/` 起始为空。无需初始化。
2. **一个概念 = 一个文件（严格）**（One concept = one file, strict）—— 无多主题编纂。禁止把单一概念拆分到多个文件（反模式，参见 §10）。
3. **边与节点同居**（Edges live with nodes）—— 出向 synapse 边保存在源概念的 YAML frontmatter 中。反向索引编译到 `SYNAPSES-INDEX.md`（从不手写）。
4. **在严格标准下自动写入**（Auto-written under strict criteria）—— 当证据积累达到标准时，`archiver` Phase 2 自动创建概念。用户通过删除或说 "undo recent concept" 来干预。
5. **Permanence 决定衰减**（Permanence determines decay）—— 每个概念携带一个 permanence 层级，决定其衰减曲线（用户决策 #9，brainstorm §7）。
6. **生命周期可逆**（Reversible lifecycle）—— `tentative → confirmed → canonical` 是单向晋升路径，但降级（demotion）始终可能（用户决策 #10）。

---

## 文件位置（File Location）

```
_meta/concepts/{domain}/{concept_id}.md
```

| 路径段 | 含义 |
|--------------|---------|
| `_meta/concepts/` | 概念网络的根 |
| `{domain}/` | 主题分区（见下文） |
| `{concept_id}.md` | 每个概念一个文件，按其 ID 命名 |

### 领域分区（Domain partitions）

Domain 是概念的顶层主题槽。最小集合（与 `wiki-spec.md` 和 `method-library-spec.md` 对齐）：

- `finance/` —— 金融实体、金融工具、金融概念
- `startup/` —— 创业、产品、增长概念
- `personal/` —— 个人生活领域概念（非身份 —— 身份属于 SOUL）
- `technical/` —— 工程、架构、实现模式
- `method/` —— 方法论、工作流、流程
- `relationship/` —— 组织与非个人的关系实体
- `health/` —— 健康、健身、医疗概念
- `legal/` —— 法律框架、合规、监管概念
- `writing/` —— 写作技艺、文档精炼方法论、编辑模式

用户可随着第二大脑的增长添加新的 domain 目录。没有 schema 强制的白名单 —— archiver 在首次分配到该概念时创建目录。

### 保留路径（Reserved paths）

- `_meta/concepts/INDEX.md` —— 所有概念的已编译单行摘要（由 `retrospective` Mode 0 重新生成）
- `_meta/concepts/SYNAPSES-INDEX.md` —— 已编译的反向边索引（由 `archiver` Phase 2 重新生成）
- `_meta/concepts/_tentative/` —— 置信度阈值之下概念的暂存区
- `_meta/concepts/_archive/` —— 已退役的概念（为审计而保留，在激活时被忽略）

---

## YAML Frontmatter Schema

每个概念文件以 YAML frontmatter 开始。所有字段已列出；可选字段已标注。

```yaml
---
concept_id: string                # required, unique across the network
canonical_name: string            # display name (human-readable)
aliases: [string]                 # other surface forms this concept may appear as
domain: string                    # finance | startup | personal | technical | method | relationship | ...
status: enum                      # tentative | confirmed | canonical
permanence: enum                  # identity | skill | fact | transient
activation_count: integer         # how many times referenced across sessions
last_activated: ISO 8601          # timestamp of last activation
created: ISO 8601                 # creation timestamp
outgoing_edges:
  - to: concept_id
    weight: integer               # 1-100, Hebbian-strengthened
    via: [tag]                    # what triggered this connection (free-form tags)
    last_reinforced: ISO 8601
provenance:
  source_sessions: [session_id]   # sessions where evidence appeared
  extracted_by: enum              # archiver | manual | dream
decay_policy: enum                # matches permanence tier (see §5)
---

# Canonical Name

Body content (markdown, optional but encouraged)...

## Evidence / Examples
- [link to source session or decision]

## Related Concepts
- [[other-concept-id]]
```

### 字段约束（Field constraints）

| 字段 | 约束 |
|-------|-----------|
| `concept_id` | 小写，仅连字符，必须以字母起始，最多 64 字符（见 §7） |
| `canonical_name` | 任何人类可读字符串 |
| `aliases` | 零或多个。由 concept-resolver 在映射原始文本到 ID 时使用 |
| `domain` | 必须与概念的父目录匹配 |
| `status` | `tentative` → `confirmed` → `canonical`。此字段不支持降级 —— 降级走 decay log |
| `permanence` | `identity` | `skill` | `fact` | `transient` |
| `activation_count` | 非负整数，活跃期间单调递增 |
| `last_activated` | 由衰减通道用于判定是否 dormant |
| `outgoing_edges.weight` | 上限 100（上限防止强化失控） |
| `decay_policy` | 必须与 `permanence` 一致 —— 见 §5 |

---

## 生命周期（Lifecycle）

```
1. 🌱 Creation（创建） — archiver Phase 2 以 ≥2 证据点从会话中提取概念，创建 tentative 文件
2. 📈 Reinforcement（强化） — 每次会话激活递增 activation_count，更新 last_activated，强化边
3. ✅ Promotion（晋升） — tentative → confirmed（≥3 个独立会话）→ canonical（用户固定 或 ≥10 个独立会话）
4. 📉 Decay（衰减） — archiver 在每次 Adjourn 运行衰减通道（用户决策 #10）
5. 💤 Retirement — last_activated > 90 days + all outgoing edges weight < 1.0 + permanence ≠ identity → move to _meta/concepts/_archive/ (activation_count preserved, never decremented)
6. ↩️ Undo（撤销） — 用户说 "undo recent concept" 或手动删除文件
```

### 创建（Creation）

`archiver` Phase 2（在会话 Adjourn 后运行，在 wiki / SOUL 自动写入之后）：

1. 扫描会话 frame 中的重复名词短语、实体提及、方法名
2. 对每个候选，应用**全部 6 条创建标准**：
   1. **提及频率 ≥ 2 次**（单次提及的事物太过短暂）
   2. **≥ 2 个独立证据点**（不同的 frame、不同的 report、或不同的 decision —— 而非同一句被引用两次）
   3. **身份超越本会话** —— 该候选在未来会话中可能被复用（由 LLM 判断）
   4. **不是个人、价值、特质或流程** —— 人属于 SOUL / user-patterns；价值/特质属于 SOUL；流程属于方法库
   5. **隐私过滤器放行** —— 剥离姓名（公共人物除外）、具体金额/账户/ID、家人/朋友指代、可追溯的日期+地点组合。若剥离后候选变得无意义 → 丢弃（这是一条个人笔记，不是可复用概念）
   6. **Domain 路由成功** —— LLM 从 §File Location Domain partitions 列出的 domain 中选一个（或创建新 domain 目录）。无法路由到任何 domain 的候选还不是一个概念
3. 全部 6 条通过 → 在 `_meta/concepts/_tentative/{domain}/{concept_id}.md` 创建文件
4. 任一标准失败 → 丢弃，记录到 `decay-log.md` 以供日后审计

> 实现现场：`pro/agents/archiver.md` §Phase 2 Mid-Step（Concept Extraction + Hebbian Update）与 `tools/migrate.py` 使用相同的 6 条标准枚举。本规范改动时，两者必须同步更新。

### 晋升（Promotion）

| 从 → 到 | 触发条件 |
|-----------|---------|
| `tentative → confirmed` | 概念在 **≥3 个独立会话**中被激活，文件从 `_tentative/` 移到 `{domain}/` |
| `confirmed → canonical` | 用户手动固定（frontmatter 中 `status: canonical`），或概念已在 **≥10 个独立会话**中被激活 |

晋升记录在 `_meta/cortex/decay-log.md` 中，带时间戳和触发会话。

### 强化（Reinforcement）

每次会话中的激活：
- `activation_count += 1`
- `last_activated = {current ISO timestamp}`
- 对每条边（A → B），若 A 和 B 在同一 frame 中共同激活：`weight += 1`（上限 100），`last_reinforced = today`

### 衰减（Decay）

archiver Phase 2 在每次 Adjourn 运行衰减通道（decay pass）（用户决策 #10）。衰减按 permanence 层级应用：

| Permanence | 衰减行为 | 原因 |
|-----------|-----------------|-----------|
| `identity` | 无衰减 | SOUL 相邻的价值永不褪色 |
| `skill` | 对数衰减至下限 | 技能一旦习得就被保留，很少被遗忘 |
| `fact` | 指数衰减 | 上下文绑定的事实随时间失去相关性 |
| `transient` | 悬崖式衰减至零 | 事件绑定的概念硬到期 |

边权重与概念的 dormancy 一同衰减。当 `weight ≤ 0` 时，边在下次 Adjourn 通道中被移除。

### 退役（Retirement）

退役由 **dormancy + 边权重崩塌**驱动，**而非**通过对 `activation_count` 做减法。`activation_count` 字段在概念整个活跃期**单调非减**（见 §Reinforcement）；退役是由不同信号触发的生命周期迁移：

1. **Dormancy 阈值** —— `last_activated` 早于 **90 天**（在该窗口内没有任何会话重新激活此概念），**且**
2. **边权重崩塌** —— 当前 Adjourn 衰减通道之后，`outgoing_edges` 中每条边的 `weight < 1.0`（即：该概念已与活跃图断连），**且**
3. **Permanence 层级不是 `identity`** —— identity 层概念永不退役（见 §5 衰减表）

当三项条件同时成立时，概念在下次 Adjourn 通道被移至 `_meta/concepts/_archive/{domain}/{concept_id}.md`。已归档概念：
- 仍在 git 历史中（无数据丢失）
- 激活时被 hippocampus 忽略
- 在巡检期间对 AUDITOR 可见
- `activation_count` 以其最终的单调值被保留（供历史审计）

未来若有重新激活（同一主题再次浮现），概念会从 `_archive/` 还原回 `{domain}/`，并从上次中断处继续递增 `activation_count`。

### 撤销（Undo）

两条撤销路径：

1. **手动删除** —— 用户移除文件 → 下次 `archiver` 运行重建 `SYNAPSES-INDEX.md` 并剪除悬空边
2. **口头撤销** —— 用户在会话中说 "undo recent concept" → archiver 下次调用回滚最近的自动写入（与 wiki undo 同模式，参见 `references/wiki-spec.md`）

---

## Hebbian 更新算法（Hebbian Update Algorithm）

在 `archiver` Phase 2 内运行，紧接在 wiki/SOUL 自动写入之后、SYNAPSES-INDEX 重新生成之前。

说明：下面两段算法伪代码保留英文原文，便于与 EN spec、测试和实现逐行对照；本地化仅覆盖解释性文字。

```
1. Extract the set of concepts activated in the session (from frame md files)
2. For each ordered pair (A, B) that co-occurred in at least one frame:
     - Find or create edge A → B in A's outgoing_edges
     - Find or create edge B → A in B's outgoing_edges
     - weight += 1 (capped at 100)
     - last_reinforced = today
3. For each new concept (not in any existing file):
     - 通过 6 条标准检查（跨会话候选 + ≥2 证据点）
     - On pass → create tentative entry with initial frontmatter
     - On fail → log in decay-log.md, do not create
4. For each activated concept (existing file):
     - activation_count += 1
     - last_activated = now
5. Decay pass (see §5 Decay)
     - Apply per-permanence decay curve
     - Remove edges with weight ≤ 0
6. Recompile SYNAPSES-INDEX.md from all concept files
```

Hebbian 更新在单一会话内是幂等的 —— 重新运行通道产生相同结果（共现计数以会话为界，而非以 agent 调用为界）。

---

## 扩散激活规则（Spreading Activation Rules）

由 `hippocampus` 子 agent 在 Pre-Router Cognitive Layer（Step 0.5，见 `devdocs/architecture/cortex-integration.md` §4）使用。扩散激活产出系统认为对当前消息"温热"（warm）的概念列表。

```
Wave 1 — Direct match
  - Concepts whose canonical_name or aliases match the user message
  - No ranking adjustment — these are the seeds

Wave 2 — Strong neighbours
  - For each seed, follow outgoing edges with weight ≥ 3
  - Collect destinations, preserve edge weight for ranking

Wave 3 — Weak neighbours
  - For each seed, follow outgoing edges with weight ≥ 1 and < 3
  - Used only for sub-threshold pre-activation (brainstorm §8.5)
```

三波之后，结果按 `relevance × edge_weight × concept.activation_count` 排序，并限制为**总体 top 5-7 概念**（硬上限 —— 防止认知洪水）。

阈下预激活（Sub-threshold pre-activation）：未进入 top 5-7 的 Wave 3 概念仍以 `salience = 0.5 × edge_weight / 10` 缓存到会话结束。它们不会自行点火，但若后续 frame 强化它们就可能跨过阈值。

---

## 概念 ID 生成（Concept ID Generation）

canonical 概念 ID 是：
- 小写 ASCII 加连字符（例如 `iterative-document-refinement`）
- 必须以字母起始
- 最多 64 字符
- 在概念网络内全局唯一

### 派生 ID（Deriving the ID）

从原始 canonical name 出发，archiver 执行小写化、把非字母数字的串替换为单个连字符、剪掉头尾连字符、截断到 64 字符。示例：

| Canonical name | Concept ID |
|----------------|-----------|
| "Iterative Document Refinement" | `iterative-document-refinement` |
| "Company-A (Holding)" | `company-a-holding` |
| "三省六部" | （不可转写 CJK → 回退到转写或显式 alias，见下文） |

### 冲突解决（Conflict resolution）

若派生 ID 已存在于一个**不同的** canonical concept，archiver 追加 domain 作为后缀：

```
iterative-document-refinement            → existing, method domain
iterative-document-refinement--writing   → new, writing domain
```

（双连字符分隔 domain 后缀，以避免与包含单个连字符的词冲突。）

### CJK 与非拉丁输入（CJK and non-Latin inputs）

当原始 canonical name 没有拉丁表示时，archiver：
1. 若明显则使用短的 Romaji/Pinyin 转写
2. 回退到一个语义英语标签（例如 `cabinet-three-departments` 对应 三省六部），并把原文存作 alias

ID 是技术标识符，不是显示名 —— `canonical_name` 和 `aliases` 携带用户可见的形式。

---

## 隐私（Privacy）

Concept 文件存储**可跨会话复用的知识**，不是个人信息。

| 属于 concepts | 属于其他地方 |
|---------------------|-------------------|
| `mvp-validation-methodology` | 个人姓名 → SOUL / user-patterns（绝不在 concepts） |
| `trust-structure-in-japan` | 特定银行账号 → 绝不存储在任何地方 |
| `pre-mortem-technique` | 家庭成员姓名 → SOUL（带隐私过滤器） |

**LLM 隐私过滤器**（LLM privacy filter，参见 `references/wiki-spec.md`）在任何概念被创建之前运行：
- 去除姓名（除非是与结论直接相关的公众人物）
- 去除具体金额、账号、ID 号
- 去除特定公司名（除非是公共领域的案例研究）
- 去除家庭/朋友引用
- 去除可追溯的日期+地点组合
- 若剥离后概念变得无意义 → 丢弃（它本就不可复用，它是一个私人笔记）

个人信息流入 SOUL.md，而非 concepts。关于个人（同事、家人、朋友）的概念明令禁止 —— 那是 SOUL 的领地（用户决策 #8）。

---

## 从 v1.6.2a 迁移（Migration from v1.6.2a）

v1.7 之前没有 concepts 目录。迁移到 v1.7 仅运行一次，由 `tools/migrate.py` 编排（用户决策 #7）：

1. 扫描 `_meta/journal/` 条目的**最近 3 个月**（有界窗口 —— 更早的材料不触动）
2. 使用与 archiver Hebbian 通道相同的算法提取候选概念
3. 对每个通过 6 条标准检查和隐私过滤器的候选：
   - 在 `_meta/concepts/_tentative/{domain}/{concept_id}.md` 下创建文件
   - 初始 `activation_count` = 该概念出现的独立会话计数（上限 10）
4. 从同一 journal 条目中的共现计算初始 synapse 权重（上限 10）
5. `activation_count ≥ 3` 的概念从 `_tentative/` 移到 `{domain}/`，状态 `status: confirmed`
6. `activation_count ≥ 10` 的概念得到 `status: canonical`
7. 生成首个 `SYNAPSES-INDEX.md` 和 `INDEX.md`
8. 把迁移结果记录到 `_meta/cortex/bootstrap-status.md`

迁移是幂等的 —— 对已迁移的树再次运行不会产生额外文件。

---

## 反模式（Anti-patterns）

这些由规范禁止，必须被 archiver 在写入时拒绝：

1. **手动编辑 `outgoing_edges`** —— archiver 拥有边状态。用户编辑会在下次 Adjourn 被覆盖。要切断连接，删除其中一个概念文件或说 "undo recent concept"。
2. **创建关于个人的概念** —— 那是 SOUL 领地（用户决策 #8）。个人关系属于 SOUL.md；`relationship/` domain 保留给组织和非个人实体。
3. **把单一概念拆分到多个文件** —— 一个概念就是一个文件。若概念太大以至于一个文件无法描述，它实际上是多个需要独立条目和显式边的概念。
4. **手写 `SYNAPSES-INDEX.md`** —— 它是已编译产物，每次 Adjourn 重新生成。手写编辑会被覆盖。
5. **跨 domain 重用 ID 而不加双连字符后缀** —— archiver 强制唯一性；冲突按 §7 规则解决。
6. **在概念正文或证据区存储个人数据** —— 必须运行隐私过滤器；未过滤文本违反规范。

---

## 每个角色如何使用 concepts（How Each Role Uses Concepts）

所有角色在引用 `_meta/concepts/INDEX.md` 之前检查它是否存在。若不存在或为空，该角色在无概念输入的情况下正常运作。

| 角色 | 读取什么 | 如何使用 |
|------|---------------|-----------------|
| **hippocampus** | `_meta/concepts/INDEX.md` + 扩散激活路径上的文件 | 为 GWT 仲裁生成 "warm concepts" 信号 |
| **gwt-arbitrator** | 由 hippocampus 产出的 concept-link 信号 | 将概念信号加权到 salience 标量 |
| **ROUTER** | 包含 warm concepts 的带注释输入 | 更清晰的意图分类 —— 把 warm concepts 作为上下文，而非事实 |
| **Six Domains (Pro)** | 在派遣上下文中传入的概念条目 | 从既有观念出发做分析，而非重新推导 |
| **REVIEWER** | `_meta/concepts/INDEX.md` | 一致性检查 —— 标记新结论与 canonical 概念冲突的情形 |
| **AUDITOR** | `_meta/concepts/` 目录（巡检期间） | 概念健康 —— 陈旧节点、孤立边、隐私违规 |
| **DREAM** | `_meta/concepts/INDEX.md` + `SYNAPSES-INDEX.md` | N3 使用图做跨领域联想；REM 创造性连接 |
| **archiver** | 会话 frames + 既有概念文件 | 在 Phase 2 运行 Hebbian 更新算法 + 衰减通道（写入 `outgoing_edges`、`SYNAPSES-INDEX.md`，并更新 `activation_count`/`last_activated`） |
| **retrospective** | 所有概念文件（Mode 0 期间） | 重新生成 `INDEX.md`（只读；衰减是 archiver 的写入职责，参见 §Decay）。在简报中标记 dormant 概念。 |

---

## 约束（Constraints）

- **一个概念一个文件** —— 拆分被禁止
- **archiver 拥有对 `outgoing_edges` 的写入权** —— 用户编辑会被覆盖
- **个人数据由隐私过滤器排除** —— 关于个人的内容归 SOUL
- **边权重上限 100** —— 强化失控被限制
- **扩散激活限制在 top 5-7** —— 防止认知洪水
- **概念 ID ≤ 64 字符，小写 + 连字符，以字母起始**
- **迁移只读取 `_meta/journal/` 最近 3 个月** —— 更早的材料不触动
- **SYNAPSES-INDEX.md 和 INDEX.md 是已编译产物** —— 绝不手写
- **仅本地 —— 无 Notion sync** —— concepts 保留在 `_meta/` 内（用户决策 #12）

---

## 相关规范（Related Specs）

- `references/cortex-spec.md` —— 总体 Cortex 架构；concepts 是四核心机制之一
- `references/hippocampus-spec.md` —— 扩散激活输出的消费者（Wave 2/3 沿 `outgoing_edges` 前进）
- `references/gwt-spec.md` —— arbitrator 消费来自 concept lookup 的 `canonical_concept`/`emerging_concept` 信号
- `references/session-index-spec.md` —— 会话 frontmatter 跟踪回指概念文件的 `concepts_activated` / `concepts_discovered`
- `references/snapshot-spec.md` —— 同级 `_meta/` 产物；共享 markdown 优先 + 仅本地约束
- `references/method-library-spec.md` —— 方法带 `related_concepts: [concept_id]` 指向此网络
- `references/wiki-spec.md` —— wiki 条目可锚定概念证据；隐私过滤器在那里定义
- `references/soul-spec.md` —— SOUL 边界（个人归那里，不归 concepts）
- `references/eval-history-spec.md` —— AUDITOR 的 `cognitive_annotation_quality` 消费概念图信号
- `pro/agents/archiver.md` —— Phase 2 拥有 Hebbian 更新、衰减通道、SYNAPSES-INDEX 重新生成、tentative 写入
- `pro/agents/retrospective.md` —— Mode 0 重新生成 `INDEX.md` 并标记 dormant 概念
- `devdocs/architecture/cortex-integration.md` —— Step 0.5 Pre-Router Cognitive Layer 上下文

---

> ℹ️ **2026-04-22 更新**：同步 EN R3.2 修复 §Creation 6-criteria / §Retirement / §Conflict
>
> ℹ️ **2026-04-22 补齐**：Lifecycle 代码块 Step 1/2/3/4/6 + §Creation 6-criteria 括注的历史遗漏翻译

> 译注：本文译自英文版 2026-04-22 snapshot；英文为权威源，歧义以英文为准。
