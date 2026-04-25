# Changelog

## Versioning Rules

This project follows **Strict SemVer**: MAJOR (Breaking Change) · MINOR (new features) · PATCH (fixes and maintenance). Changes on the same day are merged into a single release, and every release gets a git tag.

---

## [1.7.0.1] - 2026-04-25 · Briefing Contract + Hook Self-check + Cortex Config

> Patch release tightening the v1.7 GA contract: final briefings now have fixed required sections, hook installation is self-checked before Mode 0, and Cortex activation is consistently opt-in through `_meta/config.md`.

### Fixed

- **lifeos-version-check.sh cache freshness** — Added `--force` flag and remote SHA-based cache invalidation. Daily cache no longer goes stale within the same day if remote ships a new version.
- **Briefing completeness is now testable** — Start Session and Adjourn outputs must emit fixed headings with concrete values, so missing or placeholder sections are logged as `C-brief-incomplete`.
- **RETROSPECTIVE no longer assumes hooks are installed** — Mode 0 performs a pre-session hook health check and surfaces the exact `setup-hooks.sh` recovery command when the Claude Code hook backstop is missing or incomplete.
- **Cortex config path is consistent** — Reverted R1's accidental path split — Cortex configuration stays in `_meta/config.md` as shipped in v1.7.0, with `cortex_enabled: false` as the opt-in default.
- **Cortex default is unambiguous** — missing config now degrades to `cortex_enabled: false`; Cortex is OFF / opt-in until the user explicitly enables it.
- **AUDITOR Mode 3 programmatic checks** — AUDITOR now calls Bash (`lifeos-compliance-check.sh` + `grep`) instead of LLM-reasoning, eliminating same-source confabulation that allowed the 2026-04-25 testbed-machine "private repo" case to pass through.

### Added

- **Anti-confabulation hardening** — Step 8 forces literal Bash stdout paste, ROUTER pre-fetches ground truth, AUDITOR Mode 3 scans for fabrication phrase blacklist + tool-call evidence, new B-fabricate-toolcall violation class. Closes the 2026-04-25 'private repo' confabulation case.
- **Briefing Completeness Contract** — RETROSPECTIVE and ARCHIVER final reports now define required fixed-position sections and minimum evidence fields.
- **Compliance taxonomy for briefing omissions** — `C-brief-incomplete` records missing headings, session/source metadata, and escalation behavior separately from base Class C.
- **`briefing-completeness` compliance check** — `scripts/lifeos-compliance-check.sh` can now verify retrospective and archiver briefing headings in regression runs.
- **Layer 1 hook auto-install** — retrospective Step 0 + archiver Phase 0 + ROUTER trigger detection now auto-run `setup-hooks.sh` when hooks are missing. No more manual install step required after `git pull`.
- **PRIMARY-SOURCE PRECOMPUTE briefing markers** — wiki/sessions/concepts measured counts now MUST appear in briefing as `[Wiki count: measured X · index Y · drift Δ=Z]`. Missing → `C-brief-incomplete`; |Δ|≥3 without `⚠️ DRIFT` → `B-source-drift`.
- **STATUS.md staleness detection** — retrospective Step 0.5 checks STATUS last-updated vs git HEAD age; ≥7 days → STATUS narrative suppressed in briefing. New `B-source-stale` class.
- **30d-≥3 Compliance Watch auto-banner** — retrospective reads `violations.md`, auto-prepends `🚨 Compliance Watch: <class> (X/30d)` to briefing line 1 when threshold trips. Missing → `C-banner-missing`.
- **ROUTER fact-check on subagent output** — `SKILL.md` mandates ROUTER call Bash to verify numeric/version/path claims in briefing before showing to user. Third defense layer after subagent self-check + AUDITOR Mode 3.

### Migration from v1.7.0

1. Review any second-brain that enabled Cortex implicitly and keep Cortex enabled only via `_meta/config.md` where Cortex should run.
2. Add `cortex_enabled: true` to `_meta/config.md` for opt-in workspaces; leave the field absent or set `false` elsewhere.
3. Reinstall Claude Code hooks with `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` if Mode 0 reports the hook health warning.
4. Update Start Session / Adjourn eval baselines to include the fixed briefing headings and run `briefing-completeness`.

---

## [1.7.0] - 2026-04-22 · Cortex Cognitive Layer · General Availability

> Cortex graduates from alpha to GA. 65 commits after `v1.7.0-alpha.2` closed the remaining TBDs: the full shell-hook runtime (5 hooks + shared library), 10 Python tools wired under a single `life-os-tool` CLI, 3 shared Python libraries, public docs publication under `docs/`, trilingual cognitive-layer docs, Step 0.5 / Step 7.5 contract synced across CLAUDE / GEMINI / AGENTS hosts, and a migration path that preserves every existing v1.6.2a second-brain.

