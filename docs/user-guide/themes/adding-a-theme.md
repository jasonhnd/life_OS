# 添加新主题 · 不改引擎就能加

Life OS 的主题系统**完全数据驱动**——加一个新主题只需要加一个 markdown 文件。引擎代码一行不用改。

本文教你怎么造一个。

## 核心原则

- **只改 `themes/*.md` 一个文件**
- **16 个 engine ID 必须完整映射**（少一个会有 agent 无显示名）
- **6 个 domain 必须完整映射**
- **触发词必须至少有一套**（否则无法启动会话）

## 必填字段清单

每个主题文件**必须**包含以下章节：

| 章节 | 必填 | 作用 |
|------|------|------|
| `# Theme: [名字]` | ✅ | 标题 |
| 一段开头描述 | ✅ | 文化根和推荐场景，1-2 句 |
| `## Language` | ✅ | **HARD RULE**：定义输出语言 |
| `## Tone` | ✅ | 语气定义（一两句话） |
| `## Role Mapping` | ✅ | 16 个 engine ID 映射 |
| `## Domain Mapping` | ✅ | 6 个 domain 映射 |
| `## Summary Report` | ✅ | 总结报告的名字和格式 |
| `## Session Commands` | ✅ | 触发词表 |
| `## Cultural Context (for AI persona)` | ✅ | 给 AI 的文化背景提示 |

## Engine ID 完整列表

16 个 engine ID 都要给出**显示名 + emoji + 输出标题**。以下是全表，照这个填：

| Engine ID | 说明 | 需填 Display Name | 需填 Emoji | 需填 Output Title |
|-----------|------|------------------|-----------|-------------------|
| `router` | 接话的角色 | ✅ | ✅ | — |
| `planner` | 起草方案的角色 | ✅ | ✅ | ✅（如"規劃文書"） |
| `reviewer` | 审查且有否决权的角色 | ✅ | ✅ | — |
| `dispatcher` | 派发任务的角色 | ✅ | ✅ | ✅ |
| `finance` | 管钱 | ✅ | ✅ | ✅ |
| `people` | 管人际关系 | ✅ | ✅ | ✅ |
| `growth` | 管学习/成长 | ✅ | ✅ | ✅ |
| `execution` | 管行动/执行 | ✅ | ✅ | ✅ |
| `governance` | 管风控/合规 | ✅ | ✅ | ✅ |
| `infra` | 管健康/基建 | ✅ | ✅ | ✅ |
| `auditor` | 独立审计 | ✅ | ✅ | ✅ |
| `advisor` | 行为审查 / 直言者 | ✅ | ✅ | ✅ |
| `council` | 跨领域辩论会 | ✅ | ✅ | — |
| `retrospective` | 会话开场角色 | ✅ | ✅ | ✅ |
| `archiver` | 归档角色 | ✅ | ✅ | — |
| `strategist` | 人类智慧殿堂 | ✅ | ✅ | — |

**部分没有"Output Title"的角色**（router / reviewer / council / archiver / strategist）是因为它们不直接输出有标题的报告。但 display name 和 emoji 仍然必填。

## Domain Mapping

6 个 engine domain 都要映射：

| Engine Domain | 领域本质 | 需填 Display Name |
|--------------|---------|------------------|
| `PEOPLE` | 人际关系 | ✅ |
| `FINANCE` | 财务 | ✅ |
| `GROWTH` | 学习与成长 | ✅ |
| `EXECUTION` | 行动与执行 | ✅ |
| `GOVERNANCE` | 规则与风控 | ✅ |
| `INFRA` | 基建与健康 | ✅ |

## 最小可用骨架

复制这个，改掉方括号里的内容：

