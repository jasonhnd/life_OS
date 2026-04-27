---
description: 压缩对话上下文，归档低价值 turns，保留近期 + 决策内容
argument-hint: [focus 关键词，可选]
allowed-tools: Read, Write, Bash
---

# /compress · 上下文压缩

> **⚠️ Backup mode (v1.7.3.1).** 主要路径是自动触发：context > 70% 或 user 说"太长/压缩"时 ROUTER 会主动建议+执行。这个命令是给"我想精确控制"或"自动 detection 漏了"的备份。详见 `pro/CLAUDE.md` → Auto-Trigger Rules → Compress auto-suggest。

User invoked: `/compress $ARGUMENTS`

## 你要做的（按顺序）

1. **盘点当前 conversation context 用量**：估算总 turn 数 + 大致 token 数。

2. **识别可归档内容**：
   - 早于 last 5 turn 的 debug / 探索性消息
   - 与 `$ARGUMENTS` (focus 关键词) 无关的部分
   - 已被后续 turn 取代或修正的内容

3. **必须保留**：
   - last 5 turn（无条件）
   - 任何提到 SOUL / DREAM / 决策 / 长期规划的 turn
   - `$ARGUMENTS` focus 直接相关的所有 turn

4. **写 compression 档案**：
   - 创建 `_meta/compression/<sid>-compress-<timestamp>.md`
   - 内容：被归档的 turns 摘要（每条 1-2 句）+ 完整原文（可恢复）

5. **报告给用户**（必含）：

   ```
   📦 压缩完成
     原 turn 数：N
     保留：M
     归档到：_meta/compression/<file>
     释放估计：~X tokens
     保留的关键决策：[列表]
   ```

## Anti-pattern

- 不要假装压缩了 — 必须真写归档文件
- 不要丢决策记录 — SOUL / DREAM / 规划相关的 turn 永远保留
- 不要没有 focus 时全压 — 默认保守保留 last 10 turn
