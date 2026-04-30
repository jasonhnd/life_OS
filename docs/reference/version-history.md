# 版本历史（Version History）

完整变更日志见根目录 [CHANGELOG.md](/CHANGELOG.md)（三语版本：[中文](/i18n/zh/CHANGELOG.md) · [日本語](/i18n/ja/CHANGELOG.md)）。

本文件提供版本命名约定、主要版本汇总和破坏性变更迁移说明。

---

## 版本命名约定

Life OS 遵循 **Strict SemVer**（严格语义化版本）：

```
MAJOR.MINOR.PATCH[子版本字母]
```

| 段位 | 何时递增 |
|------|---------|
| **MAJOR** | 破坏性变更（Breaking Change）——会导致现有数据或工作流无法继续运行 |
| **MINOR** | 新增功能——向后兼容的增强 |
| **PATCH** | 修复和维护——不改变功能 |
| **子版本字母** | 同一天内的补丁（a, b, c...），合并到一次发布 |

同一天的变更合并为一次发布。每次发布都打 git tag。

---

## 主要版本汇总

### v1.0.0 · 首次发布（2026-04-03）

三省六部制个人内阁系统初版：
- 多个角色：丞相 + 三省 + 六部 + 御史台 + 谏官 + 政事堂 + 早朝官 + 翰林院
- Lite 模式（单上下文）+ Pro 模式（14 个独立 subagent）
- 10 个标准场景配置
- 六部 × 四司 职能详解
- Apache-2.0 License

### v1.1.0 · 文档 + 研究可见 + 记忆层（2026-04-04）

- 7 平台安装指南
- 多个 agent 全部显示 🔎/💭/🎯 研究过程
- 谏官 21 项观察能力（认知偏差检测、情绪感知、行为追踪、决策质量评估）
- 丞相意图澄清（升级前 2-3 轮对话）
- 早朝仪表盘（DTR / ACR / OFR + 4 项周指标）
- 12 个标准场景配置

### v1.1.1 · 数据层转移（2026-04-05）

GitHub second-brain 取代 Notion 成为主数据库：
- GitHub 作为主存储（.md + front matter，融合 GTD + PARA + Zettelkasten）
- Notion 下位为移动端 inbox
- 早朝官三模式（整理/复盘/收尾）
- 会话项目绑定（每次会话锁定到一个 project/area）

### v1.2.0 · 国际化 + 架构整合（2026-04-08）

- 全部 34 个文件翻译为英文（为权威版），附完整中日译本
- **pro/GLOBAL.md**：跨 多个 agent 的共享规则
- 认知管道：5 阶段信息流
- 御史台审计模式（第二种操作模式，除决策审查外加入巡检）
- 四步知识提取训练

**🔴 破坏性变更**：second-brain 目录重构 `zettelkasten/` → `wiki/`、`records/` → `_meta/journal/`，新增 `_meta/` 系统元数据层。**迁移**：旧仓库需要手动重命名目录并移动文件。

### v1.3.0 · 三平台 Pro 模式 + 存储抽象层（2026-04-10）

- 存储抽象层：1 套标准数据模型（6 类型 + 7 操作）+ 3 可选后端（GitHub / GDrive / Notion）
- 跨平台 Pro 模式：CLAUDE.md（Claude Code）/ GEMINI.md（Gemini CLI）/ AGENTS.md（Codex CLI）
- 触发词标准化（英/中/日）

### v1.4.0 · 人类智慧殿堂 + 三省深化 + 单一真相源（2026-04-12）

- 翰林院演化为 **人类智慧殿堂**：18 领域，70+ 思想家，三种对话模式（单独深谈、圆桌、辩论）
- 门下省从橡皮图章变为真正的最后防线（10/10/10 后悔测试、红队审查、结构化 Veto 格式）
- 政事堂从模糊触发变为量化规则 + 结构化辩论
- 尚书省从任务分配变为智能调度（依赖检测、咨询机制）
- 丞相意图澄清的五类策略
- 谏官从观察到学习（行为模式学习闭环、跨会话趋势分析、正向强化）
- **架构修复**：`projects/{project}/index.md` 作为单一真相源，`_meta/STATUS.md` 从中编译

