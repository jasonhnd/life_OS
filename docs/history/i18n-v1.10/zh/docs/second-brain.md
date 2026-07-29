# 第二大脑 — 架构与设置（v1.9）

## 核心架构

```
git 仓库 = 单一存储后端，两种角色：
  - 本地工作副本（磁盘）= 事实来源、完整记录，同时也是你的 Obsidian vault
  - GitHub 远端 = 备份 + 跨设备同步通道
CC（丞相 / 早朝官）= 编排 git pull / push
```

### 数据通道

```
桌面端：CC ↔ 本地工作副本（git）
跨设备：git pull（会话开始）/ git push（会话结束）
移动端：经 git 客户端（或同步文件夹）commit 进 inbox/，下次桌面 session 处理
```

### 同步规则

**同步就是纯 git**：会话开始（RETROSPECTIVE）`git pull`，会话结束（ARCHIVER Phase 4）`git push`。Merge 冲突就是普通的 git 冲突。

---

## Vault 目录结构（v1.9）

```
<vault root>/
│
├── inbox/                          # 📥 用户投递区（原始材料、捕获、研究笔记）
├── SOUL.md                         # 🧬 身份档案 — 价值观、原则、行为模式（保留在 root）
│
├── meta/                           # 🔧 系统元数据 — 透明，无隐藏子目录（v1.9）
│   │
│   │  ★ 第 1 类：配置（你写的）
│   ├── config.md                   # 后端配置 + migrated_to
│   ├── strategic-lines.md          # 战略主线定义
│   ├── extraction-rules.md         # 抽取规则
│   ├── lint-rules.md               # 质检规则
│   │
│   │  ★ 第 2 类：编译产物（系统给你看的）
│   ├── STATUS.md                   # 全局状态快照
│   ├── STRATEGIC-MAP.md            # 战略地图（从 project strategic 字段编译）
│   ├── MAP.md                      # 知识图谱
│   ├── sessions/INDEX.md           # session 索引（hippocampus 数据源）
│   ├── user-patterns.md            # ★ v1.9：从 vault-root 移入 meta/
│   │
│   │  ★ 第 3 类：精选内容（你和系统一起写的）
│   ├── decisions/<YYYY-MM>/<id>.md # ★ v1.9：月子目录，单一规范路径
│   ├── journal/<YYYY-MM-DD>.md     # ★ v1.9：时间轴 canonical
│   ├── methods/<name>.md           # 方法库（含 born_from_decisions 字段）
│   ├── queue/                      # ★ v1.9：从 inbox/ 重命名
│   │   ├── to-process/.gitkeep
│   │   ├── notifications.md
│   │   └── README.md
│   │
│   │  ★ 第 4 类：审计日志（系统的问责档案）
│   ├── compliance/violations.md    # 御史台违规记录
│   ├── eval-history/<YYYY-MM>/     # 审计统计
│   ├── snapshots/soul/<YYYY-MM-DD-HHMM>.md  # SOUL 历史快照
│   ├── lint-state.md
│   ├── lint-reports/
│   ├── extraction-log.md
│   │
│   │  ★ 第 5 类：运行时状态（系统的临时工作台）
│   ├── runtime/<sid>/              # audit trail（R11/R12/R13）
│   ├── outbox/                     # 离线 session 暂存
│   └── .merge-lock                 # 单文件锁（dot-prefix 仅为排序，非隐藏意图）
│
├── projects/{name}/                # 🎯 有终点的项目（含 archived，靠 frontmatter 区分）
│   ├── index.md                    # ★ v1.9：frontmatter 含 lifecycle_stage + ## Journal/Decisions 段
│   ├── tasks/                      # 行动项
│   └── research/                   # 项目专属研究
│       # decisions/ 已移到 meta/decisions/
│       # journal/ 已移到 meta/journal/
│
├── areas/                          # 🌊 长期生活领域（不强制命名）
│   ├── README.md                   # ★ v1.9：说明"推荐种子，不强制"
│   └── {name}/                     # 用户的实际 area
│
├── wiki/                           # 📚 知识档案（v1.9 不变）
│   ├── INDEX.md
│   ├── log.md
│   ├── OBSIDIAN-SETUP.md
│   ├── .templates/
│   └── {domain}/{topic}.md
│
└── templates/                      # 📋 顶级模板（v1.9 不变）
```

