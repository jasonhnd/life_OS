# 读懂 Dream 报告

DREAM 跑完之后，结果写到哪里？什么时候你会看到？这份文档讲清楚整个流程。

## Dream 报告存在哪

每次退朝（adjourn）之后，ARCHIVER Phase 3 跑完 DREAM，写一份报告到：

```
_meta/journal/{date}-dream.md
```

比如今天是 2026-04-20，就会生成 `_meta/journal/2026-04-20-dream.md`。

这个文件**从来不需要你手动读**——RETROSPECTIVE 会在下次 session start 时替你读。

### 如果你想直接看

文件在那儿，你当然可以打开。通常你不需要——简报会把相关内容浮现到前台。但偶尔回顾历史的 dream 报告，可以看出系统在帮你注意什么。

目录里会堆积多个 dream 报告：

```
_meta/journal/
├── 2026-04-15-dream.md
├── 2026-04-17-dream.md
├── 2026-04-20-dream.md
└── ...
```

每天最多一份（如果一天多次 adjourn，只有第一次会触发 DREAM——后续 session 因为 3 天范围内没有足够新内容会 "light sleep"）。

---

## 下次 session 如何浮现

关键角色：**RETROSPECTIVE**（起居郎）。

下次你说 start / 上朝 / 開始 / begin，RETROSPECTIVE 进入 Mode 0（Start Session），在第 16 步读取最新的、未展示过的 dream 报告：

```
Step 16. DREAM REPORT — read latest _meta/journal/*-dream.md (if exists, not yet presented):
    - Include: "💤 Last session the system had a dream: [summary]"
    - Note auto-written SOUL dimensions (awaiting "What SHOULD BE" input, confidence 0.3)
    - Note auto-written Wiki entries (list paths; user can delete any disagreement)
    - Note discarded candidates with reasons
    - Mark as presented
    - Read the triggered_actions YAML block from last dream journal
```

然后把内容放到简报的**固定位置**——在 SOUL Health Report 之后、Strategic Overview 之前。

