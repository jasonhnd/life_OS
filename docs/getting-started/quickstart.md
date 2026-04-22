# 5 分钟 Quickstart

目标：装好之后，在 5 分钟内跑通一次完整的会话启动 → 对话 → 退朝 → 归档 sync 的循环。

---

## 1. 装 Life OS（30 秒）

开 terminal，按你用的平台选一条命令：

| 平台 | 命令 |
|------|------|
| Claude Code | `/install-skill https://github.com/jasonhnd/life_OS` |
| Gemini CLI / Antigravity | `npx skills add jasonhnd/life_OS` |
| OpenAI Codex CLI | `npx skills add jasonhnd/life_OS` |

回车，等提示安装完成。三个平台都不需要改任何配置文件。

不知道该选哪个？去 [choose-your-platform.md](choose-your-platform.md)。

---

## 2. 第一次说什么

直接在 terminal 里打这三个字：

```
上朝
```

就这样。不用自我介绍，不用说「我是新用户」，不用问「你能做什么」。

---

## 3. 预期看到的输出

### 如果你从来没用过（第二大脑不存在）

系统检测到 second-brain 目录不存在，会走首次设置流程：

```
🎨 Theme: 三省六部（检测到「上朝」是 Tang Dynasty 专属词，自动加载）

📦 未检测到 second-brain 目录。要初始化吗？
请选择存储后端（可多选）：
1) GitHub
2) Google Drive
3) Notion

输入数字（比如「13」表示 GitHub + Notion）：
```

选完，系统自动建好目录结构（projects/、areas/、wiki/、_meta/ 等），然后进入正常的上朝流程。

### 如果你已经有 second-brain

你会看到主题切换确认 + 完整的会话启动块：

```
🎨 Theme: 三省六部

🌅 朝议准备：
- Session Scope：本次朝议暂未绑定项目，请确认要处理哪个项目/领域
- Storage：GitHub ✓ / Google Drive ✗ / Notion ✓
- Sync：已完成 full pull（3 条 inbox 拉入）
- Platform：Claude Code
- Life OS version：1.6.2a（已是最新）
- Project Status：3 个活跃项目，1 个待检视
- Behavior Profile：user-patterns.md 最近观察到 2 次决策疲劳

🔮 SOUL Health Report
- 核心档案（confidence ≥ 0.7）：追求自主 → ↗、深度思考 ↗、家人优先 →
- 新维度待你填写：「偏好结构化工具」（confidence 0.3，2 条证据）
- 冲突警告：无
- 休眠维度：无

💤 DREAM Auto-Triggers
- 🚨 stale commitment：32 天前你说要写 freelance 预案，无动作
- 💡 新 wiki：谈判策略（昨夜自动写入）

📋 晨报
丞相启奏：3 件事。
  1. 【高优先】law-firm-partner 回邮件了（project-alpha）
  2. stale commitment：freelance 预案
  3. 手机 inbox：3 条待分类

请指示今日议程。
```

这里面的每一块都有解释，展开讲在 [first-session.md](first-session.md)。

---

## 4. 问一个真事

随便说一件你最近在想的事。小事 ROUTER 直接回，大事 ROUTER 会问 2-3 轮澄清再决定是不是 escalate：

```
> 我在想要不要换份工作
```

系统会问清楚你的处境（现在的工作怎样？考虑新工作的原因？时间压力？），然后视情况：
- 如果是认真的决策：进入完整的 Draft → Review → Veto → Execute → Audit 流程，六部并行打分，最后给 Summary Report
- 如果只是发泄或模糊思考：ROUTER 接住情绪，不强行 escalate
- 如果是需要分析但不是决策（「自由职业的税怎么算」）：走 Express 路径，直接派 1-3 个部门给快速回答

---

## 5. 退朝

结束对话前，说：

```
退朝
```

系统会自动走 ARCHIVER 的 4 阶段流程：

1. **归档**：决策、任务、日志 → outbox
2. **知识萃取**：SOUL 和 Wiki 在满足严格条件时自动写入
3. **DREAM**：N1-N2 整理零碎 → N3 巩固知识 → REM 创造性联想 + 10 个触发动作
4. **同步**：git push → Notion 同步（orchestrator 主上下文执行）

退朝完会给你一份 Completion Checklist，每项都有具体值（不接受「TBD」）。

---

## 就到这里

你现在已经跑通了最小闭环：装 → 上朝 → 对话 → 退朝 → 同步。

下一步去哪：

- 想理解上朝之后系统那 18 步到底在做什么 → [first-session.md](first-session.md)
- 想知道第二大脑的目录结构和数据模型 → [second-brain.md](../second-brain.md)
- 想用 SOUL / DREAM / Wiki / 战略地图 → `user-guide/` 里对应的子目录
- 想看「年度规划」「职业决策」这类场景手册 → `guides/`

---

## 常见第一次卡点

**问**：说了「上朝」，系统却在列 skill 或者让我选指令
**答**：说明 Life OS 没正确加载。检查：
- Claude Code：`~/.claude/skills/life_OS/SKILL.md` 存不存在
- Gemini：`.agents/skills/life_OS/` 或 `~/.gemini/skills/life_OS/`
- Codex：`~/.codex/skills/life_OS/`
重新装一次，或检查 installation.md 的 troubleshooting 部分

**问**：ROUTER 直接给我答案了，没走六部
**答**：正常。不是每件事都需要六部。ROUTER 有三档：直接回（闲聊 / 翻译 / 安慰）、Express（非决策分析，派 1-3 部门）、完整朝议（决策类）。你可以说「完整审一下这件事」把它 escalate。

**问**：退朝后 Notion 报 sync 失败
**答**：Notion 是 orchestrator 在主上下文里用 MCP 工具同步的，subagent 看不见这些工具。如果报失败，检查 Notion MCP 连接（~/.claude.json 里的 mcp_servers 配置），或是容忍失败 —— GitHub 和 Google Drive 仍然会写成功。

**问**：我一直忘记说「退朝」直接关 terminal 会怎样
**答**：本次的决策和对话会丢失 —— ARCHIVER 没跑，outbox 没写，SOUL/Wiki 没更新，DREAM 没做。下次 start session 时系统不会知道这次发生过什么。养成说退朝的习惯。
