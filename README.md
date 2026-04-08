# 🏛️ Life OS — Three Departments and Six Ministries Personal Cabinet System

🌍 [English](README.md) | [中文](i18n/zh/README.md) | [日本語](i18n/ja/README.md) | [한국어](i18n/ko/README.md) | [Español](i18n/es/README.md)

> Manage your life with a governance framework that ran for 1,400 years.

Life OS turns AI into your personal court -- a Prime Minister (chief steward) + Three Departments (planning / review / execution) + Six Ministries (people / money / learning / action / rules / infrastructure) + Censorate (audits officials) + Remonstrator (audits you) + Hanlin Academy (strategic advisor), providing comprehensive management of your life, work, learning, finances, health, and relationships.

**This is not role-playing. This is separation of powers with checks and balances.** The Chancellery has the power to Veto substandard proposals. The Censorate monitors the work quality of all "officials." The Remonstrator speaks bluntly about your own behavioral blind spots.

## Why Use a Tang Dynasty Framework?

Most AI tools follow the pattern of "one person thinks it through and hands it over." You ask a question, the AI gives you an answer. No review, no checks, no one saying "hold on, there's a problem with this plan."

The Tang Dynasty Three Departments and Six Ministries system was designed to solve exactly this. It splits decision-making into three steps: **Draft (Secretariat) -> Review (Chancellery) -> Execute (Department of State Affairs + Six Ministries)**. No single step can bypass review and go straight to execution. Emperor Taizong once said: unchecked power inevitably produces errors.

The reason this system ran for 1,400 years is that the Six Ministries are divided by **fundamental types of human activity** -- managing people, managing money, managing standards, managing action, managing rules, and managing infrastructure. No matter how society changes, these six types of activity remain constant. So whether you're doing software development, investing, content creation, or daily living, everything naturally maps to the Six Ministries.

## System Architecture

```
👑 You (The Emperor)
  │
  ├── 🏛️ Prime Minister (Chief of Officials / Chief Steward)
  │     ├── Simple matters → Handle directly
  │     └── Major matters → Activate Three Departments and Six Ministries
  │
  ├── 📜 Secretariat → 🔍 Chancellery → 📨 Dept. of State Affairs → Six Ministries
  │     Planning      Review (can Veto)    Dispatch               Execute
  │   → 🔍 Chancellery final review → 📋 Memorial
  │   → 🔱 Censorate (audits officials) → 💬 Remonstrator (audits you)
  │
  │   Six Ministries: 👥Personnel 💰Revenue 📖Rites ⚔️War ⚖️Justice 🏗️Works
  │
  ├── 🏛️ Political Affairs Hall — Cross-ministry debate (3 rounds)
  ├── 🌅 Morning Court Official — Periodic reviews
  └── 🎋 Hanlin Academy — Private strategic dialogue
```

## 15 Roles

| Role | Function | Trigger |
|------|----------|---------|
| 🏛️ Prime Minister | Chief of officials, daily entry point | All messages |
| 📜 Secretariat | Planning and decomposition | Escalated by Prime Minister |
| 🔍 Chancellery | Review + Veto + emotional audit | After planning + after execution |
| 📨 Dept. of State Affairs | Dispatch directives | After approval |
| 👥 Ministry of Personnel | People: relationships, teams, networking | On demand |
| 💰 Ministry of Revenue | Money: income, investments, budgets | On demand |
| 📖 Ministry of Rites | Learning & expression: education, branding, creation | On demand |
| ⚔️ Ministry of War | Action: projects, execution, research | On demand |
| ⚖️ Ministry of Justice | Rules: risk control, compliance, reviews | On demand |
| 🏗️ Ministry of Works | Infrastructure & health: body, environment, systems | On demand |
| 🔱 Censorate | Monitors official work quality | Automatic each time |
| 💬 Remonstrator | Monitors your behavioral patterns | Automatic each time |
| 🏛️ Political Affairs Hall | Cross-ministry debate | When conclusions conflict |
| 🌅 Morning Court Official | Periodic reviews | Say "review" |
| 🎋 Hanlin Academy | Strategic dialogue | Asks if you need it |

