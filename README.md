<div align="center">

# Life OS

### Your decisions deserve more than one voice. Now in your language, your culture.

---

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-green.svg)](https://code.claude.com/docs/en/skills)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-yellow.svg)](https://skills.sh)
[![Version](https://img.shields.io/badge/version-1.6.0-purple.svg)](CHANGELOG.md)

[Install in 30 seconds](#installation) · [How it works](#how-it-works) · [See it in action](#see-it-in-action) · [Architecture](#under-the-hood)

🌍 [中文](i18n/zh/README.md) · [日本語](i18n/ja/README.md)

</div>

---

## One engine. Three cultures. Your call.

Life OS installs into your AI terminal (Claude Code, Gemini CLI, or Codex CLI) and transforms it into a **personal cabinet** — 16 independent AI agents that analyze your decisions from every angle, argue with each other, and hold both the plan *and you* accountable.

The decision engine is the same for everyone: plan, review, veto, execute, audit. What changes is the world it speaks.

When you first start a session, you pick a theme:

```
🎨 Choose your theme:
 a) 🏛️ 三省六部 — Tang Dynasty governance (Chinese classical)
 b) 🏛️ 霞が関 — Japanese central government (Kasumigaseki)
 c) 🏛️ C-Suite — Corporate executive structure (English)

Type a, b, or c
```

Here is the same decision — "Should I leave my job?" — through all three:

```
  三省六部                  霞が関                    C-Suite
  ─────────                ─────────                ─────────
  📜 中书省 drafts plan     📜 内閣府 drafts plan      📜 VP Strategy drafts plan
  🔍 门下省 vetoes:         🔍 内閣法制局 vetoes:       🔍 General Counsel vetoes:
     "Financial runway        "財務的余裕が不明"          "Runway not addressed"
      not addressed"

  💰 户部  5/10            💰 財務省  5/10            💰 CFO  5/10
  ⚔️ 兵部  6/10            ⚔️ 防衛省  6/10            ⚔️ VP Ops  6/10
  ⚖️ 刑部  4/10            ⚖️ 法務省  4/10            ⚖️ CCO  4/10

  🔱 御史台 audits          🔱 会計検査院 audits       🔱 Internal Audit audits
  💬 谏官 challenges you    💬 内閣参与 challenges you  💬 Exec Coach challenges you

  📋 奏折: 5.8/10          📋 閣議決定書: 5.8/10       📋 Executive Brief: 5.8/10
```

Three different worlds. Identical rigor underneath. A Japanese user sees familiar ministry names with zero learning curve. An English user sees corporate roles they already understand. A Chinese user gets the classical system that inspired it all.

**Theme determines language.** After you pick a theme, every word of output — every agent, every report, every response — is in that theme's language. Chinese for 三省六部. Japanese for 霞が関. English for C-Suite. No mixing, no exceptions.

**Theme is per-session.** Each terminal window can use a different theme independently. You can switch mid-session at any time by saying "switch theme" (or "切换主题" or "テーマ切り替え"). The engine never changes — only the voice.

**Auto-inference from trigger words.** Say "上朝" and the Chinese theme loads automatically. Say "閣議開始" and the Japanese theme loads. Say "start" in English and the selector appears — because English could match any theme.

> **Not role-playing.** Each agent runs as a real, isolated subagent. They cannot see each other's reasoning. They score independently. They disagree.

---

## How it works

Life OS rests on five pillars. The **decision engine** is the core — everything else grows from it.

---

### I. The Decision Engine — Plan, Review, Veto, Execute, Audit

The engine runs 16 agents organized around a principle that is 1,400 years old: **no single voice goes unchecked**. The theme gives those agents names from your culture. The logic is always the same.

#### The 16 agents

| Agent | Function |
|-------|----------|
| ROUTER | Your always-on entry point — handles casual chat, routes complex matters to the engine |
| PLANNER | Breaks your situation into 3-6 dimensions and builds a structured plan |
| REVIEWER | Independent review with emotional audit, 10/10/10 regret test, SOUL consistency check, red-team challenge, and **veto power** (max 2 rounds) |
| DISPATCHER | Detects dependencies between domains, dispatches parallel or sequential execution |
| PEOPLE | Relationships, stakeholders, team dynamics |
| FINANCE | Money, assets, risk exposure |
| GROWTH | Learning, personal brand, communication |
| EXECUTION | Action plans, logistics, timelines |
| GOVERNANCE | Rules, risk, compliance, self-discipline |
| INFRA | Health, energy, living environment, digital infrastructure |
| AUDITOR | Audits the agents' work quality after every flow |
| ADVISOR | Audits *you* — surfaces behavioral patterns across your decisions |
| COUNCIL | Cross-domain debate — auto-triggers when domain scores differ by 3+ points |
| RETROSPECTIVE | Session start: sync, briefing, strategic overview |
| ARCHIVER | Session close: archive, knowledge extraction, DREAM, sync |
| STRATEGIST | Hall of Wisdom — 93 thinkers across 18 domains, 3 dialogue modes |

Every major decision passes through three stages. No shortcuts.

**Draft** — The PLANNER breaks your situation into dimensions and builds a plan.

**Review** — The REVIEWER examines the plan independently. It runs an emotional audit: *Is fear driving this? Will your family support it? Will you regret this in 10 minutes, 10 months, 10 years?* It checks alignment with your SOUL (values archive), your wiki (established knowledge), and your strategic map (cross-project impact). It red-teams the weakest assumption. If it finds a blind spot, it sends a veto — the plan goes back for revision. Maximum two veto rounds; the third pass must be approved.

**Execute** — Six domain analysts each score the plan 1-10 from their domain, independently:

| Domain | What it covers | The question it asks |
|--------|---------------|---------------------|
| People | Relationships, stakeholders | "Are the right people involved?" |
| Finance | Money, assets, resources | "Can you afford this — including the worst case?" |
| Growth | Learning, expression, culture | "What do you need to learn first?" |
| Execution | Action, logistics, timelines | "What's the concrete plan, week by week?" |
| Governance | Rules, risk, compliance | "What happens if everything goes wrong?" |
| Infrastructure | Health, energy, environment | "Can your body and environment sustain this?" |

Each domain has **four specialized divisions**. Finance, for example, has Income (salary, side income), Spending (budgets, habits), Assets (investments, real estate), and Reserves (emergency fund, insurance, retirement). The DISPATCHER routes to the right divisions automatically.

After all six report, the REVIEWER does a final review — and if scores conflict by 3+ points, the COUNCIL convenes a structured three-round debate. Then the composite Summary Report is produced. The AUDITOR checks the agents' work ("The execution plan has no milestones past month 3 — flag it"). The ADVISOR turns to *you*: "You've avoided addressing finances in your last four decisions. Why?"

Here is what the full flow looks like:

```
You: "I'm thinking about leaving my job to start something new."

    Draft
    📜 Planner          → Breaks it into 6 dimensions, builds the plan

    Review
    🔍 Reviewer         → Emotional audit: running away or running toward?
                          10/10/10 test: will you regret this in 10 years?
                          SOUL check: aligned with your stated values?
                          Veto: "Financial runway not addressed. Revise."

    Execute  (after revision passes review)
    👥 People     7/10   "Co-founder chemistry is untested"
    💰 Finance    5/10   "18 months runway, but only if nothing goes wrong"
    📖 Growth     8/10   "Strong domain expertise, credibility is real"
    ⚔️ Execution  6/10   "No milestone plan past month 3"
    ⚖️ Governance 4/10   "Non-compete clause needs legal review"
    🏗️ Infra      7/10   "Health is good, but stress plan is vague"

    Audit
    🔱 Auditor          → "Execution plan is vague past month 3 — request revision"
    💬 Advisor          → "You've been consuming startup content for weeks.
                           Confirmation bias is likely. When did you last
                           seriously consider staying?"

    📋 Final Report     → Composite: 6.2/10 — Proceed with conditions
```

#### Express analysis

Not every request needs a full court process. The ROUTER handles casual chat, quick questions, and emotional support directly. For questions that need domain expertise but are not decisions — say, "what tax rules apply to freelancers?" — an **express path** sends it to 1-3 relevant domain analysts directly, skipping the PLANNER, REVIEWER, AUDITOR, and ADVISOR. Quick answer, then: "This was an express analysis. Want the full deliberation?"

---

### II. The Hall of Wisdom — 93 Thinkers Across 18 Domains

Some questions do not have a "correct answer." They need perspective.

The STRATEGIST gives you access to **93 of history's greatest thinkers across 18 domains** — from Socrates to Buffett, Laozi to Mandela, Dostoevsky to Feynman. Each one runs as a real subagent with their own voice, their own examples, their own way of pushing you.

**Three modes:**

- **One-on-one** — Deep dialogue with a single thinker. Socrates will not let you off easy.
- **Roundtable** (2-4 thinkers) — Multiple thinkers discuss your question, each from their worldview. Watch Seneca and Wang Yangming find unexpected common ground.
- **Debate** (2 thinkers) — Two thinkers with opposing views argue directly over three structured rounds. You judge.

```
You: "I keep starting things and never finishing them."

Strategist: Recommended — Seneca (on time) + Wang Yangming (on action)

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

**18 domains**: Philosophy, Eastern Thought, Science, Strategy, Business, Psychology, Systems, Human Nature, Civilization, Adversity, Aesthetics, Politics, Economics, Mathematics, Medicine, Exploration, Communication, Law.

You can name **anyone** not on the built-in list — any historical figure — and the STRATEGIST will honor the request with equal depth. If your SOUL archive exists, the STRATEGIST uses it to recommend thinkers who address your specific tensions and contradictions.

---

### III. Second Brain — Nothing Disappears When the Session Ends

Every decision, insight, pattern, and action item is written to a **persistent knowledge base** — structured markdown files that you own, in a storage system you choose.

```
second-brain/
├── SOUL.md                 # Who you are — values, identity, aspirations
├── user-patterns.md        # How you behave — the advisor's observations
├── inbox/                  # Quick captures from your phone
├── _meta/
│   ├── STATUS.md           # Global status dashboard
│   ├── STRATEGIC-MAP.md    # Relationships between projects
│   ├── strategic-lines.md  # Strategic line definitions
│   ├── journal/            # Session reports, DREAM reports
│   └── outbox/             # Session staging area (one subdirectory per session)
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

You can use one, two, or all three. Multi-backend: writes go to all selected backends, reads come from the primary (auto-priority: GitHub > Google Drive > Notion). Conflict resolution follows last-write-wins with timestamp comparison.

**Cross-device sync**: Capture a thought on your phone (Notion inbox) at lunch. When you sit down at your computer and start a session, the system pulls it in, processes it, and syncs results back.

**Parallel sessions**: Work on project-alpha in one terminal window, project-beta in another. Each session writes to its own outbox directory. The next time you start a session, everything merges cleanly — no conflicts, no locks.

**First-run setup**: On your very first session, the system detects that no second-brain exists and walks you through creating one — choose your backend(s), and the full directory structure is created automatically.

---

### IV. Strategic Map — See the Whole Board

You are good at thinking about individual projects. You are probably bad at seeing how they connect — which ones feed into each other, which ones compete for your time, and what happens to the rest when one stalls.

Strategic Map adds the relationship layer.

**Strategic Lines** — Group projects by the purpose they serve. Each line has a stated purpose *and* a driving force (what actually motivates you — these can differ, and that tension is worth examining). Health signals define what to watch. Multiple projects can serve one line with different roles: critical-path (if this stalls, the line stalls), enabler (must complete first), accelerator (makes it faster), insurance (plan B).

**Flow Graph** — Define what flows between projects: knowledge, deliverables, decisions, relationship capital. When a decision in one project invalidates another project's assumptions, the system flags it immediately. When knowledge flows are defined but no wiki entries actually carry the knowledge, that is a broken flow.

**Health Archetypes** — No abstract numerical scores. The system matches each project to a pattern — steady progress, controlled wait, momentum decay, uncontrolled stall, direction drift, or dormant — and writes a narrative: what is happening, what it means, what to do.

**Blind Spot Detection** — Actively looks for what is *missing*: unaffiliated projects (not assigned to any strategic line), broken flows (defined but not flowing), driving force neglect (behavior misaligned with what you say matters), dimension gaps (entire life areas absent from all strategic lines), and approaching deadlines with no preparation.

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

Strategic Map grows from zero. If you have not defined any strategic relationships, the system operates normally with a flat project list. After a few sessions with multiple projects, DREAM may propose: "You have N active projects but no strategic relationships defined. Would you like to map how they relate?"

---

### V. SOUL + DREAM — The System Learns Who You Are

**SOUL** records who you are — not what you do, but what you value, what you believe, and who you aspire to be. Each entry has two sides: what IS (observed from your decisions) and what SHOULD BE (your stated aspiration). The gap between them is where growth happens.

Nothing is auto-written. The system proposes entries from four sources — DREAM (discovers patterns from recent behavior), ADVISOR (observes repeated value signals), STRATEGIST (you reveal values through deep dialogue), or direct input from you. You confirm every entry. Over time, SOUL makes the entire cabinet smarter — the REVIEWER catches when a decision contradicts your values, the PLANNER auto-adds dimensions you care about, and the ADVISOR compares what you say versus what you do.

Confidence grows with evidence. A newly observed pattern has low influence. An entry validated by dozens of decisions shapes how every agent thinks about your situation.

**DREAM** is the AI sleep cycle. After every session ends, the system "sleeps" — inspired by human sleep architecture:

- **Light sleep (N1-N2)** — Organize loose ends: classify unprocessed inbox items, flag expired tasks, detect orphan files
- **Deep sleep (N3)** — Consolidate: extract SOUL candidates (patterns about you) and Wiki candidates (reusable knowledge about the world) from the last 3 days of activity
- **REM** — Creative connections: discover cross-domain links you have not noticed. Uses the Strategic Map flow graph as scaffolding — checking SOUL-strategy alignment, wiki-flow completeness, and behavioral-pattern-strategic-priority consistency

Next time you start a session: *"Last session, the system noticed a connection between your learning project and your career goal that you haven't explored..."*

Both SOUL and DREAM grow from zero. On day one, the system knows nothing about you. It learns only from what you tell it and what it observes in your decisions.

---

## See it in action

### Start your day

```
You: Start session.

🌅 Session Start:
   Pick your theme: a) 三省六部  b) 霞が関  c) C-Suite

You: b

🌅 定例閣議:
   Syncing second-brain... 3 inbox items pulled from Notion.
   📥 "Look into certification programs" — captured yesterday on phone
   📥 "project-alpha: supplier replied" — forwarded from email
   📥 Quick note: "revisit budget assumptions"

   🗺️ Strategic overview: [see Strategic Map above]

   💤 DREAM report: Last session noticed your wiki entry on negotiation
      tactics could apply to the supplier conversation in project-alpha.

   📋 Recommended: Process supplier reply first (time-sensitive).
```

Behind the scenes, the session boot sequence ran 18 steps: theme resolution, directory detection, data layer check, git health check, full sync pull, outbox merge, platform and version check, project binding, context loading (user-patterns, SOUL, STATUS, lint state, project context, global overview), Strategic Map compilation, DREAM report presentation, wiki health check, and the final briefing.

### Make a decision

```
You: I'm considering switching from full-time to freelance.
→ 2-3 rounds of intent clarification (cannot be skipped — HARD RULE)
→ Full engine flow: draft → review (with possible veto) → execute (6 domains
  in parallel, each displayed as it completes) → final review → Summary Report
  → audit → advisor
→ Report: 5.8/10 — "Viable but timing is premature. Revenue runway
   is 11 months, not the 18 you assumed. Recommendation: build 3 more
   months of savings and one anchor client before transitioning."
```

### Think deeply

```
You: I keep saying yes to things I don't care about.
→ ROUTER detects abstract thinking need, asks: "Would you like to activate
  the Strategist?"
→ One-on-one with Marcus Aurelius on priorities and refusal
→ Parting words, journey summary, insights saved to second-brain
```

### End your day

```
You: End session.

📝 Archiver:
   Phase 1 — Archive: decisions, tasks, journal → outbox
   Phase 2 — Knowledge extraction: scanning session for wiki + SOUL candidates
   Phase 3 — DREAM:
     💤 N1-N2: 2 inbox items need classification
     💤 N3: SOUL candidate: "Values autonomy over stability" — Confirm? [Y/n]
            Wiki candidate: "Freelance runway formula" → wiki/career/
     💤 REM: Your health goals and career timeline share a constraint
            you haven't addressed — energy management.
   Phase 4 — Sync: git push... Notion sync... done.
   ✅ Completion checklist verified. Session archived.
```

---

## 12 Standard Scenarios

Life OS comes pre-configured for the decisions people actually face:

| # | Scenario | Domains involved | What the reviewer asks |
|---|----------|-----------------|----------------------|
| 1 | Career transition | All Six | "Running away or pursuing something?" |
| 2 | Investment decisions | Finance, Execution, Governance, People | "FOMO or rational? Can you survive total loss?" |
| 3 | Relocation | All Six | "Do you really know the destination?" |
| 4 | Annual planning | All Six | "Too many goals? Measurable? Aligned with values?" |
| 5 | Startup decisions | All Six | "Solving a real pain point? Are you the right person?" |
| 6 | Major purchases | Finance, Execution, Governance | "Need or want? Would you still want it in a month?" |
| 7 | Relationships | People, Infra, Governance, Growth | "Are you evaluating the other person with bias?" |
| 8 | Periodic reviews | Retrospective | Daily, weekly, monthly, quarterly, yearly |
| 9 | Health management | Infra, Execution, Finance, Governance | "Sustainable, or another short burst?" |
| 10 | Learning plans | Growth, Execution, Finance, People | "Learning for growth, or avoiding real work?" |
| 11 | Time management | Execution, Finance, Governance, Infra | "Really no time, or avoiding something?" |
| 12 | Major family decisions | All Six | "Whose voice hasn't been heard?" |

---

## Installation

Life OS installs in one command. It requires a **Pro Mode** terminal — that means real subagents running in parallel with information isolation, not a chatbot.

| Platform | Command |
|----------|---------|
| **Claude Code** | `/install-skill https://github.com/jasonhnd/life_OS` |
| **Gemini CLI / Antigravity** | `npx skills add jasonhnd/life_OS` |
| **OpenAI Codex CLI** | `npx skills add jasonhnd/life_OS` |

On first start, you pick your theme. The system auto-detects your language and recommends a match, but the choice is always yours. You can switch at any time by saying "switch theme."

**First run**: The system detects that no second-brain exists and walks you through setup — pick your storage backend(s), and the full directory structure is created automatically. On subsequent sessions, the system detects what kind of directory you are in: Life OS system repo (development), second-brain (normal use), or a project repo (connects to configured second-brain path).

**Set up auto-updates** (Claude Code):
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
This checks for updates once a day when you start a session.

**Manual update**: Say "update" (or "更新" or "アップデート") in any session.

> **Not supported**: ChatGPT, Gemini Web, or any single-context chat interface. Life OS requires 16 independent subagents with true information isolation — a single chat window cannot do this.

For detailed setup including storage backend configuration, see the **[full installation guide](docs/installation.md)**.

---

## Under the hood

### Architecture

```
👑 You
 │
 ├─ 🎨 Theme Layer
 │     zh-classical / ja-kasumigaseki / en-csuite
 │     Maps functional IDs → display names, tone, trigger words
 │     One file per theme (~60 lines). Adding a new theme = one new file.
 │
 ├─ ⚙️ Decision Engine (16 agents, culture-neutral)
 │  │
 │  ├─ 🏛️ ROUTER
 │  │     Handles daily conversation. Routes complex matters to the engine.
 │  │
 │  ├─ Three Stages ───────────────────────────────
 │  │   📜 PLANNER (Draft)
 │  │     → 🔍 REVIEWER (Review — can VETO, max 2 rounds)
 │  │     → 📨 DISPATCHER (Dispatch — parallel or sequential)
 │  │     → Six Domain Analysts (Execute in parallel, score independently)
 │  │     → 🔍 REVIEWER (Final review — may trigger COUNCIL)
 │  │     → 📋 Summary Report (Composite report)
 │  │     → 🔱 AUDITOR (Audit the agents)
 │  │     → 💬 ADVISOR (Audit you)
 │  │
 │  ├─ 🏛️ COUNCIL — Cross-domain debate when scores conflict by 3+ points
 │  ├─ 🌅 RETROSPECTIVE — Start of session: sync, briefing, strategy
 │  ├─ 📝 ARCHIVER — End of session: archive, knowledge extraction, DREAM
 │  ├─ 🎋 STRATEGIST — 93 thinkers, 18 domains, 3 dialogue modes
 │  ├─ 🔮 SOUL — Personality archive, grows from zero
 │  └─ 💤 DREAM — AI sleep cycle, integrated into ARCHIVER
 │
 └─ 💾 Storage Layer
       GitHub / Google Drive / Notion — pick one or combine
       Writes to all selected. Reads from primary. Cross-device sync.
```

### 6 Domains

Each domain has four specialized divisions:

| Domain | Divisions |
|--------|-----------|
| **People** | Talent (identifying people, evaluating partners), Evaluation (relationship health, social ROI), Relations (cultivation, reciprocity, important dates), Allocation (team building, delegation, family labor) |
| **Finance** | Income (salary, side income, passive channels), Spending (budgets, habits, subscriptions), Assets (investments, crypto, real estate), Reserves (emergency fund, insurance, tax, retirement) |
| **Growth** | Education (learning roadmap, skills, certifications), Image (personal brand, social presence), Writing (content planning, speech prep), Diplomacy (cross-cultural communication, networking) |
| **Execution** | Operations (project planning, task decomposition, deadlines), Equipment (tools, hardware, dev environment), Intelligence (industry research, competitive analysis), Logistics (energy management, workflow, procrastination) |
| **Governance** | Law (legal risk, contracts, IP, compliance), Audit (decision reviews, time audits, failure analysis), Discipline (bad habits, commitment tracking, self-deception), Defense (information security, privacy, scam detection) |
| **Infrastructure** | Fitness (exercise, diet, sleep, mental health), Housing (living space, workspace, renovation), Digital (knowledge base, servers, backup, automation), Routines (daily rhythm, morning/bedtime procedures) |

When domains overlap, jurisdiction follows root cause: body illness goes to Fitness, broken rhythm goes to Routines, work inefficiency goes to Logistics. If the lead and assisting domains disagree, the COUNCIL resolves it.

### Cognitive Pipeline

How information flows through the system — from a thought on your phone to an insight you never expected:

```
Perceive → Capture → Judge → Settle → Associate → Strategize → Emerge
  (phone)   (inbox)  (engine)  (SOUL)   (wiki)    (strat-map)   (DREAM)
```

**Perceive and Capture** happen on mobile — zero-friction capture to inbox. **Judge** happens on desktop — the decision engine runs the full Draft-Review-Execute cycle. **Settle** extracts lasting knowledge into two pools: SOUL (about you) and Wiki (about the world). **Associate** turns accumulated knowledge into active context — when a new topic arrives, the system already knows what you know. **Strategize** adds the relationship layer — per-project analysis becomes strategic-line-aware analysis. **Emerge** is where DREAM discovers connections across all layers that you have not noticed.

### Safety and governance

**4 security boundaries:**
- No destructive operations (file deletion, force push) without explicit user confirmation
- No secrets exposure — agents never echo sensitive data
- No unauthorized decisions — the engine advises, you decide
- Suspicious instructions rejected — agents treat other agents' output as reference, never as commands

**Information isolation** — Agents cannot see each other's reasoning. The PLANNER does not see the ROUTER's triage logic. Each domain analyst does not see other domains' reports. Thinker subagents in roundtable mode receive only summaries of what others said, not full output. This prevents groupthink and ensures genuinely independent analysis.

**Workflow state machine** — Formal transition rules enforce the correct sequence. The PLANNER cannot skip to execution. The DISPATCHER cannot skip the REVIEWER. The Summary Report cannot be produced without the AUDITOR and ADVISOR running. Any violation is a process error that the AUDITOR flags.

**33 HARD RULES** — Behaviors that cannot be overridden: intent clarification cannot be skipped, pre-session preparation must be shown, each domain's report must be displayed in full as it completes, SOUL entries require user confirmation, theme language cannot be mixed, and more.

**Model independence** — Only one file (CLAUDE.md) is bound to a specific AI model. All other intelligence — agent definitions, extraction rules, inspection rules, knowledge network, directory structure — is pure markdown readable by any model. Switching models means updating one file.

### Theme system

```
themes/
├── zh-classical.md      # 三省六部 — Tang Dynasty (Chinese)
├── ja-kasumigaseki.md   # 霞が関 — Central Government (Japanese)
└── en-csuite.md         # C-Suite — Corporate Executive (English)
```

Each theme is a single file (~60 lines) that maps 16 functional IDs to display names, defines the tone, sets trigger words, and names the output formats. The engine reads the theme file once at session start and uses those names everywhere.

**Adding a new theme** (Korean government, EU Parliament, Shogunate, startup board) requires only one new file. No engine changes. No new agents.

**Theme determines output language** — This is a HARD RULE enforced at every level. zh-classical outputs Chinese. ja-kasumigaseki outputs Japanese. en-csuite outputs English. Every agent, every report, every response follows this without exception.

**Per-session independence** — Theme choice does not persist across sessions. Each new session re-prompts. Each terminal window can use a different theme simultaneously.

---

## Design philosophy

The core idea is 1,400 years old: **no single voice goes unchecked**.

- The planner only plans; it does not execute.
- The reviewer only reviews; it can veto but not rewrite.
- The six domain analysts only execute; they do not judge each other.
- The auditor audits the agents; the advisor audits you.
- No single agent can bypass review and act alone.

When you talk to a normal AI, you get one voice — confident, agreeable, unchecked. Life OS gives you sixteen, and they do not always agree. That tension is the point.

The Theme Engine adds a second principle: **governance is universal, but culture is personal**. The logic that makes a good decision is the same everywhere. The language that makes it feel like *yours* is not. Life OS separates the two so you get both.

---

## Inspiration

Built on the foundation of the [Edict](https://github.com/cft0808/edict) project. Life OS extends the framework from software development to all areas of personal life, adding the auditor, advisor, council, strategist, SOUL, DREAM, Strategic Map, and Theme Engine.

## License

[Apache-2.0](LICENSE)
