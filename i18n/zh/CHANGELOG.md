# 更新日志

## 版本规则

本项目遵循 **Strict SemVer**：MAJOR（破坏性变更）· MINOR（新功能）· PATCH（修复与维护）。同一天的变更合并为单次发布，每次发布打 git tag。

---

## [1.7.0-alpha.2] - 2026-04-21 · v1.7.0-alpha 后续跟进打包

> v1.7.0-alpha tag 之后 13 个 commit，关闭 alpha CHANGELOG 的 TBD + 加工具/测试基础设施。将合入 v1.7.0 稳定版。

### 🔧 新工具

- `tools/cli.py` — 统一子命令派发；`pyproject.toml` 启用 `life-os-tool` 控制台脚本
- `tools/backup.py` — 快照轮转（30d 归档、90d 删除）+ violations 日志按季度归档
- `scripts/lifeos-compliance-check.sh` — `check_adjourn()` + `check_cortex()` 实现（关闭 alpha 占位）
- `tools/lib/cortex/__init__.py` — 22 个辅助符号包级导出

### 📋 新 eval 场景

- `evals/scenarios/adjourn-compliance.md` — Class C/D/E + A3 检测
- `evals/scenarios/cortex-retrieval.md` — CX1-CX7 检测 + 降级路径

### ✅ 测试套件扩展

- `tests/test_backup.py` — 19 测试
- `tests/test_cli.py` — 8 测试
- `tests/test_compliance_check.py` — 11 subprocess-based 测试
- `tests/test_integration.py` — 7 端到端集成测试

**总测试数：122，全部 0.68s 通过。**

### 🚀 CI

- `.github/workflows/test.yml` — pytest 矩阵 + bash 语法 + smoke 测试

### 📚 架构文档

- `references/cortex-architecture.md` — 端到端数据流 + 信息隔离矩阵 + 失败级联 + 成本概况 + 合规映射

### 🔌 接线打磨

- `pro/CLAUDE.md` Information Isolation 表扩展全 6 个 v1.7 子代理
- `pro/agents/archiver.md` 加 "Phase 2 Mid-Step — SOUL Snapshot"

### 🐛 Bug 修复

- `tools/cli.py` `_print_usage(stream=sys.stdout)` 默认值求值时机 bug
- `scripts/lifeos-compliance-check.sh` `set -e` + `grep -c` 静默退出 bug
- 正则 `\s` (GNU only) → POSIX `[[:space:]]` 可移植性

---

## [1.7.0-alpha] - 2026-04-21 · Cortex 路由前认知层

> Life OS 历史上首次 Layer 2 架构升级。把跨会话记忆、概念图、身份信号作为每次决策工作流的输入。今日 19 个 commit 将 v1.7 从 spec 草稿推到功能完整。

### 🧠 路由前认知层（编排 Step 0.5）

当 `_meta/config.md` 设 `cortex_enabled: true` 时，所有非 Start-Session 的用户消息在 ROUTER 分诊**之前**经过 4 个并行子代理：

```
user message
    ↓
Step 0.5（路由前认知层）
    ├─ hippocampus       → 3 波会话检索（5-7 个 sessions）
    ├─ concept-lookup    → 概念图匹配（5-10 个 concepts）
    └─ soul-check        → SOUL 维度信号（top 5）
         ↓
    gwt-arbitrator        → 用 salience 公式选 top-5 信号
         ↓
[COGNITIVE CONTEXT] 块前置到 user message
    ↓
Step 1（ROUTER 用注释化输入分诊）
```

REVIEWER 终审后，可选的 `narrator` 用 `[source:signal_id]` 引用包装 Summary Report 实质性主张。`narrator-validator`（Sonnet 层）审计引用纪律。

### 📋 6 个新子代理（~900 行 markdown 契约）

| 代理 | 文件 | spec |
|------|------|------|
| hippocampus | `pro/agents/hippocampus.md` | `references/hippocampus-spec.md` |
| concept-lookup | `pro/agents/concept-lookup.md` | `references/concept-spec.md` |
| soul-check | `pro/agents/soul-check.md` | 派生自 soul-spec + gwt-spec §6 |
| gwt-arbitrator | `pro/agents/gwt-arbitrator.md` | `references/gwt-spec.md` |
| narrator | `pro/agents/narrator.md` | `references/narrator-spec.md` |
| narrator-validator | `pro/agents/narrator-validator.md` | narrator-spec validator 部分 |

6 个代理全部强制信息隔离：拒绝同层 Pre-Router 代理的输出。全部只读——只在 archiver Phase 2 发生写入。

### 🐍 Python 工具（~1500 行 · 纯 stdlib + pyyaml）

| 模块 | 职责 |
|------|------|
| `tools/lib/second_brain.py` | 11 种 second-brain 类型 dataclass + frontmatter parser/dumper + 路径解析 |
| `tools/lib/cortex/session_index.py` | SessionSummary IO + INDEX.md 编译（幂等）|
| `tools/lib/cortex/concept.py` | Concept IO + INDEX/SYNAPSES 编译 + Hebbian 更新 |
| `tools/lib/cortex/snapshot.py` | SoulSnapshot IO + 归档策略（30d/90d）|
| `tools/stats.py` | 合规违规升级阶梯执行 |

### 🔧 4 个 CLI 工具

```bash
uv run tools/rebuild_session_index.py [--root PATH] [--dry-run]
uv run tools/rebuild_concept_index.py [--root PATH] [--dry-run] [--no-synapses]
uv run tools/stats.py [--violations PATH] [--json]
bash scripts/setup-hooks.sh   # 自动注册 SessionStart + UserPromptSubmit hooks
```

### ✅ 77 个 pytest 测试 — 全部通过 0.23 秒

| 文件 | 测试数 |
|------|------|
| `tests/test_second_brain.py` | 15（frontmatter / dataclass / 路径）|
| `tests/test_session_index.py` | 16（truncate / write / compile / rebuild / 幂等）|
| `tests/test_concept_and_snapshot.py` | 18（concept IO / INDEX / SYNAPSES / Hebbian / 快照策略）|
| `tests/test_stats.py` | 18（parse / 升级 / 阈值 / 路径解析）|

```bash
python3 -m pytest tests/ -v        # 77 passed in 0.23s
```

### 🚦 默认 OFF（按需启用）

Cortex 在 v1.7.0-alpha 默认禁用。用户启用：

```bash
echo "cortex_enabled: true" >> _meta/config.md
```

建议在 second-brain 累积 ≥30 个 sessions 后启用。成本：~$0.05-0.25/turn（Opus tokens 跨 Pre-Router 子代理）。

### 📊 Cortex 合规分类（已加入 AUDITOR Mode 3）

| 代码 | 名称 | 严重度 |
|------|------|------|
| CX1 | Skip Pre-Router subagents | P1 |
| CX2 | Skip GWT arbitrator | P1 |
| CX3 | Missing [COGNITIVE CONTEXT] delimiters | P1 |
| CX4 | Hippocampus session cap exceeded | P1 |
| CX5 | GWT signal cap exceeded | P1 |
| CX6 | Cortex isolation breach | P0 |
| CX7 | Cortex write breach | P0 |

`cortex_enabled: false` 时跳过所有 CX 检测。

### 🚧 已知限制 / 待办

- **生产验证待办** — alpha 通过 pytest + 规格合规性测试，但未在真实 user second-brain 大规模实战
- **`concept-lookup` 不做边遍历** — 仅 Wave 1；Wave 2/3 是 hippocampus 的领域
- **Narrator validator** Phase 2 用自检环；独立 validator 子代理待 Phase 2.5
- **`tools/backup.py`** 快照归档轮转：延后到 v1.7.0 稳定版
- **adjourn-compliance eval 场景** 仍为占位

### 迁移

