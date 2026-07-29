# 同步协议 · 会话开始 git pull、结束 git push

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Life OS 的存储是**单一 git repo**——本地工作副本（也是你的 Obsidian vault）+ 一个 GitHub remote 用于备份和跨设备同步。同步发生在两个明确的时刻 — Session Start（`git pull`）和 Session Close（`git push`）。会话中间不做同步。这是故意的设计。

权威源：`references/data-model.md`（Sync Protocol）、`references/data-layer.md`（RETROSPECTIVE Housekeeping Mode）。

---

## 为什么只在两端同步

### 不是每 N 分钟轮询

传统同步工具每几秒扫一次文件系统。这在文件数少、变化频繁的场景合适。

但 second-brain 不是那种场景：

- 一次会话可能写几十个文件。中间同步 = 写一个推一个，刷爆网络。
- 决策类文件不应该"部分状态"被其他设备看到。要么完整要么没有。
- 中间同步打乱"会话是原子单位"的心智模型。

所以 Life OS 只在 Session Start `git pull` 和 Session Close `git push` 两端同步。会话中间本地写，会话结束一次性 commit + push。

---

## Session Start · git pull

触发词：`上朝` / `start` / `begin` / `はじめる` 等。

由 RETROSPECTIVE 子代理在 Mode 0（Housekeeping）执行。同步是 18 步流程里的步骤 4-7。

### Step 4 · 读 config

读 `meta/config.md` 拿到 git remote 配置（remote URL；纯本地用法可省略）。

### Step 5 · Git 健康检查

同步前扫一眼本地状态：

- `git worktree list` 有没有 prunable entries。
- `.claude/worktrees/` 有没有残留。
- `core.hooksPath` 是否指向不存在路径。

有问题 → 报告给用户确认后再修复（不自动执行破坏性操作，见 Security Boundary #1）。

### Step 6 · git pull

`git pull`（若配置了 remote 且可达）：

1. 拉回远端自上次以来的变更（含手机经 git 写入 `inbox/` 的条目）。
2. 有冲突 → 普通的 git 合并冲突，按常规 git 流程解决（见下方）。
3. remote 不可达 → 降级为纯本地，记录 "⚠️ remote unavailable"，不阻塞。

### Step 7 · Outbox merge

扫 `meta/outbox/` 下的未合并会话目录（之前会话退朝时写的 outbox）。按时间顺序合并到主目录。详见 `parallel-sessions.md`。

---

## 冲突解决规则

两台设备在上次同步后都改了同一个文件。怎么办？

这就是**普通的 git 合并冲突**。`git pull` 时 git 会标出冲突的文件，你按平常解决 git 冲突的方式处理：编辑冲突标记选定内容、`git add`、提交。没有跨后端的特殊冲突逻辑、没有 last-write-wins 时间戳裁决。

真实场景里，两台设备在没先 pull 的情况下同时改同一个决策文件的概率极低 — 出现了 git 会拦住你，让你手动合并。

### 冲突文件长啥样

git 在冲突文件里插入标准的冲突标记：

```
<<<<<<< HEAD
score: 6.8
=======
score: 7.2
>>>>>>> origin/main
```

选定要保留的内容、删掉标记、`git add` + 提交即可。Obsidian 也能直接打开带标记的文件编辑。

---

## Session Close · git push

触发词：`退朝` / `adjourn` / `done` / `end` / `お疲れ` 等。

由 ARCHIVER 子代理执行。写入是 ARCHIVER Phase 4（Sync）的内容。

### 写入流程

```
1. 写所有输出到本地工作副本（meta/outbox/{session_id}/）
2. git add meta/outbox/{session_id}/ → commit → push 到 GitHub remote
3. push 失败（无 remote / 网络断 / 需先 pull）→ 本地 commit 已写好，记录提示，不阻塞；下次会话 pull 后再 push
```

### Outbox 模式

ARCHIVER **不直接写主目录**。先写进 outbox：

```
meta/outbox/claude-20260408-2200/
├── manifest.md         ← 会话元信息
├── decisions/          ← 本会话的决策
├── tasks/              ← 本会话的任务
├── journal/            ← 本会话的日志
├── wiki/               ← 本会话抽出的 wiki 条目
├── index-delta.md      ← projects/{project}/index.md 要改的字段
└── patterns-delta.md   ← meta/user-patterns.md 要追加的内容
```

为什么：`parallel-sessions.md` 讲得更细。核心是 — 多个会话同时写共享文件会互相踩，outbox 让每个会话只写自己的一份，合并动作原子化由下一次 Start Session 独占执行。

### git commit · 只 stage outbox

```bash
git add meta/outbox/{session_id}/
git commit -m "[life-os] session {session_id} output"
git push
```

