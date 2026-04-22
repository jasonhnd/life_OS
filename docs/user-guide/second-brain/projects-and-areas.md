# Projects vs Areas · 分类的临界点

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Life OS 借的是 PARA 模型（Projects / Areas / Resources / Archive）。这篇只讲 Projects 和 Areas — 最难分的那两个。分清楚了，你的会话就有边界；分不清楚，每次决策都要重新思考"这算啥"。

权威源：`references/data-model.md`（Project 和 Area 数据类型）、`docs/second-brain.md`。

---

## 最简单的区别

**Projects 有终点**。可以被完成。完成了就移进 `archive/`。

**Areas 没终点**。永远在。只有"活跃"和"不活跃"两种状态。

---

## 5 个测试问题

不知道某件事是 project 还是 area？问自己：

1. **它有可以勾掉的完成标志吗？** — 有 → project。没有 → area。
2. **它是不是"持续的一部分人生"？** — 是 → area。
3. **完成后会不会归档整个文件夹？** — 会 → project。
4. **这东西会改名吗？** — 不会（它永远叫"家庭"或"健康"）→ area。会（今天叫"找房"，半年后叫"搬家完成"）→ project。
5. **能画出甘特图吗？** — 能（start 到 end 线段）→ project。不能（是一条持续的河流）→ area。

---

## 真实例子

### 明确的 projects

```
projects/
├── buy-tokyo-apartment/       # 有明确成交日期就结束
├── publish-v2/                 # 发布完就结束
├── japan-startup-visa/         # 拿到就结束
├── move-to-tokyo/              # 搬完就结束
├── write-book-draft/           # 写完第一稿就结束
├── run-2026-tokyo-marathon/    # 跑完就结束
```

### 明确的 areas

```
areas/
├── career/        # 职业生涯 — 永远在
├── finance/       # 金融健康 — 永远在
├── health/        # 身体 — 永远在
├── family/        # 家庭 — 永远在
├── learning/      # 学习 — 永远在
├── product/       # 产品（如果你是产品经理）— 永远在
├── creation/      # 创作 — 永远在
├── social/        # 社交网络 — 永远在
├── ops/           # 运维（家 + 工作）— 永远在
├── spirit/        # 精神生活 — 永远在
```

### 边界模糊的情况

**健身**：
- "三个月瘦 5 公斤" = project。
- "保持身体健康" = area (health/)。

**职业**：
- "从工程师转产品经理" = project (career-transition/)。
- "职业发展" = area (career/)。

**家庭**：
- "陪父母出游一次" = project (family-trip-2026/)。
- "家庭关系" = area (family/)。

同一个主题既可以是 area（持续方向）又可以有底下的 project（当前阶段性目标）。Project 的 `area: health` 字段把它们链起来。

---

## 项目 index.md · 必需字段

每个 project 根目录必须有 `index.md`。格式：

```yaml
---
type: project
name: japan-startup-visa
status: active
priority: p1
deadline: 2026-09-30
area: career
last_modified: "2026-04-08T15:30:00+09:00"

# v1.6.0 可选 strategic 字段
strategic:
  line: relocate-japan
  role: critical-path
  flows_to:
    - target: move-to-tokyo
      type: decision
      description: "签证结果决定搬家时间表"
  flows_from:
    - source: finance-runway
      type: resource
      description: "资金储备支撑申请期"
  last_activity: 2026-04-08
  status_reason: "等入管局审核中"
---

# 日本创业签证

## 目标

2026 Q3 前拿到经营管理签证。

## 当前阶段

等待入管局审核。

## 关键里程碑

- ✅ 公司注册（2026-01）
- ✅ 办公室租赁（2026-02）
- ✅ 材料提交（2026-03-15）
- ⏳ 入管局审核
- ⏳ 签证发放

## 关联

- Area: career/
- 上游依赖: finance-runway（资金）
- 下游触发: move-to-tokyo（搬家）
```

### 为什么每个字段重要

| 字段 | 作用 |
|------|------|
| `status` | RETROSPECTIVE 编译 STATUS.md 时的源头 |
| `priority` | ROUTER 在 Global Overview 里排序的依据 |
| `deadline` | AUDITOR 巡查超期项目时用 |
| `area` | 把项目链到大方向 |
| `strategic.*` | STRATEGIC-MAP 编译时用，跨项目依赖图的节点 |
| `last_modified` | 多后端同步冲突解决时用 |

### status 的五个值