现有用户（v1.6.3b → v1.7.0-alpha）：
1. 重装 skill：`/install-skill https://github.com/jasonhnd/life_OS`
2. 重跑 hooks 安装：`bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`
3.（可选）安装 Python 工具：`cd ~/.claude/skills/life_OS && uv sync`
4.（可选）启用 Cortex：`echo "cortex_enabled: true" >> {你的 second-brain}/_meta/config.md`

默认 OFF 意味着现有用户除非主动启用否则零行为变化。v1.6.3 五层合规防御保持激活不变。

---

## [1.6.3b] - 2026-04-21 · AUDITOR Mode 3 自动触发已接线

> v1.6.3 把 Mode 3（Compliance Patrol）规格交付到 `pro/agents/auditor.md`，但**没人实际调用它**。在用户 second-brain 的首次生产运行确认了这个缺口：retrospective Mode 0 完成、简报显示，但没有 AUDITOR Compliance Patrol 报告。五层防御的第 4 层处于失活状态。

### 🔧 修复

`pro/CLAUDE.md` Orchestration Code of Conduct 新增规则 #7：

> **AUDITOR Compliance Patrol 自动触发** — 每次 `retrospective` Mode 0（Start Session）完成或 `archiver` 返回后，orchestrator 必须启动 `auditor` 的 Mode 3（Compliance Patrol）。不可跳过。HARD RULE。

3 个配套文档更新使契约显式：

- `pro/agents/retrospective.md` — 加 "Auto-Follow: AUDITOR Compliance Patrol" 段，注明 orchestrator 在 Mode 0 返回后链接 Mode 3。子代理本身不启动 AUDITOR。
- `pro/agents/auditor.md` — Mode 3 "When to run" 段加明确触发契约：orchestrator 启动，非自启动，交叉引用 `pro/CLAUDE.md` 规则 #7。
- `SKILL.md` — 版本 1.6.3a → 1.6.3b。

### 📊 五层防御状态（v1.6.3b 后）

| 层 | 状态 |
|-------|--------|
| L1 · UserPromptSubmit hook | ✅ v1.6.3 交付 · setup-hooks.sh 自动安装（v1.6.3a）|
| L2 · Pre-flight Compliance Check | ✅ 已交付 + 2026-04-21 生产验证 |
| L3 · Subagent Self-Check | ✅ 已交付 + 2026-04-21 生产验证 |
| L4 · AUDITOR Compliance Patrol（Mode 3）| ✅ 规格已交付（v1.6.3）· **触发已接线（v1.6.3b）** |
| L5 · Eval 回归 | ✅ 场景已交付（v1.6.3）· auto-runner 扩展延后到 v1.7 |

### 涉及文件

- `SKILL.md`（版本 1.6.3a → 1.6.3b）
- `pro/CLAUDE.md`（+ Orchestration 规则 #7）
- `pro/agents/retrospective.md`（+ Auto-Follow 段）
- `pro/agents/auditor.md`（Mode 3 "When to run" 触发契约明确化）
- `README.md` + 三语（徽章）
- `CHANGELOG.md` + 三语

### 迁移

用户无需操作。现有 v1.6.3a 安装会在下次会话自动启用规则 #7。今后每次 Start Session 和 Adjourn 结束都会出 AUDITOR Compliance Patrol 报告。无违规时的输出格式：

```
🔱 [theme: auditor] · Compliance Patrol (v1.6.3)
✅ All 6 Start Session compliance checks passed
No violations logged. Session adheres to v1.6.3 HARD RULES.
```

---

## [1.6.3a] - 2026-04-21 · v1.6.3 热修补 · 第 1 层安装缺口 + Hook 假阳性守卫

> v1.6.3 在用户 second-brain 的首次生产运行（同日）验证了第 2-5 层防御端到端 work。同时暴露 2 个真实 gap：
> 1. **第 1 层（UserPromptSubmit hook）未自动注册** — `/install-skill` 只复制文件，不改 `~/.claude/settings.json`。默认安装下 L1 直接没了。
> 2. **Hook regex 误报粘贴内容** — 粘贴的转录里含触发词时会错误触发 reminder。

### 🔧 修复 1 — 第 1 层安装自动化

`scripts/setup-hooks.sh` 重构：
- 单次运行同时安装 SessionStart hook（版本检查）和 UserPromptSubmit hook（第 1 层防御）
- 加入 `register_hook()` 辅助函数，DRY 幂等注册跨事件类型
- 幂等：可安全反复运行；已注册的 hook 跳过
- 向后兼容：现有 v1.6.3 安装不受影响；重跑会干净地补上 L1

