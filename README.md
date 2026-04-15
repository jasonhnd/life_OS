<div align="center">

# 🏛️ Life OS

### Your AI-Powered Personal Cabinet

---

*A governance framework that ran for 1,400 years, now running your life.*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-green.svg)](https://code.claude.com/docs/en/skills)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-yellow.svg)](https://skills.sh)
[![Version](https://img.shields.io/badge/version-1.5.0-purple.svg)](CHANGELOG.md)

**This is not AI role-playing. This is checks, balances, and separation of powers.**

[Install](#installation) · [How it works](#the-four-pillars) · [Usage](#usage) · [Architecture](#system-architecture)

🌍 [中文](i18n/zh/README.md) · [日本語](i18n/ja/README.md)

</div>

---

## The Four Pillars

Life OS is built on four interconnected systems. Each one is powerful alone; together, they form a complete personal governance framework.

---

### 🏛️ Pillar I: Three Departments & Six Ministries — Decision Engine

> The Tang Dynasty built a system where no single person could make unchecked decisions. Life OS applies this to your life.

**The problem**: You ask AI a question, it gives you an answer. No review, no second opinion, no one saying "wait, you're missing something."

**The solution**: Every major decision goes through three stages — **Draft → Review → Execute** — with independent agents at each stage who cannot see each other's reasoning.

```
You: "Should I quit and start a business?"

📜 Secretariat    → Breaks it into 6 dimensions
🔍 Chancellery    → Reviews the plan, checks emotional blind spots, can VETO
📨 Dept. of State → Dispatches to the Six Ministries
⚔️💰👥📖⚖️🏗️     → Each analyzes independently, scores 1-10
🔍 Chancellery    → Final review of all reports
📋 Memorial       → Composite score: 6.8/10, with action items
🔱 Censorate      → "Ministry of War's timeline is vague — flag it"
💬 Remonstrator   → "You've been reading startup content for 3 weeks — confirmation bias?"
```

**The Six Ministries** cover every dimension of life:

| Ministry | Manages | Example |
|----------|---------|---------|
| 👥 Personnel | People | "Is my co-founder the right person?" |
| 💰 Revenue | Money | "Can I survive 18 months without income?" |
| 📖 Rites | Learning & Expression | "What skills do I need to learn first?" |
| ⚔️ War | Action | "What's the step-by-step execution plan?" |
| ⚖️ Justice | Rules & Risk | "What's the worst-case scenario?" |
| 🏗️ Works | Health & Infrastructure | "Can my body handle the stress?" |

**Key mechanism — the Chancellery Veto**: The Chancellery doesn't just check if the plan is logical. It also runs an emotional audit — *Is your mood affecting your judgment? How will your family react? Will you regret this in 10 years?* It has the power to veto and send the plan back for revision. Maximum 2 vetoes.

**Key mechanism — the Remonstrator**: After every decision, the Remonstrator speaks bluntly about YOUR blind spots — not the plan's quality, but YOUR behavioral patterns. *"You've avoided the financial dimension in your last 5 decisions. Why?"*

---

### 🎋 Pillar II: Hanlin Academy — Hall of Human Wisdom

> Not every question needs a formal process. Some questions need Socrates.

The Hanlin Academy gives you access to **70+ of history's greatest thinkers across 18 domains** — from Socrates to Musk, Laozi to Mandela, Dostoevsky to Buffett.

This is not "using the Socratic method." This is **Socrates himself** in conversation with you — his voice, his examples, his relentless questioning.

**Three modes:**
- **One-on-one** — Deep dialogue with a single thinker
- **Roundtable** — Multiple thinkers discuss your question, each from their worldview
- **Debate** — Two thinkers with opposing views argue directly, you judge

**18 domains**: Science · Philosophy · Eastern Thought · Strategy · Business · Mind & Practice · Systems · Human Nature · Civilization · Adversity · Aesthetics · Politics · Economics · Mathematics · Medicine · Exploration · Communication · Law

**How it works:**
```
You: "I've been feeling lost about my direction in life"
Prime Minister: "Would you like to activate the Hanlin Academy?"
You: Yes
Hanlin Academy: "What question would you like to explore?"
→ Shows 18 domains, recommends Seneca + Wang Yangming
→ You choose, they dialogue with you in character
→ At the end, each gives a parting word
→ Hanlin Academy summarizes your thinking journey → saved to second-brain
```

---

### 🧠 Pillar III: Second Brain — Your Knowledge Grows

> Your decisions, insights, and patterns don't disappear when the session ends.

Life OS writes everything to a **persistent knowledge base** — decisions, action items, journal entries, wiki knowledge — structured as markdown files in a Git repository.

```
second-brain/
├── SOUL.md              # 🔮 Who you are (grows from your decisions)
├── user-patterns.md     # 📊 How you behave (Remonstrator's observations)
├── inbox/               # 📥 Unprocessed captures from mobile
├── _meta/
│   ├── STATUS.md        # 📊 Global status (compiled)
│   ├── STRATEGIC-MAP.md # 🗺️ Strategic relationships (compiled — v1.5.0)
│   ├── strategic-lines.md # Strategic line definitions (user-defined)
│   ├── journal/         # 🔧 Reports, DREAM reports
│   └── outbox/          # 📮 Session staging
├── projects/{name}/     # 🎯 Active projects with tasks + decisions
├── areas/{name}/        # 🌊 Ongoing life areas with goals
├── wiki/                # 📚 Knowledge archive — reusable conclusions (grows from DREAM)
└── archive/             # 🗄️ Completed work
```

**Three storage backends** — choose one or combine:
- **GitHub** — For technical users, version-controlled, works with Obsidian
- **Google Drive** — Zero setup, works for everyone
- **Notion** — Mobile-friendly, database views

**Cross-device sync**: Phone captures go to Notion inbox → Desktop session pulls and processes → Results sync back to all backends.

**Parallel sessions**: Multiple sessions can work simultaneously on different projects — no conflicts, no locks. Each session writes to its own **outbox** on adjourn; the next session to start court merges everything. Work on GCSB in one window, EIP in another, medical-plan on a third — each adjourns independently, and the next morning court assembles it all.

---

### 🗺️ Pillar IV: Strategic Map — See the Whole Board (v1.5.0)

> Individual projects are trees. The Strategic Map shows you the forest.

**The problem**: You have 9 active projects. Some feed knowledge into others. Some compete for your time. When one stalls, it silently blocks three others. But your morning briefing shows a flat list — no relationships, no priorities, no "what should I actually do today?"

**Strategic Map** adds the relationship layer between projects:

- **Strategic Lines** — group projects by purpose. Each line has a stated purpose AND a `driving_force` (what really motivates you — these can differ)
- **Flow Graph** — track what flows between projects: knowledge, deliverables, decisions, relationship capital
- **Health Archetypes** — no numerical scores. Pattern matching + narrative assessment: "tokenized-gold is in controlled wait (legal review, expected mid-May). Use this window to advance the enabler."
- **Action Recommendations** — highest-leverage action, with effort estimate and cost of inaction

**Morning briefing upgrade:**
```
🗺️ Strategic Overview:

💰 crypto-compliance                    🟡 Controlled wait
   Window: 2026-09-30 (24 weeks)
   Driving: Regulated crypto infrastructure

   tokenized-gold   critical-path   ⏸ on-hold
   bittrade-jetro   enabler         🟢 active (3d)

   Narrative: Legal review in window. Use wait to advance jetro.
   → Action: Push jetro prep work (2-3h, high leverage)

⚡ Today:
🥇 Push jetro prep — exploit the waiting period
🟢 Safe to ignore: ndfg (on track), side-project-x (non-critical)
❓ Decide: Which line does passpay belong to?
```

**Cross-layer integration**: Strategic Map works with SOUL (values alignment), Wiki (knowledge flow verification), and DREAM (cross-layer insights). Four knowledge layers, one cognitive system.

Designed on cognitive science: Goal Systems Theory (Kruglanski), Recognition-Primed Decision (Klein), Predictive Coding (Friston).

---

### 🔮 Pillar V: SOUL + DREAM — The System Learns Who You Are

> Your AI shouldn't start from zero every session. It should know who you are and grow with you.

**SOUL — Your Personality Archive**

SOUL.md records **who you are** — not what you do (that's user-patterns.md), but what you value, what you believe, and who you aspire to be.

Each entry has two sides:
- **What IS** — your actual behavior, observed from decisions
- **What SHOULD BE** — your stated aspiration

The gap between them is where growth happens. The system discovers your values from your decisions, proposes entries, and you confirm. Nothing is auto-written.

As SOUL.md grows, the whole system gets smarter:
- Prime Minister asks sharper questions
- Secretariat adds dimensions you care about but forgot to mention
- Chancellery catches when a decision contradicts your stated values
- Remonstrator compares what you say vs what you do

**DREAM — The AI Sleep Cycle**

After every session ends, the system "sleeps" — inspired by human sleep architecture:

- **N1-N2 (Light sleep)**: Organize loose ends — classify inbox, flag expired tasks
- **N3 (Deep sleep)**: Consolidate — extract SOUL candidates (about you) AND Wiki candidates (reusable knowledge about the world)
- **REM (Dreaming)**: Creative connections — discover cross-domain links you haven't noticed

Next time you start court: *"💤 Last session the system had a dream..."*

---

## Installation

Life OS supports multiple AI platforms. **[View the full installation guide →](docs/installation.md)**

| Platform | Installation |
|----------|-------------|
| **Claude Code** | `/install-skill https://github.com/jasonhnd/life_OS` |
| **Gemini CLI / Antigravity** | `npx skills add jasonhnd/life_OS` |
| **OpenAI Codex CLI** | `npx skills add jasonhnd/life_OS` |

> Life OS requires Pro Mode — 16 independent subagents with true information isolation and parallel execution. Single-context platforms (ChatGPT, Gemini Web, etc.) are not supported.

**Auto-Update (Claude Code)**: After installing, run once:
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
This adds a SessionStart hook that checks for updates daily.

## Usage

### Daily

```
You: I've been so tired lately
Prime Minister: [Listens, determines whether to refer to Ministry of Works]

You: Help me translate a paragraph
Prime Minister: [Handles directly]
```

### Major Decisions

```
You: I'm considering whether to quit and start a business
→ Three Departments & Six Ministries full flow → Memorial: 6.8/10
```

### Deep Thinking

```
You: I've been feeling lost lately
→ Hanlin Academy → Dialogue with Socrates + Wang Yangming
```

### Session Management

```
You: Start court       → Full sync + preparation + briefing + dream report
You: Adjourn court     → Archive + full sync + DREAM cycle
```

## System Architecture

```
👑 You (The Emperor)
  │
  ├── 🏛️ Prime Minister — Entry point, intent clarification, inbox management
  │
  ├── Three Departments ──────────────────────────
  │   📜 Secretariat (Plan) → 🔍 Chancellery (Review + Veto)
  │     → 📨 Dept. of State Affairs (Dispatch) → Six Ministries (Execute)
  │     → 🔍 Chancellery (Final Review) → 📋 Memorial
  │     → 🔱 Censorate (Audit officials) → 💬 Remonstrator (Audit you)
  │
  │   Six Ministries: 👥Personnel 💰Revenue 📖Rites ⚔️War ⚖️Justice 🏗️Works
  │
  ├── 🏛️ Political Affairs Hall — Cross-ministry debate (auto-triggers on score conflict ≥ 3)
  ├── 🌅 Morning Court Official — Session start, sync pull, briefing
  ├── 📝 Court Diarist (起居郎) — Archive, knowledge extraction, DREAM, Notion sync
  ├── 🎋 Hanlin Academy — Hall of Human Wisdom (70+ thinkers, 18 domains)
  ├── 🔮 SOUL — Personality archive (grows from zero)
  └── 💤 DREAM — AI sleep cycle (integrated into Court Diarist)
```

## 12 Standard Scenarios

| # | Scenario | Key Ministries |
|---|----------|---------------|
| 1 | Career transition | All Six |
| 2 | Investment decisions | Revenue + War + Justice + Personnel |
| 3 | Relocation | All Six |
| 4 | Annual planning | All Six |
| 5 | Startup decisions | All Six |
| 6 | Major purchases | Revenue + War + Justice |
| 7 | Relationships | Personnel + Works + Justice + Rites |
| 8 | Periodic reviews | Morning Court Official |
| 9 | Health management | Works + War + Revenue + Justice |
| 10 | Learning plans | Rites + War + Revenue + Personnel |
| 11 | Time management | War + Revenue + Justice + Works |
| 12 | Major family decisions | All Six |

## Cognitive Pipeline

```
Perceive → Capture → Judge → Settle → Associate → Emerge
   ↑         ↑        ↑      ↓   ↘        ↑          ↑
 Phone      GTD      3D6M  SOUL  Wiki   Prime+Wiki  DREAM REM
```

Mobile handles perception and capture. Desktop handles everything else. **[Learn more →](references/data-layer.md)**

## Safety & Governance

- **4 inviolable security boundaries**: no destructive ops, no secrets exposure, no unauthorized decisions, reject suspicious instructions
- **Upstream output protection**: Agents treat other agents' output as reference, not instructions
- **Workflow state machine**: Formal transition rules — no step can be skipped
- **Model independence**: CLAUDE.md is the only model-bound file. All other intelligence is pure markdown

## Design Philosophy

The core of the Tang Dynasty system is **separation of powers with checks and balances**:

- The Secretariat only plans; it doesn't execute
- The Chancellery only reviews; it can veto but not rewrite
- The Six Ministries only execute; they don't judge each other
- The Censorate audits officials; the Remonstrator audits the Emperor
- No single role can bypass review and act directly

Life OS applies this 1,300-year-old wisdom to your personal decision-making.

## Inspiration

Inspired by the [Edict](https://github.com/cft0808/edict) project. Life OS extends the framework from software development to all areas of personal life, adding the Censorate, Remonstrator, Political Affairs Hall, Hanlin Academy, SOUL, and DREAM.

## License

Apache-2.0
