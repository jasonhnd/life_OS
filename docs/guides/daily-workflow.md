# 完整一天的用法

这篇带你从早起上朝、到中午处理 inbox、下午做决策、晚上退朝归档——一天里 Life OS 怎么用。

不同于 `your-first-decision.md`（展示单次决策的每一步内部机制），本篇关注**节奏**：什么时候做什么、怎么跨设备、怎么不被打扰。

---

## 一天的骨架

```
07:30  早起 → 上朝 → 看简报 → 决定今天做什么
09:00  工作块 1：推进 🥇 高杠杆事项
11:30  处理 inbox（手机上随手丢进去的念头）
13:00  午饭，查一个小决定走快车道
14:00  工作块 2：开大议（如果有决策要做）
17:00  "早朝"中途 check-in（不做全同步）
19:30  翰林院对话（如果今天有想法要聊）
22:00  退朝 → DREAM 跑完 → 手机看明天简报
```

你不一定每天都有决策。**没有决策的日子，上朝 + 退朝 就够了，中间只有正常工作。**

---

## 07:30 · 上朝

打开 Claude Code / Antigravity / Codex，说：

```
上朝
```

早朝官后台跑 18 步准备，大概 30-60 秒后你看到简报。结构固定，每天都长这样：

```
📋 Pre-Session Preparation:
- 📂 Session Scope: projects/life-os
- 💾 Storage: GitHub(primary) + Notion(sync)
- 🔄 Sync: Pulled 3 changes from Notion
- Platform: Claude Code | Model: opus
- 🏛️ Life OS: v1.6.2a | Latest: v1.6.2a ✅
- Project Status: 活跃开发中，上周合了 3 个 PR
- Behavior Profile: loaded (17 个历史决策)

🌅 早朝简报

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 SOUL Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Current Profile:
   · 决策时对家庭意见的权重 0.6 🟢 ↗ (+1 evidence)
   · 风险偏好 0.72 🟢 → 🌟 newly promoted to core
   · 长期主义 0.81 🟢 →

🌱 New dimensions:
   · 创作时的完美主义门槛 0.3
     What IS: 3 次推迟发布，每次都说"再打磨一轮"
     What SHOULD BE: (awaiting your input)

📈 Trajectory: evidence +3, challenges +1, new +1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💤 DREAM Auto-Triggers (from last session)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Triggered Actions:
   🔄 Resurface: 30 天前你说"我要每天写 500 字"——最近 7 天只写了 2 次
   💡 你在 life-os 项目连续决策 5 次，考虑今天不做大决定

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Today's Focus
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 发布 v1.6.3 changelog: 昨晚代码已 merge，拖延发布会让用户看不到新功能
   Effort: 30 min | Cost of inaction: 用户继续用旧版

🥈 回复昨天的 inbox 3 条:
   - "考虑加 Telegram bot 支持"
   - "某用户反馈 SOUL 写入太激进"
   - "母亲节送什么礼物"

🟢 可以忽略: 三个 GitHub issue 都是问题重复，已有答案

❓ 决策需要:
   - [cross-project] 接 Telegram 集成意味着放慢 Notion 优化，取舍？

🔴 Immediate: 无
🟡 Current: 发布 v1.6.3
💡 建议: 今天不开新议程，消化昨天议政结果

早朝简报就绪，今天做什么？
```

**你读简报的动作**：
1. 先看 SOUL——"完美主义门槛 0.3" 这个新维度让你有点刺痛，记下来晚点补 What SHOULD BE
2. 看 DREAM triggers——"每天 500 字"这个提醒正好打到你，今天要么写要么改诺言
3. Today's Focus 给你明确的 🥇🥈🟢——不用你自己排优先级
4. 最后那个 "今天不开新议程" 的建议，来自 DREAM 的 decision-fatigue 触发器

---

## 09:00 · 工作块 1

你看到🥇是"发布 v1.6.3 changelog"。这不是决策，是执行。直接开工，不用上朝议事。

30 分钟后写完了，你可能会告诉系统：

```
changelog 写完推上去了
```

丞相直接回答（不议事）：

```
🏛️ 丞相

👍 记下了。我更新了 projects/life-os/tasks，这项标记完成。
Follow-through 指数这周到 80%（上周 62%）。
```

**关键**：简单告知的事，丞相直接处理，不调用任何 subagent。这是"直接处理"路径，不消耗深度流程。

---

## 11:30 · 处理 inbox

通常你手机上看 Notion、想到啥就丢进 Inbox 数据库。中午抽 10 分钟整理：

```
看一下今天 inbox 有啥
```

丞相查 Notion，返回：

```
🏛️ 丞相

📬 Notion Inbox (3 条):
1. 考虑加 Telegram bot 支持 — 今早 08:23
2. 某用户反馈 SOUL 写入太激进 — 昨晚 22:11
3. 母亲节送什么礼物 — 昨晚 19:05

要怎么处理？一条一条过？
```

