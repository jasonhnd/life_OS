---
description: 立即手动触发某个 Life OS cron job（不等 schedule）
argument-hint: <job-name>，支持 reindex / daily-briefing / backup / spec-compliance / wiki-decay / archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency
allowed-tools: Bash
---

# /run-cron · 立即触发 cron job

User invoked: `/run-cron $ARGUMENTS`

## 你要做的

1. **如果 `$ARGUMENTS` 为空或为 `list` / `--list`**：

   ```bash
   bash scripts/run-cron-now.sh --list
   ```

   显示所有 10 个 v1.8.0 cron job 列表 + 每个的 schedule。

2. **如果 `$ARGUMENTS` 是 job 名**：

   ```bash
   bash scripts/run-cron-now.sh "$ARGUMENTS"
   ```

   立即跑该 job。输出 stream 给用户。

3. **报告结果**：

   - 退出码 0 → "✅ {job-name} 跑完成功"
   - 非 0 → "❌ {job-name} 失败 (exit {N})，看上面 log"

## 用法举例

```
/run-cron list                  → 列所有 cron job
/run-cron archiver-recovery     → 立即跑 archiver recovery（不等 23:30）
/run-cron spec-compliance       → 立即跑 spec compliance 报告
/run-cron daily-briefing        → 立即生成今日 briefing
```

## Backup mode note

⚠️ 这个 slash command 主要给 `/monitor` 模式用。你也可以在业务 session 里临时用，但**建议用 `/monitor` 进入运维模式后再操作 cron**。

业务 session 跑 cron 会污染你的对话上下文。

## Spec source

- `scripts/run-cron-now.sh`
- `pro/CLAUDE.md` → Session Modes → Monitor
