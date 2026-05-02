#!/bin/bash
# Life OS · pre-bash-approval.sh (v1.8.1 · zero-python pattern guard)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PreToolUse
# Matcher: Bash
# Exit:    0 (approve, silent) | 2 (block, stderr -> Claude visible)
# Timeout: 5s
#
# Purpose
#   Screen every Bash command against ~40 dangerous-command patterns BEFORE
#   it executes. Replaces the v1.7.x Python bridge to tools/approval.py
#   (deleted in v1.8.1 zero-python pivot).
#
# Behaviour
#   - Reads JSON from stdin (Claude Code hook protocol)
#   - Extracts tool_input.command via jq (preferred) or python3 (fallback)
#   - Lowercases command, then iterates ~40 dangerous regex patterns
#   - exit 0 silently if no match (no UI noise on safe commands)
#   - exit 2 with bilingual stderr message if matched
#
# Bypass switch
#   - export LIFEOS_YOLO_MODE=1   # one-session bypass (use sparingly)
#     Note: Claude Code env is evaluated BEFORE PreToolUse fires, so inline
#     `export` inside a previous Bash call doesn't take effect for the next
#     call. Persist via ~/.claude/settings.local.json env block for real bypass.
#
# Provenance
#   The pattern corpus is forked from NousResearch/hermes-agent (MIT) commit
#   59b56d445c34e1d4bf797f5345b802c7b5986c72 → was tools/approval.py @ v1.7.3.
#   v1.8.1 ports them to a bash regex array; 5 Hermes-product-specific
#   patterns dropped (gateway/cli.py/hermes update — Life OS doesn't ship
#   that runtime). Net pattern count: ~42 → ~40.
#
# Safety design
#   - Fail-CLOSED on JSON parse error (block, surface cause)
#   - Fail-CLOSED on missing parser tools (block, instruct user)
#   - Fail-OPEN ONLY when LIFEOS_YOLO_MODE=1 (explicit user override)
# ─────────────────────────────────────────────────────────────────────────────

set -u

# ─── YOLO bypass (early exit, before any expensive work) ────────────────────
if [ "${LIFEOS_YOLO_MODE:-0}" = "1" ]; then
  exit 0
fi

INPUT="$(cat)"
if [ -z "$INPUT" ]; then
  exit 0
fi

# ─── Detect python3 (used only for JSON parsing fallback if jq missing) ─────
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  PYTHON=""
fi

# ─── Extract command from hook JSON ─────────────────────────────────────────
COMMAND=""
PARSE_OK=0
if command -v jq >/dev/null 2>&1; then
  if COMMAND="$(printf '%s' "$INPUT" | jq -er '.tool_input.command // ""' 2>/dev/null)"; then
    PARSE_OK=1
  fi
fi
if [ "$PARSE_OK" -eq 0 ] && [ -n "$PYTHON" ]; then
  PARSED="$(printf '%s' "$INPUT" | "$PYTHON" -c "
import json, sys
try:
    d = json.load(sys.stdin)
    cmd = d.get('tool_input', {}).get('command', '')
    print(cmd if isinstance(cmd, str) else '')
except Exception:
    sys.exit(1)
" 2>/dev/null)"
  if [ $? -eq 0 ]; then
    PARSE_OK=1
    COMMAND="$PARSED"
  fi
fi

if [ "$PARSE_OK" -eq 0 ]; then
  cat >&2 <<'EOF'
🛡️ Life OS 守门人 · 输入 JSON 无法解析（fail-CLOSED）

  原因: 既无 jq 也无 python3 可用，无法从 hook input 中提取 command。
  补救: brew install jq / apt install jq 或安装 python3；
        或 export LIFEOS_YOLO_MODE=1 暂时绕过（仅在你确认风险可控时使用）
EOF
  exit 2
fi

if [ -z "$COMMAND" ]; then
  # Valid JSON but empty command — legit pass-through.
  exit 0
fi

# ─── Normalize command (strip ANSI, lowercase) ──────────────────────────────
# approval.py used Python: strip ANSI + NFKC + lowercase. The bash port keeps
# ANSI-strip + lowercase; full NFKC is overkill for shell-level matching.
NORM="$(printf '%s' "$COMMAND" \
  | sed -E $'s/\x1b\\[[0-9;]*[A-Za-z]//g' \
  | tr 'A-Z' 'a-z')"