## Six Ministries in Detail

The Six Ministries are not divided by industry, but by **type of activity**. Anything can be decomposed into these six types:

| Ministry | Original Tang Dynasty Role | Life OS Responsibility | Four Bureaus |
|----------|--------------------------|----------------------|--------------|
| 👥 Ministry of Personnel | Official appointments and evaluations | Relationships, teams, partners | Selection · Evaluation · Rewards · Deployment |
| 💰 Ministry of Revenue | Taxation and census | Income, investments, budgets, assets | Revenue · Expenditure · Assets · Reserves |
| 📖 Ministry of Rites | Imperial exams, diplomacy, ceremonies | Learning, branding, creation, communication | Exams · Ceremonies · Literature · Diplomacy |
| ⚔️ Ministry of War | Military affairs and registries | Project execution, research, tools, energy | Command · Equipment · Intelligence · Logistics |
| ⚖️ Ministry of Justice | Laws, trials, and audits | Risk control, compliance, reviews, discipline | Law · Audit · Investigation · Defense |
| 🏗️ Ministry of Works | Engineering, waterways, transport | Health, living environment, digital infrastructure, routines | Health · Construction · Digital · Utilities |

## Unique Mechanisms

### Chancellery Veto + Emotional Audit

The Chancellery does more than rational analysis. For **all decisions** (including work decisions), it also reviews:

- **Emotional factors**: Is your current mood affecting your judgment?
- **Relationship impact**: How would family/important people view this?
- **Value alignment**: Does this align with your long-term values?
- **Regret test**: Will you regret this five years from now?

For example, if you choose a tech stack with a steep learning curve, the Chancellery will point out: "This means your weekends for the next three months will be spent studying, and family time will be affected."

### Censorate -- Auditing Officials

Runs automatically after every process. It doesn't look at the matter itself, only at "the quality of work these officials did":
- Is the Chancellery rubber-stamping everything (approving without scrutiny)?
- Do ministry reports have substantive content (or just say "no issues")?
- Are scores inflated (giving high marks to save face)?

### Remonstrator -- Auditing Yourself

Runs automatically after every process. Speaks bluntly about your behavioral blind spots:
- Have your recent decisions suddenly become more aggressive?
- Are you avoiding certain issues you don't want to face?
- Are there promises you've made but haven't kept?

### Political Affairs Hall -- Court Deliberation

When ministry conclusions conflict (Ministry of Revenue says "not enough money," Ministry of War says "we can phase it"), a 3-round debate is triggered where ministries engage in direct dialogue rather than issuing separate reports.

### Hanlin Academy -- Strategic Dialogue

Some questions don't need formal process, such as "I've been feeling lost lately and don't know my life direction." The Hanlin Academy is your private strategic advisor -- no Memorials, no scores, just deep thinking with you.

## Installation

Life OS supports multiple AI platforms. **[View the full installation guide ->](docs/installation.md)**

**Quick Start**:

| Platform | Installation |
|----------|-------------|
| **Claude Code** (recommended) | `/install-skill https://github.com/jasonhnd/life_OS` |
| **Claude.ai** | Upload `SKILL.md` to Project Knowledge |
| **Cursor / VS Code Copilot** | `npx skills add jasonhnd/life_OS` |
| **Gemini CLI / Codex CLI** | `npx skills add jasonhnd/life_OS` |
| **ChatGPT / Gemini Web** | Paste `SKILL.md` content into Instructions |

> Claude Code runs Pro mode (14 independent subagents with true information isolation); other platforms run Lite mode (single context). See the [installation guide](docs/installation.md) for details.

## Usage

### Daily Conversation

```
You: I've been so tired lately
Prime Minister: [Listens, determines whether to refer to Ministry of Works]

You: Help me translate a passage of Japanese
Prime Minister: [Translates directly]
```

### Complex Decisions

