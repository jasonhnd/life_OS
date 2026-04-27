---
description: 即时记忆登记 / 读取（~/.claude/lifeos-memory/ 短期记忆库 · v1.8.0 pivot 直接读写文件）
argument-hint: emit <key>=<value> | read | remove <key> | path
allowed-tools: Read, Write, Bash, Glob
---

# /memory · 即时记忆 (v1.8.0 pivot)

> **v1.8.0 pivot 注解**：之前调用 `python -m tools.memory`，但 `tools/memory.py` 在 v1.8.0 pivot 中被删除。Memory 现在是一个扁平 KV 目录 (`~/.claude/lifeos-memory/<key>.json`)，ROUTER 直接用 Write/Read tool 读写，没有 python 中间层。

> **Backup mode**: 主要路径是 ROUTER 在 `pre-prompt-guard.sh` 检测 "记一下/提醒我/TODO/覚えて" 等关键词后自动 emit。这个命令是给"我想精确控制 key/value 格式"的备份。详见 `pro/CLAUDE.md` → Auto-Trigger Rules → Memory auto-emit。

User invoked: `/memory $ARGUMENTS`

## 数据结构

每条 memory 是 `~/.claude/lifeos-memory/<key>.json`：

```json
{
  "value": "<text>",
  "role": "礼/户/刑/工/吏/兵",
  "created": "<ISO8601>",
  "trigger_time": "<optional ISO8601 if value contains date/time>"
}
```

Key 推荐格式：`reminder:<context>` / `decision:<topic>` / `note:<context>`。

## 你要做的

### `emit <key>=<value>`

1. 解析 `key` 和 `value`
2. 推断 `role`：决策→刑、人际/学习/品牌→礼、财务→户、健康/数字基建→工、关系经营/团队→吏、项目执行→兵
3. 如果 `value` 含日期/时间 → 提取为 `trigger_time` 字段
4. 用 Write 工具创建 `~/.claude/lifeos-memory/<sanitized-key>.json`（key 中的 `:` 改为 `__`、`/` 改为 `_`）
5. 报告：

   ```
   📚 已入档案柜
     · key: <key>
     · role: <role>
     · trigger time: <if any>
     · 24h 后未完成会出现在状态行
   ```

### `read`

1. Glob `~/.claude/lifeos-memory/*.json`
2. 对每个文件 Read 内容
3. 按 `created` 倒序列出
4. 格式：
   ```
   📚 当前 memory（{N} 条）
   - <key> · <role> · <value 前 60 字>... · <created 相对时间>
   - ...
   ```

### `remove <key>`

1. Resolve sanitized path
2. `Bash: rm ~/.claude/lifeos-memory/<sanitized-key>.json`
3. 报告 "🗑️ 已删除 <key>"

### `path`

显示 `~/.claude/lifeos-memory/` 路径，`ls -1` 列出当前所有 key。

## 退朝时自动整理

退朝（archiver 流程）时，archiver 的 knowledge-extractor 会读 `~/.claude/lifeos-memory/` 评估哪些 memory 值得提升为 `wiki/`，哪些过期可删。本命令本身不参与晋升逻辑。

## 三层记忆分工

| 时长 | 位置 | 例子 |
|------|------|------|
| 即时（<48h） | `~/.claude/lifeos-memory/<key>.json` | 临时提醒、临时决策 |
| 中期（week） | `wiki/<topic>.md` | archiver 退朝时写 |
| 长期（年） | `SOUL.md` | 价值观、维度 |

## Anti-pattern

- 不要把长 narrative 塞进 memory — 长内容应该写到 wiki/
- 不要尝试调用已删除的 `tools/memory.py`（v1.8.0 pivot 删了）—— 直接 Write 文件
- 不要在 key 里用 `/` 或 `:` 之外的奇怪字符（保持文件名安全）
