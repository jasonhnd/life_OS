# Scenario 06: Read `$cwd/projects/foo.md` → Pass-Through

**Hook chain**: pre-read-allowlist.sh PASS (allowlist: `$cwd/**`)

## Input

### PreToolUse payload
```json
{
  "tool_name": "Read",
  "tool_input": {"file_path": "<repo_root>/projects/foo.md"},
  "cwd": "<repo_root>"
}
```

## Expected hook output

### pre-read-allowlist.sh
- Exit: **0** (pass-through via allowlist)
- Stdout: empty
- Stderr: empty

## Expected violations.md diff

**No new rows.**

## Failure modes this scenario catches

- Allowlist resolution failure (cwd match miss)
- Relative-path normalization bug
- False-positive blocks breaking normal repo reads

## Manual replay

```bash
cwd=$(pwd)
echo '{"tool_name":"Read","tool_input":{"file_path":"'$cwd'/projects/foo.md"},"cwd":"'$cwd'"}' \
  | bash scripts/hooks/pre-read-allowlist.sh
# expect: exit 0, no violation
```