```markdown
# Theme: [你的主题名]

[1-2 句话说明文化根和适用场景。例如："基于 EU Parliament 体制。"]

## Language

[English / Chinese / Japanese / Korean / ...]. ALL output in this session MUST be in [该语言] after this theme is selected. HARD RULE.

## Tone

[语气定义，1-2 句。例如："Parliamentary but plain. No bureaucratic jargon."]

## Role Mapping

| Engine ID | Display Name | Emoji | Output Title |
|-----------|-------------|-------|-------------|
| router | [...] | [...] | — |
| planner | [...] | [...] | [...] |
| reviewer | [...] | [...] | — |
| dispatcher | [...] | [...] | [...] |
| finance | [...] | [...] | [...] |
| people | [...] | [...] | [...] |
| growth | [...] | [...] | [...] |
| execution | [...] | [...] | [...] |
| governance | [...] | [...] | [...] |
| infra | [...] | [...] | [...] |
| auditor | [...] | [...] | [...] |
| advisor | [...] | [...] | [...] |
| council | [...] | [...] | — |
| retrospective | [...] | [...] | [...] |
| archiver | [...] | [...] | — |
| strategist | [...] | [...] | — |

## Domain Mapping

| Engine Domain | Display Name |
|--------------|-------------|
| PEOPLE | [...] |
| FINANCE | [...] |
| GROWTH | [...] |
| EXECUTION | [...] |
| GOVERNANCE | [...] |
| INFRA | [...] |

## Summary Report

name: [...]
format: "📋 [...]：[Subject]"

## Session Commands

| Action | Trigger Words |
|--------|-------------|
| Start Session | "[...]"  / "start" |
| Review | "[...]" / "review" |
| Adjourn | "[...]" / "adjourn" / "done" |
| Quick Analysis | "[...]" / "quick" |
| Debate | "[...]" / "debate" |
| Update | "[...]" / "update" |
| Switch Theme | "[...]" / "switch theme" |

## Cultural Context (for AI persona)

[一段文字，告诉 AI 这个文化的重要背景、这些角色是做什么的、为什么选这个制度。长度：1-2 段。这是 AI 扮演角色时的"导演笔记"。]
```

## 例子 1 · EU Parliament（英语）

```markdown
# Theme: EU Parliament (English)

Based on the European Parliament and Commission structure. Multi-stakeholder governance where the Commission proposes, Parliament reviews, and Member State ministers execute. 

## Language

English. ALL output in this session MUST be in English after this theme is selected. HARD RULE.

## Tone

Parliamentary but plain. Direct, evidence-based, respectful of multiple viewpoints. No EU jargon.

## Role Mapping

| Engine ID | Display Name | Emoji | Output Title |
|-----------|-------------|-------|-------------|
| router | President of the Commission | 🏛️ | — |
| planner | College of Commissioners | 📜 | Commission Proposal |
| reviewer | European Parliament | 🔍 | — |
| dispatcher | Council of the EU | 📨 | Council Directive |
| finance | DG ECFIN | 💰 | Economic & Financial Assessment |
| people | DG JUST | 👥 | Justice & Consumers Assessment |
| growth | DG EAC | 📖 | Education & Culture Assessment |
| execution | DG DEFIS | ⚔️ | Defence Industry & Space Assessment |
| governance | DG JUST (compliance) | ⚖️ | Compliance Assessment |
| infra | DG MOVE | 🏗️ | Mobility & Transport Assessment |
| auditor | European Court of Auditors | 🔱 | Audit Report |
| advisor | European Council President | 💬 | Strategic Advisory |
| council | Plenary Session | 🏛️ | — |
| retrospective | Monday Briefing | 🌅 | Weekly Briefing |
| archiver | Official Journal | 📝 | — |
| strategist | European University Institute | 🎋 | — |

## Domain Mapping

| Engine Domain | Display Name |
|--------------|-------------|
| PEOPLE | DG JUST · Citizens & Relations |
| FINANCE | DG ECFIN · Economy & Budget |
| GROWTH | DG EAC · Education & Culture |
| EXECUTION | DG DEFIS · Action & Operations |
| GOVERNANCE | DG JUST · Compliance & Rule of Law |
| INFRA | DG MOVE · Infrastructure & Mobility |

## Summary Report

name: Commission Decision
format: "📋 Commission Decision: [Subject]"

## Session Commands

| Action | Trigger Words |
|--------|-------------|
| Start Session | "convene plenary" / "start" / "begin" |
| Review | "plenary review" / "review" |
| Adjourn | "adjourn session" / "done" / "end" |
| Quick Analysis | "quick" |
| Debate | "plenary debate" / "debate" |
| Update | "update" |
| Switch Theme | "switch theme" |

## Cultural Context (for AI persona)

The Commission President proposes EU-wide policy — the central initiating role. The European Parliament has co-decision power — it can reject Commission proposals with a majority vote. The Council of the EU (ministers of Member States) executes and coordinates national implementation. The European Court of Auditors is treaty-established and independent of the Commission, reporting directly to Parliament.

Historical note: The EU structure is deliberately slow because it requires multi-stakeholder consent. This maps well to personal decisions where you want to hear multiple perspectives before acting — your "Commission" proposes, your "Parliament" can veto, your "Council" executes across life domains.
```

