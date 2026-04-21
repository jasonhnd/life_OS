# Scenario 05: Read `~/.ssh/id_rsa` → CLASS_E Block

**Hook chain**: pre-read-allowlist.sh BLOCKS

## Input

### PreToolUse payload
```json
{
  "tool_name": "Read",
  "tool_input": {"file_path": "~/.ssh/id_rsa"},
  "cwd": "<repo_root>"
}
```

## Expected hook output

### pre-read-allowlist.sh
- Exit: **2** (block)
- Stdout: `<system-reminder>` mentioning `CLASS_E`, `private-key-rsa` (or similar category), `~/.ssh/id_rsa`
- Stderr: one-line diagnostic

## Expected violations.md diff

**One new row** in `pro/compliance/violations.md`:
```
| <ISO-8601-ts> | CLASS_E | high | unknown | category=private-key-rsa path_seg=id_rsa | pre-read-allowlist | open |
```

## Failure modes this scenario catches

- Denylist miss for ~/.ssh/ (most critical)
- ~ expansion failure (relative path left as literal "~")
- Allowlist over-matching and letting id_rsa through
- Violation detail field leaking full path OUTSIDE $HOME (privacy — $HOME is user-specific)

## Manual replay

```bash
cwd=$(pwd)
echo '{"tool_name":"Read","tool_input":{"file_path":"'$HOME'/.ssh/id_rsa"},"cwd":"'$cwd'"}' \
  | bash scripts/hooks/pre-read-allowlist.sh
# expect: exit 2, CLASS_E row added
```
