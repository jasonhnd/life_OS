# 第一次上朝：完整流程

这篇展开讲：说完「上朝」到看到晨报之间，系统到底在做什么。

---

## 前置条件

开始之前确认：

1. **Life OS 已装好**。Claude Code / Gemini / Codex 对应命令见 [quickstart.md](quickstart.md) 或 [installation.md](../installation.md)
2. **选好一种主题**。不用提前选 —— 第一次说「上朝」时，系统会根据你用的触发词自动推断或弹出 a-i 选单。触发词和主题对应关系：
   - 说「上朝」→ 自动 zh-classical（三省六部 —— 唐朝专属词）
   - 说「閣議開始」→ 自动 ja-kasumigaseki（霞が関 —— 现代政府专属词）
   - 说「开始 / 开会」→ 检测到中文，弹出 d/e/f
   - 说「はじめる」→ 检测到日语，弹出 g/h/i
   - 说「start / begin」→ 检测到英文，弹出 a/b/c
3. **第二大脑已初始化**。如果是全新安装，系统检测到 second-brain 目录不存在时会跑初始化向导。首次会花一点时间 —— 之后每次上朝都是秒级

---

## 说「上朝」之后发生了什么

系统启动 RETROSPECTIVE subagent 跑 18 步会话准备。你不用记每一步，只需要知道三件事：

1. **一次性全做完**，不是逐步询问你
2. **全程在 background**，你看不见中间过程，只看到最后的晨报
3. **每次都会跑**，哪怕你每天都上朝 —— 这是 HARD RULE，不允许跳步

18 步简化分组：

| 分组 | 在做什么 | 失败会怎样 |
|------|---------|----------|
| 主题 + 目录检测（步 1-3） | 读触发词 / 配置、判断当前目录是 system repo / second-brain / 项目 repo、必要时初始化 second-brain | 目录类型错会写错文件；主题错会输出错语言 |
| 同步 PULL（步 4-7） | 读 config、git health check、从所有后端拉数据、合并 outbox | 拉失败会降级（标记「后端不可用」），不 block |
| 项目绑定 + 版本检查（步 8-9） | 确定本次会话绑定哪个项目 / area、对比本地 version 和 remote | 没绑定会在晨报请你确认 |
| Context 加载（步 10-14） | 读 user-patterns、SOUL、STATUS、当前项目、全局概览 | SOUL 不存在不 block，会显示「Awaiting SOUL」 |
| 战略地图编译（步 15） | 读 strategic-lines + 所有项目的 strategic frontmatter，现场 compile STRATEGIC-MAP.md | 没定义战略线不 block，显示「Strategic Map not initialized」 |
| DREAM 报告（步 16） | 把上次会话的 DREAM 结果（N1-N2 整理 / N3 巩固 / REM 联想 + 10 触发）呈现出来 | 无上次会话就跳过 |
| Wiki 健康检查（步 17） | 重编 wiki/INDEX.md，检测孤儿条目 / 矛盾 | 无 wiki 目录就跳过 |
| 晨报生成（步 18） | 把以上信息 compile 成一份简报 | 必跑 |

跑完，RETROSPECTIVE 把 Pre-Session Preparation 结果交给 ROUTER，ROUTER 给你第一条响应 —— 必须包含这份准备结果（HARD RULE）。

---

## 朝议准备块：每个字段什么意思

晨报顶上有一个固定的「朝议准备」块。字段固定，值会变：

### Session Scope
本次会话绑定的项目 / area。第一次通常是空的，ROUTER 会问你「本次处理哪个项目？」。绑定之后所有读写都限定在这个 scope 内（Session Project Binding HARD RULE）。跨项目决策必须显式标 `[Cross-project decision]`。

为什么要绑定：防止你说「帮我看看这个合同」，系统不知道是哪个项目的合同，读进一堆无关 context。

