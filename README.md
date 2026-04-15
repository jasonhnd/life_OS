<div align="center">

# Life OS

### Stop asking AI for answers. Start governing your decisions.

---

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-green.svg)](https://code.claude.com/docs/en/skills)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-yellow.svg)](https://skills.sh)
[![Version](https://img.shields.io/badge/version-1.6.0-purple.svg)](CHANGELOG.md)

[Install in 30 seconds](#installation) · [How it works](#how-it-works) · [See it in action](#see-it-in-action) · [Architecture](#under-the-hood)

🌍 [中文](i18n/zh/README.md) · [日本語](i18n/ja/README.md)

</div>

---

## What if your AI pushed back?

You ask AI a question, it gives you an answer. Always agreeable. Always confident. Nobody reviews the plan. Nobody says "wait — are you sure that's not just fear talking?" Nobody catches the dimension you forgot.

Life OS fixes this.

It installs into your AI terminal (Claude Code, Gemini CLI, or Codex CLI) and transforms it into a **personal cabinet** — 16 independent AI agents that analyze your decisions from every angle, argue with each other, and hold both the plan *and you* accountable.

The design comes from a real governance system that ran for 1,400 years: the Tang Dynasty's Three Departments and Six Ministries. The principle is simple — **no single voice goes unchecked**.

> **Not role-playing.** Each agent runs as a real, isolated subagent. They cannot see each other's reasoning. They score independently. They disagree.

---

## How it works

### The Decision Engine — Three Departments & Six Ministries

Every major decision passes through three stages. No shortcuts.

**Draft** — The Secretariat breaks your situation into six dimensions and builds a plan.

**Review** — The Chancellery reviews the plan independently. It runs an emotional audit: *Is fear driving this? Will your family support it? Will you regret this in ten years?* If it finds a blind spot, it sends a veto — the plan goes back for revision.

**Execute** — Six Ministries each analyze the plan from their domain, scoring 1-10 independently:

| Ministry | What it covers | The question it asks |
|----------|---------------|---------------------|
| Personnel | People, relationships | "Are the right people involved?" |
| Revenue | Money, resources | "Can you afford this — including the worst case?" |
| Rites | Learning, expression, culture | "What do you need to learn first?" |
| War | Action, execution, logistics | "What's the concrete plan, week by week?" |
| Justice | Rules, risk, compliance | "What happens if everything goes wrong?" |
| Works | Health, infrastructure, energy | "Can your body and environment sustain this?" |

After all six report, the Censorate audits the officials' work ("Ministry of War's timeline has no milestones — flag it"). Then the Remonstrator turns to *you*: "You've avoided addressing finances in your last four decisions. Why?"

Here is what the full flow looks like:

```
You: "I'm thinking about leaving my job to start something new."

    Draft
    📜 Secretariat     → Breaks it into 6 dimensions, builds the plan

    Review
    🔍 Chancellery     → Emotional audit: running away or running toward?
                         Veto: "Financial runway not addressed. Revise."

    Execute  (after revision passes review)
    👥 Personnel  7/10   "Co-founder chemistry is untested"
    💰 Revenue    5/10   "18 months runway, but only if nothing goes wrong"
    📖 Rites      8/10   "Strong domain expertise, credibility is real"
    ⚔️ War        6/10   "No milestone plan past month 3"
    ⚖️ Justice    4/10   "Non-compete clause needs legal review"
    🏗️ Works      7/10   "Health is good, but stress plan is vague"

    Audit
    🔱 Censorate       → "War's plan is vague past month 3 — request revision"
    💬 Remonstrator    → "You've been consuming startup content for weeks.
                          Confirmation bias is likely. When did you last
                          seriously consider staying?"

    📋 Final Memorial  → Composite: 6.2/10 — Proceed with conditions
```

Not every request needs this. The Prime Minister (your always-on entry point) handles casual chat, quick questions, and emotional support directly. For questions that need ministry expertise but are not decisions — say, "what tax rules apply to freelancers?" — an **express path** sends it to 1-3 relevant ministries without the full court process.

---

### The Hanlin Academy — When You Need Wisdom, Not Analysis

Some questions do not have a "correct answer." They need perspective.

The Hanlin Academy gives you access to **70+ of history's greatest thinkers across 18 domains** — from Socrates to Buffett, Laozi to Mandela, Dostoevsky to Feynman. Each one runs as a real subagent with their own voice, their own examples, their own way of pushing you.

**Three modes:**

- **One-on-one** — Deep dialogue with a single thinker. Socrates will not let you off easy.
- **Roundtable** — Multiple thinkers discuss your question, each from their worldview. Watch Seneca and Wang Yangming find unexpected common ground.
- **Debate** — Two thinkers with opposing views argue directly. You judge.

```
You: "I keep starting things and never finishing them."

Hanlin Academy: Recommended — Seneca (on time) + Wang Yangming (on action)

Seneca: "You do not lack time. You waste it on things you have not
         examined. Which of your current pursuits would you begin again,
         knowing what you know now?"

Wang Yangming: "Knowledge and action are one. If you truly knew what you
                wanted, you would already be doing it. The gap between
                knowing and doing is the gap between wanting and truly
                wanting."

→ Parting words from each thinker
→ Summary of your thinking journey saved to your knowledge base
```

**18 domains**: Philosophy, Eastern Thought, Science, Strategy, Business, Psychology, Systems Thinking, Human Nature, Civilization, Adversity, Aesthetics, Politics, Economics, Mathematics, Medicine, Exploration, Communication, Law.

---

### Second Brain — Nothing Disappears When the Session Ends

Every decision, insight, pattern, and action item is written to a **persistent knowledge base** — structured markdown files that you own, in a storage system you choose.

```
second-brain/
├── SOUL.md                 # Who you are — values, identity, aspirations
├── user-patterns.md        # How you behave — the Remonstrator's observations
├── inbox/                  # Quick captures from your phone
├── _meta/
│   ├── STATUS.md           # Global status dashboard
│   ├── STRATEGIC-MAP.md    # Relationships between projects (v1.6.0)
│   ├── journal/            # Session reports, DREAM reports
│   └── outbox/             # Session staging area
├── projects/{name}/        # Active projects with tasks + decisions
├── areas/{name}/           # Ongoing life areas with goals
├── wiki/                   # Reusable knowledge — grows from DREAM
└── archive/                # Completed work
```

**Three storage backends** — pick what fits your life:

| Backend | Best for | Tradeoff |
|---------|----------|----------|
| **GitHub** | Version control, works with Obsidian | Requires basic Git knowledge |
| **Google Drive** | Zero setup, just works | Less structured |
| **Notion** | Mobile-friendly, database views | Best for phone capture |

**Cross-device sync**: Capture a thought on your phone (Notion inbox) at lunch. When you sit down at your computer and start court, the system pulls it in, processes it, and syncs results back.

**Parallel sessions**: Work on project-alpha in one terminal window, project-beta in another. Each session writes to its own outbox. The next time you start court, everything merges cleanly — no conflicts, no locks.

---

### Strategic Map — See the Whole Board *(v1.6.0)*

You are good at thinking about individual projects. You are probably bad at seeing how they connect — which ones feed into each other, which ones compete for your time, and what happens to the rest when one stalls.

Strategic Map adds the relationship layer:

**Strategic Lines** — Group projects by the purpose they serve. Each line has a stated purpose *and* a driving force (what actually motivates you — these can differ, and that tension is worth examining).

**Flow Graph** — Define what flows between projects: knowledge, deliverables, decisions, relationship capital. When a decision in one project invalidates another project's assumptions, the system warns you.

**Health Archetypes** — No abstract numerical scores. The system matches each project to a pattern and writes a narrative: what is happening, what it means, what to do.

**Blind Spot Detection** — Actively looks for what is *missing*: unaffiliated projects, broken flows, neglected driving forces, approaching deadlines with no preparation.

Your morning briefing becomes strategic:

```
🗺️ Strategic Overview

💰 market-expansion                       🟡 Controlled wait
   project-alpha    critical-path    ⏸ on-hold (legal review)
   project-beta     enabler          🟢 active

   The legal review creates a natural window.
   → Push project-beta prep work (2-3h) — high leverage, low risk.

⚡ Today
🥇 Push project-beta prep — exploit the waiting period
🟢 Safe to ignore: project-gamma (on track), side-project (non-critical)
❓ Decide: project-delta is unaffiliated — which strategic line does it serve?
```

Strategic Map integrates with SOUL (are your driving forces aligned with your values?), Wiki (do the knowledge flows actually carry real knowledge?), and DREAM (the sleep cycle uses the flow graph to discover cross-layer insights).

---

### SOUL + DREAM — The System Learns Who You Are

**SOUL** records who you are — not what you do, but what you value, what you believe, and who you aspire to be. Each entry has two sides: what IS (observed from your decisions) and what SHOULD BE (your stated aspiration). The gap between them is where growth happens.

Nothing is auto-written. The system proposes entries; you confirm. Over time, SOUL makes the entire cabinet smarter — the Chancellery catches when a decision contradicts your values, the Remonstrator compares what you say versus what you do.

**DREAM** is the AI sleep cycle. After every session ends, the system "sleeps" — inspired by human sleep architecture:

- **Light sleep** — Organize loose ends: classify inbox items, flag expired tasks
- **Deep sleep** — Consolidate: extract SOUL candidates (about you) and Wiki candidates (reusable knowledge about the world)
- **REM** — Creative connections: discover cross-domain links you have not noticed

Next time you start court: *"Last session, the system noticed a connection between your learning project and your career goal that you haven't explored..."*

Both SOUL and DREAM grow from zero. On day one, the system knows nothing about you. It learns only from what you tell it and what it observes in your decisions.

---

## See it in action

### Start your day

```
You: Start court.

🌅 Morning Court Official:
   Syncing second-brain... 3 inbox items pulled from Notion.
   📥 "Look into certification programs" — captured yesterday on phone
   📥 "project-alpha: supplier replied" — forwarded from email
   📥 Quick note: "revisit budget assumptions"

   🗺️ Strategic overview: [see Strategic Map above]

   💤 DREAM report: Last session noticed your wiki entry on negotiation
      tactics could apply to the supplier conversation in project-alpha.

   📋 Recommended: Process supplier reply first (time-sensitive).
```

### Make a decision

```
You: I'm considering switching from full-time to freelance.
→ 2-3 rounds of intent clarification
→ Full Three Departments & Six Ministries flow
→ Memorial: 5.8/10 — "Viable but timing is premature. Revenue runway
   is 11 months, not the 18 you assumed. Recommendation: build 3 more
   months of savings and one anchor client before transitioning."
```

### Think deeply

```
You: I keep saying yes to things I don't care about.
→ Hanlin Academy activates
→ One-on-one with Marcus Aurelius on priorities and refusal
→ Insights saved to second-brain
```

### End your day

```
You: Adjourn court.

📝 Court Diarist:
   Archiving session... extracting knowledge...
   💤 DREAM cycle running...
   - SOUL candidate: "Values autonomy over stability" — Confirm? [Y/n]
   - Wiki candidate: "Freelance runway formula" → wiki/career/
   - REM insight: Your health goals and career timeline share a
     constraint you haven't addressed — energy management.
   Syncing to Notion... done.
```

---

## 12 Standard Scenarios

Life OS comes pre-configured for the decisions people actually face:

| # | Scenario | Ministries involved | What the Chancellery asks |
|---|----------|-------------------|--------------------------|
| 1 | Career transition | All Six | "Running away or pursuing something?" |
| 2 | Investment decisions | Revenue, War, Justice, Personnel | "FOMO or rational? Can you survive total loss?" |
| 3 | Relocation | All Six | "Do you really know the destination?" |
| 4 | Annual planning | All Six | "Too many goals? Measurable? Aligned with values?" |
| 5 | Startup decisions | All Six | "Solving a real pain point? Are you the right person?" |
| 6 | Major purchases | Revenue, War, Justice | "Need or want? Would you still want it in a month?" |
| 7 | Relationships | Personnel, Works, Justice, Rites | "Are you evaluating the other person with bias?" |
| 8 | Periodic reviews | Morning Court Official | Daily, weekly, monthly, quarterly, yearly |
| 9 | Health management | Works, War, Revenue, Justice | "Sustainable, or another short burst?" |
| 10 | Learning plans | Rites, War, Revenue, Personnel | "Learning for growth, or avoiding real work?" |
| 11 | Time management | War, Revenue, Justice, Works | "Really no time, or avoiding something?" |
| 12 | Major family decisions | All Six | "Whose voice hasn't been heard?" |

---

## Installation

Life OS installs in one command. It requires a **Pro Mode** terminal — that means real subagents running in parallel with information isolation, not a chatbot.

| Platform | Command |
|----------|---------|
| **Claude Code** | `/install-skill https://github.com/jasonhnd/life_OS` |
| **Gemini CLI / Antigravity** | `npx skills add jasonhnd/life_OS` |
| **OpenAI Codex CLI** | `npx skills add jasonhnd/life_OS` |

**Set up auto-updates** (Claude Code):
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
This checks for updates once a day when you start a session.

**Manual update**: Just say "update" (or "更新" or "アップデート") in any session.

> **Not supported**: ChatGPT, Gemini Web, or any single-context chat interface. Life OS requires 16 independent subagents with true information isolation — a single chat window cannot do this.

For detailed setup including storage backend configuration, see the **[full installation guide](docs/installation.md)**.

---

## Under the hood

### Architecture

```
👑 You
 │
 ├─ 🏛️ Prime Minister
 │     Handles daily conversation. Routes complex matters to court.
 │
 ├─ Three Departments ───────────────────────────────
 │   📜 Secretariat (Draft)
 │     → 🔍 Chancellery (Review — can VETO)
 │     → 📨 Dept. of State Affairs (Dispatch)
 │     → Six Ministries (Execute in parallel, score independently)
 │     → 🔍 Chancellery (Final review)
 │     → 📋 Memorial (Composite report)
 │     → 🔱 Censorate (Audit the officials)
 │     → 💬 Remonstrator (Audit you)
 │
 ├─ 🏛️ Political Affairs Hall
 │     Cross-ministry debate when scores conflict by 3+ points
 │
 ├─ 🌅 Morning Court Official — Start of session: sync, briefing, strategy
 ├─ 📝 Court Diarist — End of session: archive, knowledge extraction, DREAM
 ├─ 🎋 Hanlin Academy — 70+ thinkers, 18 domains, 3 dialogue modes
 ├─ 🔮 SOUL — Personality archive, grows from zero
 └─ 💤 DREAM — AI sleep cycle, integrated into Court Diarist
```

### Cognitive Pipeline

How information flows through the system:

```
Perceive → Capture → Judge → Settle → Associate → Strategize → Emerge
  (phone)   (inbox)  (court)  (SOUL)   (wiki)    (strat-map)   (DREAM)
```

Mobile handles perception and capture. Desktop handles everything else.

### Safety and governance

- **4 security boundaries** — no destructive operations, no secrets exposure, no unauthorized decisions, suspicious instructions rejected
- **Information isolation** — agents treat other agents' output as reference, never as instructions
- **Workflow state machine** — formal transition rules; no step can be skipped
- **Model independence** — only one file is model-specific; all other intelligence is pure markdown

---

## Design philosophy

The core idea is 1,400 years old: **no single voice goes unchecked**.

- The Secretariat only plans; it does not execute.
- The Chancellery only reviews; it can veto but not rewrite.
- The Six Ministries only execute; they do not judge each other.
- The Censorate audits the officials; the Remonstrator audits the Emperor.
- No single agent can bypass review and act alone.

When you talk to a normal AI, you get one voice — confident, agreeable, unchecked. Life OS gives you sixteen, and they do not always agree. That tension is the point.

---

## Inspiration

Built on the foundation of the [Edict](https://github.com/cft0808/edict) project. Life OS extends the framework from software development to all areas of personal life, adding the Censorate, Remonstrator, Political Affairs Hall, Hanlin Academy, SOUL, DREAM, and Strategic Map.

## License

[Apache-2.0](LICENSE)