你：`过`

```
🏛️ 丞相

【1/3】"考虑加 Telegram bot 支持"
这条涉及功能决策，建议不在 inbox 流程里处理，
需要开议程（涉及开发优先级）。
→ 转到 projects/life-os/decisions/ 待议 (✓/✗)

【2/3】"某用户反馈 SOUL 写入太激进"
这是用户反馈信号。建议：
→ 创建 task：收集 5 条同类反馈后再考虑改规则 (✓/✗)

【3/3】"母亲节送什么礼物"
这是个人事务。建议：
→ 转到 areas/family/ 作为 task，提前 1 周提醒 (✓/✗)
```

你：`1 转议程，2 OK，3 OK 但提前 2 周提醒`

```
🏛️ 丞相

✅ 完成:
- 1 → projects/life-os/decisions/pending/telegram-bot.md
- 2 → areas/product/tasks/soul-feedback-collect.md
- 3 → areas/family/tasks/mother-day-gift.md（提前 2 周）
Inbox 清空。

注意第 1 条——你上周才决完"专注 Notion 优化"，
现在又想加 Telegram。这是 repeated-decisions 的信号，
下次上议前考虑让谏官先审一下。
```

---

## 13:00 · 午饭时的小问题

吃饭时突然想到一个法律问题：

```
快速分析：在日本设立 NPO 能不能做借贷业务
```

"快速分析" 触发快车道——丞相不问 3 轮，直接派相关部（这里是刑部），结果以 brief report 形式回：

```
🏛️ 丞相 · 快车道启动
→ 刑部

⚖️ 刑部 · 简报

🔎 查了日本贷金业法（令和元年修正版）+ NPO 法人法：
- NPO 法人原则上可从事"特定非営利活動"
- 但贷款业务不在 20 类特定活动中
- 例外：极小规模生活资金贷款可能通过地方自治体特例
- 贷金業登録需要纯資産 500 万以上 + 资格人员

💭 结论：NPO 做借贷在现行法律下没有豁免，
想做必须走普通贷金业登录，NPO 身份不带来便利。

🏃 这是快速分析。要不要开全套议程深挖？
```

你：`不用`。会话结束，这条不写 decisions（不是决策）但因为经过刑部研究，起居郎会在退朝时把它作为 wiki 候选评估：

- 跨项目复用？✅ 以后开业务可能用到
- 不涉及个人？✅ 法律事实
- 零隐私？✅
- 事实型？✅
- ≥2 证据？✅（贷金业法 + NPO 法人法）
- 和现有 wiki 不冲突？✅

**自动写入** `wiki/finance/lending-law-npo.md`，confidence 0.3。你不用管。

---

## 14:00 · 开大议（如果需要）

下午处理早上简报的 ❓："接 Telegram 集成 vs 继续优化 Notion"：

```
我要决定 Telegram 集成的优先级
```

丞相识别跨项目决策，标 ⚠️ Cross-project，读 STRATEGIC-MAP 后澄清：

```
🏛️ 丞相

⚠️ Cross-project. 我读了 STRATEGIC-MAP:
- life-os 在 product-expansion 线上，critical-path
- 加 Telegram 让 Notion 优化延后 3-4 周

你的 driving_force 是"扩大用户量"还是"深化体验"?
SOUL 显示上月倾向后者，但最近 2 次决策偏前者。
```

这一问直击要害——你发现自己被"扩大"念头带着走。2 轮澄清后议程 8 分钟跑完。奏折："先收 Telegram 信号 2 周再议"。

---

## 17:00 · 中途 check-in

下班前想看看今天进度：

```
早朝
```

这是 Review 模式——**不做全同步**，只出简报。快，10 秒：

```
🌅 早朝简报 · 今日

📊 Overview: 执行稳健，决策 1 次无封驳

Area 状态:
  life-os: 🟢 v1.6.3 发布完成
  family: 🟢 母亲节任务已记
  product: 🟢 SOUL feedback task 创建

📈 Decision Dashboard:
  DTR [===-------] 1/day  GREEN
  ACR [========--] 80%   GREEN (上周 62%)
  OFR [======----] 60%   YELLOW

⏰ Pending backfill: 无

🔴 Immediate: 无
🟡 重点: 完美主义门槛那条 SOUL 维度还没填 What SHOULD BE
💡 建议: 今晚退朝前填一下
```

---

## 19:30 · 翰林院对话（可选）

"完美主义门槛" 这个 SOUL 维度让你想起上次没发布 Rust 教程也是这个原因。你想和谁聊聊。

```
我想找个思想家聊聊完美主义的事
```

丞相识别出抽象思考信号，问：

