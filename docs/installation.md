# 安装指南

Life OS 可以在多种 AI 平台上使用。选择你用的平台，按步骤操作即可。

> **SKILL.md** 是 Life OS 的核心文件，包含了三省六部制的所有指令。下文中多次提到这个文件。
> 👉 **[点击这里获取 SKILL.md](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**（打开后点右上角的"Raw"按钮可以看到纯文本，方便复制）

---

## 目录

- [Claude Code（推荐，Pro 模式）](#claude-code推荐pro-模式)
- [Claude.ai 网页版 / 桌面版（Lite 模式）](#claudeai-网页版--桌面版lite-模式)
- [Cursor](#cursor)
- [VS Code + GitHub Copilot](#vs-code--github-copilot)
- [Gemini CLI](#gemini-cli)
- [OpenAI Codex CLI](#openai-codex-cli)
- [ChatGPT](#chatgpt)
- [Gemini 网页版](#gemini-网页版)
- [其他平台](#其他平台)
- [Pro vs Lite 模式对比](#pro-vs-lite-模式对比)
- [安装验证](#安装验证)
- [更新](#更新)
- [常见问题](#常见问题)

---

## Claude Code（推荐，Pro 模式）

这是 Life OS 的完整形态：14 个独立 AI 角色，真正的信息隔离和并行执行。

### 前提

你需要已经安装了 [Claude Code](https://claude.ai/code)（Anthropic 的命令行 AI 工具）。

### 安装步骤

1. 打开终端（Terminal）
2. 输入以下命令并回车：

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

3. 等待安装完成，会显示安装成功的提示
4. 完成！14 个 subagent 自动就绪，所有项目都能用

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

- 14 个 AI 角色各自独立运行，互相看不到对方的思考过程
- 六部可以同时并行工作（不用排队）
- 门下省审查时看不到中书省怎么想的 —— 真正独立的审查
- 所有角色使用最强的 opus 模型

---

## Claude.ai 网页版 / 桌面版（Lite 模式）

### 方法 1：Project Knowledge（推荐，永久生效）

1. 打开 [claude.ai](https://claude.ai/)，登录你的账号
2. 在左侧栏找到 **Projects**，点击 **+ 新建 Project**
3. 给 Project 取个名字，比如"Life OS"
4. 点击进入这个 Project
5. 找到 **Project Settings**（项目设置），点击 **Add to project knowledge**
6. 下载 SKILL.md 文件：👉 **[点击这里下载](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**（打开后点击右上角 ⬇️ 下载按钮，或点"Raw"然后 Ctrl+S / Cmd+S 保存）
7. 把下载好的 `SKILL.md` 文件上传到 Project Knowledge
8. 完成！之后在这个 Project 里开的**每个新对话**都自带三省六部能力

### 方法 2：单次对话（临时试用）

1. 打开 [claude.ai](https://claude.ai/)，开一个新对话
2. 下载 SKILL.md 文件：👉 **[点击这里下载](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**
3. 把 `SKILL.md` 文件直接**拖入对话窗口**
4. 开始提问即可

> 方法 2 仅当前对话有效，关闭对话后需要重新上传。

### 桌面版（Desktop App）

Claude 桌面应用（macOS / Windows）与网页版操作完全相同，支持 Project Knowledge。

---

## Cursor

[Cursor](https://cursor.com/) 是一款 AI 代码编辑器，支持 Agent Skills 标准。

### 安装步骤

1. 打开 Cursor
2. 打开内置终端（快捷键：`` Ctrl+` `` 或 `` Cmd+` ``）
3. 输入以下命令并回车：

```bash
npx skills add jasonhnd/life_OS
```

4. 等待安装完成
5. 完成！在 Cursor 的 AI 对话（Cmd+L / Ctrl+L）中即可使用

---

## VS Code + GitHub Copilot

[VS Code](https://code.visualstudio.com/) 配合 GitHub Copilot 插件，也支持 Agent Skills。

### 前提

你需要已经安装了 [GitHub Copilot 插件](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)。

### 安装步骤

1. 打开 VS Code
2. 打开内置终端（快捷键：`` Ctrl+` ``）
3. 输入以下命令并回车：

```bash
npx skills add jasonhnd/life_OS
```

4. 等待安装完成
5. 完成！在 Copilot Chat 中即可使用

---

## Gemini CLI

[Gemini CLI](https://github.com/google-gemini/gemini-cli) 是 Google 的命令行 AI 工具，支持 Agent Skills 标准。

### 安装步骤

1. 打开终端
2. 输入以下命令并回车：

```bash
npx skills add jasonhnd/life_OS
```

3. 完成！在 Gemini CLI 对话中即可使用

---

## OpenAI Codex CLI

[Codex CLI](https://github.com/openai/codex) 是 OpenAI 的命令行 AI 工具，支持 Agent Skills 标准。

### 安装步骤

1. 打开终端
2. 输入以下命令并回车：

```bash
npx skills add jasonhnd/life_OS
```

3. 完成！在 Codex CLI 对话中即可使用

---

## ChatGPT

[ChatGPT](https://chat.openai.com/) 不支持 Agent Skills 标准，需要手动设置。

### 方法 1：创建 Custom GPT（推荐，永久生效）

1. 打开 [chat.openai.com](https://chat.openai.com/)，登录你的账号（需要 Plus 订阅）
2. 点击左侧栏的 **Explore GPTs**
3. 点击右上角 **+ Create**（创建）
4. 在 **Configure**（配置）标签页中：
   - **Name**：输入 `Life OS`
   - **Description**：输入 `三省六部制个人内阁系统`
   - **Instructions**：打开 👉 **[SKILL.md 原始内容](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)**，全选（Ctrl+A / Cmd+A），复制（Ctrl+C / Cmd+C），粘贴到 Instructions 框中
5. 点击右上角 **Save**（保存），选择 "Only me"（仅自己可用）
6. 完成！之后在 ChatGPT 左侧栏找到"Life OS"这个 GPT，点击开始对话

> **注意**：ChatGPT 的 Instructions 有字符限制（~8000 字符）。如果粘贴后提示超限，去掉 SKILL.md 中"10 个标准场景"以下的内容，只保留核心的角色定义和流程描述。

### 方法 2：单次对话（临时试用）

1. 打开 [chat.openai.com](https://chat.openai.com/)，开一个新对话
2. 打开 👉 **[SKILL.md 原始内容](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)**
3. 全选复制，粘贴到对话框中，发送
4. 然后开始提问即可

> 仅当前对话有效。

---

## Gemini 网页版

[Gemini](https://gemini.google.com/) 可以通过 Gems 功能使用 Life OS。

### 通过 Gems 设置（推荐，永久生效）

1. 打开 [gemini.google.com](https://gemini.google.com/)，登录你的 Google 账号
2. 在左侧栏找到 **Gem manager**，点击 **New Gem**（新建 Gem）
3. 在设置中：
   - **Name**：输入 `Life OS`
   - **Instructions**：打开 👉 **[SKILL.md 原始内容](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)**，全选复制，粘贴到 Instructions 框中
4. 点击 **Save**（保存）
5. 完成！之后在 Gems 列表中找到"Life OS"，点击开始对话

### 单次对话（临时试用）

在新对话中直接粘贴 SKILL.md 的全部内容，然后开始提问。

---

## 其他平台

### 支持 Agent Skills 标准的平台

如果你使用的 AI 工具支持 [Agent Skills 标准](https://agentskills.io/)（如 Roo Code、Windsurf、JetBrains Junie 等），统一使用以下命令安装：

```bash
npx skills add jasonhnd/life_OS
```

完整兼容平台列表见 [agentskills.io](https://agentskills.io/)。

### 不支持 Agent Skills 的平台

通用方法：
1. 打开 👉 **[SKILL.md 原始内容](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)**
2. 全选复制
3. 粘贴到该平台的 System Prompt / Instructions / Custom Instructions 中

大多数 AI 平台都支持某种形式的自定义指令。

---

## Pro vs Lite 模式对比

| | Lite | Pro（Claude Code） |
|--|------|-------------------|
| 角色隔离 | 所有角色在同一个对话中，共享上下文 | 每个角色独立运行，互相看不到 |
| 门下省审查 | 能看到中书省的推理过程（独立性弱化） | 看不到，真正独立判断 |
| 六部执行 | 一个接一个串行 | 同时并行 |
| 模型 | 平台当前模型 | 所有角色使用 opus |
| 安装 | 上传/粘贴 SKILL.md | 一行命令 |
| 支持平台 | 30+ | Claude Code 专属 |

**Lite 模式仍然有价值**：即使在单个对话中，六部各自从不同角度分析问题、门下省做感性审查、谏官监督你的行为模式，这些机制仍然比直接问 AI 得到更全面的分析。

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

## 更新

### 查看当前版本

SKILL.md 顶部的 `version` 字段显示当前版本号。最新版本见 [GitHub](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md) 或 [更新日志](../CHANGELOG.md)。

### 各平台更新方法

| 平台 | 怎么更新 |
|------|---------|
| **Claude Code** | 重新运行 `/install-skill https://github.com/jasonhnd/life_OS`，自动覆盖旧版 |
| **Claude.ai** | 进入 Project Settings → 删除旧的 SKILL.md → 重新上传 [新版](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md) |
| **Cursor / VS Code 等** | 重新运行 `npx skills add jasonhnd/life_OS`，自动覆盖 |
| **ChatGPT** | 编辑你的 Life OS GPT → 用 [新版 SKILL.md 内容](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md) 替换 Instructions |
| **Gemini** | 编辑你的 Life OS Gem → 用 [新版 SKILL.md 内容](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md) 替换 Instructions |

### 怎么知道有新版本？

- 在 GitHub 上 [Watch 这个仓库](https://github.com/jasonhnd/life_OS)，有更新时会收到通知
- 查看 [更新日志（CHANGELOG.md）](../CHANGELOG.md)

---

## 常见问题

**Q：我完全没用过 AI 工具，应该从哪个平台开始？**
A：推荐从 [Claude.ai](https://claude.ai/) 开始（网页版，免费注册），用 Project Knowledge 方式安装。操作最简单，体验完整。

**Q：Lite 模式下六部能并行吗？**
A：不能。并行执行是 Pro 模式（Claude Code）专属。Lite 模式所有角色在一个对话中依次执行。

**Q：不连接 Notion 能用吗？**
A：能。Notion 是可选的数据层。不连接时所有功能照常工作，只是没有跨会话记忆。

**Q：SKILL.md 太长，平台装不下怎么办？**
A：去掉"10 个标准场景"和"Token 消耗估算"以下的内容，保留核心的角色定义和流程描述（约 4000 字符）。

**Q：可以用中文以外的语言吗？**
A：可以。系统指令是中文的，但你用任何语言提问都能正常工作。

**Q：装完之后每次对话都要重新装吗？**
A：取决于安装方式。Project Knowledge（Claude.ai）、Custom GPT（ChatGPT）、Gems（Gemini）、`/install-skill`（Claude Code）都是一次安装永久生效。只有"单次对话"方式需要每次重新操作。