用户在 install/upgrade 后跑一次：
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```

### 🔧 修复 2 — Hook 假阳性降低

`scripts/lifeos-pre-prompt-guard.sh` 在 regex 匹配前加两道前置检查：
- **长度检查**：prompt 整体 ≤ 500 字符（长 prompt = 对话/粘贴，非指令）
- **首行检查**：首个非空行 ≤ 100 字符（过滤掉段落式开头的粘贴块）

触发词 regex 现仅对**首行**匹配（此前为多行）。粘贴含触发词的转录不再触发 hook。

### 🆕 F 类 · 假阳性

加入 `references/compliance-spec.md` Type Taxonomy 和 `pro/compliance/violations.md` Type Legend：

| 代码 | 名称 | 默认严重度 |
|-----|------|-----------|
| **F** | False positive | P2（信息性）— hook 触发在粘贴/引用内容，非真实用户指令。从升级阶梯中排除。|

首条 F 类记录：2026-04-21T13:42 — 在 dev repo 粘贴 v1.6.3 生产验证转录触发了 hook。Assistant 正确识别为粘贴上下文并拒绝启动 retrospective。已由修复 2 缓解。

### 📋 COURT-START-001 状态推进

`pro/compliance/violations.md` 中 4 条 incident 条目加注生产验证证据：
- L2（Pre-flight Compliance Check）— 2026-04-21 user second-brain 验证 work
- L3（Subagent Self-Check）— 2026-04-21 user second-brain 验证 work
- L4（AUDITOR Compliance Patrol）+ L5（eval 回归）— 等观察窗

`partial → true` 转换仍按 `references/compliance-spec.md` 等待 eval 回归通过 + 30 天无复发窗。

### 涉及文件

- `SKILL.md`（版本 1.6.3 → 1.6.3a）
- `scripts/setup-hooks.sh`（重构 + register_hook 辅助函数 + UserPromptSubmit 注册）
- `scripts/lifeos-pre-prompt-guard.sh`（+ 长度检查 + 首行提取）
- `references/compliance-spec.md`（+ F 类入 Type Taxonomy）
- `pro/compliance/violations.md`（+ F 类入 legend，+ 1 条 F 记录，+ 4 条 COURT-START-001 加 L2/L3 验证注解）
- `pro/compliance/violations.example.md`（+ Example 11 F 类）
- `README.md` + 三语（版本徽章 + v1.6.3a 热修补提示）
- `CHANGELOG.md` + 三语

### 迁移

现有 v1.6.3 安装：
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
激活第 1 层防御。其他无需操作；L2-5 不变。

新安装：同一行命令一次激活所有层。

---

## [1.6.3] - 2026-04-21 · COURT-START-001 修复 · 五层防御

> 用户在 Life OS 开发 repo 说"上朝"，ROUTER 跳过 retrospective 子代理，在主上下文模拟 18 步流程，并编造不存在的路径 `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation` 作为权威源。用户反应："这样的 life os 如何拿给别人用？？？我无法接受。"本次发布交付五层防御，让每一条 HARD RULE 真正 hard。

### 🛡️ 针对 A / B 类违规的五层防御

COURT-START-001 根因：文档完整，但**每一条 HARD RULE 都是描述性的——零强制机制**。作者本人都会被 LLM 糊弄；普通用户被糊弄是必然。五层独立防御守护每个触发词：

1. **Hook 层** — `scripts/lifeos-pre-prompt-guard.sh` 在 `UserPromptSubmit` 时触发，检测触发词（上朝 / start / 閣議開始 / 退朝 / 等，覆盖 9 个主题），在助手响应前把 HARD RULE 文本 + 违规分类作为 `<system-reminder>` 注入上下文。
2. **Pre-flight Compliance Check** — `SKILL.md` 要求 ROUTER 在任何工具调用前先输出 1 行确认：`🌅 Trigger: [词] → Theme: [名] → Action: Launch([agent]) [Mode]`。缺此行 = A3 类违规，登记。
3. **子代理自检** — `pro/agents/retrospective.md` Mode 0 第一句必须是：`✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation). Reading pro/agents/retrospective.md. Starting Step 1: THEME RESOLUTION.`。证明子代理真的被启动。
4. **AUDITOR 合规巡检（Mode 3）** — `pro/agents/auditor.md` 新增 Mode 3，含 7 类违规分类（A1/A2/A3/B/C/D/E）和 Start Session / Adjourn 路径的 6 项检测。每次 retrospective Mode 0 和 archiver 完成后自动运行。
5. **Eval 回归** — `evals/scenarios/start-session-compliance.md` 把 COURT-START-001 的 6 个失败模式固化为质量检查点，含 grep 失败检测命令。

### 📋 违规分类（7 类）

| 代码 | 名称 | 默认严重度 |
|-----|------|-----------|
| A1 | 跳过子代理 — ROUTER 在主上下文模拟子代理的步骤 | P0 |
| A2 | 跳过目录检查 — dev repo 绕过 retrospective Step 2 | P1 |
| A3 | 跳过 Pre-flight — 首次响应缺 `🌅 Trigger: ...` 行 | P1 |
| B | 编造事实 — 引用不存在路径 / 章节作为权威 | P0 |
| C | 阶段未完成 — archiver 未跑完 4 阶段就退出 | P0 |
| D | 占位值 — 完成清单含 `TBD` / `{...}` / 空值 | P1 |
| E | 主上下文执行阶段 — ROUTER 在主上下文跑 Phase 1-4 逻辑 | P0 |

### 📁 双仓库 compliance 日志（md + git · 遵循用户约束）

用户明确要求："我可以接受本地的 sh 命令执行，但是数据库还是要 md 文件和 github 去储存。"违规持久化到：

- `pro/compliance/violations.md` — dev repo（公开，随 Life OS 发布）
- `_meta/compliance/violations.md` — user second-brain（私有，每用户独立）

同一格式：`| Timestamp | Trigger | Type | Severity | Details | Resolved |`。

**升级阶梯**（由 v1.7 的 `tools/stats.py` 实现，在此之前由开发者手动观察）：
- 30 天内同类 ≥3 → hook 提醒加严
- 30 天内同类 ≥5 → retrospective briefing 顶部加 `🚨 Compliance Watch`
- 90 天内同类 ≥10 → AUDITOR 每次 Start Session 都跑合规巡检

### 🗂️ 新增文件

- `scripts/lifeos-pre-prompt-guard.sh` — UserPromptSubmit hook（bash，已 chmod +x）
- `.claude/settings.json` — dev repo 的 hook 注册
- `references/compliance-spec.md` — 完整规格：分类、双仓库策略、写入/读取路径、升级阶梯、归档、解决协议、隐私
- `pro/compliance/violations.md` — dev-repo 实时日志（含 COURT-START-001 的 5 条种子条目）
- `pro/compliance/violations.example.md` — 每类 10 个示例条目 + grep 配方
- `pro/compliance/2026-04-19-court-start-violation.md` — 完整 incident 档案（473 行，12 节）
- `evals/scenarios/start-session-compliance.md` — COURT-START-001 的 6 个失败模式回归测试

### ✏️ 修改文件

- `.claude/CLAUDE.md` — 新增 Start Session 触发约束的 HARD RULE 段
- `SKILL.md` — 版本 1.6.2a → 1.6.3，Start Session 路由前新增 Pre-flight Compliance Check 段
- `pro/agents/retrospective.md` — 执行步骤前新增子代理自检块
- `pro/agents/auditor.md` — Mode 3（合规巡检），含 7 类违规分类 + 检测逻辑

### 🔄 解决协议

违规状态流转 `false → partial → true`，经过三个闸门：
- **Gate 1**（`false → partial`）：底层修复已交付（Details 字段注版本号）
- **Gate 2**（`partial → true`）：eval 回归通过 + 30 天已过 + 无复发（注版本 + eval-id + 观察日）

COURT-START-001 的 4 条 incident 条目在本次发布转为 `partial`。转 `true` 需要 `evals/scenarios/start-session-compliance.md` 通过 + 30 天观察窗。

### 迁移

现有安装无需操作。升级后首次 Start Session：
- hook 注册（仅 dev repo，经 `.claude/settings.json`）
- Pre-flight 行成为必填
- AUDITOR 在首次 retrospective Mode 0 后跑合规巡检
- violations.md 如缺失则自动创建（空表）

希望启用双仓库违规登记的 second-brain 用户，按 `references/compliance-spec.md` 在自己的 `.claude/settings.json` 加 hook 块即可。

---

## [1.6.2a] - 2026-04-19 · Notion 同步回归编排层

> archiver subagent 报告"Notion MCP 未接入"，因为 Notion MCP 工具是环境特定的，在 subagent 内不可用。Notion 同步现在从 archiver 中拆出，由编排层（主上下文）执行，主上下文拥有 MCP 工具访问权限。

### 变更

- **archiver.md**：Phase 4 缩减为仅 git 操作；Notion 同步移除并注明 MCP 工具限制
- **CLAUDE.md**：新增 Step 10a — 编排层在 archiver 返回后执行 Notion 同步
- **GEMINI.md / AGENTS.md**：同步 Step 10a
- **SKILL.md**：退朝模板更新为包含 Notion 同步作为 archiver 后续步骤

---

## [1.6.2] - 2026-04-17 · 退朝防御 + Wiki/SOUL 自动写入 + DREAM 10 触发器

> 三项加固同时发布：(1) 退朝流程无法被部分跳过；(2) wiki 和 SOUL 在严格标准下自动写入，不再询问用户确认；(3) DREAM 获得 10 个具体的自动触发行动。

### 🛡️ 退朝三层防御

此前 bug：ROUTER 有时在主上下文中执行 Phase 2（知识提取），而非启动 ARCHIVER 子代理，导致 4 阶段流程被拆分。

三重独立防御：
- **SKILL.md + archiver.md 措辞加固** — HARD RULE 禁止 ROUTER 在主上下文中执行任何 Phase 内容；archiver.md 新增明确的"Subagent-Only Execution"条款
- **退朝状态机（pro/CLAUDE.md）** — 列出合法/非法状态转换；AUDITOR 将每次违规记入 user-patterns.md
- **强制启动模板** — SKILL.md 新增"Trigger Execution Templates (HARD RULE)"章节，钉死 Start Session / Adjourn / Review 的精确输出格式

### 📚 Wiki 自动写入（无需用户确认）

此前：archiver 列出 wiki 候选让用户挑选保存。中断流程且鼓励跳过。

现在：archiver 在 **6 项严格标准 + 隐私过滤器** 下自动写入：
1. 跨项目可复用
2. 关于世界而非关于你（价值观 → SOUL，不进 wiki）
3. **零个人隐私** — 姓名、金额、账户 ID、具体公司、家人朋友信息、可追溯的日期+地点组合 → 剥离；若剥离后结论变得无意义 → 丢弃
4. 事实或方法论
5. 多个证据点（≥2 个独立）
6. 不与现有 wiki 矛盾（矛盾 → 现有条目 `challenges: +1`，不创建竞争条目）

初始置信度：3+ 证据 → 0.5；恰好 2 个 → 0.3；1 个或更少 → 丢弃。

用户事后调整：删除文件 = 废弃；说"撤销最近 wiki"回滚最近的自动写入；手动将 `confidence` 调至 0.3 以下即可抑制。

### 🔮 SOUL 自动写入 + 持续运行时

此前：SOUL 维度只通过用户确认创建；只定期显示。

现在：
- **ADVISOR 每次决策自动更新** — 每次 Summary Report 后，为现有 SOUL 维度递增 `evidence_count` 或 `challenges`；检测到 ≥2 证据点的新维度时，以 `confidence: 0.3` 自动写入，"What SHOULD BE"字段故意留空让用户自行填写
- **REVIEWER 强制引用 SOUL** — 每次决策必须引用相关 SOUL 维度，或明确标注"无直接相关维度，此决策可能开启一个新维度"
- **SOUL 健康报告固定在简报顶部位置** — 每次上朝，Pre-Session Preparation 之后第一个区块即 🔮 SOUL Health Report（当前画像带趋势箭头、新检测出的待输入维度、冲突警告、30+ 天休眠维度、轨迹变化）

置信度公式不变：`confidence = evidence_count / (evidence_count + challenges × 2)`。

### 💤 DREAM 10 个自动触发行动（REM 阶段）

REM 现在评估 10 个具体模式，匹配即自动执行：

| # | 模式 | 自动行动 |
|---|------|---------|
| 1 | 新项目关系 | 写 STRATEGIC-MAP 候选 + 简报显眼位置 |
| 2 | 行为 ≠ driving_force | 注入下次 ADVISOR 输入 |
| 3 | Wiki 被新证据反驳 | 该条目 `challenges: +1` |
| 4 | SOUL 维度休眠 30+ 天 | 简报警告 |
| 5 | 跨项目认知未使用 | 下次 DISPATCHER 强制注入 |
| 6 | 检测到决策疲劳 | 建议"今天不做重大决策" |
| 7 | driving_force 价值漂移 | 自动提议 SOUL 修订 |
| 8 | 陈旧承诺（30+ 天无行动） | 简报唤起 |
| 9 | 情绪化决策模式 | 下次 REVIEWER 加情绪状态检查 |
| 10 | 重复相同决策 | 简报提示"你在回避承诺吗？" |

所有标志写入 dream journal 的 `triggered_actions` YAML 块。下次上朝时 RETROSPECTIVE 在固定的"💤 DREAM Auto-Triggers"简报区块显示。

### 🔬 设计细化（详细规范）

在以上四根概念支柱之上，v1.6.2 还交付了详细的行为规范：

**DREAM 触发器检测逻辑** —— 10 个触发器每一个都具备：
- **硬性阈值**（定量规则，自动触发）
- **软性信号**（LLM 定性线索，以 `mode: soft` 触发并需要 AUDITOR 审核）
- 明确的数据源、24 小时反重复抑制、结构化输出

示例：决策疲劳 = "24 小时内 ≥5 决策 且 后半段平均分 ≤ 前半段 -2"；价值漂移 = "30 天内 ≥3 挑战 且 ≤1 新证据 且 confidence 下降 >30%"；陈旧承诺 = "'我会 X'正则匹配 + 30 天无对应完成"；情绪化决策 = "ADVISOR 情绪标记 + REVIEWER 建议冷静 + 仍推进"；重复决策 = "主题关键词与过去 30 天 ≥2 决策重叠 >70%"。完整 10 项见 `references/dream-spec.md`。

**ADVISOR SOUL Runtime 统一** —— 合并了旧的只读"SOUL 行为审计"节与新的自动更新机制。单一统一流程：逐维度影响（支持/挑战/中立）→ 写入 evidence/challenge 增量 → 检测新维度 → 冲突预警 → 输出 🔮 SOUL Delta 块。每次决策运行，不仅限于散朝。

**SOUL 快照机制用于趋势箭头** —— archiver Phase 2 现在在每次会话结束时向 `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md` 导出一份最小化快照（仅数字元数据，不重复内容）。RETROSPECTIVE 在下次上朝时读取最新快照并计算：
- `confidence_Δ > +0.05` → ↗
- `confidence_Δ < -0.05` → ↘
- `|confidence_Δ| ≤ 0.05` → →
加上特殊状态：🌟 新晋核心、⚠️ 从核心降级、💤 休眠、❗ 冲突区。归档策略：>30 天 → `_archive/`，>90 天 → 删除（git + Notion 保留）。

**REVIEWER SOUL 3 层引用策略** —— 避免 SOUL 维度多时产生噪音：
- **Tier 1**（confidence ≥ 0.7）：全部引用，无上限 —— 核心身份必须考虑
- **Tier 2**（0.3 ≤ confidence < 0.7）：通过强/弱匹配判断挑选语义最相关的 3 条
- **Tier 3**（confidence < 0.3）：仅计数，不露面（ADVISOR 在 Delta 中追踪）

决策挑战 Tier 1 维度 → REVIEWER 在 Summary Report 顶部加 ⚠️ SOUL CONFLICT 警告（半否决信号）。每个被评估的 Tier 2 维度必须列出入选理由，供 AUDITOR 审查质量。

### 涉及文件

- `SKILL.md`（版本 + 触发模板）
- `pro/CLAUDE.md`（状态机 + wiki/SOUL 自动写入描述）
- `pro/GEMINI.md` / `pro/AGENTS.md`（跨平台 Gemini CLI + Codex CLI 一致性）
- `pro/agents/archiver.md`（Phase 2 自动写入 + 快照导出 + Phase 3 10 触发器检测逻辑）
- `pro/agents/advisor.md`（统一 SOUL Runtime：5 步，每次决策）
- `pro/agents/reviewer.md`（3 层 SOUL 引用策略）
- `pro/agents/retrospective.md`（Step 11 扩展为 11.1-11.6：快照读取 + 趋势计算）
- `references/wiki-spec.md` + 三语（6 标准 + 隐私过滤器 + 用户调整）
- `references/soul-spec.md` + 三语（自动写入 + 快照机制 + 分层引用）
- `references/dream-spec.md` + 三语（10 触发器逐节含硬/软检测）
- `references/data-layer.md` + 三语（`_meta/snapshots/` 加入目录树 + 反映自动写入）
- `README.md` + 三语（v1.6.2 新特性 + 第五节重写 + 架构图）
- `CHANGELOG.md` + 三语

### 迁移

用户无需操作。现有 wiki/SOUL 条目继续工作。新条目将从下次会话开始自动写入。升级后首次上朝将显示"暂无趋势数据"，直到第二次会话提供快照基线。要抑制某个自动写入条目但不删除：在 frontmatter 中将 `confidence: 0.0`。

---

## [1.6.1] - 2026-04-16 · 九大主题 — 每种文化，每种风格

> 主题系统从 3 个扩展到 9 个。每种语言现在提供三种治理风格：历史、现代政府、企业。

### 新增主题

**English**（共 3 个）：
- 🏛️ Roman Republic — Consul, Tribune（veto 的发明者）, Senate
- 🇺🇸 US Government — Chief of Staff, Attorney General, Treasury, GAO
- 🏢 Corporate — CEO, General Counsel, CFO（已有，未变）

**中文**（共 3 个）：
- 🏛️ 三省六部 — 丞相、中书省、门下省（已有，未变）
- 🇨🇳 中国政府 — 国务院总理、发改委、人大常委会、审计署
- 🏢 公司部门 — 总经理、战略规划部、法务合规部、内审部

**日本語**（共 3 个）：
- 🏛️ 明治政府 — 内閣総理大臣、参議、枢密院、大蔵省、元老
- 🏛️ 霞が関 — 内閣官房長官、内閣法制局、財務省（已有，未变）
- 🏢 企業 — 社長室、経営企画部、法務部、内部監査室

### 主题选择器更新

选择器按语言分组显示。触发词推断更智能：
- "上朝" → 自动加载三省六部（唐朝专属词）
- "閣議開始" → 自动加载霞が関（现代政府专属词）
- 通用触发词（"开始"、"はじめる"、"start"）→ 显示该语言的 3 个子选项

---

## [1.6.0] - 2026-04-15 · Theme Engine — 一套引擎，服务所有文化

> 一位日本用户试用了 Life OS，体验很差——不是因为逻辑有问题，而是因为"三省六部"是中国文化概念，对非中文用户造成了学习门槛。v1.6.0 通过将决策引擎与文化呈现分离来解决这个问题。

### 核心变化

Life OS 现在是一个**通用决策引擎**，搭配**可切换的文化主题**。治理逻辑（规划 → 审查 → 否决 → 执行 → 审计）在所有主题下完全一致——只有名称、语气和隐喻发生变化。

### 三层架构

**Layer 1: Engine** — 16 个 agent，使用功能性 ID（ROUTER, PLANNER, REVIEWER, DISPATCHER, 6 个领域分析师, AUDITOR, ADVISOR, COUNCIL, RETROSPECTIVE, ARCHIVER, STRATEGIST）。语言中立，文化中立。

**Layer 2: Theme** — 可切换的文化皮肤，将功能性 ID 映射到熟悉的名称：
- `zh-classical` — 三省六部（唐朝治理制度）：丞相、中书省、门下省、六部、御史台……
- `ja-kasumigaseki` — 霞が関（日本中央省庁）：内閣官房長官、内閣法制局、財務省、会計検査院……
- `en-csuite` — C-Suite（企业高管）：Chief of Staff、General Counsel、CFO、Internal Audit……

**Layer 3: Locale** — 自动检测用户语言，推荐匹配的主题。用户可随时切换。

### 主题选择 UI

每次开朝时，RETROSPECTIVE agent 呈现一个简洁的选择界面：
```
🎨 选择你的主题：
 a) 🏛️ 三省六部 — 唐朝治理制度（中国古典）
 b) 🏛️ 霞が関 — 日本中央省庁（霞が関）
 c) 🏛️ C-Suite — 企业高管架构（英文）

