# Changelog

## Versioning Rules

This project follows **Strict SemVer**: MAJOR (Breaking Change) · MINOR (new features) · PATCH (fixes and maintenance). Changes on the same day are merged into a single release, and every release gets a git tag.

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
