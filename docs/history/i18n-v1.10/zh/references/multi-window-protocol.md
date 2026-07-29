---
spec_id: multi-window-protocol.v1
description: 多个并发终端窗口共享同一 vault 的协议——outbox 认领纪律（任何条目不得在两次 session 启动后仍无决定）、按 session 声明提交范围（共享 vault 上绝不做仓库级 git add -A）、以及朝前显示中的跨窗口感知行。关闭隐含的"一个 session 独占 vault"假设（issue #3 C2）。
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - agents/retrospective.md (Mode 0 step 7 outbox merge + pre-session display)
  - agents/archiver.md (Phase 4 commit scoping)
  - references/data-model.md (§Constraints, outbox pattern)
---

# 多窗口协议 v1（Multi-Window Protocol v1）

真实使用中会有多个终端窗口并发运行在同一个 vault 上。outbox 模式（`references/data-model.md` §Constraints）已经防止了共享文件上的写冲突，但生产暴露了它未覆盖的三种失败模式：outbox 包跨多次 session 启动无人认领（"那是别的 session 的事"）、跨窗口交接彻底丢失、以及一个窗口的 commit 把另一个窗口进行中的文件一并卷走。本 spec 关闭这三者。

## Rule 1 · Outbox 认领纪律

在每次 session 启动时（retrospective Mode 0 step 7），在正常合并遍历之后：

1. 任何在本次启动中未被合并的 outbox 目录（merge-lock 被另一窗口持有、manifest 不完整、或合并出错）都是**无人认领条目（unclaimed item）**。记录其 `<sid>` + 年龄（来自 manifest 的 `adjourned` 时间戳，manifest 不可读时用目录 mtime）。
2. 年龄超过 **4 小时**的无人认领条目必须在简报中浮出：

   ```
   📮 Unclaimed outbox: <sid> (age 26h) — adopt (merge now) or archive (move to meta/outbox/.archived/)? [awaiting your decision]
   ```

3. **HARD RULE——任何条目不得在连续两次 session 启动后仍未获得明确决定。**通过在条目的 manifest 追加 `seen_by: <this-session-start-date>` 行来跟踪其存活次数。第二次看到时，简报将该条目升级到 `## 4. Today's Focus / decisions needed`——session 不得第二次把它当作"别人的事"。
4. `adopt` = 立即对该目录跑正常合并。`archive` = 移到 `meta/outbox/.archived/<sid>/`（保留，不删除——Security Boundary #1）。两种结局都是决定；跳过不是。

## Rule 2 · 提交范围声明

1. 在 session 启动时，每个 session 声明自己的**写路径**——写进 `meta/runtime/<sid>/scope.md` 的一行：

   ```
   write_scope: [meta/outbox/<sid>/, projects/<bound-project>/, meta/runtime/<sid>/]
   ```

   默认范围恰好就是 outbox 模式已经隐含的那些路径（自己的 outbox + 绑定项目 + 自己的 runtime 目录）；这条声明使其对其他窗口可 grep。
2. **提交只 stage 已声明的路径。**在共享 vault 上，session 流程（archiver Phase 4、/save、outbox-merge commit）中禁止 `git add -A` / `git add .`。按显式路径 stage：`git add meta/outbox/<sid>/ meta/methods/...`。
   - 唯一例外：session 启动的 **outbox 合并 commit**（retrospective step 7）stage 的是合并本身移动的那些具体文件——逐一列举，而不是 `-A`。
3. 若某次 commit 会 stage 到本 session 声明范围之外的文件 → 停下，列出范围外路径，询问用户。另一个窗口进行中的工作绝不能搭在一个不相关的 commit 里。

## Rule 3 · 跨窗口感知行

当工作树中存在本 session 声明范围之外的未提交更改时，朝前显示（retrospective Mode 0 / Mode 1 输出）包含一行：

```
🪟 Other work areas: N uncommitted path groups not in this session's scope (projects/other-proj/, meta/runtime/claude-.../) — not yours, do not stage.
```

机械计算：`git status --porcelain` → 剔除自身 `write_scope` 内的路径 → 将剩余路径按顶层目录分组。剩余为零 → 不输出该行（健康路径保持沉默）。

## 本 spec 不做什么

- 不引入超出既有 5 分钟 `meta/.merge-lock` 的锁——git 仍是并发兜底。
- 不建跨窗口消息总线——交接走 outbox（持久化），绝不走 `git stash`（生产证据：窗口间 stash/patch 交接曾全部丢失；stash 是单个 clone 的工作树状态，对其他窗口的流程和同步都不可见）。
- 不改动 Session Binding 规则（`hosts/CLAUDE.md`）——讨论范围仍不受限；本 spec 只约束数据写入与 staging。

## Eval 锚点

`evals/scenarios/v1.10-multi-window.md`——两个模拟 session 的脏工作树相互重叠 → 无跨窗口 staging；无人认领 outbox 在第一次启动时浮出、在第二次启动时被强制决定。
