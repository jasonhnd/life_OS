#!/bin/bash
# Life OS · pre-notion-write.sh (v1.8.3 outbound boundary)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PreToolUse
# Matcher: notion-(create|update|move).*|mcp__notion.*-(create|update|move).*
# Exit:    0 = pass / warn / info | 2 = block (CLASS_F violation)
# Timeout: 5s
#
# Purpose
#   Outbound boundary scan: every Notion MCP write call passes through this
#   hook. The threat model is "what may safely live in _meta/outbox/<sid>/
#   under user's git, but should NOT travel to Notion" — Notion may be a
#   shared workspace, indexed by Notion AI, mobile-readable, or breach-prone.
#
#   Pre-existing pre-write-scan.sh defends inbound (knowledge files); this
#   hook defends outbound. They share Group A "hard secrets" and diverge on
#   Group B-E (third-party names, financial specifics, contact info).
#
# Contract
#   references/outbound-pii-patterns.md (full pattern catalogue)
#   references/hooks-spec.md §5.6 (this hook in the v1.8.3 hook map)
#
# Three-tier action model:
#   - Group A hit → exit 2 (block)
#   - Group B/C/D hit → exit 0 + <system-reminder> (warn — orchestrator decides)
#   - Group E hit → exit 0 + quiet log (info)
#   - No hit → exit 0 silently
#
# Audit trail
#   Always writes _meta/runtime/<sid>/notion-pii-scan-<ts>.json with the
#   matched_patterns block (category IDs only, never raw content).
# ─────────────────────────────────────────────────────────────────────────────

set -u

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_lib.sh"

ACTIVITY_DIR="$HOME/.cache/lifeos"
ACTIVITY_LOG="$ACTIVITY_DIR/hook-activity-$(date +%F).log"
ACTIVITY_TOOL="unknown"
ACTIVITY_VERDICT="pass"
emit_activity() {
  local line="🪝 pre-notion-write: tool=${ACTIVITY_TOOL} verdict=${ACTIVITY_VERDICT}"
  mkdir -p "$ACTIVITY_DIR" 2>/dev/null || true
  printf '%s\n' "$line"
  printf '%s %s\n' "$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')" "$line" >> "$ACTIVITY_LOG" 2>/dev/null || true
}
trap emit_activity EXIT

INPUT="$(cat)"
[ -z "$INPUT" ] && exit 0

TOOL_NAME="$(lib_json_field "$INPUT" tool_name)"
ACTIVITY_TOOL="${TOOL_NAME:-unknown}"

# ─── Tool-name gate ─────────────────────────────────────────────────────────
# Matcher already filters in settings.json, but defense-in-depth — re-check
# inside the hook so a misregistration doesn't leak unscanned writes through.
case "$TOOL_NAME" in
  *notion*create*|*notion*update*|*notion*move*|*Notion*Create*|*Notion*Update*|*Notion*Move*) : ;;
  *) exit 0 ;;
esac

# ─── Extract scannable content from tool_input ──────────────────────────────
# Notion MCP write tools have varied schemas (notion-create-pages takes a
# `pages` array; notion-update-page takes `page_id` + `properties` + body).
# Rather than schema-match each tool, we serialize tool_input to JSON and scan
# the whole blob. False-positive cost: tool args like database_id may match
# Group A9 (high-entropy). Mitigation: A9 is calibrated to 40+ chars (database
# IDs are 32 chars, won't match) and we exclude UUID-shaped fields below.

CONTENT=""

if command -v jq >/dev/null 2>&1; then
  # Strip out fields that are *structurally* IDs, not content. Keep title,
  # body content, properties values.
  CONTENT="$(printf '%s' "$INPUT" \
    | jq -r '.tool_input
      | walk(if type == "object" then
          del(.page_id, .database_id, .parent_id, .id, .ids, .page_ids, .parent.page_id, .parent.database_id, .icon, .cover)
        else . end)
      | tojson' 2>/dev/null || echo "")"
elif command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
  PY_CMD="$(command -v python || command -v python3)"
  CONTENT="$(printf '%s' "$INPUT" | "$PY_CMD" -c "
