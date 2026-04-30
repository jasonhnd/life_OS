---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# 工作流状态机

Life OS 有两套严格的状态机: **主决策状态机**(Step 0-10)和**退朝状态机**(Adjourn)。任何违反合法转换的行为都是 process violation, AUDITOR 必须标记。

源: `pro/CLAUDE.md` 的 "Workflow State Machine" 和 "Adjourn State Machine" 章节。

---

## 主决策状态机

### 合法转换表

| 当前状态 | 合法下一状态 | 不能跳到 |
|---------|-----------|---------|
| Pre-Session Preparation | ROUTER Triage | 任何其他状态 |
| ROUTER Triage | PLANNER / Handle Directly / Express Analysis / STRATEGIST / Review | Six Domains (除非通过 Express) |
| Express Analysis | Domain Execution → Brief Report → (结束 or 升格 PLANNER) | REVIEWER / AUDITOR / ADVISOR |
| PLANNER Planning | REVIEWER Review | DISPATCHER / Six Domains |
| REVIEWER Review | DISPATCHER / Veto 回 PLANNER | Six Domains (必须经过 Dispatch) |
| DISPATCHER Dispatch | Six Domains Execution | Summary Report (必须先执行) |
| Six Domains Execution | REVIEWER Final Review | Summary Report (必须先审) |
| REVIEWER Final Review | Summary Report / COUNCIL | ARCHIVER (必须先出 Summary Report) |
| Summary Report | AUDITOR | ARCHIVER (必须先跑 AUDITOR) |
| AUDITOR | ADVISOR | ARCHIVER (必须先跑 ADVISOR) |
| ADVISOR | ARCHIVER | — |

### 非法转换的常见表现

| 非法转换 | 具体表现 |
|---------|---------|
| ROUTER → Six Domains | 跳过 PLANNER 直接让领域做事 (Express 路径除外) |
| PLANNER → Six Domains | 跳过 REVIEWER |
| REVIEWER → Six Domains | 跳过 DISPATCHER |
| Six Domains → Summary Report | 跳过 REVIEWER Final Review |
| 任何状态 → ARCHIVER | 跳过 Summary Report / AUDITOR / ADVISOR 中的任何一个 |
| Express → REVIEWER/AUDITOR | Express 路径本来就不应触发这些, 触发了就是流程混乱 |

### 特殊: Veto Correction Loop

REVIEWER 的 Veto 不是状态跳跃, 而是在 PLANNER ↔ REVIEWER 之间循环。

- Max 2 次循环 (反馈回 PLANNER → 改 → 再送 REVIEWER)
- 第 3 次 REVIEWER 必须返回 Approved 或 Conditionally Approved
- 如果 REVIEWER 第 3 次仍然 Veto → 流程错误, AUDITOR 标记

---

## 退朝状态机 (Adjourn)

**退朝是独立状态机**, 不是主流程的一个 step。用户说退朝后, 无论主决策流程在哪里, 都进入这套独立状态机, 端到端强制执行。

### 合法转换表

| 当前状态 | 合法下一状态 | 不能做 |
|---------|-----------|-------|
| Adjourn Triggered | Launch(archiver) as subagent | 任何主上下文的 Phase 执行、问用户候选、部分执行 |
| archiver Running | archiver 输出 Completion Checklist | 无 checklist 就结束、把 checklist 分散到多条消息 |
| Checklist Output | Session End | 接受含有占位符的 checklist ("TBD", 空白) |
| Session End | — | — |

### 合法转换 (3 条)

1. Adjourn Triggered → archiver Running (通过 subagent launch)
2. archiver Running → Checklist Output (archiver 在**单次调用**内跑完 4 个 Phase)
3. Checklist Output → Session End

### 非法转换 (都是违规)

