---
title: Storage and Optional Sync
version: 1.11.0
status: current
---

# Storage and Optional Sync

Local Markdown writes are the primary persistence operation.

Git may provide version history, diffing, rollback evidence, and remote
synchronization. It is optional, and its absence does not reduce a valid
second-brain binding to Conversation-Only Mode.

## Separate actions

| Action | Effect |
|---|---|
| Save Markdown | Changes the authorized local record |
| Commit | Creates local Git history |
| Pull | Retrieves remote Git changes |
| Push | Sends local Git changes to a remote |
| Publish or export | Sends or presents content through another system |

One action does not imply another.

When Git is requested, the model should protect unrelated work, resolve the
exact repository and branch, use scoped changes, and verify the resulting local
or remote state. When Git is absent, it may use another proportionate
preservation method.
