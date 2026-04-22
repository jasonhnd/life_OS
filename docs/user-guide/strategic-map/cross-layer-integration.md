# 跨层集成

Strategic Map 不是孤立系统。它与 SOUL、Wiki、DREAM 一起构成 Life OS 的**端到端认知管线**——每一层都在自己的时间尺度上，合起来形成"既记住你是谁，也记住世界是什么，还能把两者对齐"的完整循环。

## 三条集成线

### 1. Strategic Map × SOUL · driving_force 就是 "SOUL 的哪一面"

`driving_force` 是 Strategic Map 里的核心字段（详见 `strategic-lines.md`），但它本质上**是从 SOUL 派生的**——每条战略线的 driving_force 回答的问题是："我 SOUL 里的哪个维度在驱动这条线？"

### 对齐检查

RETROSPECTIVE Step 15e 做三个交叉验证：

1. **SOUL-strategy 方向对齐**
   - 读 SOUL.md 的所有 confidence ≥0.5 的维度
   - 读每条战略线的 driving_force
   - 检查：是否有 SOUL 维度在任何战略线的 driving_force 里都不出现？

   例：SOUL 说 "family > career" (confidence 0.8)，但 3 条战略线都围绕 career → 标记 **SOUL-strategy 失配**

2. **driving_force 覆盖检查**
   - 如果某战略线的 driving_force 声明"建立家庭关系"，但 SOUL 里家庭维度 confidence < 0.3 → 标记不一致（要么战略线里的表达夸大了，要么 SOUL 还没捕捉到）

3. **价值漂移的跨层反馈**
   - DREAM 的 #7 触发器（value-drift）发现 SOUL 维度在漂移
   - Strategic Map 的战略线 driving_force 是否也应该更新？
   - DREAM 在这种情况下会同时提议 SOUL 修订 + 战略线修订

### REVIEWER 的硬规则

每次做决策时，REVIEWER 必须检查：
- 这个决策所属的战略线，其 driving_force 是否和 SOUL 相关维度一致？
- 如果不一致，REVIEWER 会降分 + 在审议报告里显式标出

这是 **decision-level 的 SOUL × strategy 一致性检查**——不是事后回顾，是决策当下。

### DREAM REM 的跨层检查

DREAM REM 会问：
- 最近 3 天的行为和 SOUL 维度一致吗？
- 如果 SOUL 说 "创造力是核心"（0.7），但最近的战略线都在优化执行效率 → **drift signal**

---

### 2. Strategic Map × Wiki · cognition 流的实际载体是 wiki 条目

战略线里定义了 cognition 流：`project-alpha → (cognition) → project-beta`。这个流的**实际载体**是什么？

答案：**wiki 条目**。

#### 载体对应关系

| Flow 类型 | 载体 |
|-----------|------|
| cognition | wiki/ 下的条目（跨项目复用的结论） |
| resource | 项目内的交付物（docs/code/artifacts） |
| decision | decision 文件 + 下游 index.md 的前提 |
| trust | 关系 journal / 联系人记录 |

cognition 是**唯一由 wiki 承载**的 flow 类型——因为 wiki 的定义就是"跨项目可复用的世界知识"。

#### 流完整性验证

RETROSPECTIVE Step 15e 做的 **wiki × flow** 交叉验证：

对每条 cognition 流 A → B：
- A 所属项目的 domain 在 wiki/ 下有没有条目？
  - 没有 → flow 定义了但没内容可流，标记 **empty flow**
- 那些条目最近 30 天有没有被 B 项目的决策引用？
  - 没有 → flow 意图对了但没兑现，标记 **cold flow**
- B 项目最近 5 个 decision 里，有没有"重新推导 A 已写过的结论"？
  - 有 → B 在浪费时间，标记 **redundant flow**

#### DREAM 的 #5 触发器（cross-project-cognition-unused）

DREAM REM 在 3 天扫描里做同样的检查，但用 wiki/INDEX.md 对最近所有项目的决策，找"本该引用但没引用"的条目。触发之后，下次 DISPATCHER 会把相关 wiki 条目作为"已知前提"**强制注入**给 B 项目的领域——这样下次 B 做决策，wiki 知识不会被忽略。

#### REVIEWER 的 wiki 一致性检查

决策时，REVIEWER 读 wiki/INDEX.md：
- 当前结论和某个高置信度（≥0.5）wiki 条目矛盾？→ 触发 DREAM #3（wiki-contradicted）在后台记录 challenges +1
- 当前结论是某个 wiki 条目的**新证据**？→ 触发 evidence_count +1

Wiki 不是静态的——它在每次决策里都被验证。

---

### 3. Strategic Map × DREAM · REM 用 flow graph 当脚手架

这是最关键的集成。

#### 没有 Strategic Map 时的 REM

DREAM REM 的任务是"发现跨项目连接"。如果没有 Strategic Map：
- REM 的问题是 open-ended："最近的项目之间有什么连接？"
- 没有结构——全靠 LLM 大海捞针
- 常见失败：要么编造牵强连接，要么错过真连接

#### 有 Strategic Map 时的 REM

DREAM REM 有了**脚手架**。扫描时除了 open-ended 提问，还机械检查：

1. **Structural 检查**
   - 定义的 flows 还有效吗？
   - 哪些 flow 变成了 stale（定义但 3 个月没动）？
   - 有没有在最近决策里出现的新关系应该被加到 flow 里？

