# /save 命令 · 在项目 repo 里写入 second-brain

**本地备忘。不推送 GitHub。给自己看的技术参考。**

典型场景：你在项目代码仓（比如 `~/my-app`）里和 CC 讨论一个设计决策。讨论完想把决策写进 second-brain，但 CC 当前 cwd 不在 second-brain — 怎么办？

这就是 `/save` 命令的用途。

权威源：`pro/CLAUDE.md`（`/save Command` 部分）、`docs/second-brain.md`（Multi-Repo Workflow）。

---

## 什么问题

Life OS 典型配置：

```
~/my-app/              ← 项目代码 repo
  ├── .git/
  └── src/

~/life-os-data/second-brain/   ← 另一个 repo
  ├── .git/
  ├── projects/
  ├── areas/
  └── _meta/
```

两个 repo，两份 .git。

你在 `~/my-app` 里开 CC 会话写代码。突然聊到"要不要把 auth 换成 Cognito"。走完 3D6M 决策流程，产出一份纪要。

这份纪要不应该写进 `~/my-app`，应该写进 `~/life-os-data/second-brain/projects/my-app/decisions/`。

问题：

1. CC 当前 cwd 是 `~/my-app`，需要切到 second-brain。
2. 写完文件后需要在 second-brain repo 里 commit + push。
3. 做完上述所有后回到 `~/my-app` 继续写代码。

手工做 = 一堆 cd、git、cd — 容易忘 push、容易搞乱 branch。

`/save` 一个命令搞定。

---

## /save 做什么

### 完整流程

```
用户：/save

ROUTER：
  1. 识别当前讨论的决策 / 任务 / 研究。
  2. 根据 session binding 确定目标路径（projects/{project}/ 或 areas/{area}/）。
  3. 生成 .md 文件名（{date}-{slug}.md）+ YAML front matter + 正文。
  
  4. cd 到 second-brain 目录。
  5. 写入文件。
  6. git add {specific-file}
  7. git commit -m "[life-os] {brief description}"
  8. git push
  9. 如果配置了 sync backend：也写到 GDrive / Notion。
  10. cd 回原项目目录。
  
  11. 输出确认：
      ✅ Saved to second-brain/projects/my-app/decisions/2026-04-08-switch-to-cognito.md
      ✅ git push 成功
      📍 回到 ~/my-app
```

中间出错会报告具体哪一步失败，不会静默吞掉。

---

## /save vs Session Adjourn 的区别

这两个容易混。

### /save · 单个文件的即时写入

- 触发：`/save` 命令。
- 作用：写**一个东西**到 second-brain。
- 适用：会话中途产出了一个值得存档的决策 / 研究，不想等到退朝。
- 绕过：**不经过 outbox**。直接写进主目录 + commit。

### Session Adjourn · 整个会话的完整归档

- 触发：`adjourn` / `退朝` / `done` / `end`。
- 作用：整个会话的输出批量写入。
- 流程：ARCHIVER 4 阶段（Archive + Extraction + DREAM + Sync）。
- 经过：**outbox** → 下次 Start Session 合并到主目录。

### 什么时候用 /save

1. 讨论到一半，重要决策要立刻沉淀（怕忘或怕会话太长）。
2. 你会话里只想做一件事（"帮我记一下这个研究笔记"），不需要完整退朝流程。
3. 在项目 repo 里工作但要写 second-brain。

### 什么时候用 Session Adjourn

1. 正常结束一次会话。
2. 本次会话产出多个东西（决策 + 任务 + 笔记），需要整体归档。
3. 需要 DREAM 抽 wiki。
4. 需要更新 SOUL snapshot。
5. 需要同步到 Notion 让手机看到。

### 能并用吗

可以。会话中途用 `/save` 存了一个重要决策（防止丢），退朝时 ARCHIVER 继续处理剩下的东西 + DREAM + Notion sync。

但注意：`/save` 直接写主目录 = 不走 outbox = 和并行会话可能冲突。所以：

- 单会话 / 单平台：`/save` 随便用。
- 多会话 / 多平台：尽量用 Session Adjourn 的 outbox 模式，`/save` 只在必要时。

---

## 实战例子

### 例 1 · 项目 repo 里的决策

