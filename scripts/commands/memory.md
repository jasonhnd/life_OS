---
description: 即时记忆登记 / 读取（_meta/MEMORY.md 短期记忆库）
argument-hint: emit <key>=<value> | read | remove <key> | path
allowed-tools: Bash, Read
---

# /memory · 即时记忆

> **⚠️ Backup mode (v1.7.3.1).** 主要路径是 ROUTER 自动检测 "记一下/提醒我/TODO/覚えて" 等关键词后自动 emit。这个命令是给"我想精确控制 key/value 格式"的备份。详见 `pro/CLAUDE.md` → Auto-Trigger Rules → Memory auto-emit。

User invoked: `/memory $ARGUMENTS`

## 你要做的

1. **运行 memory tool**：

   ```bash
   python -m tools.memory $ARGUMENTS
   ```

2. **根据子命令格式化输出**：

   - `emit <key>=<value>` → 报告 "📚 已入档案柜"，附 key + 触发时间 + 关联角色（基于 key 推断：reminder/decision/insight 等）
   - `read` → 列出当前所有 memory entries（按相关度排序）
   - `remove <key>` → 报告已删除
   - `path` → 显示 _meta/MEMORY.md 路径

3. **emit 时额外**：

   - 检查 key 是否有 `reminder=` 前缀 → 自动加入今日待办
   - 检查 value 是否含日期/时间 → 标注触发时刻
   - 推断角色归属：决策→刑部、人际→礼部、财务→户部、健康→工部、学习→吏部、规划→兵部

4. **退朝时自动整理**：

   提醒用户 `_meta/MEMORY.md` 是 24-48h 短期记忆，archiver 退朝时会自动评估哪些值得提升为 `wiki/`，哪些过期。

## 三层记忆分工

| 时长 | 工具 | 例子 |
|------|------|------|
| 即时（<48h） | `/memory` | 临时提醒、临时决策 |
| 中期（week） | `wiki/` | archiver 退朝时写 |
| 长期（年） | `SOUL.md` | 价值观、维度 |

## Anti-pattern

- 不要把长 narrative 塞进 memory — 长内容应该写到 wiki/
- 不要绕过 tool 直接编辑 _meta/MEMORY.md — 失去 audit trail