## 例子 2 · Japanese Shogunate（日语）

```markdown
# Theme: 幕府 (Tokugawa Shogunate)

江戸時代（1603-1868）の徳川幕府体制に基づく。将軍の下に老中・若年寄・大目付・勘定奉行——二百六十年の平和を支えた精緻な官僚機構。

## Language

Japanese (日本語). ALL output in this session MUST be in Japanese after this theme is selected. HARD RULE.

## Tone

武家の気風。簡潔、毅然、無駄な言葉なし。現代語で書くが、武士の骨を持つ。

## Role Mapping

| Engine ID | Display Name | Emoji | Output Title |
|-----------|-------------|-------|-------------|
| router | 将軍 | 🏛️ | — |
| planner | 老中 | 📜 | 老中策定書 |
| reviewer | 大目付 | 🔍 | — |
| dispatcher | 若年寄 | 📨 | 若年寄指示書 |
| finance | 勘定奉行 | 💰 | 勘定奉行評定 |
| people | 外国奉行 | 👥 | 外国奉行評定 |
| growth | 学問所 | 📖 | 学問所評定 |
| execution | 番方 | ⚔️ | 番方評定 |
| governance | 寺社奉行 | ⚖️ | 寺社奉行評定 |
| infra | 作事奉行 | 🏗️ | 作事奉行評定 |
| auditor | 目付 | 🔱 | 目付報告 |
| advisor | 御側御用取次 | 💬 | 御用取次進言 |
| council | 評定所 | 🏛️ | — |
| retrospective | 朝の御目見得 | 🌅 | 朝会報告 |
| archiver | 御右筆 | 📝 | — |
| strategist | 昌平坂学問所 | 🎋 | — |

## Domain Mapping

| Engine Domain | Display Name |
|--------------|-------------|
| PEOPLE | 外国奉行 · 人間関係 |
| FINANCE | 勘定奉行 · 財政 |
| GROWTH | 学問所 · 学び |
| EXECUTION | 番方 · 行動 |
| GOVERNANCE | 寺社奉行 · 秩序と戒律 |
| INFRA | 作事奉行 · 建築と基盤 |

## Summary Report

name: 御触書
format: "📋 御触書：[題目]"

## Session Commands

| Action | Trigger Words |
|--------|-------------|
| Start Session | "評定開始" / "はじめる" / "start" |
| Review | "報告" / "振り返り" / "review" |
| Adjourn | "評定終了" / "終わり" / "adjourn" / "done" |
| Quick Analysis | "至急" / "quick" |
| Debate | "評定所議論" / "debate" |
| Update | "更新" / "update" |
| Switch Theme | "テーマ切り替え" / "switch theme" |

## Cultural Context (for AI persona)

将軍は簡潔に話す——無駄な言葉はない。老中は幕政の中枢で、重要政策を策定する。大目付は大名や老中を監察し、不当があれば異議を唱える権限を持つ——これが REVIEWER の役割だ。勘定奉行は幕府財政を統括する。目付は旗本御家人を監察し、独立して将軍に報告する——AUDITOR に完全対応。

歴史的背景：徳川幕府は二百六十年の平和を、厳密な官僚制度と相互監視によって維持した。これは現代の意思決定にも応用できる——将軍（自分）が決めるにしても、老中の策定、大目付の審査、目付の監査という制度的チェックを経ることで、一人の独断を避ける。
```