### v1.4.1 · SOUL + DREAM（2026-04-12）

系统开始学习"你是谁"：
- **SOUL.md**——用户人格档案（从零生长、基于证据、四种来源）
- **DREAM**——AI 睡眠周期（N1-N2 整理、N3 巩固、REM 创造性关联）
- 新增参考文件：`references/soul-spec.md`、`references/dream-spec.md`

### v1.4.2 · Outbox 并行会话（2026-04-12）

多会话并行无冲突：
- 每个会话写入独立 outbox 目录（`_meta/outbox/{session_id}/`）
- 合并在下次 Start Court 进行
- Session-id 格式：`{platform}-{YYYYMMDD}-{HHMM}`
- 零冲突保证

### v1.4.3–1.4.3e · Wiki 激活 + 版本自检 + 知识提取重构（2026-04-13）

- **Wiki 激活**：wiki/ 从空目录变成主动知识参与者（DREAM 写、早朝官编译 INDEX、丞相读、门下省检查、御史台审计）
- **Wiki 首次初始化引导**（1.4.3a）
- **Wiki 遗留迁移**（1.4.3a）
- **SOUL bootstrapping**（1.4.3a）
- **Adjourn 知识提取**（1.4.3b）——不再完全依赖 DREAM
- **版本自检移入 SKILL.md**（1.4.3c）——解决 bootstrap 悖论
- **版本检查作为输出格式字段**（1.4.3d）
- **SKILL.md 精简**（1.4.3e）——从 384 行压缩到 93 行，移除 Lite 模式（单上下文模拟违背 Life OS 核心价值）

### v1.4.4 · 起居郎专司收尾（2026-04-14）

- 早朝官拆分为两个角色：早朝官（会话开始，读）+ 起居郎（会话结束，写）
- DREAM 合并进起居郎（不再是独立 agent）
- 起居郎 4 阶段：归档 → 知识提取 → DREAM → 同步
- **15 角色 → 16 角色**

### v1.4.4a–b · 三层强制执行 + 防时间戳捏造（2026-04-15）

- `MUST read pro/agents/X.md and launch as subagent. HARD RULE.`
- Session-id 必须用真实 date 命令输出，不许捏造

### v1.5.0 · 战略地图（2026-04-15）

从项目助手变成生活战略师：
- **战略线**（Strategic Lines）——按战略目的分组项目
- **流动图**（Flow Graph）——定义项目间流动（cognition / resource / decision / trust）
- **叙事健康评估**——不再是"6/10 🟡" 数字评分，而是匹配健康原型 + 写叙事
- 基于认知科学研究：Goal Systems Theory、Recognition-Primed Decision、Predictive Coding、Expected Value of Control、Biased Competition
- 新增 `references/strategic-map-spec.md`

### v1.6.0 · 主题引擎（2026-04-15）

一个引擎，多种文化：
- 引擎 + 主题 + 本地化三层架构
- **多个 agent 文件 → 16 个**（i18n 去重）
- 主题文件 ~60 行定义角色映射、语气、触发词
- 3 个初始主题：zh-classical、ja-kasumigaseki、en-csuite

### v1.6.1 · 九个主题（2026-04-16）

每种语言都有三种风格：
- 英文：Roman Republic / US Government / Corporate
- 中文：三省六部 / 中国政府 / 公司部门
- 日文：明治政府 / 霞が関 / 企業
- 触发词自动推断更智能

### v1.6.2 · 三重加固（2026-04-17）

三个方向的关键加固：
- **Adjourn 三层防御**——HARD RULE 措辞 + 状态机 + 强制启动模板
- **Wiki 自动写入**——6 条严格标准 + 隐私过滤器，不再询问用户确认
- **SOUL 自动写入 + 持续运行**——ADVISOR 每次决策自动更新，3 层引用策略（core/2/3）
- **DREAM 10 个自动触发动作**——每个都有硬阈值 + 软信号 + 24h 反垃圾
- **SOUL 快照机制**——趋势箭头（↗↘→）

### v1.6.2a · Notion 同步移回主上下文（2026-04-19）

