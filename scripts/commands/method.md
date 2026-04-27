---
description: 个人方法论库管理（创建 / 更新 method 候选，archiver Phase 2 来源）
argument-hint: create <name> | update <name> | list
allowed-tools: Bash, Read, Write
---

# /method · 方法论库管理

> **⚠️ Backup mode (v1.7.3.1).** 主要路径是 archiver Phase 2 退朝时自动检测 method candidate 并 create/update。这个命令是给"我想现在立刻 seed 一个具体 method"的备份。详见 `pro/CLAUDE.md` → Auto-Trigger Rules → Method auto-create。

User invoked: `/method $ARGUMENTS`

## 你要做的

1. **如果是 `list`（无子命令也按 list 处理）**：

   ```bash
   ls _meta/methods/ 2>/dev/null
   ```

   列出当前 `_meta/methods/` 下所有 method 文件，每个 1 行展示 name + 一句用途（从 frontmatter 读 description）。

2. **如果是 `create` / `update`**：

   ```bash
   python -m tools.skill_manager $ARGUMENTS
   ```

   工具历史命名 `skill_manager.py`，实际功能是 method library 管理。v1.7.3 暂未重命名以避免大规模波及。

3. **报告**：

   - `create` → "✏️ 已创建 method: \<name\>。路径：\<path\>。下次同类决策时 archiver / Cortex 会引用。"
   - `update` → "🔧 已更新 method: \<name\>。修订时间：\<timestamp\>。"
   - `list` → 表格形式：name | description | 最后修改时间 | 引用次数（grep 全 second-brain）

## Method vs Skill 区分

- **method** = 你的个人决策方法论（"接单边界判断法"、"早朝节律检查表"）
- **skill** = Claude Code 平台 skill 包（这个 lifeos repo 本身就是一个 skill）

`/method` 管前者；`/skill` 在 v1.7.3 暂未实现（无对应 CLI），后续版本若加 skill 商店再补。

## Anti-pattern

- 不要把单次决策当 method — method 必须是可复用的判断框架
- 不要 method 跟 wiki 混用 — wiki 是知识沉淀，method 是判断流程
