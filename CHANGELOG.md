# Changelog

## Versioning Rules

This project follows **Strict SemVer**:

- **MAJOR** (X.0.0) — Breaking changes that require user migration (directory restructure, config format change, etc.)
- **MINOR** (0.X.0) — New features, backward compatible, no user action needed
- **PATCH** (0.0.X) — Bug fixes, documentation, i18n sync, wording changes

Additional rules:
- Same-day changes are batched into a single release
- No `a`/`b`/`rc` suffixes
- Every release gets a git tag

---

## [1.3.1] - 2026-04-12

### Changed — Process Visibility + Role Governance + Maintenance

- **Code of Conduct #11 strengthened** — all subagent output must display complete process with mandatory emoji markers (🔎/💭/🎯/🔄/✅/⚠️). No batching, no summarizing, no omitting any step
- **Code of Conduct #14 strengthened** — Pro environments must launch real independent subagents (separate context per role). Single-context simulation absolutely prohibited. If platform cannot launch subagents, explicitly notify user and fall back to Lite mode
- **Code of Conduct #17 added** — only the 15 defined roles exist. Creating or referencing historical offices not in the system (通政使司, 大理寺, etc.) is prohibited
- **Prime Minister gains inbox management** — inbox checking, triaging, and reporting added to Prime Minister's responsibilities
- **GLOBAL.md research process upgraded** — emoji markers mandatory, must show specific URLs/file paths consulted, omitting any marker is a process violation
- **Morning Court Official git health check** — step 1.5 added to Start Court: checks for broken worktrees, stale hooksPath, and dead references before sync
- **adapter-github.md worktree maintenance** — prevention and recovery procedures for worktree path breakage after repo migration
- **installation.md troubleshooting expanded** — added git fatal error after repo migration fix
- **ko/es language support removed** — Korean and Spanish placeholders deleted, language links updated to EN/ZH/JA only
- **Git tags cleaned** — 13 old tags removed, 5 correct Strict SemVer tags created
- **second-brain templates standardized** — all templates now use YAML front matter matching data-model.md; added task.md and capture.md
- **second-brain old directories removed** — gtd/, records/, zettelkasten/, test-results/ deleted; .gitignore updated

## [1.3.0] - 2026-04-10

### Added — Storage Abstraction Layer + Cross-Platform Pro Mode

**Storage Abstraction Layer**
- **`references/data-model.md`** — Standard data model: 6 types (Decision/Task/JournalEntry/WikiNote/Project/Area) with field definitions, 7 standard operations (Save/Update/Archive/Read/List/Search/ReadProjectContext)
- **`references/adapter-github.md`** — GitHub backend: .md + front matter format, directory paths, query via grep/glob, change detection via git log
- **`references/adapter-gdrive.md`** — Google Drive backend: same .md format, Google Drive MCP calls, change detection via modifiedTime
- **`references/adapter-notion.md`** — Notion backend: standard field to Notion property mapping, Notion MCP calls, change detection via last_edited_time
- **Multi-backend support** — Users choose 1, 2, or all 3 backends (GitHub/GDrive/Notion). Multi-backend: writes to all, reads from primary (auto: GitHub > GDrive > Notion)
- **Cross-device sync** — Full sync on every session start: query all backends for changes since last sync, timestamp comparison, conflict resolution (last write wins, <1min = ask user)
- **Trigger word table** — Defines all trigger words in English, Chinese, and Japanese for 5 actions (Start Court / Review / Adjourn Court / Quick Analysis / Court Debate)
- **Start Court / Adjourn Court** — "Start Court" = full sync PULL + preparation + briefing. "Adjourn Court" = full sync PUSH + archive

**Cross-Platform Pro Mode**
- **`pro/GEMINI.md`** — Gemini CLI / Antigravity orchestration file. 14 subagents with full workflow state machine, information isolation, and parallel Six Ministries execution
- **`pro/AGENTS.md`** — OpenAI Codex CLI orchestration file following the AGENTS.md open standard
- **Platform auto-detection** — SKILL.md detects the runtime platform and loads the correct orchestration file automatically
- **Model-agnostic mapping** — Each platform automatically uses its strongest available model. No hardcoded model names — future model upgrades require zero changes
- **Troubleshooting guide** — Added to `docs/installation.md` covering common issues (worktree context overflow, Pro Mode not activating)

### Changed
- **SKILL.md** — "Data Layer" → "Storage Configuration" with multi-backend table; Pro Mode section rewritten for three platforms; Code of Conduct #14 updated to "Pro environment forces Pro mode"
- **docs/installation.md** — Restructured: Pro Mode platforms listed first, added Gemini/Codex Pro Mode sections, Troubleshooting section, updated FAQ
- **README.md** — Installation table now shows Mode column (Pro/Lite) for each platform

### Design Principle

