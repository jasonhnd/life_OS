# Obsidian 集成 · second-brain 的查看层

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Life OS 的 second-brain 是纯 markdown + YAML 文件。Obsidian 可以直接把它当 vault 打开，不需要任何转换。

这是设计决策，不是巧合 — `references/data-layer.md` 明确说"Obsidian is the viewing layer"。

---

## 为什么选 Obsidian

很多工具可以打开 markdown，但 Obsidian 有 Life OS 需要的三件事：

1. **Wikilinks 原生支持**。`[[some-page]]` 自动解析为链接。Life OS 的 wiki 靠这个成网。
2. **知识图谱可视化**。你的 decisions、wiki、projects 互相引用能画成图。
3. **本地优先**。打开一个本地文件夹就开工。不需要登录账号。不需要上传数据。

其他选项（Typora、Logseq、VSCode markdown 插件）可以读文件，但没法无缝把 wikilinks 做成知识图。

---

## 设置 Obsidian vault

### 路径 A · GitHub second-brain

你的 second-brain 是 git repo，clone 在本地某处（比如 `~/second-brain`）。

1. 打开 Obsidian。
2. "Open folder as vault" → 选 `~/second-brain`。
3. 第一次打开 Obsidian 会建一个 `.obsidian/` 目录存它的配置（主题、插件等）。
4. 把 `.obsidian/` 加进 second-brain repo 的 `.gitignore` — 那是 Obsidian 自己的东西，不应该同步。

之后：

- CC 会话在终端跑，写 .md 文件。
- Obsidian 同时打开那个 vault，浏览、搜索、看图。
- 两边实时同步（Obsidian 监控文件系统）。

### 路径 B · Google Drive second-brain

GDrive 的 second-brain 没 clone 在本地。你有两个选择：

**选项 1 · 本地 Google Drive Sync**

在桌面装 Google Drive 桌面客户端。让它同步 `second-brain/` 到本地。然后用 Obsidian 打开本地副本。

风险：文件冲突。Obsidian 和 Drive 都在写时可能互相覆盖。

**选项 2 · 手动导出 → 只读浏览**

定期用 `rclone` 或 Drive 导出把 second-brain 拉到本地。Obsidian 只读模式浏览。新增内容还是走 CC 会话。

### 路径 C · Notion primary

不适用。Notion 里是数据库，不是 markdown 文件。Obsidian 打不开。

如果你想用 Obsidian → 不要选 Notion 作为 primary。选 GitHub 或 GDrive。

---

## Wikilinks 怎么用

### Life OS 已经在用

DREAM 抽 wiki 时默认用 wikilinks 风格：

```markdown
# Notion 替代品调研

Notion 有一些开源替代品，比如 [[appflowy]] 和 [[anytype]]。
但都有自己的权衡 — 详见 [[notion-vs-appflowy]]。

这个话题和 [[tool-migration-cost]] 相关。

## 结论

[[appflowy]] 对技术用户友好，[[anytype]] 对普通用户更亲和。
项目 [[../../projects/notion-migration|Notion migration 项目]] 已立项。
```

打开 Obsidian：

- `[[appflowy]]` → 点一下跳到 `wiki/tools/appflowy.md`（如果存在）。如果不存在 → Obsidian 用红色标出来，点一下创建。
- `[[../../projects/notion-migration|Notion migration 项目]]` → 跳到那个项目目录的 index.md。管道后的是显示名。

### 反向链接（Backlinks）

Obsidian 自动跟踪：如果 `wiki/tools/appflowy.md` 被多个地方引用，打开那个文件时右边栏显示所有引用者。

这对回溯特别有用 — "3 个月前我在哪个决策里提到 appflowy 来着？" 点反向链接就知道。

### Life OS 角度的规则

- 域内链用 `[[slug]]`（短形式）— Obsidian 会自动找。
- 跨域链用 `[[wiki/tools/appflowy]]` 或相对路径。
- 标题和 slug 都可以作为链接目标 — Obsidian 智能解析。

---

## 知识图谱

Obsidian 的 Graph View（快捷键 `Cmd+G`）把所有文件画成节点 + 边：

```
               [career-transition]
                     /   \
                    /     \
      [japan-visa]      [finance-runway]
            |                  |
      [wiki/visa]     [wiki/money-basics]
            |                  |
      [wiki/immigration]  [wiki/investing]
                \        /
             [wiki/life-in-tokyo]
```

看到什么：

- 孤立节点 = 没被引用的文件。可能是 inbox 里没处理掉的残留，或者 wiki 条目没被用起来。
- 密集簇 = 高活动领域。
- 桥接节点 = 跨域的关键概念。

