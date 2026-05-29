# Cross-Version Migration Guide

> 当你的 lifeos vault 落后多个版本，要升级到当前版本时怎么办。
>
> v1.9.0 新增 — 因为 `/migrate-v1.9` 不再自动 chain 跨多代迁移（per DR-1.9.14 / Q-undecided-1）。

---

## 谁需要看这份指南

如果你的 vault `meta/config.md` 里 `migrated_to:` 字段是：

- `v1.9` → ✅ 已是最新，无需操作
- `v1.8.0` / `v1.8.1` / ... / `v1.8.7` → 直接跑 `/migrate-v1.9`
- `v1.7.0` / `v1.7.1` / `v1.7.2` / `v1.7.3` → **这份指南适用**
- `v1.6.x` 或更早 → **这份指南适用**
- 字段缺失 → 大概率是 v1.6 之前，**这份指南适用**

---

## 为什么不自动 chain

`/migrate-v1.9` 检测到 v1.8.0 之前的 vault 会直接中止，输出引导而不是自动 chain 跑前置迁移工具。理由（per DR-1.9.14）：

1. **复杂度爆炸**：每代迁移有自己的 schema / 流程 / git commit 期望；串起来 commit history 乱
2. **黑箱风险**：用户看不到每代迁移的 dry-run diff，全自动跑过去
3. **失败定位地狱**：中途失败时不知道是哪一代的问题
4. **真实用户分布**：主动跑 v1.9 升级的用户大概率已经在 v1.8.x；v1.6/v1.7 vault 多是僵尸

所以是设计选择 — 用户多走几步换来每代迁移可单独 review。

---

## 推荐升级路径

### 路径 A · v1.7.x → v1.8.x → v1.9.0

如果你的 vault 是 v1.7.x：

```
1. /migrate-v1.7  （如果存在该 slash 命令）
   或参考 docs/history/v1.7-migration.md 手动升级到 v1.8.0
   
2. 跑几次正常 session（验证 v1.8.x 行为正常）

3. /migrate-v1.9
```

### 路径 B · v1.6.x → v1.7.x → v1.8.x → v1.9.0

如果你的 vault 是 v1.6.x：

```
1. /migrate-from-v1.6  （已存在 slash 命令）
   把 zettelkasten 老结构 + SOUL v1 schema 升级到 v1.7+

2. 跑几次正常 session（验证 v1.7+ 行为正常）

3. 路径 A 继续
```

### 路径 C · 不知道当前版本

如果 `migrated_to:` 字段缺失或文件不存在：

```
1. 看 vault 目录结构判断：
   - 有 _meta/journal/<date>-<type>.md（按 type 命名）+ _meta/concepts/ → 是 v1.7+，走路径 A
   - 有 _meta/zettelkasten/ 或 单一 _meta/index.md → 是 v1.6 或更早，走路径 B
   - 都不像 → 不是 lifeos vault，或非常老的版本，先 git log 看历史
```

---

## 每一步的 Pre-flight 提示

每代迁移工具都应该有自己的 Pre-flight 检查：

| 检查 | 目的 |
|------|------|
| git working dir clean | 防止 batch rename 与未提交杂改混合 |
| 备份建议 | 强烈建议跑迁移前做 `cp -r ~/vault ~/vault-backup-pre-vX.Y` |
| 版本检测 | 确认当前 vault 处于该工具能升级的起点 |
| 进度文件 | 每代迁移工具应写 `meta/.migration-progress-vX.Y.md` 便于断点续传 |

---

## 失败 / 中断时怎么办

### 中途失败

每代迁移工具都应写 `meta/.migration-progress.md` 标记已完成阶段。失败时：

```
1. 读 progress 文件看到哪一步
2. git status / git diff 看当前状态
3. 选择：
   a. git reset --hard <pre-migration-commit> 完全回滚
   b. 手工修 root cause 后重跑迁移工具（应该跳过已完成阶段）
```

### 完成一代后想停下

每代迁移完成后，**强烈建议**：

```
1. 跑几次正常 session 验证行为
2. 检查 `meta/compliance/violations.md` 没有新 P0
3. 跑 auditor patrol / Mode 3 看看有没有 schema drift
4. 觉得 OK 了再开始下一代
```

