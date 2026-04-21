# Installation Guide

Life OS can be used on various AI platforms. Choose your platform and follow the steps.

> **SKILL.md** is the core file of Life OS, containing all instructions for the Three Departments and Six Ministries system. It is referenced multiple times below.
> 👉 **[Click here to get SKILL.md](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)** (click the "Raw" button in the top right to see plain text for easy copying)

---

## Table of Contents

- [Claude Code (Pro Mode)](#claude-code-pro-mode)
- [Gemini CLI / Antigravity (Pro Mode)](#gemini-cli--antigravity-pro-mode)
- [OpenAI Codex CLI (Pro Mode)](#openai-codex-cli-pro-mode)
- [Other Platforms](#other-platforms)
- [Installation Verification](#installation-verification)
- [Troubleshooting](#troubleshooting)
- [Updates](#updates)
- [FAQ](#faq)

---

## Claude Code (Pro Mode)

This is the full form of Life OS on Claude: 16 independent AI roles with true information isolation and parallel execution.

### Prerequisites

You need to have [Claude Code](https://claude.ai/code) (Anthropic's command-line AI tool) installed.

### Installation Steps

1. Open Terminal
2. Enter the following command and press Enter:

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

3. Wait for installation to complete; a success message will appear
4. Done! All 16 subagents are automatically ready and available across all projects

### Verification

After installation, type in Claude Code:

```
Help me analyze whether I should switch jobs
```

If you see a response in this format, installation was successful:

```
🏛️ Prime Minister · Presenting
📋 Decree: ... | 📌 Type: ... | 💡 Suggested activation: ...
```

### What Makes Pro Mode Special

- 16 AI roles each run independently, unable to see each other's thought processes
- Six Ministries can work in parallel (no queuing)
- The Chancellery cannot see how the Secretariat thinks during review — truly independent review
- All roles use Claude's opus-tier model (strongest available, auto-selected)

---

## Gemini CLI / Antigravity (Pro Mode)

Pro Mode is now available on [Gemini CLI](https://github.com/google-gemini/gemini-cli) and [Google Antigravity](https://idx.google.com/) with 16 independent subagents powered by Gemini's strongest available model (auto-selected at runtime, no hardcoded version).

### Installation Steps

1. Open Terminal (Gemini CLI) or the built-in terminal in Antigravity
2. Enter the following command:

```bash
npx skills add jasonhnd/life_OS
```

3. Done! The system auto-detects Gemini and loads `pro/GEMINI.md` for orchestration

### Antigravity-Specific Notes

- Antigravity loads skills from `.agents/skills/` (workspace scope) or `~/.gemini/antigravity/skills/` (global scope)
- **Important**: Add `.claude/worktrees/` to your project's `.gitignore` to prevent context overflow from Claude Code worktree artifacts. This is the most common cause of Gemini failing to respond in projects that also use Claude Code.

### What's Different from Claude Pro Mode

- Automatically uses Gemini's strongest available model (no hardcoded version)
- Tool names are mapped automatically (see `pro/GEMINI.md` for the mapping table)
- Same workflow, same information isolation, same 16 roles

---

## OpenAI Codex CLI (Pro Mode)

Pro Mode is now available on [Codex CLI](https://github.com/openai/codex) with 16 independent subagents powered by Codex's strongest reasoning model (auto-selected at runtime, no hardcoded version).

### Installation Steps

1. Open Terminal
2. Enter the following command:

```bash
npx skills add jasonhnd/life_OS
```

3. Done! The system auto-detects Codex and loads `pro/AGENTS.md` for orchestration

### What's Different from Claude Pro Mode

- Automatically uses Codex's strongest available model (no hardcoded version)
- Follows the [AGENTS.md open standard](https://agents.md/)
- Same workflow, same information isolation, same 16 roles

---

> **Note**: Life OS requires Pro Mode — 16 independent subagents with true information isolation. Single-context platforms (ChatGPT, Gemini Web, Claude.ai web) are not supported.

---

## Other Platforms

### Platforms Supporting the Agent Skills Standard

If your AI tool supports the [Agent Skills standard](https://agentskills.io/) (e.g., Roo Code, Windsurf, JetBrains Junie, etc.), use this command to install:

```bash
npx skills add jasonhnd/life_OS
```

See the full list of compatible platforms at [agentskills.io](https://agentskills.io/).

> **Note**: Life OS requires Pro Mode (independent subagents). Platforms without Agent Skills support are not compatible.

---

## Installation Verification

Regardless of platform, test with these messages after installation:

| You say | You should see |
|---------|---------------|
| "Help me analyze whether I should buy a MacBook" | Prime Minister determines it needs to be escalated, initiates Three Departments and Six Ministries process |
| "Help me translate a paragraph of Japanese" | Prime Minister handles directly (no process initiated) |
| "Morning court" | Morning Court Official delivers briefing |
| "I've been feeling lost lately" | Prime Minister asks whether to activate the Hanlin Academy |

---

## Troubleshooting

**Gemini / Antigravity stops responding in a specific project folder**

This is usually caused by large files in `.claude/worktrees/` (leftover from Claude Code sessions). These worktree copies flood Gemini's context window.

> ⚠️ **Manual Recovery (Human Only)** — The following commands involve destructive operations (`rm -rf`). Agents MUST NOT auto-execute them; run them yourself in your own terminal. GLOBAL.md Security Boundary #1 forbids agents from executing destructive commands without explicit user confirmation.

```text
# HUMAN ONLY — DO NOT auto-execute
# 1. Delete the worktree folder
rm -rf .claude/worktrees/

# 2. Add `.claude/worktrees/` to your `.gitignore` (edit manually)

# 3. Restart Antigravity / Gemini CLI
```

**Git operations fail with `fatal: not a git repository` after moving the repo**

This happens when Claude Code worktree references still point to the old location. The `.claude/worktrees/` directory contains `.git` files with hardcoded absolute paths.

> ⚠️ **Manual Recovery (Human Only)** — The following commands involve destructive operations (`rm -rf`, `git config --unset`). Agents MUST NOT auto-execute them; run them yourself in your own terminal. GLOBAL.md Security Boundary #1 forbids agents from executing destructive commands without explicit user confirmation.

```text
# HUMAN ONLY — DO NOT auto-execute
# 1. Clean git worktree references
git worktree prune

# 2. Delete stale worktree directories
rm -rf .claude/worktrees/

# 3. Check for broken config — if it points to a non-existent path,
#    run the unset command below
git config --get core.hooksPath
git config --unset core.hooksPath

# 4. Remove worktree extension flag
git config --unset extensions.worktreeConfig
```

Prevention: Before moving a repo (e.g., Dropbox → iCloud), always clean up worktrees first. After Claude Code worktree sessions, choose "remove" instead of "keep".

**Pro Mode not activating on Gemini/Codex**

Ensure you installed via `npx skills add jasonhnd/life_OS` and the skill files are in the correct location:
- Gemini CLI: `~/.gemini/skills/` or project-level `.agents/skills/`
- Codex CLI: `~/.codex/skills/`
- Claude Code: `~/.claude/skills/`

**Context window overflow**

If your project has very large files, AI platforms may silently fail. Solutions:
- Use `.gitignore` to exclude build artifacts, `node_modules/`, and large binary files
- For Antigravity, use the `.agignore` file (if supported) to exclude irrelevant directories

---

## Updates

### Check Current Version

The `version` field at the top of SKILL.md shows the current version number. See the latest version on [GitHub](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md) or the [changelog](../CHANGELOG.md).

### Update Methods by Platform

| Platform | How to update |
|----------|--------------|
| **Claude Code** | Re-run `/install-skill https://github.com/jasonhnd/life_OS` |
| **Gemini CLI / Antigravity** | Re-run `npx skills add jasonhnd/life_OS` |
| **Codex CLI** | Re-run `npx skills add jasonhnd/life_OS` |

### How to Know When There's a New Version?

- [Watch this repository](https://github.com/jasonhnd/life_OS) on GitHub to get notified of updates
- Check the [changelog (CHANGELOG.md)](../CHANGELOG.md)

---

## FAQ

**Q: Which platform should I start with?**
A: [Claude Code](https://claude.ai/code) is recommended. Full Pro Mode with 16 independent subagents, one-command install.

**Q: I use both Claude Code and Antigravity. Will they conflict?**
A: No. They use different orchestration files (`CLAUDE.md` vs `GEMINI.md`) and different agent model mappings. The same `pro/agents/*.md` files are shared. Just make sure `.claude/worktrees/` is in your `.gitignore` to prevent Antigravity from choking on Claude's temporary files.

**Q: Can I use it without connecting Notion?**
A: Yes. Notion is an optional data layer. Without it, all features work normally — you just won't have cross-session memory on mobile.

**Q: Can I use it in a language other than Chinese?**
A: Yes. The system supports English, Chinese, and Japanese. You can ask questions in any language.

**Q: What's the Express analysis path?**
A: When your request doesn't involve a decision (just analysis, research, or planning), the Prime Minister can skip the full Three Departments flow and directly launch 1-3 relevant ministries. Faster, fewer tokens, same quality for non-decision tasks.
