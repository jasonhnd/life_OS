# Eval 系统总览

Life OS 的 eval 系统用来回答一个很实在的问题：**我改了系统之后，它还正确运行吗？**

不是跑性能基准，不是刷分。是用固定的剧本测系统的输出质量——Router 该不该升格、Planner 该不该全开六部、Reviewer 该不该否决、Auditor 该不该抓到 face-saving 分数、Archiver 该不该往 wiki 里写东西。

---

## 为什么要做 eval

Life OS 不是一个纯粹的代码库。它的核心产品是 23 个 subagent 相互交互的行为，而行为本身是 LLM 给的——换句话说，**系统质量不是跑一遍单元测试就能验的**。

三个具体风险：

1. **改了某个 agent 的 prompt，其他 agent 悄悄退化**。比如你把 REVIEWER 的 checklist 从 8 条改成 6 条，以为只影响审议，但实际上 AUDITOR 靠那 8 条做召回率计算，你改完之后 AUDITOR 在「互相护短」而你不知道。
2. **新增 HARD RULE 之后没人检查是否被遵守**。SKILL.md 里写了 33 条 HARD RULE，改代码的时候加一条容易，但加完之后有没有被 ROUTER / PLANNER / REVIEWER 实际执行，要测才知道。
3. **跨版本的回归**。1.6.2 能跑通的场景，1.7.0 是不是还能跑通？这个问题人工点开 10 次 session 去看不现实，必须脚本化。

eval 系统就是解决这三个。

---

## 目录结构

```
evals/
├── README.md                       # 英文入口（公开版）
├── run-eval.sh                     # 自动测试脚本
├── scenarios/                      # 固定测试场景
│   ├── resign-startup.md           # 辞职创业（全六部）
│   ├── large-purchase.md           # 大额消费（FINANCE + EXECUTION + GOVERNANCE）
│   ├── relationship.md             # 人际关系（PEOPLE + INFRA + GOVERNANCE + GROWTH）
│   ├── council-debate.md           # 配偶随迁（触发 COUNCIL 辩论）
│   ├── fengbo-loop.md              # 封驳循环（Reviewer 必须否决）
│   └── router-triage.md            # Router 分流边界（3 条消息）
├── rubrics/                        # 评分准则
│   ├── agent-output-quality.md     # agent 输出质量（0-2 分维度）
│   └── orchestrator-compliance.md  # 流程合规性（14 项 checklist）
└── outputs/                        # 测试输出（gitignored）
    └── {scenario}_{YYYYMMDD_HHMMSS}.md
```

`scenarios/` 和 `rubrics/` 是两个正交的轴：**scenarios 定义输入**，**rubrics 定义用什么标准打分**。一个场景跑完可以用多份 rubrics 评——同一份输出，可以既看 agent 输出质量又看流程合规性。

---

## 手动测试 vs 自动测试

两种模式都保留，各有用处。

### 手动测试

装完 life-os skill 之后，直接把 `scenarios/{name}.md` 里 `## User Message` 那个 code block 的内容粘进 Claude Code / Gemini CLI / Codex CLI 的对话框，看全流程输出。

**用途**：

- 新增场景时，先手动跑一遍确认设计意图对齐
- 调试流程 bug，比如为什么 COUNCIL 没触发
- 人工感受输出「像不像自己想要的」——rubrics 测不出的审美问题

### 自动测试

```bash
./evals/run-eval.sh          # 跑所有场景
./evals/run-eval.sh resign-startup   # 只跑一个
```

脚本用 `claude -p`（headless mode）逐个跑场景，输出写到 `evals/outputs/{name}_{timestamp}.md`。

**用途**：

- 版本发布前做回归
- CI 里的 pre-merge gate
- 快速比对「改动前 vs 改动后」同一场景的行为差异

详见 [运行 eval 套件](running-evals.md)。

---

## 9 个评估维度

每个场景跑完，按这 9 个维度对照输出找问题。不是每个维度都适用于每个场景——比如 `router-triage.md` 不触发六部，就不用看「领域选择」。

### 1. 格式合规

每个 agent 有自己的输出格式（比如 FINANCE 必须给 「分数 / 分析 / 建议」三段，REVIEWER 必须按 8 项 checklist 逐条过）。