跨多代连续跑容易撞到 silent corruption — 慢比快好。

---

## 当前已知存在的迁移工具

| 工具 | 起点 | 终点 | 状态 |
|------|------|------|------|
| `/migrate-from-v1.6` | v1.6.x | v1.7+ | 存在（`scripts/prompts/migrate-from-v1.6.md`） |
| `/migrate-confidence` | v1.6 confidence schema | v1.7 confidence formula | 存在（`scripts/prompts/migrate-confidence.md`） |
| `/migrate-soul-v2` | SOUL v1 | SOUL v2 (v1.8.5) | 存在 (`.claude/commands/migrate-soul-v2.md`) |
| `/migrate-wiki-v2` | wiki v1 | wiki v2 (v1.8.5) | 存在 (`.claude/commands/migrate-wiki-v2.md`) |
| `/migrate-to-wikilinks` | plain text refs | wikilinks (v1.8.0 R-1.8.0-013) | 存在（`scripts/prompts/migrate-to-wikilinks.md`） |
| `/migrate-v1.9` | v1.8.0-v1.8.7 | v1.9.0 | 存在（`scripts/prompts/migrate-v1.9.md`） |

中间代如 v1.7 → v1.8 没有显式的命名迁移工具 —— v1.8.0/v1.8.1/v1.8.5 等很多是 within-version patches，vault structure 改动小到不需要独立工具，正常 session 跑几次自动适配。

---

## 我能不能跳代

**强不推荐**。例如 v1.6.x 直接跑 `/migrate-v1.9` 会立即中止；v1.7.x 也会。

**理由**：
- 每代有自己的 schema 假设。v1.9 假设 `meta/incidents/*.yml` 存在（要转 .md）；但 v1.7.x vault 没有 incidents（v1.8.5 引入的）。如果跳代，迁移工具看到一堆缺失的预期文件，要么报错要么 silent skip
- Schema 字段是层层加上去的：`reopen_condition`（v1.8.5）、`applied_methods`（v1.9）。跳代会让中间字段缺失但又不被任何工具补
- 每代 git commit 是单代变更的 audit trail。跳代会让 git log 失去这种粒度

如果实在想跳代，承担风险：手工 commit 前手动备份整个 vault 到外部位置；跑完跨代迁移后立即 `/verify-v1.9`；任何一项 ❌ 都把 vault 整体回滚到备份。

---

## FAQ

**Q: 为什么不能一条命令 `/migrate-vault-to-latest` 自动 detect + chain？**

A: 见上面"为什么不自动 chain"。简短版：可控性 > 便利性。

**Q: 我能 fork 个 chain 工具吗？**

A: 可以，但请在本 repo fork 之外维护 —— 本 repo 的 v1.9.0 RFC § Q-undecided-1 已经决策不在主干提供 chain。

**Q: 我跑 `/migrate-from-v1.6` 但找不到这个命令怎么办？**

A: 检查 `scripts/prompts/migrate-from-v1.6.md` 是否存在。如果存在，触发它的方式是用户在 Claude Code 里说"从 v1.6 升级"或 "migrate from v1.6"（trigger keywords）；不需要 slash 命令前缀。

**Q: 如果 v1.6 vault 老到连 `meta/config.md` 都没有怎么办？**

A: 那就是 v1.6 之前（v1.0-v1.5 时代）。这些版本接近实验性，建议手工迁移：
1. 把所有 .md 文件备份
2. 跑 `/setup-secondbrain` 建立现代结构
3. 把老 .md 文件一个一个手工放到新结构合适的位置
4. 跑 `/audit-mode-3` 检查 schema

---

## 与 RFC 的关系

| RFC | 相关章节 |
|-----|---------|
| `_meta/rfc/v1.9-second-brain-structure-optimization.md` §3.4.6 | 提到本指南 |
| `_meta/rfc/v1.9-second-brain-structure-optimization.md` DR-1.9.14 | 不 chain 决策 |
| `_meta/rfc/v1.9-second-brain-structure-optimization.md` R-1.9-008 | 跨版本链路风险登记 |
