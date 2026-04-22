# 平台选择

Life OS 装在 AI 终端里。三个平台官方支持：Claude Code、Gemini CLI（含 Antigravity）、OpenAI Codex CLI。**必须是 Pro Mode 平台**，也就是支持真实独立 subagent + 信息隔离的那种。网页版聊天界面全部不行。

先给结论：**首选 Claude Code**，除非你有明确理由选其他两个。

---

## 为什么必须 Pro Mode

Life OS 的核心机制是 16 个 subagent **互相看不见对方的思考过程**。PLANNER 出计划，REVIEWER 独立复核时拿到的是计划本身，拿不到 PLANNER 怎么想出这个计划的推理链。这是制衡的前提 —— 如果 REVIEWER 能看到 PLANNER 的思考，它会被锚定，否决就走形式。

这需要真实的 subagent 机制：每个 agent 跑在独立上下文里，orchestrator 负责传消息，消息内容由协议规定（`pro/CLAUDE.md` 的「信息隔离」表）。

单一聊天窗口做不到这件事。你可以在 ChatGPT 里让它「扮演 16 个角色」，但那是同一个上下文在打不同称呼 —— 本质上只有一个声音，互相根本没法真正独立。Life OS 的所有 HARD RULE 在单上下文里全部失效。

---

## 平台对比

| 维度 | Claude Code | Gemini CLI / Antigravity | OpenAI Codex CLI |
|------|-------------|-------------------------|------------------|
| 模型 | Claude opus / sonnet / haiku 三级（按角色分配，自动选当前最强版本） | Gemini 最强可用模型（orchestrator 运行时自动选择，无硬编码版本） | Codex 最强推理模型（orchestrator 运行时自动选择，无硬编码版本） |
| Subagent 机制 | 原生 Task tool，独立上下文 | `.agents/skills/` 加载 subagent 文件 | `AGENTS.md` 开放标准 |
| 编排文件 | `pro/CLAUDE.md` | `pro/GEMINI.md` | `pro/AGENTS.md` |
| 信息隔离 | 完整 | 完整 | 完整 |
| 并行 subagent | 是 | 是 | 是 |
| 工具调用 | Read / Edit / Write / Bash / Grep / Glob / Task | 对应 Gemini 工具集（有映射表） | 对应 Codex 工具集 |
| Notion MCP | 支持（在主上下文执行 Step 10a） | 支持（同上） | 支持（同上） |
| 成本 | Claude 订阅 / Max 计划 / API 量 | Google AI Studio 免费额度大 / Gemini Advanced | ChatGPT Plus / Pro |
| 安装命令 | `/install-skill https://github.com/jasonhnd/life_OS` | `npx skills add jasonhnd/life_OS` | `npx skills add jasonhnd/life_OS` |
| 自动更新 hook | 支持（`scripts/setup-hooks.sh`） | 需手动 `npx skills add` 重装 | 需手动重装 |
| IDE 集成 | VS Code / Terminal | Antigravity workspace / Gemini CLI | Terminal |
| 主要限制 | opus 额度用光后降级到下一级 | `.claude/worktrees/` 会撑爆 context，必须加 .gitignore | 最强推理模型调用较慢；ratelimit 偏严 |

---

## 为什么首选 Claude Code

1. **Claude 的 opus 级模型在 PLANNER / REVIEWER / COUNCIL 上的判断力明显好**。这三个角色是引擎的瓶颈 —— 计划质量、否决敏锐度、辩论深度都决定了 Summary Report 的含金量。当前版本的 Claude opus 在这三件事上的信号比 Gemini 和 Codex 的最强版本都更稳定（作者主观评估，截至 2026-04）。
2. **Task tool 原生支持并行 subagent**。六部并行执行是编排协议的 HARD RULE（Step 5，one-by-one reporting）。Claude Code 的 Task tool 直接支持；Gemini / Codex 需要通过 skill 文件模拟，稍复杂。
3. **`pro/CLAUDE.md` 是母版**。GEMINI.md 和 AGENTS.md 是从它同步过来的 —— 有新功能时 CLAUDE.md 先改，另外两个后跟。首选平台意味着拿到最新逻辑的时差最短。
4. **auto-update hook** 可以做到「每天第一次上朝自动检查更新」，跑一次 `scripts/setup-hooks.sh` 就行。Gemini / Codex 要手动重装。
5. **Notion MCP 成熟度**。Step 10a 需要在 orchestrator 的主上下文里调用 Notion MCP 工具。Claude Code 的 MCP 体系最成熟，`~/.claude.json` 里配好 MCP server 就能用；另外两个平台 MCP 支持度和稳定性还在追赶。