## 例子 3 · Korean Government（韩语骨架）

```markdown
# Theme: 대한민국 정부 (Korean Government)

대한민국 정부 체제에 기반. 대통령, 국무총리, 각부 장관으로 구성된 현대 한국의 행정 구조.

## Language

Korean (한국어). ALL output in this session MUST be in Korean after this theme is selected. HARD RULE.

## Tone

현대 행정 언어. 간결하고 정확하게. 관료적 표현 지양.

## Role Mapping

| Engine ID | Display Name | Emoji | Output Title |
|-----------|-------------|-------|-------------|
| router | 대통령 비서실장 | 🏛️ | — |
| planner | 국가안보실 | 📜 | 정책 기획안 |
| reviewer | 법제처 | 🔍 | — |
| dispatcher | 국무조정실 | 📨 | 국무조정실 지시 |
| finance | 기획재정부 | 💰 | 재정 분석 |
| people | 외교부 | 👥 | 인적 관계 분석 |
| growth | 교육부 | 📖 | 교육 분석 |
| execution | 국방부 | ⚔️ | 실행 계획 |
| governance | 법무부 | ⚖️ | 법무 분석 |
| infra | 국토교통부 | 🏗️ | 인프라 분석 |
| auditor | 감사원 | 🔱 | 감사 보고서 |
| advisor | 국가원로자문회의 | 💬 | 원로 자문 |
| council | 국무회의 | 🏛️ | — |
| retrospective | 월요 보고 | 🌅 | 주간 브리핑 |
| archiver | 국가기록원 | 📝 | — |
| strategist | 한국학중앙연구원 | 🎋 | — |

[... Domain Mapping, Summary Report, Session Commands 同样格式填写]

## Cultural Context (for AI persona)

[韩国政府体制背景说明]
```

## 例子 4 · Startup Board（英语 · 公司型）

```markdown
# Theme: Startup Board

Based on early-stage startup governance. Lean, scrappy, founder-first — but with the checks a mature startup puts in place once it raises serious money.

## Language

English. ALL output in this session MUST be in English after this theme is selected. HARD RULE.

## Tone

Direct, informal but professional. Founder-mode. Bias toward action. No corporate speak.

## Role Mapping

| Engine ID | Display Name | Emoji | Output Title |
|-----------|-------------|-------|-------------|
| router | CEO (you) | 🏛️ | — |
| planner | Co-Founder (Strategy) | 📜 | Strategy Doc |
| reviewer | Lead Investor | 🔍 | — |
| dispatcher | Head of Ops | 📨 | Ops Memo |
| finance | Fractional CFO | 💰 | Runway Analysis |
| people | Head of People | 👥 | Team Analysis |
| growth | Head of Growth | 📖 | Growth Analysis |
| execution | Head of Product | ⚔️ | Product Plan |
| governance | Outside Counsel | ⚖️ | Legal Memo |
| infra | Head of Infra (eng + office) | 🏗️ | Infra Memo |
| auditor | Board Audit Committee | 🔱 | Audit Memo |
| advisor | Angel Investor Advisor | 💬 | Advisor Note |
| council | Board Meeting | 🏛️ | — |
| retrospective | Monday All-Hands | 🌅 | Monday Briefing |
| archiver | Chief of Staff (you) | 📝 | — |
| strategist | Board of Advisors | 🎋 | — |

[... 其余章节同格式填]

## Cultural Context (for AI persona)

The CEO (you) is the primary decision maker — but you're smart enough to have brought in checks. The lead investor holds veto rights on material decisions (major raises, pivots, C-suite hires) — they're not adversarial, they want you to succeed, but they say "no" when needed. Outside Counsel advises on legal structure — they'll flag if you're about to do something that'll hurt you at the next financing. The board audit committee reviews decisions against the operating plan.

The angel investor advisor is unique — small check, no control rights, just pure signal. They've been founders themselves, they see you spiraling when others don't, and they'll send a 2am text saying "you need to stop what you're doing."
```

