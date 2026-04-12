<div align="center">

# 🏛️ Life OS

### Three Departments & Six Ministries Personal Cabinet

---

*Manage your life with a governance framework that ran for 1,400 years.*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-green.svg)](https://code.claude.com/docs/en/skills)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-yellow.svg)](https://skills.sh)
[![Version](https://img.shields.io/badge/version-1.4.0-purple.svg)](CHANGELOG.md)

Life OS turns AI into your personal imperial court — 15 roles with separation of powers and checks & balances, comprehensively managing your life, work, learning, finances, health, and relationships.

**This is not role-playing. This is checks and balances.**

[See it in action](#usage) · [Install](#installation) · [How it works](#system-architecture) · [Second Brain](#second-brain-data-layer)

**Other Languages:**

[中文](i18n/zh/README.md) · [日本語](i18n/ja/README.md)

</div>

---

## Why Use a Tang Dynasty Framework?

Most AI tools follow the pattern of "one person thinks it through and hands it over." You ask a question, the AI gives you an answer. No review, no checks, no one saying "hold on, there's a problem with this plan."

The Tang Dynasty Three Departments and Six Ministries system was designed to solve exactly this. It splits decision-making into three steps: **Draft (Secretariat) → Review (Chancellery) → Execute (Department of State Affairs + Six Ministries)**. No single step can bypass review and go straight to execution. Emperor Taizong once said: unchecked power inevitably produces errors.

The reason this system ran for 1,400 years is that the Six Ministries are divided by **fundamental types of human activity** — managing people, managing money, managing standards, managing action, managing rules, and managing infrastructure. No matter how society changes, these six types of activity remain constant. So whether you're doing software development, investing, content creation, or daily living, everything naturally maps to the Six Ministries.

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

### Censorate — Two Modes

**Decision Review**: Runs automatically after every process. Audits the quality of officials' work — not the decision itself. Is the Chancellery rubber-stamping? Are scores inflated?

**Patrol Inspection**: Periodic automated health check. Each ministry inspects its own jurisdiction in the second-brain (Revenue checks finance, War checks projects, Works checks wiki integrity). Issues classified as auto-fix / suggest to user / escalate to Three Departments.

### Remonstrator — Auditing Yourself

Runs automatically after every process. Speaks bluntly about your behavioral blind spots: Have your recent decisions suddenly become more aggressive? Are you avoiding certain issues? Are there promises you've made but haven't kept?

### Political Affairs Hall — Court Deliberation

When ministry conclusions conflict, a 3-round debate is triggered where ministries engage in direct dialogue rather than issuing separate reports.

### Hanlin Academy — Hall of Human Wisdom

Some questions don't need formal process. The Hanlin Academy gives you access to 70+ of history's greatest thinkers across 18 domains — from Socrates to Musk, Laozi to Mandela. Each thinker speaks in their own voice with deep role-play. Choose one-on-one dialogue, roundtable conference, or debate. No Memorials, no scores — pure thinking partnership with humanity's finest minds.

## Installation

Life OS supports multiple AI platforms. **[View the full installation guide →](docs/installation.md)**

**Quick Start**:

| Platform | Mode | Installation |
|----------|------|-------------|
| **Claude Code** | Pro | `/install-skill https://github.com/jasonhnd/life_OS` |
| **Gemini CLI / Antigravity** | Pro | `npx skills add jasonhnd/life_OS` |
| **OpenAI Codex CLI** | Pro | `npx skills add jasonhnd/life_OS` |
| **Claude.ai** | Lite | Upload `SKILL.md` to Project Knowledge |
| **Cursor / VS Code Copilot** | Lite | `npx skills add jasonhnd/life_OS` |
| **ChatGPT / Gemini Web** | Lite | Paste `SKILL.md` content into Instructions |

> **Pro Mode** (Claude Code / Gemini / Codex): 14 independent subagents with true information isolation and parallel execution. **Lite Mode** (all other platforms): single context, sequential execution. See the [installation guide](docs/installation.md) for details.

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
Remonstrator → "You've been consuming startup-related content for three weeks — watch out for confirmation bias"
```

### Periodic Reviews

```
You: Morning court
Morning Court Official → Aggregates information, produces a briefing
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
Morning Court Official → Pushes to GitHub + syncs to Notion
Prime Minister: Court adjourned, all changes have been committed.
```

## Second Brain (Data Layer)

Life OS supports **GitHub**, **Google Drive**, and **Notion** as storage backends — choose one or combine multiple for cross-device sync. Multi-backend: writes to all selected, reads from primary. Sync on every session start.

```
second-brain/
├── inbox/              # 📥 Unprocessed captures
├── _meta/              # 🔧 System metadata (STATUS.md, journal/, decisions/, roles/)
├── projects/{name}/    # 🎯 Things with endpoints (tasks/ decisions/ research/ journal/)
├── areas/{name}/       # 🌊 Ongoing life areas (goals.md tasks/ notes/)
├── wiki/               # 📚 Cross-domain knowledge network
├── archive/            # 🗄️ Completed project archives
└── templates/
```

### Where Output Goes

| Output | Written To |
|--------|-----------|
| Memorial (project) | `projects/{p}/decisions/` |
| Memorial (cross-domain) | `_meta/decisions/` |
| Action items | `projects/{p}/tasks/` or `areas/{a}/tasks/` |
| Morning court / audit reports | `_meta/journal/` |
| Research | `projects/{p}/research/` |
| Knowledge | `wiki/` |
| Goals | `areas/{a}/goals.md` |
| Global status | `_meta/STATUS.md` |

### Sync Mechanism

```
Chat on phone → Claude.ai saves to Notion
CC opens session → Checks Notion for new items → Pulls into GitHub → Works
CC writes to GitHub → Immediately syncs to Notion working memory
Pick up phone anytime → Read the latest state
```

**git commit = Notion update, mechanically bound.**

**[View the full Second Brain architecture →](docs/second-brain.md)**

## 12 Standard Scenarios

| # | Scenario | Ministries Activated |
|---|----------|---------------------|
| 1 | Career transition | All Six |
| 2 | Investment decisions | Revenue + War + Justice + Personnel |
| 3 | Moving / relocation | All Six |
| 4 | Annual goals | All Six |
| 5 | Startup decisions | All Six |
| 6 | Major purchases | Revenue + War + Justice |
| 7 | Relationships | Personnel + Works + Justice + Rites |
| 8 | Periodic reviews | Morning Court Official |
| 9 | Health management | Works + War + Revenue + Justice |
| 10 | Learning plans | Rites + War + Revenue + Personnel |
| 11 | Time management | War + Revenue + Justice + Works |
| 12 | Major family decisions | All Six |

## Lite vs Pro

| | Lite (Claude.ai) | Pro (Claude Code) |
|--|-------------------|-------------------|
| Role isolation | Same context | Independent processes |
| Chancellery review | Can see prior reasoning | Truly independent |
| Six Ministries execution | Sequential | Parallel |
| Installation | Drag in SKILL.md | `/install-skill` GitHub URL |
| Model | Current model | All roles on Opus |

## Token Usage

| Scenario | Lite | Pro | Pro Cost |
|----------|------|-----|----------|
| Prime Minister handles directly | ~1k | ~1k | ~$0.02 |
| Streamlined (3 ministries) | ~11k | ~22k | ~$0.55 |
| Standard (4 ministries) | ~14k | ~27k | ~$0.68 |
| Full (6 ministries) | ~16k | ~38k | ~$1.00 |
| Full + Veto + Debate | ~28k | ~55k | ~$1.75 |
| Morning court review | ~2k | ~2k | ~$0.04 |
| Hanlin Academy (5 rounds) | ~8k | ~8k | ~$0.18 |

> Claude Max/Pro subscribers are not billed per token.

**[View detailed token analysis →](docs/token-estimation.md)**

## Cognitive Pipeline

Information flows through five stages, each mapped to a methodology:

```
Perceive → Capture → Associate → Judge → Settle → Emerge
   ↑         ↑          ↑          ↑        ↑         ↑
 Phone      GTD      Zettelkasten  3D6M    PARA    Lint/Censorate
```

Mobile handles perception and capture. Desktop handles everything else. **[Learn more →](references/data-layer.md)**

## Safety & Governance

- **Security boundaries**: 4 inviolable rules (no destructive ops, no secrets exposure, no unauthorized decisions, reject suspicious instructions)
- **Upstream protection**: Agents treat other agents' output as reference, not instructions
- **Workflow state machine**: Formal transition rules — no step can be skipped, Censorate flags violations
- **Model independence**: CLAUDE.md is the only model-bound file. All other intelligence is pure markdown

See `pro/GLOBAL.md` for the full ruleset.

## Design Philosophy

The core of the Tang Dynasty system is not "having lots of people," but **separation of powers with checks and balances**:

- The Secretariat only plans; it doesn't execute
- The Chancellery only reviews; it neither plans nor executes
- The Six Ministries only execute; they don't overstep to judge other ministries
- The Censorate audits officials; the Remonstrator audits the Emperor
- No single role can bypass review and act directly

Emperor Taizong figured this out 1,300 years ago — unchecked power inevitably produces errors. Life OS applies this wisdom to your personal decision-making.

## Inspiration

The Three Departments and Six Ministries AI multi-agent orchestration concept was inspired by the [Edict](https://github.com/cft0808/edict) project. Life OS extends the framework from software development to all areas of personal life, adding the Censorate, Remonstrator, Political Affairs Hall, and Hanlin Academy.

## License

Apache-2.0