修复：archiver subagent 报告 "Notion MCP not connected"，因为 Notion MCP 工具是环境特定的、在 subagent 中不可用。
- archiver Phase 4 缩减为仅 git
- Notion 同步移出 archiver，由主上下文（编排器）执行
- 新增 Step 10a：archiver 返回后主上下文执行 Notion 同步

---

## 破坏性变更迁移说明

### v1.2.0 迁移

**第二大脑目录重构**：
- `zettelkasten/` → `wiki/`
- `records/` → `_meta/journal/`
- 新增 `_meta/` 系统元数据层

迁移步骤：
1. 手动重命名 `zettelkasten/` 为 `wiki/`
2. 把 `records/` 的内容移到 `_meta/journal/`
3. 创建 `_meta/` 下的子目录（`decisions/`、`outbox/`、`snapshots/` 等）
4. 旧文件的 wikilink 可能断——手动修复或用 Obsidian 的重命名功能

### v1.4.4 迁移

**起居郎拆分**——如果你有自定义 agent 文件，`qiju.md`（旧：早朝官合集）被拆为 `zaochao.md`（早朝官）+ `qiju.md`（起居郎）。标准模板用户无需操作。

### v1.6.0 迁移

**v1.6.0 当时的 agent 文件重命名（v1.6.0 时为 16 个，至 v1.8.0 增至 23 个）**：
- 中文拼音（`chengxiang.md`、`zhongshu.md`...）→ 功能英文（`router.md`、`planner.md`...）
- `departments.md` → `domains.md`（六部 → 六领域）

若你的 second-brain 中有引用旧 agent 路径的文件，需要手动更新。标准 Life OS 用户无需操作（重命名在 repo 层完成）。

### v1.6.2 迁移

**Wiki / SOUL 从"询问确认"改为"自动写入"**——不需要用户操作，既有条目继续工作。新条目从下次会话开始自动写入。首次 Start Session 会看到"no trend data yet"，直到第二次会话提供快照基线。

若要抑制某个自动写入的条目但不删除：`frontmatter: confidence: 0.0`。

---

## 如何检查当前版本

### 方法 1：查看 SKILL.md 头部

```yaml
---
name: life-os
version: "1.6.2a"       ← 当前版本
---
```

### 方法 2：命令行

```bash
# Claude Code
cat ~/.claude/skills/life_OS/SKILL.md | head -5

# Gemini CLI
cat ~/.gemini/skills/life_OS/SKILL.md | head -5

# Codex CLI
cat ~/.codex/skills/life_OS/SKILL.md | head -5
```

### 方法 3：会话开始时

每次 Start Session 的简报开头都显示：
```
🏛️ Life OS: v[local] | Latest: v[remote]
```

若 local 落后于 remote，会话会提示你升级。

---

## 如何升级

| 平台 | 命令 |
|------|------|
| **Claude Code** | `cd ~/.claude/skills/life_OS && git pull` 或说 "update" |
| **Gemini CLI / Antigravity** | `npx skills add jasonhnd/life_OS` 或说 "update" |
| **Codex CLI** | `npx skills add jasonhnd/life_OS` 或说 "update" |

会话内说 "update"（或主题等价词）→ ROUTER 自动执行当前平台的升级命令。

---

## Git Tag 约定

每个版本都打 git tag，格式为 `v{major}.{minor}.{patch}`：

```bash
git tag -l            # 列出所有 tag
git tag -l "v1.6.*"   # 列出 v1.6.x 的 tag
git show v1.6.2a      # 查看某版本的提交
```

子版本字母（a、b、c...）合并为单个 tag。例如 1.6.2、1.6.2a 是独立 tag。

---

## 完整变更日志

本文件是版本**汇总**。详细的每次变更说明（包含受影响文件、迁移说明、设计细节）请看完整 CHANGELOG.md：

- **英文**：[CHANGELOG.md](/CHANGELOG.md)
- **中文**：[i18n/zh/CHANGELOG.md](/i18n/zh/CHANGELOG.md)
- **日本語**：[i18n/ja/CHANGELOG.md](/i18n/ja/CHANGELOG.md)

三个 CHANGELOG 的版本标题对齐，内容三语一致。
