# 多平台设置 · Claude Code + Antigravity + Codex 一起用

Life OS 不绑死在单一 CLI 上。同一个 second-brain 可以同时被 Claude Code、Google Antigravity、OpenAI Codex CLI 使用——三个平台共享数据、共享 agent 定义，只是**编排文件**不同。

本文告诉你：怎么安装到每个平台、gitignore 的关键修复（worktrees 陷阱）、为什么 CLAUDE.md / GEMINI.md / AGENTS.md 要分开、同步冲突怎么处理。

---

## 为什么多平台

三个平台各有优势：

| 平台 | 优势 | 什么时候用 |
|------|------|-----------|
| **Claude Code** | Opus 4.x 推理深度 | 重大决策、深度研究、复杂议程 |
| **Google Antigravity** | Gemini 长上下文 + Web 集成 | 查资料多、跨文档分析 |
| **OpenAI Codex CLI** | 速度快、便宜 | 日常查询、简单议程 |

**你不必三个都用**。很多用户只用 Claude Code。但如果你已经多平台工作，Life OS 支持你**一套数据三个入口**。

---

## 安装

每个平台用自己的命令：

```bash
# Claude Code
/install-skill https://github.com/jasonhnd/life_OS

# Google Antigravity (Gemini CLI)
npx skills add jasonhnd/life_OS

# OpenAI Codex CLI  
npx skills add jasonhnd/life_OS
```

安装后：
- Claude Code 读 `pro/CLAUDE.md`
- Gemini / Antigravity 读 `pro/GEMINI.md`
- Codex 读 `pro/AGENTS.md`

**16 个 subagent 定义共享**（都在 `pro/agents/*.md`）。只有编排文件分三份。

---

## 共享 second-brain

三个平台共享**同一个 second-brain 目录**。第一次配置的时候，任何平台都会问：

```
📦 First session — no second-brain detected.

Where should I store your data?
a) GitHub (version-controlled, works with Obsidian)
b) Google Drive (zero setup)
c) Notion (mobile-friendly)
You can pick multiple.
```

你选完后，`_meta/config.md` 记录配置。另外两个平台启动时读这个配置，**直接接入同一个 second-brain**。

---

## 关键陷阱：worktrees 和 gitignore

这是多平台用户最常见的坑。

### 问题

如果你在 Claude Code 里用 git worktrees（比如 Anthropic 的 `ccd_directory` 或 git 自带的 worktree 功能），默认情况下 `.claude/worktrees/` 目录会被 Claude Code 创建。

如果你的 second-brain 是 git 仓库（选项 a），这个目录可能**被 git 追踪**——导致：
- 所有 worktree 快照被 commit
- 推到 GitHub 后仓库变得臃肿
- Antigravity 或 Codex pull 下来会看到一堆 worktree 垃圾

### 解决：在 second-brain 根部加 .gitignore

```
# ~/second-brain/.gitignore

# Claude Code worktrees — 不跨平台同步
.claude/worktrees/
.claude/cache/

# Antigravity / Gemini 本地缓存
.gemini/
.ag/

# Codex 本地 session 数据
.codex/

# 平台通用临时文件
*.tmp
*.lock
_meta/.merge-lock
```

**关键行**：`.claude/worktrees/` 必须 ignore。很多人的第一次 git push 带了 500MB worktree 就是因为少了这行。

### 如果已经 commit 进去了

```bash
cd ~/second-brain
git rm -r --cached .claude/worktrees/
git commit -m "chore: untrack worktrees (local only)"
git push
```

然后更新 .gitignore。

---

## 编排文件为什么要分三份

你可能想问：为什么不一个文件统一？

**原因**：三个平台对编排指令的解释不同。

### Claude Code 特性

- **真实 subagent** 是核心——Pro Mode 必须用 `Launch(agent)`，不能单 context 模拟
- Opus 模型指令风格偏向"先规划后执行"
- `Task` 工具 + subagent 架构是强制

`pro/CLAUDE.md` 强化这些：

```
## CC Environment Enforces Pro Mode (HARD RULE)

When a Claude Code environment is detected, Pro Mode must be used 
(launching independent subagents); simulating roles within a single 
context is prohibited.
```

### Antigravity / Gemini 特性