# ─── Dangerous-command pattern list ─────────────────────────────────────────
# Each entry is two consecutive array slots: [pattern, description].
# Ported from tools/approval.py @ v1.7.3 (HARDLINE + DANGEROUS combined).
# `\s` → `[[:space:]]` and `\S` → `[^[:space:]]` for portability across
# GNU and BSD grep -E. `\b` is kept because both modern grep variants
# support it as a word-boundary extension.
PATTERNS=(
  # ─ Filesystem destruction (was HARDLINE) ─
  '\brm[[:space:]]+(-[^[:space:]]*[[:space:]]+)*(/|/\*)([[:space:]]|$)'
  'rm targeting root filesystem (/)'

  '\brm[[:space:]]+(-[^[:space:]]*[[:space:]]+)*(/home|/root|/etc|/usr|/var|/bin|/sbin|/boot|/lib)([[:space:]]|/|$)'
  'rm targeting system directory'

  '\brm[[:space:]]+(-[^[:space:]]*[[:space:]]+)*(~|\$home)(/?|/\*)?([[:space:]]|$)'
  'rm targeting home directory'

  '\bmkfs(\.[a-z0-9]+)?\b'
  'format filesystem (mkfs)'

  '\bdd\b[^\n]*\bof=/dev/(sd|nvme|hd|mmcblk|vd|xvd)[a-z0-9]*'
  'dd writing to raw block device'

  '>[[:space:]]*/dev/(sd|nvme|hd|mmcblk|vd|xvd)[a-z0-9]*'
  'redirect to raw block device'

  ':\(\)[[:space:]]*\{[[:space:]]*:[[:space:]]*\|[[:space:]]*:[[:space:]]*&[[:space:]]*\}[[:space:]]*;[[:space:]]*:'
  'fork bomb'

  '\bkill[[:space:]]+(-[^[:space:]]+[[:space:]]+)*-1\b'
  'kill -1 (kill all processes)'

  '(^|[;&|`]|\$\()[[:space:]]*(sudo[[:space:]]+)?(shutdown|reboot|halt|poweroff)\b'
  'system shutdown/reboot'

  '(^|[;&|`]|\$\()[[:space:]]*(sudo[[:space:]]+)?init[[:space:]]+[06]\b'
  'init 0/6 (shutdown/reboot)'

  '\bsystemctl[[:space:]]+(poweroff|reboot|halt|kexec)\b'
  'systemctl poweroff/reboot/halt/kexec'

  '\btelinit[[:space:]]+[06]\b'
  'telinit 0/6 (shutdown/reboot)'

  # ─ Recursive rm (was DANGEROUS) ─
  '\brm[[:space:]]+(-[^[:space:]]*[[:space:]]+)*/'
  'rm in root path'

  '\brm[[:space:]]+-[^[:space:]]*r'
  'recursive rm (-r/-rf/-Rf)'

  '\brm[[:space:]]+--recursive\b'
  'recursive rm (--recursive)'

  # ─ Permission disasters ─
  '\bchmod[[:space:]]+(-[^[:space:]]*[[:space:]]+)*(777|666|o\+[rwx]*w|a\+[rwx]*w)\b'
  'world/other-writable chmod'

  '\bchmod[[:space:]]+--recursive\b.*(777|666|o\+[rwx]*w|a\+[rwx]*w)'
  'recursive world-writable chmod'

  '\bchown[[:space:]]+(-[^[:space:]]*[[:space:]]+)*r[[:space:]]+root'
  'recursive chown to root'

  '\bchown[[:space:]]+--recursive\b.*root'
  'recursive chown to root (--recursive)'

  # ─ Disk / device writes ─
  '\bdd[[:space:]]+.*if='
  'dd disk copy (if=...)'

  # ─ SQL destruction ─
  '\bdrop[[:space:]]+(table|database)\b'
  'SQL DROP TABLE/DATABASE'

  '\bdelete[[:space:]]+from\b'
  'SQL DELETE FROM (review for missing WHERE)'

  '\btruncate[[:space:]]+(table[[:space:]]+)?[a-z_][a-z_0-9]*'
  'SQL TRUNCATE'

  # ─ System config writes ─
  '>[[:space:]]*/etc/'
  'overwrite under /etc/'

  '\bsystemctl[[:space:]]+(-[^[:space:]]+[[:space:]]+)*(stop|restart|disable|mask)\b'
  'systemctl stop/restart/disable/mask'

  '\bpkill[[:space:]]+-9\b'
  'pkill -9 (force kill)'

  # ─ Shell / script execution ─
  '\b(bash|sh|zsh|ksh)[[:space:]]+-[^[:space:]]*c([[:space:]]+|$)'
  'shell -c command execution'

  '\b(python[23]?|perl|ruby|node)[[:space:]]+-[ec][[:space:]]+'
  'script -e/-c execution'

  '\b(curl|wget)\b.*\|[[:space:]]*(ba)?sh\b'
  'pipe remote content to shell (curl|sh)'

  '\b(bash|sh|zsh|ksh)[[:space:]]+<[[:space:]]*<?[[:space:]]*\([[:space:]]*(curl|wget)\b'
  'execute remote script via process substitution'

  '\b(python[23]?|perl|ruby|node)[[:space:]]+<<'
  'script execution via heredoc'

  # ─ Sensitive-target writes ─
  '\btee\b.*("|'\'')?(/etc/|/dev/sd|~/\.ssh/|\$home/\.ssh/)'
  'tee writing to system/ssh path'

  '>>?[[:space:]]*("|'\'')?(/etc/|/dev/sd|~/\.ssh/|\$home/\.ssh/)'
  'redirect to system/ssh path'

  '\btee\b.*("|'\'')?[^[:space:]"\'\'']*\.env(\.[^[:space:]"\'\''/]+)?($|[[:space:]]|;|&|\|)'
  'tee writing to .env file'

  '>>?[[:space:]]*("|'\'')?[^[:space:]"\'\'']*\.env(\.[^[:space:]"\'\''/]+)?($|[[:space:]]|;|&|\|)'
  'redirect to .env file'

  '\b(cp|mv|install)\b.*[[:space:]]/etc/'
  'cp/mv/install into /etc/'

  '\bsed[[:space:]]+-[^[:space:]]*i.*[[:space:]]/etc/'
  'sed -i on /etc/'

  '\bsed[[:space:]]+--in-place\b.*[[:space:]]/etc/'
  'sed --in-place on /etc/'

  # ─ Find / xargs destruction ─
  '\bxargs[[:space:]]+.*\brm\b'
  'xargs piped into rm'

  '\bfind\b.*-exec[[:space:]]+(/[^[:space:]]*/)?rm\b'
  'find -exec rm'

  '\bfind\b.*-delete\b'
  'find -delete'

  # ─ Process self-termination ─
  '\bkill\b.*\$\([[:space:]]*pgrep\b'
  'kill $(pgrep ...) self-termination risk'

  '\bkill\b.*`[[:space:]]*pgrep\b'
  'kill `pgrep ...` self-termination risk'

  # ─ Git destruction ─
  '\bgit[[:space:]]+reset[[:space:]]+--hard\b'
  'git reset --hard (destroys uncommitted)'

  '\bgit[[:space:]]+push\b.*--force\b'
  'git push --force (rewrites remote history)'

  '\bgit[[:space:]]+push\b.*[[:space:]]-f([[:space:]]|$)'
  'git push -f (rewrites remote history)'

  '\bgit[[:space:]]+clean[[:space:]]+-[^[:space:]]*f'
  'git clean -f (deletes untracked)'

  '\bgit[[:space:]]+branch[[:space:]]+-d\b'
  'git branch -D (force delete branch)'

  # ─ chmod-then-execute combo ─
  '\bchmod[[:space:]]+\+x\b.*[;&|]+[[:space:]]*\./'
  'chmod +x followed by immediate ./ execution'
)