### ✨ Highlights

- **Cortex Pre-Router Cognitive Layer goes GA** — no longer opt-in-alpha; full contract with deterministic degradation
- **5 shell hooks enforced at runtime** — pre-prompt guard, pre-write scan, pre-read allowlist, post-response verify, stop-session verify; shared `_lib.sh`
- **10 Python tools unified under `life-os-tool`** — reindex / reconcile / stats / research / daily-briefing / backup / migrate / search / export / seed (+ embed placeholder + sync-notion)
- **3 Python libraries** — `tools/lib/{config, llm, notion}` as the shared surface for every tool
- **Trilingual user guide shipped** — 6 new Cortex guides (EN) + Chinese/Japanese cortex-spec and hippocampus-spec translations
- **Host-agnostic orchestration contract** — Step 0.5 (Pre-Router Cognitive) + Step 7.5 (Narrator validation) now normative in CLAUDE.md / GEMINI.md / AGENTS.md (root + `pro/`)
- **Life OS agents register as native Claude Code subagents** — install writes 21 Task-spawnable `~/.claude/agents/lifeos-*.md` wrappers from the 22 `pro/agents/*.md` definitions, skipping the ROUTER-internal narrator template so `Task(lifeos-retrospective)` no longer falls back to `general-purpose`

### Features

- **Cortex subagents (Pre-Router Cognitive Layer)** — hippocampus 3-wave session retrieval · GWT salience arbitration on top-5 signals · concept graph lookup with synapse matching · SOUL-dimension conflict check · Narrator citation wrapping · Narrator-Validator audit (Sonnet-tier)
- **Shell hooks (5 enforcement points + shared library)**
  - `pre-prompt-guard.sh` — UserPromptSubmit-time class-B/C policy and Cortex enablement gating
  - `pre-write-scan.sh` — block injection into `second-brain/wiki/**` and other protected surfaces
  - `pre-read-allowlist.sh` — SSH/secret denylist + cwd allowlist enforcement
  - `post-response-verify.sh` — verify `[COGNITIVE CONTEXT]` delimiters + adjourn checklist
  - `stop-session-verify.sh` — end-of-session compliance net (adjourn Phase 4 presence, narrator citation discipline)
  - `scripts/hooks/_lib.sh` — shared helpers (path resolution, JSON read, logging) reused by all five
- **Python tools (10 shipped + 1 placeholder + 1 Notion sync = 12 under `life-os-tool`)**
  - `reindex` — rebuild session INDEX + concept INDEX + SYNAPSES in one pass
  - `reconcile` — detect drift between SOUL/Wiki/Strategic-Map and session summaries
  - `stats` — violations escalation ladder + `--period / --since / --output` analytics
  - `research` — deep-research scaffold (web/code/company via Exa)
  - `daily_briefing` — morning briefing generator pulling from INDEX + STATUS + SOUL top-5
  - `backup` — 30d archive / 90d delete rotation + quarterly violations archival
  - `migrate` — v1.6.2a → v1.7 migration runner (3-month backfill window)
  - `search` — substring + concept-slug search across second-brain
  - `export` — serialize second-brain into portable bundle
  - `seed` — bootstrap empty second-brain from user templates
  - `embed` — placeholder (explicit no-op, per v1.7 decision "no vector DB")
  - `sync_notion` — two-way Notion mirror (via `tools/lib/notion.py`)
- **Python libraries** — `tools/lib/config.py` (env + pyproject resolution) · `tools/lib/llm.py` (LLM call wrapper with retries + token accounting) · `tools/lib/notion.py` (Notion API client)
- **Orchestration** — Step 0.5 (Pre-Router Cognitive Layer) and Step 7.5 (Narrator validation) synchronized into CLAUDE.md, GEMINI.md, and AGENTS.md at both root and `pro/` levels; contract is now host-agnostic
- **Bootstrap tooling** — `tools/seed_concepts.py` + 3 user-facing templates for second-brain bootstrap; 11 tests

### Documentation

- **6 new Cortex user guides** under `docs/user-guide/cortex/`
  - `overview.md` — the "what is Cortex" entry point
  - `hippocampus-recall.md` — how 3-wave session retrieval works
  - `concept-graph-and-methods.md` — concept node promotion + method-library signals
  - `narrator-citations.md` — reading and trace-ing `[S:][D:][SOUL:]` citations
  - `gwt-arbitration.md` — salience formula and why a signal made it to top-5
  - `auditor-eval-history.md` — eval-history self-feedback loop
- `docs/guides/v1.7-migration.md` — "第一周日常体验对标" section added for post-upgrade week-one pacing
- `devdocs/architecture/cortex-integration.md` — marked **deprecated**, aligned with spec freeze (source of truth is now `references/cortex-spec.md`)
- `docs/architecture/system-overview.md` — `_meta/` shard paths + Step 0.5 / Step 7.5 orchestration diagram updated
- `docs/getting-started/what-is-life-os.md` — Cortex now named as the third pillar alongside Second Brain and Decision Engine
- `MIGRATION.md` — dev-machine handoff guide (tar syntax fix for paths starting with dash)