import json, sys
ID_KEYS = {'page_id', 'database_id', 'parent_id', 'id', 'ids', 'page_ids', 'icon', 'cover'}
def strip_ids(x):
    if isinstance(x, dict):
        return {k: strip_ids(v) for k, v in x.items() if k not in ID_KEYS}
    if isinstance(x, list):
        return [strip_ids(v) for v in x]
    return x
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    print(json.dumps(strip_ids(ti), ensure_ascii=False))
except Exception:
    pass
" 2>/dev/null)"
else
  # Last resort: use the whole INPUT. Best-effort scan; the audit trail will
  # note degraded mode.
  CONTENT="$INPUT"
  echo "[pre-notion-write] WARNING: jq and python unavailable, scanning raw INPUT" >&2
fi

[ -z "$CONTENT" ] && CONTENT="$INPUT"

# ─── Pattern scan helpers ───────────────────────────────────────────────────
HITS_A=""
HITS_B=""
HITS_C=""
HITS_D=""
HITS_E=""

scan_group() {
  local id="$1"; local case_flag="$2"; local re="$3"; local group_var="$4"
  local matched=0
  if [ "$case_flag" = "i" ]; then
    if printf '%s' "$CONTENT" | grep -qiE -e "$re"; then matched=1; fi
  else
    if printf '%s' "$CONTENT" | grep -qE -e "$re"; then matched=1; fi
  fi
  if [ "$matched" = "1" ]; then
    case "$group_var" in
      A) HITS_A="${HITS_A:+$HITS_A,}$id" ;;
      B) HITS_B="${HITS_B:+$HITS_B,}$id" ;;
      C) HITS_C="${HITS_C:+$HITS_C,}$id" ;;
      D) HITS_D="${HITS_D:+$HITS_D,}$id" ;;
      E) HITS_E="${HITS_E:+$HITS_E,}$id" ;;
    esac
  fi
}

# ─── Group A · Hard Secrets (block) ────────────────────────────────────────
scan_group A1 x '-----BEGIN[[:space:]]+(RSA[[:space:]]+|DSA[[:space:]]+|EC[[:space:]]+|OPENSSH[[:space:]]+)?PRIVATE[[:space:]]+KEY-----' A
scan_group A2 x 'AKIA[0-9A-Z]{16}' A
scan_group A3 x 'ghp_[a-zA-Z0-9]{36}' A
scan_group A4 x 'xox[pbar]-[0-9]{10,}-[a-zA-Z0-9]{24,}' A
scan_group A5 x '(sk|pk|api|secret|token)_[a-zA-Z0-9]{20,}' A
scan_group A6 x '4[0-9]{12}([0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(011|5[0-9]{2})[0-9]{12}' A
scan_group A7 x '[0-9]{3}-[0-9]{2}-[0-9]{4}' A
# A8 jp-mynumber: 12 digits, often hyphenated as 4-4-4. Order matters — run
# AFTER phone scans to reduce false-positive on phone numbers.
scan_group A9 x '[A-Za-z0-9+/]{40,}={0,2}' A

# ─── Group D · Contact Info (warn) — scanned BEFORE A8 to avoid phone collision ──
scan_group D1 x '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' D
scan_group D2 x '\+[0-9]{1,3}[[:space:]\-]?[0-9]{2,4}[[:space:]\-]?[0-9]{4,8}' D
scan_group D3 x '0[789]0[[:space:]\-]?[0-9]{4}[[:space:]\-]?[0-9]{4}' D
scan_group D4 x '1[3-9][0-9][[:space:]\-]?[0-9]{4}[[:space:]\-]?[0-9]{4}' D
scan_group D5 x '〒?[0-9]{3}[-[:space:]]?[0-9]{4}[^\n]{0,40}(都|道|府|県)' D

# A8 jp-mynumber — after D so phones are caught first
scan_group A8 x '[0-9]{4}[-[:space:]]?[0-9]{4}[-[:space:]]?[0-9]{4}' A