**失败信号**：agent 说「我综合判断分数是 6」但没给 checklist 逐条。

**怎么测**：正则扫输出里是否包含必要的 section header。

### 2. 分数分布

六部评分 0-10，全部落在 7-8 就是**面子分**——意味着 agent 在互相给台阶，没在真做判断。

**失败信号**：6 个 domain 分数标准差 < 1.0，或者 ≥7 的比例 > 80%。

**怎么测**：AUDITOR 应该主动标记，但 eval 阶段可以把所有场景跑完后脚本统计一次分数分布。

### 3. 门下省（REVIEWER）实质性

REVIEWER 的设计初衷是**封驳**。每次都批准，就是橡皮图章。

**失败信号**：连续 N 次 Summary Report 里 REVIEWER 都说「通过」，没有一次「修正后通过」或「否决」。

**怎么测**：`fengbo-loop.md` 场景专门设计来触发否决（3-4 个月 runway + 情绪驱动 + 用户说「别劝」），REVIEWER 必须否决。如果没否决 → 失败。

### 4. 信息隔离

HARD RULE：PLANNER 看不到 ROUTER 的推理、REVIEWER 看不到 PLANNER 的推理、每个 DOMAIN 看不到其他 domain 的分数。

**失败信号**：PLANNER 的输出里出现「ROUTER 觉得 ...」；FINANCE 的输出里出现「参考 EXECUTION 的评分 ...」。

**怎么测**：字符串搜。`rubrics/orchestrator-compliance.md` 的 Information Isolation Verification 表格给了具体搜索词。

### 5. 可执行性

六部给的 action items 必须具体到能直接做。「考虑一下」「好好想想」是 0 分。

**失败信号**：action 里有「think about ...」、「consider ...」、「reflect on ...」。

**怎么测**：rubrics 的 "Recommendation actionability" 维度（0-2 分）人工打分。

### 6. 一致性

同一场景多跑几次，**核心结论**应该稳定。不要求每次输出一字不差，但该否决的永远否决、该触发 COUNCIL 的永远触发。

**失败信号**：同一场景跑 3 次，有 1 次 REVIEWER 批准了本该否决的 plan。

**怎么测**：批量跑 3-5 次同一场景，diff 核心决策点。

### 7. 快车道（Express）路由

不是每条消息都要升格到全朝会议。「帮我翻译这句日语」就该直接翻，「我睡眠不好」就该直接给建议 + 最多 1 个 follow-up。

**失败信号**：`router-triage.md` 的 Message 1（翻译）或 Message 3（睡眠）被升格到全部六部。

**怎么测**：检查 ROUTER 的输出，不应出现「呈堂」/「閣議」/「Escalate」等升格词。

### 8. 领域选择

Router / Planner 应该根据场景选对 domain，不是每次都 6 个全开。

**失败信号**：`large-purchase.md`（买电脑）触发了全六部——这场景不涉及人际、学习、健康，开 FINANCE + EXECUTION + GOVERNANCE 就够了。

**怎么测**：对照 scenario 的 "Expected Behavior" 列出来的推荐 domain 数，看实际激活的 domain 是不是匹配。

### 9. Wiki 萃取

Adjourn 时 ARCHIVER 必须按 6 条准则 + Privacy Filter 自动写 wiki。

**失败信号**：

- 用户说过「上次我 XYZ 的决策教训是 ABC」这种跨项目可复用的结论，没被写进 wiki
- 或者写进 wiki 的条目里有具体姓名 / 具体金额 / 具体公司名（Privacy Filter 失效）
- 或者写了一堆但都是废话（「保持冷静」「多角度思考」）

**怎么测**：Adjourn 之后人工检查 `wiki/{domain}/*.md` 新增的文件。自动化这个很难，短期靠人工。

---

## 接下来读什么

- [运行 eval 套件](running-evals.md) — 怎么跑脚本、怎么读输出、怎么接 CI
- [写新 eval 场景](writing-new-scenarios.md) — frontmatter 格式、user message 写法、Expected Behavior 该怎么列

从 Hermes 调研学到的一条：**具体的规则比抽象的原则有用**。eval 系统最大的价值不是跑分，是逼我们把「什么算好的输出」写成可检查的条目。
