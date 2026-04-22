# 设置存储后端 · GitHub / Google Drive / Notion

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Life OS 支持三个存储后端，选 1、2 或 3 个。选几个决定了你愿意为"持久化 + 多设备"付出多少设置成本。

权威源：`references/data-model.md`（多后端规则 + 冲突解决）、`references/adapter-github.md`、`references/adapter-gdrive.md`、`references/adapter-notion.md`。

---

## 三个后端的定位

| 后端 | 最适合 | 格式 | 典型用户 |
|------|--------|------|---------|
| **GitHub** | 技术用户、Claude Code 用户 | `.md + YAML front matter` | 会用 git、有 GitHub 账号、想要完整版本历史 |
| **Google Drive** | 普通用户、零配置 | `.md + YAML front matter`（和 GitHub 一样） | 不想学 git、已经用 Drive 存所有东西 |
| **Notion** | Notion 重度用户 | Notion 数据库 | 工作流已经锚定 Notion、要在手机上浏览决策 |

GitHub 和 Google Drive 文件格式**完全一样**。从 GitHub 导出到 Drive 是 copy-paste，不需转换。

Notion 格式不一样 — 是数据库和属性。迁出 Notion 需要导出 + 转换。

---

## 1 个后端 vs 2 个 vs 3 个

### 只选 1 个

推荐组合：

- **GitHub only** — 最干净。技术用户默认选这个。
- **GDrive only** — 新手友好。不需要 git 知识。
- **Notion only** — 你的所有工作流都在 Notion，希望决策也在那里。

缺点：没有跨设备冗余。GitHub 挂了你当会话得不到数据。

### 选 2 个

常见组合：

- **GitHub + Notion** — 技术用户 + 手机浏览。GitHub 是主，Notion 是传输层（4 个组件）给手机用。**最推荐**。
- **GDrive + Notion** — 非技术用户 + 手机浏览。
- **GitHub + GDrive** — 想要 GitHub 的历史，同时让家里非技术的人也能看。

### 选 3 个

- **GitHub + GDrive + Notion** — 最大冗余。所有东西三份。
- 代价：每次会话结束写三份，任何一份挂了要处理降级。
- 适合：极度依赖 Life OS、无法容忍数据丢失的用户。

---

## 多后端的优先级规则

当选了多个后端，系统自动决定谁是"主"谁是"同步"：

**自动选择规则**：`GitHub > Google Drive > Notion`

| 配置 | Primary（读+写） | Sync（只写） |
|------|-----------------|-------------|
| GitHub only | GitHub | — |
| GDrive only | GDrive | — |
| Notion only | Notion | — |
| GitHub + Notion | GitHub | Notion |
| GitHub + GDrive | GitHub | GDrive |
| GDrive + Notion | GDrive | Notion |
| 三个都选 | GitHub | GDrive + Notion |

"主"是读写的权威源。"同步"只接受写入 — 读取总是从主读。

为什么这么排：GitHub 有版本历史和最干净的 diff；GDrive 次之；Notion 数据格式最封闭。

---

## 第一次设置流程

### 路径 A · GitHub

1. 在 GitHub 创建一个叫 `second-brain`（或任何名字）的 private repo。
2. 本地 clone 到 `~/second-brain`。
3. 首次上朝：RETROSPECTIVE 进入 FIRST-RUN 模式，问你存哪里。选 "a) GitHub"。
4. 系统在你的 repo 里创建标准目录（`_meta/`、`projects/`、`areas/`、`wiki/`、`inbox/`、`archive/`、`templates/`）。
5. 写 `_meta/config.md` 记录选的后端。
6. 首次 commit + push。

之后每次上朝自动 `git pull`，每次退朝自动 `git commit + push`。

### 路径 B · Google Drive

1. 在 Drive 创建一个叫 `second-brain` 的文件夹。
2. 配置 Google Drive MCP（见 `docs/installation.md`）。
3. 首次上朝：选 "b) GDrive"。
4. 系统在 Drive 里创建标准目录。
5. 写 `_meta/config.md`。

同步依赖 Drive 的 `modifiedTime` 字段。没有 git 那样的精细 diff，但有 Drive 自己的版本历史可以恢复。

### 路径 C · Notion