# ─── Group B · Personal Identifier (warn) ──────────────────────────────────
# B1 family-relation-event (CN/JP/EN family terms + sensitive event)
scan_group B1 i '(老婆|老公|妻子|丈夫|爸爸?|妈妈?|父親|母親|儿子|女儿|息子|娘|兄弟|姐妹|姉|妹|哥哥?|弟弟?|wife|husband|mom|mother|dad|father|son|daughter)[^.\n]{0,50}(出轨|生病|住院|破产|失业|被裁|离婚|分手|去世|过世|cheat|sick|fired|laid[[:space:]]?off|divorce|died|passed[[:space:]]away)' B
# B2 named-person-event (Western "FirstName LastName" + sensitive verb)
scan_group B2 i '[A-Z][a-z]+[[:space:]][A-Z][a-z]+[^.\n]{0,40}(was[[:space:]]fired|laid[[:space:]]?off|got[[:space:]]divorced|cheating|bankrupt|hospitalized|died)' B
# B3 cn-name-event — bash POSIX regex can't easily express CJK ranges, so
# we rely on the predicate verbs alone. The verb list is rare enough in
# benign content that hits indicate a name-event pattern. Tighten in v1.9
# if false-positive rate is problematic.
scan_group B3 x '(出轨|破产|被裁|被开|跑路|跳槽)' B

# ─── Group C · Financial Specifics (warn) ──────────────────────────────────
# C1 company-amount (Capitalized token + currency or large number nearby)
scan_group C1 x '[A-Z][A-Za-z0-9&]{2,}([[:space:]]?(株式会社|有限公司|Inc|Ltd|LLC|Corp))?[^.\n]{0,30}(¥|￥|\$|€|£)[[:space:]]?[0-9]{4,}' C
# C2 bank-account-shaped (8-19 digit run) — high false-positive, treated
# only when accompanied by a banking keyword
scan_group C2 i '(account|账户|账号|口座|iban|swift)[^.\n]{0,20}[0-9]{8,19}' C
# C3 jp-bank-detail
scan_group C3 x '(三菱UFJ|三井住友|みずほ|ゆうちょ|楽天銀行)[^.\n]{0,30}[0-9]{6,}' C

# ─── Group E · Soft Signals (info) ─────────────────────────────────────────
scan_group E1 x 'https?://[^[:space:]]*[?&](utm_|fbclid|gclid)' E
scan_group E2 x 'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}' E

# ─── Verdict resolution ─────────────────────────────────────────────────────
VERDICT="pass"
if [ -n "$HITS_A" ]; then
  VERDICT="block"
elif [ -n "$HITS_B" ] || [ -n "$HITS_C" ] || [ -n "$HITS_D" ]; then
  VERDICT="warn"
elif [ -n "$HITS_E" ]; then
  VERDICT="info"
fi

ACTIVITY_VERDICT="$VERDICT"

# ─── Audit trail (always written) ──────────────────────────────────────────
write_audit_trail() {
  local sid="${LIFEOS_AUDIT_SESSION_ID:-${SESSION_ID:-unknown}}"
  local ts
  ts="$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')"
  local ts_compact
  ts_compact="$(date '+%Y%m%dT%H%M%S' 2>/dev/null || date '+%Y%m%d%H%M%S')"
  local audit_dir
  audit_dir="$(pwd)/_meta/runtime/$sid"
  mkdir -p "$audit_dir" 2>/dev/null || return 0
  local audit_path="$audit_dir/notion-pii-scan-$ts_compact.json"

  local body_len="${#CONTENT}"

  # Build matched_patterns JSON (manually — no jq dependency at write time)
  patterns_to_json() {
    local hits="$1"
    if [ -z "$hits" ]; then printf '[]'; return; fi
    local items=""
    local IFS=','
    # shellcheck disable=SC2086
    for h in $hits; do
      items="${items:+$items,}\"$h\""
    done
    printf '[%s]' "$items"
  }

  local pa pb pc pd pe
  pa="$(patterns_to_json "$HITS_A")"
  pb="$(patterns_to_json "$HITS_B")"
  pc="$(patterns_to_json "$HITS_C")"
  pd="$(patterns_to_json "$HITS_D")"
  pe="$(patterns_to_json "$HITS_E")"

  local all_hits="${HITS_A}${HITS_A:+${HITS_B:+,}}${HITS_B}${HITS_B:+${HITS_C:+,}}${HITS_C}${HITS_C:+${HITS_D:+,}}${HITS_D}${HITS_D:+${HITS_E:+,}}${HITS_E}"

  cat > "$audit_path" <<EOF
{
  "subagent": "pre-notion-write",
  "step_or_phase": "outbound-scan",
  "step_name": "Notion outbound PII scan",
  "started_at": "$ts",
  "ended_at": "$ts",
  "input_summary": "tool_name=$TOOL_NAME body_length=$body_len",
  "tool_calls": [],
  "llm_reasoning": "(regex scan, no LLM)",
  "output_summary": "verdict=$VERDICT hits=$all_hits",
  "matched_patterns": {
    "A": $pa,
    "B": $pb,
    "C": $pc,
    "D": $pd,
    "E": $pe
  },
  "verdict": "$VERDICT",
  "tokens": {"input": 0, "output": 0},
  "audit_trail_version": "v1.8.3-r11"
}
EOF
}