Gemini 和 Codex 都是完整支持的一等公民 —— 功能同构，只是 Claude Code 在以上几点上稍稳。如果你的工作流已经在 Gemini 或 Codex 上，直接用，不需要切。

---

## 什么时候该选 Gemini CLI

- 已经在 Antigravity workspace 里做项目开发，不想再开一个 terminal
- Gemini Advanced 订阅不想浪费
- 需要 Google Drive 作为主存储（Gemini CLI 和 GDrive 集成更顺）
- 想跑 Gemini 最强模型的原生大 context 窗口（Claude opus 当前也是 1M 级，这点差距不大）

**必做**：把 `.claude/worktrees/` 加进 `.gitignore`。Claude Code 在共享 repo 里会产生临时 worktree 目录，Gemini 的 context loader 读到这些大文件会撑爆上下文然后假装没事地不响应。这是 Gemini 用户最常见的「上朝卡住」原因。

---

## 什么时候该选 Codex CLI

- ChatGPT Pro 订阅 + 想复用它的最强推理模型额度
- 团队已经用 AGENTS.md 标准（agents.md 开放协议）
- 喜欢 Codex CLI 的 UX

Codex 的最强推理模型在长链路推理上稳定，但 ratelimit 偏严 —— 如果朝议跑到 COUNCIL 辩论（3 轮 × 2 位思想家 × 每轮 500-1000 token），可能会撞限流。这时候只能等或拆会话。

---

## 明确不支持的平台

