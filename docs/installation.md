# 安装指南

Life OS 遵循 [Agent Skills 开放标准](https://agentskills.io/)，兼容 30+ 个 AI agent 产品。本文详细介绍各平台的安装和使用方式。

---

## Claude 生态

### Claude Code（Pro 模式）—— 推荐

Pro 模式是 Life OS 的完整形态：14 个独立 subagent，真正的进程隔离和并行执行。

**安装**：

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

安装后成为永久能力，所有项目都能用。

**验证**：安装后输入"帮我分析一下要不要换工作"，应该看到丞相启奏格式：

```
🏛️ 丞相 · 启奏
📋 旨意：... | 📌 类型：... | 💡 建议启用：...
```

**Pro 模式特性**：
- 14 个 subagent 独立进程、独立 context window
- 六部可并行执行
- 门下省审查时看不到中书省的思考过程 —— 真正的分权制衡
- 所有角色使用 opus 模型

### Claude.ai Web（Lite 模式）

**方法 1：Project Knowledge（推荐，永久生效）**

1. 在 Claude.ai 左侧栏创建一个 Project，比如"Life OS"
2. 进入 Project Settings → Add to project knowledge
3. 上传 `SKILL.md` 文件（[从 GitHub 下载](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)）
4. 之后在这个 Project 里开的**每个新对话**都自带三省六部能力

**方法 2：单次对话**

直接把 `SKILL.md` 文件拖入对话窗口。仅当前对话有效。适合临时试用。

**验证**：同上，输入一个需要分析的问题，看到丞相响应即成功。

### Claude.ai Desktop（Lite 模式）

与 Web 版操作相同。Claude Desktop 支持 Project Knowledge，步骤一致。

---

## Agent Skills 兼容平台（Lite 模式）

以下平台通过 [Agent Skills 标准](https://agentskills.io/) 支持 Life OS。安装命令统一为：

```bash
npx skills add jasonhnd/life_OS
```

### Cursor

1. 打开终端，运行 `npx skills add jasonhnd/life_OS`
2. Skill 会安装到项目的 `.cursor/skills/` 目录
3. 在 Cursor 的 AI 对话中即可使用

### VS Code Copilot

1. 打开终端，运行 `npx skills add jasonhnd/life_OS`
2. Skill 会安装到项目的 `.github/skills/` 目录
3. 在 Copilot Chat 中即可使用

### Gemini CLI

1. 运行 `npx skills add jasonhnd/life_OS`
2. Skill 会安装到项目的 `.gemini/skills/` 目录
3. 在 Gemini CLI 对话中即可使用

### OpenAI Codex CLI

1. 运行 `npx skills add jasonhnd/life_OS`
2. Skill 会安装到项目的 `.codex/skills/` 目录
3. 在 Codex CLI 对话中即可使用

### Roo Code

1. 运行 `npx skills add jasonhnd/life_OS`
2. 在 Roo Code 对话中即可使用

### 其他兼容平台

任何支持 Agent Skills 标准的平台都可以通过 `npx skills add jasonhnd/life_OS` 安装。完整兼容平台列表见 [agentskills.io](https://agentskills.io/)。

---

## Web 端 AI 助手（手动安装）

以下平台不支持 Agent Skills 标准，需要手动将 SKILL.md 的内容导入。

### ChatGPT

**方法 1：创建 Custom GPT（推荐）**

1. 进入 [ChatGPT](https://chat.openai.com/) → Explore GPTs → Create a GPT
2. 在 Instructions 中粘贴 `SKILL.md` 的全部内容
3. 命名为"Life OS"，保存
4. 之后选择这个 GPT 开对话即可

**方法 2：单次对话**

在对话开头粘贴 `SKILL.md` 的内容，然后开始提问。仅当前对话有效。

**注意**：ChatGPT Custom Instructions 有字符限制（~8000 字符）。如果 SKILL.md 超限，可以去掉"10 个标准场景"和"Token 消耗估算"部分，保留核心流程和角色定义。

### Gemini Web

**通过 Gems**：

1. 进入 [Gemini](https://gemini.google.com/) → Gems → New Gem
2. 在 Instructions 中粘贴 `SKILL.md` 的全部内容
3. 命名为"Life OS"，保存
4. 之后选择这个 Gem 开对话即可

### 其他 Web AI 助手

通用方法：将 `SKILL.md` 的内容粘贴到该平台的 System Prompt / Instructions / Custom Instructions 中。大多数平台都支持某种形式的自定义指令。

---

## Pro vs Lite 模式对比

| | Lite | Pro（Claude Code） |
|--|------|-------------------|
| 角色隔离 | 同一 context，所有角色共享上下文 | 独立进程，真正的信息隔离 |
| 门下省审查 | 能看到中书省的推理过程 | 看不到，独立判断 |
| 六部执行 | 串行（一个接一个） | 并行（同时执行） |
| 模型 | 平台当前模型 | 所有角色使用 opus |
| 安装方式 | 上传/粘贴 SKILL.md | `/install-skill` 一行命令 |
| 平台 | 30+ 平台 | Claude Code 专属 |

**Lite 模式的限制**：在单 context 中，模型已经"看到"了中书省的输出再去扮演门下省，信息隔离是模拟的而非强制的。分权制衡的效果弱于 Pro 模式，但多维度分析框架仍然有效。

**选择建议**：
- 如果你用 Claude Code → Pro 模式，获得完整体验
- 如果你用其他平台 → Lite 模式也有价值，重点在多维度分析和感性审查

---

## 安装验证

安装成功后，输入以下任一消息测试：

| 测试消息 | 预期响应 |
|---------|---------|
| "帮我分析一下要不要买 MacBook" | 丞相上报，启动三省六部流程 |
| "帮我翻译一段日语" | 丞相直接处理（不上报） |
| "早朝" | 早朝官出简报 |
| "我最近很迷茫" | 丞相询问是否启动翰林院 |

---

## 常见问题

**Q：Lite 模式下六部能并行吗？**
A：不能。Lite 模式在单个 context 中串行执行所有角色。并行执行是 Pro 模式（Claude Code）专属。

**Q：不连接 Notion 能用吗？**
A：能。Notion 是可选的数据层。不连接时所有决策和分析功能照常工作，只是没有跨会话记忆和自动存档。

**Q：SKILL.md 太长，平台装不下怎么办？**
A：去掉"10 个标准场景"和"Token 消耗估算"章节，保留核心的角色定义和流程描述。核心内容约 4000 字符。

**Q：可以用中文以外的语言吗？**
A：可以。AI 模型支持多语言。系统指令是中文的，但你用任何语言提问都能正常工作。角色输出会跟随你的语言。

**Q：如何更新到最新版本？**
A：Claude Code 用户重新运行 `/install-skill https://github.com/jasonhnd/life_OS`。其他平台重新下载 `SKILL.md` 并替换。
