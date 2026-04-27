---
description: 跨 session 搜索历史对话和决策（v1.8.0 pivot · 直接用 Grep tool）
argument-hint: <关键词>
allowed-tools: Read, Grep, Glob
---

# /search · 历史会话搜索 (v1.8.0 pivot)

> **v1.8.0 pivot 注解**：之前调用 `python -m tools.session_search`（SQLite FTS5），但 `tools/session_search.py` 在 v1.8.0 pivot 中被删除。Search 现在用 Grep tool 直接搜 `_meta/sessions/*.md`，没有 python 中间层。

> **Backup mode**: 主要路径是 ROUTER 在 Cortex pull-based 调度下 launch `hippocampus` subagent，结果出现在 `[COGNITIVE CONTEXT]` 块里。这个命令是给"我想精确搜某个关键词不走 Cortex"的备份。详见 `pro/CLAUDE.md` → §0.5 (Cortex pull-based)。

User invoked: `/search $ARGUMENTS`

## 你要做的

1. **用 Grep 工具直接搜**：

   ```
   Grep(pattern="$ARGUMENTS", path="_meta/sessions/", output_mode="files_with_matches", head_limit=10)
   ```

2. **对每个命中文件，Read frontmatter + 摘录命中行的上下文**：
   - session 日期 + 标题（从 frontmatter）
   - 命中行 + 前后 2 行（用 Grep 的 `-C 2`）
   - 当时是否有 SOUL 评分 / commitment / decision（看 frontmatter 的 `outcome_score` / `commitments` 字段）

3. **报告给用户**：

   ```
   🔍 找到 N 条相关 session：

     1. 📅 <date> · <title>
        命中行：<excerpt>
        当时承诺：<commitment if any>
        ⤷ 现在兑现状态：<check via Read journal/decisions>
        [Read <session_file>] 看完整

     ...
   ```

4. **如果 0 命中**：建议拓宽关键词或先 `/memory read` 看短期记忆。

## 多关键词搜索

如果用户给多个关键词（空格分隔），用 Grep 的正则 OR：
```
Grep(pattern="(关键词1|关键词2|关键词3)", ...)
```

## 中文/日文关键词

Grep 支持 Unicode。无需特殊处理。

## Anti-pattern

- 不要只读出文件名 — 必须打开 session 文件提取 commitment 和兑现状态
- 不要超过 10 条结果 — 太多反而让用户淹没
- 不要尝试调用已删除的 `tools/session_search.py`、`tools/cli.py`、`tools/rebuild_session_index.py`（部分已删，部分没用）—— 直接 Grep