```
你（在 ~/my-app 里）：我们要不要把 auth 从 Auth0 换成 Cognito

ROUTER：[走完 3D6M 流程，产出 Summary Report]

[几轮讨论后]

你：/save

ROUTER：要保存什么？
  a) 完整决策纪要（Summary Report + 各部报告）
  b) 只保存决策结论（精简版）
  c) 其他 — 指定内容

你：a

ROUTER：
  绑定项目: my-app
  目标路径: projects/my-app/decisions/2026-04-08-switch-to-cognito.md
  
  执行...
  ✅ 写入完成
  ✅ git commit: "[life-os] decision: switch auth to cognito"
  ✅ git push 成功
  📍 回到 ~/my-app

继续讨论代码 — 我在这里。
```

### 例 2 · 快速笔记

```
你：我刚看了个 blog 讲 AppFlowy，记一下要点给 wiki：
    - AppFlowy 是 Notion 的开源替代
    - Rust 写的
    - 数据本地优先
    - 缺点：mobile app 还不成熟

你：/save

ROUTER：这看起来是知识笔记，不是决策。
  a) 放 wiki/tools/appflowy.md
  b) 放 areas/learning/notes/
  c) 放 inbox/ 让我以后处理

你：a

ROUTER：
  ✅ 写入 wiki/tools/appflowy.md
  ✅ 自动加 wikilinks: [[notion-alternatives]]
  ✅ git commit + push
  📍 回到 ~/my-app
```

### 例 3 · 失败处理

```
你：/save

ROUTER：
  目标: projects/my-app/decisions/...
  
  执行...
  ✅ 写入完成
  ❌ git push 失败：
      remote: Permission denied (publickey)
      
  文件已写入本地 second-brain repo，但没推送到远程。
  可能原因：ssh key 过期。
  
  选项：
  a) 我重试一次 push
  b) 你手动处理（cd ~/life-os-data/second-brain && git push）
  c) 暂时不管，下次 Start Session 会自动 retry pending push

你：a

ROUTER：
  [retry...]
  ❌ 还是失败
  
  建议 c — 下次上朝会 retry。现在继续工作。
```

---

## 实现层面

### cd 回去怎么做

CC 的 Bash 工具在每次调用之间**cwd 不持久化**（见 agent 系统提示）— 每个 Bash call 起始于原项目目录。

所以实现：

```bash
cd ~/life-os-data/second-brain && \
  mkdir -p projects/my-app/decisions && \
  cat > projects/my-app/decisions/{date}-{slug}.md <<EOF
{file contents}
EOF

cd ~/life-os-data/second-brain && \
  git add projects/my-app/decisions/{date}-{slug}.md && \
  git commit -m "[life-os] {msg}" && \
  git push
```

每个命令独立 cd 到目标，执行完 Bash 工具回原目录。对 CC 的体感是"切了一下又回来"。

### 绝不 git add -A

和 Session Adjourn 一样的规则。`/save` 只 stage 具体写的文件。防止误加 `.env` / 临时文件 / 其他东西。

### second-brain 路径在哪读

CC 从 `_meta/config.md` 或用户配置里知道 second-brain 的本地路径。如果是 GitHub primary → 就是本地 clone 的路径。

`/save` 不适合 GDrive primary — GDrive MCP 没有 "cd + git" 的语义。对 GDrive primary 用户，相当于 `/save` 降级为"用 GDrive MCP 上传一个文件"。

对 Notion primary — `/save` 相当于 notion-create-pages。没有 git 步骤。

---

## 一个清单

### /save 的保证

- ✅ 文件进对的目录（基于 session binding）。
- ✅ YAML front matter 完整（type / title / date / status / last_modified）。
- ✅ git commit message 符合 Life OS 规范（`[life-os]` 前缀）。
- ✅ git push 成功或明确报告失败。
- ✅ 回到原项目目录不影响后续工作。
- ✅ 所有 sync backends 都写（不止 primary）。

### /save 的限制

- ❌ 不触发 DREAM / wiki 抽取 / SOUL snapshot。
- ❌ 不编译 STATUS.md。
- ❌ 不触发 AUDITOR 巡查 / ADVISOR 观察。
- ❌ 不走 outbox — 多会话并行时可能冲突。

如果你需要完整的"结束一次会话"语义 → 用 Session Adjourn，不要用 `/save`。

`/save` 是 CRUD 级别的工具。`Adjourn` 是会话仪式。
