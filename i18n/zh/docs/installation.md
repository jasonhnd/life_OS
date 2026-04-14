# 安装指南

Life OS 可以在多种 AI 平台上使用。选择你用的平台，按步骤操作即可。

> **SKILL.md** 是 Life OS 的核心文件，包含了三省六部制的所有指令。下文中多次提到这个文件。
> 👉 **[点击这里获取 SKILL.md](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**（打开后点右上角的"Raw"按钮可以看到纯文本，方便复制）

---

## 目录

- [Claude Code（Pro 模式）](#claude-codepro-模式)
- [Gemini CLI / Antigravity（Pro 模式）](#gemini-cli--antigravitypro-模式)
- [OpenAI Codex CLI（Pro 模式）](#openai-codex-clipro-模式)
- [其他平台](#其他平台)
- [安装验证](#安装验证)
- [故障排除](#故障排除)
- [更新](#更新)
- [常见问题](#常见问题)

---

## Claude Code（Pro 模式）

这是 Life OS 在 Claude 平台的完整形态：16 个独立 AI 角色，真正的信息隔离和并行执行。

### 前提

你需要已经安装了 [Claude Code](https://claude.ai/code)（Anthropic 的命令行 AI 工具）。

### 安装步骤

1. 打开终端（Terminal）
2. 输入以下命令并回车：

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

3. 等待安装完成，会显示安装成功的提示
4. 完成！16 个 subagent 自动就绪，所有项目都能用

### 验证

安装后，在 Claude Code 中输入：

```
帮我分析一下要不要换工作
```

如果看到以下格式的回复，说明安装成功：

```
🏛️ 丞相 · 启奏
📋 旨意：... | 📌 类型：... | 💡 建议启用：...
```

### Pro 模式的特别之处

- 16 个 AI 角色各自独立运行，互相看不到对方的思考过程
- 六部可以同时并行工作（不用排队）
- 门下省审查时看不到中书省怎么想的 —— 真正独立的审查
- 所有角色使用最强的 opus 模型

---

## Gemini CLI / Antigravity（Pro 模式）

Pro 模式现已支持 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 和 [Google Antigravity](https://idx.google.com/)，由 Gemini 2.5 Pro 驱动 16 个独立 subagent。

### 安装步骤

1. 打开终端（Gemini CLI）或 Antigravity 的内置终端
2. 输入以下命令：

```bash
npx skills add jasonhnd/life_OS
```

3. 完成！系统自动检测 Gemini 并加载 `pro/GEMINI.md` 进行编排

### Antigravity 注意事项

- Antigravity 从 `.agents/skills/`（工作区范围）或 `~/.gemini/antigravity/skills/`（全局范围）加载技能
- **重要**：将 `.claude/worktrees/` 添加到项目的 `.gitignore` 中，以防止 Claude Code worktree 产物导致上下文溢出。这是 Gemini 在同时使用 Claude Code 的项目中无法响应的最常见原因。

### 与 Claude Pro 模式的区别

- 自动使用 Gemini 最强可用模型（无硬编码版本号）
- 工具名自动映射（详见 `pro/GEMINI.md` 的映射表）
- 相同的流程、相同的信息隔离、相同的 16 个角色

---

## OpenAI Codex CLI（Pro 模式）

Pro 模式现已支持 [Codex CLI](https://github.com/openai/codex)，由 o3 驱动 16 个独立 subagent。

### 安装步骤

1. 打开终端
2. 输入以下命令：

```bash
npx skills add jasonhnd/life_OS
```

3. 完成！系统自动检测 Codex 并加载 `pro/AGENTS.md` 进行编排

### 与 Claude Pro 模式的区别

- 自动使用 Codex 最强可用模型（无硬编码版本号）
- 遵循 [AGENTS.md 开放标准](https://agents.md/)
- 相同的流程、相同的信息隔离、相同的 16 个角色

---

> **注意**：Life OS 需要 Pro 模式 —— 16 个独立 subagent 和真正的信息隔离。单上下文平台（ChatGPT、Gemini 网页版、Claude.ai 网页版）不受支持。

---

## 其他平台

### 支持 Agent Skills 标准的平台

如果你使用的 AI 工具支持 [Agent Skills 标准](https://agentskills.io/)（如 Roo Code、Windsurf、JetBrains Junie 等），统一使用以下命令安装：

```bash
npx skills add jasonhnd/life_OS
```

完整兼容平台列表见 [agentskills.io](https://agentskills.io/)。

> **注意**：Life OS 需要 Pro 模式（独立 subagent）。不支持 Agent Skills 的平台不兼容。

---

## 安装验证

不管用哪个平台，安装后可以用以下消息测试：

| 你说 | 应该看到 |
|------|---------|
| "帮我分析一下要不要买 MacBook" | 丞相判断为需要上报，启动三省六部流程 |
| "帮我翻译一段日语" | 丞相直接处理（不启动流程） |
| "早朝" | 早朝官出简报 |
| "我最近很迷茫" | 丞相询问是否启动翰林院 |

---

## 故障排除

**Gemini / Antigravity 在某个项目目录中停止响应**

通常是 `.claude/worktrees/` 中的大文件（Claude Code 会话残留）导致。这些 worktree 副本会淹没 Gemini 的上下文窗口。

修复方法：
1. 删除 worktree 文件夹：`rm -rf .claude/worktrees/`
2. 将 `.claude/worktrees/` 添加到 `.gitignore`
3. 重启 Antigravity / Gemini CLI

**移动仓库后 Git 操作失败，报错 `fatal: not a git repository`**

这是因为 Claude Code worktree 引用仍指向旧路径。`.claude/worktrees/` 目录中包含硬编码绝对路径的 `.git` 文件。

修复方法：
1. 清理 git worktree 引用：`git worktree prune`
2. 删除过时的 worktree 目录：`rm -rf .claude/worktrees/`
3. 检查损坏的配置：`git config --get core.hooksPath` —— 如果指向不存在的路径，运行 `git config --unset core.hooksPath`
4. 移除 worktree 扩展标志：`git config --unset extensions.worktreeConfig`

预防措施：移动仓库前（例如从 Dropbox 到 iCloud），务必先清理 worktree。Claude Code worktree 会话结束后，选择"remove"而非"keep"。

**Pro 模式在 Gemini/Codex 上没有激活**

确保通过 `npx skills add jasonhnd/life_OS` 安装，且技能文件在正确位置：
- Gemini CLI：`~/.gemini/skills/` 或项目级 `.agents/skills/`
- Codex CLI：`~/.codex/skills/`
- Claude Code：`~/.claude/skills/`

**上下文窗口溢出**

如果项目中有非常大的文件，AI 平台可能会静默失败。解决方案：
- 使用 `.gitignore` 排除构建产物、`node_modules/` 和大型二进制文件
- 对于 Antigravity，使用 `.agignore` 文件（如支持）排除无关目录

---

## 更新

### 查看当前版本

SKILL.md 顶部的 `version` 字段显示当前版本号。最新版本见 [GitHub](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md) 或 [更新日志](../CHANGELOG.md)。

### 各平台更新方法

| 平台 | 怎么更新 |
|------|---------|
| **Claude Code** | 重新运行 `/install-skill https://github.com/jasonhnd/life_OS` |
| **Gemini CLI / Antigravity** | 重新运行 `npx skills add jasonhnd/life_OS` |
| **Codex CLI** | 重新运行 `npx skills add jasonhnd/life_OS` |

### 怎么知道有新版本？

- 在 GitHub 上 [Watch 这个仓库](https://github.com/jasonhnd/life_OS)，有更新时会收到通知
- 查看 [更新日志（CHANGELOG.md）](../CHANGELOG.md)

---

## 常见问题

**Q：应该从哪个平台开始？**
A：推荐 [Claude Code](https://claude.ai/code)。完整 Pro 模式，16 个独立 subagent，一行命令安装。

**Q：我同时用 Claude Code 和 Antigravity，会冲突吗？**
A：不会。它们使用不同的编排文件（`CLAUDE.md` vs `GEMINI.md`）和不同的模型映射。共享的是 `pro/agents/*.md` 文件。只需确保 `.claude/worktrees/` 在你的 `.gitignore` 中，防止 Antigravity 因 Claude 的临时文件而卡住。

**Q：不连接 Notion 能用吗？**
A：能。Notion 是可选的数据层。不连接时所有功能照常工作，只是没有移动端的跨会话记忆。

**Q：可以用中文以外的语言吗？**
A：可以。系统支持英文、中文和日文。你用任何语言提问都能正常工作。

**Q：什么是快车道分析？**
A：当你的请求不涉及决策（只是分析、研究或规划）时，丞相可以跳过完整的三省流程，直接启动 1-3 个相关部门。更快、更省 token，非决策类任务质量不变。
