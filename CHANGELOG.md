# Changelog

## Versioning Rules

This project follows **Strict SemVer**: MAJOR (Breaking Change) · MINOR (new features) · PATCH (fixes and maintenance). Changes on the same day are merged into a single release, and every release gets a git tag.

---

## [1.6.2] - 2026-04-17 · Adjourn Defense + Wiki/SOUL Auto-Write + 10 DREAM Triggers

> Three reinforcements in one release: (1) bulletproof adjourn flow that cannot be partially skipped; (2) wiki and SOUL now auto-write under strict criteria instead of asking for confirmation; (3) DREAM gains 10 concrete auto-triggered actions.

### 🛡️ Adjourn 3-Layer Defense

Previous bug: ROUTER sometimes executed Phase 2 (knowledge extraction) in the main context instead of launching the ARCHIVER subagent, splitting the 4-phase flow.

Three independent defenses added:
- **SKILL.md + archiver.md wording** — HARD RULE forbidding ROUTER from any Phase content in the main context; explicit "Subagent-Only Execution" block in archiver.md
- **Adjourn State Machine in pro/CLAUDE.md** — legal/illegal state transitions enumerated; AUDITOR flags every violation to user-patterns.md
- **Mandatory launch templates** — SKILL.md's "Trigger Execution Templates (HARD RULE)" section pins the exact output pattern for Start Session / Adjourn / Review

### 📚 Wiki Auto-Write (no user confirmation)

Previous: archiver listed wiki candidates and asked user to pick which to save. This interrupted the flow and encouraged skipping.