### i18n

- `i18n/{zh,ja}/references/{concept,cortex,eval-history,gwt,hippocampus,hooks,method-library,narrator,session-index,snapshot,tools}-spec.md` — Chinese/Japanese translations for the 11 frozen v1.7 specs
- `i18n/{zh,ja}/docs/getting-started/what-is-life-os.md` + `i18n/{zh,ja}/docs/user-guide/cortex/*.md` — localized onboarding plus 6 Cortex user guides
- `README.md` + `i18n/{zh,ja}/README.md` — topic-block order, language switcher, and decision-table wording aligned across all three languages

### Infrastructure

- **CI** — pytest suite grew **184 → 400 (+216 tests)**; ruff warnings **50+ → 0**; bash syntax check **11/11** green
- **Makefile** — common dev commands (test / lint / format / build-docs) consolidated
- `UV_LINK_MODE=copy` written into `~/.bashrc` to resolve Dropbox hardlink conflicts during `uv sync`
- `.github/workflows/test.yml` pytest matrix extended with the 10 new tool modules + 3 new library modules
- 8 new hook-compliance eval scenarios under `evals/scenarios/hook-compliance/` (01-start-compliant-launch through 08-arbitrary-prompt-silent)

### Breaking / Migration

- Users on **v1.6.2a → v1.7.0** must run `uv run life-os-tool migrate` — the migration tool backfills the past 3 months of journal / snapshot data into the new `_meta/cortex/` shard layout
- Cortex defaults to **enabled on new installs** in v1.7.0 (flip from v1.7.0-alpha's opt-in default); existing second-brains keep whatever `cortex_enabled` setting they had
- Full migration procedure: `docs/guides/v1.7-migration.md`

### Compliance

- **2 incident dossiers** captured during the Cortex GA run
  - `backup/pro/compliance/2026-04-19-court-start-violation.md` — archived (resolved, lesson absorbed into L1/L2 hooks)
  - Narrator-spec violation — **pending resolution** (tracked in next Compliance Patrol cycle)

### Selected Files Touched (post-alpha.2 commits)

```
65b0d57 docs(i18n): publish zh/ja v1.7 specs and Cortex guide translations
170ca07 docs: publish v1.7 public docs trees (exclude plugin-system drafts)
8e47d61 docs(release): path docs/→devdocs/ in 8 specs + CHANGELOG SHA rewrite + tri-lingual sync
91b7896 chore(tests): remove unused pytest import in seed_concepts cleanup
fdf8748 chore(cli/tests): wire 10 v1.7 tools, fix Windows encoding, and track compliance dossiers
1b41f85 feat(tools): add seed.py + tests
9159e38 feat(tools): add migrate.py + tests
f2d5a1d feat(tools): add research.py + tests
b33f7dd feat(tools): extend stats.py aggregates and add sync_notion.py
7240446 feat(tools): add daily_briefing.py + tests
d2d43d8 feat(tools): add export.py + tests
b7e7335 feat(tools): add reconcile.py + tests
f8a26c6 feat(tools): embed.py placeholder + search.py (S5+S4 parallel-sprint merge)
032bdc7 feat(tools): add reindex.py + tests
2b7226f test(hooks): add 8 hook-compliance eval scenarios
0e5128b chore(hooks): extend setup-hooks.sh for v1.7 all 5 hooks
63e923e feat(hooks): add pre-read-allowlist.sh
5ff0d32 feat(hooks+lib): stop-session-verify.sh + Notion lib + pyproject (S1+S2 parallel-sprint merge)
4a2590f docs(orchestration): update root AGENTS.md with host-agnostic Step 0.5/7.5 contract
4ae2a65 feat(hooks): add pre-write-scan.sh
bf7f87e docs(orchestration): sync Step 0.5/7.5 to pro/AGENTS.md
877c629 feat(lib): add tools/lib/llm.py + tests
efa339d feat(lib): add tools/lib/config.py + tests
1414677 feat(hooks): add post-response-verify.sh
7c1fd3a docs(orchestration): sync Step 0.5/7.5 to GEMINI.md
a503301 feat(hooks): add pre-prompt-guard.sh
```

(Plus `tools/seed_concepts.py` + templates, `MIGRATION.md`, `Makefile`, additional spec/docs publication commits, and 3 trilingual CHANGELOG syncs.)

---

## [1.7.0-alpha.2] - 2026-04-21 · Post-v1.7.0-alpha follow-ups bundle

> 📚 **Comprehensive overview**: see [`references/v1.7-shipping-report-2026-04-21.md`](references/v1.7-shipping-report-2026-04-21.md) for the full single-page narrative covering both the v1.6.3 COURT-START-001 fix line AND the v1.7 Cortex line in one document. Recommended starting point if you're returning to the repo and want to know "what shipped today".

> 13 commits shipped after v1.7.0-alpha to close TBDs from the alpha CHANGELOG and add tooling/test infrastructure. Will roll into v1.7.0 stable release.

### 🔧 New tooling

- `tools/cli.py` — unified subcommand dispatcher; `pyproject.toml` activates `life-os-tool` console script
- `tools/backup.py` — snapshot rotation (30d archive, 90d delete) + violations log archival to quarterly files
- `tools/extract.py` — concept candidate extraction CLI (frequency counter + slug generator)
- `tools/lib/cortex/extraction.py` — non-LLM helpers (normalize_name, slug_from_name, is_stopword, count_frequencies, deduplicate_aliases) — handles deterministic parts of archiver Phase 2 Step A so LLM doesn't burn tokens on counting
- `scripts/lifeos-compliance-check.sh` — `check_adjourn()` + `check_cortex()` implementations (closing the placeholder from alpha)
- `tools/lib/cortex/__init__.py` — package-level exports of all 29 helper symbols

### 📋 New eval scenarios

- `evals/scenarios/adjourn-compliance.md` — Class C/D/E + A3 detection
- `evals/scenarios/cortex-retrieval.md` — CX1-CX7 detection + degradation paths

### ✅ Test suite expansion

- `tests/test_backup.py` — 19 tests (snapshot rotation, violations archival, path resolution)
- `tests/test_cli.py` — 8 tests (help / unknown / dispatch / argv preservation)
- `tests/test_compliance_check.py` — 11 subprocess-based tests for the bash compliance script
- `tests/test_integration.py` — 7 end-to-end integration tests (full Cortex pipeline with fixtures)
- `tests/test_package_imports.py` — 7 tests (cortex + second_brain package import surfaces, regression guard for __all__ drift)
- `tests/test_extraction.py` — 44 tests (normalize, slug, stopwords (EN/ZH/JA), phrase split, frequency, dedup)

**Total tests now: 173, all pass in 0.83s combined.**

### 🚀 CI

- `.github/workflows/test.yml` — pytest matrix (Python 3.11/3.12) + bash syntax + smoke tests for hooks

### 📚 Architecture documentation

- `references/cortex-architecture.md` — end-to-end data flow (Adjourn → Compile → Read paths), info isolation matrix, failure cascade, cost profile, compliance map

### 🔌 Wiring polish

- `pro/CLAUDE.md` Information Isolation table extended for all 6 v1.7 subagents (was: only hippocampus + GWT) + narrator-validator chain note in Step 0.5
- `pro/agents/archiver.md` adds explicit "Phase 2 Mid-Step — SOUL Snapshot" with both Python helper + direct write paths

### 🐛 Bug fixes

- `tools/cli.py` `_print_usage(stream=sys.stdout)` default eval bug — fixed to None+resolve-at-call so pytest capsys works
- `scripts/lifeos-compliance-check.sh` `set -e` + `grep -c` → silent kill; added `|| true` guards
- `scripts/lifeos-compliance-check.sh` `\s` regex (GNU-only) → POSIX `[[:space:]]` for portability

### Files Touched (post-alpha commits)

```
b1bf474 feat: tools/cli.py dispatcher + check_cortex() + pyproject scripts entry
4fa8db9 feat: check_adjourn() implementation + cortex-retrieval eval scenario
81c96ec feat: v1.7.0-alpha follow-up — backup.py + adjourn eval + CI workflow
2fecaa9 test: end-to-end integration tests for Cortex pipeline (7 tests)
72c942c feat: tools.lib.cortex package exports + Info Isolation table + archiver snapshot step
eb477a5 feat: tests/test_cli + test_compliance_check + cortex-architecture doc
```

(Plus the 1ce61d1 v1.7.0-alpha release commit itself.)

---

## [1.7.0-alpha] - 2026-04-21 · Cortex Pre-Router Cognitive Layer

> First Layer-2 architectural upgrade in Life OS history. Adds cross-session memory, concept graph, and identity signals as inputs to every decision workflow. 19 commits today brought v1.7 from spec drafts to functional completeness.

### 🧠 Pre-Router Cognitive Layer (orchestrator Step 0.5)

When `cortex_enabled: true` in `_meta/config.md`, every non-Start-Session user message now flows through 4 parallel subagents BEFORE ROUTER triage:

```
user message
    ↓
Step 0.5 (Pre-Router Cognitive Layer)
    ├─ hippocampus       → 3-wave session retrieval (5-7 sessions)
    ├─ concept-lookup    → concept-graph match (5-10 concepts)
    └─ soul-check        → SOUL dimension signals (top 5)
         ↓
    gwt-arbitrator        → top-5 signals via salience formula
         ↓
[COGNITIVE CONTEXT] block prepended to user message
    ↓
Step 1 (ROUTER Triage with annotated input)
```

After REVIEWER Final Review, optional `narrator` wraps Summary Report substantive claims with `[source:signal_id]` citations. `narrator-validator` (Sonnet-tier) audits citation discipline.

### 📋 6 new subagents (~900 lines markdown contracts)

| Agent | File | Spec |
|-------|------|------|
| hippocampus | `pro/agents/hippocampus.md` | `references/hippocampus-spec.md` |
| concept-lookup | `pro/agents/concept-lookup.md` | `references/concept-spec.md` |
| soul-check | `pro/agents/soul-check.md` | derived from soul-spec + gwt-spec §6 |
| gwt-arbitrator | `pro/agents/gwt-arbitrator.md` | `references/gwt-spec.md` |
| narrator | `pro/agents/narrator.md` | `references/narrator-spec.md` |
| narrator-validator | `pro/agents/narrator-validator.md` | narrator-spec validator section |

All 6 enforce information isolation: peer Pre-Router agent outputs are rejected. All are read-only — mutations happen only in archiver Phase 2.

### 🐍 Python tools (~1500 lines, pure stdlib + pyyaml)

| Module | Purpose |
|--------|---------|
| `tools/lib/second_brain.py` | Dataclasses for 11 second-brain types + frontmatter parser/dumper + path resolver |
| `tools/lib/cortex/session_index.py` | SessionSummary IO + INDEX.md compilation (idempotent) |
| `tools/lib/cortex/concept.py` | Concept IO + INDEX/SYNAPSES compilation + Hebbian update |
| `tools/lib/cortex/snapshot.py` | SoulSnapshot IO + archive policy (30d/90d) |
| `tools/stats.py` | Compliance violations escalation ladder enforcement |

### 🔧 4 CLI tools

```bash
uv run tools/rebuild_session_index.py [--root PATH] [--dry-run]
uv run tools/rebuild_concept_index.py [--root PATH] [--dry-run] [--no-synapses]
uv run tools/stats.py [--violations PATH] [--json]
bash scripts/setup-hooks.sh   # auto-registers SessionStart + UserPromptSubmit hooks (v1.6.3a)
```

### ✅ 77 pytest tests — all passing in 0.23s

| File | Tests |
|------|-------|
| `tests/test_second_brain.py` | 15 (frontmatter parser, dataclasses, path resolver) |
| `tests/test_session_index.py` | 16 (truncate, write, compile, rebuild, idempotence) |
| `tests/test_concept_and_snapshot.py` | 18 (concept IO, INDEX, SYNAPSES, Hebbian, snapshot policy) |
| `tests/test_stats.py` | 18 (parse, escalation, threshold triggers, path resolution) |

```bash
python3 -m pytest tests/ -v        # 77 passed in 0.23s
```

### 🔌 Wiring updates

- **`pro/agents/archiver.md`** Phase 2 — adds (a) concept extraction + Hebbian update + SYNAPSES regeneration step, (b) SessionSummary write step
- **`pro/agents/retrospective.md`** Mode 0 — adds INDEX.md compilation step + AUDITOR Compliance Patrol auto-follow
- **`pro/CLAUDE.md`** — new Workflow Step 0.5 (Pre-Router Cognitive Layer); Information Isolation table extended for hippocampus + gwt-arbitrator entries
- **`pro/agents/auditor.md`** Mode 3 — adds 7 Cortex compliance checks (CX1-CX7)

### 🚦 Default OFF (opt-in)

Cortex is disabled by default in v1.7.0-alpha. Users opt in:

```bash
echo "cortex_enabled: true" >> _meta/config.md
```

Recommended once a second-brain has accumulated ≥30 sessions. Cost: ~$0.05-0.25/turn (Opus tokens across Pre-Router subagents).

### 📊 Cortex compliance taxonomy (added to AUDITOR Mode 3)

| Code | Name | Severity |
|------|------|----------|
| CX1 | Skip Pre-Router subagents | P1 |
| CX2 | Skip GWT arbitrator | P1 |
| CX3 | Missing [COGNITIVE CONTEXT] delimiters | P1 |
| CX4 | Hippocampus session cap exceeded | P1 |
| CX5 | GWT signal cap exceeded | P1 |
| CX6 | Cortex isolation breach | P0 |
| CX7 | Cortex write breach | P0 |

CX checks skipped when `cortex_enabled: false`.

### 📁 Files Touched (19 commits)

Specs: `references/{cortex,hippocampus,gwt,concept,snapshot,session-index,narrator,hooks,tools,eval-history,method-library}-spec.md` + 8 modified existing references.
Subagents: `pro/agents/{hippocampus,gwt-arbitrator,concept-lookup,soul-check,narrator,narrator-validator}.md`.
Wiring: `pro/CLAUDE.md`, `pro/agents/{archiver,retrospective,auditor}.md`.
Tools: `tools/lib/{second_brain.py,cortex/*}`, `tools/{stats,rebuild_session_index,rebuild_concept_index}.py`.
Project: `pyproject.toml`, `.python-version`, `tools/README.md`.
Tests: `tests/{__init__,test_second_brain,test_session_index,test_concept_and_snapshot,test_stats}.py`.
Hooks: `scripts/lifeos-compliance-check.sh` (L5 closure for v1.6.3 chain).
Docs: 3 README + 3 CHANGELOG (this commit).

### 🚧 Known limitations / TBD

- **Production validation pending** — alpha is theory-tested via pytest + spec compliance, but not yet exercised in a real user second-brain at scale
- **No `concept-lookup` traversal of edges yet** — Wave 1 only; Wave 2/3 is hippocampus's domain
- **Narrator validator** is shipped but uses self-check loop in Phase 2; standalone validator subagent pending Phase 2.5
- **`tools/backup.py`** for snapshot archival rotation: deferred to v1.7.0 stable
- **adjourn-compliance eval scenario** still placeholder

### Migration

Existing users (v1.6.3b → v1.7.0-alpha):
1. Re-install skill: `/install-skill https://github.com/jasonhnd/life_OS`
2. Re-run hooks setup: `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`
3. (Optional) Install Python tools: `cd ~/.claude/skills/life_OS && uv sync`
4. (Optional) Enable Cortex: `echo "cortex_enabled: true" >> {your-second-brain}/_meta/config.md`

Default OFF means existing users see ZERO behavior change unless they opt in. v1.6.3 five-layer compliance defense remains active and unchanged.

---

## [1.6.3b] - 2026-04-21 · AUDITOR Mode 3 Auto-Trigger Wired

> v1.6.3 shipped Mode 3 (Compliance Patrol) spec into `pro/agents/auditor.md` but **nothing actually invoked it**. The first production run in a user second-brain confirmed the gap: retrospective Mode 0 completed, briefing displayed, but no AUDITOR Compliance Patrol report appeared. Layer 4 of the five-layer defense was inert.

### 🔧 Fix

`pro/CLAUDE.md` Orchestration Code of Conduct gains rule #7:

> **AUDITOR Compliance Patrol auto-trigger** — after every `retrospective` Mode 0 (Start Session) completes OR every `archiver` returns, the orchestrator MUST launch `auditor` in Mode 3 (Compliance Patrol). Cannot be skipped. HARD RULE.

Three supporting docs updated to make the contract explicit:

- `pro/agents/retrospective.md` — adds "Auto-Follow: AUDITOR Compliance Patrol" section noting orchestrator chains Mode 3 after Mode 0 returns. Subagent itself does not launch AUDITOR.
- `pro/agents/auditor.md` — Mode 3 "When to run" section adds explicit trigger contract: orchestrator-launched, not self-launched, with cross-reference to `pro/CLAUDE.md` rule #7.
- `SKILL.md` — version 1.6.3a → 1.6.3b.

### 📊 Five-layer defense status (post-1.6.3b)

| Layer | Status |
|-------|--------|
| L1 · UserPromptSubmit hook | ✅ shipped (v1.6.3) · auto-installed by setup-hooks.sh (v1.6.3a) |
| L2 · Pre-flight Compliance Check | ✅ shipped + production-verified 2026-04-21 |
| L3 · Subagent Self-Check | ✅ shipped + production-verified 2026-04-21 |
| L4 · AUDITOR Compliance Patrol (Mode 3) | ✅ spec shipped (v1.6.3) · **trigger wired (v1.6.3b)** |
| L5 · Eval regression | ✅ scenario shipped (v1.6.3) · auto-runner extension deferred to v1.7 |

### Files Touched

- `SKILL.md` (version 1.6.3a → 1.6.3b)
- `pro/CLAUDE.md` (+ Orchestration rule #7)
- `pro/agents/retrospective.md` (+ Auto-Follow section)
- `pro/agents/auditor.md` (Mode 3 "When to run" trigger contract clarified)
- `README.md` + 三語 (badge)
- `CHANGELOG.md` + 三語

### Migration

No user action required. Existing v1.6.3a installs will auto-pick-up rule #7 on next session. AUDITOR Compliance Patrol report will appear at end of every Start Session and Adjourn going forward. Output format (when no violations):

```
🔱 [theme: auditor] · Compliance Patrol (v1.6.3)
✅ All 6 Start Session compliance checks passed
No violations logged. Session adheres to v1.6.3 HARD RULES.
```

---

## [1.6.3a] - 2026-04-21 · v1.6.3 Hot Patch · Layer 1 Install Gap + Hook False-Positive Guard

> First production run of v1.6.3 in a user second-brain (same day) validated Layers 2-5 working end-to-end. Two real gaps surfaced:
> 1. **Layer 1 (UserPromptSubmit hook) was NOT auto-registered** — `/install-skill` copies files but doesn't modify `~/.claude/settings.json`. Default installs shipped without L1 defense.
> 2. **Hook regex fired on paste content** — pasted transcripts containing a trigger word mid-content erroneously triggered the reminder.

### 🔧 Fix 1 — Layer 1 install automation

`scripts/setup-hooks.sh` refactored:
- Now installs both SessionStart hook (version check) AND UserPromptSubmit hook (Layer 1 defense) in one run
- Added `register_hook()` helper for DRY idempotent registration across event types
- Idempotent: safe to re-run; skips already-registered hooks
- Backwards compatible: existing v1.6.3 installs unaffected; re-running adds L1 cleanly

User runs once after install/upgrade:
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```

### 🔧 Fix 2 — Hook false-positive reduction

`scripts/lifeos-pre-prompt-guard.sh` adds two pre-checks before regex matching:
- **Length check**: prompt overall ≤ 500 chars (long prompts = conversational/paste, not triggers)
- **First-line check**: first non-empty line ≤ 100 chars (filters paste blocks starting with paragraph-length intros)

Trigger regex now runs against **first line only** (was multiline). Pasted transcripts with trigger words mid-content no longer fire the hook.

### 🆕 Class F — False positive

Added to `references/compliance-spec.md` Type Taxonomy and `pro/compliance/violations.md` Type Legend:

| Code | Name | Default Severity |
|------|------|------------------|
| **F** | False positive | P2 (informational) — hook fired on paste/quote content, not real user trigger. Excluded from escalation ladder. |

First documented Class F entry: 2026-04-21T13:42 — paste of v1.6.3 production-verification transcript triggered hook in dev repo. Assistant correctly identified paste context and refused to launch retrospective. Mitigated by Fix 2 above.

### 📋 COURT-START-001 status update

4 incident entries in `pro/compliance/violations.md` annotated with production-verification evidence:
- L2 (Pre-flight Compliance Check) — verified working in user second-brain on 2026-04-21
- L3 (Subagent Self-Check) — verified working in user second-brain on 2026-04-21
- L4 (AUDITOR Compliance Patrol) + L5 (eval regression) — pending observation window

`partial → true` transition still gated by eval regression pass + 30-day no-recurrence window per `references/compliance-spec.md`.

### Files Touched

- `SKILL.md` (version 1.6.3 → 1.6.3a)
- `scripts/setup-hooks.sh` (refactor with register_hook helper + UserPromptSubmit registration)
- `scripts/lifeos-pre-prompt-guard.sh` (+ length check + first-line extraction)
- `references/compliance-spec.md` (+ Class F to Type Taxonomy)
- `pro/compliance/violations.md` (+ Class F to legend, + 1 F entry, + L2/L3 verification annotations on 4 COURT-START-001 entries)
- `pro/compliance/violations.example.md` (+ Example 11 Class F)
- `README.md` + 三語 (version badge + v1.6.3a hot-patch note)
- `CHANGELOG.md` + 三語

### Migration

Existing v1.6.3 installs:
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
Activates Layer 1 defense. No other action needed; Layers 2-5 unchanged.

New installs: same single command activates everything.

---

## [1.6.3] - 2026-04-21 · COURT-START-001 Fix · Five-Layer Defense

> When the user said "上朝" in the Life OS dev repo, ROUTER bypassed the retrospective subagent, simulated 18 steps inline, and fabricated the non-existent path `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation` as authority. User reaction: "how can this Life OS be given to others? I cannot accept." This release ships a five-layer defense so every HARD RULE is actually hard.

### 🛡️ Five-Layer Defense Against Class A / B Violations

Root cause of COURT-START-001: documentation was complete, but **every HARD RULE was descriptive — zero enforcement**. The author himself could be tricked by the LLM; ordinary users would be inevitably misled. Five independent layers now guard every trigger word:

1. **Hook layer** — `scripts/lifeos-pre-prompt-guard.sh` runs on `UserPromptSubmit`, detects trigger words (上朝 / start / 閣議開始 / 退朝 / etc., all 9 themes), injects a `<system-reminder>` with the exact HARD RULE text and violation taxonomy into the assistant's context before any response.
2. **Pre-flight Compliance Check** — `SKILL.md` now requires ROUTER to output a 1-line confirmation before any tool call: `🌅 Trigger: [word] → Theme: [name] → Action: Launch([agent]) [Mode]`. Missing line = Class A3 violation, logged.
3. **Subagent self-check** — `pro/agents/retrospective.md` Mode 0 first line must be: `✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation). Reading pro/agents/retrospective.md. Starting Step 1: THEME RESOLUTION.` This proves the subagent was actually launched.
4. **AUDITOR Compliance Patrol (Mode 3)** — `pro/agents/auditor.md` adds Mode 3 with a 7-class taxonomy (A1/A2/A3/B/C/D/E) and 6 detection checks for Start Session / Adjourn paths. Runs after every retrospective Mode 0 and archiver completion.
5. **Eval regression** — `evals/scenarios/start-session-compliance.md` codifies the 6 COURT-START-001 failure modes as Quality Checkpoints with grep-based failure detection commands.

### 📋 Violation Taxonomy (7 classes)

| Code | Name | Default Severity |
|------|------|------------------|
| A1 | Skip subagent — ROUTER simulates subagent's steps in main context | P0 |
| A2 | Skip directory check — dev repo bypasses retrospective Step 2 | P1 |
| A3 | Skip Pre-flight — first response missing `🌅 Trigger: ...` line | P1 |
| B | Fabricate fact — reference non-existent path / section as authority | P0 |
| C | Incomplete Phase — archiver exits before all 4 phases complete | P0 |
| D | Placeholder value — Completion Checklist contains `TBD` / `{...}` / empty | P1 |
| E | Main-context Phase execution — ROUTER runs Phase 1-4 logic inline | P0 |

### 📁 Dual-Repo Compliance Log (md + git, per user constraint)

User explicitly required: *"local sh command execution is fine, but the database must be md files and GitHub storage."* Violations are persisted to:

- `pro/compliance/violations.md` — dev repo (public, ships with Life OS)
- `_meta/compliance/violations.md` — user second-brain (private, per-user)

Both use the same format: `| Timestamp | Trigger | Type | Severity | Details | Resolved |`.

**Escalation ladder** (implemented by `tools/stats.py` in v1.7, manually observed until then):
- ≥3 same type in 30 days → hook reminder strictness upgrades
- ≥5 same type in 30 days → retrospective briefing prepends `🚨 Compliance Watch`
- ≥10 same type in 90 days → AUDITOR Compliance Patrol runs every Start Session

### 🗂️ New Files

- `scripts/lifeos-pre-prompt-guard.sh` — UserPromptSubmit hook (bash, chmod +x)
- `.claude/settings.json` — hook registration for dev repo
- `references/compliance-spec.md` — full specification: taxonomy, dual-repo strategy, write/read paths, escalation ladder, archival, resolution protocol, privacy
- `pro/compliance/violations.md` — dev-repo live log (5 seed entries from COURT-START-001)
- `pro/compliance/violations.example.md` — 10 example entries per class + grep recipes
- `pro/compliance/2026-04-19-court-start-violation.md` — full incident archive (473 lines, 12 sections)
- `evals/scenarios/start-session-compliance.md` — regression test for 6 COURT-START-001 failure modes

### ✏️ Modified Files

- `.claude/CLAUDE.md` — new HARD RULE section for Start Session triggers
- `SKILL.md` — version 1.6.2a → 1.6.3, Pre-flight Compliance Check section inserted before Start Session routing
- `pro/agents/retrospective.md` — Subagent Self-Check block before Execution Steps
- `pro/agents/auditor.md` — Mode 3 (Compliance Patrol) with 7-class taxonomy + detection checks

### 🔄 Resolution Protocol

Violations transition `false → partial → true` through three gates:
- **Gate 1** (`false → partial`): underlying fix shipped (version cited in Details field)
- **Gate 2** (`partial → true`): eval regression passes + 30 days elapsed + no recurrence (cite version + eval-id + observed-date)

COURT-START-001's 4 incident entries move to `partial` with this release. Transition to `true` requires `evals/scenarios/start-session-compliance.md` pass + 30-day observation window.

### Migration

No user action required for existing installations. On next Start Session after upgrade:
- Hook registers (dev repo only, via `.claude/settings.json`)
- Pre-flight line becomes mandatory
- AUDITOR runs Compliance Patrol after first retrospective Mode 0
- violations.md is auto-created if missing (empty table)

User second-brains that want the dual-repo violations log should add the hook block to their own `.claude/settings.json` per `references/compliance-spec.md`.

---

## [1.6.2a] - 2026-04-19 · Notion Sync Returns to Orchestrator

> The archiver subagent reported "Notion MCP not connected" because Notion MCP tools are environment-specific and unavailable inside subagents. Notion sync is now split out of the archiver and executed by the orchestrator (main context) which has MCP access.

### Changes

- **archiver.md**: Phase 4 reduced to git-only; Notion sync removed with explicit note about MCP tool limitation
- **CLAUDE.md**: New Step 10a — orchestrator executes Notion sync after archiver returns
- **GEMINI.md / AGENTS.md**: Synced with Step 10a addition
- **SKILL.md**: Adjourn template updated to include Notion sync as post-archiver step

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