- Gemini 的长 context (1M+) 让单 context 模拟可行
- 但 Pro Mode 仍优先——只是 fallback 可以容忍
- Web 工具集成更自然

`pro/GEMINI.md` 类似，但放宽了 "subagent 必须" 到 "subagent 推荐"。

### Codex 特性

- 快、便宜、但上下文较短
- 复杂议程可能被截断
- 倾向于 express path（快车道）

`pro/AGENTS.md` 针对 Codex 有明确引导：

```
# Codex 的最佳实践

- 大议程分 2-3 条会话跑完更稳
- express path 是 Codex 的默认优势场景
- Opus-级深推理的议程建议转 Claude Code
```

**设计理念**：每个平台发挥自己的长处，而不是削足适履。

---

## 跨平台数据流

### 场景 1：桌面 Claude Code 跑完，手机 Antigravity 继续

```
09:00  你在桌面 Claude Code "上朝" → 做完议程 → "退朝"
         起居郎写: _meta/outbox/claude-20260420-0915/
         git push 到 GitHub
         Notion 同步
  
12:00  午饭在咖啡馆，打开手机 Antigravity "开始"
         早朝官 Phase B 读 _meta/config.md → git pull
         发现 _meta/outbox/claude-20260420-0915/ 未合并
         → Phase B.7 Outbox Merge
         合并到 projects/*/decisions, tasks, journal
         输出简报里显示: "📮 Merged 1 offline session"
```

第二个平台**无缝接上**。

### 场景 2：并发写入冲突

假设你不小心在两个平台同时开会话：

```
平台 A: Claude Code 09:00 启动
平台 B: Antigravity 09:05 启动

两边都做 outbox merge，可能冲突。
```

系统有保护——`_meta/.merge-lock`：

- 先到的平台写 lock + timestamp
- 后到的平台看到 lock < 5 分钟 → 跳过 merge，只做读取
- 第一个结束后删 lock
- 后启动者如果 > 5 分钟后依然需要 merge → 再合

**实际操作**：你几乎不会遇到这个。但如果同时退朝，可能只有先完成的那个 push，后完成的需要 `git pull --rebase`。

---

## 每个平台的 ergonomic 差异

### Claude Code

- 命令：`上朝` `退朝` 和英文 `start` `adjourn` 都支持
- 支持自定义 slash command（在 `.claude/commands/`）
- CC CLI 支持 `/save` 快捷命令

### Antigravity

- 命令：同上
- Gemini 长 context 让一次会话可以议多个议程（Claude Code 里建议拆开）
- Antigravity 的 "workflow view" 可以同时看多个 agent 运行

### Codex

- 命令：同上
- Codex CLI 对"长运行任务"较敏感——议程跑超过 5 分钟可能被截
- 建议 Codex 主做 express path，大议程用 Claude Code

---

## 主题（Theme）是 per-session 的

**重要**：Theme 是会话级的，不是平台级的。

- 你可以在 Claude Code 会话里用 **三省六部** 主题
- 同时在 Antigravity 里用 **C-Suite** 主题
- 在 Codex 里用 **霞が関** 主题

彼此不影响。写入 second-brain 的数据是**功能 ID 中立**的——你在"丞相"下做的决策，在"Chief of Staff"的平台也能读到完整历史。

Theme 只影响**输出的 display name**，不影响数据本身。

---

## 配置文件对照表

| 文件 | 平台专属 | 内容 |
|------|----------|------|
| `SKILL.md` | 共享 | 系统总入口 |
| `pro/GLOBAL.md` | 共享 | 通用 agent 规则 |
| `pro/agents/*.md` | 共享 | 16 个 subagent 定义 |
| `themes/*.md` | 共享 | 9 个主题 |
| `references/*.md` | 共享 | 规格定义 |
| `pro/CLAUDE.md` | Claude Code | 编排协议 |
| `pro/GEMINI.md` | Gemini/Antigravity | 编排协议 |
| `pro/AGENTS.md` | Codex | 编排协议 |

设计原则：**data 和 logic 共享，编排方言分开**。

---

## 项目级 CLAUDE.md（在 second-brain 里）

如果你的 second-brain 作为 Claude Code project，可以在根部加 `CLAUDE.md` 来定制**这个 second-brain** 的额外规则（比如个人偏好）：

