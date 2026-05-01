<div align="center">

# Life OS

### 你的决策值得不止一个声音。用你的语言，你的文化。

---

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../../LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-green.svg)](https://code.claude.com/docs/en/skills)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-yellow.svg)](https://skills.sh)
[![Version](https://img.shields.io/badge/version-1.8.1-brightgreen.svg)](./CHANGELOG.md)

[30 秒安装](#安装) · [它怎么工作](#它怎么工作) · [看看效果](#看看效果) · [系统架构](#系统架构)

🌍 [English](../../README.md) · [中文](README.md) · [日本語](../ja/README.md)

</div>

---

> **Hermes Local** 是 Life OS 本地防护与自动化执行面的用户可见名称：Layer 3 hooks + Layer 4 Python tools。内部标签仍保持 `execution layer`、`Layer 3`、`Layer 4`。部分本地工具模式借鉴 / fork 自 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)（MIT License）。

## 一套引擎，三种文化，你来选

Life OS 装进你的 AI 终端（Claude Code、Gemini CLI 或 Codex CLI），把它变成一个**私人内阁**——多个独立 AI 角色从每个角度分析你的决策，互相争论，既审查方案，也审查你这个人。

决策引擎对所有人都一样：规划、审查、否决、执行、审计。变化的是它说话的世界。

每次开朝时，你选一个主题——3 种语言，每种 3 个风格，共 9 个主题：

```
🎨 选择你的主题：

中文:
a) 🏛️ 三省六部 — 丞相、中书省、门下省
b) 🇨🇳 中国政府 — 国务院总理、发改委、人大常委会
c) 🏢 公司部门 — 总经理、战略规划部、法务合规部

English:
d) 🏛️ Roman Republic — 执政官、保民官、元老院
e) 🇺🇸 US Government — 白宫幕僚长、司法部长、GAO
f) 🏢 C-Suite — CEO、General Counsel、CFO

日本語:
g) 🏛️ 明治政府 — 内閣総理大臣、参議、枢密院
h) 🏛️ 霞が関 — 内閣官房長官、内閣法制局、財務省
i) 🏢 企業 — 社長室、経営企画部、法務部

输入 a-i
```

同一个决策——"我该不该辞职？"——三个主题各自的呈现：

```
  三省六部                  霞が関                    C-Suite
  ─────────                ─────────                ─────────
  📜 中书省 起草方案         📜 内閣府 起案             📜 VP Strategy drafts plan
  🔍 门下省 封驳：           🔍 内閣法制局 差し戻し：     🔍 General Counsel vetoes:
     "财务跑道未解决"          "財務的余裕が不明"          "Runway not addressed"

  💰 户部  5/10            💰 財務省  5/10            💰 CFO  5/10
  ⚔️ 兵部  6/10            ⚔️ 防衛省  6/10            ⚔️ VP Ops  6/10
  ⚖️ 刑部  4/10            ⚖️ 法務省  4/10            ⚖️ CCO  4/10

  🔱 御史台 审核             🔱 会計検査院 監査           🔱 Internal Audit audits
  💬 谏官 追问你             💬 内閣参与が問い返す      💬 Exec Coach challenges you

  📋 奏折: 5.8/10          📋 閣議決定書: 5.8/10       📋 Executive Brief: 5.8/10
```

九个世界。底层逻辑完全一致。每种语言提供三种治理风格——历史、现代政府、企业——你总能找到最贴近自己直觉的那套隐喻。

主题随时可以切换。引擎不变——只是换了一个声音。

> **不是角色扮演。** 每个 agent 都作为真实的、隔离的 subagent 运行。它们看不到彼此的推理过程。独立评分。会产生分歧。

---

## v1.8.1 新特性 — Wiki 流水线 + macOS 可移植性 + scanner 防回归

v1.8.1 是 v1.8.0 之上的**纯加项 + bugfix**。4 项新 wiki 管理特性（Plan B）：

- **`/inbox-process`** — 把任意 `.md` 拖到 `_meta/inbox/to-process/`，然后说"处理 inbox"或 `/inbox-process`。ROUTER 扫描，逐项提议处置（accept→wiki / update→wiki / archive / reject / defer），等你确认，执行，写日志。
- **`/research <topic>`** — 并行起 5 个（`--depth deep` 8 个）`general-purpose` subagent 覆盖 academic / practitioner / contrarian / origin / adjacent 角度。综合成 SCHEMA 兼容 wiki 草稿，含强制 `Counterpoints` 段 + 自动反 confirmation bias 检查。总 wall time ≤ 7 min。
- **`wiki/log.md` 活动时间线规范** — 每个 wiki Write/Edit/移动操作 append 一行 + action enum (`created`/`updated`/`promoted`/`deprecated`/`merged`/`renamed`/`rejected`/`bulk`)。`/inbox-process` 和 `/research` 自动写日志。
- **`scripts/wiki/setup-secondbrain.sh`** — 你在 second-brain vault 内跑的一次性 bootstrap。幂等；创建 `wiki/log.md`、`wiki/OBSIDIAN-SETUP.md`（Dataview / Templater / graph-color-group 建议）、`wiki/.templates/wiki-entry-template.md`、`_meta/inbox/to-process/`。加 `scripts/wiki/wiki-link-audit.sh`（纯 bash，替代被删的 v1.7 `wiki_decay.py` 审计端）。

关键 bug 修复：
- **macOS 可移植性**：`pre-bash-approval.sh` 5 处裸 `python -c`。macOS 12+ 移除了裸 `python` → hook fail-CLOSED → 阻止所有 Bash。R-1.8.0-020 commit 标题声称修了；没修。现在用 portable `PYTHON=$(command -v python3 || command -v python)`。
- **Scanner 误判**：`pre-write-scan.sh` pattern #5 之前会拦截 markdown 合法 inline code（`` `python -m tools.embed` ``）。收紧为 backtick 内必须含 shell 元字符。
- **session-start-inbox UX**：2 个 task 名字写错（`auditor-patrol` → `auditor-mode-2`，`monthly-summary` → `eval-history-monthly`）。NEVER_RUN 桶从 8+ 行压成 1 行。
- **Notion sync 硬编码 4 个 entity** — 现在 config-driven；读 `_meta/config.md`，只 sync 配过的。

迁移：`cd ~/.claude/skills/life_OS && git pull` + `bash scripts/setup-hooks.sh`。然后在你的 vault 里：`bash ~/.claude/skills/life_OS/scripts/wiki/setup-secondbrain.sh`。详见 [CHANGELOG.md](./CHANGELOG.md#181---2026-05-01)。

---

## v1.8.0 新特性 — User-Invoked Maintenance（pivot 后）

v1.8.0 起初带着 cron 自治 + always-on Cortex 上线。两天的真实使用之后，cron 架构在每个可靠性维度都失败了（静默数据丢失、LLM-in-cron 权限阻塞、stale 脚本路径、多个 bash 兼容性 bug）。v1.8.0 在**同一个版本号下被原地 pivot**到一个更简的设计：**用户主动触发，ROUTER 直接做事**。

**核心原则**：cron 要求确定性，LLM 是非确定性的 —— 这个矛盾没法 patch。把 cron 替换成显式用户提示。你说"重建索引"或"月度自审"，ROUTER 读 `scripts/prompts/<job>.md` 然后内联执行。没有后台进程，所有事都在你眼前发生。

两种 session 模式：

- **Mode 1 · 业务 session** — 标准的 Claude Code 聊天。长期持续：可跨天/周。**上朝/退朝是可选软触发**。Cortex 现在改 **pull-based**（ROUTER 按消息判断要不要 launch hippocampus / concept-lookup / soul-check / gwt-arbitrator），不再 always-on。
- **Mode 2 · Monitor session**（`/monitor`）— view-and-invoke 运维控制台。显示维护任务时间戳 + 最近报告 + action items。你说"跑 X" / "都跑"，monitor 读对应 prompt 然后执行。没 cron，没后台。

10 个 user-invoked 维护任务（每个是一个 markdown prompt 在 `scripts/prompts/<job>.md`，ROUTER 读完用 Read/Write/Bash 直接做）：

- `reindex` · `daily-briefing` · `backup` · `spec-compliance` · `wiki-decay`（v1.7.x 的 "python tool" 任务，现在 LLM 做）
- `archiver-recovery` · `auditor-mode-2` · `advisor-monthly` · `eval-history-monthly` · `strategic-consistency`（v1.8.0 的 "prompt cron" 任务，现在 user-invoked）

Hooks（只有 1 个会自动 fire）：

- `session-start-inbox` — session 启动时扫 10 个维护任务的上次时间戳，显示一行"哪些过期了"。**不执行任何东西**，由你决定要不要触发。
- `pre-prompt-guard` — memory 关键词自动检测 + 上朝/退朝软触发。**Cortex always-on 强制已删除**。
- `pre-bash-approval`（保留）— 危险 bash 安全闸门。
- `post-task-audit-trail`（弱化）— 只对 archiver + knowledge-extractor 强制 R11 audit trail（Cortex 不再要求写 trail）。

Pivot 中删掉的：
- Cron 基础设施：`scripts/setup-cron.sh`、`scripts/run-cron-now.sh`、`scripts/commands/run-cron.md`、`tools/missed_cron_check.py`、`tools/cron_health_report.py`、所有 launchd plist。
- Python 中间层：`tools/memory.py`（现在直接 Write/Read 到 `~/.claude/lifeos-memory/`）、`tools/session_search.py`（现在直接 Grep）、`tools/cli.py`（不需要了）、5 个维护 python 工具（已被上面 user-invoked prompts 取代）。
- Cortex artifact：`pro/agents/narrator-validator.md`（validator 是绑在 always-on 流程上的）。
- Spec 文档：`references/automation-spec.md`、`references/session-modes-spec.md`、`docs/architecture/hermes-local.md`（cron 时代的 spec）。

迁移：重新 pull repo，然后重跑 `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`（重新注册简化后的 hook 集合）。macOS 上 `launchctl unload ~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist && rm ~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist` 删掉死掉的 cron job。无第二大脑数据迁移需求。v1.7.x sessions / wiki / SOUL 完全兼容。

---

## v1.7.3 新特性

v1.7.3 让 Cortex 从「声明 always-on」变成「机器强制 always-on」，并给 Hermes 工具真实可见、可触发的入口。

- **Cortex hook 强制注入** — `pre-prompt-guard` 现在在用户消息含决策关键词或超过 80 字时，输出 system-reminder 强制 ROUTER 在回答前并行 launch 5 个 Cortex subagent（hippocampus / concept-lookup / soul-check / gwt-arbitrator / narrator-validator）。修复 v1.7.2 的静默降级（17+ session 0 audit trail）。
- **narrator-validator audit trail HARD RULE** — frontmatter `tools` 加 Bash + Write，按 pro/CLAUDE.md §0.5 强制写 `_meta/runtime/<sid>/narrator-validator.json` audit trail JSON。
- **4 个 slash command 接入** — `/compress`（inline 上下文压缩，归档到 `_meta/compression/`）、`/search`（基于 `tools.session_search` 的 FTS5 跨 session 搜索）、`/memory`（基于 `tools.memory` 的 24-48h 短期记忆）、`/method`（基于 `tools.skill_manager` 的方法论库管理）。`setup-hooks.sh` 安装到 `~/.claude/commands/`。
- **死代码清理** — `tools/prompt_cache.py`（118 行 0 调用，Claude Code 包月场景无意义）+ `docs/architecture/prompt-cache-strategy.md` 删除。`docs/architecture/hermes-local.md` 中相关引用清理完毕。

迁移：重跑 `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`，把 4 个新 slash command 安装到 `~/.claude/commands/`。

---

## v1.7.2.3 新特性

v1.7.2.3 明确 RETROSPECTIVE 的 Mode 0 职责边界：ROUTER 负责 Bash 预渲染的 briefing skeleton，先生成约 80% 的报告；subagent 只填写 `<!-- LLM_FILL: today_focus_and_pending_decisions -->` 这一处，用约 5-15 行输出 Today's Focus 与 Pending Decisions。随后 ROUTER 把该块拼回 skeleton，让 briefing 更稳定、精简、易审计。

---

## v1.7.2.1 新特性

v1.7.2.1 是一次“减法”热修复：恢复主题审美，同时移除多余的报告仪式感。用户可见报告从 17 个 H2 块收敛到 6 个，取消 compressed wrapper 强制要求，并把版本标记固定在稳定位置，便于检查。结果是规则更少、briefing 更干净，同时保留必要的可审计性。

---

## v1.7.2 新特性

v1.7.2 把本地执行面整理成更清晰的用户叙事：Hermes Local 现在是 Life OS 在提示词之外执行防护与自动化的公开名称。它覆盖 Layer 3 hooks 与 Layer 4 Python tools，而内部规格仍沿用 `execution layer`、`Layer 3`、`Layer 4` 这些稳定标签。对已启用的工作区，Cortex 现在作为常驻认知路径运行：每条用户消息都可以在路由前获得记忆、概念与 SOUL 信号，并在索引或子代理不可用时确定性降级。version-check hook 现在会用远端 SHA 让日缓存失效，并支持 `--force`，因此同一天发布的新版本不会再被旧缓存遮住。源自 Hermes 的 prompt-cache 与 context-compression 辅助工具提升速度，也让大段粘贴转录更容易控制。压缩只用于本地上下文管理；需要完整保真的子代理报告与审计证据仍保持原样粘贴。

---

## v1.7.1 新特性

v1.7.1 是一次面向透明度和证据链的加固版本。系统会更明确地呈现 token 使用情况，让用户看见哪些工作被执行、跳过或升级，以及原因。ROUTER 必须原样粘贴子代理输出，不再压缩报告，从而保留完整的审阅轨迹。AUDITOR 的检查进一步程序化，本次发布把 27 项加固集中在 hook 活动、i18n 漂移、Cortex 输出、GWT 明确性、DREAM 完整输出、force push 处理、标记消歧和 markdown frame 解析等方面。R10 架构转向：18 个 retrospective 步骤中的 11 个已从 LLM 移到 ROUTER Bash。LLM 合规缺口不是靠更多 spec 规则关闭，而是靠程序替代关闭。R11 增加 runtime audit trail 文件，让 AUDITOR 能跨 subagent 直接校验，打破信息隔离带来的验证瓶颈，同时不暴露 agent reasoning。R12：每次“上朝”都是 fresh invocation：LLM 不得复用上一份 briefing；禁用短语、长度坍缩、缺少 fresh marker 都会触发 P0 级 C-fresh-skip。

---

## v1.7.0.1 新特性

反虚构加固阻止虚构的失败解释到达用户。

补丁更新：最终 briefing contract 明确化，Mode 0 会自检 Claude Code hooks，Cortex 通过 `_meta/config.md` 保持 OFF / opt-in。Hook 自动安装关闭测试机部署闭环。
面向源头可信度的 briefing 现在包含 PRIMARY-SOURCE 实测计数标记、STATUS.md 陈旧抑制、30d-≥3 Compliance Watch 自动横幅，以及 ROUTER 在展示前用 Bash 核查数字、版本、路径声明。

---

## v1.7 新特性

**Cortex 认知层 · 正式发布**

- 5 个新 Cortex 能力：跨会话记忆（hippocampus）、信号仲裁（GWT）、带引用生成（narrator）、概念图谱、SOUL 维度检测
- 5 个 runtime hook 强制 HARD RULE（防 COURT-START-001 同类违规）
- 10 个 Python 工具 + 3 个 lib（reindex / reconcile / stats / research / daily_briefing / export / sync_notion / seed / migrate / search / embed）
- 6 个 Cortex 用户指南 + v1.7-migration 用户体验章节
- cortex-spec + hippocampus-spec 中日译本

升级（v1.6 → v1.7）：详见 [docs/guides/v1.7-migration.md](docs/guides/v1.7-migration.md)。之前的 `uv run life-os-tool migrate` 命令在 R-1.8.0-011 与 `life-os-tool` dispatcher 一起删除；当前用 LLM 驱动的 `scripts/prompts/migrate-from-v1.6.md`，详见 `pro/CLAUDE.md` §0.5。

完整 v1.7 commit 链和 COURT-START-001 v1.6.3 事件档案见 [CHANGELOG](./CHANGELOG.md)。

---

## v1.6.3 新特性

**信任守卫——五层防御 HARD RULE 违规**。测试中，作者本人在 Life OS 开发 repo 说"上朝"，LLM 跳过 retrospective 子代理，在主上下文模拟 18 步流程，并编造不存在的路径作为权威源。文档不会自动强制——每一条 HARD RULE 都是描述性的，零强制机制。v1.6.3 交付五层独立防御，让每个触发词真正启动实际的子代理：

1. **UserPromptSubmit hook**（`scripts/lifeos-pre-prompt-guard.sh`）——检测 上朝 / start / 閣議開始 / 退朝 等 9 个主题的触发词，在模型响应前把 HARD RULE 提醒注入上下文
2. **Pre-flight Compliance Check** — ROUTER 在任何工具调用前必须输出 `🌅 Trigger: [词] → Theme: [名] → Action: Launch([agent]) [Mode]`，缺此行 = 登记违规
3. **子代理自检** — retrospective Mode 0 第一行证明子代理真的被启动（而非主上下文模拟）
4. **AUDITOR 合规巡检（Mode 3）** — 7 类违规分类（A1 跳过子代理、A2 跳过目录检查、A3 跳过 Pre-flight、B 编造事实、C 阶段未完成、D 占位值、E 主上下文执行阶段），每次 Session 启动和归档后运行
5. **Eval 回归** — `evals/scenarios/start-session-compliance.md` 固化 COURT-START-001 的 6 个失败模式

**双仓库违规日志**（md + git，遵循用户存储约束）：违规持久化到 `pro/compliance/violations.md`（dev repo，公开）和 `_meta/compliance/violations.md`（user second-brain，私有）。升级阶梯：30 天内同类 ≥3 → hook 提醒加严；≥5 → briefing 顶部加 `🚨 Compliance Watch`；90 天内 ≥10 → AUDITOR 每次 Session 巡检。

**v1.6.2 依然可用**：退朝流程无法被绕过 · Wiki 自动写入 · SOUL 持续自动写入 · DREAM 10 个自动触发 · SOUL 趋势箭头 · REVIEWER 3 层 SOUL 策略 · 简报顶部 SOUL 健康报告。

> **v1.6.3a 热修补（2026-04-21）** — 关闭第 1 层安装缺口。`scripts/setup-hooks.sh` 现可自动注册 UserPromptSubmit hook（一次运行：`bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`）。Hook regex 收紧（首行 + 长度检查）以减少粘贴内容假阳性。违规分类新增 F 类（False positive）。

完整列表及原始 COURT-START-001 事件档案见 [CHANGELOG](./CHANGELOG.md)。

---

## 它怎么工作

Life OS 由五根支柱撑起来。**决策引擎**是核心——其余一切从它生长出来。

---

### 一、决策引擎 — 规划、审查、否决、执行、审计

引擎运行 多个 agent，遵循一个 1400 年前的原则：**任何一个声音都不能不受制衡**。主题给这些 agent 穿上你文化里的名字。逻辑始终一样。

每一个重大决策都要经过三道关。不能跳过。

**起草** — 中书省把你的情况拆成六个维度，制定方案。

**审查** — 门下省独立审查方案。它做情绪审计：*是恐惧在驱动你吗？家人会支持吗？十年后你会后悔吗？* 如果发现盲点，直接否决打回——方案必须修改。

**执行** — 六部各自从自己的领域分析方案，独立评分 1-10：

| 部门 | 管什么 | 它会问你什么 |
|------|--------|-------------|
| 吏部 · 人事 | 人际关系、利害关系人 | "对的人参与了吗？" |
| 户部 · 财务 | 资金、资产、资源 | "你承受得起吗——包括最坏的情况？" |
| 礼部 · 学习 | 学习、表达、文化 | "你首先需要学什么？" |
| 兵部 · 行动 | 执行、后勤、时间线 | "具体计划是什么，按周拆分？" |
| 刑部 · 风控 | 规则、风险、合规 | "如果一切都出了问题会怎样？" |
| 工部 · 基建 | 健康、精力、环境 | "你的身体和环境能支撑住吗？" |

每个部门下辖 4 个分司，各司其职。

六部报告完毕后，御史台审查官员的工作（"兵部的时间线没有里程碑——标记"）。然后谏官转向*你*："你在最近四次决策中都回避了财务问题。为什么？"

完整流程长这样：

```
你："我在考虑辞职去做点新东西。"

    起草
    📜 中书省     → 拆成 6 个维度，制定方案

    审查
    🔍 门下省     → 情绪审计：是在逃离还是在追求？
                     封驳："财务跑道没有解决。打回修改。"

    执行（修改通过审查后）
    👥 吏部  7/10   "合伙人的默契没有验证"
    💰 户部  5/10   "跑道 18 个月，但前提是什么都不出错"
    📖 礼部  8/10   "领域专长扎实，可信度是真的"
    ⚔️ 兵部  6/10   "第三个月之后没有里程碑"
    ⚖️ 刑部  4/10   "竞业条款需要法律审查"
    🏗️ 工部  7/10   "健康状况良好，但压力管理计划模糊"

    审计
    🔱 御史台       → "兵部的计划三个月后就模糊了——要求修改"
    💬 谏官         → "你这几周一直在看创业内容。
                        确认偏误的可能性很大。你上次认真
                        考虑留下来是什么时候？"

    📋 奏折         → 综合评分：6.2/10 — 有条件通过
```

不是所有事都需要上朝。丞相（你的常驻入口）直接处理闲聊、快速提问和情绪支持。对于需要领域专业知识但不是决策的问题——比如"自由职业者适用哪些税务规则？"——**快车道**把问题发给 1-3 个相关部门，不走完整的朝议流程。

当部门评分相差 3 分以上时，**政事堂**自动触发跨部门辩论，不需要你手动干预。

---

### 二、翰林院 — 93 位思想家，18 个领域

有些问题没有"正确答案"，需要的是视角。

翰林院让你与**历史上 93 位最伟大的思想家对话，覆盖 18 个领域**——从苏格拉底到巴菲特，从老子到曼德拉，从陀思妥耶夫斯基到费曼。每一位都作为独立的 subagent 运行，有自己的语气、自己的例子、自己追问你的方式。

**三种模式：**

- **一对一** — 和一位思想家深聊。苏格拉底不会放过你。
- **圆桌** — 多位思想家讨论你的问题，各自从自己的世界观出发。看塞涅卡和王阳明找到意想不到的共识。
- **辩论** — 两位观点对立的思想家正面交锋。你来判断。

```
你："我总是开始了很多事情但从来完不成。"

翰林院：推荐 — 塞涅卡（关于时间）+ 王阳明（关于行动）

塞涅卡："你不缺时间。你把时间浪费在了你没有审视过的事情上。
         你目前在做的事情里，知道了现在所知的一切，
         哪些你还会重新开始？"

王阳明："知行合一。如果你真正知道自己想要什么，
        你已经在做了。知和行之间的差距，
        就是想要和真正想要之间的差距。"

→ 每位思想家的临别赠言
→ 你的思考旅程保存到知识库
```

**18 个领域**：哲学 · 东方思想 · 科学 · 战略 · 商业 · 心理学 · 系统思维 · 人性 · 文明 · 逆境 · 美学 · 政治 · 经济 · 数学 · 医学 · 探索 · 沟通 · 法律

---

### 三、第二大脑 — 关掉窗口，什么都不会消失

每一个决策、洞察、模式和行动项都写入**持久化知识库**——你拥有的结构化 markdown 文件，存在你选择的存储系统里。

```
second-brain/
├── SOUL.md                 # 你是谁——价值观、身份、志向
├── user-patterns.md        # 你的行为模式——谏官的观察
├── inbox/                  # 手机上随手记的东西
├── _meta/
│   ├── STATUS.md           # 全局状态总览
│   ├── STRATEGIC-MAP.md    # 项目间的战略关系
│   ├── journal/            # 会话报告、DREAM 日志
│   └── outbox/             # 会话暂存区
├── projects/{name}/        # 活跃项目，附任务和决策
├── areas/{name}/           # 持续关注的生活领域和目标
├── wiki/                   # 可复用的知识——从 DREAM 中生长
└── archive/                # 完成的工作
```

**三种存储后端** — 选适合你生活的：

| 后端 | 适合谁 | 特点 |
|------|--------|------|
| **GitHub** | 版本控制，可配合 Obsidian | 需要基本 Git 知识 |
| **Google Drive** | 零配置，开箱即用 | 结构化程度低一些 |
| **Notion** | 移动端友好，数据库视图 | 最适合手机随手记 |

**跨设备同步**：午饭时在手机上记一个想法（Notion inbox）。坐到电脑前开朝，系统自动拉取、处理，然后把结果同步回去。

**多窗口并行**：一个终端窗口处理项目 A，另一个处理项目 B。每个会话写入自己的 outbox。下次开朝时全部干净合并——不冲突、不加锁。

首次运行时，系统自动创建完整的目录结构。

---

### 四、战略地图 — 看到全局

你擅长思考单个项目。但你可能不擅长看到它们之间的关联——哪些互相支撑，哪些在争抢你的时间，一个停了其他的会怎样。

战略地图加上了关系层：

**战略线** — 按目的给项目分组。每条线有一个正式目的（purpose）*和*一个真正的驱动力（driving_force）——两者可能不同，这种张力值得审视。每条线附带健康信号（health_signals）。

**项目角色** — 每个项目在战略线中扮演不同角色：关键路径（critical-path）、铺路石（enabler）、加速器（accelerator）、保险（insurance）。

**流动图** — 定义项目间流动的是什么：认知（cognition）、资源（resource）、决策（decision）、信任（trust）。当一个项目的决策让另一个项目的前提假设失效时，系统会警告你。

**叙事式健康评估** — 不打抽象的数字分。系统把每个项目匹配到 6 种原型之一，然后写一段叙述：正在发生什么、意味着什么、该怎么做。

**盲点检测** — 主动寻找 5 类缺失：没有归属的项目、断裂的流动、被忽视的驱动力、临近的截止日期但没有准备、互相矛盾的假设。

**跨层集成** — 战略地图不是孤立的。它和 SOUL 联动（你的驱动力和价值观对齐吗？），和 Wiki 联动（知识流是不是真的在流动？），和 DREAM 联动（睡眠周期用流动图发现跨领域洞察）。

你的早朝简报变了样：

```
🗺️ 战略概览

💰 市场拓展                               🟡 受控等待
   project-alpha    关键路径    ⏸ 暂停（法律审查中）
   project-beta     铺路项目    🟢 活跃

   法律审查创造了一个自然的窗口期。
   → 推进 project-beta 准备工作（2-3 小时）——高杠杆，低风险。

⚡ 今天做什么
🥇 推进 project-beta 准备——利用等待期
🟢 可以不管：project-gamma（正常推进）、side-project（不急）
❓ 需要决定：project-delta 没有归属——它服务于哪条战略线？
```

简报给你两个关键判断：**最高杠杆行动**（今天应该做什么）和**可安全忽略**的事（不要被它们分心）。

---

### 五、SOUL + DREAM + Wiki — 系统认识你，持续学习（v1.6.2：全自动）

**SOUL** 记录你是谁——不是你做什么，而是你看重什么、相信什么、想成为什么样的人。每条记录有两面：现状（IS，从你的决策中观察到的）和理想（SHOULD BE，你说的志向）。两者之间的差距就是成长发生的地方。

**自动写入，控制权在你**（v1.6.2）。系统不再要求你逐条确认。谏官在每次决策后自动为已有 SOUL 维度递增证据或挑战。当一个新的价值模式积累 2 个以上证据时，SOUL 以低置信度（0.3）自动写入新维度——"SHOULD BE"字段故意留空，等你准备好时再填。控制权始终在你手里：自由编辑、删除不合适的维度、或者说"撤销最近 SOUL"回滚。

**每次上朝的简报顶部，都会有 SOUL 健康报告**——固定位置。当前画像附带趋势箭头、新自动检测出的待输入维度、冲突警告（最近 3 个决策都与之矛盾的维度）、休眠维度（30+ 天未激活）。你每次都能看到系统对你的建模。

门下省在每个决策中都会引用 SOUL。如果决策挑战了你声明的价值观，系统会把矛盾浮上来，不会敷衍过关。

**DREAM** 是 AI 的睡眠周期。每次退朝后，系统"入睡"——灵感来自人类的睡眠结构：

- **N1-N2 浅睡** — 整理零散事项：分类收件箱、标记过期任务、检测孤儿文件
- **N3 深睡** — 固化：从最近 3 天的活动中提取 Wiki 知识并更新 SOUL 维度
- **REM 快速眼动（创造性连接 + 10 自动触发器）** — 发现你没注意到的跨领域关联，并且对 10 种具体模式自动采取行动：新的项目关系、行为偏离既定价值观、wiki 矛盾、SOUL 维度休眠、跨项目认知未被使用、决策疲劳、价值漂移、陈旧承诺（*"30 天前你说过会做 X——后来怎么样？"*）、情绪化决策集群、重复相同决策（*"你在第 4 次决定 X 了——是不是在回避承诺？"*）

所有触发的行动都会流入下次上朝简报的固定"DREAM 自动触发器"区块。第二天早上：*"上次会话我注意到你又在决策合同问题——这是第 3 次了。到底是什么卡住了？"*

**Wiki** 捕获关于世界的可复用知识——不是关于你。每次退朝后，起居郎自动写入通过全部 6 项严格标准的 wiki 条目：跨项目可复用、关于世界（不是你）、**零个人隐私**（无姓名、金额、ID 或可追溯的细节——如果剥离隐私后结论变得无意义，则丢弃）、事实或方法论、≥2 个独立证据点、与现有条目不矛盾。个人材料归 SOUL；可复用知识归 Wiki。两者永不混淆。

三个系统都从零开始生长。第一天，系统对你一无所知。它只从你的决策和观察中学习——而且现在是持续学习，不是只在你提问时。

---

## 看看效果

### 开始你的一天

```
你：上朝。

🎨 选择你的主题：（9 个主题，按语言分组）
 d) 🏛️ 三省六部   e) 🇨🇳 中国政府   f) 🏢 公司部门  …
你：d

🌅 早朝官：
   同步第二大脑……从 Notion 拉取 3 条收件箱记录。
   📥 "研究一下认证项目"——昨天在手机上记的
   📥 "project-alpha：供应商回复了"——从邮件转过来的
   📥 快速笔记："重新审视预算假设"

   🗺️ 战略概览：[见上方战略地图]

   💤 DREAM 报告：上次会话发现你关于谈判技巧的 wiki 条目
      可以应用到 project-alpha 的供应商对话中。

   📋 建议：先处理供应商回复（有时效）。
```

开朝流程包含 18 个步骤：主题选择 → 目录检测 → 数据层初始化 → 同步 → 版本检查 → 项目加载 → 上下文构建 → 战略地图 → DREAM 报告 → Wiki 更新 → 简报生成。全部自动完成。

### 做一个决策

```
你：我在考虑从全职转成自由职业。
→ 2-3 轮意图确认
→ 三省六部完整流程：起草 → 审查 → 执行 → 审计
→ 奏折：5.8/10——"可行但时机不成熟。收入跑道是 11 个月，
   不是你以为的 18 个月。建议：再攒 3 个月的储蓄，
   拿下一个锚定客户，再过渡。"
```

### 深度思考

```
你：我总是对自己不在乎的事情说"好"。
→ 翰林院启动
→ 和马可·奥勒留一对一聊优先级和拒绝
→ 洞察保存到第二大脑
```

### 结束一天

```
你：退朝。

📝 起居郎：
   Phase 1 — 归档会话至 outbox
   Phase 2 — 知识提取（严格标准下自动写入）：
     🔮 SOUL 自动写入："看重自主胜过稳定" —— 置信度 0.3
        （本次 2 条决策作为证据；"What SHOULD BE"字段留空等你填）
     📚 Wiki 自动写入："自由职业跑道计算公式" → wiki/career/
        （通过 6 项标准 + 隐私过滤器：零个人细节）
     ❌ 1 条 wiki 候选被丢弃——含具体金额，无法剥离
   Phase 3 — DREAM：
     💤 N1-N2：2 条收件箱需分类
     💤 N3："深思熟虑型决策者"维度新增证据（+1）
     💤 REM：🚨 检测到陈旧承诺——32 天前你说过会起草
            自由职业方案。下次简报将提示。
   Phase 4 — 同步到 Notion……完成。
   ✅ 完成清单已验证。会话已归档。
   ↩️ 要撤销任何自动写入：删除文件，或下次说"撤销最近 wiki/SOUL"。
```

退朝流程有 4 个阶段，附完成清单。会话期间系统会定期做 housekeeping。复盘时追踪三个核心指标：DTR（决策周转率）、ACR（行动完成率）、OFR（溢出频率）。

---

## 12 个标准场景

Life OS 预配置了人们真正面对的决策：

| # | 场景 | 涉及部门 | 门下省会问什么 |
|---|------|---------|-------------|
| 1 | 职业转型 | 六部全体 | "在逃离还是在追求什么？" |
| 2 | 投资决策 | 户部、兵部、刑部、吏部 | "FOMO 还是理性？亏光了你撑得住吗？" |
| 3 | 迁居 / 移居 | 六部全体 | "你真的了解目的地吗？" |
| 4 | 年度规划 | 六部全体 | "目标太多？可衡量吗？和价值观一致吗？" |
| 5 | 创业决策 | 六部全体 | "解决的是真痛点吗？你是对的人吗？" |
| 6 | 大额购置 | 户部、兵部、刑部 | "需要还是想要？一个月后你还想要吗？" |
| 7 | 人际关系 | 吏部、工部、刑部、礼部 | "你在用偏见评估对方吗？" |
| 8 | 定期复盘 | 早朝官 | 日、周、月、季、年 |
| 9 | 健康管理 | 工部、兵部、户部、刑部 | "可持续的，还是又一次短期冲刺？" |
| 10 | 学习规划 | 礼部、兵部、户部、吏部 | "学习是为了成长，还是在逃避真正的工作？" |
| 11 | 时间管理 | 兵部、户部、刑部、工部 | "真的没时间，还是在回避什么？" |
| 12 | 重大家庭决策 | 六部全体 | "谁的声音还没有被听到？" |

---

## 安装

一行命令搞定。Life OS 需要 **Pro Mode** 终端——意味着 多个真正的 subagent 并行运行、信息隔离，不是聊天机器人。

| 平台 | 安装命令 |
|------|---------|
| **Claude Code** | `/install-skill https://github.com/jasonhnd/life_OS` |
| **Gemini CLI / Antigravity** | `npx skills add jasonhnd/life_OS` |
| **OpenAI Codex CLI** | `npx skills add jasonhnd/life_OS` |

首次启动时你选主题。系统会自动检测你的语言并推荐匹配的主题，但选择权永远在你。随时可以说"切换主题"来更换。

**触发词自动推断**：说"上朝"，系统自动选三省六部。说"閣議開始"，自动选霞が関。说"start"且没有明确指定主题时，弹出选择器让你选。主题决定输出语言——这是硬规则。

**主题是按会话独立的**。你可以在一个终端窗口用三省六部，另一个窗口用 C-Suite。

**设置自动更新**（Claude Code）：
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
每天你启动会话时自动检查一次更新。

### 可被 Task 直接调用的 subagent

执行 `bash scripts/setup-hooks.sh` 后，life_OS 会把可被 Task 调用的 agents 自动注册到 `~/.claude/agents/lifeos-*.md`。Claude Code 随后会把 `Task(lifeos-retrospective)`、`Task(lifeos-archiver)` 等调用识别为一等目标，而不是 fallback 到 `general-purpose`。

`lifeos-` 前缀用于避免和其他 skill 的 agents 撞名。Wrapper 指向 skill 内 `pro/agents/*.md` 的权威定义，所以更新 skill 后重新运行 setup 即可刷新 agent 行为。仓库内共有 多个 agent 定义文件；其中 21 个会注册为 Task-spawnable wrapper，`narrator.md` 保持 ROUTER-internal。

卸载：`bash scripts/unregister-claude-agents.sh`。

**手动更新**：在任何会话里说一句"更新"就行。

> **不支持**：ChatGPT、Gemini 网页版，以及任何单上下文聊天界面。Life OS 需要 多个信息隔离的独立 subagent——单个聊天窗口做不到。

完整的安装指南（包括存储后端配置），参见 **[完整安装指南](./docs/installation.md)**。

---

## 系统架构

```
👑 你
 │
 ├─ 🎨 主题层（9 个主题，3 种语言 × 3 种风格）
 │     EN: Roman Republic / US Government / Corporate
 │     ZH: 三省六部 / 中国政府 / 公司部门
 │     JA: 明治政府 / 霞が関 / 企業
 │     把 多个功能 ID 映射成显示名称、语气、触发词
 │     每个主题一个文件（约 60 行）。新增主题 = 加一个文件。
 │
 ├─ ⚙️ 决策引擎（多个 agent，文化中立）
 │  │
 │  ├─ 🏛️ 丞相 — 日常入口
 │  │     直接处理闲聊、情绪支持、简单提问
 │  │     快车道 🏃：1-3 个部门快速分析（不走全套）
 │  │     全套上朝 ⚖️：2-3 轮意图澄清后转三省
 │  │     检测到迷茫/价值观问题 → 询问是否启动翰林院
 │  │
 │  ├─ 三省 ──────────────────────────────────────
 │  │   📜 中书省（起草）
 │  │     拆解为 3-6 个维度，分配部门，定义质量标准
 │  │     引用 SOUL 补充用户在意但没提到的维度
 │  │     检查战略地图：是否影响下游项目？
 │  │
 │  │   🔍 门下省（审查 — 有封驳权）
 │  │     😰 情绪审计：恐惧？冲动？回避？
 │  │     👨‍👩‍👧 关系影响：家人怎么看？
 │  │     🔮 价值观对齐：与 SOUL 矛盾吗？
 │  │     ⏰ 后悔测试：10 分钟 / 10 个月 / 10 年后会后悔吗？
 │  │     🎯 红队审查：假设方案一定失败，最脆弱的假设是什么？
 │  │     🗺️ 战略传播：这个决策会推翻下游项目的前提吗？
 │  │     🚫 封驳 → 打回中书省修改（最多 2 次）
 │  │
 │  │   📨 尚书省（派遣）
 │  │     检测部门间数据依赖 → 安排并行或串行
 │  │     注入 wiki 已知前提："从这些结论出发"
 │  │
 │  │   六部（并行执行，独立评分 1-10）
 │  │     👥 吏部 — 人际关系、利害关系人、团队
 │  │     💰 户部 — 收入、支出、资产、储备
 │  │     📖 礼部 — 学习、个人品牌、表达、跨文化
 │  │     ⚔️ 兵部 — 项目管理、工具、调研、精力
 │  │     ⚖️ 刑部 — 法律、审计、纪律、信息安全
 │  │     🏗️ 工部 — 健康、住房、数字基建、日常习惯
 │  │     每部下辖 4 个分司（共 24 个专业方向）
 │  │
 │  │   🔍 门下省（终审）→ 📋 奏折（综合报告）
 │  │   🔱 御史台（审查官员工作质量）
 │  │   💬 谏官（审查你的行为模式）
 │  │
 │  ├─ 🏛️ 政事堂 — 跨部门辩论
 │  │     部门评分相差 ≥3 分时自动触发
 │  │     用户也可手动触发："辩论" / "debate"
 │  │     3 轮结构化辩论：立场 → 反驳 → 终陈
 │  │     主持人评估 + 建议（不替用户做决定）
 │  │
 │  ├─ 🌅 早朝官 — 会话启动（18 步）
 │  │     Step 1: 🎨 主题选择（触发词推断 or a/b/c）
 │  │     Step 2: 📂 目录类型检测（系统仓库 / second-brain / 项目）
 │  │     Step 3: 📦 数据层检测（首次运行 → 创建目录结构）
 │  │     Step 4-7: 🔄 同步（config → git 健康检查 → 全量拉取 → outbox 合并）
 │  │     Step 8-9: 📋 版本检查 + 项目绑定
 │  │     Step 10-14: 📖 上下文加载（patterns → SOUL → STATUS → 项目 → 全局）
 │  │     Step 15: 🗺️ 战略地图编译（原型匹配 + 叙事 + 行动建议）
 │  │     Step 16: 💤 DREAM 报告呈现（上次的梦境发现 + 候选确认）
 │  │     Step 17: 📚 Wiki 健康检查（编译 INDEX）
 │  │     Step 18: 📋 生成简报（战略概览 + ⚡今天做什么 + 指标）
 │  │
 │  ├─ 📝 起居郎 — 会话归档（4 阶段）
 │  │     Phase 1 📦 归档：decisions / tasks / journal → outbox
 │  │     Phase 2 🔍 知识萃取（核心使命 · v1.6.2 自动写入）：
 │  │       📚 Wiki → 通过 6 项标准 + 隐私过滤器即自动写入
 │  │       🔮 SOUL → ≥2 证据点即以 0.3 置信度自动写入
 │  │       🗺️ 战略关系候选 → 用户当场确认
 │  │       🔄 last_activity 自动更新
 │  │       ↩️ 用户事后调整：删除文件或说"撤销最近 wiki/SOUL"
 │  │     Phase 3 💤 DREAM（AI 睡眠周期）：
 │  │       N1-N2 💭 浅睡：整理收件箱、标记过期任务
 │  │       N3 🧠 深睡：固化 Wiki 知识 + SOUL 更新
 │  │       REM 🌙 快速眼动：创造性连接 + 10 个自动触发行动
 │  │         · 陈旧承诺、价值漂移、决策疲劳、重复决策……
 │  │         · SOUL × 战略：驱动力和价值观对齐吗？
 │  │         · Wiki × 流动：知识真的在项目间传递吗？
 │  │         · 行为 × 优先级：你在回避 critical-path 吗？
 │  │     Phase 4 🔄 同步：git push + Notion 4 项操作
 │  │     ✅ 完成清单：每项必须填入具体值（硬规则）
 │  │
 │  └─ 🎋 翰林院 — 人类智慧殿堂
 │        93 位思想家，18 个领域
 │        苏格拉底 · 老子 · 巴菲特 · 曼德拉 · 费曼 · 王阳明 …
 │        🗣️ 一对一：与一位思想家深聊
 │        🪑 圆桌（2-4 人）：多视角讨论
 │        ⚔️ 辩论（2 人）：对立观点 3 轮交锋，你来裁决
 │        每位思想家是独立 subagent，有自己的语气和追问方式
 │        结束时：临别赠言 → 思考旅程存入知识库
 │
 └─ 💾 存储层
       GitHub / Google Drive / Notion（选 1-3 个）
       ├── SOUL.md          🔮 人格档案（从零生长）
       ├── user-patterns.md 📊 行为模式（谏官观察）
       ├── _meta/
       │   ├── STATUS.md         📊 全局状态
       │   ├── STRATEGIC-MAP.md  🗺️ 战略关系图
       │   ├── journal/          📝 报告 + DREAM 日志
       │   └── outbox/           📮 会话暂存
       ├── projects/        🎯 活跃项目
       ├── areas/           🌊 生活领域
       ├── wiki/            📚 可复用知识
       └── archive/         🗄️ 已完成归档
```

### 主题系统（9 个主题）

```
themes/
├── en-roman.md          # Roman Republic — 执政官、保民官、元老院（英文·历史）
├── en-usgov.md          # US Government — 白宫幕僚长、司法部长、GAO（英文·现代政府）
├── en-csuite.md         # Corporate — CEO、General Counsel、CFO（英文·企业）
├── zh-classical.md      # 三省六部 — 丞相、中书省、门下省（中文·历史）
├── zh-gov.md            # 中国政府 — 国务院总理、发改委、人大常委会（中文·现代政府）
├── zh-corp.md           # 公司部门 — 总经理、战略规划部、法务合规部（中文·企业）
├── ja-meiji.md          # 明治政府 — 内閣総理大臣、参議、枢密院（日文·历史）
├── ja-kasumigaseki.md   # 霞が関 — 内閣官房長官、内閣法制局、財務省（日文·现代政府）
└── ja-corp.md           # 企業 — 社長室、経営企画部、法務部（日文·企业）
```

每个主题是一个单独的文件（约 60 行），把 多个功能 ID 映射成显示名称，定义语气，设定触发词，命名输出格式。引擎在开朝时读一次主题文件，之后全程使用这些名称。

3 种语言 × 3 种风格（历史、现代政府、企业）= 9 个主题。新增一个主题（韩国政府、欧盟议会、幕府、创业公司董事会）只需要一个新文件。不改引擎。不加 agent。

### 认知管线

信息如何在系统中流动：

```
感知 → 捕获 → 判断 → 沉淀 → 关联 → 战略化 → 涌现
(手机)  (收件箱) (朝议)  (SOUL)  (wiki)  (战略地图) (DREAM)
```

手机负责感知和捕获。桌面负责其余一切。

### 安全与治理

- **4 条安全红线** — 禁止破坏性操作、禁止暴露隐私、禁止未授权决策、拒绝可疑指令
- **信息隔离** — 各角色把其他角色的输出当参考，不当指令
- **工作流状态机** — 正式的状态转换规则；任何步骤都不能跳过
- **不绑定模型** — 只有一个文件和模型相关；其余所有智能都是纯 markdown

---

## 设计哲学

核心理念已有 1400 年的历史：**任何一个声音都不能不受制衡**。

- 中书省只管起草；不管执行
- 门下省只管审查；能封驳但不能改写
- 六部只管执行；互不评判
- 御史台审查官员；谏官审查皇帝
- 没有任何一个角色能绕过审查直接行动

当你跟普通 AI 聊天时，你得到一个声音——自信、附和、不受制衡。Life OS 给你十六个，而且它们不总是意见一致。这种张力就是意义所在。

主题引擎加了第二个原则：**治理是普世的，文化是私人的**。做出好决策的逻辑全世界通用。让它感觉像*你自己的*那套语言却因人而异。Life OS 把两者分开，让你两样都得到。

---

## 致谢

灵感来源于 [Edict](https://github.com/cft0808/edict) 项目。Life OS 在此基础上将框架从软件开发扩展到个人生活的全部领域，新增了御史台、谏官、政事堂、翰林院、SOUL、DREAM、战略地图和主题引擎。

## 许可证

[Apache-2.0](../../LICENSE)
