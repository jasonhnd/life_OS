# WHEN NOT TO ADD to `scripts/`

> **Intentionally near-empty principle**: this directory holds two subdirectories only — `commands/` (slash command md sources installed to user's `~/.claude/commands/`) and `prompts/` (maintenance job prompts that ROUTER reads and executes inline). Both subdirs are md-only since v1.8.5/v1.8.6.

## What does NOT belong here

1. **Any `.sh` / `.bash` shell script** — per `SKILL.md` md-only ontological constraint (DR-10 v1.8.7). v1.8.5 retired the entire bash hook layer; v1.8.7 makes that retirement permanent. Forbidden extensions: `.sh / .bash / .py / .yml / .yaml / .json / .sql / .db / .sqlite`.
2. **Any `.py` Python script** — same as above.
3. **A new slash command "just for me"** — slash commands are user-facing; they must have a clear name + argument-hint + description and ship as part of a release. Personal one-off automation goes in your `~/.claude/commands/` directly (not in this repo).
4. **A new maintenance prompt without a trigger word** — `scripts/prompts/*.md` files are invoked by ROUTER via natural language patterns documented in `hosts/CLAUDE.md`. A prompt with no documented trigger is dead code.
5. **Documentation for users** — `docs/` and `gitbooks/` exist for that.
6. **Helper functions / libraries** — there are no helper libs in scripts/; commands and prompts are self-contained LLM-driven md files.

## What DOES belong here

### `scripts/commands/<name>.md`

User-facing slash commands. Each is a single md file with `description:` and `argument-hint:` frontmatter. Installed to `~/.claude/commands/<name>.md` by `/install-agents` or similar.

Current: `compress.md`, `inbox-process.md`, `memory.md`, `method.md`, `monitor.md`, `research.md`, `search.md`.

### `scripts/prompts/<name>.md`

Internal maintenance prompts that ROUTER reads inline (no installation step). Triggered by natural language patterns documented in `hosts/CLAUDE.md` §"Auto-Trigger Rules".

Current 21+ prompts (advisor-monthly, archiver-recovery, auditor-mode-2, backup, daily-briefing, eval-history-monthly, extract-concepts, inbox-process, migrate-confidence, migrate-from-v1.6, migrate-to-wikilinks, rebuild-concept-index, rebuild-session-index, reindex, research, review-queue, snapshot-cleanup, spec-compliance, strategic-consistency, wiki-decay, wiki-link-audit, wiki-obsidian-upgrade).

## Before adding a new command or prompt — Minimality Rule check

Per `hosts/CLAUDE.md` Minimality Rule:

1. Could **ROUTER handle this natively** (no command needed)?
2. Could **an existing command/prompt** be extended?
3. Could **an agent's existing procedure** absorb this?
4. Could **a regression fixture** + AUDITOR mode accomplish this?

If ANY answer is yes, prefer that. New command = forever maintenance + install/uninstall logic + cross-host compatibility (Claude Code / Gemini CLI / Codex CLI).

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- `SKILL.md` HARD RULE md-only ontological constraint (DR-10)
- Pattern source: `tinyhumansai/openhuman` `.claude/rules/README.md`
