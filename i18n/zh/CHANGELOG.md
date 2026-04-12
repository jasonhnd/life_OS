# 更新日志

## 版本规则

本项目遵循**严格 SemVer**：

- **MAJOR**（X.0.0）— 需要用户迁移的破坏性变更（目录结构调整、配置格式变更等）
- **MINOR**（0.X.0）— 新功能，向后兼容，用户无需任何操作
- **PATCH**（0.0.X）— Bug 修复、文档更新、i18n 同步、措辞调整

附加规则：
- 同一天的变更合并为单次发布
- 不使用 `a`/`b`/`rc` 后缀
- 每次发布均打 git tag

---

## [1.3.1] - 2026-04-12

### 变更 — 过程可见性 + 角色治理 + 维护

- **行为准则 #11 强化** — 所有 subagent 输出必须展示完整过程，强制使用 emoji 标记（🔎/💭/🎯/🔄/✅/⚠️）。禁止批量汇总、压缩摘要、省略任何步骤
- **行为准则 #14 强化** — Pro 环境必须启动真实的独立 subagent（每个角色单独 context）。绝对禁止单 context 模拟。平台不支持时必须告知用户并回退 Lite 模式
- **行为准则 #17 新增** — 只有已定义的 15 个角色，禁止创造或引用系统外历史官职（通政使司、大理寺等）
- **丞相新增信箱管理** — 朝前准备时检查、分类和汇报信箱状态
- **GLOBAL.md 研究过程升级** — emoji 标记强制，必须展示具体的 URL/文件路径，省略任何标记视为流程违规
- **早朝官 git 健康检查** — 上朝流程新增步骤 1.5：同步前检查 worktree 残留、hooksPath 断链等
- **adapter-github.md worktree 维护** — 新增仓库迁移后的预防和恢复流程
- **installation.md 故障排查扩展** — 新增搬家后 git fatal 错误的解决方案
- **ko/es 语言支持移除** — 删除韩语和西班牙语占位符，语言链接更新为仅 EN/ZH/JA
- **Git tag 清理** — 删除 13 个旧 tag，创建 5 个正确的 Strict SemVer tag
- **second-brain 模板标准化** — 所有模板改用 YAML front matter 对齐 data-model.md；新增 task.md 和 capture.md
- **second-brain 旧目录清理** — 删除 gtd/、records/、zettelkasten/、test-results/；更新 .gitignore

## [1.3.0] - 2026-04-10

### 新增 — 存储抽象层 + 跨平台 Pro Mode

**存储抽象层**
- **`references/data-model.md`** — 标准数据模型：6 种类型（Decision/Task/JournalEntry/WikiNote/Project/Area），含字段定义；7 种标准操作（Save/Update/Archive/Read/List/Search/ReadProjectContext）
- **`references/adapter-github.md`** — GitHub 后端：.md + front matter 格式，目录路径，通过 grep/glob 查询，通过 git log 检测变更
- **`references/adapter-gdrive.md`** — Google Drive 后端：相同 .md 格式，Google Drive MCP 调用，通过 modifiedTime 检测变更
- **`references/adapter-notion.md`** — Notion 后端：标准字段到 Notion 属性映射，Notion MCP 调用，通过 last_edited_time 检测变更
- **多后端支持** — 用户选择 1、2 或全部 3 个后端（GitHub/GDrive/Notion）。多后端模式：写入全部，从主后端读取（自动优先级：GitHub > GDrive > Notion）
- **跨设备同步** — 每次会话启动时全量同步：查询所有后端自上次同步以来的变更，时间戳比较，冲突处理（最后写入者优先，<1 分钟=询问用户）
- **触发词表** — 定义英文、中文、日文三种语言的触发词，覆盖 5 个动作（Start Court / Review / Adjourn Court / Quick Analysis / Court Debate）
- **Start Court / Adjourn Court** — "Start Court"= 全量同步拉取 + 朝前准备 + 早朝简报。"Adjourn Court"= 全量同步推送 + 存档

**跨平台 Pro Mode**
- **`pro/GEMINI.md`** — Gemini CLI / Antigravity 编排文件。14 个 subagent，含完整工作流状态机、信息隔离和六部并行执行
- **`pro/AGENTS.md`** — OpenAI Codex CLI 编排文件，遵循 AGENTS.md 开放标准
- **平台自动检测** — SKILL.md 自动检测运行平台并加载对应编排文件
- **模型无关映射** — 每个平台自动使用其最强可用模型。无硬编码模型名称——未来模型升级无需任何改动
- **故障排查指南** — 新增至 `docs/installation.md`，涵盖常见问题（worktree 上下文溢出、Pro Mode 未激活）

### 变更
- **SKILL.md** — "数据层"→"存储配置"，含多后端表格；Pro Mode 章节针对三个平台重写；行为准则第 14 条更新为"Pro 环境强制 Pro mode"
- **docs/installation.md** — 重新整理：Pro Mode 平台优先列出，新增 Gemini/Codex Pro Mode 章节、故障排查章节，更新 FAQ
- **README.md** — 安装表格新增 Mode 列（Pro/Lite），对应每个平台