write_audit_trail || true

# ─── Action ─────────────────────────────────────────────────────────────────
case "$VERDICT" in
  pass)
    exit 0
    ;;

  info)
    # Quiet — log only, no user-facing reminder
    exit 0
    ;;

  warn)
    # Compose category list for the reminder
    cat_list=""
    [ -n "$HITS_B" ] && cat_list="${cat_list:+$cat_list, }Group B (third-party names + sensitive events): $HITS_B"
    [ -n "$HITS_C" ] && cat_list="${cat_list:+$cat_list, }Group C (financial specifics): $HITS_C"
    [ -n "$HITS_D" ] && cat_list="${cat_list:+$cat_list, }Group D (contact info): $HITS_D"

    cat >&1 <<EOF
<system-reminder>
🛡️ Outbound PII gate · pre-notion-write detected sensitive content.

Tool: $TOOL_NAME
Matched: $cat_list

This content may travel to Notion (third-party storage; potentially shared,
AI-indexed, or mobile-readable). It is acceptable in your local outbox under
git, but the boundary tier is stricter.

REQUIRED before proceeding:
1. Briefly tell the user what category was detected (no raw content quoted).
2. Ask whether to:
   (a) sanitize — re-issue the Notion call after redacting third-party names,
       specific amounts, contact info; OR
   (b) skip — drop this Notion sync entry; OR
   (c) override — proceed as-is (user explicitly accepts the boundary risk).
3. Only after explicit user choice, retry the Notion MCP call.

DO NOT silently retry. DO NOT proceed without asking. The local outbox is
already preserved under git regardless of which option is chosen.

Contract: references/outbound-pii-patterns.md
Audit:    _meta/runtime/<sid>/notion-pii-scan-<ts>.json
</system-reminder>
EOF
    # exit 0 → tool call proceeds; the reminder is advisory. The orchestrator
    # is expected to read it and stop the sync (per pro/CLAUDE.md Step 10a
    # sanitize gate). To enforce hard-block on warn, an organisation can flip
    # this to exit 2; v1.8.3 ships advisory because false-positive cost on
    # B3/C2 is non-zero.
    exit 0
    ;;

  block)
    lib_log_violation "CLASS_F" "critical" "ROUTER" \
      "outbound-pii block hits=$HITS_A tool=$TOOL_NAME" \
      "pre-notion-write"

    cat >&1 <<EOF
<system-reminder>
🚫 HARD RULE VIOLATION (CLASS_F) · pre-notion-write blocked $TOOL_NAME.

Matched (Group A · hard secrets): $HITS_A

Notion writes containing private keys, AWS/GitHub/Slack tokens, full credit-
card numbers, SSN, or high-entropy keys are unconditionally blocked. These
must NOT be sent to a third-party storage layer.

Required action:
1. Identify the leaked credential in the staged content.
2. Rotate the credential if it was a real secret (treat it as compromised
   the moment it touched a tool_input that left the LLM context boundary).
3. Remove the credential from the source (likely the session conversation
   or a Decision body) and retry the Notion sync.

Local outbox content under _meta/outbox/ is unaffected. The block applies
to the Notion MCP call only.

Logged to compliance path as CLASS_F (critical).
Contract: references/outbound-pii-patterns.md §3 Group A
</system-reminder>
EOF

    cat >&2 <<EOF
Blocked by life-os-pre-notion-write: Group A patterns matched ($HITS_A) in $TOOL_NAME.
EOF

    exit 2
    ;;
esac

exit 0
