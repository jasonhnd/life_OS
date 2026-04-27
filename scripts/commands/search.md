---
description: 跨 session 搜索历史对话和决策（SQLite FTS5 索引）
argument-hint: <关键词>
allowed-tools: Bash, Read
---

# /search · 历史会话搜索

> **⚠️ Backup mode (v1.7.3.1).** 主要路径是 Cortex 的 hippocampus 自动调 `tools.session_search`，结果出现在 [COGNITIVE CONTEXT] 块里。这个命令是给"我想精确搜某个关键词不走 Cortex"的备份。详见 `pro/CLAUDE.md` → Auto-Trigger Rules → Search auto-trigger。

User invoked: `/search $ARGUMENTS`

## 你要做的

1. **运行 SQLite FTS5 搜索**：

   ```bash
   python -m tools.session_search --query "$ARGUMENTS" --limit 5 --json
   ```

2. **解析 JSON 结果**。对每条命中：
   - session 日期 + 标题
   - 相关度分数
   - 当时是否有 SOUL 评分 / commitment / decision

3. **报告给用户**：

   ```
   🔍 找到 N 条相关 session：

     1. 📅 <date> · <title> · 相关度 X%
        当时承诺：<commitment if any>
        ⤷ 现在兑现状态：<check via Read journal/decisions>
        [Read <session_file>] 看完整

     ...
   ```

4. **如果 0 命中**：建议拓宽关键词或先 `/memory read` 看短期记忆。

## Anti-pattern

- 不要只读出文件名 — 必须打开 session 文件提取 commitment 和兑现状态
- 不要超过 5 条结果 — 太多反而让用户淹没
- FTS5 索引缺失时（tool 报错）→ 提示用户跑 `python -m tools.rebuild_session_index` 重建