| 值 | 含义 |
|----|------|
| `planning` | 想做还没正式开始 |
| `active` | 正在推进 |
| `on-hold` | 暂停（有明确暂停理由） |
| `done` | 完成 — 等待归档到 `archive/` |
| `dropped` | 放弃 — 等待归档到 `archive/` 并标注原因 |

`done` 和 `dropped` 都会被归档，但 wiki 抽取时处理方式不同。`dropped` 的项目会写 "why dropped" 到 wiki 里，帮未来的你不要再掉同一个坑。

---

## 领域 index.md · 更简单

Area 的 index.md 不需要 strategic 字段。例：

```yaml
---
type: area
name: finance
status: active
review_cycle: monthly
last_modified: "2026-04-01"
---

# 金融健康

## 当前方向

- 保持 12 个月 runway
- 投资组合 70% 股票 30% 债券
- 每月追踪支出，控制在 20 万日元以内

## 关联项目

- [[../projects/japan-startup-visa/]]
- [[../projects/buy-tokyo-apartment/]]

## 目标详见 goals.md
```

`review_cycle` 字段告诉 ADVISOR 多久提醒你回顾一次。

---

## Session binding · 限定 scope

每次会话开始必须绑定一个 project 或 area。这是 HARD RULE。

```
上朝后，RETROSPECTIVE 问：
"我们这次关注哪个项目？"

你："japan-startup-visa"

绑定后：
- 所有写入默认去 projects/japan-startup-visa/
- 六部读 context 时读这个项目
- AUDITOR 审查范围限定在此
```

### 为什么必须绑定

没绑定 → 数据乱写。会话中说到 career，ARCHIVER 不知道应该写进 career area 还是 japan-startup-visa project，随便猜一个，数据永远对不上。

### 跨项目决策

有时候决策明显跨项目 — 比如"要不要辞职去创业"同时影响 `career/`、`finance/`、`family/`。这种情况：

1. 还是绑定其中一个（通常是主导的那个）。
2. 决策标题加 "(跨项目决策)"。
3. 决策文件写进 `_meta/decisions/` 而不是 `projects/{project}/decisions/`。
4. 每个相关项目的 index.md 的 strategic 字段 flows_to / flows_from 互相链。

示例：

```
你：要不要辞职 fulltime 做 Life OS

ROUTER：这看起来跨了 career、life-os、finance 三个 scope。
       建议作为跨项目决策，写进 _meta/decisions/。
       你同意吗？

你：同意

[走完 3D6M 流程]

ARCHIVER 写入：
  _meta/decisions/2026-04-08-quit-job-for-lifeos.md
  （而不是 projects/life-os/decisions/）
```

---

## 什么时候开新 project

### 该开

- 明确的完成标志（日期 / 结果 / 可勾掉的目标）。
- 会生产多个决策、多个研究、多个任务。
- 会持续 2 周以上。
- 完成后你想归档它而不是继续。

### 不该开

- 一次性任务（直接进某个 area 的 tasks/）。
- 不确定要不要做（先进 inbox，想清楚再开）。
- 只是"持续关注"某个话题（进 area 的 notes/）。

### 例子

**该开**：
- "拿日本经营管理签证" → `japan-startup-visa/`
- "发布 Life OS v2" → `lifeos-v2-launch/`
- "找搬家公司搬到东京" → `move-to-tokyo/`

**不该开**：
- "今天买牛奶" → `areas/ops/tasks/`
- "学德语" → `areas/learning/notes/`（如果只是隐约想法）→ 或开 `learn-german-a1/`（如果明确目标：考 A1）
- "关注 AI 进展" → `areas/learning/notes/`

---

## 项目归档 · 完成后怎么办

`status: done` 或 `status: dropped` 时：

1. 会话里说"归档 XX 项目"。
2. ARCHIVER 把整个 `projects/{name}/` 目录移到 `archive/{YYYY}/{name}/`。
3. DREAM 扫描整个项目材料，抽 wiki 条目。
4. STATUS.md 重编译，不再出现这个项目。

归档后的项目数据**不会消失** — 在 `archive/` 里永远可查。但它不再占 RETROSPECTIVE 的注意力，不再出现在 Global Overview，不再干扰新决策。

这是系统"减负"的机制。不归档的项目会让你每次会话都被陈年往事拖住。

---

## 核心心态

Project 是流星，Area 是恒星。

流星有开始、有轨迹、有结束。结束后烧尽，留下陨石坑当纪念（wiki 条目）。

恒星一直在。你可以观察它、靠它导航、偶尔升级它 — 但它不会"结束"。

把所有东西硬塞成 project 会让 archive 爆炸。把所有东西硬塞成 area 会让当前焦点模糊。

分清楚。