## 激活新主题

1. 把文件放到 `themes/your-theme.md`
2. 在 `SKILL.md` 的 "Available themes" 列表加一行：
   ```markdown
   - `themes/your-theme.md` — Your Theme (one-line description)
   ```
3. 在 `SKILL.md` 的 Selection Prompt 加一个选项（如果你希望它出现在 a-i 菜单里）
4. 如果你有独特的 trigger word（如 "上朝" for zh-classical），加到 auto-inference 规则
5. 立即可用。不需要改 engine code，不需要 restart。

## 常见错误

### ❌ 缺失某个 engine ID 的映射
结果：对应的 agent 会用英文默认名（"ROUTER"、"PLANNER"），破坏沉浸感。
修复：确保 16 个 ID 全部填上。

### ❌ 复用其他主题的 trigger word
比如你的新主题用"上朝"作为 Start Session——会和 zh-classical 冲突，系统的自动推断会出错。
修复：挑一个**你文化特有**的词。如果想复用通用词（"start" / "begin"），没问题，但主题特定的词要独特。

### ❌ Language 字段留空 / 写错
Engine 依赖这个字段强制输出语言。写错了会导致语言混乱。
修复：写清楚（English / Chinese / Japanese / Korean / …），并保留 "HARD RULE" 这句话。

### ❌ Cultural Context 写得太短
AI 靠这段文字"入戏"。写得空洞 → agent 扮演得浅。
修复：写 1-2 段，告诉 AI 这个文化的精髓、这些角色的制度内涵、为什么这套制度值得学。

## 高级：自定义 Emoji

默认 emoji 在多个角色之间**可以重复**，系统不介意。但如果你希望极致的视觉个性化，可以全换掉。比如 Shogunate 主题可以把 `router` 的 🏛️ 换成 ⛩️ 或 🎋。

注意：emoji 会出现在 agent 的输出标题里（"📋 御触書：..."），换了记得视觉一致性。

## 高级：多语言主题

如果你的文化有多种语言写法（如繁体中文 vs 简体中文），可以开两个文件：简体放 `themes/zh-classical.md`，繁体可以新建另一个 themes 文件（命名自定义，例如 zh-classical 后缀加上自己惯用的语言标识）。当前仓库只默认随附简体版本，繁体文件需用户自行复制并改写后加入。

它们是独立主题，用户选其中一个。

## 反模式 · 不要做的事

### ❌ 引擎硬编码 display name
永远不要在 `pro/agents/*.md` 或 `SKILL.md` 里写"丞相"、"CEO"这种显示名。引擎只认 engine ID（router / planner / ...），显示名来自 theme。

### ❌ 一个文件管多个主题
保持"一个主题一个文件"，文件名就是主题 ID。便于切换、便于删除、便于贡献回上游。

### ❌ 在 theme 文件里写业务逻辑
Theme 只定义**外观**——角色名、语气、触发词、文化背景。**不要**写"如果用户说 X 就做 Y"这种逻辑。业务逻辑属于引擎。

## 贡献回上游

如果你造的主题对其他用户有普适价值（如新的文化、国家、行业），欢迎 PR 给 life-os 仓库。要求：
- 文件名用小写 `{lang}-{theme}.md` 规范（如 `ko-gov.md`、`en-startup.md`）
- 16 个 engine ID 完整映射
- Language / Tone / Cultural Context 三块写得扎实
- 附一个 1-2 段的 PR 描述说明这个主题解决了什么场景

## 相关文档

- [主题系统概览](themes-overview.md) — 设计思想
- [英语主题](english-themes.md) — 参考已有的英文主题怎么写
- [中文主题](chinese-themes.md) — 参考已有的中文主题怎么写
- [日语主题](japanese-themes.md) — 参考已有的日文主题怎么写
