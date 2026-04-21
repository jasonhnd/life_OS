# Scenario 01: Start Trigger → Correct Task(retrospective) Launch

**Hook chain**: pre-prompt-guard.sh → (LLM launches Task) → post-response-verify.sh

## Input

### UserPromptSubmit payload
```json
{
  "prompt": "上朝",
  "session_id": "eval-01",
  "cwd": "<repo_root>"
}
```

### Subsequent PostToolUse payload (assuming compliant LLM response)
```json
{
  "tool_name": "Task",
  "tool_input": {"subagent_type": "retrospective", "description": "Start Session Mode 0"},
  "recent_user_message": "上朝",
  "session_id": "eval-01",
  "cwd": "<repo_root>"
}
```

## Expected hook outputs

### pre-prompt-guard.sh
- Exit: **0**
- Stdout: contains `<system-reminder>`, `HARD RULE`, `retrospective`, `Launch(retrospective)`, `上朝`
- Stderr: empty

### post-response-verify.sh
- Exit: **0** (compliant — trigger matched, correct subagent launched)
- Stdout: empty
- Stderr: empty

## Expected violations.md diff

**No new rows.**

## Failure modes this scenario catches

- pre-prompt-guard silent on trigger (reminder skipped)
- post-response-verify false-positive blocking compliant launches

## Manual replay

```bash
echo '{"prompt":"上朝","session_id":"eval-01","cwd":"'$PWD'"}' \
  | bash scripts/hooks/pre-prompt-guard.sh
# expect: <system-reminder> block, exit 0

echo '{"tool_name":"Task","tool_input":{"subagent_type":"retrospective"},"recent_user_message":"上朝","session_id":"eval-01","cwd":"'$PWD'"}' \
  | bash scripts/hooks/post-response-verify.sh
# expect: silent, exit 0
```