# ─── Iterate patterns ───────────────────────────────────────────────────────
i=0
LEN=${#PATTERNS[@]}
while [ "$i" -lt "$LEN" ]; do
  PATTERN="${PATTERNS[$i]}"
  DESCRIPTION="${PATTERNS[$((i+1))]}"

  if printf '%s' "$NORM" | grep -qiE -e "$PATTERN" 2>/dev/null; then
    MATCHED="$(printf '%s' "$NORM" | grep -oiE -e "$PATTERN" 2>/dev/null | head -1)"
    cat >&2 <<EOF
🛡️ Life OS 守门人 · 危险命令拦截

  命令: $COMMAND
  描述: $DESCRIPTION
  匹配: ${MATCHED:-(unable to extract substring)}
  正则: $PATTERN

  下一步:
    a) 改命令绕开此模式（推荐）
    b) 临时关闭守门人本会话: export LIFEOS_YOLO_MODE=1
       注意: Claude Code 内 inline export 通常无效 (PreToolUse hook 在 export
       之前求值 env)。要持久 bypass 改 ~/.claude/settings.local.json 的 env 块
       添加 "LIFEOS_YOLO_MODE": "1"，然后重启 Claude Code session。
    c) 永久 allowlist 此 pattern: 编辑 scripts/hooks/pre-bash-approval.sh

  Provenance: ~40 patterns ported from NousResearch/hermes-agent (MIT) → bash @ v1.8.1
EOF
    exit 2
  fi
  i=$((i+2))
done

exit 0
