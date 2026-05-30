# 设置存储 · git repo（本地工作副本 + GitHub remote）

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Life OS 的存储是**单一后端：一个 git repo**——本地工作副本（在硬盘上，也是你的 Obsidian vault）+ 一个 GitHub remote 用于备份和跨设备同步。没有多后端，没有 primary/sync 之分。

权威源：`references/data-model.md`、`references/adapter-github.md`。

---

## 存储的两个角色

| 角色 | 是什么 | 作用 |
|------|--------|------|
| **本地工作副本** | 硬盘上的 git repo（如 `~/second-brain`），同时是你的 Obsidian vault | 当前活跃文件系统，本地直接读写 |
| **GitHub remote** | 一个 git remote（GitHub 私有 repo） | 离线备份 + 跨设备同步通道 |

格式：`.md + YAML front matter`。纯 markdown，任何编辑器 / 任何模型都能读，不锁定任何工具。

---

## 要不要配 GitHub remote

- **配上 remote**（推荐）：有离线备份，能跨设备同步（`git pull` / `git push`）。
- **纯本地**：不配 remote 也能用，所有数据持久化在本地工作副本，只是不跨机器同步。随时可以之后再加 remote。

缺点对比：纯本地若硬盘坏了没有异地备份；配 remote 后 `git push` 即异地备份。

---

## 第一次设置流程

1. 在 GitHub 创建一个叫 `second-brain`（或任何名字）的 private repo（可选——纯本地用法可跳过）。
2. 本地建目录并 `git init`（或 `git clone` 你刚建的 repo）到 `~/second-brain`。
3. 首次上朝：RETROSPECTIVE 进入 FIRST-RUN 模式，初始化 git repo，问你要不要配 GitHub remote。
4. 系统创建标准目录（`meta/`、`projects/`、`areas/`、`wiki/`、`inbox/`、`archive/`、`templates/`）。
5. 写 `meta/config.md` 记录 git remote 配置。
6. 首次 commit（配了 remote 则 push）。

之后每次上朝自动 `git pull`，每次退朝自动 `git add + commit + push`。

---

## 同步就是普通 git

- 会话开始：`git pull`（RETROSPECTIVE）拉回远端变更。
- 会话结束：`git add + commit + push`（ARCHIVER Phase 4）推到 GitHub remote。
- 跨设备：在另一台机器 `git clone` / `git pull` 即可参与。

GitHub 自带完整版本历史和最干净的 diff，任何一次改动都可追溯、可回滚。

---

## 冲突解决 · 普通 git 合并

你在手机上改了一条，桌面 2 分钟后也改了同一条 — 怎么办？

这就是**普通的 git 合并冲突**。下次 `git pull` 时 git 会标出冲突的文件，按平常解决 git 冲突的方式处理（编辑冲突标记、`git add`、提交）。没有跨后端的特殊冲突逻辑。

真正同时改同一个文件的情况极罕见（两台设备都在改同一个决策文件、且都没先 pull）。出现了 git 会拦住你，让你手动合并。

### 时间戳精度

YAML front matter 里的 `last_modified` 字段是 ISO 8601 带时区，便于人和 DREAM 判断新旧：

```yaml
last_modified: "2026-04-08T15:30:00+09:00"
```

东京时间 15:30。比旧金山同一时刻的 23:30（前一天）晚。时区信息不丢。

### .merge-lock 机制

多个会话同时上朝可能同时合并 outbox。为了防止互相覆盖：

- 合并 outbox 前写 `meta/.merge-lock`。
- 合并完删掉。
- 上朝时看到 `.merge-lock` 存在且 < 5 分钟 → 跳过合并（假定另一个会话在做）。
- > 5 分钟 → 视为 stale 锁，清掉并自己合并。

详见 `sync-protocol.md`。

---

## 删除由 git 追踪

删除文件就是删除文件，git 像追踪任何改动一样追踪删除。

你在一台设备上删了一个 todo 文件并 push。另一台设备 `git pull` 时这个删除会同步过来。如果两边对同一文件有冲突的改动（一边删、一边改），git 会标为冲突让你裁决。

---

## remote 不可用时

不阻塞会话：

| 情况 | 处理 |
|------|------|
| GitHub remote 不可达（网络断 / 无 remote） | 本地 git 照常读写，`git push` 延后到下次会话；晨报标注 "⚠️ remote unavailable" |
| `git push` 被拒（远端有新提交） | 先 `git pull` 合并（可能解决冲突）再 push |
| 纯本地（从未配 remote） | 正常跑会话，数据持久化在本地工作副本，只是不跨设备同步 |

好处：你在飞机上 / 没 WiFi — 本地 `git commit` 照常工作，联网后再 push。

---

## 配置 / 切换 remote

### 加一个 remote

说"给 second-brain 配一个 GitHub remote"。ROUTER 引导你 `git remote add origin <url>`，首次 `git push -u origin main` 把现有数据推上去。

### 换 remote

说"把 remote 换到另一个 GitHub repo"。两步：

1. 创建新的 GitHub repo。
2. `git remote set-url origin <new-url>` → push。历史随之带过去。

### 多加一个 remote 做冗余

git 支持多个 remote（如再加一个第二托管商）。`git push` 到每个 remote 即可获得多份异地备份。这些都是普通 git 操作，不是 Life OS 特有机制。
