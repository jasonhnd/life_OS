# Scenario 08: Arbitrary Prompt → All Hooks Silent

**Hook chain**: pre-prompt-guard.sh PASS, post-response-verify.sh PASS

Baseline scenario. A normal non-trigger prompt must produce zero hook noise.

## Input

### UserPromptSubmit payload
```json
{
  "prompt": "what's the weather in Tokyo today",
  "session_id": "eval-08",
  "cwd": "<repo_root>"
}
```

### Subsequent PostToolUse (LLM did anything — a Bash call, a Read, etc.)
```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "curl -s wttr.in/Tokyo"},
  "recent_user_message": "what's the weather in Tokyo today",
  "session_id": "eval-08",
  "cwd": "<repo_root>"
}
```

## Expected hook output

### pre-prompt-guard.sh
- Exit: **0**
- Stdout: empty (no trigger matched)
- Stderr: empty

### post-response-verify.sh
- Exit: **0**
- Stdout: empty
- Stderr: empty

## Expected violations.md diff

**No new rows.**

## Failure modes this scenario catches

- False-positive trigger match (e.g., "start of the day" hitting the `start` regex)
- Any hook emitting stdout in the no-trigger path (would inject unwanted reminder)
- Hook performance regression on the hot path (most prompts will be this scenario)

## Manual replay

```bash
cwd=$(pwd)
echo '{"prompt":"what is the weather in Tokyo today","session_id":"eval-08","cwd":"'$cwd'"}' \
  | bash scripts/hooks/pre-prompt-guard.sh
# expect: exit 0, zero stdout, zero stderr

echo '{"tool_name":"Bash","tool_input":{"command":"echo hi"},"recent_user_message":"what is the weather","session_id":"eval-08","cwd":"'$cwd'"}' \
  | bash scripts/hooks/post-response-verify.sh
# expect: exit 0, zero stdout, zero stderr
```