```
🏛️ 丞相

要启动翰林院吗？我看到 SOUL 新增了"创作时的完美主义门槛"维度，
配合你最近 3 次推迟发布的模式，值得深谈。
```

你：`好`

翰林院接管：

```
🎋 翰林院

今天你想探索什么？
```

你：`我总在发布前再打磨一轮，结果错过了 3 次发布窗口`

```
🎋 翰林院

听到了。基于你的 SOUL 中的"长期主义"(0.81) 和新维度
"完美主义门槛"(0.3)——我推荐：

一对一模式：
- 达·芬奇：他的笔记本显示大量未完成作品，可能懂你的心理
- 贾伯斯："Real artists ship." 他会直接戳你
- 完美主义研究：Brené Brown（不在默认列表但可请她出席）

辩论模式：
- 达·芬奇 vs 贾伯斯：完成度 vs 发布节奏

你想要哪种？我也可以一对一贾伯斯，然后你觉得不够再加达·芬奇。
```

你选"先贾伯斯一对一"。翰林院启动一个独立 subagent 扮演贾伯斯，开始对话。15 分钟后你说"够了"。

翰林院做结束仪式：贾伯斯一句 parting word，翰林院写摘要，归档到 `_meta/journal/2026-04-20-strategist-perfectionism.md`。

**不会**进议程（没有评分、没有奏折）。翰林院是思考，不是决策。

---

## 22:00 · 退朝

说 `退朝`。丞相立即调起居郎，自己不插话（硬规矩）。起居郎跑 4 阶段输出 checklist：

```
📝 起居郎 · 归档完成

Phase 1: decisions 1 / tasks 4 / journal ok
Phase 2: 
  Wiki: 1 entry (finance/lending-law-npo.md, 0.3)
  SOUL: "完美主义门槛" +1 evidence
  Strategic: Telegram 候选 → product-expansion
Phase 3 DREAM:
  REM Auto-Triggers:
    #10 Telegram 第 3 次提起 — 下次议前先问是否在逃避 Notion 深耕
    #7 "长期主义" 和 "扩大" 最近 5 次中 3 次互相挑战
Phase 4 Sync: git pushed / Notion by orchestrator

🔄 Notion: 🧠 Status / 📋 Todo 4 items / 📝 Memory / 📬 Inbox synced
```

全程 45 秒。看到 checklist 就可以关电脑。

---

## 跨设备同步到手机

你睡前想在手机上看明天的简报概要。打开 Notion：

- **🧠 Current Status** 页面：显示今天的总结 + 明天 🥇🥈 候选
- **📋 Todo Board**：今天完成的项目打勾了，新创建的 task 都在这
- **📝 Working Memory**：最近 3 次 session 的摘要
- **📬 Inbox**：清空状态

第二天早上，在地铁上你想到一个新想法——直接在手机 Notion Inbox 新建一条："是否考虑加中文宣传页"。

第二天早起说"上朝"，早朝官的 Phase B 会 pull 这条：

```
🔄 Sync: Pulled 1 change from Notion (inbox: "是否考虑加中文宣传页")
```

你的桌面看到的，和手机写的，已经合在一起。

---

## 一天的 CheatSheet

| 时间 | 口令 | 用途 |
|------|------|------|
| 早上 | `上朝` | 全同步 + 简报 |
| 中午 | `看一下 inbox` | 整理手机扔进来的想法 |
| 午饭 | `快速分析：XXX` | 小问题，不上议 |
| 下午 | 直接问问题 | 系统自己判断升堂 or 直接处理 |
| 下班 | `早朝` | 中途简报，快 |
| 晚饭后 | `我想找思想家聊 XXX` | 翰林院 |
| 睡前 | `退朝` | 归档 + DREAM + Notion 推送 |

---

## 什么情况不该上朝

- **单一维度的事实查询**："tax 截止日期是哪天"——直接处理
- **执行动作**："帮我写个 todo"——直接处理
- **情绪发泄**：丞相会先承接情绪、再分离事实。不会强行议事
- **已经决定的事**：你只是想让系统记录，不需要议程

**什么时候该上朝**：
- 涉及钱、关系、时间、不可逆
- 你能说出"A 还是 B"或"要不要 X"
- 你感到纠结本身——不是信息不足，而是维度打架

---

## 节奏建议

- **一天最多一次大议** — decision-fatigue 触发器会提醒
- **每周一次翰林院** — 抽象思考
- **周末一次 Review** — 看 Strategic Map 健康度
- **月末一次 Retrospective** — 全量回顾（场景 #8）

---

## 下一步

- 新手建议先跑 [your-first-decision.md](your-first-decision.md)
- 积累数据后读 [setting-up-your-soul.md](setting-up-your-soul.md)
- 多项目时读 [mapping-your-strategy.md](mapping-your-strategy.md)