### 简报里的 DREAM 块长这样

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💤 DREAM Auto-Triggers (from last session)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Triggered Actions (auto-applied):
   [From DREAM action #1: new project relationship]
   · STRATEGIC-MAP updated: [project-A] →(cognition)→ [project-B]

   [From DREAM action #2: behavior-driving_force mismatch]
   · ADVISOR will flag this session: "You said [driving_force] but last 5 sessions focused on..."

   [From DREAM action #4: dormant SOUL dimension]
   · ⚠️ [Dimension] has been dormant 30+ days

   [From DREAM action #6: decision fatigue]
   · 💡 Recommendation: no major decisions today — you made N decisions in last 3 days

   [From DREAM action #8: stale commitments]
   · 🔄 Resurface: 30 days ago you said "I will [X]" — what happened?

   [From DREAM action #10: repeated decisions]
   · 🤔 You've decided [X] 3+ times — is something keeping you from committing?
```

看完之后，这份报告被标记为"已展示"，不会再出现。下一次 session start 会读**更新的**那份。

### 如果没有 DREAM 触发

如果上次 session 的 DREAM 没触发任何动作，简报里会显示：

```
💤 DREAM Auto-Triggers (from last session)

No actions triggered from last session's dream.
```

不是错误——是正常的"浅睡"。

---

## `triggered_actions` YAML 块

Dream 报告的 front matter 里有一个 `triggered_actions` YAML 块，这是 RETROSPECTIVE 机械读取的数据：

```yaml
---
type: journal
journal_type: dream
date: 2026-04-19
scope_files: 27
stages: [N1-N2, N3, REM]
soul_candidates: 1
wiki_candidates: 0
strategic_candidates: 1
triggered_actions:
  - trigger_id: 1
    trigger_name: "new-project-relationship"
    mode: "hard"
    detection:
      hard_signals:
        - "project-alpha decision mentions project-beta as downstream consumer"
        - "new edge detected: alpha →(cognition)→ beta"
      soft_signals: []
    action: "write-strategic-map-candidate"
    surfaces_at: "next-start-session"
    auditor_review: false

  - trigger_id: 6
    trigger_name: "decision-fatigue"
    mode: "soft"
    detection:
      hard_signals: []
      soft_signals:
        - "user said '随便' twice in decision session"
        - "response length dropped from avg 150 chars to 20"
    action: "flag-next-briefing-no-major-decisions-today"
    surfaces_at: "next-start-session"
    auditor_review: true
---
```

字段含义：

| 字段 | 含义 |
|------|------|
| `trigger_id` | 1-10，对应 10 个触发器之一 |
| `trigger_name` | kebab-case 标识名 |
| `mode` | `hard`（量化阈值达成）或 `soft`（LLM 定性信号）|
| `detection.hard_signals` | 硬阈值的量化证据列表 |
| `detection.soft_signals` | LLM 观察到的软信号列表 |
| `action` | 系统自动执行的动作（kebab-case 短语）|
| `surfaces_at` | 在哪里浮现（目前都是 `next-start-session`）|
| `auditor_review` | soft 模式为 `true`（需要 AUDITOR 审核），hard 模式为 `false` |

RETROSPECTIVE 读这个 YAML 块，把每条生成简报里对应的一行。

---

## DREAM Candidates vs Session Candidates

Life OS 里有**两种候选**——搞清楚区别对理解系统很重要。

### Session Candidates（Phase 2 产出）

- 来源：**当前 session** 的材料（summary report、reviewer/advisor 报告、对话摘要）
- 时机：退朝时 ARCHIVER 的 Phase 2 提取
- 去向：满足 6 条标准直接**自动写入** wiki/SOUL.md，不用用户确认
- 置信度：wiki 初始 0.3 或 0.5（看证据数），SOUL 初始 0.3
- 特征：**范围窄**——只看当前 session

Phase 2 的目标：从刚刚结束的这段对话里，抓住**热的、即时的**价值/知识信号。

### DREAM Candidates（Phase 3 产出）

- 来源：**最近 3 天**的所有材料（跨多个 session）
- 时机：退朝时 ARCHIVER 的 Phase 3 跑 DREAM
- 去向：写入 dream 报告，**下次 session start 时** RETROSPECTIVE 浮现给用户
- 反重复：读取 Phase 2 的 manifest，**不重复提议** Phase 2 已经提取的东西
- 特征：**范围宽**——跨 session 看趋势

Phase 3 的目标：从最近几天的累积里，抓住**冷的、累积的**模式信号。

### 对比

| 维度 | Session Candidates | DREAM Candidates |
|------|-------------------|------------------|
| 范围 | 当前 session | 最近 3 天 |
| 执行者 | ARCHIVER Phase 2 | ARCHIVER Phase 3 |
| 写入时机 | 退朝时直接写 | 下次 session 用户确认后写 |
| 用户确认 | 不需要（满足 6 条标准直接写）| 通过下次简报浮现给用户 |
| 反重复 | - | 不重复 Phase 2 已做的 |
| 典型场景 | 今天的决策里学到一个方法 | 最近一周行为和声明的价值在分叉 |

---

## 回退和修正

所有的 DREAM 自动写入都是**可逆的**：

- **SOUL.md 的自动写入**：编辑 / 删除 / 在下次 session 说 "undo recent SOUL"
- **Wiki 条目的自动写入**：删除文件 = 退休 / 下次 session 说 "undo recent wiki"
- **STRATEGIC-MAP 候选**：下次 session 可以拒绝（简报会问你要不要采纳）

系统的哲学是："先替你记，然后你删剩下的"——而不是"问你要不要记"。后者太烦，前者才可持续。

---

## 历史 dream 报告的作用

除了下次 session 浮现一次之外，dream 报告还有两个长期价值：

1. **ADVISOR 的上下文**：ADVISOR 读最近几份 dream 报告，在 pattern update suggestion 里引用
2. **AUDITOR 的巡查**：AUDITOR 做巡查（patrol inspection）时，看多份 dream 是不是在重复同一个问题——可能是系统提醒了但用户没响应

所以即使"已展示"的 dream 报告不会再出现在简报里，它们仍在被系统使用。

不需要手动清理——文件小，堆几个月都不会有问题。如果一定要清理，30 天以上的可以手动归档到 `_meta/journal/_archive/`。

---

## 相关文件

- `_meta/journal/{date}-dream.md`——实际 dream 报告的位置
- `references/dream-spec.md`——权威 spec（Output Format 章节）
- `pro/agents/retrospective.md`——Mode 0 Step 16 的 DREAM 读取逻辑
- `pro/agents/archiver.md`——Phase 3 的 DREAM 写入逻辑
- `docs/user-guide/dream/dream-overview.md`——概览
- `docs/user-guide/dream/10-auto-triggers.md`——10 个触发器细节
