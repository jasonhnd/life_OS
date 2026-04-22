# 英语主题 · en-roman / en-usgov / en-csuite

三个英语主题：罗马共和国、美国政府、公司高管层。**文化根不同，决策引擎相同。**

所有英语主题的输出语言都是英语。HARD RULE。

## 三个主题速览

| 主题 | 文件 | 文化根 | 语气 | 最适合 |
|------|------|-------|------|-------|
| 🏛️ Roman Republic | `themes/en-roman.md` | 罗马共和国（前 509 - 前 27） | 庄重但清晰，古典分量感，现代语言 | 想要历史感 + 严肃 |
| 🇺🇸 US Government | `themes/en-usgov.md` | 美国联邦政府 | 专业、简洁、华盛顿简报风 | 英语职场 + 政府熟悉感 |
| 🏢 Corporate | `themes/en-csuite.md` | 现代企业高管层 | 专业直接，不用公司黑话 | 商务 + 英语专业沟通 |

## 角色映射对照表

三个主题的 16 个 engine ID → 显示名对照：

| Engine ID | Roman Republic | US Government | C-Suite |
|-----------|----------------|---------------|---------|
| router | Consul 🏛️ | Chief of Staff 🏛️ | Chief of Staff 🏛️ |
| planner | Senate 📜 | National Security Council 📜 | VP Strategy 📜 |
| reviewer | Tribune 🔍 | Attorney General 🔍 | General Counsel 🔍 |
| dispatcher | Praetor 📨 | OMB 📨 | COO 📨 |
| finance | Quaestor 💰 | Dept. of Treasury 💰 | CFO 💰 |
| people | Aedile of the Plebs 👥 | Dept. of State 👥 | CHRO 👥 |
| growth | Pontifex 📖 | Dept. of Education 📖 | CLO 📖 |
| execution | Legatus ⚔️ | Dept. of Defense ⚔️ | VP Operations ⚔️ |
| governance | Censor ⚖️ | Dept. of Justice ⚖️ | Chief Compliance Officer ⚖️ |
| infra | Aedile of the Curule 🏗️ | Dept. of HHS 🏗️ | VP Infrastructure 🏗️ |
| auditor | Censor (audit) 🔱 | GAO 🔱 | Internal Audit 🔱 |
| advisor | Augur 💬 | Council of Economic Advisers 💬 | Executive Coach 💬 |
| council | Comitia 🏛️ | Cabinet Meeting 🏛️ | Board Meeting 🏛️ |
| retrospective | Salutatio 🌅 | Daily Intelligence Brief 🌅 | Monday Standup 🌅 |
| archiver | Scriba 📝 | National Archives 📝 | Executive Assistant 📝 |
| strategist | Oracle of Delphi 🎋 | Library of Congress 🎋 | Advisory Board 🎋 |

## 总结报告名字

- Roman Republic: **Senatus Consultum**
- US Government: **Presidential Memorandum**
- C-Suite: **Executive Brief**

## 触发词对比

| Action | Roman | US Gov | C-Suite | 共同触发（任何英文主题都认） |
|--------|-------|--------|---------|---------------------------|
| Start Session | "convene" / "begin" | "begin" / "brief me" | "open session" | "start" |
| Review | "review" / "report" | "review" / "brief me" | "standup" / "check in" | "review" |
| Adjourn | "adjourn" / "dismiss" | "adjourn" / "end" | "close session" | "adjourn" / "done" / "end" |
| Quick | "quick analysis" | "quick analysis" | "quick analysis" | "quick" |
| Debate | "comitia" | "cabinet session" | "board discussion" | "debate" |

**规则**：英文通用触发词（`start` / `adjourn` / `quick` / `debate` 等）在任何英文主题里都工作。主题特定的触发词（`convene` / `comitia` / `dismiss` 等）增加沉浸感。

## 何时选哪个

### 🏛️ Roman Republic — 选这个如果...

- 你喜欢**历史感和古典分量**。"Senatus Consultum"比"Executive Brief"更有仪式感
- 你做**人生级决策**（不是日常），希望会话的氛围配得上
- 你对**制衡体制本身**感兴趣——罗马是源头：Tribune 的 veto 就是"veto"这个词的出处
- 你希望 AI 用有分量但仍然清晰的语气，不是商务话术

### 🇺🇸 US Government — 选这个如果...

- 你对美国政府架构熟悉（看新闻、读 West Wing、关心政策）
- 你想要**政府级的严肃感**但不想要古典外壳
- "Attorney General can veto this" 对你来说比"Tribune" 更直观
- 你做**合规 / 政策 / 风险类**决策，政府外壳比企业外壳更契合

### 🏢 Corporate (C-Suite) — 选这个如果...

- 你在企业环境工作，**CEO / CFO / General Counsel** 是你每天听到的词
- 你做**商业 / 职业 / 投资**决策，企业外壳最契合语境
- 你希望**最低学习成本**——不需要解释"what is OMB"或"who is the Tribune"
- 你想要的是**工具感**，不是仪式感

## 文化背景详解

### 🏛️ Roman Republic