**v1.9 变化总览**：
- `_meta/` → `meta/`（去下划线前缀；透明性）
- `meta/inbox/` → `meta/queue/`（避免与 vault-root inbox/ 混淆）
- decisions 统一到 `meta/decisions/<YYYY-MM>/<id>.md`
- archive 用 frontmatter `lifecycle_stage: archived` 替代物理移动（projects/ 内停留）
- journal 时间轴 canonical 在 `meta/journal/<YYYY-MM-DD>.md`
- `user-patterns.md` 移入 `meta/`
- areas 不再预创建 10 个空目录

---

## 理解 `meta/` — 5 类心智模型（v1.9）

按 v1.9 RFC §3.1，`meta/` 内容分 5 大类。所有可见（无 `.system/` 隐藏层）；分类仅作文档解释，不靠目录边界表达。

| 类别 | 例子 | 谁写 | 谁读 | 保留期 |
|------|------|------|------|------|
| **配置**（你写的） | `config.md`、`strategic-lines.md`、`extraction-rules.md`、`lint-rules.md` | 人 | 各 agent | 永久 |
| **编译产物**（系统给你看的） | `STATUS.md`、`STRATEGIC-MAP.md`、`MAP.md`、`sessions/INDEX.md`、`user-patterns.md` | retrospective / archiver / advisor | 人 + ROUTER | 重生成，可丢 |
| **精选内容**（你和系统一起写的） | `decisions/`、`journal/`、`methods/`、`queue/notifications.md` | 人 + 机器协作 | 人 + 所有 agent | 永久 |
| **审计日志**（系统的问责档案） | `compliance/violations.md`、`eval-history/`、`snapshots/soul/`、`lint-reports/`、`extraction-log.md` | agent（机器） | auditor / advisor / 人偶尔 | 长期 |
| **运行时状态**（系统的临时工作台） | `runtime/<sid>/`、`outbox/`、`.merge-lock` | agent（机器） | auditor Mode 3 | 短期（30-90 天） |

**透明性原则**：lifeos 是单用户系统；系统对用户没有秘密。即使 audit trail 和 runtime 数据都可见 —— 你能 `cd meta/runtime/<sid>/` 读每一步 agent 做的事。这是有意为之（DR-1.9.1）。

---

## Areas — 推荐种子，不强制（v1.9）

v1.9 中，`areas/` 在 FIRST-RUN 不再预创建 10 个分类。你拿到的是空 `areas/` 目录 + 一份 `README.md` 列出推荐种子：

```
career     · 工作 / 事业方向
product    · 你在做的产品/项目
finance    · 收支、投资、税务、保险
health     · 身体、睡眠、营养、运动
family     · 家人、伴侣、孩子
social     · 朋友、合作者、社群
learning   · 学习计划、技能升级、个人品牌
ops        · 数字基建、生活流程、居住环境
creation   · 创作、内容、表达
spirit     · 价值观、人生方向、精神世界
```

**系统不强制任何命名**。你可以：
- 删除不适用的
- 新增自己的（`art/`、`travel/`、`spiritual-practice/`，任何名字）
- 自由重命名
- 从零开始按需扩建

lifeos 对 `areas/<name>/` 的处理只看目录是否存在，不检查名字。

---

## 核心概念

### projects/ — 有终点的事

每个项目有自己的世界：tasks、research、一份 `index.md`（含 `## Journal` 和 `## Decisions` 段，archiver 自动维护为 Dataview block + Recent 5 wikilinks fallback）。

**v1.9 变化**：项目完成时**不再** mv 到 `archive/`。改为给项目 `index.md` frontmatter 加 `lifecycle_stage: archived`。项目留在 `projects/` —— 保护所有引用它的 wikilinks。索引层（retrospective Mode 0 编译 STATUS、archiver Phase 1）按 `lifecycle_stage` 过滤默认视图隐藏 archived；Obsidian graph view 用 "archived" colorGroup 标灰。

### areas/ — 长期生活领域

无终点、无 deadline。每个 area 有 goals、tasks、notes。项目可以引用 area；area 可以衍生项目。

### wiki/ — 知识档案

替代原 zettelkasten 结构。按域组织、互相链接的笔记 + INDEX.md 入口。不绑定具体项目 —— 项目会死，知识活下来。由 DREAM 增长：早朝官从 session 分析中抽取可复用结论写入 wiki 页。**v1.9：wiki 内部不动**。

### SOUL.md — 身份档案

