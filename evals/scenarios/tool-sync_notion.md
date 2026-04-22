# Tool Scenario · sync_notion

**Contract**: references/tools-spec.md §6.11 · Notion fallback sync when archiver Phase 4 MCP failed.

## User Message

```
archiver 上次 Phase 4 失败了，帮我重试一下 Notion 同步；如果没有 token 就优雅退出，别把 log 搞乱。
```

(English equivalent: "Archiver Phase 4 failed last time; please retry Notion sync. Skip gracefully if no token present — don't corrupt the log.")

## Scenario

Out-of-session retry for pending/failed Notion pushes. Reads
`_meta/notion-sync-log.md`, finds rows with status `pending` or
`failed`, then calls `NotionClient.upsert_page` for each. Per-page
try/except so one failure doesn't block the rest. Result rows are
appended back to the log with timestamps and reason strings.

Token resolution priority:
1. `--notion-token` CLI flag
2. `NOTION_TOKEN` env var
3. `[notion] token_env_var` in `~/second-brain/.life-os.toml`

No token anywhere → graceful skip (exit 2, clear message).

## Success Criteria

- [ ] No token resolved → prints "no notion token — skipping sync", exit 2, log file unchanged
- [ ] Token present + 3 pending rows + mocked successful Notion client → all 3 rows updated to `synced`, exit 0
- [ ] Token present + 3 pending + 1 mocked 429 rate-limit → 2 synced, 1 failed (with retry reason), exit 1
- [ ] Token present but auth fails (mocked 401) → exit 2, rows unchanged
- [ ] Network unreachable (mocked connection error) → exit 3, rows unchanged
- [ ] `--since 2026-04-01` only retries rows after that date
- [ ] `--retry` explicitly includes previously `failed` rows (default: only `pending`)
- [ ] Log file preserves original rows and appends result rows — never truncates
- [ ] Round-trip test: sync a row, re-run, second run finds 0 pending (idempotent)
- [ ] `--verbose` prints per-page status updates

## Input Fixture

`_meta/notion-sync-log.md` synthetic rows:

```markdown
| Date       | Life-OS ID                       | Database ID                         | Status   |
|------------|----------------------------------|-------------------------------------|----------|
| 2026-04-20 | 2026-04-20-0900-plan-ab          | 00000000-0000-0000-0000-000000000db | pending  |
| 2026-04-19 | 2026-04-19-1400-budget           | 00000000-0000-0000-0000-000000000db | failed   |
| 2026-04-15 | 2026-04-15-1000-negotiation-prep | 00000000-0000-0000-0000-000000000db | synced   |
```

(Synthetic UUIDs — not real Notion database IDs.)

Mock `NotionClient` via `sys.modules['tools.lib.notion']` injection.

## Expected Output

**No token (graceful skip):**
```
$ unset NOTION_TOKEN
$ uv run tools/sync_notion.py
no notion token — skipping sync
Exit 2
```

**Token + mocked success:**
```
$ NOTION_TOKEN=test-token uv run tools/sync_notion.py --retry --verbose
INFO: 2 candidates (1 pending, 1 failed)
INFO: 2026-04-20-0900-plan-ab → upserted (page_id=abc123)
INFO: 2026-04-19-1400-budget → upserted (page_id=def456)
2 synced, 0 failed
Exit 0
```

**Second run after success (idempotent):**
```
$ NOTION_TOKEN=test-token uv run tools/sync_notion.py
0 candidates. Exit 0
```

## Failure Modes

- Log file missing → create empty scaffold, exit 0 (no-op)
- Token resolves but config `.life-os.toml` malformed → warn, fall back to env/flag
- Mid-run interrupt (Ctrl-C) → partial updates already written to log, safe to re-run

## Linked Documents

- `references/tools-spec.md` §6.11
- `tools/sync_notion.py`
- `tools/lib/notion.py`
- `tests/test_sync_notion.py`
- `pro/agents/archiver.md` Phase 4 (primary sync path)