### Storage
显示当前激活的后端。格式：`GitHub ✓ / Google Drive ✗ / Notion ✓` —— 选中的打勾。读取走优先级（GitHub > GDrive > Notion），写入走全部选中的。某个后端不可用（网络断 / API key 失效）会标 `⚠️ unreachable`，继续用其他的，不 block。

### Sync
Full pull 的结果。典型值：
- `已完成 full pull（3 条 inbox 拉入）` —— 正常
- `Notion 离线，跳过` —— 降级，手机 inbox 这次拉不到
- `outbox 合并：2 个会话，无冲突` —— 有并行会话的情况

### Platform
Claude Code / Gemini CLI / Codex CLI。系统自己检测环境变量和工具集判断。影响的只是编排文件（读 CLAUDE.md / GEMINI.md / AGENTS.md），16 个 agent 的定义完全一样。

### Life OS version
当前装的版本 + 是否有新版。格式：
- `1.6.2a（已是最新）` —— 不用动
- `1.6.2a → 1.6.3（有新版）` —— 会在晨报末尾加一行 update 提示。你说「更新」/「update」就触发 `git pull` 或 `npx skills add`

### Project Status
所有活跃项目的 high-level 状态：数量、上次活动时间、哪个有 pending 决策。从各项目的 `index.md` 和 STATUS.md 读出来。

### Behavior Profile
ADVISOR 最近从 user-patterns.md 读到的行为模式摘要。典型：「最近 5 次决策平均分递减 —— 检查决策疲劳」「过去 30 天连续 4 次 override veto —— 标记」。

---

## SOUL Health Report 块

这个块是 v1.6.2 的新设定，每次上朝固定位置 —— 在朝议准备之后、晨报主体之前。目的是每次都让你看到系统对你的理解模型。

如果是**首次上朝**（SOUL.md 不存在）：

```
🔮 SOUL Health Report
SOUL 档案尚未初始化。
系统将在你每次决策后观察，积累 ≥2 条证据后自动创建低 confidence 维度。
你不需要现在填写。想要提前声明你的核心价值观？说「build SOUL」。
```

**非首次**的四段：

1. **核心档案（confidence ≥ 0.7）**：高置信度的维度 + 趋势箭头。`↗` = 比上次 snapshot 高 ≥0.05 confidence；`↘` = 低 ≥0.05；`→` = 变化在阈值内。特殊状态：`🌟` 最近被提到核心（跨过 0.7）；`⚠️` 被降级；`💤` 30 天未激活；`❗` 最近 3 次决策都在挑战它
2. **新维度待你填写**：ADVISOR 近期自动创建的新条目（confidence 0.3）。「What IS」有值，「What SHOULD BE」留空 —— 需要你来填，你觉得对就填，觉得不准就删
3. **冲突警告**：最近 3 次决策都在挑战某个 core 维度 → `⚠️ SOUL CONFLICT` 提示
4. **休眠维度**：30+ 天无证据增量。可能是它不再重要了，也可能是你最近没面对这个维度的决策 —— 值得思考

趋势箭头怎么算：
- 每次会话结束时，ARCHIVER 在 `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md` 存一份完整快照
- 下次上朝 RETROSPECTIVE 读最新快照 + 当前 SOUL.md 做 diff
- 阈值 ±0.05 confidence。小波动不显示箭头避免噪音

---

## DREAM Auto-Triggers 块

上次退朝时 DREAM REM 阶段触发的 10 类动作的结果，在这里列出来。每条带一个 emoji 前缀：

| 触发类型 | Emoji | 什么情况 |
|---------|------|---------|
| stale commitment | 🚨 | 30 天前说的「我会做 X」到现在没动（regex 匹配「我会 / I will / X する」+ 时间阈值） |
| 决策疲劳 | 😵 | 24 小时内 ≥5 次决策 + 后半段平均分 ≤ 前半段 −2 |
| 重复决策 | 🔄 | 同一主题第 3 次决策（在问「你是不是在逃避承诺？」） |
| 价值观漂移 | 🌊 | 行为连续偏离 stated SOUL value |
| 情绪态决策簇 | 💢 | 短时间内多个决策都在情绪激动时做的 |
| 新项目关系 | 🔗 | DREAM 发现两个项目之间有 flow 但没声明 |
| 跨项目认知未复用 | 📚 | wiki 里有答案但没带入相关项目 |
| wiki 矛盾 | ⚡ | 两条 wiki 互相打架 |
| SOUL 维度休眠 | 💤 | 提醒 30+ 天未激活 |
| 新 wiki 自动写入 | 💡 | 上次会话新增 wiki 条目的提示 |