| 非法行为 | 描述 |
|---------|------|
| Adjourn Triggered → 主上下文执行 Phase 2 | ROUTER 说「让我先看看要保存什么候选」, 然后列候选 |
| Adjourn Triggered → 分裂流程 | ROUTER 说「你告诉我要保存哪些, 然后我启动 subagent 跑 DREAM/sync」 |
| archiver Running → 部分退出 | archiver 跑完 Phase 2 就返回, Phase 3 DREAM 和 Phase 4 Sync 没做 |
| Checklist Output → Session End | Checklist 里有「TBD」、空值、占位符 |
| archiver phases 之间 ROUTER 插话 | ROUTER 在 Phase 1 和 Phase 2 之间问用户问题 |

### 强制机制

**AUDITOR 在会话结束后立即运行**。检测到任何非法转换:
1. 写入本次流程审计报告
2. 记录到 `user-patterns.md`
3. 下次会话开始时 ADVISOR 会把它作为 behavioral pattern 标记
4. 「累犯」行为会累加, 被用户看到

---

## AUDITOR 捕获违规的机制

### Decision Review Mode (流程后自动)

每次完整决策流程结束后, AUDITOR 收到**完整工作流记录**作为输入。检测项:

| 违规类型 | 检测信号 |
|---------|---------|
| 跳步 | 工作流记录里没有某个必须步骤 (如没 REVIEWER Final Review 就到 Summary Report) |
| 面子分 | 全部领域评分在 7-8 范围, 无低分, 无高分 |
| 分析-评分不一致 | 报告文字说「严重风险」但评分 ≥6 |
| 走过场的 REVIEWER | 多次决策, REVIEWER 从不 Veto, 审议深度浅 |
| 退朝违规 | 见上节「退朝状态机」的非法转换 |
| 信息泄漏 | agent 收到不该收到的信息 (如 domain 收到其他 domain 的报告) |

### 输出格式

```
🔱 [theme: auditor] · Agent Performance Review

📊 Overall Assessment: [一句话]
👍 Good Performance: [角色] — [原因]
👎 Poor Performance: [角色] — [原因]
⚠️ Process Issues: [如有]
🎯 Improvement Suggestions: [下次该注意什么]
```

如果检测到**严重违规** (退朝没跑完 / 跳了 REVIEWER), 在 Process Issues 里必须明确标出。

---

## 状态机实现原理

### 状态不是持久化变量, 是流程秩序

Life OS 没有「状态机引擎」这种东西。状态转换靠的是:

1. **编排协议文件** (`pro/CLAUDE.md`) 里**明确规定**每步的前置条件
2. **agent 文件** 里明确该 agent 只接受什么输入 (信息隔离)
3. **AUDITOR 自动巡查** 工作流记录, 回溯检查

### 为什么这样设计

- **简单**: 全部逻辑在 markdown 里, 可读, 不需要运行时引擎
- **可变**: 改状态机 = 改 markdown, 不需要重启服务
- **可审计**: 每次流程有完整记录, AUDITOR 任何时候都能回头看
- **失败兜底**: LLM 可能偶尔跳步, 但 AUDITOR 会发现, 用户会看到, 下次不会再犯

### 风险

- LLM 可能**连续**跳步 (例如连续 3 次会话都跳 REVIEWER)
- 如果用户没注意 AUDITOR 的标记, 违规不会被纠正
- 应对: ADVISOR 把违规记入 `user-patterns.md`, 会在下次会话开始时被 RETROSPECTIVE 读出来并在晨报展示

---

## 调试流程 bug 时的速查

**用户说「不对, 流程走错了」时, 查这几个地方**:

1. 看 Summary Report 的 Audit Log 块 — 记录各阶段是否跑了
2. 看 AUDITOR 报告 — 有没有标记 Process Issues
3. 看 `_meta/outbox/{session_id}/manifest.md` — 记录了本次 session 的产出计数
4. 看 `user-patterns.md` — 有没有累积的违规模式
5. 对照本文件的合法转换表, 看当前状态跳到的下一状态是不是合法的

**如果是退朝相关 bug**:
1. 检查 ARCHIVER 是不是作为 subagent 启动 (不是主上下文执行)
2. 检查 Completion Checklist 是否完整
3. 检查 Phase 3 DREAM 和 Phase 4 Sync 是否都跑了
4. 检查 Notion Sync 是否由 orchestrator 在 archiver 之后做 (不是 archiver 自己做)