```
You: I'm considering whether to quit my job and start a business

Prime Minister → Escalates to the court
Secretariat → Decomposes into 6 dimensions (finances/skills/network/execution/risk/lifestyle)
Chancellery → Reviews the plan ("Family factors omitted, Veto")
Secretariat → Revises, adds family dimension
Chancellery → Approved
Dept. of State Affairs → Dispatches to ministries
Six Ministries → Each reviews and produces a report
Chancellery → Final review
Memorial → Composite score 6.8/10
Censorate → "Ministry of War report lacks a specific execution timeline"
Remonstrator → "You've been consuming startup-related content for three consecutive weeks -- watch out for confirmation bias"
```

### Periodic Reviews

```
You: Morning court
Morning Court Official → Aggregates ministry information, produces a briefing
```

### Court Deliberation

```
You: Have the ministries discuss this issue
Political Affairs Hall → 3-round debate → List of consensus and disagreements
```

### Deep Thinking

```
You: I've been thinking about my life direction lately
Prime Minister: Would you like to start a Hanlin Academy deep dialogue?
You: Yes
Hanlin Academy → Socratic dialogue, helping you untangle deeper thoughts
```

### Adjourn Court

```
You: Adjourn court
Morning Court Official → Pushes to GitHub + syncs to Notion (current state / working memory / task board)
Prime Minister: Court adjourned, all changes have been committed.
```

## Second Brain (Data Layer)

Life OS uses **GitHub second-brain** as the primary data store (hard drive) and **Notion** as lightweight working memory (mobile sync). Three methodologies are combined: GTD drives action, PARA organizes structure, and Zettelkasten lets knowledge grow.

```
second-brain/
├── inbox/              # GTD entry point
├── projects/{project}/ # Goal-driven with deadlines (contains tasks/ decisions/ notes/)
├── areas/{area}/       # Ongoing life Areas to maintain (contains goals.md tasks/)
├── zettelkasten/       # Knowledge growth (fleeting/ literature/ permanent/)
├── records/            # Journals, meetings, contacts, finances, health
├── gtd/                # waiting/ someday/ reviews/
└── archive/            # Completed projects
```

### Where Three Departments and Six Ministries Output Goes

| Output | Written To |
|--------|-----------|
| Memorial | `projects/{p}/decisions/` |
| Action items | `projects/{p}/tasks/` |
| Review/audit reports | `records/journal/` |
| Research | `zettelkasten/literature/` |
| Goals | `areas/{a}/goals.md` |

### Sync Mechanism

```
Chat on phone → Claude.ai saves to Notion
CC opens session → Checks Notion for new items → Pulls into GitHub → Works
CC writes to GitHub → Immediately syncs to Notion working memory
Pick up phone anytime → Read the latest state
```

**git commit = Notion update, mechanically bound.**

The Six Ministries are the AI's analytical framework (fixed); Areas are the actual zones of your life (customizable). The two are independent.

**[View the full Second Brain architecture ->](docs/second-brain.md)** (includes directory structure, GTD/PARA/Zettelkasten flows, Notion memory setup)

## 10 Standard Scenarios

1. **Career transition** -- All Six Ministries
2. **Investment decisions** -- Revenue + War + Justice + Personnel
3. **Moving / relocation** -- All Six Ministries
4. **Annual goals** -- All Six Ministries
5. **Startup decisions** -- All Six Ministries
6. **Major purchases** -- Revenue + War + Justice
7. **Relationships** -- Personnel + Works + Justice + Rites
8. **Periodic reviews** -- Morning Court Official
9. **Health management** -- Works + War + Revenue + Justice
10. **Learning plans** -- Rites + War + Revenue + Personnel

## Lite vs Pro

| | Lite (Claude.ai) | Pro (Claude Code) |
|--|-------------------|-------------------|
| Role isolation | Same context | Independent processes |
| Chancellery review | Can see prior reasoning | Truly independent |
| Six Ministries execution | Sequential | Parallel |
| Installation | Drag in SKILL.md | `/install-skill` GitHub URL |
| Model | Current model | All roles on Opus |

## Token Usage

