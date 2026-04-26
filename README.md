<div align="center">

# Life OS

### Your decisions deserve more than one voice. Now in your language, your culture.

---

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-green.svg)](https://code.claude.com/docs/en/skills)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-yellow.svg)](https://skills.sh)
[![Version](https://img.shields.io/badge/version-1.7.3-brightgreen.svg)](CHANGELOG.md)

[Install in 30 seconds](#installation) · [How it works](#how-it-works) · [See it in action](#see-it-in-action) · [Architecture](#under-the-hood)

🌍 [English](README.md) · [中文](i18n/zh/README.md) · [日本語](i18n/ja/README.md)

</div>

---

> **Hermes Local** is the user-facing name for Life OS's local safeguards and
> automation: Layer 3 hooks plus Layer 4 Python tools. Internal labels remain
> `execution layer`, `Layer 3`, and `Layer 4`. Selected local-tool patterns are
> borrowed/forked from [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
> under the MIT License.

## One engine. Nine worlds. Your call.

Life OS installs into your AI terminal (Claude Code, Gemini CLI, or Codex CLI) and transforms it into a **personal cabinet** — 16 independent AI agents that analyze your decisions from every angle, argue with each other, and hold both the plan *and you* accountable.

The decision engine is the same for everyone: plan, review, veto, execute, audit. What changes is the world it speaks.

When you first start a session, you pick a theme:

```
🎨 Choose your theme:

English:
a) 🏛️ Roman Republic — Consul, Tribune, Senate
b) 🇺🇸 US Government — Chief of Staff, Attorney General, GAO
c) 🏢 C-Suite — CEO, General Counsel, CFO

中文:
d) 🏛️ 三省六部 — 丞相、中书省、门下省
e) 🇨🇳 中国政府 — 国务院总理、发改委、人大常委会
f) 🏢 公司部门 — 总经理、战略规划部、法务合规部

日本語:
g) 🏛️ 明治政府 — 内閣総理大臣、参議、枢密院
h) 🏛️ 霞が関 — 内閣官房長官、内閣法制局、財務省
i) 🏢 企業 — 社長室、経営企画部、法務部

Type a-i
```

Here is the same decision — "Should I leave my job?" — through all three:

```
  三省六部                  霞が関                    C-Suite
  ─────────                ─────────                ─────────
  📜 中书省 起草方案         📜 内閣府 起案             📜 VP Strategy drafts plan
  🔍 门下省 封驳：           🔍 内閣法制局 差し戻し：     🔍 General Counsel vetoes:
     "财务跑道未解决"          "財務的余裕が不明"          "Runway not addressed"

  💰 户部  5/10            💰 財務省  5/10            💰 CFO  5/10
  ⚔️ 兵部  6/10            ⚔️ 防衛省  6/10            ⚔️ VP Ops  6/10
  ⚖️ 刑部  4/10            ⚖️ 法務省  4/10            ⚖️ CCO  4/10

  🔱 御史台 审核             🔱 会計検査院 監査           🔱 Internal Audit audits
  💬 谏官 追问你             💬 内閣参与が問い返す      💬 Exec Coach challenges you

  📋 奏折: 5.8/10          📋 閣議決定書: 5.8/10       📋 Executive Brief: 5.8/10
```

Nine different worlds. Identical rigor underneath. Each language offers three governance styles — historical, modern government, and corporate — so every user finds a voice that fits. A Japanese user picks between Meiji-era ministers, Kasumigaseki bureaucrats, or corporate departments. An English user chooses Roman senators, US federal officials, or C-Suite executives. A Chinese user selects Tang Dynasty mandarins, modern State Council roles, or corporate divisions.

**Theme determines language.** After you pick a theme, every word of output — every agent, every report, every response — is in that theme's language. Chinese for 三省六部. Japanese for 霞が関. English for C-Suite. No mixing, no exceptions.

**Theme is per-session.** Each terminal window can use a different theme independently. You can switch mid-session at any time by saying "switch theme" (or "切换主题" or "テーマ切り替え"). The engine never changes — only the voice.

**Auto-inference from trigger words.** Say "上朝" and the 三省六部 theme loads automatically (唐朝-specific). Say "閣議開始" and the 霞が関 theme loads (modern government-specific). Generic triggers like "开始", "はじめる", or "start" show that language's three sub-choices — because the word alone does not distinguish historical, government, or corporate.

> **Not role-playing.** Each agent runs as a real, isolated subagent. They cannot see each other's reasoning. They score independently. They disagree.

---

## What's New in v1.7.3

v1.7.3 turns Cortex from declared-always-on into actually-always-on, and gives the Hermes tools real entry points users can see and trigger.

- **Cortex hook injection** — `pre-prompt-guard` now emits a system-reminder that forces ROUTER to launch all 5 Cortex subagents (hippocampus, concept-lookup, soul-check, gwt-arbitrator, narrator-validator) in parallel before answering, whenever the prompt has a decision keyword or exceeds 80 chars. Closes the silent-degradation gap found in v1.7.2 (0 audit trails across 17+ sessions).
- **narrator-validator audit trail HARD RULE** — frontmatter `tools` extended to `[Read, Bash, Write]`; audit trail JSON write to `_meta/runtime/<sid>/narrator-validator.json` is now mandatory per pro/CLAUDE.md §0.5.
- **4 slash commands wired** — `/compress` (inline context compression with `_meta/compression/` archive), `/search` (FTS5 cross-session search via `tools.session_search`), `/memory` (24-48h short-term memory via `tools.memory`), `/method` (method library management via `tools.skill_manager`). Installed by `setup-hooks.sh` to `~/.claude/commands/`.
- **Dead-weight removed** — `tools/prompt_cache.py` (118 lines, 0 callers, no value in Claude Code subscription mode) and its `docs/architecture/prompt-cache-strategy.md` deleted. References cleaned from `docs/architecture/hermes-local.md`.

Migration: re-run `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` to install the 4 new slash commands into `~/.claude/commands/`.

---

## What's New in v1.7.2.3

v1.7.2.3 clarifies Mode 0 ownership for RETROSPECTIVE. ROUTER now owns the Bash-rendered briefing skeleton and pre-renders roughly 80% of the report, while the subagent contributes only the `<!-- LLM_FILL: today_focus_and_pending_decisions -->` block with a short Today's Focus and Pending Decisions section. ROUTER splices that block back into the skeleton, keeping the briefing grounded, compact, and easier to audit.

---

## What's New in v1.7.2.1

v1.7.2.1 is a subtraction hotfix: it restores the theme aesthetic while removing extra reporting ceremony. The user-visible report shape is reduced from 17 H2 blocks to 6, the compressed wrapper requirement is removed, and version markers stay in fixed positions for easier checking. The result is fewer rules, cleaner briefings, and the same auditability without the visual clutter.

---

## What's New in v1.7.2

v1.7.2 turns the local execution surface into a clearer user story: Hermes Local is now the public name for the safeguards and automation that make Life OS enforceable outside the prompt. It covers Layer 3 hooks and Layer 4 Python tools, while internal specs keep the stable `execution layer`, `Layer 3`, and `Layer 4` labels. Cortex is now described as an always-on cognitive path for enabled workspaces: every user message can receive pre-router memory, concept, and SOUL signals, with graceful degradation when indexes or subagents are unavailable. The version-check hook now invalidates its daily cache against the remote SHA and supports `--force`, so same-day updates are no longer hidden by stale cache output. Hermes-derived prompt-cache and context-compression helpers improve speed and help large pasted transcripts stay manageable. Compression is only for local context management; subagent reports and audit evidence still stay literal where the workflow requires full fidelity.

---

## What's New in v1.7.1

v1.7.1 is a hardening release for transparency and evidence handling. Token use is now surfaced more explicitly so users can see why work was run, skipped, or escalated. ROUTER must paste subagent output without compressing it, preserving the full report trail for review. AUDITOR checks are more programmatic, and the release groups 27 fixes across hooks, i18n drift, Cortex emission, GWT clarity, DREAM output, force-push handling, marker disambiguation, and markdown frame resolution. R10 architectural shift: 11 of 18 retrospective steps moved from LLM to ROUTER Bash. LLM compliance gap closed by program substitution, not more spec rules. R11 adds runtime audit trail files so AUDITOR can verify across subagents directly, breaking the information-isolation bottleneck without exposing agent reasoning. R12: every '上朝' is fresh — LLM cannot reuse previous briefing. Forbidden phrases + length collapse + missing fresh markers all trigger C-fresh-skip P0.

---

## What's New in v1.7.0.1

Patch update: final briefing contracts are now explicit, Mode 0 self-checks Claude Code hooks, and Cortex is OFF / opt-in via `_meta/config.md`. Hook auto-install closes the test-machine deployment gap.
Anti-confabulation hardening prevents fabricated failure explanations from reaching users.
Source-grounded briefings now include PRIMARY-SOURCE measured-count markers, STATUS.md staleness suppression, automatic 30d-≥3 Compliance Watch banners, and ROUTER Bash fact-checks for numeric/version/path claims before user display.

---

## What's New in v1.7

**Cortex Cognitive Layer — GA release**

- 5 new Cortex capabilities: cross-session memory (hippocampus), signal arbitration (GWT), cited generation (narrator), concept graph, SOUL dimension detection
- 5 runtime hooks enforcing HARD RULEs (prevents COURT-START-001 class of violations)
- 10 Python tools + 3 libs (reindex / reconcile / stats / research / daily_briefing / export / sync_notion / seed / migrate / search / embed)
- 6 Cortex user-guides + v1.7-migration UX chapter
- cortex-spec + hippocampus-spec translated to Chinese and Japanese

Upgrade: `uv run life-os-tool migrate` (see [docs/guides/v1.7-migration.md](docs/guides/v1.7-migration.md))

See [CHANGELOG](CHANGELOG.md) for the full v1.7 commit chain and the COURT-START-001 v1.6.3 incident archive.

---

## What's new in v1.6.3

**Trust guard — five-layer defense against HARD RULE violations.** In testing, the author said "上朝" in the Life OS dev repo and the LLM bypassed the retrospective subagent, simulated 18 steps inline, and fabricated non-existent paths as authority. Documentation alone doesn't enforce anything — every HARD RULE was descriptive, with zero real enforcement. v1.6.3 ships five independent layers so every trigger word actually launches a real subagent:

1. **UserPromptSubmit hook** (`scripts/lifeos-pre-prompt-guard.sh`) — detects 上朝 / start / 閣議開始 / 退朝 etc. across all 9 themes, injects HARD RULE reminder into the model's context before any response
2. **Pre-flight Compliance Check** — ROUTER must output `🌅 Trigger: [word] → Theme: [name] → Action: Launch([agent]) [Mode]` before any tool call; missing line = logged violation
3. **Subagent self-check** — retrospective Mode 0 first line proves the subagent was actually launched (not main-context simulation)
4. **AUDITOR Compliance Patrol (Mode 3)** — 7-class violation taxonomy (A1 skip subagent, A2 skip directory check, A3 skip Pre-flight, B fabricate, C incomplete phase, D placeholder, E main-context phase) runs after every session start and archive
5. **Eval regression** — `evals/scenarios/start-session-compliance.md` codifies all 6 COURT-START-001 failure modes

**Dual-repo violations log** (md + git, per user's storage constraint): violations persist to `pro/compliance/violations.md` (dev repo, public) and `_meta/compliance/violations.md` (user second-brain, private). Escalation ladder: ≥3 same type in 30 days → stricter hook reminder; ≥5 → briefing `🚨 Compliance Watch`; ≥10 in 90 days → AUDITOR patrol every session.

**Still current from v1.6.2**: Bulletproof adjourn · Wiki auto-writes · SOUL auto-writes · DREAM 10 auto-triggers · SOUL trend arrows · REVIEWER 3-tier SOUL strategy · SOUL Health Report in briefing.

> **v1.6.3a hot patch (2026-04-21)** — closes the Layer 1 install gap. `scripts/setup-hooks.sh` now auto-registers the UserPromptSubmit hook (run once: `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`). Hook regex tightened (first-line + length checks) to reduce false positives on pasted content. New Class F (false positive) added to violation taxonomy.

See [CHANGELOG](CHANGELOG.md) for the full list and the original COURT-START-001 incident archive.

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

### V. SOUL + DREAM + Wiki — The System Learns Who You Are (v1.6.2: now fully automatic)

**SOUL** records who you are — not what you do, but what you value, what you believe, and who you aspire to be. Each entry has two sides: what IS (observed from your decisions) and what SHOULD BE (your stated aspiration). The gap between them is where growth happens.

**Auto-writes, with you in control** (v1.6.2). The system no longer asks you to confirm every entry. ADVISOR runs after every decision and increments evidence or challenges on existing SOUL dimensions. When a new value pattern accumulates 2+ pieces of evidence, SOUL auto-writes a new dimension at low confidence (0.3) — with the "What SHOULD BE" field deliberately left empty for you to fill in when you're ready. You stay in charge: edit freely, delete dimensions that don't fit, or say "undo recent SOUL" to roll back.

**Every session starts with a SOUL Health Report** — fixed position at the top of the briefing. Current profile with trend arrows, newly auto-detected dimensions awaiting your input, conflict warnings (dimensions your last 3 decisions all challenged), and dormant dimensions (30+ days without activation). You see the system's model of you every single time.

REVIEWER references SOUL in every decision. If a decision challenges a stated value, it surfaces the contradiction instead of rubber-stamping.

**DREAM** is the AI sleep cycle. After every session ends, the system "sleeps" — inspired by human sleep architecture:

- **Light sleep (N1-N2)** — Organize loose ends: classify unprocessed inbox items, flag expired tasks, detect orphan files
- **Deep sleep (N3)** — Consolidate: extract Wiki knowledge and update SOUL dimensions from the last 3 days of activity
- **REM (creative connections + 10 auto-triggers)** — Discovers cross-domain links you have not noticed, and automatically acts on 10 specific patterns: new project relationships, behavior diverging from stated values, wiki contradictions, dormant SOUL dimensions, unused cross-project cognition, decision fatigue, value drift, stale commitments (*"30 days ago you said you would do X — what happened?"*), emotional-state decision clusters, and repeated identical decisions (*"You're deciding X for the 4th time — are you avoiding commitment?"*)

All triggered actions flow into the next session's briefing in a fixed "DREAM Auto-Triggers" block. Next morning: *"Last session I noticed you're deciding the contract question again — this is the 3rd time. What's actually blocking you?"*

**Wiki** captures reusable knowledge about the world — not about you. After every session, the ARCHIVER auto-writes wiki entries that pass all 6 strict criteria: cross-project reusable, about the world (not you), **zero personal privacy** (no names, amounts, IDs, or traceable details — if stripping privacy makes the conclusion meaningless, it's discarded), factual/methodological, ≥2 independent evidence points, no contradiction with existing entries. Personal material belongs in SOUL; reusable knowledge belongs in Wiki. The two never mix.

All three systems grow from zero. On day one, the system knows nothing about you. It learns only from your decisions and observations — and it now learns continuously, not just when you ask.

---

## See it in action

### Start your day

```
You: Start session.

🌅 Session Start:
   Pick your theme: a-i (3 per language — historical / government / corporate)

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
   Phase 2 — Knowledge extraction (auto-write under strict criteria):
     🔮 SOUL auto-written: "Values autonomy over stability" — confidence 0.3
        (evidence: 2 decisions this session; "What SHOULD BE" left empty for you)
     📚 Wiki auto-written: "Freelance runway formula" → wiki/career/
        (passes 6 criteria + privacy filter: zero personal details)
     ❌ 1 wiki candidate discarded — contained personal amount, couldn't strip
   Phase 3 — DREAM:
     💤 N1-N2: 2 inbox items need classification
     💤 N3: new evidence for "deliberate decision-maker" dimension (+1)
     💤 REM: 🚨 Stale commitment detected — 32 days ago you said you would
            draft the freelance plan. Triggered for next session's briefing.
   Phase 4 — Sync: git push... Notion sync... done.
   ✅ Completion checklist verified. Session archived.
   ↩️ To undo any auto-write: delete the file, or say "undo recent wiki/SOUL"
      next session.
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

### Task-spawnable subagents

After `bash scripts/setup-hooks.sh`, life_OS auto-registers its Task-spawnable agents under `~/.claude/agents/lifeos-*.md`. Claude Code then recognizes calls such as `Task(lifeos-retrospective)` and `Task(lifeos-archiver)` as first-class targets instead of falling back to `general-purpose`.

The `lifeos-` prefix avoids collisions with other skills. Wrappers point at the canonical definitions under `pro/agents/*.md` in the skill, so updating the skill and rerunning setup refreshes agent behavior. There are 22 agent definition files; 21 are Task-spawnable wrappers, while `narrator.md` remains ROUTER-internal.

Uninstall: `bash scripts/unregister-claude-agents.sh`.

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
 │     9 themes across 3 languages (3 per language: historical / government / corporate)
 │     zh: 三省六部 · 中国政府 · 公司部门
 │     ja: 明治政府 · 霞が関 · 企業
 │     en: Roman Republic · US Government · C-Suite
 │     Maps 16 functional IDs → display names, tone, trigger words
 │     One file per theme (~60 lines). Adding a new theme = one new file.
 │
 ├─ ⚙️ Decision Engine (16 agents, culture-neutral)
 │  │
 │  ├─ 🏛️ ROUTER — Daily entry point
 │  │     Direct handling: casual chat, emotional support, quick questions
 │  │     Express 🏃: 1-3 domains for non-decision analysis
 │  │     Full deliberation ⚖️: 2-3 rounds of intent clarification → three stages
 │  │     Detects confusion/values questions → offers STRATEGIST
 │  │
 │  ├─ Three Stages ──────────────────────────────────────
 │  │   📜 PLANNER (Draft)
 │  │     Break into 3-6 dimensions, assign domains, set quality criteria
 │  │     Reference SOUL for value dimensions user didn't mention
 │  │     Check Strategic Map: does this affect downstream projects?
 │  │
 │  │   🔍 REVIEWER (Review — has veto power)
 │  │     😰 Emotional audit: fear? impulse? avoidance?
 │  │     👨‍👩‍👧 Relationship impact: how will family react?
 │  │     🔮 SOUL alignment: contradicts your stated values?
 │  │     ⏰ Regret test: 10 minutes / 10 months / 10 years?
 │  │     🎯 Red team: assume it fails — weakest assumption?
 │  │     🗺️ Strategic propagation: invalidates downstream premises?
 │  │     🚫 Veto → back to PLANNER (max 2 rounds)
 │  │
 │  │   📨 DISPATCHER (Dispatch)
 │  │     Detect data dependencies → parallel or sequential execution
 │  │     Inject wiki known premises: "start from these conclusions"
 │  │
 │  │   Six Domains (parallel execution, independent scoring 1-10)
 │  │     👥 PEOPLE — relationships, stakeholders, team dynamics
 │  │     💰 FINANCE — income, spending, assets, reserves
 │  │     📖 GROWTH — learning, personal brand, expression, cross-cultural
 │  │     ⚔️ EXECUTION — project mgmt, tools, research, energy
 │  │     ⚖️ GOVERNANCE — legal, audit, discipline, info security
 │  │     🏗️ INFRA — fitness, housing, digital infrastructure, routines
 │  │     Each domain has 4 specialized divisions (24 total)
 │  │
 │  │   🔍 REVIEWER (Final review) → 📋 Summary Report
 │  │   🔱 AUDITOR (Audit agent work quality)
 │  │   💬 ADVISOR (Audit YOUR behavioral patterns)
 │  │
 │  ├─ 🏛️ COUNCIL — Cross-domain debate
 │  │     Auto-triggers when domain scores differ by ≥3 points
 │  │     Manual trigger: "debate" / theme equivalent
 │  │     3 structured rounds: position → rebuttal → final statement
 │  │     Moderator assessment + recommendation (not decision)
 │  │
 │  ├─ 🌅 RETROSPECTIVE — Session start (18 steps)
 │  │     Step 1: 🎨 Theme selection (trigger word inference or a/b/c)
 │  │     Step 2: 📂 Directory type detection (system repo / second-brain / project)
 │  │     Step 3: 📦 Data layer check (first-run → create directory structure)
 │  │     Step 4-7: 🔄 Sync (config → git health → full pull → outbox merge)
 │  │     Step 8-9: 📋 Version check + project binding
 │  │     Step 10-14: 📖 Context loading (patterns → SOUL → STATUS → project → overview)
 │  │     Step 15: 🗺️ Strategic Map compilation (archetype matching + narrative + actions)
 │  │     Step 16: 💤 DREAM report (present last session's discoveries + candidates)
 │  │     Step 17: 📚 Wiki health check (compile INDEX)
 │  │     Step 18: 📋 Generate briefing (strategic overview + ⚡ today's actions + metrics)
 │  │
 │  ├─ 📝 ARCHIVER — Session close (4 phases)
 │  │     Phase 1 📦 Archive: decisions / tasks / journal → outbox
 │  │     Phase 2 🔍 Knowledge extraction (core mission · v1.6.2 auto-write):
 │  │       📚 Wiki → auto-written if passes 6 criteria + privacy filter
 │  │       🔮 SOUL → auto-written at confidence 0.3 if ≥2 evidence
 │  │       🗺️ Strategic relationship candidates → user confirms on the spot
 │  │       🔄 last_activity auto-update for touched projects
 │  │       ↩️ User nudges post-hoc: delete file or "undo recent wiki/SOUL"
 │  │     Phase 3 💤 DREAM (AI sleep cycle):
 │  │       N1-N2 💭 Light sleep: organize inbox, flag expired tasks
 │  │       N3 🧠 Deep sleep: consolidate Wiki knowledge + SOUL updates
 │  │       REM 🌙 Dreaming: creative connections + 10 auto-triggered actions
 │  │         · Stale commitments, value drift, decision fatigue, repeated decisions...
 │  │         · SOUL × strategy: driving forces aligned with values?
 │  │         · Wiki × flows: knowledge actually transferring between projects?
 │  │         · Patterns × priorities: avoiding a critical-path project?
 │  │     Phase 4 🔄 Sync: git push + Notion (4 operations)
 │  │     ✅ Completion checklist: every item must have a concrete value
 │  │
 │  └─ 🎋 STRATEGIST — Hall of Human Wisdom
 │        93 thinkers across 18 domains
 │        Socrates · Laozi · Buffett · Mandela · Feynman · Wang Yangming …
 │        🗣️ One-on-one: deep dialogue with one thinker
 │        🪑 Roundtable (2-4): multi-perspective discussion
 │        ⚔️ Debate (2): opposing views, 3 rounds, you judge
 │        Each thinker is an independent subagent with their own voice
 │        Ending: parting words → thinking journey saved to knowledge base
 │
 └─ 💾 Storage Layer
       GitHub / Google Drive / Notion (pick 1-3)
       ├── SOUL.md          🔮 Personality archive (grows from zero)
       ├── user-patterns.md 📊 Behavioral patterns (ADVISOR observations)
       ├── _meta/
       │   ├── STATUS.md         📊 Global status dashboard
       │   ├── STRATEGIC-MAP.md  🗺️ Strategic relationship map
       │   ├── journal/          📝 Reports + DREAM logs
       │   └── outbox/           📮 Session staging
       ├── projects/        🎯 Active projects with tasks + decisions
       ├── areas/           🌊 Ongoing life areas with goals
       ├── wiki/            📚 Reusable knowledge (grows from DREAM)
       └── archive/         🗄️ Completed work
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

**HARD RULES index** — Non-overridable behavior is tracked in [`references/hard-rules-index.md`](references/hard-rules-index.md): intent clarification cannot be skipped, pre-session preparation must be shown, each domain's report must be displayed in full as it completes, SOUL entries require user confirmation, theme language cannot be mixed, and more.

**Model independence** — Only one file (CLAUDE.md) is bound to a specific AI model. All other intelligence — agent definitions, extraction rules, inspection rules, knowledge network, directory structure — is pure markdown readable by any model. Switching models means updating one file.

### Theme system

9 themes across 3 languages — each language offers three governance styles: historical, modern government, and corporate.

```
themes/
├── zh-classical.md      # 🏛️ 三省六部 — Tang Dynasty (Chinese historical)
├── zh-gov.md            # 🇨🇳 中国政府 — Modern Chinese government
├── zh-corp.md           # 🏢 公司部门 — Corporate departments (Chinese)
├── ja-meiji.md          # 🏛️ 明治政府 — Meiji-era governance (Japanese historical)
├── ja-kasumigaseki.md   # 🏛️ 霞が関 — Central Government (Japanese modern)
├── ja-corp.md           # 🏢 企業 — Corporate structure (Japanese)
├── en-roman.md          # 🏛️ Roman Republic — Classical Roman governance (English historical)
├── en-usgov.md          # 🇺🇸 US Government — American federal government
└── en-csuite.md         # 🏢 C-Suite — Corporate Executive (English)
```

Each theme is a single file (~60 lines) that maps 16 functional IDs to display names, defines the tone, sets trigger words, and names the output formats. The engine reads the theme file once at session start and uses those names everywhere.

**Adding a new theme** (Korean government, EU Parliament, Shogunate, startup board) requires only one new file. No engine changes. No new agents.

**Theme determines output language** — This is a HARD RULE enforced at every level. All Chinese themes output Chinese. All Japanese themes output Japanese. All English themes output English. Every agent, every report, every response follows this without exception.

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
