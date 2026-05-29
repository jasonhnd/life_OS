---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# 多平台编排: Claude / Gemini / Codex

Life OS 支持 3 个平台: Claude Code、Gemini CLI / Antigravity、OpenAI Codex CLI。每个平台有自己的编排文件, 但 16 个 agent 定义**完全共享**。

---

## 文件一览

| 文件 | 用途 | 平台 |
|------|------|------|
| `pro/CLAUDE.md` | Claude 平台的编排协议 | Claude Code |
| `pro/GEMINI.md` | Gemini 平台的编排协议 | Gemini CLI / Antigravity |
| `pro/AGENTS.md` | Codex 平台的编排协议 | OpenAI Codex CLI |
| `pro/GLOBAL.md` | 通用 agent 规则 | 3 平台共用 |
| `pro/agents/*.md` | 16 个 subagent 定义 | 3 平台共用 |
| `SKILL.md` | Skill 根入口 | 3 平台共用 |
| `themes/*.md` | 9 个主题 | 3 平台共用 |
| `references/*.md` | 规格文件 | 3 平台共用 |

---

## 三份编排文件的差别

三份文件结构等价, 内容大部分相同 (11 步工作流、状态机、信息隔离、安全边界)。**真正不同的只有 3 件事**:

1. **subagent 启动机制** (不同平台的 API 不同)
2. **工具名映射** (每个平台有自己的内置工具名)
3. **"环境检测与强制 Pro Mode" 的平台名**

---

## 差别 1: Subagent 启动机制

### Claude Code

Claude 用内置的 `Task` 工具启动 subagent。主 agent 调用 `Task(subagent_type=reviewer, prompt=...)`, 启动一个独立 context 的 subagent。

### Gemini CLI / Antigravity

Gemini 作为独立的 agent 实例启动。每个 `pro/agents/*.md` 是 self-contained subagent definition。

调用模式: "Spawn a new agent instance with the agent file's content as its system prompt, passing only the specified input data."

### Codex CLI

Codex 支持 parallel spawning — 对六部并行尤其有用。

调用模式: "Spawn a new agent with the agent file's content as its system prompt, passing only the specified input data."

---

## 差别 2: 工具名映射

agent 文件 frontmatter 的 `tools:` 字段是**平台无关的**。在不同平台上, 这些工具名被翻译成平台自己的工具名:

| agent 里写 | Claude 映射 | Gemini 映射 | Codex 映射 |
|-----------|------------|-----------|----------|
| `Read` | `Read` | `read_file` | `read_file` |
| `Write` | `Write` | `write_file` | `write_file` |
| `Edit` | `Edit` | `edit_file` | `edit_file` |
| `Grep` | `Grep` | `search_files` | `grep` |
| `Glob` | `Glob` | `list_files` | `glob` |
| `Bash` | `Bash` | `run_shell` | `shell` |
| `WebSearch` | `WebSearch` | `google_search` | `web_search` |
| `WebFetch` | `WebFetch` | `fetch_url` | `web_fetch` |
| `Agent` | 内置 Task 工具 | spawn subagent | spawn subagent |

### model 字段

每个 agent 文件都写 `model: opus`。映射:
- Claude: 直接映射到 Claude Opus
- Gemini: 映射到 Gemini 最强可用模型 (auto-select)
- Codex: 映射到 Codex 最强可用模型 (auto-select)

`opus` 在这里是「平台无关的意图标记」, 意思是「用最强可用模型」。

---

## 差别 3: 环境强制 Pro Mode

三份文件各自的「Pro Mode 强制声明」:

### Claude Code

```
## CC Environment Enforces Pro Mode (HARD RULE)

When a Claude Code environment is detected, Pro Mode must be used
(launching independent subagents); simulating roles within a single
context is prohibited.
```

### Gemini

```
## Gemini Environment Enforces Pro Mode (HARD RULE)

When Gemini CLI or Antigravity is detected, Pro Mode must be used
(launching independent subagents); simulating roles within a single
context is prohibited.
```

### Codex

```
## Codex Environment Enforces Pro Mode (HARD RULE)

When Codex CLI is detected, Pro Mode must be used (spawning independent
subagents); simulating roles within a single context is prohibited.
```

实质是同一条规则, 只是平台名和动词略有不同 (launching / spawning)。

---

## 平台自动检测逻辑

SKILL.md 被 load 时, 平台根据自己的 CLI 环境选择对应的编排文件:

- Claude Code 读 `pro/CLAUDE.md`
- Gemini CLI 读 `pro/GEMINI.md`
- Codex CLI 读 `pro/AGENTS.md` (AGENTS.md 是开放标准, Codex 跟随这个标准)

**检测不是动态的**, 是**约定的**。每个 CLI 在启动 skill 时, 按自己的设计选定一份编排文件。

### SKILL.md 的安装命令提示

```
| Platform | Command |
|----------|---------|
| Claude Code | /install-skill https://github.com/jasonhnd/life_OS |
| Gemini CLI / Antigravity | npx skills add jasonhnd/life_OS |
| OpenAI Codex CLI | npx skills add jasonhnd/life_OS |
```

用户自己选平台, 平台自己知道读哪份编排文件。

---

## 为什么 agent 文件所有平台共享

### 核心设计: agent 是抽象的

`pro/agents/*.md` 里不写任何平台具体的东西。全部定义是:

- 角色身份 (你是谁、你干什么)
- 输入 (你会收到什么)
- 输出 (你要产出什么格式)
- 行为规则 (你要遵守什么)
- 反模式 (你不能做什么)

工具名、model 名都是**平台无关的意图标记**, 由编排文件翻译成平台具体实现。

### 好处

1. **改 agent = 一次改, 3 平台通用**。比如修改 REVIEWER 的封驳规则, 只改 `pro/agents/reviewer.md`, 3 平台自动同步。
2. **测试方便**。一个 agent 在 Claude 上测好了, Gemini 和 Codex 上行为一致 (模型差异除外)。
3. **文档清晰**。用户想知道「REVIEWER 做什么」, 直接读 reviewer.md, 不用看 3 份编排文件。

### 坏处

1. **工具名差异只能在编排文件里处理**, 这让编排文件的映射表变长
2. **平台新出工具时**, 3 份编排文件都要加新映射

---

## 差异实战: 如果 agent 文件里写错了

假设某 agent 文件写了 Claude-specific 的工具名:

```yaml
tools: Read, Grep, Glob, Task   # ← 错了, Task 是 Claude 内置
```

### Claude 上会发生什么

正常工作, 因为 Task 是 Claude 自己的工具。

### Gemini / Codex 上会发生什么

找不到 `Task` 工具 → 报错或者用不上 subagent 能力 → agent 行为退化。

### 正确做法

```yaml
tools: Read, Grep, Glob, Agent   # ← 对
```

`Agent` 是平台无关的抽象名。3 份编排文件各自映射到 Task / spawn subagent / spawn subagent。

---

## AGENTS.md 特别说明

AGENTS.md 遵循一个**开放标准** — 不是 Codex 专属, 任何新兴的 CLI agent 平台都可以支持这个标准。

好处: 如果未来某个新平台 X 也支持 AGENTS.md 标准, Life OS 可能不需要写新的编排文件, 直接用 AGENTS.md。

实际上, 目前 Life OS 有 3 份平行编排文件, 是因为 3 个平台虽然都支持 skill + subagent, 但细节不同 (subagent 启动 API、工具名)。

如果 3 个平台的 API 未来收敛, Life OS 可以合并成 1 份编排文件。

---

## 3 个平台在具体能力上的差异

### Claude Code

- Subagent 支持 ✅
- 内置 MCP 工具丰富 (Notion, GDrive, computer-use 等)
- Notion MCP 必须在主 context 调用 (不能在 archiver subagent 里调) — 这就是 Step 10a 存在的原因

### Gemini CLI / Antigravity

- Subagent 支持 ✅
- 工具集跟 Claude 类似但名字不同
- Notion MCP 可用性取决于用户配置

### Codex CLI

- Subagent 支持 ✅
- Parallel spawning 支持好 (六部并行尤其顺)
- 工具集更接近 Codex 原生

---

## 换新平台的流程

想支持新平台 X:

1. 写一份新的编排文件, 比如 `pro/X.md`
2. 照着 CLAUDE.md 结构, 改 "Platform Mapping" 章节的工具名映射
3. 改 "X Environment Enforces Pro Mode" 章节
4. 如果 X 的 subagent 启动机制有特殊之处, 说清楚
5. 测试: 确认 16 个 agent 在 X 上的行为和 Claude 上一致

**不要改**:
- 16 个 agent 文件 — 它们是平台无关的
- SKILL.md 的角色表 — 它定义的是 engine ID
- themes/ — 显示名和平台无关
- references/ — 规格和平台无关
- GLOBAL.md — 基线规则和平台无关

---

## 如何定位跨平台 bug

### 症状: 「在 Claude 上好用, 在 Gemini 上报错」

可能原因:
1. agent 文件里用了 Claude-specific 工具名
2. 某 subagent 启动时缺少 Gemini 需要的参数
3. Gemini 的模型上下文窗口小于 Claude, 输入被截断

排查:
1. 看 `pro/GEMINI.md` 的工具名映射表, 检查 agent 文件的 `tools:` 字段是否都有对应映射
2. 看 Gemini 的 subagent 启动 API 文档, 对比 `pro/GEMINI.md` 的 "Subagent Invocation" 章节
3. 打印 subagent 收到的 context 长度, 确认没超出 Gemini 的窗口

### 症状: 「3 平台都能跑但输出不一样」

可能原因:
1. 模型能力差异 (Claude Opus vs Gemini Pro vs Codex)
2. 某 agent 文件的指令对 Claude 清楚, 对 Gemini 模糊

处理:
1. 接受一定程度的模型差异 (这是 LLM-agnostic 的代价)
2. 如果差异过大, 改 agent 文件让指令更明确 (不允许含糊表达)

---

## 跨平台同步维护

改任何一处编排逻辑时, **3 份编排文件都要同步**。

常见的坑:
- 改了 CLAUDE.md 的 Step 10a (Notion sync 模板), 忘了改 GEMINI.md / AGENTS.md
- 加了新的状态转换规则, 只改了一份

**建议**:
- 改编排文件时, 把 3 份文件打开, 一个改完立刻改其他两份
- commit 时把 3 份放在同一个 commit 里
- 最好有一个脚本对比 3 份文件的 "Complete Workflow" 章节, 检查结构一致