**One set of agents, three platforms.** All 14 agent definitions (`pro/agents/*.md`) and global rules (`pro/GLOBAL.md`) are shared. Only the orchestration files differ per platform.

## [1.2.0] - 2026-04-08

### Added — Internationalization + Architecture Consolidation

- **Full English translation** — All 34 files translated to English as primary version
- **i18n directory** — zh/ (Chinese), ja/ (Japanese) full translations
- **Visual README redesign** — Centered header, shields.io badges, visual hierarchy
- **pro/GLOBAL.md** — Universal rules for all agents extracted into a single source of truth: Research Process (🔎/💭/🎯), Progress Reporting (🔄/🔎/💡/✅), Upstream Output Protection, Security Boundaries (4 inviolable rules), Universal Anti-Patterns, Model Independence
- **Workflow State Machine** — Formal state transition table in pro/CLAUDE.md defining legal and illegal jumps between workflow steps

### Changed
- **14 agent files simplified** — Each agent now references pro/GLOBAL.md. Average 30% reduction per file
- **Cognitive pipeline model** — Five-stage information flow: Perceive→Capture→Associate→Judge→Settle→Emerge
- **Censorate patrol inspection mode** — New second operating mode alongside decision review. Three trigger levels: startup (>4h idle), post-sync, deep (weekly/manual)
- **Knowledge extraction mechanism** — Four-step training: user decides → accumulate samples → LLM induces rules → periodic correction
- **Model independence declaration** — CLAUDE.md is the only model-bound file. All other intelligence is pure markdown

### 🔴 Breaking Change — Second Brain Directory Restructure

- `zettelkasten/` → `wiki/` — Simpler naming
- `records/journal/` → `_meta/journal/` — System logs move to _meta
- Added `_meta/` system metadata layer (STATUS.md, MAP.md, roles/, extraction and lint rules)
- Removed `records/` and `gtd/` directories

## [1.1.1] - 2026-04-05

### Changed — Data Layer Architecture + Session Binding

- **GitHub second-brain replaces Notion as primary data store** — Notion downgraded to "working memory" (mobile sync)
- **GitHub second-brain directory structure** — Fusion of GTD + PARA + Zettelkasten methodologies
- **Morning Court Official three operating modes** — Housekeeping (auto-start), Review (user-triggered), Wrap-up (post-workflow)
- **Session-level project binding** — Each session confirms associated project/area; all reads/writes scoped to that project
- **Adjourn Court command** — Wrap-up: push to GitHub + refresh Notion memory
- **CC environment enforces Pro mode** — Hard rule: Claude Code detected → must use independent subagents
- **Sync mechanism** — git commit = Notion update, mechanically bound
- **/save command** — Save ideas to second-brain while working in any project repo

## [1.1.0] - 2026-04-04

### Added — Documentation + Research Process + Memory Layer

- **Multi-platform installation guide** (`docs/installation.md`) — Steps for Claude Code, Claude.ai, Cursor, Gemini CLI, Codex CLI, ChatGPT, Gemini Web
- **Second Brain setup guide** (`docs/second-brain.md`) — Notion database creation tutorial
- **Token consumption breakdown** (`docs/token-estimation.md`) — 8 scenarios, monthly cost estimates
- **Eval system** (`evals/`) — 3 test scenarios, scoring criteria, automation script
- **Notion database schema** (`references/notion-schema.md`) — Complete field definitions
- **All 14 agents gain research process display** — 🔎 What I'm researching / 💭 What I'm thinking / 🎯 My judgment
- **Remonstrator 21 observation capabilities** — Cognitive bias scanning (7), Emotion detection (3), Behavioral tracking (7), Decision quality signals (7), Positive signals (1)
- **Prime Minister three thinking tools** — First Principles, Socratic Questioning, Occam's Razor
- **Prime Minister intent clarification flow** — 2-3 rounds of dialogue before escalation
- **Prime Minister memory layer** — Auto-queries 3 Notion sources before escalation
- **Morning court metrics dashboard** — 7 metrics: DTR, ACR, OFR + 4 weekly metrics
- **user-patterns.md long-term memory mechanism** — Behavioral pattern profiles
- **10 + 2 standard scenario configurations** — Time management, major family decisions added
- **SKILL.md behavioral rules #9-#13** — Hard rules for intent clarification, pre-court prep, report display

### Changed
- **Agent prompts streamlined** — Kept skeleton, removed scaffolding
- **Orchestrator → Prime Minister** — Renamed across entire repository
- **SKILL.md opening hard directive** — "From the first message you are the Prime Minister"

## [1.0.0] - 2026-04-03

### Added — Initial Release

- 15 roles: Prime Minister + Three Departments + Six Ministries + Censorate + Remonstrator + Political Affairs Hall + Morning Court Official + Hanlin Academy
- Lite mode (single context) + Pro mode (14 independent subagents)
- 10 standard scenario configurations
- Six Ministries × Four Bureaus detailed functional definitions
- Apache-2.0 License