| 平台 | 为什么不行 |
|------|----------|
| ChatGPT（网页 / iOS / Android） | 单上下文 |
| Gemini Web / Gemini App | 单上下文 |
| Claude.ai 网页版 | 单上下文，没有 Task tool |
| Cursor（chat 模式） | 单上下文 |
| Copilot Chat | 单上下文 |
| 任何没实现 [Agent Skills 标准](https://agentskills.io/) 的 IDE 插件 | skill 文件加载不了 |

单上下文平台非要装也能把 SKILL.md 贴给它读，但行为会退化到「一个 LLM 扮演 16 个角色」—— REVIEWER 的 veto 不独立，COUNCIL 的辩论是左手打右手，AUDITOR 审到的永远是同一个声音。这种用法不叫 Life OS，叫「带结构的 prompt」。

---

## 一条补充建议

如果你打算长期用 Life OS 做主要决策引擎，在两个平台上装一份：一个主力（比如 Claude Code），一个备用（比如 Gemini CLI）。SKILL.md 和 `pro/agents/*.md` 都是一样的 markdown，两边共享。真哪天 Opus 额度打满、或者 Anthropic 服务挂了，你切到另一个平台还能继续用，第二大脑的数据（GitHub / GDrive / Notion）平台无关，不会丢。

---

## 成本实测（作者本人用量）

给个参考数字，不是官方保证：

| 场景 | Claude Code | Gemini CLI | Codex CLI |
|------|------------|-----------|----------|
| 一次 start session（18 步）| ~15k tokens | ~18k tokens | ~20k tokens |
| 一次完整朝议（PLANNER→REVIEWER→DISPATCHER→6 部→REVIEWER→Summary→AUDITOR→ADVISOR）| ~80-120k tokens | ~90-140k tokens | ~100-150k tokens |
| 一次 Express 分析（ROUTER + 2 部） | ~20-30k tokens | 同量级 | 同量级 |
| 一次翰林院对话（2 位思想家 + 20 轮）| ~40-60k tokens | 同量级 | 同量级 |
| 一次 adjourn（ARCHIVER 4 阶段 + DREAM + orchestrator Notion sync）| ~30-50k tokens | ~35-55k tokens | ~40-60k tokens |

典型一天：1 次 start + 1-2 次完整朝议 + 3-5 次 Express + 1 次 adjourn ≈ 200-400k tokens。

Claude Code Max 计划日常日用足够；API 直接 billing 大概每天 $3-8 这个量级。

---

## 换平台时数据会怎样

核心：**第二大脑和平台解绑**。你的 SOUL / projects / wiki / journal 全都在你选的存储后端（GitHub / GDrive / Notion），和装在哪个 AI 平台无关。

换平台步骤：
1. 旧平台里说「退朝」，确保这次数据都 sync 上去了
2. 新平台上装 Life OS（命令见上表）
3. 第一次说「上朝」，系统会读你在 `_meta/config.md` 里声明的存储后端，自动 pull 所有历史
4. SOUL / wiki / user-patterns / strategic-map 全部还在

会丢的东西：平台原生的对话历史（不是 Life OS 写的 markdown），这个本来就不由 Life OS 管。

---

## 每个平台的已知坑

### Claude Code
- **opus 额度**：Max 计划里 opus 级模型是有额度的，用完会自动降级到 sonnet 级。PLANNER / REVIEWER / COUNCIL 在 sonnet 上也能跑，但判断力降一档，特别是 REVIEWER 的 veto 敏感度。关键决策前如果看到「降级到 sonnet」提示，可以等额度刷新或切 Gemini 备用
- **worktree 遗留**：之前用过 Claude Code 的 worktree 模式，目录里可能有 `.claude/worktrees/` 堆积。不清理会撑大 repo，影响 git push 速度。退一个 worktree 时选 "remove" 不要选 "keep"
- **MCP server 配置要点**：Notion MCP 配在 `~/.claude.json` 的 `mcp_servers` 字段。配好之后 orchestrator 才能在 Step 10a 执行 Notion sync

### Gemini CLI / Antigravity
- **`.claude/worktrees/` 必须 gitignore**：这是最常见的「Gemini 不响应」原因。Claude Code 的临时 worktree 文件被 Gemini 的 context loader 吞进去就撑爆了
- **Antigravity 的 skill 路径**：workspace scope 在 `.agents/skills/`，global scope 在 `~/.gemini/antigravity/skills/`。装错地方 Antigravity 找不到
- **工具名映射**：Gemini 的工具和 Claude 的不完全同名。`pro/GEMINI.md` 里有完整映射表，正常用户不需要知道，但调试时有用

### Codex CLI
- **最强推理模型 ratelimit**：COUNCIL 辩论 + 翰林院圆桌这两个高 token 场景容易撞限流。遇到时拆会话（先处理决策，下一个会话单独开圆桌）
- **AGENTS.md 标准**：Codex 遵循开放的 agents.md 协议。理论上其他支持这个协议的 agent 框架也能读 Life OS 的 `pro/AGENTS.md`，实测以 Codex 为准
- **Codex 的 MCP 支持**：比 Claude 新，偶尔有 Notion sync 时序问题。如果退朝后 Notion 没更新，手动说「sync notion」触发一次

---

## 快速决策树

如果你还拿不定主意，按顺序问自己：

1. 有没有 Claude 订阅或 Anthropic API key？→ 有就 Claude Code，结束
2. 主要在 Antigravity 或 Google 生态里工作？→ Gemini CLI
3. 只有 ChatGPT Pro？→ Codex CLI
4. 什么都没有、但想试试？→ Claude Code + 免费试用额度，或 Gemini CLI + Google AI Studio 免费额度

三个平台的体验差异在 80-95 分之间，功能完全同构。别在选平台上纠结超过 10 分钟 —— 装了用起来比选错重要 100 倍。