2. **SOUL × strategy 检查**
   - driving_force 和 SOUL 维度是否持续一致？
   - 哪个 SOUL 维度在所有战略线里都没被 driving_force 覆盖？

3. **Patterns × strategy 检查**
   - `user-patterns.md` 里的行为模式和战略优先级匹配吗？
   - 你在回避某条 critical-path 项目吗？（比如每次轮到它做，就跳去做别的）

4. **Wiki × flows 检查**
   - cognition flow 实际在传输 wiki 知识吗？
   - 哪些 wiki 条目从来没被下游项目引用？

5. **Beyond structure**
   - 哪些连接是 Strategic Map 还没捕捉到的？
   - DREAM 提议新的 flow（用户确认后加入 strategic 字段）

#### REM 的提议回写

DREAM REM 发现的新关系会变成：
- 新的 flow（写入 dream 报告的 Strategic Map Observations，下次 session 让用户确认）
- 新的战略线（如果发现多个项目在服务同一未定义目的）
- 对已有战略线的 driving_force 修订提议

这是 Strategic Map 的**增长机制**——不是一次性设计，是持续演化。

---

## 端到端认知管线（完整图）

```
      USER 做决策
         │
         │ (decision 写入 projects/{project}/decisions/)
         ↓
      REVIEWER ─── 检查 SOUL × driving_force 一致性
         │         检查 wiki 一致性（发现矛盾 → challenges +1）
         │         检查 flow graph（decision 流 veto 下游破坏）
         │
         │ (summary report)
         ↓
      ADVISOR  ─── 检查行为 vs driving_force
                   检查行为 vs SOUL 维度
                   (写入 patterns-delta)
         │
         ↓
      ARCHIVER
         Phase 2 ── 提取当前 session 的 wiki/SOUL 候选（自动写）
         Phase 3 (DREAM) ── 3 天范围扫描：
            N1-N2: 整理
            N3: 提取 Phase 2 遗漏的 wiki/SOUL
            REM: 用 Strategic Map 做脚手架的 5 类检查
                 + 10 个机械触发器
         │
         ↓
      session 结束
         │
         ↓
      下次 session:
      RETROSPECTIVE
         Step 11 ── 读 SOUL snapshot，计算 trend arrows
         Step 15 ── 编译 Strategic Map:
                    - 匹配 6 个健康原型
                    - 盲点检测（5 类）
                    - 交叉验证（SOUL × strategy, wiki × flow）
                    - 生成 🥇🥈🟢❓
         Step 16 ── 读最新 dream 报告，浮现 triggered_actions
         │
         ↓
      briefing 给用户（SOUL Health Report 在顶、DREAM 在次、Strategic Overview 在三）
         │
         ↓
      USER 看到全景，做下一个决策
         │
         ↓
      (循环回开头)
```

这个管线的特征：

1. **三层记忆在不同时间尺度上**：
   - SOUL（关于你）——月级别更新
   - wiki（关于世界）——周级别累积
   - Strategic Map（关于你在世界里怎么走）——每次 session 编译
   - DREAM——每次退朝做 3 天窗口的综合

2. **每一层都是相互验证的**：
   - 行为验证 SOUL（evidence/challenges）
   - 决策验证 wiki（supporting/contradicting）
   - 战略验证两者（driving_force × SOUL × wiki）

3. **系统无法被骗**：
   - 你说你重视健康（SOUL）——但最近决策全在工作（behavior × SOUL）→ DREAM #2 触发
   - 你定了一条 "学习" 战略线（driving_force）——但 6 周没推进 critical-path → Momentum decay + driving-force neglect 盲点
   - 你在 wiki 里写过 "用户访谈要选极端用户"——但新项目又在访谈所有人 → DREAM #5 触发

4. **自动写入 + 可逆修正**：
   - SOUL/wiki 在严格标准下自动写入（不烦你）
   - 你可以编辑 / 删除 / 撤销（不失控）
   - Strategic Map 的结构变化需要用户确认（避免 AI 猜错）

---

## 跨层降级（Graceful degradation）

任何一层缺失，其他层仍然工作：

- SOUL.md 不存在 → 跳过 SOUL × strategy 一致性检查；Strategic Map 仍编译；REVIEWER 不做 SOUL 检查
- wiki/ 不存在 → 跳过 wiki × flow 验证；cognition flow 仍然定义（但没有载体验证）
- `_meta/strategic-lines.md` 不存在 → Strategic Map 整体休眠；简报 fallback 到 Area Status 扁平列表；DREAM REM 退回 open-ended 模式
- 只有 Strategic Map 没有 SOUL → 可以用，但丢失"价值校准"这一维；driving_force 会变成纯组织性的，不是心理性的

这让系统**从 Day 0 可用**——不需要先配置半天。

---

## 相关文件

- `references/strategic-map-spec.md`——Cross-Layer Integration 章节（第 172 行附近）
- `references/soul-spec.md`——SOUL 维度定义
- `references/wiki-spec.md`——wiki 自动写入 6 条标准
- `references/dream-spec.md`——DREAM 三阶段和 10 个触发器
- `pro/agents/retrospective.md`——Step 15e 跨层验证
- `pro/agents/archiver.md`——Phase 3 的 cross-layer checks
- `docs/user-guide/strategic-map/strategic-lines.md`——driving_force 和 SOUL 的关系
- `docs/user-guide/strategic-map/blind-spot-detection.md`——SOUL-strategy 失配作为盲点
- `docs/user-guide/dream/10-auto-triggers.md`——#2, #3, #5, #7 都涉及跨层检查