1. 配置 Notion MCP。
2. 首次上朝：选 "c) Notion"。
3. 系统创建 6 个数据库（🤔 Decisions、✅ Tasks、📓 Journal、📚 Wiki、🎯 Projects、🌊 Areas）。或者用模板。
4. 写 `_meta/config.md`（本地存一份，保证 session 间能读到配置）。

完整后端模式下 Notion 存所有东西。传输模式下只用 4 个组件。两者区别在 `docs/user-guide/storage-and-sync/notion-as-transport.md`。

### 组合路径（多后端）

在 FIRST-RUN 时可以多选。例如选 "a + c" → GitHub primary + Notion sync。系统会：

1. 在 GitHub 建目录。
2. 在 Notion 建 4 个传输层组件（Inbox / Status / Working Memory / Todo Board）。
3. `_meta/config.md` 记录 `backends: [github: primary, notion: sync]`。

---

## 冲突解决 · last-write-wins + timestamp

你在手机上改了一条，桌面 2 分钟后也改了同一条 — 怎么办？

### 规则

| 情况 | 处理 |
|------|------|
| 只有一个后端改了 | 采用那个后端的版本 |
| 两个后端都改了，时间差 > 1 分钟 | `last_modified` 新的赢（last write wins） |
| 两个后端都改了，时间差 ≤ 1 分钟 | **CONFLICT**：保留两个版本，ROUTER 让用户选 |
| 用户选了其中一个 | 赢家推送到所有后端 |

### 为什么选 last-write-wins

简单 + 可预测 + 99% 情况下够用。真正同时改一个文件的情况极罕见（两台设备上你都在线 + 都在改同一个决策 + 在 1 分钟内）。出现了就问你。

### 时间戳精度

所有时间戳精确到秒。YAML front matter 里的 `last_modified` 字段是 ISO 8601 带时区：

```yaml
last_modified: "2026-04-08T15:30:00+09:00"
```

东京时间 15:30。比旧金山同一时刻的 23:30（前一天）晚。时区信息不丢。

### .merge-lock 机制

多个会话同时上朝可能同时合并 outbox。为了防止互相覆盖：

- 合并 outbox 前写 `_meta/.merge-lock`。
- 合并完删掉。
- 上朝时看到 `.merge-lock` 存在且 < 5 分钟 → 跳过合并（假定另一个会话在做）。
- > 5 分钟 → 视为 stale 锁，清掉并自己合并。

详见 `sync-protocol.md`。

---

## 删除不跨后端同步

这是**故意的**设计。

你在手机上删了一个 todo。桌面 primary backend 还有。下次上朝：

- ROUTER 问："手机上删了『去买牛奶』。是要从所有后端删吗？"
- 你选**是** → 所有后端硬删。
- 你选**否** → 手机上那条恢复回来。

为什么这样：删除是破坏性操作。多设备场景下不小心删掉数据比重复危险。加一道确认比不加安全得多。

---

## 后端不可用时

任何后端挂掉都不阻塞会话：

| 情况 | 处理 |
|------|------|
| Primary 不可用 | 临时提升下一个可用 backend 为 primary，晨报标注 "⚠️ primary backend unavailable" |
| Sync backend 不可用 | 标⚠️，记录到 `_meta/sync-log.md`，下次会话自动重试 |
| 所有后端都不可用 | 正常跑会话，输出显示在对话里，不持久化 |

降级规则的好处：你在飞机上 / 没 WiFi / Notion 挂了 — Life OS 依然能用。

---

## 切换后端

### 加一个

说"加 Notion 作为同步后端"。ROUTER 问："要把现有数据从 GitHub 同步到 Notion 吗？"你同意 → 一次性把所有数据推过去 → 更新 config。

### 删一个

说"不再同步到 Notion"。ROUTER 问："保留 Notion 上的数据还是清理？"

- 保留 → 只更新 config，Notion 数据冻结在那里。
- 清理 → 软删除所有 Notion 条目。

### 换 primary

比如 GDrive → GitHub。两步：

1. 创建 GitHub repo，配置好。
2. 告诉系统"把主后端切到 GitHub"。系统把 GDrive 数据复制到 GitHub，更新 config 里的 role。

不会自动做这些破坏性操作 — 永远先问你。