罗马共和国是**世界上第一个制度化的权力分立系统**。关键点：
- 两位 Consul 同时在任，互相制衡
- Tribune of the Plebs 代表平民，对 Senate 决议有**绝对否决权**（Latin "veto" = "I forbid"，这个词就从这来）
- Censor 审计公众道德和财政，独立于 Consul
- Augur 读预兆，是古罗马的"行为审计"——他们有权说"时机不对"

Life OS 把这套 2500 年前的系统映射到你的个人决策：
- Consul（ROUTER）接你的话，但不独断
- Senate（PLANNER）起草决策
- Tribune（REVIEWER）有否决权，真的会说"不行"
- Censor（AUDITOR）独立审计
- Augur（ADVISOR）读你行为的模式，警告苗头不对

### 🇺🇸 US Government

美国联邦政府的设计就是"制衡的教科书"。关键点：
- Chief of Staff 不是总统本人——是把一切事务**分流**到合适部门的枢纽
- Attorney General 可以**在法律上**阻止行政命令（合法性否决）
- GAO（Government Accountability Office）向国会而非总统报告——真正的独立审计
- Council of Economic Advisers 给坦率的经济和行为建议，不受部门利益绑架

Life OS 把这套体制套在你头上：
- Chief of Staff（ROUTER）管你的"收件箱"
- NSC（PLANNER）跨部门起草
- Attorney General（REVIEWER）在合法合规上可以说 No
- GAO（AUDITOR）审计决策质量，独立于其他部门
- CEA（ADVISOR）观察你的行为模式

### 🏢 C-Suite

现代企业的治理结构。关键点：
- Chief of Staff 是高管的右手——**路由、管理收件箱、确保不遗漏**
- General Counsel 审所有重大决策——"I can't approve this as structured, here's why"
- Internal Audit 独立评估决策执行质量
- Executive Coach 观察行为模式，直言盲点

Life OS 把这映射到你：
- 你是这家"公司"的 CEO
- Chief of Staff / General Counsel / CFO / CHRO 各司其职
- Board Meeting（COUNCIL）在冲突时召开
- Executive Coach（ADVISOR）像真正的 coach 一样告诉你"你最近在躲某件事"

## 实战例子

### 例子 1：用 Roman Republic 思考跳槽

```
You: I'm thinking about leaving my job to start something.

Consul: 🏛️ This is a decision requiring deliberation. Let me assemble 
        the Senate to draft, the Tribune to review, and the six 
        domains to assess.

Senate (PLANNER): 📜 Senate Brief
        ...

Tribune (REVIEWER): 🔍 I review this with my veto authority. 
        I find the financial runway assumption aggressive—
        Conditional approval: require 12 months runway, not 6.

Quaestor (FINANCE): 💰 Treasury Assessment
        ...

Final: 📋 Senatus Consultum: Leaving employment for entrepreneurship
       Overall rating: 7/10 — Viable with stricter financial preparation.
```

### 例子 2：用 C-Suite 审查一笔投资

```
You: Should I put $50k into this crypto ETF?

Chief of Staff: 🏛️ Let me clarify — is this a financial analysis only, 
                or are you asking for a full decision?

You: Full decision.

[decision flow runs]

Final: 📋 Executive Brief: $50k Crypto ETF Investment
       Overall rating: 4/10 — Not recommended at current allocation.
       
       Must Address:
       - CFO: This exceeds 5% of total portfolio risk budget
       - General Counsel: No written exit criteria
       
       Board Meeting (COUNCIL) was triggered: 
       CFO and Executive Coach disagreed. Resolution: reduce to $15k max.
```

### 例子 3：用 US Government 做健康决策

```
You: I keep skipping sleep for work.

Chief of Staff: This pattern concerns me. Briefing the CEA 
                (Behavioral) and HHS (Health) in parallel.

CEA (ADVISOR): 💬 CEA Advisory
    You've mentioned sleep compromise 4 times in the last 2 weeks. 
    Pattern consistent with burnout precursor. 
    Recommend immediate intervention, not analysis.

Dept. of HHS (INFRA): 🏗️ HHS Assessment
    Health risk: chronic sleep deprivation is cumulative.
    Concrete protocol: [...]
```

## 如何在这三者之间切换

```
You: switch theme

System: 🎨 Current theme: Roman Republic. Choose new theme: [a-i list]

You: b

System (in new theme's language, which is still English since all 3 are English):
     🇺🇸 Switched to US Government. Chief of Staff at your service.
```

三个英语主题**互相切换**语言不变（都是英语），只是显示名变。切到中文或日文主题则语言也变。

## 反模式 · 不要做的事

### ❌ 在 Roman Republic 里用商务黑话
"leverage synergies"、"stakeholders" —— 不契合 Tribune / Censor / Augur 的语气。选了 Roman 就进入那个氛围。

### ❌ 在 US Government 里写得像学术论文
简报风是"关键结论在前，支撑证据在后"。不是"首先我要说明…然后我要指出…"。

### ❌ 在 C-Suite 里摆官僚姿态
C-Suite 不是"开会议"——是"解决问题"。General Counsel 不会说"根据第 X 条…"，会说"This is a problem, here's why"。

## 相关文档

- [主题系统概览](themes-overview.md) — 设计思想
- [中文主题](chinese-themes.md) — 中文三主题
- [日语主题](japanese-themes.md) — 日语三主题
- [添加新主题](adding-a-theme.md) — 自己造一个
