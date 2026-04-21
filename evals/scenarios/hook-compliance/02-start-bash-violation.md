# Scenario 02: Start Trigger → Bash Read (CLASS_A)

**Hook chain**: pre-prompt-guard.sh → (LLM runs Bash instead of Task) → post-response-verify.sh BLOCKS

This is the COURT-START-001 regression scenario at hook level.

## Input

### UserPromptSubmit payload
```json
{
  "prompt": "上朝",
  "session_id": "eval-02",
  "cwd": "<repo_root>"
}
```

### Subsequent PostToolUse payload (non-compliant — Bash instead of Task)
```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "cat _meta/sessions/INDEX.md"},
  "recent_user_message": "上朝",
  "session_id": "eval-02",
  "cwd": "<repo_root>"
}
```

## Expected hook outputs

### pre-prompt-guard.sh
- Exit: **0**
- Stdout: `<system-reminder>` with HARD RULE

### post-response-verify.sh
- Exit: **2** (block)
- Stdout: `<system-reminder>` containing `CLASS_A`, `Task(retrospective)`, `Bash`
- Stderr: one-line diagnostic

## Expected violations.md diff

**One new row** appended to `pro/compliance/violations.md`:
```
| <ISO-8601-ts> | CLASS_A | critical | ROUTER | trigger=start expected=Task(retrospective) got=Bash | post-response-verify | open |
```

## Failure modes this scenario catches

- post-response-verify NOT blocking Bash after trigger (the exact COURT-START-001 failure)
- Missing CLASS_A row in violations.md
- False-positive block (if the test shows it blocks `Task(retrospective)` too, that's a regression)

## Manual replay

```bash
cwd=$(pwd)
echo '{"tool_name":"Bash","tool_input":{"command":"cat _meta/sessions/INDEX.md"},"recent_user_message":"上朝","session_id":"eval-02","cwd":"'$cwd'"}' \
  | bash scripts/hooks/post-response-verify.sh
# expect: exit 2, CLASS_A row added to pro/compliance/violations.md
```
