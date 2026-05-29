---
spec_id: gotchas-spec.v1
description: 「pro/gotchas.md」规范 —— 项目级技术坑知识库。每条记录"踩过的坑 + 文件路径 + 修复方法"，让 ROUTER 和下游 agent 在新任务前 short-circuit 已知问题。区别于 `pro/compliance/violations.md`（流程违规）和 `meta/sessions/`（单次会话记录）。模式借鉴自 tinyhumansai/openhuman `.claude/memory.md`；lifeos 落地是 md-only，由 `memory-keeper` agent 写入。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, .claude/memory.md (259 行扁平单文件 + 主题分组)
introduced_in: v1.8.7
referenced_by:
  - pro/agents/memory-keeper.md
  - pro/agents/archiver.md (wrap-up phase 5)
  - SKILL.md (ROUTER 任务前扫描，未来版本)
---

# Gotchas 规范 v1

`pro/gotchas.md` 是 lifeos 的**项目级技术坑知识库** —— 单文件集中收纳非显然的行为、文件特定的 bug、纠正办法，让任何新会话在动手前先知道。

## 与其他知识库的定位区别

| 存储 | 记录什么 | 生命周期 |
|------|---------|---------|
| `meta/sessions/<sid>.md` | 单次会话的时间线 + 决策 | 一会话一文件，归档 |
| `pro/compliance/violations.md` | 流程违规（A1/A2/A3/B/C/D/E/F + F1-F17） | 仅追加审计日志 |
| `meta/wiki/<topic>.md` | 可复用的世界知识（"NPO 借贷无貸金業法 豁免"） | 人工策展 |
| `meta/concepts/<concept>.md` | 突触图节点（Cortex） | hippocampus 激活 |
| **`pro/gotchas.md`** | **项目技术坑 + 文件路径 + 修复** | **memory-keeper 持续提炼** |

Gotchas **不是**违规（那是 `compliance/violations.md`）。Gotchas **不是**可复用世界知识（那是 `meta/wiki/`）。Gotchas 是 **dev 内部 short-circuit 记忆**："下次碰 X，先看这里"。

## 文件位置与范围

- **路径**：`pro/gotchas.md`（单文件，dev repo 根区）
- **语言**：仅英文单语（项目内部 dev 知识库 —— 按 v1.8.7 RFC DR-03 不做三语镜像）
- **大小预算**：目标 ≤500 行；800 行软阈值触发拆分讨论
- **受众**：ROUTER + memory-keeper + 任何在已踩过区域开展重大任务的 agent

## 条目格式

每条 gotcha 是 `##` 主题分组下一个 bullet：

```markdown
## <主题 / 组件>

- **<短标题（5-10 词）>** — <行为描述>。<文件路径:行号> 适用时给出。修复：<workaround 或正确方法>。(#<引用：PR/issue/RFC>)
```

### 字段规则

| 字段 | 必需 | 备注 |
|------|------|------|
| 短标题 | ✅ | 前 5-10 词；grep 友好 |
| 行为描述 | ✅ | 什么意外 / 什么失败 / 什么非显然 |
| 文件路径:行号 | 适用时 | 用 `src/path:LN` 格式；横切性问题可省 |
| 修复 | ✅ | workaround 或 "无 workaround，升级到 X" |
| 引用 | ✅ | PR / issue / RFC / commit sha —— 必须指向持久工件 |

### 示例条目

```markdown
## archiver

- **archiver Phase 2 候选扫描遇 wiki 缺失会阻塞** — `meta/wiki/` 目录不存在时 Phase 2 卡住而不是跳过。修复：archiver 先创建目录如果缺失。(#v1.8.7-C6-task-2d)

- **archiver wrap-up phase 5（memory-keeper）v1.8.7 后必跑** — 跳过 phase 5 = 漏 gotchas 提炼。修复：archiver Mode 0 强制 phase 5 即使短会话；gotchas 表可以空但 phase 必须跑。(#RFC-v1.8.7)
```

## 捕获什么（memory-keeper 输入规则）

捕获：
- ✅ lifeos 自己的 agent / 命令 / spec 互动中的非显然行为
- ✅ 文件特定 bug 及其 workaround
- ✅ 代码库或运行时中"看起来 X 实际 Y"的意外
- ✅ 用户显式强调的严格不变量
- ✅ 跨版本迁移的坑

**不**捕获：
- ❌ 单次会话内容（用 sessions/）
- ❌ 流程违规（用 compliance/violations.md）
- ❌ 跟 lifeos 自身无关的可复用世界知识（用 meta/wiki/）
- ❌ 用户个人信息（身份级用 SOUL.md；瞬时用 sessions/）
- ❌ 已在 pro/CLAUDE.md 或其他权威源已有的内容

## 如何更新

memory-keeper agent 是 `pro/gotchas.md` 的**唯一写入者**。人工直接编辑允许但不鼓励 —— 绕过去重且可能产生不符合格式的条目。

更新流程（memory-keeper 由 archiver wrap-up phase 5 调用）：

1. memory-keeper 读取当前 `pro/gotchas.md`
2. 扫描当前 session 找新 gotcha 候选
3. 对每个候选：
   - 跟既有条目去重（短标题子串匹配）
   - 验证条目格式合规
   - 追加到对应 `##` 分组（需要时创建新分组）
4. 输出报告：N 个候选发现，M 个去重，K 个追加
5. 返回 archiver phase 5 完成信号

## 初始种子（v1.8.7 ship 要求）

按 RFC §7 退出标准，memory-keeper 在 v1.8.7 release session 首次跑必须扫描以下来源产出 ≥10 条种子：

- `_meta/rfc/v1.8.5-cleanup-and-hardening.md`
- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md`
- `_meta/rfc/v1.9-second-brain-structure-optimization.md`
- `pro/compliance/violations.md`（过滤：根因是技术性的而非纯流程的条目）

种子条目仍是 gotcha（技术性），不是流程违规。

## 去重与保留

- **去重**：短标题子串匹配 —— 新候选短标题若是既有条目的子串，合并到既有（扩展行为描述或加新文件路径）而非创建重复
- **保留**：gotchas 不自动过期。仅在底层问题在代码库永久修复**且**修复经验证后才移除
- **移除流程**：memory-keeper 标记条目为 `<!-- removed v1.X.Y: fixed in <ref> -->`（在文件中保留为注释作审计），或移到未来的 `pro/gotchas-resolved.md` 归档

## 失败模式

| 失败 | 检测 | 恢复 |
|------|------|------|
| memory-keeper 写重复条目 | AUDITOR Mode 7 M7-1（存在性检查 + 去重完整性检查） | memory-keeper 用 dedup-strict 标志重跑 |
| 条目无 `(#<ref>)` 引用 | AUDITOR Mode 7 M7-1 | memory-keeper 拒绝条目；archiver phase 5 失败 |
| 文件超 800 行 | 人工 review | 按分组拆子文件（罕见；预期最早 v1.9+ 发生） |
| 格式漂移（条目不符 schema） | AUDITOR Mode 7 M7-1 | memory-keeper 下次跑时重新格式化 |

## 相关 spec

- `pro/agents/memory-keeper.md` —— agent 定义
- `references/compliance-spec.md` —— 区分 gotchas 与 violations
- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.1 C6 —— 本 spec 起源