每一类都有 hard threshold（量化规则）+ soft signal（LLM 定性判断，soft 模式必须过 AUDITOR 审）。硬规则和软信号的具体定义在 `references/dream-spec.md`。

如果上次没触发任何动作，这个块显示：
```
💤 DREAM Auto-Triggers
上次 REM 未发现需要行动的模式。
```

---

## 晨报主体

前面都是背景信息，晨报主体是今天真正要决策的内容：

```
📋 晨报
[theme 的 PM 显示名] 启奏：[N] 件事。

  1. 【高优先】[具体事] —— 来源（比如 "law-firm-partner 的邮件"）
  2. [中优先] [具体事]
  3. [低优先 / 仅 inbox] ...

⚡ 今日建议
🥇 [最该做的那件]
🟢 可以忽略：[正常进行的]
❓ 待定：[需要你现场拍板的]

请指示今日议程。
```

优先级怎么排：
- 时间敏感（合同 deadline / 邮件需回复）排最前
- Strategic map 判定为 critical-path 的项目活动排前
- stale commitment 和 SOUL conflict 警告嵌入相关事项之后
- 纯 inbox 待分类排最后（低认知负担）

---

## 到此为止，接下来你可以做什么

晨报出完，系统在等你输入。几种典型下一步：

### 选一件事让它处理
> 处理第 1 件事 —— 回 law-firm-partner 的邮件

ROUTER 接过来，如果是决策 → 2-3 轮澄清 → 进入完整朝议；如果是执行（起草回复）→ Express 路径直接交给对应部门（这里是 People + Governance）。

### 问个和今天议程无关的事
> 顺便问一下，Japan permanent residency 需要哪些材料

ROUTER 判定为 Express 分析请求（非决策），派 1-3 部门（这里可能是 People + Growth + Governance）给简报，结束。不会启动完整朝议。

### 激活翰林院
> 我有点困惑最近做的事情到底有什么意义

ROUTER 识别抽象思考需求，问「要不要激活翰林院？」。你说「要」→ STRATEGIST 接管，问你目的，推荐 2-3 位思想家，进入对话模式。

### 直接退朝
> 退朝

好的，走 ARCHIVER 4 阶段流程。详见 [quickstart.md](quickstart.md) 的第 5 步。

---

## 第一次会话的几个实际感受

- **18 步听起来多，实际 30-60 秒内跑完**。除了首次初始化 second-brain + 多个后端 PULL 的时候会慢到 2 分钟
- **晨报会有很多 emoji 和块状结构**。这是有意的 —— 每个块都是可被系统自己解析的。熟了之后你会开始只扫特定块（比如每天只看 DREAM Auto-Triggers）
- **ROUTER 不会主动推销功能**。它不会说「你要不要试试 SOUL？」 —— 你说了再做。唯一例外是检测到抽象思考需求时，会问你要不要激活翰林院（这也是 HARD RULE，抓住用户的「深夜 3 点困惑」瞬间）
- **第一次决策会慢**。完整朝议走一遍要 3-5 分钟（六部并行执行 + REVIEWER 两轮）。熟练后你会学会用 Express 走快路径做日常分析，只在真正的大决策时用完整朝议
- **第一次退朝的 DREAM 报告会比较空**。DREAM 需要积累 —— 它看的是近 3 天 + 跨会话模式。用了两周后，REM 开始频繁报 10 类触发里的有价值信号
