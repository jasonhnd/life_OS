# Installation Guide

Life OS can be used on various AI platforms. Choose your platform and follow the steps.

> **SKILL.md** is the core file of Life OS, containing all instructions for the Three Departments and Six Ministries system. It is referenced multiple times below.
> 👉 **[Click here to get SKILL.md](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)** (click the "Raw" button in the top right to see plain text for easy copying)

---

## Table of Contents

- [Claude Code (Recommended, Pro Mode)](#claude-code-recommended-pro-mode)
- [Claude.ai Web / Desktop (Lite Mode)](#claudeai-web--desktop-lite-mode)
- [Cursor](#cursor)
- [VS Code + GitHub Copilot](#vs-code--github-copilot)
- [Gemini CLI](#gemini-cli)
- [OpenAI Codex CLI](#openai-codex-cli)
- [ChatGPT](#chatgpt)
- [Gemini Web](#gemini-web)
- [Other Platforms](#other-platforms)
- [Pro vs Lite Mode Comparison](#pro-vs-lite-mode-comparison)
- [Installation Verification](#installation-verification)
- [Updates](#updates)
- [FAQ](#faq)

---

## Claude Code (Recommended, Pro Mode)

This is the full form of Life OS: 14 independent AI roles with true information isolation and parallel execution.

### Prerequisites

You need to have [Claude Code](https://claude.ai/code) (Anthropic's command-line AI tool) installed.

### Installation Steps

1. Open Terminal
2. Enter the following command and press Enter:

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

3. Wait for installation to complete; a success message will appear
4. Done! All 14 subagents are automatically ready and available across all projects

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

- 14 AI roles each run independently, unable to see each other's thought processes
- Six Ministries can work in parallel (no queuing)
- The Chancellery cannot see how the Secretariat thinks during review — truly independent review
- All roles use the strongest opus model

---

## Claude.ai Web / Desktop (Lite Mode)

### Method 1: Project Knowledge (Recommended, Permanent)

1. Open [claude.ai](https://claude.ai/) and log in
2. Find **Projects** in the sidebar, click **+ New Project**
3. Name the project, e.g., "Life OS"
4. Click into the project
5. Find **Project Settings**, click **Add to project knowledge**
6. Download the SKILL.md file: 👉 **[Click here to download](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)** (click the ⬇️ download button in the top right, or click "Raw" then Ctrl+S / Cmd+S to save)
7. Upload the downloaded `SKILL.md` file to Project Knowledge
8. Done! Every new conversation in this project will have Three Departments and Six Ministries capabilities

### Method 2: Single Conversation (Temporary Trial)

1. Open [claude.ai](https://claude.ai/) and start a new conversation
2. Download the SKILL.md file: 👉 **[Click here to download](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**
3. **Drag** the `SKILL.md` file into the conversation window
4. Start asking questions

> Method 2 only works for the current conversation; you need to re-upload after closing.

### Desktop App

The Claude desktop app (macOS / Windows) works identically to the web version and supports Project Knowledge.

---

## Cursor

[Cursor](https://cursor.com/) is an AI code editor that supports the Agent Skills standard.

### Installation Steps

1. Open Cursor
2. Open the built-in terminal (shortcut: `` Ctrl+` `` or `` Cmd+` ``)
3. Enter the following command and press Enter:

```bash
npx skills add jasonhnd/life_OS
```

4. Wait for installation to complete
5. Done! Available in Cursor's AI chat (Cmd+L / Ctrl+L)

---

## VS Code + GitHub Copilot

[VS Code](https://code.visualstudio.com/) with the GitHub Copilot extension also supports Agent Skills.

### Prerequisites

You need to have the [GitHub Copilot extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) installed.

### Installation Steps

1. Open VS Code
2. Open the built-in terminal (shortcut: `` Ctrl+` ``)
3. Enter the following command and press Enter:

```bash
npx skills add jasonhnd/life_OS
```

4. Wait for installation to complete
5. Done! Available in Copilot Chat

---

## Gemini CLI

[Gemini CLI](https://github.com/google-gemini/gemini-cli) is Google's command-line AI tool that supports the Agent Skills standard.

### Installation Steps

1. Open Terminal
2. Enter the following command and press Enter:

```bash
npx skills add jasonhnd/life_OS
```

3. Done! Available in Gemini CLI conversations

---

## OpenAI Codex CLI

[Codex CLI](https://github.com/openai/codex) is OpenAI's command-line AI tool that supports the Agent Skills standard.

### Installation Steps

1. Open Terminal
2. Enter the following command and press Enter:

```bash
npx skills add jasonhnd/life_OS
```

3. Done! Available in Codex CLI conversations

---

## ChatGPT

[ChatGPT](https://chat.openai.com/) does not support the Agent Skills standard and requires manual setup.

### Method 1: Create a Custom GPT (Recommended, Permanent)

1. Open [chat.openai.com](https://chat.openai.com/) and log in (requires Plus subscription)
2. Click **Explore GPTs** in the sidebar
3. Click **+ Create** in the top right
4. In the **Configure** tab:
   - **Name**: Enter `Life OS`
   - **Description**: Enter `Three Departments and Six Ministries personal cabinet system`
   - **Instructions**: Open 👉 **[SKILL.md raw content](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)**, select all (Ctrl+A / Cmd+A), copy (Ctrl+C / Cmd+C), paste into the Instructions field
5. Click **Save** in the top right, select "Only me"
6. Done! Find the "Life OS" GPT in the ChatGPT sidebar and click to start a conversation

> **Note**: ChatGPT's Instructions have a character limit (~8000 characters). If you hit the limit after pasting, remove content below "10 Standard Scenarios" in SKILL.md, keeping only the core role definitions and process descriptions.

### Method 2: Single Conversation (Temporary Trial)

1. Open [chat.openai.com](https://chat.openai.com/) and start a new conversation
2. Open 👉 **[SKILL.md raw content](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)**
3. Select all, copy, paste into the conversation, and send
4. Start asking questions

> Only works for the current conversation.

---

## Gemini Web

[Gemini](https://gemini.google.com/) can use Life OS through the Gems feature.

### Via Gems (Recommended, Permanent)

1. Open [gemini.google.com](https://gemini.google.com/) and log in with your Google account
2. Find **Gem manager** in the sidebar, click **New Gem**
3. In the settings:
   - **Name**: Enter `Life OS`
   - **Instructions**: Open 👉 **[SKILL.md raw content](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)**, select all, copy, paste into the Instructions field
4. Click **Save**
5. Done! Find "Life OS" in the Gems list and click to start a conversation

### Single Conversation (Temporary Trial)

Paste the entire content of SKILL.md directly into a new conversation, then start asking questions.

---

## Other Platforms

### Platforms Supporting the Agent Skills Standard

If your AI tool supports the [Agent Skills standard](https://agentskills.io/) (e.g., Roo Code, Windsurf, JetBrains Junie, etc.), use this command to install:

```bash
npx skills add jasonhnd/life_OS
```

See the full list of compatible platforms at [agentskills.io](https://agentskills.io/).

### Platforms Without Agent Skills Support

Universal method:
1. Open 👉 **[SKILL.md raw content](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)**
2. Select all and copy
3. Paste into the platform's System Prompt / Instructions / Custom Instructions

Most AI platforms support some form of custom instructions.

---

## Pro vs Lite Mode Comparison

| | Lite | Pro (Claude Code) |
|--|------|-------------------|
| Role isolation | All roles in the same conversation, sharing context | Each role runs independently, invisible to others |
| Chancellery review | Can see the Secretariat's reasoning (weakened independence) | Cannot see it, truly independent judgment |
| Six Ministries execution | One after another, sequential | Simultaneous, parallel |
| Model | Platform's current model | All roles use opus |
| Installation | Upload/paste SKILL.md | One command |
| Supported platforms | 30+ | Claude Code exclusive |

**Lite mode is still valuable**: Even in a single conversation, the Six Ministries analyzing from different angles, the Chancellery doing emotional review, and the Remonstrator monitoring your behavioral patterns — these mechanisms still deliver more comprehensive analysis than asking AI directly.

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

## Updates

### Check Current Version

The `version` field at the top of SKILL.md shows the current version number. See the latest version on [GitHub](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md) or the [changelog](../CHANGELOG.md).

### Update Methods by Platform

| Platform | How to update |
|----------|--------------|
| **Claude Code** | Re-run `/install-skill https://github.com/jasonhnd/life_OS`, automatically overwrites the old version |
| **Claude.ai** | Go to Project Settings → delete old SKILL.md → re-upload [new version](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md) |
| **Cursor / VS Code etc.** | Re-run `npx skills add jasonhnd/life_OS`, automatically overwrites |
| **ChatGPT** | Edit your Life OS GPT → replace Instructions with [new SKILL.md content](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md) |
| **Gemini** | Edit your Life OS Gem → replace Instructions with [new SKILL.md content](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md) |

### How to Know When There's a New Version?

- [Watch this repository](https://github.com/jasonhnd/life_OS) on GitHub to get notified of updates
- Check the [changelog (CHANGELOG.md)](../CHANGELOG.md)

---

## FAQ

**Q: I've never used an AI tool before. Which platform should I start with?**
A: Start with [Claude.ai](https://claude.ai/) (web version, free signup) and install via Project Knowledge. Simplest setup, complete experience.

**Q: Can the Six Ministries run in parallel in Lite mode?**
A: No. Parallel execution is exclusive to Pro mode (Claude Code). In Lite mode, all roles execute sequentially in one conversation.

**Q: Can I use it without connecting Notion?**
A: Yes. Notion is an optional data layer. Without it, all features work normally — you just won't have cross-session memory.

**Q: SKILL.md is too long and won't fit on my platform. What should I do?**
A: Remove content below "10 Standard Scenarios" and "Token Consumption Estimates", keeping the core role definitions and process descriptions (~4000 characters).

**Q: Can I use it in a language other than Chinese?**
A: Yes. The system instructions are in Chinese, but you can ask questions in any language and it will work normally.

**Q: Do I need to reinstall for every conversation?**
A: Depends on the installation method. Project Knowledge (Claude.ai), Custom GPT (ChatGPT), Gems (Gemini), and `/install-skill` (Claude Code) are all install-once-use-forever. Only the "single conversation" method requires repeating each time.