### 设计原则

**一套 agent，三个平台。** 全部 14 个 agent 定义（`pro/agents/*.md`）和全局规则（`pro/GLOBAL.md`）共用。仅编排文件因平台而异。

## [1.2.0] - 2026-04-08

### 新增 — 国际化 + 架构整合

- **完整英文翻译** — 全部 34 个文件翻译为英文作为主版本
- **i18n 目录** — zh/（中文）、ja/（日文）完整翻译
- **README 视觉重设计** — 居中头部、shields.io 徽章、视觉层次
- **pro/GLOBAL.md** — 所有 agent 的通用规则提取为单一权威源：研究过程（🔎/💭/🎯）、进度播报（🔄/🔎/💡/✅）、上游输出防护、安全边界（4 条不可违反的硬规则）、通用反模式、模型无关声明
- **工作流状态机** — pro/CLAUDE.md 中的正式状态转换表，定义工作流步骤间的合法与非法跳转

### 变更
- **14 个 agent 文件精简** — 每个 agent 现在引用 pro/GLOBAL.md。每个文件平均精简 30%
- **认知管线模型** — 五阶段信息流：感知→捕获→关联→判断→沉淀→涌现
- **御史台巡检模式** — 在决策审查之外新增的第二种运行模式。三级触发：启动（空闲 >4 小时）、同步后、深度（每周/手动）
- **知识提取机制** — 四步训练法：用户决定→积累样本→LLM 归纳规则→定期纠偏
- **模型无关声明** — CLAUDE.md 是唯一绑定模型的文件。所有其他智能都是纯 markdown

### 🔴 破坏性变更 — 第二大脑目录结构调整

- `zettelkasten/` → `wiki/` — 更简洁的命名
- `records/journal/` → `_meta/journal/` — 系统日志移至 _meta
- 新增 `_meta/` 系统元数据层（STATUS.md、MAP.md、roles/、提取和巡检规则）
- 移除 `records/` 和 `gtd/` 目录

## [1.1.1] - 2026-04-05

### 变更 — 数据层架构 + 会话绑定

- **GitHub second-brain 替代 Notion 成为数据主库** — Notion 降级为"工作内存"（手机端同步）
- **GitHub second-brain 目录结构** — GTD + PARA + Zettelkasten 三套方法论融合
- **早朝官三种运行模式** — 家务模式（自动启动）、审视模式（用户触发）、收尾模式（流程结束后）
- **会话级项目绑定** — 每次会话确认关联的 project/area，所有读写限定在该项目范围内
- **退朝指令** — 收尾：push 到 GitHub + 刷新 Notion 内存
- **CC 环境强制 Pro mode** — 硬规则：检测到 Claude Code 时必须使用独立 subagent
- **同步机制** — git commit = Notion 更新，机械绑定
- **/save 命令** — 在任何项目 repo 工作时保存想法到 second-brain

## [1.1.0] - 2026-04-04

### 新增 — 文档 + 研究过程 + 记忆层

- **多平台安装指南**（`docs/installation.md`）— Claude Code、Claude.ai、Cursor、Gemini CLI、Codex CLI、ChatGPT、Gemini Web 等平台的详细安装步骤
- **第二大脑搭建指南**（`docs/second-brain.md`）— Notion 数据库创建教程
- **Token 消耗详解**（`docs/token-estimation.md`）— 8 种场景，月度成本估算
- **Eval 体系**（`evals/`）— 3 个测试场景、评分标准、自动化脚本
- **Notion 数据库 schema**（`references/notion-schema.md`）— 完整字段定义
- **全 14 个 agent 加入研究过程展示** — 🔎 我在查什么 / 💭 我在想什么 / 🎯 我的判断
- **谏官 21 条观察能力** — 认知偏差扫描（7种）、情绪检测（3种）、行为模式追踪（7种）、决策质量信号（7种）、正向信号（1种）
- **丞相三个思维工具** — 第一性原理、苏格拉底式提问、奥卡姆剃刀
- **丞相意图澄清流程** — 上报前 2-3 轮对话
- **丞相记忆层** — 上报前自动查询 3 个 Notion 数据源
- **早朝指标仪表盘** — 7 个指标：DTR、ACR、OFR + 4 个周度指标
- **user-patterns.md 长期记忆机制** — 行为模式档案
- **10 + 2 个标准场景配置** — 新增时间管理、家庭重大决策
- **SKILL.md 行为准则 #9-#13** — 意图澄清、朝前准备、报告展示的硬规则

### 变更
- **Agent prompts 精简** — 保留骨架，去掉脚手架
- **编排器 → 丞相** — 全仓库重命名
- **SKILL.md 开头硬指令** — "从第一条消息开始你就是丞相"

## [1.0.0] - 2026-04-03

### 新增 — 初始发布

- 15 个角色：丞相 + 三省 + 六部 + 御史台 + 谏官 + 政事堂 + 早朝官 + 翰林院
- Lite 模式（单 context）+ Pro 模式（14 独立 subagent）
- 10 个标准场景配置
- 六部 × 四司详细职能定义
- Apache-2.0 License