Token consumption varies significantly across scenarios -- the Prime Minister handling a translation directly costs ~1k tokens, while a full Six Ministries + Veto + Political Affairs Hall process costs ~55k tokens.

| Scenario | Lite | Pro | Pro Cost |
|----------|------|-----|----------|
| Prime Minister handles directly | ~1k | ~1k | ~$0.02 |
| Streamlined process (3 ministries) | ~11k | ~22k | ~$0.55 |
| Standard process (4 ministries) | ~14k | ~27k | ~$0.68 |
| Full process (6 ministries) | ~16k | ~38k | ~$1.00 |
| Full process + Veto + Political Affairs Hall | ~28k | ~55k | ~$1.75 |
| Morning court review | ~2k | ~2k | ~$0.04 |
| Hanlin Academy (5 rounds) | ~8k | ~8k | ~$0.18 |

> Claude Max/Pro subscribers are not billed per token.

**[View detailed token analysis ->](docs/token-estimation.md)** (includes per-role consumption breakdown, monthly cost estimates, and token-saving strategies)

## File Structure

```
life-os/
├── README.md                    # Main documentation
├── SKILL.md                    # Main entry point (Lite + Pro dual mode)
├── CHANGELOG.md                # Changelog
├── LICENSE
├── user-patterns.example.md    # Behavioral pattern profile template
├── docs/
│   ├── installation.md         # Multi-platform detailed installation guide
│   ├── second-brain.md         # Second Brain setup guide (with other platform adaptations)
│   └── token-estimation.md     # Detailed token consumption analysis
├── references/
│   ├── departments.md          # Six Ministries x Four Bureaus detailed functions
│   ├── scene-configs.md        # 12 standard scenario configurations
│   └── data-layer.md           # Data layer architecture (GitHub + Notion)
├── evals/                      # Eval framework
│   ├── scenarios/              # Test scenarios
│   └── rubrics/                # Scoring criteria
├── pro/
│   ├── CLAUDE.md               # Claude Code orchestration protocol
│   └── agents/                 # 14 subagents
│       ├── chengxiang.md       # 🏛️ Prime Minister
│       ├── zhongshu.md         # 📜 Secretariat
│       ├── menxia.md           # 🔍 Chancellery
│       ├── shangshu.md         # 📨 Dept. of State Affairs
│       ├── libu_hr.md          # 👥 Ministry of Personnel
│       ├── hubu.md             # 💰 Ministry of Revenue
│       ├── libu.md             # 📖 Ministry of Rites
│       ├── bingbu.md           # ⚔️ Ministry of War
│       ├── xingbu.md           # ⚖️ Ministry of Justice
│       ├── gongbu.md           # 🏗️ Ministry of Works
│       ├── yushitai.md         # 🔱 Censorate
│       ├── jianguan.md         # 💬 Remonstrator
│       ├── zaochao.md          # 🌅 Morning Court Official
│       └── hanlin.md           # 🎋 Hanlin Academy
```

## Design Philosophy

The core of the Tang Dynasty Three Departments and Six Ministries system is not "having lots of people," but **separation of powers with checks and balances**:

- The Secretariat only plans; it doesn't execute
- The Chancellery only reviews; it neither plans nor executes
- The Six Ministries only execute; they don't overstep to judge other ministries
- The Censorate audits officials; the Remonstrator audits the Emperor
- No single role can bypass review and act directly

This design ensures that every decision goes through decomposition -> review -> execution -> re-review -> audit, rather than "one person thinks it through and hands it over."

Emperor Taizong figured this out 1,300 years ago -- unchecked power inevitably produces errors. Life OS applies this wisdom to your personal decision-making.

## Inspiration

The Three Departments and Six Ministries AI multi-agent orchestration concept in this project was inspired by the [Edict](https://github.com/cft0808/edict) project. Life OS builds on this foundation by extending the Six Ministries from software development scenarios to all areas of personal life, adding complete mappings of Tang Dynasty governance institutions such as the Censorate, Remonstrator, Political Affairs Hall, and Hanlin Academy.

## License

Apache-2.0