### 实用姿势

每周开一次 Graph View：

- 看有没有孤立节点 → 清理或连接。
- 看新长出来的簇 → 这是你最近关注的重心。
- 看长期稳定的核心 → 这是你知识网的骨架。

Life OS 的 AUDITOR 也做类似检查，但肉眼看图更直观。

---

## 只读 vs 读写

### 只读用法（推荐）

Obsidian 只用来**浏览**，不用来编辑。所有写入走 CC 会话。

好处：

- 数据永远经过 Life OS 流程。格式正确、front matter 对、写到对的目录。
- 不会误改 STATUS.md（那是编译产物）。
- AUDITOR 能追踪所有变更。

### 读写用法（有风险）

你用 Obsidian 直接编辑文件。比如在 inbox 里加一条想法，或改一个决策的标题。

风险：

- **绕过 AUDITOR 巡查**。不合规的写入不会被标记。
- **手写 STATUS.md 会被 ARCHIVER 下次重编译时覆盖**。
- **把 decisions 和 wiki 当一般笔记用** — 破坏 Life OS 的数据模型。

如果你确实要直写，遵守：

1. 只改 `inbox/`、`{area}/notes/`、wiki 条目正文。
2. 不碰 `_meta/STATUS.md`、`_meta/STRATEGIC-MAP.md`、各 index.md。
3. 加新文件时记得写 YAML front matter（否则 ROUTER 读不到类型）。

### 混合模式

常见节奏：

- 90% 写入走 CC 会话（决策、任务、wiki 自动抽）。
- 10% 快速笔记在 Obsidian 里写（临时灵感、稿子草稿）。
- 批量整理用 CC 的"清理 inbox"流程。

---

## 插件推荐（都不强制）

### Calendar

左边栏展示日历。点某天看那天的所有 journal / decisions / tasks。

Life OS 的文件名约定 `{date}-{slug}.md` 和 Calendar 插件天然配合。

### Dataview

写 SQL-like 查询聚合数据。例子：

```dataview
TABLE status, priority, deadline
FROM "projects"
WHERE status = "active"
SORT deadline ASC
```

列出所有 active projects。Life OS 的 front matter 是 Dataview 的饲料。

### Tag Wrangler

统一标签命名、批量重命名。如果你的 wiki 标签乱了可以用这个救。

### Git 插件（obsidian-git）

在 Obsidian 里直接 git commit/push。**不推荐** — Life OS 的 CC 会话已经做 git，Obsidian 再 commit 会搞乱 `.merge-lock` 机制和 outbox 模式。

让 git 操作只走一个来源：CC 会话。

---

## 不推荐的用法

### 1. Obsidian Sync

Obsidian 官方有云同步服务。**不要用。** Life OS 已经有自己的同步机制（GitHub / GDrive / Notion）。加一层 Obsidian Sync 会让冲突解决变成噩梦。

### 2. 写决策的正式流程

决策要走 3D6M 或 Express — 需要 multiple agents 配合。在 Obsidian 里写一个决策文件 = 没经过任何审查。

Obsidian 只放"准备要讨论的东西"、"想要 CC 帮忙的原始材料"。正式决策永远从 CC 会话产生。

### 3. 把 `.obsidian/` 加进 git

Obsidian 配置文件夹（`.obsidian/`）包含主题、快捷键、插件状态 — 这些是你**个人的 Obsidian 偏好**，不是 Life OS 数据。

加进 `.gitignore`：

```
.obsidian/
```

不同电脑可以有不同的 Obsidian 配置。数据本身一致。

---

## 跨平台体验

### iPad / iPhone

Obsidian 有移动端。如果你的 second-brain 在本地 + iCloud Drive 同步 → 手机也能打开。

但注意：手机上编辑会让数据绕过 CC 会话，还会触发 iCloud 的同步延迟问题。**建议手机只读**。

手机上写东西的正路：Notion Inbox → 桌面 CC 下次上朝拉进来。

### Linux / Windows

Obsidian 有完整 Linux 和 Windows 版本。跨平台体验一致。

---

## 一个真实的设置

我的配置（Jason）：

```
~/life-os-data/second-brain/       ← git repo，CC 会话在这里写
  ├── .obsidian/                   ← 在 gitignore
  ├── .git/
  └── [所有 second-brain 数据]
```

Obsidian 打开 `~/life-os-data/second-brain/` 作为 vault。CC 终端 `cd` 到那里跑会话。

两边同时开。CC 写文件 → Obsidian 实时看到。我在 Obsidian 里浏览 + 用 Graph View 整理思路，再切换回终端跑决策。

配合得很好，只要记住：**写入永远走 CC**。