```markdown
# My Second-Brain · Custom Rules

## 默认主题
三省六部 (zh-classical)

## 必写字段
所有 decisions 必须包含 `reversibility` 字段（true/false）

## 个人偏好
- 简报中不要显示 Metrics Dashboard（我自己看）
- 谏官报告不要超过 10 句
```

同理 `GEMINI.md` for Antigravity, `AGENTS.md` for Codex。

**这些是 per-second-brain 定制**，不影响其他人的 Life OS 安装。

---

## 升级策略

Life OS 更新时：

```bash
# Claude Code
cd ~/.claude/skills/life_OS && git pull

# Antigravity / Codex
npx skills add jasonhnd/life_OS   # 重新运行即升级
```

升级**只动系统代码**，不动你的 second-brain 数据。

早朝官会在 Phase C.8 自动做 version check：

```
🏛️ Life OS: v1.6.2a | Latest: v1.7.0 ⬆️ Update available
  Claude Code: cd ~/.claude/skills/life_OS && git pull
  Gemini/Codex: npx skills add jasonhnd/life_OS
```

三个平台独立升级——你可能 Claude Code 是 v1.7，Codex 还在 v1.6.2。这不会导致数据问题（数据层向前兼容），但会导致**功能差异**（v1.7 的新触发器在 Codex 上不起作用）。

**建议**：三个平台保持同步升级，每月一次检查。

---

## 故障排查

### 症状：Antigravity 看不到 Claude Code 刚做的决策

**原因**：Claude Code 没 push 到 GitHub（或 push 失败）

**排查**：
```bash
cd ~/second-brain
git status
git log --oneline -5
```

如果看到未 push 的 commit → 手动 push 或让 Claude Code 重新 "退朝"。

### 症状：两个平台的 SOUL 状态不一致

**原因**：snapshot 文件冲突，或 merge-lock 过期没清

**排查**：
```bash
ls ~/second-brain/_meta/snapshots/soul/ | tail -5
cat ~/second-brain/_meta/.merge-lock 2>/dev/null  # 应该不存在
```

如果 .merge-lock 存在且很旧 → 删掉，下次上朝会重新合并。

### 症状：Notion 只在一个平台同步成功

**原因**：Notion token 只在某个平台配置了

**排查**：
确认每个平台都配置了 Notion MCP（在各自的 settings）。Notion sync 由 orchestrator（主 context）做，不是 archiver subagent。

---

## 推荐的多平台用法

**Flow 1：Claude Code 为主，Antigravity 为副**

- 桌面办公：Claude Code（opus 深度）
- 出门 / 手机：Antigravity (Gemini 快且便携)
- Codex 不用

**Flow 2：Codex 为日常，Claude Code 为大事**

- 日常查询：Codex（便宜）
- 每周大决策：Claude Code（Opus 深度）
- Antigravity 作为 Web 研究工具

**Flow 3：全部都用**

- 早起 + 睡前：Claude Code（上朝/退朝最严）
- 中午快速议题：Codex
- 跨文档/Web 研究：Antigravity

数据统一，入口多样。

---

## 常见问题

**Q：能把 3 个平台的对话 log 合并吗？**
A：已合并。所有平台写到同一个 `_meta/journal/` 和 `decisions/`。起居郎的 session-id 里带平台前缀（`claude-20260420-0915` / `gemini-20260420-1200`），便于追溯来源。

**Q：如果只想用 1 个平台需要做啥？**
A：什么都不需要。单平台是默认状态。这篇文档是给多平台用户的。

**Q：Theme 冲突怎么办？**
A：不会冲突。Theme 是 per-session，每次会话独立选择。数据层用 functional ID，无 theme 影响。

**Q：可以用非官方平台吗？**
A：只要平台支持读 markdown + 调 MCP + 启动 subagent（或长 context 模拟），理论都能跑。但 SKILL 没专门适配文件——需要你自己写一个 `pro/XXX.md` 编排。

---

## 下一步

- 多平台配好之后，按 [daily-workflow.md](daily-workflow.md) 的节奏用
- second-brain 作为 git 仓库，定期备份：`git push` 已经是备份，多一个 remote 更稳
- 推荐加一个 Google Drive 作为 sync backend（防止 GitHub 意外）