**绝不用 `git add -A` 或 `git add .`**。那些会误加：

- `.env` 里的密钥
- `.claude/` 下的会话日志
- 各种临时文件

Life OS 永远只提交自己写的东西。

存储是单一 git repo，同步就是这个 `git push` —— archiver Phase 4 端到端做完，没有独立的传输层或编排层后处理步骤。手机端跨设备看到更新 = 在手机上 `git pull`。

---

## .merge-lock 机制详解

**问题**：两个会话同时 Start Session，同时要合并 outbox。谁先谁后？

**答案**：用 `.merge-lock` 文件做 mutex。

### 锁的写入和清理

```
Session X 开始合并 outbox：
  1. 检查 meta/.merge-lock 存在吗？
     - 不存在 → 走步骤 2
     - 存在但 > 5 分钟 → stale（上次崩溃了），清掉，走步骤 2
     - 存在且 < 5 分钟 → 跳过合并，假定另一个会话在做
  2. 写 .merge-lock：
     {
       "session_id": "claude-20260408-2200",
       "locked_at": "2026-04-08T22:00:30+09:00"
     }
  3. 合并所有 outbox 到主目录
  4. 编译 STATUS.md
  5. git commit + push
  6. 删 .merge-lock
```

### 5 分钟阈值怎么定的

- 正常合并 10-30 秒完成。
- 网络慢 / 大量 outbox → 可能 2-3 分钟。
- 极端情况下 5 分钟绰绰有余。
- 超过 5 分钟还没释放 → 高概率进程崩了，应该强制接管。

### 锁冲突发生了怎么办

Session A 在合并（写了 lock）。Session B 上朝看到 lock 跳过合并。Session B 正常跑完会话，退朝时只写自己的 outbox，不影响 A 的合并。

Session A 合并完 → 删 lock。Session B 下次再上朝时看到 lock 没了，自己触发合并（把 B 之前退朝写的 outbox 合并掉）。

整个流程 race-free，哪怕 A 和 B 完全同时触发 lock 检查也没问题（文件系统的 exclusive-create 语义保证）。

---

## 配置

```yaml
# meta/config.md
storage:
  type: git
  remote: "git@github.com:user/second-brain.git"   # 可选；纯本地用法可省略
```

跨设备同步通过普通 git remote 完成 —— 任何机器 `git clone` 后即可参与，会话开始 `git pull`、结束 `git push`。git 自身按 commit 追踪每台设备的状态，不需要 Life OS 维护各平台的同步时间戳。

---

## 降级规则

### remote 不可用

| 情况 | 处理 |
|------|------|
| GitHub remote 不可达（网络断 / 无 remote） | 本地 git 照常读写，`git push` 延后；晨报标 "⚠️ remote unavailable" |
| `git push` 被拒（远端有新提交） | 先 `git pull` 合并（可能解决冲突）再 push |
| 纯本地（从未配 remote） | 继续会话，数据持久化在本地工作副本，只是不跨设备同步 |

### 网络断了

ARCHIVER 写本地（outbox）+ `git commit` 能成功。`git push` 失败 → 记录。下次上朝：

```
Step 6 git pull 之前，RETROSPECTIVE 检查本地是否有未推送的 commits：
  - 有 → 尝试 push
  - push 成功 → 继续
  - push 失败 → 晨报"⚠️ 有 N 个本地 commits 未推送，网络问题持续"
```

---

## 同步审计

每次会话的 git commit 本身就是审计记录 —— `git log` 能看到每次退朝写了什么、何时 push。RETROSPECTIVE / AUDITOR 可读 `git log` / `git status` 检查有没有积压的未推送 commits。

```
$ git log --oneline -3
a1b2c3d [life-os] session claude-20260409-0730 output
e4f5g6h [life-os] session claude-20260408-2200 output
...
$ git status
Your branch is ahead of 'origin/main' by 1 commit.   # ← 有未推送的 commit
```

---

## 实战节奏

### 正常节奏

```
早上 上朝
  → Session Start git pull 拉取远端变更
  → 合并昨晚的 outbox（如果有）
  → 晨报
一整天 开会话、跑决策、写 wiki
  → 所有写入在本地 / outbox
夜里 退朝
  → ARCHIVER 写本会话 outbox
  → git add + commit + push
```

### 飞机模式

```
飞机起飞前 上朝（有网）→ git pull 成功
飞行中 开会话 → 所有写入本地 + outbox
落地 退朝（还没网）
  → outbox 写到本地 git，git commit 成功
  → git push 失败 → 记录
到酒店 (下次上朝)
  → Step 6 之前尝试 push pending commits → 成功
  → 继续正常流程
```

系统对无网容忍。关键是你要 Session Start + Session Close 的触发词敲对。