New: archiver auto-writes under **6 strict criteria** + Privacy Filter:
1. Cross-project reusable
2. About the world, not about you (values → SOUL, not wiki)
3. **Zero personal privacy** — names, amounts, account IDs, specific companies, family/friend info, traceable date+location combos → stripped; if stripping makes the conclusion meaningless → discard
4. Factual or methodological
5. Multiple evidence points (≥2 independent)
6. No contradiction with existing wiki (contradictions → `challenges: +1` on existing entry, don't create competitor)

Initial confidence: 3+ evidence → 0.5; exactly 2 → 0.3; 1 or below → DISCARD.

User nudges post-hoc: delete file = retire, say "undo recent wiki" to rollback most recent auto-writes, or manually lower `confidence` below 0.3 to suppress.

### 🔮 SOUL Auto-Write + Continuous Runtime

Previous: SOUL dimensions only created through user confirmation; only surfaced periodically.

New:
- **ADVISOR auto-updates every decision** — increments `evidence_count` or `challenges` on existing SOUL dimensions after every Summary Report; detects new dimensions with ≥2 evidence points and auto-writes at `confidence: 0.3` with "What SHOULD BE" deliberately left empty for the user to fill when ready
- **REVIEWER mandatory SOUL reference** — every decision must cite relevant SOUL dimensions or explicitly note "no directly relevant dimension, this may open a new one"
- **SOUL Health Report in fixed briefing position** — every Start Session, the first block after Pre-Session Preparation is 🔮 SOUL Health Report (current profile with trend arrows, newly auto-detected dimensions awaiting user input, conflict warnings, dormant dimensions 30+ days, trajectory delta)

Confidence formula unchanged: `confidence = evidence_count / (evidence_count + challenges × 2)`.

### 💤 DREAM 10 Auto-Triggered Actions (REM stage)

REM now evaluates 10 concrete patterns and auto-acts on matches:

| # | Pattern | Auto-Action |
|---|---------|-------------|
| 1 | New project relationship | Write STRATEGIC-MAP candidate + flag for briefing |
| 2 | Behavior ≠ driving_force | Inject into next ADVISOR input |
| 3 | Wiki contradicted by new evidence | `challenges: +1` on that entry |
| 4 | SOUL dimension dormant 30+ days | Briefing warning |
| 5 | Cross-project cognition unused | Force-inject into next DISPATCHER |
| 6 | Decision fatigue detected | Suggest "no major decisions today" |
| 7 | Value drift in driving_force | Auto-propose SOUL revision |
| 8 | Stale commitment (30+ days no action) | Resurface in briefing |
| 9 | Emotional decision pattern | Next REVIEWER adds emotional-state check |
| 10 | Repeated identical decisions | Briefing: "Are you avoiding commitment?" |

All flags written to dream journal's `triggered_actions` YAML block. RETROSPECTIVE surfaces them in the fixed "💤 DREAM Auto-Triggers" briefing block at next Start Session.

### 🔬 Design Refinements (detailed specifications)

Building on the four conceptual pillars above, v1.6.2 also ships the detailed behavior specs:

**DREAM trigger detection logic** — each of the 10 triggers now has:
- A **hard threshold** (quantitative rule, auto-fires)
- **Soft signals** (LLM qualitative cues, fires with `mode: soft` + AUDITOR review required)
- Explicit data source, anti-spam 24h suppression, and structured output

Examples: decision-fatigue = "≥5 decisions in 24h AND second-half avg score ≤ first-half - 2"; value-drift = "≥3 challenges with ≤1 new evidence in 30d AND confidence drop >30%"; stale-commitment = "I will X / 我会 X / X する regex + 30 days no matching completion"; emotional-decision = "ADVISOR emotional flag + REVIEWER cool-off advised + session proceeded anyway"; repeated-decisions = "topic keyword overlap >70% with ≥2 past 30-day decisions". See `references/dream-spec.md` for all 10.

**ADVISOR SOUL Runtime unification** — merged the old read-only "SOUL Behavioral Audit" section into the new auto-update mechanism. One unified flow: per-dimension impact (support/challenge/neutral) → write evidence/challenge deltas → detect new dimensions → conflict warnings → output 🔮 SOUL Delta block. Runs every decision, not only at adjourn.

**SOUL snapshot mechanism for trend arrows** — archiver Phase 2 now dumps a minimal snapshot to `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md` at the end of every session (numerical metadata only, no duplicated content). RETROSPECTIVE reads latest snapshot at next Start Session and computes:
- `confidence_Δ > +0.05` → ↗
- `confidence_Δ < -0.05` → ↘
- `|confidence_Δ| ≤ 0.05` → →
Plus special states: 🌟 newly promoted to core, ⚠️ demoted from core, 💤 dormant, ❗ conflict zone. Archive policy: >30 days → `_archive/`, >90 days → delete (git + Notion retain).

**REVIEWER 3-tier SOUL reference strategy** — prevents noise when SOUL has many dimensions:
- **Tier 1** (confidence ≥ 0.7): reference ALL, no upper limit — core identity must be considered
- **Tier 2** (0.3 ≤ confidence < 0.7): top 3 semantically relevant via strong/weak-match judgment
- **Tier 3** (confidence < 0.3): count only, don't surface (ADVISOR tracks in Delta)

Decision challenging a Tier 1 dimension → REVIEWER adds ⚠️ SOUL CONFLICT warning at top of Summary Report (semi-veto signal). Every Tier 2 dimension evaluated is listed with inclusion reason so AUDITOR can review quality.

### Files Touched

- `SKILL.md` (version + trigger templates)
- `pro/CLAUDE.md` (state machines + wiki/SOUL auto-write descriptions)
- `pro/GEMINI.md` / `pro/AGENTS.md` (cross-platform Gemini CLI + Codex CLI parity)
- `pro/agents/archiver.md` (Phase 2 auto-write + snapshot dump + Phase 3 10-trigger detection logic)
- `pro/agents/advisor.md` (unified SOUL Runtime: 5 steps, every decision)
- `pro/agents/reviewer.md` (3-tier SOUL reference strategy)
- `pro/agents/retrospective.md` (Step 11 expanded to 11.1-11.6: snapshot read + trend computation)
- `references/wiki-spec.md` + 三語 (6 criteria + privacy filter + user nudges)
- `references/soul-spec.md` + 三語 (auto-write + snapshot mechanism + tiered reference)
- `references/dream-spec.md` + 三語 (10 triggers per-section with hard/soft detection)
- `references/data-layer.md` + 三語 (`_meta/snapshots/` in directory tree + auto-write reflected)
- `README.md` + 三語 (What's new in v1.6.2 + Section V rewritten + architecture diagram)
- `CHANGELOG.md` + 三語

### Migration

No user action required. Existing wiki/SOUL entries continue to work. New entries auto-write starting next session. First Start Session after upgrade will show "no trend data yet" until second session provides a snapshot baseline. To disable a specific auto-written entry without deleting it: set `confidence: 0.0` in the frontmatter.

---

## [1.6.1] - 2026-04-16 · Nine Themes — Every Culture, Every Style

> The theme system expands from 3 to 9 themes. Each language now offers three distinct governance styles: historical, modern government, and corporate.

### New Themes

**English** (3 total):
- 🏛️ Roman Republic — Consul, Tribune (veto inventor), Senate, Quaestor, Legatus
- 🇺🇸 US Government — Chief of Staff, Attorney General, NSC, Treasury, GAO
- 🏢 Corporate — CEO, General Counsel, CFO, VP Operations (existing, unchanged)

**中文** (3 total):
- 🏛️ 三省六部 — 丞相、中书省、门下省、六部、御史台 (existing, unchanged)
- 🇨🇳 中国政府 — 国务院总理、发改委、人大常委会、财政部、审计署
- 🏢 公司部门 — 总经理、战略规划部、法务合规部、财务部、内审部

**日本語** (3 total):
- 🏛️ 明治政府 — 内閣総理大臣、参議、枢密院、大蔵省、元老
- 🏛️ 霞が関 — 内閣官房長官、内閣法制局、財務省、会計検査院 (existing, unchanged)
- 🏢 企業 — 社長室、経営企画部、法務部、経理部、内部監査室

### Theme Selection UI Updated

The selector now groups by language. Trigger word inference is smarter:
- "上朝" → auto-loads 三省六部 (唐朝-specific word)
- "閣議開始" → auto-loads 霞が関 (modern government-specific)
- Generic triggers ("开始", "はじめる", "start") → show that language's 3 sub-choices

---

## [1.6.0] - 2026-04-15 · Theme Engine — One Engine, Every Culture

> A Japanese user tried Life OS and the experience was poor — not because the logic was wrong, but because "Three Departments and Six Ministries" is a Chinese cultural concept that creates a learning barrier for non-Chinese users. v1.6.0 solves this by separating the decision engine from its cultural presentation.

### The Change

Life OS is now a **universal decision engine** with **swappable cultural themes**. The governance logic (plan → review → veto → execute → audit) is identical across all themes — only the names, tone, and metaphors change.

### Three-Layer Architecture

**Layer 1: Engine** — 16 agents with functional IDs (ROUTER, PLANNER, REVIEWER, DISPATCHER, 6 domain analysts, AUDITOR, ADVISOR, COUNCIL, RETROSPECTIVE, ARCHIVER, STRATEGIST). Language-neutral, culture-neutral.

**Layer 2: Theme** — Swappable cultural skins that map functional IDs to familiar names:
- `zh-classical` — 三省六部 (Tang Dynasty governance): 丞相, 中书省, 门下省, 六部, 御史台...
- `ja-kasumigaseki` — 霞が関 (Japanese central government): 内閣官房長官, 内閣法制局, 財務省, 会計検査院...
- `en-csuite` — C-Suite (corporate executive): Chief of Staff, General Counsel, CFO, Internal Audit...

**Layer 3: Locale** — Auto-detects user language, recommends matching theme. User can switch at any time.

### Theme Selection UI

At the first Start Session, the RETROSPECTIVE agent presents a simple a/b/c choice:
```
🎨 Choose your theme:
 a) 🏛️ 三省六部 — Tang Dynasty governance (Chinese classical)
 b) 🏛️ 霞が関 — Japanese central government (Kasumigaseki)
 c) 🏛️ C-Suite — Corporate executive structure (English)

Type a, b, or c
```

- **Theme choice is per-session** — each terminal window can use a different theme independently
- Theme selection does not persist across sessions; each new session re-prompts
- Users can switch mid-session by saying "switch theme" / "切换主题" / "テーマ切り替え"

### What Changed

- **16 agent files renamed**: Chinese pinyin (chengxiang.md, zhongshu.md...) → functional English (router.md, planner.md...)
- **themes/ directory created**: 3 theme files (~60 lines each) define role mappings, tone, trigger words, output titles
- **i18n agent duplication eliminated**: 48 agent files (16 × 3 languages) → 16 files. Themes handle display, agents handle logic.
- **~42 translated agent/orchestration files deleted**: No longer needed — one source of truth per agent
- **departments.md → domains.md**: Six Ministries → Six Domains (PEOPLE, FINANCE, GROWTH, EXECUTION, GOVERNANCE, INFRA)
- **All orchestration protocols updated**: CLAUDE.md, AGENTS.md, GEMINI.md use functional IDs
- **All reference docs updated**: data-layer, data-model, strategic-map-spec, wiki-spec, soul-spec, dream-spec, scene-configs
- **All eval scenarios updated**: Test cases use functional IDs (router-triage.md, council-debate.md)

### Why This Matters

- **Japanese users** see 財務省, 法務省, 会計検査院 — zero learning curve
- **English users** see CFO, General Counsel, Internal Audit — immediately intuitive
- **Chinese users** still see 丞相, 中书省, 门下省 — nothing lost
- **Developers** maintain 16 agent files instead of 48 — every logic change applies once
- **New themes** require only one ~60-line file — no engine changes needed

### Zero Functionality Loss

All 28 Hard Rules preserved. All scoring rubrics intact. All output formats maintained (with theme-dependent names). SOUL, DREAM, Wiki, Strategic Map, Completion Checklist, veto loops, session lifecycle — everything works identically. Verified against the complete 34-item preservation checklist.

---

## [1.5.0] - 2026-04-15 · Strategic Map — From Project Assistant to Life Strategist

> Life OS could analyze any single project brilliantly but was blind to the connections between them. With many active projects sharing dependencies, resources, and hidden strategic purposes, the system needed a relationship layer. Strategic Map adds exactly that — and integrates deeply with SOUL, Wiki, and DREAM to form a unified cognitive system.

### The Problem

You have many projects. Some feed knowledge into others. Some share your limited time. Some exist for a stated purpose that differs from your real motivation. When one stalls, it silently blocks others. But the morning briefing showed a flat list with no relationships, no priorities, no "what should I actually do today?"

### What's New

**Strategic Lines** — Group projects by strategic purpose. Each line has a `purpose` (formal), a `driving_force` (what actually motivates you), and `health_signals` (what to watch). Multiple projects can serve one line with different roles: `critical-path`, `enabler`, `accelerator`, `insurance`.

**Flow Graph** — Define what flows between projects: `cognition` (knowledge), `resource` (deliverables), `decision` (constraints), `trust` (relationship capital). When a decision in Project A invalidates Project B's assumptions, the system warns you.

**Narrative Health Assessment** — No more "6/10 🟡" scores. Based on Klein's Recognition-Primed Decision model, the system matches projects to health archetypes (🟢 steady progress / 🟡 controlled wait / 🟡 momentum decay / 🔴 uncontrolled stall / 🔴 direction drift / ⚪ dormant) and writes a narrative: what's happening, what it means, what to do.

**Morning Briefing Upgrade** — The flat "Area Status" list becomes a strategic overview grouped by strategic lines, with blind spot detection and actionable recommendations:
- 🥇 Highest leverage action (with effort estimate and cost of inaction)
- 🥈 Worth attention
- 🟢 Safe to ignore (active suppression reduces cognitive load)
- ❓ Decisions needed (structural gaps for user to fill)

**Cross-Layer Integration** — Strategic Map works with SOUL, Wiki, and DREAM as one system:
- SOUL × Strategy: checks if your driving forces align with your stated values
- Wiki × Flows: verifies that cognition flows actually carry wiki knowledge (detects paper-only flows)
- DREAM × Strategy: REM stage uses the flow graph as scaffolding to discover cross-layer insights
- Patterns × Strategy: flags when your behavior contradicts your strategic priorities

**Blind Spot Detection** — Based on predictive coding neuroscience: the system actively looks for what's missing, not just what's present. Unaffiliated projects, broken flows, neglected driving forces, missing life dimensions, approaching time windows with no preparation.

### Agent Integration

| Agent | How they use the Strategic Map |
|-------|-------------------------------|
| Morning Court Official | Compiles STRATEGIC-MAP.md at Start Court (step 8.5). Briefing grouped by strategic lines |
| Prime Minister | Frames cross-project questions in strategic-line terms. Recommends time allocation by role |
| Secretariat | Adds cross-project impact dimensions when flows exist. Flags enabler dependency risks |
| Chancellery | Checks decision propagation (downstream impact) + SOUL-strategy alignment |
| Ministry of War | Weights task priority by strategic role. Recommends exploiting waiting periods |
| Court Diarist | Detects new relationships (Phase 2 candidates). Updates last_activity. DREAM REM enhanced with flow graph scaffolding |

### Data Architecture

- `_meta/strategic-lines.md` — Strategic line definitions (user-defined, like config.md)
- `projects/{p}/index.md` strategic fields — Per-project relationships (like existing status/priority fields)
- `_meta/STRATEGIC-MAP.md` — Compiled view (like STATUS.md / wiki/INDEX.md — never hand-edited)
- Cognitive pipeline: 5 stages → 6 stages (added "Strategize" between Associate and Emerge)
- Follows existing patterns: single source of truth, outbox merge, user-confirmed candidates, from-zero growth

### Design Foundations

Built on cognitive science research:
- **Goal Systems Theory** (Kruglanski 2002) — dual-layer intent (purpose vs driving_force)
- **Recognition-Primed Decision** (Klein 1998) — archetype matching + narrative assessment instead of numerical scoring
- **Predictive Coding** (Friston 2005) — blind spot detection through absence monitoring
- **Expected Value of Control** (Shenhav et al. 2013) — leverage-based action recommendations considering effort and opportunity cost
- **Biased Competition** (Desimone & Duncan 1995) — "safe to ignore" as active cognitive suppression

---

## [1.4.4b] - 2026-04-15 · Prevent Fabricated Timestamps

> LLMs were fabricating timestamps in session-id generation instead of reading the system clock. All session-id generation instructions now explicitly require running a date command. Template-style specs changed to command-style specs.

### Changes

- **qiju.md**: session-id step changed from template format to "run date command, use real output. HARD RULE."
- **data-layer.md + data-model.md**: session-id generation synced with same command-style wording
- All changes applied across EN/ZH/JA

---

## [1.4.4a] - 2026-04-15 · Enforce Agent File Loading

> LLMs were skipping adjourn phases by executing from memory instead of reading `qiju.md`. This patch adds 3-layer enforcement: explicit MUST-read routing in SKILL.md, a mandatory completion checklist in qiju.md, and a new orchestration rule requiring agent file loading on every trigger word.

### Enforcement Changes

- **SKILL.md**: Start Court / Adjourn routing changed from "Route to X" → "MUST read `pro/agents/X.md` and launch as subagent. HARD RULE."
- **qiju.md**: Added mandatory Completion Checklist — every phase must report a concrete value (commit hash, Notion sync status, etc.). Missing items = incomplete adjourn.
- **Orchestration Code of Conduct**: Added rule #6 — "Trigger words MUST load agent files. Never execute a role from memory without reading its definition file. HARD RULE."

### Also Included (audit remediation from same day)

- zaochao.md git health check: auto-fix → detect-report-confirm (GLOBAL.md Security Boundary #1)
- GLOBAL.md: "complete thought process" → "publishable reasoning summary" (cross-model portability)
- 14→16 subagent count fixed in remaining entry files
- Dead link `notion-schema.md` removed from AGENTS.md
- adapter-github.md: recovery commands changed to text blocks with manual-only headers
- evals/run-eval.sh: exit code capture, path sanitization, tri-lingual header support
- setup-hooks.sh: pre-flight validation before file writes
- lifeos-version-check.sh: XDG cache path, grep-based version parsing

---

## [1.4.4] - 2026-04-14 · Court Diarist (起居郎) — Session Close Specialist

> The Morning Court Official is split into two roles: the Morning Court Official handles session start (read), the Court Diarist handles session close (write). DREAM is absorbed into the Court Diarist — no more separate agent launch.

### 📝 New Role: Court Diarist (起居郎)

Named after the Tang Dynasty official who recorded the emperor's words and actions at court. The Court Diarist handles everything that happens when you say "退朝":

- **Phase 1 — Archive**: decisions, tasks, journal → outbox
- **Phase 2 — Knowledge Extraction** (core responsibility): scan ALL session materials (not just memorial) for wiki + SOUL candidates
- **Phase 3 — DREAM**: 3-day deep review (N1-N2 organize, N3 consolidate, REM creative connections) — no longer a separate agent
- **Phase 4 — Sync**: git push + Notion sync (4 explicit operations)

### Key Improvements
- **Knowledge extraction is now the Court Diarist's core mission** — not step 6.5 in a 298-line file
- **DREAM merged into closing flow** — one fewer agent launch, no more "last step that gets skipped"
- **Session conversation summary** passed to Court Diarist — can extract knowledge from PM direct-handle conversations, not just memorials
- **Notion sync guaranteed explicit** — 4 specific writes, failure reported (not silently skipped)
- 16 roles (was 15): Morning Court Official + Court Diarist replace the old combined role
- `dream.md` deleted — fully absorbed into `qiju.md`

---

## [1.4.3e] - 2026-04-13 · SKILL.md Slim Down — Pure Routing File

> SKILL.md compressed from 384 lines to 93 lines. Lite Mode removed. All detailed role definitions, output formats, and configuration are in agent files and reference docs where they belong.

### Token Savings
- **SKILL.md**: 384 → 93 lines (−291 lines ≈ −4,700 tokens/session)
- Removed: Censorate/Remonstrator/Political Affairs Hall/Morning Court Official detailed descriptions, Memorial format, Storage Configuration, Lite Mode flow, Two Types of Deliberation table, Pro Mode installation details
- All removed content already exists in agent files (`pro/agents/*.md`) or reference files (`references/*.md`)

### Code of Conduct Redistribution
- PM-relevant rules (8 rules) stay in SKILL.md
- Orchestration rules (#2 veto, #7 auto-trigger, #11 full output, #14 real subagents, #9 degradation) moved to `pro/CLAUDE.md` new "Orchestration Code of Conduct" section
- Universal agent rules already covered by `pro/GLOBAL.md`

### Ministry On-Demand Selection
- `zhongshu.md`: New "Ministry Selection (HARD RULE)" — only assign relevant ministries with justification
- `shangshu.md`: New "Dispatch Only Assigned Ministries (HARD RULE)" — don't dispatch unassigned ministries

### Lite Mode Removed
- Life OS's core value is independent subagent checks-and-balances — single-context simulation defeats this purpose
- README installation table: Lite Mode rows removed, note added that single-context platforms are not supported
- SKILL.md no longer needs to be self-contained for single-file platforms

---

## [1.4.3d] - 2026-04-13 · Version Check as Output Format Field

> Version detection moved from a standalone instruction (that LLMs skip) to a mandatory field in the Pre-Court Preparation output template (that LLMs reliably fill).

- **Version display is now a template field**: `🏛️ Life OS: v[local] | Latest: v[remote]` with update instructions shown inline
- **zaochao.md Mode 0 + Mode 1**: Step 3 now explicitly fetches remote version via WebFetch; both local and remote versions are mandatory output fields
- **chengxiang.md**: Pre-Court Preparation format synced with same version display
- **SKILL.md**: Removed verbose Version Self-Check section (moved to output format)
- Works because LLMs reliably fill output templates (HARD RULE #13) even when they skip standalone instructions

---

## [1.4.3c] - 2026-04-13 · Version Self-Check in SKILL.md

> Version detection moved from agent files to SKILL.md — the first file every LLM reads. Solves the bootstrap paradox where outdated agent files couldn't detect their own updates.

- **Version Self-Check section** added to SKILL.md top (before Prime Minister instruction): checks remote version via WebFetch, prompts update, reports failure
- **zaochao.md simplified**: Mode 0 and Mode 1 version check now references SKILL.md instead of duplicating WebFetch logic
- Works even when zaochao.md or other agent files are outdated — SKILL.md is always read first

---

## [1.4.3b] - 2026-04-13 · Knowledge Extraction in Adjourn Flow

> Wiki extraction no longer depends solely on DREAM. The adjourn flow now directly scans session outputs and proposes wiki candidates before DREAM runs.

- **Adjourn knowledge extraction (step 6.5)**: Wrap-up and Adjourn modes now scan session outputs for reusable conclusions → present wiki candidates to user → confirmed entries written to outbox wiki/
- **Outbox wiki merge**: Start Court merge now handles wiki/ files from outbox → moves to wiki/{domain}/{topic}.md
- **DREAM dedup**: DREAM N3 checks if the adjourn flow already extracted wiki candidates (via manifest) → skips re-proposing, focuses on missed conclusions only
- **Outbox format**: manifest.md now includes `wiki` count in outputs

---

## [1.4.3a] - 2026-04-13 · Wiki & SOUL Initialization Guidance

> The system now detects when wiki/ and SOUL.md haven't been initialized, and guides the user through first-time setup and legacy migration.

- **Wiki first-time initialization**: Morning Court Official detects empty wiki/ or missing INDEX.md → proposes extracting conclusions from existing decisions/journal
- **Wiki legacy migration**: Detects old-format wiki files (research reports without front matter) → proposes extracting conclusions and archiving originals
- **SOUL bootstrapping**: When SOUL.md doesn't exist, DREAM proposes initial entries from user-patterns.md at the first Adjourn Court
- **Start Court detection**: Steps 5.5 (SOUL check) and 10.5 (wiki health check) now report initialization status in the briefing

---

## [1.4.3] - 2026-04-13 · Wiki Activation — Knowledge Pipeline Comes Alive

> The cognitive pipeline's "settle → emerge" stages finally work. Wiki goes from an empty directory to an active knowledge participant.

### 📚 Wiki Specification (`references/wiki-spec.md`)

Wiki was designed into the second-brain but never plugged into any workflow — no agent wrote to it, no agent read it. Now it has all four elements:

- **Who writes**: DREAM proposes wiki candidates during N3 (alongside SOUL candidates)
- **When written**: After every Adjourn Court, confirmed by user at next Start Court
- **Who reads**: Prime Minister reads wiki/INDEX.md, Chancellery checks consistency, Censorate audits health
- **When read**: Every session start, every decision review, every patrol inspection

### 🔍 Prime Minister Knowledge Matching

The Prime Minister now scans wiki/INDEX.md before routing. If high-confidence entries exist for the current domain: "📚 We already have N established conclusions here. Start from known knowledge, or research from scratch?" — skips redundant analysis when user agrees.

### ⚖️ Chancellery Wiki Consistency Check

The Chancellery now checks new conclusions against established wiki entries. If a contradiction is detected: "⚠️ This contradicts [wiki entry] (confidence X)." Either the analysis needs revision, or the wiki needs updating.

### 🔱 Censorate Wiki Health Audit

Patrol inspection now covers wiki health: entries with confidence < 0.3 and no update in 90+ days (suggest retire), entries with challenges > evidence (suggest review), domains with decisions but no wiki entries (knowledge gap).

### 📨 Dept. of State Affairs Wiki Context

When the Prime Minister flags relevant wiki entries, the Dept. of State Affairs includes them in dispatch: "📚 Known Premises — start from here, do not re-derive."

### 🧠 Cognitive Pipeline Reordered

The pipeline now reflects actual information flow: `Perceive → Capture → Judge → Settle → Associate → Emerge`. Settle splits into SOUL (person) and Wiki (knowledge). Associate happens when the Prime Minister matches new requests against wiki. Emerge happens when DREAM's REM stage finds cross-domain connections.

### Design Principle

No new agents, no new flows. Wiki plugged into existing rhythms: DREAM writes → Morning Court Official compiles INDEX → Prime Minister reads → Chancellery checks → Censorate audits.

---

## [1.4.2] - 2026-04-12 · Outbox — Parallel Sessions Without Conflicts

> Multiple sessions can now work on different projects simultaneously. No git conflicts, no locks. Each session writes to its own outbox on adjourn; the next session to start court merges everything.

### 📮 Outbox Architecture

The old model assumed one session at a time and used a `.lock` file to warn about concurrency. The new model embraces parallelism:

- **Each session writes to its own isolated directory** (`_meta/outbox/{session-id}/`) on adjourn — decisions, tasks, journal entries, index deltas, pattern deltas, and a manifest
- **No direct writes to shared files** during wrap-up or adjourn — `projects/`, `STATUS.md`, and `user-patterns.md` are never touched until merge
- **Merge happens at Start Court** — the next session to start court scans all outboxes, merges them chronologically into the main structure, compiles STATUS.md, and cleans up
- **Session-id = `{platform}-{YYYYMMDD}-{HHMM}`**, generated at adjourn time (not session start)
- **Zero-conflict guarantee** — different directories, different files, no concurrent writes to the same path
- **Merge-lock** for the rare case of two simultaneous start courts (< 5 minutes, auto-cleanup)

### Scenarios Covered

- Single session, normal flow ✅
- Multiple platforms alternating ✅
- Multiple windows in parallel ✅
- Multiple computers ✅
- Session spanning multiple days ✅
- Same session, multiple start/adjourn cycles ✅
- Empty sessions (no output, no outbox) ✅
- Push failure (outbox saved locally, retried next time) ✅
- Lite users (no second-brain, no outbox) ✅
- Mobile Notion captures (inbox/, unchanged) ✅

### Files Changed

- `pro/agents/zaochao.md` — Mode 0/1 add outbox merge, Mode 3/4 rewritten to write outbox
- `references/data-model.md` — Session lock removed, outbox rules + manifest/delta formats added
- `references/data-layer.md` — Directory structure + Housekeeping/Wrap-Up flows updated
- `references/adapter-github.md` — Commit convention rewritten for outbox pattern
- `SKILL.md` — Parallel sessions mentioned in Storage Configuration

---

## [1.4.1] - 2026-04-12 · SOUL + DREAM — The System Learns Who You Are

> SOUL.md grows from your decisions to record who you are. DREAM processes memories while you're away — like the brain during sleep. Together, they give Life OS a self-awareness loop.

### 🔮 SOUL — User Personality Archive

Your values, beliefs, and identity — captured as evidence-based entries that grow from zero. Each entry has two sides: what you actually do (What IS) and what you aspire to (What SHOULD BE). The gap between them is where growth happens.

- **Grows organically** — starts empty, accumulates from decisions and behavior
- **Four sources** — DREAM discovers, Remonstrator observes, Hanlin Academy surfaces, you can write directly
- **User-confirmed** — system proposes, you decide. Nothing auto-written
- **Confidence-scaled influence** — new entries affect only the Remonstrator; deeply validated entries influence the entire system
- **Every role reads SOUL.md differently** — Prime Minister for sharper questions, Secretariat for relevant dimensions, Chancellery for value consistency, Remonstrator for behavioral audit, Hanlin Academy for thinker matching

### 💤 DREAM — AI Sleep Cycle

After every Adjourn Court, the system "sleeps" — inspired by human sleep architecture:

- **N1-N2 (Organize)** — classify inbox, flag expired tasks, find orphan files
- **N3 (Consolidate)** — extract recurring themes into wiki, update behavior patterns, propose SOUL entries
- **REM (Connect)** — discover cross-domain links, check value-behavior alignment, generate unexpected insights
- **Scope**: last 3 days only. Dream reports stored in `_meta/journal/` and presented at next Start Court
- **New agent**: `pro/agents/dream.md`

### 📐 New Reference Files

- `references/soul-spec.md` — SOUL format, lifecycle, confidence calculation, role usage rules
- `references/dream-spec.md` — DREAM trigger, three stages, output format, constraints

---

## [1.4.0] - 2026-04-12 · Hall of Human Wisdom + Three Chancelleries Deepened + Single Source of Truth

> The Hanlin Academy evolves from three thinking tools into a deep-dialogue hall with 70+ of history's greatest minds; five core roles get a serious upgrade; and a critical data integrity bug is fixed — `index.md` is now the single source of truth, `STATUS.md` is compiled from it.

### 🏗️ Architecture Fix — Single Source of Truth

`projects/{p}/index.md` is now the authoritative source for project version, phase, and status. `_meta/STATUS.md` is compiled from index.md files — never hand-written. This fixes a bug where STATUS.md and index.md could drift out of sync. Censorate patrol inspection now includes a mandatory version consistency lint rule.

### 🎋 Hanlin Academy → Hall of Human Wisdom

The Hanlin Academy is no longer just "first principles + Socratic method + Occam's razor." Now you can talk life with Socrates, dissect business logic with Musk, or let Laozi and Nietzsche argue about the meaning of existence.

- **18 domains, 70+ thinkers** — from science to philosophy, Eastern thought to legal justice, spanning every major dimension of human civilization
- **Deep roleplay** — not "using the Socratic method," but Socrates himself in conversation with you: his cadence, his examples, his relentless questioning
- **Three dialogue modes** — one-on-one deep dive, roundtable (multiple thinkers each weighing in), debate (adversarial exchange)
- **Independent subagents** — each thinker runs in its own context; the Hanlin Academy itself serves as moderator
- **Closing ritual** — the thinker offers a parting insight → the Hanlin Academy summarizes how your thinking shifted → saved to second-brain

### 🔍 Chancellery — From Rubber Stamp to Real Last Line of Defense

- **10/10/10 regret test** — you must answer separately for 10 minutes from now, 10 months, and 10 years; a vague "I won't regret it" doesn't pass
- **Red-team review** — assume the plan will fail; surface the most fragile assumptions, the luckiest dependencies, the risks you've been quietly downplaying
- **Structured veto format** — a veto is no longer just "not approved"; it must specify which dimension failed, what the core problem is, and exactly what to change

### 🏛️ Political Affairs Hall — From Fuzzy Triggers to Quantified Rules + Structured Debate

- **Quantified trigger** — if two departments' scores differ by ≥ 3, or one says go and one says stop, the Political Affairs Hall convenes automatically
- **New dedicated agent** — `zhengshitang.md`, with 3 rounds of structured debate: opening position → clash → final stance → ruling
- **Dept. of State Affairs chairs, you decide** — debate has rules and word limits; it won't collapse into monologue

### 📨 Dept. of State Affairs — From Task Assignment to Intelligent Scheduling

- **Dependency detection** — automatically identifies cross-department dependencies like "the Ministry of Revenue's conclusion affects the Ministry of War's plan," running group A before group B
- **Consultation mechanism** — the Ministry of War can ask "Revenue, give me one number: how much is available?" — the Dept. of State Affairs relays it without exposing the full report

### 🏛️ Prime Minister — Intent Clarification, Now Categorized

- **Five-category strategy** — decision (criteria? constraints?), planning (goal? resources?), confusion (emotion? real concern?), retrospective (standard? dimensions?), information (handle directly)
- **Emotion separation protocol** — when emotion and decision are tangled, one sentence acknowledges the feeling first, then the facts are separated out

### 💬 Remonstrator — From Observation to Learning

- **Behavioral pattern learning loop** — every new pattern or pattern shift is flagged and written to user-patterns.md
- **Cross-session trend analysis** — compares the last 3 reports: shifts in risk appetite, decision speed, follow-through, and what you're paying attention to
- **Positive reinforcement** — not just criticism. If the last report said "be more decisive" and you were, it says so explicitly

### ⚖️ System-Level

- **"Two kinds of council" comparison table** — SKILL.md now includes a side-by-side: Political Affairs Hall vs Hanlin Academy — one debates "should we do this," the other explores "who are you"
- **Prime Minister routing rule** — conflicting data goes to the Political Affairs Hall; value confusion goes to the Hanlin Academy

---

## [1.3.1] - 2026-04-12 · Process Must Be Visible

> Every subagent now shows its full thinking, and Pro mode is required to spin up real subagents — no more single-context simulations.

- **Emoji enforcement** — all subagent outputs must carry 🔎/💭/🎯 markers; omission is a violation
- **Real subagent enforcement** — in Pro environments, each role must be an independent agent call; simulating multiple roles in one context is banned
- **Role boundary lock** — HARD RULE #17: only the 15 defined roles exist; inventing officials like the Bureau of Transmission or Court of Judicial Review is forbidden
- **Inbox goes to Prime Minister** — the Prime Minister now officially owns inbox management
- **Morning Court auto-update** — the Morning Court Official checks the GitHub version on startup and runs platform update commands if a newer version is found
- **Git health check** — checks for worktree remnants and broken hooksPath before court opens
- **ko/es removed** — Korean and Spanish placeholders deleted; EN/ZH/JA only
- **Tag cleanup** — 13 old tags consolidated into 5 correct Strict SemVer tags
- **Second-brain tidy** — templates filled in with proper front matter; legacy directories (gtd/records/zettelkasten) removed

---

## [1.3.0] - 2026-04-10 · Three-Platform Pro Mode + Storage Abstraction Layer

> Life OS expands from Claude Code-only to a full three-platform Pro Mode across Claude + Gemini + Codex — and storage moves from Notion hardcoding to a pluggable three-backend architecture.

### Storage Abstraction Layer

One standard data model (6 types, 7 operations), three optional backends (GitHub / Google Drive / Notion) — load whichever adapter you choose. Multiple backends sync automatically; conflicts resolve by last-write-wins or user prompt.

### Cross-Platform Pro Mode

All 14 agent definitions are shared; orchestration files split by platform: `CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini CLI / Antigravity), `AGENTS.md` (Codex CLI). Each platform automatically uses its strongest model — no hardcoding.

### Trigger Word Standardization

English / Chinese / Japanese trigger words formally defined, resolving behavioral inconsistencies between Claude and Codex on commands like "open court."

---

## [1.2.0] - 2026-04-08 · Internationalization + Architecture Consolidation

> All 34 files translated into English as the primary version, with complete Chinese and Japanese translations — alongside a significant architectural consolidation.

### Internationalization

English is now the canonical version; Chinese and Japanese ship as i18n translations. The README is redesigned with shields.io badges and visual hierarchy.

### Architecture Consolidation

- **pro/GLOBAL.md** — shared rules across all 14 agents extracted into a single authoritative source; each agent file trimmed by ~30%
- **Cognitive pipeline** — five-stage information flow: perceive → capture → associate → judge → distill → emerge
- **Censorate audit mode** — a second operating mode beyond decision review: each ministry audits its own territory in the second-brain
- **Four-step knowledge extraction training** — user decides → accumulates examples → LLM distills rules → periodic correction

### 🔴 Breaking Change

Second-brain directory restructured: `zettelkasten/` → `wiki/`, `records/` → `_meta/journal/`, new `_meta/` system metadata layer added.

---

## [1.1.1] - 2026-04-05 · Data Layer Shift

> GitHub second-brain replaces Notion as the primary database; Notion steps down to mobile working memory.

- **GitHub as primary store** — .md + front matter, merging GTD + PARA + Zettelkasten
- **Morning Court Official three modes** — housekeeping (automatic), review (user-triggered), wrap-up (post-session)
- **Session binding** — each session locks to one project/area; all reads and writes stay in scope
- **Adjourn command** — pushes to GitHub + refreshes Notion
- **CC enforces Pro** — detecting Claude Code triggers mandatory independent subagent launch

---

## [1.1.0] - 2026-04-04 · Docs + Research Visibility + Memory Layer

> A complete documentation system goes live, every agent gains a visible research process, and the Prime Minister gets a memory layer and thinking tools.

- **Multi-platform install guide** — detailed steps for 7 platforms
- **All 14 agents gain 🔎/💭/🎯 research process display**
- **Remonstrator: 21 observation capabilities** — cognitive bias detection, emotional sensing, behavior tracking, decision quality assessment
- **Prime Minister intent clarification** — 2-3 rounds of dialogue before escalating; no more direct forwarding
- **Morning Court dashboard** — DTR / ACR / OFR + 4 weekly indicators
- **12 standard scene configs** — covering career, investment, relocation, entrepreneurship, and other major decision scenarios

---

## [1.0.0] - 2026-04-03 · Initial Release

> The Three Chancelleries and Six Ministries personal cabinet system launches. 15 roles. Checks, balances, and separation of powers.

- 15 roles: Prime Minister + Three Chancelleries + Six Ministries + Censorate + Remonstrator + Political Affairs Hall + Morning Court Official + Hanlin Academy
- Lite mode (single context) + Pro mode (14 independent subagents)
- 10 standard scene configurations
- Six Ministries × Four Bureaus detailed function definitions
- Apache-2.0 License