捕获用户的核心价值、原则、决策倾向、行为模式。被谏官和翰林院引用以提供个性化建议。**v1.9：保留在 vault 根**（高频引用 + wikilink 简洁 `[[SOUL]]` + ~50 处 spec 引用）。

### DREAM — 知识抽取

早朝官的 session-close 流程：复盘 session、抽取可复用洞察、写入 wiki/ 作为永久知识。这是临时分析变成持久知识的方式。

### decisions / methods / journal 三方互引（v1.9 Opt #8）

`meta/` 里的三类 artifact 现在有 frontmatter 字段相互连接：

```
methods            decisions          journal
   │                  │                  │
   ├── born_from_decisions → ←──┘                  │
   │                  │                  │
   │ ←── applied_methods                │
   │                  │                  │
   │                  │ ←── referenced_decisions
   │                  │                  │
   │ ←─────────────── referenced_methods
```

反向查询（如"哪些 decisions 应用了这个 method？"）用 Dataview + Recent 5 wikilinks 模式 —— 不维护反向字段。详见 `_meta/rfc/v1.9-second-brain-structure-optimization.md` §3.8。

---

## 三省六部输出去向（v1.9）

| 输出 | GitHub 路径 |
|------|------------|
| 决策备忘录（所有） | `meta/decisions/<YYYY-MM>/<id>.md`（含 type / projects / domains / applied_methods / journal_date frontmatter） |
| 行动项 | `projects/{project}/tasks/` 或 `areas/{area}/tasks/` |
| 上朝简报 | `meta/journal/<date>.md`（含 type_tags: [briefing]） |
| 御史台/谏官报告 | `meta/journal/<date>.md`（含 type_tags: [auditor] / [advisor]） |
| 研究 | `projects/{project}/research/` |
| 跨域知识 | `wiki/{domain}/{topic}.md` |
| 目标 | `areas/{area}/goals.md` |
| Session journal（session-close） | `meta/journal/<date>.md`（含 type_tags: [dream]） |
| Wiki 抽取（session-close） | `wiki/{domain}/{topic}.md`（早朝官） |
| 全局状态 | `meta/STATUS.md` |
| 用户行为模式 | `meta/user-patterns.md`（v1.9：从 vault-root 移入） |

---

## 跨设备同步（git）

没有独立的云内存层 —— 一切都以 markdown 形式存在于这一个 git 仓库里。

### 📥 inbox/

移动端和桌面端之间的投递区。在手机上，用 git 客户端（如 Working Copy）或同步到仓库的文件夹，把一条 markdown 笔记 commit 进 `inbox/`。下次桌面 session 的 `git pull` 把它拉下来，RETROSPECTIVE 处理它。

### 🧠 meta/STATUS.md

全局状态文件。早朝官在 session 关闭时覆写（作为 archive + Phase 4 `git push` 的一部分），`git pull` 后在任何设备可见。

### 📋 tasks 文件

活动任务存在 `projects/*/tasks/` 和 `areas/*/tasks/`。在任何设备上经 Obsidian / 任意编辑器在同步的工作副本上读写。

### 同步机制

会话开始：`git pull`。会话结束：`git add` + `commit` + `push`。跨设备交接就是在另一台机器上 pull；冲突编辑就是普通的 git merge 冲突。

---

## 多 repo 工作流

- **项目代码**（如 life_OS）→ 各自独立 repo
- **关于项目的思考**（决策、笔记、tasks）→ second-brain repo

同一个 CC 对话连接两个目录。`/save` 命令：写文件 → cd ~/second-brain → git commit/push → 回到项目。

---

## 从 v1.8.x 迁移到 v1.9

跑一次 `/migrate-v1.9`。工具会：

1. Pre-flight 检查（git working dir 干净、版本 ≥ v1.8.0、archive 无非项目内容）
2. 输出 per-stage dry-run 摘要
3. 用户回 `go` 后执行 8 阶段
4. 在当天 journal 追加迁移报告
5. 最终 `git commit`

迁移完成后跑 `/verify-v1.9` 验证 8 项验收。

详细 RFC：`_meta/rfc/v1.9-second-brain-structure-optimization.md`

如果你的 vault 老于 v1.8.0（v1.6 / v1.7），见 `docs/guides/cross-version-migration.md` —— v1.9 不自动 chain 跨多代迁移。

---

## 没有数据层会怎样

如果你不设置 second-brain，所有功能正常工作 —— 只是没有持久化和跨 session 记忆。
