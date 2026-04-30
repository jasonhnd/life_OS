# 常见问题（FAQ）

综合 FAQ，涵盖平台、存储、主题、SOUL/wiki/DREAM、Pro Mode 要求、隐私、成本。

---

## 平台问题

### Q：我应该从哪个平台开始？

推荐 **[Claude Code](https://claude.ai/code)**。它是 Life OS 开发的原始平台，也是功能最完整的——多个独立 subagent 都能真正并行运行。一条命令安装：

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

### Q：我同时用 Claude Code 和 Antigravity，它们会冲突吗？

**不会**。它们使用不同的编排文件（`pro/CLAUDE.md` vs `pro/GEMINI.md`）和不同的模型映射。同一套 `pro/agents/*.md` 文件共享。

**唯一需要注意**：把 `.claude/worktrees/` 加进 `.gitignore`，防止 Antigravity 被 Claude Code 留下的临时文件淹没上下文。

### Q：Gemini / Antigravity 在某个项目文件夹里不响应了

通常是 `.claude/worktrees/` 里的大文件（Claude Code session 残留）把 Gemini 的上下文窗口占满了。

> ⚠️ **手动恢复手册（仅限人工执行）** —— 以下命令涉及破坏性操作（`rm -rf`）。Agent 不得自动执行，必须由用户在自己终端中手动运行。GLOBAL.md 安全边界 #1 禁止 agent 未经确认执行破坏性命令。

```text
# HUMAN ONLY — DO NOT auto-execute
# 1. 删除 worktree 文件夹
rm -rf .claude/worktrees/

# 2. 把 `.claude/worktrees/` 加进 `.gitignore`（手动编辑）

# 3. 重启 Antigravity / Gemini CLI
```

### Q：搬仓库位置后 git 报 "fatal: not a git repository"

这是 Claude Code worktree 引用仍指向旧路径导致。`.claude/worktrees/` 目录里的 `.git` 文件包含硬编码的绝对路径。

> ⚠️ **手动恢复手册（仅限人工执行）** —— 以下命令涉及破坏性操作（`rm -rf`、`git config --unset`）。Agent 不得自动执行，必须由用户在自己终端中手动运行。GLOBAL.md 安全边界 #1 禁止 agent 未经确认执行破坏性命令。

```text
# HUMAN ONLY — DO NOT auto-execute
# 1. 清理 worktree
git worktree prune

# 2. 删除陈旧目录
rm -rf .claude/worktrees/

# 3. 检查破损 config —— 若指向不存在的路径，运行下面的 unset 命令
git config --get core.hooksPath
git config --unset core.hooksPath

# 4. 移除 worktree 扩展
git config --unset extensions.worktreeConfig
```

**预防**：搬仓库前（如 Dropbox → iCloud）先清理 worktree。Claude Code worktree session 结束时选 "remove" 而不是 "keep"。

### Q：Pro Mode 在 Gemini/Codex 没启动

确认你用 `npx skills add jasonhnd/life_OS` 安装且 skill 文件在正确位置：
- Gemini CLI：`~/.gemini/skills/` 或项目级 `.agents/skills/`
- Codex CLI：`~/.codex/skills/`
- Claude Code：`~/.claude/skills/`

### Q：ChatGPT、Claude.ai Web、Gemini Web 为什么不能用？

**Life OS 需要 Pro Mode**——多个独立 subagent 的真正信息隔离。单上下文平台无法做到这一点，因为所有"角色"都在同一个上下文里互相看见，失去了制衡意义。

只有支持 **独立 subagent** 的命令行工具（Claude Code、Gemini CLI、Codex CLI）才能运行 Life OS。

---

## 存储问题

### Q：可以不连 Notion 吗？

**可以**。Notion 是可选数据层。不连 Notion，所有功能正常——只是失去"移动端收件箱"和跨会话的云端同步。

### Q：三个后端该选哪个？

| 情况 | 推荐 |
|------|------|
| 懂 git、熟悉命令行 | **GitHub**（推荐） |
| 不想学 git、希望零配置 | **Google Drive** |
| 重度 Notion 用户 | **Notion**（作为完整后端） |
| 已有 GitHub，想要移动端 | **GitHub + Notion**（Notion 作传输层） |
| 混合场景 | 可同时启用三个 |

自动选择规则：`GitHub > Google Drive > Notion`，优先级高的作 primary（读+写），其余作 sync（仅写）。

### Q：多后端冲突时怎么办？

- 只有一个后端改了 → 直接采纳
- 两个后端都改了同一项，时间差 > 1 分钟 → `last_modified` 胜出
- 两个后端都改了同一项，时间差 ≤ 1 分钟 → 保留两版本，ROUTER 问用户选哪个

详见 `references/data-model.md` 的 Conflict Resolution。

### Q：多会话并行会不会打架？

**不会**。v1.4.2 引入 outbox 模式：
- 每个会话写自己独立的 `_meta/outbox/{session_id}/`
- 合并在下次 Start Court 进行
- 零冲突保证——不同目录、不同文件

可以在 Claude Code 窗口 A 处理项目 A、同时在窗口 B 处理项目 B，互不干扰。

### Q：我在 Notion 页面里直接改了东西，为什么没同步？

**在传输模式下**（Notion 只作 sync，primary 是 GitHub/GDrive），Notion **没有** Task/Decision/Journal 数据库——这些都在 GitHub/GDrive。Notion 只有 📬 Inbox、🧠 STATUS 镜像、🗄️ Archive 三个组件。

若你在 Inbox 之外的 Notion 页面直接编辑，这些变更对同步协议不可见。

**解决**：
- 移动端捕获都走 📬 Inbox
- 正文编辑都在桌面端用 Obsidian（对 GitHub）或 Drive 客户端（对 GDrive）

---

## 主题问题

### Q：9 个主题我该选哪个？

参考 [docs/reference/all-9-themes/](all-9-themes/) 下每个主题的文档。快速指南：

| 偏好 | 推荐主题 |
|------|---------|
| 中文用户，偏好古典仪式感 | 🏛️ 三省六部 |
| 中文用户，熟悉中国政府体制 | 🇨🇳 中国政府 |
| 中文用户，职场人士 | 🏢 公司部门 |
| 日文用户，偏好明治志士气质 | 🏛️ 明治政府 |
| 日文用户，熟悉霞が関 | 🏛️ 霞が関 |
| 日文用户，公司员工 | 🏢 企業 |
| 英文用户，偏好古典庄重 | 🏛️ Roman Republic |
| 英文用户，熟悉美式政府 | 🇺🇸 US Government |
| 英文用户，职场人士 | 🏢 C-Suite |

### Q：主题是每次会话切还是一次定好？

**每个会话独立**——每个对话窗口可以用不同主题。主题选择不跨会话持久化；每次新会话都重新询问或自动推断。

### Q：会话中能切换主题吗？

可以。随时说 `switch theme` / `切换主题` / `テーマ切り替え`：
1. 系统重新显示 a/b/c 菜单
2. 选择新主题 → 立即载入
3. 输出语言立即切换
4. 用新语言确认

### Q：主题影响功能吗？

**不影响**。所有主题共用同一套 engine agent 的逻辑。主题只改变：
- 显示名（"丞相" vs "Chief of Staff"）
- 语气（古典 vs 现代 vs 商务）
- 触发词（"上朝" vs "start"）
- 输出标题（"奏折" vs "Executive Brief"）

分权逻辑、审查机制、Veto 规则、六部分工——全部保持一致。

### Q：能自定义主题吗？

可以。复制现有主题文件（`themes/*.md`），修改角色映射和触发词，存为 `themes/custom-xxx.md`。主题文件通常 ~60 行，结构简单。详见 `themes/` 下任一文件的格式。

---

## SOUL / Wiki / DREAM 问题

### Q：SOUL.md 和 user-patterns.md 有什么区别？

- **user-patterns.md** 记录**你做什么**——由 ADVISOR 观察到的行为模式（"倾向于回避财务维度"）
- **SOUL.md** 记录**你是谁**——价值观、信念、身份（"风险偏好：中高"）

一个是描述性（patterns），另一个是身份（soul）。两者互相喂养：模式揭示价值观，价值观为模式提供语境。

### Q：SOUL 维度怎么自动生长？

v1.6.2 后 ADVISOR 在每次决策自动更新：
1. 对既有维度（confidence ≥ 0.3）：支持 → evidence +1；抵触 → challenges +1
2. 累积 ≥2 条证据的新模式 → 自动写入 SOUL.md，`confidence: 0.3`，`What SHOULD BE` 留空
3. 重新计算 `confidence = evidence_count / (evidence_count + 2 × challenges)`

**用户事后介入**：编辑 What SHOULD BE、删除维度、说 "undo recent SOUL" 回滚。不需要事先批准。

详见 `docs/reference/specifications/soul-spec.md`。

### Q：Wiki 什么时候写入？怎么确认质量？

v1.6.2 后 Wiki **自动写入，不询问确认**，但必须通过 **6 条严格标准**：
1. 跨项目可复用
2. 关于世界、不是关于你
3. 零个人隐私（见下一问）
4. 事实或方法
5. 多证据点（≥2 条独立）
6. 不与既有 wiki 冲突

任何一条失败 → 丢弃，不写入低质量条目。

**用户事后介入**：删除文件退役；说 "undo recent wiki" 回滚；设置 `confidence: 0.0` 抑制但不删除。

### Q：Wiki 的"零隐私过滤器"具体做什么？

每次写入前自动去除：
- 姓名（除非与结论直接相关的公众人物）
- 具体金额、账号、ID 号
- 具体公司名（除非是公开案例）
- 家人朋友引用
- 可追溯的日期+地点组合

**如果去除后结论失去意义 → 丢弃**（那不是可复用知识，而是穿着知识外衣的个人笔记）。

这保证 wiki/ 目录可以被安全分享、迁移、或让 AI 助手跨项目参考，而不泄露个人信息。

### Q：DREAM 什么时候触发？怎么不打扰我？

DREAM 在每次 Adjourn Court 时作为 ARCHIVER 的 Phase 3 运行：
- Phase 1 归档 → Phase 2 知识提取 → Phase 3 DREAM（3 阶段：N1-N2、N3、REM）→ Phase 4 同步

DREAM 不会打断你——它只在你主动说 "adjourn"（或主题等价词）时运行，且所有输出写入 `_meta/journal/{date}-dream.md`，在下次 Start Session 时才呈现给你。

若 DREAM 失败或超时 → 记录警告到 `_meta/sync-log.md`，不阻塞会话结束。

### Q：DREAM 的 10 个自动触发动作是什么？

v1.6.2 新增。REM 阶段会自动检测 10 种模式：
1. 新项目关系
2. 行为 ≠ driving_force
3. Wiki 被新证据反驳
4. SOUL 维度休眠 30+ 天
5. 跨项目知识未被使用
6. 决策疲劳
7. 价值漂移
8. 陈旧承诺（30+ 天无行动）
9. 情绪化决策
10. 重复决策

每个都有硬阈值（定量）+ 软信号（定性）+ 24h 反垃圾抑制。完整列表见 `docs/reference/specifications/dream-spec.md`。

---

## Pro Mode 要求

### Q：Pro Mode 有什么特别的？

- 每个 AI 角色都独立运行，互相看不到彼此的思考过程
- 六部可以并行工作（不排队）
- 门下省审查中书省时，真正看不到中书省是怎么想的——真独立审查
- 所有角色用该平台最强的模型（opus / gemini 2.5 pro / o3）

### Q：为什么 Life OS 需要 Pro Mode？

Life OS 的核心价值是**独立 subagent 间的制衡**。如果所有"角色"在同一个上下文里运行：
- 门下省能看到中书省的思考 → 审查失去独立性
- 御史台看到整个过程的内部细节 → 审计不客观
- 各部的结论互相影响 → 六部不再"并行独立分析"

单上下文模拟从架构上破坏了 Life OS 的本质。因此 v1.4.3e 移除了 Lite 模式。

### Q：哪些平台支持 Pro Mode？

| 平台 | 支持 |
|------|------|
| Claude Code | ✅ |
| Gemini CLI | ✅ |
| Google Antigravity | ✅（通过 Gemini 底层） |
| OpenAI Codex CLI | ✅ |
| Roo Code / Windsurf / Junie 等（支持 Agent Skills） | ✅（通过 `npx skills add`） |
| Claude.ai Web / ChatGPT / Gemini Web | ❌ 单上下文 |

---

## 隐私问题

### Q：Life OS 会把我的数据发给谁？

- **模型侧**：每次会话的输入都发给你选择的模型供应商（Anthropic / Google / OpenAI）。这些数据受各供应商的隐私政策约束
- **存储侧**：Life OS 只写入你配置的后端（GitHub 自己的 repo / Google Drive 自己的账户 / Notion 自己的 workspace）——没有任何 "Life OS 服务器"
- **分析侧**：没有——Life OS 没有遥测、没有用量追踪

### Q：Wiki 的"零隐私过滤器"是什么？

见 SOUL/Wiki/DREAM 部分。简单说：wiki/ 是被设计成**可以分享出去**的知识池，所有写入前会剥离个人可识别信息；若剥离后失去意义，就丢弃。

你的 SOUL.md、decisions/、projects/ 等则**可能包含敏感信息**——这些从不自动暴露给其他 agent 或跨项目使用。

### Q：我的 decisions/ 里有敏感信息，会不会被 wiki 抽取？

DREAM N3 阶段扫描 decisions/ 寻找可复用结论时，会应用隐私过滤器：
- 若结论一去掉个人信息就没意义 → 丢弃（不是可复用知识）
- 若结论本身就是关于世界的事实（如"日本 NPO 放贷没有貸金業法豁免"）→ 可以抽取到 wiki

你的具体决策内容永远**留在** decisions/，不会跑到 wiki/。

### Q：能完全离线使用吗？

部分可以：
- 模型调用必须联网（所有 LLM 都是云端服务）
- 但存储后端如果用 GitHub，`git commit` 可以离线；等联网时再 `git push`
- Google Drive 和 Notion 必须联网
- 读取既有 `.md` 文件（用 Obsidian）可以完全离线——Life OS 文件本身就是纯 markdown

---

## 成本问题

### Q：Life OS 贵吗？

**对 Claude Max / Pro 订阅用户**：订阅费已覆盖，无额外成本。Max $100/月 / Pro $20/月 的配额远够日常使用。

**对 API 用户**：
- 典型月度用量 ~298k tokens
- 月度成本 ~$7-9

详见 [docs/reference/token-estimation.md](token-estimation.md)。

### Q：怎么节省 Token？

策略（效果从大到小）：
1. **简单事项不开朝会** → 节省 90%+（丞相直接处理 ~1k）
2. **Express 分析** → 节省 60-75%（跳过三省，直接启动 1-2 部门）
3. **按需激活部门** → 节省 20-50%（3 部门 vs 6 部门差 2 倍）
4. **用早朝做日常复盘** → 节省 80%+（单次 ~2k，不走完整流程）
5. **限制翰林院轮数** → 每轮 +1-2k

### Q：哪个场景最贵？

- 完整流程（6 部门）+ 2 次 Veto + 政事堂辩论 → ~55k tokens → ~$1.75
- 这是理论单次最大消耗

典型月度用量中，这种极限场景只占 0-2 次。

### Q：Pro Mode 的 Opus 比 Sonnet 贵很多吗？

Pro 模式使用 Opus：
- 输入 $15 / 1M tokens（Sonnet 的 5 倍）
- 输出 $75 / 1M tokens（Sonnet 的 5 倍）

但 **Life OS 对推理质量要求高**——Opus 的深度显著优于 Sonnet，值得这个成本差。Max/Pro 订阅用户不受此影响。

---

## 其他常见问题

### Q：可以用中文之外的语言吗？

**可以**。Life OS 支持英、中、日三语。选主题时：
- 英文主题（en-roman / en-usgov / en-csuite）→ 全程英语输出
- 中文主题（zh-classical / zh-gov / zh-corp）→ 全程中文输出
- 日文主题（ja-meiji / ja-kasumigaseki / ja-corp）→ 全程日语输出

主题决定输出语言是 **HARD RULE**，不混用。你可以用任何语言提问，系统会以当前主题的语言回复。

### Q：Express 分析路径是什么？

当你的请求**不涉及决策**（只是分析、研究、规划），丞相跳过完整三省流程，直接启动 1-3 个相关部门。更快、更省 Token、对非决策任务同等质量。

详见 [docs/reference/token-estimation.md](token-estimation.md) 的场景 A2。

### Q：Morning Court / 早朝官是什么？

每次 Start Session 时自动运行的简报流程：
- 读 STATUS 全局状态
- 同步 outbox、编译 STATUS.md
- 读 SOUL.md 生成健康报告
- 读 wiki/INDEX.md
- 编译 STRATEGIC-MAP.md
- 触发轻量巡检（若 >4h 未运行）
- 输出简报

典型耗时 ~2k tokens，是一天中最划算的会话开场。

### Q：如果我不想用 SOUL / Wiki / DREAM 怎么办？

直接不创建 `SOUL.md`、不创建 `wiki/` 目录——Life OS 检测到文件不存在时会正常运行，所有角色跳过相关功能。

这些都是**可选增强层**，Life OS 的核心（三省六部决策流程）不依赖它们。

### Q：我能自己修改 agent 行为吗？

可以。每个 agent 定义在 `pro/agents/{agent-id}.md`，用 markdown 写，可读可编辑。修改后重新加载 Life OS（`/install-skill` 或 `npx skills add` 再运行一次）。

但：
- 修改 HARD RULE 会破坏制衡机制——谨慎
- 自定义不会合并到上游，升级时需要手动 rebase

---

## 找不到答案？

- **完整文档**：[docs/](/docs/)
- **安装指南**：[docs/installation.md](../installation.md)
- **系统概览**：[docs/architecture/](/docs/architecture/)
- **规范细节**：[docs/reference/specifications/](specifications/)
- **完整变更日志**：[CHANGELOG.md](/CHANGELOG.md)
- **提 Issue**：[GitHub Issues](https://github.com/jasonhnd/life_OS/issues)