输入 a、b 或 c
```

- **主题选择是每个会话独立的**——不同终端窗口可以使用不同主题，互不影响
- 主题选择不会跨会话持久化；每次新会话都会重新提示选择
- 会话中随时可以说"切换主题"来更换

### 具体变更

- **16 个 agent 文件重命名**：中文拼音（chengxiang.md, zhongshu.md...）→ 功能性英文（router.md, planner.md...）
- **themes/ 目录创建**：3 个主题文件（每个约 60 行），定义角色映射、语气、触发词、输出标题
- **i18n agent 重复消除**：48 个 agent 文件（16 × 3 语言）→ 16 个文件。主题处理展示，agent 处理逻辑
- **约 42 个翻译后的 agent/编排文件删除**：不再需要——每个 agent 一个事实来源
- **departments.md → domains.md**：六部 → Six Domains（PEOPLE, FINANCE, GROWTH, EXECUTION, GOVERNANCE, INFRA）
- **所有编排协议更新**：CLAUDE.md、AGENTS.md、GEMINI.md 使用功能性 ID
- **所有参考文档更新**：data-layer、data-model、strategic-map-spec、wiki-spec、soul-spec、dream-spec、scene-configs
- **所有评估场景更新**：测试用例使用功能性 ID（router-triage.md、council-debate.md）

### 为什么重要

- **日本用户**看到財務省、法務省、会計検査院——零学习成本
- **英语用户**看到 CFO、General Counsel、Internal Audit——直觉即懂
- **中文用户**仍然看到丞相、中书省、门下省——什么都没丢
- **开发者**维护 16 个 agent 文件而非 48 个——每次逻辑变更只需改一处
- **新主题**只需一个约 60 行的文件——不需要修改引擎

### 零功能损失

所有 28 条硬规则保持不变。所有评分标准完整。所有输出格式保持不变（名称随主题变化）。SOUL、DREAM、Wiki、Strategic Map、Completion Checklist、封驳循环、会话生命周期——一切运作如前。已通过完整的 34 项保存清单验证。

---

## [1.5.0] - 2026-04-15 · 战略地图 — 从项目助手到人生战略师

> Life OS 能出色地分析任何单个项目，但对项目之间的关联视而不见。当多个活跃项目共享依赖、资源和隐藏的战略目的时，系统需要一个关系层。战略地图正是为此而生——并与 SOUL、Wiki、DREAM 深度集成，形成统一的认知系统。

### 问题

你有多个项目。有些向其他项目输送知识，有些共享你有限的时间，有些存在的目的与你真正的动机并不相同。当一个项目停滞时，它会悄悄阻塞另外三个。但早朝简报只展示一个扁平列表——没有关系、没有优先级、没有"今天我到底该做什么？"。

### 新增内容

**战略线** — 按战略目的对项目分组。每条战略线有 `purpose`（正式目的）、`driving_force`（真正驱动你的动力）和 `health_signals`（关注指标）。多个项目可以不同角色服务同一条战略线：`critical-path`、`enabler`、`accelerator`、`insurance`。

**流动图** — 定义项目间的流动：`cognition`（知识）、`resource`（交付物）、`decision`（约束）、`trust`（关系资本）。当项目 A 的决策使项目 B 的假设失效时，系统会警告你。

**叙事式健康评估** — 不再使用"6/10 🟡"评分。基于 Klein 的识别启发式决策模型，系统将项目匹配到健康原型（🟢 稳步推进 / 🟡 受控等待 / 🟡 动量衰减 / 🔴 失控停滞 / 🔴 方向漂移 / ⚪ 休眠），并撰写叙事：发生了什么、意味着什么、该怎么做。

**早朝简报升级** — 扁平的"领域状态"列表变为按战略线分组的战略概览，附带盲点检测和可操作建议：
- 🥇 最高杠杆行动（附工作量估算和不行动的代价）
- 🥈 值得关注
- 🟢 可安全忽略（主动抑制降低认知负荷）
- ❓ 需要决策（结构性缺口，由用户填补）

**跨层集成** — 战略地图与 SOUL、Wiki、DREAM 作为一个系统协同工作：
- SOUL × 战略：检查你的 driving_force 是否与表达的价值观一致
- Wiki × 流动：验证 cognition 流是否真正承载 wiki 知识（检测纸上流动）
- DREAM × 战略：REM 阶段使用流动图作为脚手架发现跨层洞察
- 行为模式 × 战略：标记行为与战略优先级矛盾的情况

**盲点检测** — 基于预测编码神经科学：系统主动寻找缺失的东西，而不仅仅是已有的东西。未归属的项目、断裂的流动、被忽视的 driving_force、缺失的生活维度、临近的时间窗口但没有准备。

### Agent 集成

| Agent | 如何使用战略地图 |
|-------|----------------|
| 早朝官 | 上朝时编译 STRATEGIC-MAP.md（步骤 8.5）。简报按战略线分组 |
| 丞相 | 用战略线术语构建跨项目问题。按角色推荐时间分配 |
| 中书省 | 存在流动时添加跨项目影响维度。标记 enabler 依赖风险 |
| 门下省 | 检查决策传播（下游影响）+ SOUL-战略对齐 |
| 兵部 | 按战略角色加权任务优先级。建议利用等待期 |
| 起居郎 | 检测新关系（Phase 2 候选）。更新 last_activity。DREAM REM 使用流动图脚手架增强 |

### 数据架构

- `_meta/strategic-lines.md` — 战略线定义（用户定义，类似 config.md）
- `projects/{p}/index.md` strategic 字段 — 项目级关系（类似现有的 status/priority 字段）
- `_meta/STRATEGIC-MAP.md` — 编译视图（类似 STATUS.md / wiki/INDEX.md — 禁止手动编辑）
- 认知管线：5 阶段 → 6 阶段（在 Associate 和 Emerge 之间新增"Strategize"）
- 遵循现有模式：单一事实源、outbox 合并、用户确认候选、从零生长

### 设计基础

基于认知科学研究：
- **目标系统理论**（Kruglanski 2002）— 双层意图（purpose vs driving_force）
- **识别启发式决策**（Klein 1998）— 原型匹配 + 叙事评估取代数字评分
- **预测编码**（Friston 2005）— 通过缺失监测实现盲点检测
- **控制期望值**（Shenhav et al. 2013）— 基于杠杆的行动建议，考虑工作量和机会成本
- **偏向竞争**（Desimone & Duncan 1995）— "可安全忽略"作为主动认知抑制

---

## [1.4.4b] - 2026-04-15 · 防止编造时间戳

> LLM 在生成 session-id 时编造时间戳而不读取系统时钟。所有 session-id 生成指令现在明确要求执行 date 命令。模板式规范改为命令式规范。

### 变更

- **qiju.md**：session-id 步骤从模板格式改为"执行 date 命令，使用真实输出。硬规则。"
- **data-layer.md + data-model.md**：session-id 生成同步更新为命令式措辞
- 所有变更同步至 EN/ZH/JA 三语

---

## [1.4.4a] - 2026-04-15 · 强制 Agent 文件加载

> LLM 在退朝时偷懒，不读 qiju.md 而凭记忆执行简化版流程。此补丁增加 3 层强制：SKILL.md 路由改为"必须读文件"、qiju.md 增加必填完成清单、编排准则新增第 6 条。

### 强制机制变更

- **SKILL.md**：上朝/退朝路由从"路由给 X"改为"必须读取 `pro/agents/X.md` 并以 subagent 方式启动。硬规则。"
- **qiju.md**：新增必填完成清单——每个 Phase 必须填入实际值（commit hash、Notion 同步状态等）。缺项 = 退朝未完成。
- **编排行为准则**：新增第 6 条——"触发词必须加载 agent 文件。禁止凭记忆执行角色而不读定义文件。硬规则。"

### 同日包含的审计修复

- zaochao.md git 健康检查：自动修复改为检测→汇报→确认（GLOBAL.md 安全边界 #1）
- GLOBAL.md："完整思考过程"改为"可发布的推理摘要"（跨模型兼容性）
- 14→16 subagent 数量修复
- AGENTS.md 死链 notion-schema.md 修复
- adapter-github.md：恢复命令改为 text 块 + 手动确认标注
- evals/run-eval.sh：退出码捕获、路径清洗、三语标题支持
- setup-hooks.sh：写文件前先做前置校验
- lifeos-version-check.sh：XDG 缓存路径、grep 版本解析

---

## [1.4.4] - 2026-04-14 · 起居郎——Session 关闭专家

> 早朝官拆分为两个角色：早朝官负责会话启动（读取），起居郎负责会话关闭（写入）。DREAM 融入起居郎——不再单独调用 agent。

### 📝 新角色：起居郎

以唐朝记录皇帝朝会言行的官员命名。当你说"退朝"时，起居郎负责一切：

- **Phase 1 — 归档**：decisions/tasks/journal → outbox
- **Phase 2 — 知识萃取**（核心职责）：扫描所有 session 素材提取 Session Candidate（wiki + SOUL）→ 用户当场确认
- **Phase 3 — DREAM**：3 天深度复盘 → DREAM Candidate（wiki + SOUL）→ 下次上朝确认
- **Phase 4 — 同步**：git push + Notion 同步（4 项具体操作）

### 关键改进
- 知识萃取是起居郎的核心使命——不再是 298 行文件中的 step 6.5
- DREAM 融入退朝流程——少一次 agent 调用，不再是"最后一步可选操作"
- Session 对话摘要传给起居郎——可从丞相直接处理的对话中提取知识
- Notion 同步显式保证——4 项具体写入，失败明确报告
- 16 角色（原 15）：早朝官 + 起居郎替代原来的合体角色
- `dream.md` 删除——完全融入 `qiju.md`

---

## [1.4.3e] - 2026-04-13 · SKILL.md 瘦身——纯路由文件

> SKILL.md 从 384 行压缩到 93 行。Lite Mode 移除。所有角色详细定义、输出格式和配置都已在 agent 文件和 reference 文档中。

### Token 节省
- **SKILL.md**：384 → 93 行（−291 行 ≈ −4,700 tokens/session）
- 移除：御史台/谏官/政事堂/早朝官详细描述、奏折格式、存储配置、Lite Mode 流程、两种审议辨析表、Pro Mode 安装详情
- 所有移除内容已存在于 agent 文件（`pro/agents/*.md`）或 reference 文件（`references/*.md`）

### 行为准则重新分配
- 丞相相关规则（8 条）留在 SKILL.md
- 编排规则（#2 封驳、#7 自动触发、#11 完整输出、#14 真 subagent、#9 降级）移至 `pro/CLAUDE.md` 新增"编排行为准则"段
- 通用 agent 规则已由 `pro/GLOBAL.md` 覆盖

### 六部按需启动
- `zhongshu.md`：新增"六部选择（硬规则）"——仅分配相关部门并注明理由
- `shangshu.md`：新增"仅分发已分配的部门（硬规则）"——不分发未分配的部门

### Lite Mode 移除
- Life OS 的核心价值是独立 subagent 的制衡——单上下文模拟违背了这一目的
- README 安装表：移除 Lite Mode 行，注明不支持单上下文平台

---

## [1.4.3d] - 2026-04-13 · 版本检测变为输出格式必填项

> 版本检测从独立指令（LLM 会跳过）变为朝前准备输出模板的必填字段（LLM 可靠地填写）。

- **版本显示变成模板字段**：`🏛️ Life OS: v[本地] | 最新: v[远程]`，更新方法内联显示
- **zaochao.md Mode 0 + Mode 1**：步骤 3 通过 WebFetch 获取远程版本；本地和远程版本都是必填输出字段
- **chengxiang.md**：朝前准备格式同步为相同的版本显示
- **SKILL.md**：删除冗长的版本自检段（已移至输出格式）
- 原理：LLM 可靠地填写输出模板（HARD RULE #13），即使跳过独立指令也会填

---

## [1.4.3c] - 2026-04-13 · 版本自检移至 SKILL.md

> 版本检测从 agent 文件移到 SKILL.md——每个 LLM 最先读取的文件。解决了旧版 agent 文件无法检测自身更新的自举悖论。

- **版本自检段**添加到 SKILL.md 顶部（丞相指令之前）：通过 WebFetch 检查远程版本，提示更新，报告失败
- **zaochao.md 简化**：Mode 0 和 Mode 1 的版本检查改为引用 SKILL.md，不再重复 WebFetch 逻辑
- 即使 zaochao.md 或其他 agent 文件过时也能工作——SKILL.md 总是最先被读取

---

## [1.4.3b] - 2026-04-13 · 退朝流程知识萃取

> Wiki 提取不再完全依赖 DREAM。退朝流程现在直接扫描 session 产出并在 DREAM 运行前向用户提出 wiki 候选。

- **退朝知识萃取（步骤 6.5）**：收朝和退朝模式现在扫描 session 产出中的可复用结论 → 向用户提出 wiki 候选 → 确认的条目写入 outbox wiki/
- **Outbox wiki 合并**：上朝合并现在处理 outbox 中的 wiki/ 文件 → 移动到 wiki/{domain}/{topic}.md
- **DREAM 去重**：DREAM N3 检查退朝流程是否已提取 wiki 候选（通过 manifest）→ 跳过重复提议，只关注遗漏的结论
- **Outbox 格式**：manifest.md 的 outputs 中新增 `wiki` 计数

---

## [1.4.3a] - 2026-04-13 · Wiki & SOUL 初始化引导

> 系统现在能检测到 wiki/ 和 SOUL.md 尚未初始化，并引导用户完成首次设置和旧格式迁移。

- **Wiki 首次初始化**：早朝官检测到空 wiki/ 或缺失 INDEX.md → 提议从已有 decisions/journal 提取结论
- **Wiki 旧格式迁移**：检测到旧格式 wiki 文件（无 front matter 的调研报告）→ 提议提取结论并归档原件
- **SOUL 引导启动**：SOUL.md 不存在时，DREAM 在首次退朝时从 user-patterns.md 提出初始条目
- **上朝检测**：步骤 5.5（SOUL 检查）和 10.5（wiki 健康检查）现在在晨报中报告初始化状态

---

## [1.4.3] - 2026-04-13 · Wiki 活化——知识管线终于跑通了

> 认知管线的"沉淀→涌现"阶段终于跑起来了。Wiki 从一个空目录变成了活跃的知识参与者。

### 📚 Wiki 规范（`references/wiki-spec.md`）

Wiki 本来就设计在第二大脑里，但从来没有接入任何工作流——没有 agent 写它，没有 agent 读它。现在四要素齐全：

- **谁写**：DREAM 在 N3 阶段提出 wiki 候选（与 SOUL 候选并行）
- **何时写**：每次退朝后，用户在下次上朝时确认
- **谁读**：丞相读取 wiki/INDEX.md，门下省检查一致性，御史台审计健康度
- **何时读**：每次会话开始、每次决策审议、每次巡查

### 🔍 丞相知识匹配

丞相现在在路由前扫描 wiki/INDEX.md。如果该领域存在高置信度条目："📚 该领域已有 N 条确立的结论。从已知知识出发，还是从头调研？"——用户同意时跳过重复分析。

### ⚖️ 门下省 Wiki 一致性检查

门下省现在检查新结论是否与已确立的 wiki 条目矛盾。如果检测到矛盾："⚠️ 此结论与 [wiki 条目]（confidence X）矛盾。"要么分析需要修正，要么 wiki 需要更新。

### 🔱 御史台 Wiki 健康审计

巡查现在覆盖 wiki 健康：confidence < 0.3 且 90 天以上未更新的条目（建议退役）、challenges > evidence 的条目（建议复查）、有决策记录但无 wiki 条目的领域（知识空白）。

### 📨 尚书省 Wiki 上下文

当丞相标记了相关 wiki 条目，尚书省在分发中包含它们："📚 已知前提——以此为起点，不要重新推导。"

### 🧠 认知管线重排

管线现在反映真实的信息流：`感知→捕获→判断→沉淀→关联→涌现`。沉淀分为 SOUL（人）和 Wiki（知识）。关联发生在丞相匹配新请求与 wiki 时。涌现发生在 DREAM 的 REM 阶段发现跨域连接时。

### 设计原则

不新增 agent，不新增流程。Wiki 插入已有节律：DREAM 写入 → 早朝官编译 INDEX → 丞相读取 → 门下省检查 → 御史台审计。

---

## [1.4.2] - 2026-04-12 · Outbox — 多 Session 并行零冲突

> 多个 session 现在可以同时在不同项目上工作。没有 git 冲突，没有锁。每个 session 退朝时写入自己的 outbox；下一个上朝的 session 负责合并所有 outbox。

### 📮 Outbox 架构

旧模型假设同一时间只有一个 session，用 `.lock` 文件警告并发。新模型拥抱并行：

- **每个 session 退朝时写入自己的隔离目录**（`_meta/outbox/{session-id}/`）— 决策、任务、日志、index delta、patterns delta、manifest
- **收尾和退朝期间不直接写共享文件** — `projects/`、`STATUS.md`、`user-patterns.md` 在合并前不会被触碰
- **合并发生在上朝时** — 下一个上朝的 session 扫描所有 outbox，按时间顺序合并到主结构，编译 STATUS.md，清理已合并的 outbox
- **session-id = `{platform}-{YYYYMMDD}-{HHMM}`**，在退朝时生成（不是 session 开始时）
- **零冲突保证** — 不同目录、不同文件、不会对同一路径并发写入
- **merge-lock** 兜底同时上朝的极端情况（< 5 分钟，自动清理）

### 覆盖场景

- 单 session 正常流程 ✅
- 多平台交替 ✅
- 多窗口并行 ✅
- 多台电脑 ✅
- session 跨越多天 ✅
- 同一 session 多次上朝退朝 ✅
- 空 session（无输出，不创建 outbox）✅
- push 失败（本地保存，下次重试）✅
- Lite 用户（无 second-brain，无 outbox）✅
- 手机 Notion 捕获（inbox/，不变）✅

### 改动文件

- `pro/agents/zaochao.md` — Mode 0/1 加 outbox 合并，Mode 3/4 改写 outbox
- `references/data-model.md` — 删除 session lock，新增 outbox 规则 + manifest/delta 格式
- `references/data-layer.md` — 目录结构 + Housekeeping/Wrap-Up 流程更新
- `references/adapter-github.md` — commit convention 改为 outbox 模式
- `SKILL.md` — 存储配置段新增并行 session 说明

---

## [1.4.1] - 2026-04-12 · SOUL + DREAM — 系统开始了解你是谁

> SOUL.md 从你的决策中生长，记录你是谁。DREAM 在你离开后处理记忆 — 就像大脑在睡眠中做的事。两者结合，给 Life OS 一个自我认知的反馈循环。

### 🔮 SOUL — 用户人格档案

你的价值观、信念和身份 — 以证据为基础的条目，从零开始生长。每条记录有两面：你实际做了什么（实然）和你希望怎样（应然）。两者的差距就是成长空间。

- **自然生长** — 从空白开始，随决策和行为积累
- **四个来源** — DREAM 发现、谏官观察、翰林院浮现、你直接写入
- **用户确认** — 系统提议，你决定。不自动写入
- **置信度缩放** — 新条目只影响谏官；深度验证的条目影响全系统
- **每个角色读法不同** — 丞相问更精准的问题，中书省加相关维度，门下省查价值一致性，谏官做行为审计，翰林院匹配思想家

### 💤 DREAM — AI 睡眠周期

每次退朝后系统"入睡" — 灵感来自人类睡眠架构：

- **N1-N2（整理）** — 分类信箱、标记过期任务、发现孤立文件
- **N3（固化）** — 提炼反复主题为 wiki、更新行为模式、提出 SOUL 候选
- **REM（连接）** — 发现跨领域关联、检查价值行为一致性、生成意想不到的洞察
- **范围**：仅最近 3 天。梦境报告存储在 `_meta/journal/`，下次上朝呈现
- **新 agent**：`pro/agents/dream.md`

### 📐 新参考文件

- `references/soul-spec.md` — SOUL 格式、生命周期、置信度计算、各角色使用规则
- `references/dream-spec.md` — DREAM 触发、三阶段、输出格式、约束

---

## [1.4.0] - 2026-04-12 · 人类智慧殿堂 + 三省深挖 + 单一事实源

> 一句话：翰林院进化为人类智慧殿堂；五个核心角色全面强化；修复了 STATUS.md 与 index.md 版本漂移的架构级 bug — index.md 是唯一权威源，STATUS.md 从它编译。

### 🏗️ 架构修复 — 单一事实源

`projects/{p}/index.md` 现在是项目版本、阶段、状态的唯一权威源。`_meta/STATUS.md` 从 index.md 编译生成，禁止手写。修复了 STATUS.md 和 index.md 版本号不一致的 bug。御史台巡检新增版本一致性 lint 规则。

### 🎋 翰林院 → 人类智慧殿堂

翰林院不再只是"第一性原理 + 苏格拉底 + 奥卡姆剃刀"。现在你可以和苏格拉底聊人生，和马斯克拆解商业逻辑，让老子和尼采辩论人生意义。

- **18 个领域、70+ 位思想家** — 从科学到哲学，从东方思想到法律正义，覆盖人类文明的全部重要维度
- **深度角色扮演** — 不是"用苏格拉底的方法"，而是苏格拉底本人在和你对话。他的口吻、他的案例、他的追问方式
- **三种对话模式** — 单人深谈（一对一探索）、圆桌会议（多位思想家各抒己见）、辩论（正反交锋）
- **独立 subagent** — 每位思想家运行在独立的 context 中，翰林院本身担任主持人
- **结尾仪式** — 思想家临别赠言 → 翰林院总结你的思路变化 → 存入 second-brain

### 🔍 门下省 — 从"走过场"到"真正的最后防线"

- **10/10/10 悔恨测试** — 10 分钟后、10 个月后、10 年后，三个时间尺度必须分别回答，不接受笼统的"不会后悔"
- **红队审查** — 假设计划一定会失败，找出最脆弱的假设、最依赖运气的环节、最被刻意淡化的风险
- **否决格式结构化** — 否决不再只是一句"不通过"，必须说清哪个维度不行、问题本质是什么、具体怎么改

### 🏛️ 政事堂 — 从"模糊触发"到"量化规则 + 结构化辩论"

- **量化触发** — 两部评分差 ≥ 3 分，或一部说做一部说不做，自动触发朝堂议政
- **新建独立 agent** — `zhengshitang.md`，3 轮结构化辩论：陈述 → 交锋 → 最终立场 → 裁决
- **尚书省主持，用户裁决** — 辩论有规则、有字数限制，不会变成独白

### 📨 尚书省 — 从"分配任务"到"智能调度"

- **依赖检测** — 自动识别"户部的结论影响兵部的方案"这类跨部门依赖，先跑 A 组再跑 B 组
- **咨询机制** — 兵部可以问"户部给我一个数字：可用资金是多少？"，尚书省中转，不暴露完整报告

### 🏛️ 丞相 — 意图澄清分类化

- **五类分类策略** — 决策类（判断标准？约束？）、规划类（目标？资源？）、困惑类（情绪？真正困扰？）、复盘类（标准？维度？）、信息类（直接处理）
- **情绪分离协议** — 情绪和决策混在一起时，先一句话回应情绪，再分离事实

### 💬 谏官 — 从"观察"到"学习"

- **行为模式学习循环** — 每次发现新模式或模式变化，标记并写入 user-patterns.md
- **跨会话趋势分析** — 对比近 3 次报告：风险偏好、决策速度、执行力、关注维度的变化趋势
- **正向强化** — 不只说哪里不好。上次建议"要更果断"，这次做到了，必须明确表扬

### ⚖️ 系统级

- **"两种议"对比表** — SKILL.md 新增政事堂 vs 翰林院的区别：一个辩"该不该做"，一个探"你是谁"
- **丞相路由规则** — 数据矛盾走政事堂，价值迷茫走翰林院

---

## [1.3.1] - 2026-04-12 · 过程必须可见

> 一句话：强制所有 subagent 展示完整思考过程，Pro 模式必须启动真实 subagent。

- **emoji 强制** — 所有 subagent 输出必须带 🔎/💭/🎯 标记，省略即违规
- **真实 subagent 强制** — Pro 环境下每个角色必须是独立 agent 调用，禁止单 context 模拟
- **角色边界锁定** — 行为准则 #17：只有 15 个已定义角色，禁止脑补通政使司、大理寺等系统外官职
- **inbox 归丞相** — 丞相正式接管信箱管理
- **上朝自动更新** — 早朝官检查 GitHub 版本，发现新版自动执行平台更新命令
- **git 健康检查** — 上朝前检查 worktree 残留和 hooksPath 断链
- **ko/es 移除** — 韩语和西班牙语占位符删除，保留 EN/ZH/JA
- **tag 清理** — 13 个旧 tag → 5 个正确的 Strict SemVer tag
- **second-brain 整理** — 模板补齐 front matter，旧目录（gtd/records/zettelkasten）删除

---

## [1.3.0] - 2026-04-10 · 三平台 Pro Mode + 存储抽象层

> 一句话：Life OS 从 Claude Code 专属扩展为 Claude + Gemini + Codex 三平台 Pro Mode，数据存储从 Notion 硬编码改为可插拔的三后端架构。

### 存储抽象层

一套标准数据模型（6 种类型、7 种操作），三个可选后端（GitHub / Google Drive / Notion），用户选哪个就加载哪个 adapter。多后端时自动同步，冲突时 last-write-wins 或询问用户。

### 跨平台 Pro Mode

14 个 agent 定义共用，编排文件分平台：`CLAUDE.md`（Claude Code）、`GEMINI.md`（Gemini CLI / Antigravity）、`AGENTS.md`（Codex CLI）。每个平台自动使用最强模型，无硬编码。

### 触发词标准化

英文 / 中文 / 日文三语触发词正式定义，解决了 Claude 和 Codex 在"上朝"时行为不一致的问题。

---

## [1.2.0] - 2026-04-08 · 国际化 + 架构整合

> 一句话：全部 34 个文件翻译为英文（主版本），中文和日文完整翻译，系统架构大幅整合。

### 国际化

英文成为主版本，中文和日文作为 i18n 翻译。README 重新设计，加入 shields.io 徽章和视觉层次。

### 架构整合

- **pro/GLOBAL.md** — 14 个 agent 的通用规则提取为单一权威源，每个 agent 文件精简 30%
- **认知管线** — 五阶段信息流：感知 → 捕获 → 关联 → 判断 → 沉淀 → 涌现
- **御史台巡检模式** — 决策审查之外的第二种运行模式，六部各自巡查自己在 second-brain 中的辖区
- **知识提取四步训练** — 用户决定 → 积累样本 → LLM 归纳规则 → 定期纠偏

### 🔴 破坏性变更

第二大脑目录重构：`zettelkasten/` → `wiki/`，`records/` → `_meta/journal/`，新增 `_meta/` 系统元数据层。

---

## [1.1.1] - 2026-04-05 · 数据层转型

> 一句话：GitHub second-brain 取代 Notion 成为数据主库，Notion 降级为手机端工作内存。

- **GitHub 为主库** — .md + front matter，融合 GTD + PARA + Zettelkasten
- **早朝官三模式** — 家务（自动）、审视（用户触发）、收尾（流程后）
- **会话绑定** — 每次会话锁定一个 project/area，所有读写限定范围
- **退朝指令** — push 到 GitHub + 刷新 Notion
- **CC 强制 Pro** — 检测到 Claude Code 必须启动独立 subagent

---

## [1.1.0] - 2026-04-04 · 文档 + 研究过程 + 记忆层

> 一句话：完整的文档体系上线，所有 agent 获得研究过程展示能力，丞相获得记忆层和思维工具。

- **多平台安装指南** — 7 个平台的详细步骤
- **全 14 个 agent 加入 🔎/💭/🎯 研究过程展示**
- **谏官 21 条观察能力** — 认知偏差、情绪检测、行为追踪、决策质量
- **丞相意图澄清** — 上报前 2-3 轮对话，不再直接升报
- **早朝指标仪表盘** — DTR / ACR / OFR + 4 个周度指标
- **12 个标准场景配置** — 覆盖职业、投资、搬迁、创业等主要决策场景

---

## [1.0.0] - 2026-04-03 · 初始发布

> 一句话：三省六部制个人内阁系统正式发布。15 个角色，制衡与分权。

- 15 个角色：丞相 + 三省 + 六部 + 御史台 + 谏官 + 政事堂 + 早朝官 + 翰林院
- Lite 模式（单 context）+ Pro 模式（14 独立 subagent）
- 10 个标准场景配置
- 六部 × 四司详细职能定义
- Apache-2.0 License
