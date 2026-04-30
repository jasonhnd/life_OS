#!/bin/bash
# Life OS compliance checker.
#
# Usage:
#   bash scripts/lifeos-compliance-check.sh <output_file> <scenario_name> [violations_file]
#   bash scripts/lifeos-compliance-check.sh fresh-invocation <transcript_file>
#   bash scripts/lifeos-compliance-check.sh <dummy-existing-file> trail-completeness <session_id>
#   bash scripts/lifeos-compliance-check.sh trail-completeness <session_id>
#
# Exit codes:
#   0  all checks passed
#   1  one or more violations detected
#   2  usage error or input file missing
#
# AUDITOR Mode 3 treats this script's exit code as authoritative. The checks
# are intentionally text-based so evals and post-hoc transcript audits can run
# without relying on LLM judgment.

set -euo pipefail

OUTPUT_FILE="${1:-}"
SCENARIO="${2:-}"
VIOLATIONS_FILE="${3:-pro/compliance/violations.md}"
TRAIL_SESSION_ID=""

if [[ "$OUTPUT_FILE" == "fresh-invocation" ]]; then
  SCENARIO="fresh-invocation"
  OUTPUT_FILE="${2:-}"
  VIOLATIONS_FILE="${3:-pro/compliance/violations.md}"
elif [[ "$OUTPUT_FILE" == "trail-completeness" ]]; then
  TRAIL_SESSION_ID="${2:-}"
  SCENARIO="trail-completeness"
  OUTPUT_FILE="/dev/null"
  VIOLATIONS_FILE="${3:-pro/compliance/violations.md}"
elif [[ "$SCENARIO" == "trail-completeness" ]]; then
  TRAIL_SESSION_ID="${3:-}"
  VIOLATIONS_FILE="${4:-pro/compliance/violations.md}"
fi

if [[ -z "$OUTPUT_FILE" || -z "$SCENARIO" ]]; then
  echo "Usage: $0 <output_file> <scenario_name> [violations_file]" >&2
  echo "scenario_name: start-session-compliance | adjourn-compliance | briefing-completeness | version-markers | subagent-launched | cortex-status | placeholder-check | cortex-retrieval | subagent-launch | directory-check | preflight-check | fabricate-path-check | toolcall-evidence | source-drift | source-stale | numeric-stale | retrospective-completeness | fresh-invocation | trail-completeness | banner-check | output-completeness | i18n-sync | frame-md-resolution | main-context-phase | false-positive-check | cortex-cx1..cortex-cx7" >&2
  exit 2
fi

if [[ "$OUTPUT_FILE" != "/dev/null" && ! -f "$OUTPUT_FILE" ]]; then
  echo "ERROR: output file not found: $OUTPUT_FILE" >&2
  exit 2
fi

VIOLATIONS=()

add_violation() {
  VIOLATIONS+=("$1")
}

has() {
  grep -qE "$1" "$OUTPUT_FILE"
}

has_fixed() {
  grep -qF -- "$1" "$OUTPUT_FILE"
}

python_bin() {
  if command -v python3 >/dev/null 2>&1; then
    echo python3
  elif command -v python >/dev/null 2>&1; then
    echo python
  else
    return 1
  fi
}

check_subagent_launch() {
  if ! has 'I am the (RETROSPECTIVE|ARCHIVER) subagent|(RETROSPECTIVE|ARCHIVER) subagent|Task\((retrospective|archiver)\)|Launch\((retrospective|archiver)\)'; then
    add_violation "A1 (P0): subagent-launched failed; no retrospective/archiver Task/Launch/self-check evidence found"
  fi
  if has 'simulated (the )?(retrospective|archiver)|I will act as (retrospective|archiver)|main context.*(retrospective|archiver)|executed (retrospective|archiver).*main context'; then
    add_violation "A1 (P0): transcript suggests main-context subagent simulation"
  fi
}

check_version_markers() {
  local marker
  local saw_retrospective=0

  if has 'Launch\(retrospective\)|RETROSPECTIVE subagent|Pre-Session Preparation|Session Briefing|上朝准备|二脑同步状态|\[Local SKILL\.md version:|\[Remote check \(forced fresh\):'; then
    saw_retrospective=1
  fi

  # Adjourn/archiver transcripts do not emit Step 8 version markers.
  [[ "$saw_retrospective" -eq 1 ]] || return 0

  for marker in "[Local SKILL.md version:" "[Remote check (forced fresh):"; do
    if ! has_fixed "$marker"; then
      add_violation "C (P0): version-markers failed; missing required marker: $marker"
    fi
  done
  if has '\[Local SKILL\.md version:[[:space:]]*version:'; then
    add_violation "B (P0): version-markers failed; local marker includes the literal 'version:' prefix instead of raw stdout"
  fi
}

check_directory_check() {
  if [[ -f "pro/agents/retrospective.md" ]]; then
    if ! has 'DIRECTORY TYPE CHECK|a\) .*second-brain|b\) .*dev|c\) .*new|a\) connect|b\) dev|c\) new'; then
      add_violation "A2 (P1): directory-check failed; dev repo detected but no a/b/c directory menu evidence found"
    fi
  fi
}

check_preflight_check() {
  if ! has 'Trigger:.*Action: Launch\((retrospective|archiver|council)\)|Pre-flight Compliance Check'; then
    add_violation "A3 (P1): preflight-check failed; missing Trigger -> Action: Launch(...) line"
  fi
}

check_fabricate_path() {
  local path
  for path in "_meta/roles/CLAUDE.md" "_meta/roles/" "Pre-Court Preparation" "3-line briefing path" "lightweight briefing path"; do
    if has_fixed "$path"; then
      add_violation "B (P0): fabricate-path-check found known fabricated path/escape route: $path"
    fi
  done

  while IFS= read -r candidate; do
    [[ -z "$candidate" ]] && continue
    [[ "$candidate" == http://* || "$candidate" == https://* ]] && continue
    [[ "$candidate" == *"<"* || "$candidate" == *">"* ]] && continue
    if [[ "$candidate" == */* || "$candidate" == *.md || "$candidate" == *.sh ]]; then
      if [[ ! -e "$candidate" && ! -e "${candidate#./}" ]]; then
        add_violation "B (P0): referenced path does not exist: $candidate"
      fi
    fi
  done < <(grep -oE '`[A-Za-z0-9_./:-]+\.(md|sh|py|json)|`[A-Za-z0-9_./:-]+/[A-Za-z0-9_./:-]+`' "$OUTPUT_FILE" 2>/dev/null | tr -d '`' | sort -u)
}

check_toolcall_evidence() {
  local phrase_output
  if has 'private repo|private repository|WebFetch failed|network unavailable|permission denied|HTTP 40[13]|curl failed'; then
    if ! has 'tool_call|Bash\(|WebFetch\(|curl .*exit|HTTP status|exit code [1-9]'; then
      phrase_output="$(grep -nEi 'private repo|private repository|WebFetch failed|network unavailable|permission denied|HTTP 40[13]|curl failed' "$OUTPUT_FILE" || true)"
      echo "OBSERVE: tool-failure wording appears without adjacent tool evidence; manual review hint only in v1.7.2.1" >&2
      while IFS= read -r line; do
        [[ -n "$line" ]] && echo "  hint: $line" >&2
      done <<< "$phrase_output"
    fi
  fi
  check_version_markers
}

check_source_drift() {
  local py
  py="$(python_bin || true)"
  if [[ -z "$py" ]]; then
    add_violation "B-source-drift (P1): python unavailable; cannot parse measured/index drift"
    return
  fi
  "$py" - "$OUTPUT_FILE" <<'PY' || add_violation "B-source-drift (P1): measured/index delta >=3 without DRIFT marker"
import re, sys
text = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
bad = []
for line in text:
    if "count:" not in line.lower() or "measured" not in line.lower() or "index" not in line.lower():
        continue
    nums = [int(x) for x in re.findall(r"(?:measured|index)\D+(\d+)", line, flags=re.I)]
    if len(nums) >= 2 and abs(nums[0] - nums[1]) >= 3 and "DRIFT" not in line:
        bad.append(line)
if bad:
    for line in bad:
        print(line)
    sys.exit(1)
PY
}

check_source_stale() {
  local py
  if ! has_fixed "[STATUS staleness:"; then
    add_violation "B-source-stale (P1): missing [STATUS staleness:] marker before STATUS-derived claims can be trusted"
    return
  fi
  if ! has_fixed "[STATUS staleness: HEAD-distance"; then
    add_violation "B-source-stale (P1): STATUS staleness marker must use HEAD-distance format"
    return
  fi
  py="$(python_bin || true)"
  if [[ -z "$py" ]]; then
    add_violation "B-source-stale (P1): python unavailable; cannot parse STATUS staleness"
    return
  fi
  "$py" - "$OUTPUT_FILE" <<'PY' || add_violation "B-source-stale (P1): STATUS.md is >=7 days stale while numeric STATUS claims appear"
import re, sys
text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
m = re.search(r"\[STATUS staleness:\s*(?:HEAD-distance\s*)?(\d+)\s*days?", text, re.I)
if not m:
    sys.exit(0)
days = int(m.group(1))
if days < 7:
    sys.exit(0)
for line in text.splitlines():
    if "STATUS.md" in line and re.search(r"\d", line) and "[STATUS staleness:" not in line:
        print(line)
        sys.exit(1)
PY
}

check_numeric_stale() {
  if has '[0-9]+[[:space:]]*(items|entries|files|days|sessions|concepts|%)' && ! has 'measured|wc -l|find .* -name|git log|primary-source|source:'; then
    add_violation "B-stale (P1): numeric claim appears without primary-source measurement evidence"
  fi
}

check_briefing_completeness() {
  local kind=""
  local heading
  local -a missing=()
  local retrospective_heading_0='## 0. <display name> · 上朝准备'
  local -a retrospective_headings=(
    "## 1. 第二大脑同步状态"
    "## 2. SOUL Health 报告"
    "## 3. DREAM / 隔夜更新"
    "## 4. Today's Focus + 待陛下圣裁"
    "## 5. 系统状态"
  )
  local -a archiver_headings=(
    "## Phase 1"
    "## Phase 2"
    "## Phase 3"
    "## Phase 4"
    "## Completion Checklist"
  )

  if has 'Launch\(archiver\)|ARCHIVER subagent|Completion Checklist|Session Closed'; then
    kind="archiver"
  elif has 'Launch\(retrospective\)|RETROSPECTIVE subagent|Pre-Session Preparation|Session Briefing|上朝准备|第二大脑同步状态'; then
    kind="retrospective"
  else
    missing+=("briefing type marker")
  fi

  if [[ "$kind" == "retrospective" ]]; then
    if ! has '^## 0\. .+ · 上朝准备'; then
      missing+=("$retrospective_heading_0")
    fi
    for heading in "${retrospective_headings[@]}"; do
      has_fixed "$heading" || missing+=("$heading")
    done
  elif [[ "$kind" == "archiver" ]]; then
    has 'I am the ARCHIVER subagent' || missing+=("archiver self-check: I am the ARCHIVER subagent")
    for heading in "${archiver_headings[@]}"; do
      has_fixed "$heading" || missing+=("$heading")
    done
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    add_violation "C (P0): briefing-completeness failed; missing required briefing headings: ${missing[*]}"
  fi
}

check_retrospective_completeness() {
  local briefing="$OUTPUT_FILE"
  local m
  local -a required=(
    "[Local SKILL.md version:"
    "[Remote check (forced fresh):"
    "[Wiki count: measured"
    "[Sessions count: measured"
    "[Concepts count: measured"
    "[STATUS staleness:"
    "[FRESH INVOCATION"
  )
  local -a missing=()

  for m in "${required[@]}"; do
    if ! grep -qF -- "$m" "$briefing"; then
      missing+=("$m")
    fi
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "FAIL: missing core markers: ${missing[*]}"
    exit 1
  fi

  echo "PASS: core markers present"
  exit 0
}

check_fresh_invocation() {
  local trigger_count
  local fresh_marker_count
  local forbidden_output=""
  local length_output=""
  local length_status=0
  local py
  local failed=0

  forbidden_output="$(grep -nEi '如上次|参考上次|previously reported|as before|unchanged from last|see Mode 0 output above|skip step.*already done' "$OUTPUT_FILE" || true)"

  trigger_count="$( (grep -Eio '上朝|Start Session|begin court|开始' "$OUTPUT_FILE" 2>/dev/null || true) | wc -l | tr -d ' ')"
  fresh_marker_count="$( (grep -Fo '[FRESH INVOCATION' "$OUTPUT_FILE" 2>/dev/null || true) | wc -l | tr -d ' ')"
  trigger_count="${trigger_count:-0}"
  fresh_marker_count="${fresh_marker_count:-0}"

  if [[ "$trigger_count" -gt 1 && "$fresh_marker_count" -lt "$trigger_count" ]]; then
    failed=1
  fi

  if [[ "$trigger_count" -gt 1 ]]; then
    py="$(python_bin || true)"
    if [[ -z "$py" ]]; then
      length_status=1
      length_output="python_unavailable expected_full_output_chars=unknown actual_chars=unknown"
    else
      length_output="$("$py" - "$OUTPUT_FILE" <<'PY'
import math
import re
import sys

path = sys.argv[1]
text = open(path, encoding="utf-8", errors="replace").read()
matches = list(re.finditer(r"上朝|Start Session|begin court|开始", text, flags=re.I))
if len(matches) <= 1:
    sys.exit(0)

segments = []
for index, match in enumerate(matches):
    start = match.start()
    end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
    segments.append(text[start:end].strip())

first_chars = len(segments[0])
if first_chars <= 0:
    sys.exit(0)

expected = math.ceil(first_chars * 0.8)
failed = False
for index, segment in enumerate(segments[1:], start=2):
    actual = len(segment)
    if actual < expected:
        print(f"trigger_index={index} expected_full_output_chars={expected} actual_chars={actual}")
        failed = True

if failed:
    sys.exit(1)
PY
)" || length_status=$?
    fi
    if [[ "$length_status" -ne 0 ]]; then
      failed=1
    fi
  fi

  if [[ "$failed" -ne 0 ]]; then
    echo "FAIL: C (P0): fresh-invocation trigger_count_in_session=$trigger_count fresh_marker_count=$fresh_marker_count"
    if [[ -n "$forbidden_output" ]]; then
      echo "reuse_wording_hints:"
      while IFS= read -r line; do
        [[ -n "$line" ]] && echo "  $line"
      done <<< "$forbidden_output"
    fi
    if [[ "$trigger_count" -gt 1 && "$fresh_marker_count" -lt "$trigger_count" ]]; then
      echo "missing_marker: expected at least $trigger_count occurrences of [FRESH INVOCATION"
    fi
    if [[ "$length_status" -ne 0 ]]; then
      echo "length_collapse:"
      while IFS= read -r line; do
        [[ -n "$line" ]] && echo "  $line"
      done <<< "$length_output"
    fi
    exit 1
  fi

  if [[ -n "$forbidden_output" ]]; then
    echo "OBSERVE: fresh-invocation reuse wording hint(s) found; no violation emitted for phrases in v1.7.2.1"
    while IFS= read -r line; do
      [[ -n "$line" ]] && echo "  hint: $line"
    done <<< "$forbidden_output"
  fi

  echo "PASS: fresh-invocation trigger_count_in_session=$trigger_count fresh_marker_count=$fresh_marker_count"
  exit 0
}

check_trail_completeness() {
  local session_id="${TRAIL_SESSION_ID:-}"
  local trail_dir
  local trail
  local py
  local schema_output=""
  local schema_status=0
  local failed=0
  local checked_count
  local -a required_trails=(
    "retrospective-step-1.json"
    "retrospective-step-6.json"
    "retrospective-step-9.json"
    "retrospective-step-16.json"
    "retrospective-step-18.json"
  )
  local -a missing=()

  if [[ -z "$session_id" ]]; then
    echo "FAIL: trail-completeness requires session_id" >&2
    exit 2
  fi
  if [[ "$session_id" == *"/"* || "$session_id" == *"\\"* || "$session_id" == "." || "$session_id" == ".." ]]; then
    echo "FAIL: invalid session_id for trail-completeness: $session_id" >&2
    exit 2
  fi

  trail_dir="_meta/runtime/$session_id"

  for trail in "${required_trails[@]}"; do
    if [[ ! -f "$trail_dir/$trail" ]]; then
      missing+=("$trail_dir/$trail")
    fi
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    failed=1
  fi

  py="$(python_bin || true)"
  if [[ -z "$py" ]]; then
    echo "FAIL: python3/python unavailable; cannot parse trail JSON" >&2
    exit 1
  fi

  if [[ -d "$trail_dir" ]]; then
    schema_output="$("$py" - "$trail_dir" <<'PY'
import json
import sys
from pathlib import Path

trail_dir = Path(sys.argv[1])
required = [
    "subagent",
    "step_or_phase",
    "step_name",
    "started_at",
    "ended_at",
    "input_summary",
    "tool_calls",
    "llm_reasoning",
    "output_summary",
    "tokens",
    "fresh_invocation",
    "trigger_count_in_session",
    "audit_trail_version",
]
files = sorted(trail_dir.glob("*.json"))
if not files:
    print("NO_JSON_FILES")
    sys.exit(1)

failed = False
for path in files:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"{path}\tinvalid_json\t{exc}")
        failed = True
        continue
    missing = [field for field in required if field not in data]
    if missing:
        print(f"{path}\tmissing_fields\t{','.join(missing)}")
        failed = True
    if data.get("fresh_invocation") is not True:
        print(f"{path}\tinvalid_field\tfresh_invocation must be true")
        failed = True
    if not isinstance(data.get("trigger_count_in_session"), int):
        print(f"{path}\tinvalid_field\ttrigger_count_in_session must be integer")
        failed = True

if failed:
    sys.exit(1)
print(f"SCHEMA_OK\t{len(files)}")
PY
)" || schema_status=$?
  else
    schema_status=1
    schema_output="NO_TRAIL_DIR"
  fi

  if [[ "$schema_status" -ne 0 ]]; then
    failed=1
  fi

  if [[ "$failed" -ne 0 ]]; then
    echo "FAIL: trail-completeness session_id=$session_id"
    if [[ ${#missing[@]} -gt 0 ]]; then
      echo "missing required trails:"
      for trail in "${missing[@]}"; do
        echo "  expected_trail_path: $trail"
      done
    fi
    if [[ "$schema_status" -ne 0 ]]; then
      echo "schema check failures:"
      if [[ "$schema_output" == "NO_TRAIL_DIR" ]]; then
        echo "  trail_dir_missing: $trail_dir"
      else
        while IFS= read -r trail; do
          [[ -n "$trail" ]] && echo "  $trail"
        done <<< "$schema_output"
      fi
    fi
    exit 1
  fi

  checked_count="$(printf '%s\n' "$schema_output" | awk -F '\t' '/^SCHEMA_OK/ {print $2}')"
  echo "PASS: trail-completeness session_id=$session_id"
  echo "PASS: required trails present; JSON schema fields complete (${checked_count:-0} files checked)"
  exit 0
}

check_banner() {
  local cutoff
  local count
  local py
  local first_line
  py="$(python_bin || true)"
  if [[ -z "$py" ]]; then
    add_violation "C-banner-missing (P0): python unavailable; cannot count 30d compliance banner threshold"
    return
  fi
  cutoff="$("$py" - <<'PY'
from datetime import date, timedelta
print((date.today() - timedelta(days=30)).isoformat())
PY
)"
  count=$(awk -F '|' -v c="$cutoff" '
    /^\| 20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]/ {
      ts=$2; type=$4; resolved=$7
      gsub(/^[ \t]+|[ \t]+$/, "", ts)
      gsub(/^[ \t]+|[ \t]+$/, "", type)
      gsub(/^[ \t]+|[ \t]+$/, "", resolved)
      d=substr(ts,1,10)
      is_p0=(type=="C-banner-missing" || type=="C-output-suppressed" || type=="E")
      is_b=(type=="B" || type ~ /^B-/)
      if (d>=c && resolved !~ /^true/ && type!="F" && (is_p0 || is_b)) print
    }
  ' "$VIOLATIONS_FILE" 2>/dev/null | wc -l | tr -d ' ')
  first_line="$(sed -n '1p' "$OUTPUT_FILE")"
  if [[ "${count:-0}" -ge 3 ]] && ! printf '%s\n' "$first_line" | grep -qF "Compliance Watch"; then
    add_violation "C-banner-missing (P0): 30d threshold count=$count but first line lacks Compliance Watch banner"
  fi
}

check_output_completeness() {
  if has 'output suppressed|omitted for brevity|details omitted|not shown here|省略|割愛|truncated output'; then
    add_violation "C-output-suppressed (P0): required compliance/audit output was suppressed or summarized away"
  fi
}

check_i18n_sync() {
  # NOTE (v1.7.1 R8.2 fix): Removed keyword-literal grep that was self-referential
  # false positive — it fired when CHANGELOG legitimately described the
  # C-translation-drift violation class using its own name ("translation drift",
  # "i18n drift", etc.). Real i18n drift detection is enforced by:
  #   - Subagent F's 14-section Briefing Contract (trilingual H2 must align)
  #   - Version badge consistency (grep elsewhere)
  #   - Trilingual [version] section presence in CHANGELOG
  # Keeping the Type Legend check below since "Type Legend" lives in
  # violations.md which is NOT tracked by pre-commit, so this won't false-positive
  # on README/CHANGELOG diffs.
  if has 'Type Legend' && ! has 'C-output-suppressed|C-translation-drift|C-toctou-frame-md'; then
    add_violation "C-translation-drift (P0): Type Legend appears stale; new C subclasses absent"
  fi
}

check_frame_md_resolution() {
  if has 'FRAME\.md' && has 'not resolved|unresolved|stale frame|TOCTOU|time-of-check|time of check|guessed project|assumed project'; then
    add_violation "C-toctou-frame-md (P0): frame-md-resolution found unresolved/stale FRAME.md context"
  fi
  if has '`[^`]*FRAME\.md`'; then
    while IFS= read -r frame; do
      [[ -z "$frame" ]] && continue
      [[ -e "$frame" || -e "${frame#./}" ]] || add_violation "C-toctou-frame-md (P0): referenced FRAME.md path does not exist: $frame"
    done < <(grep -oE '`[^`]*FRAME\.md`' "$OUTPUT_FILE" | tr -d '`' | sort -u)
  fi
}

check_placeholder() {
  local placeholder
  for placeholder in "TBD" "{...}" "{actual" "pending (TBD)" "TODO"; do
    if has_fixed "$placeholder"; then
      add_violation "D (P1): placeholder-check found unresolved placeholder: $placeholder"
    fi
  done
}

check_main_context_phase() {
  if has 'main context.*Phase [1-4]|ROUTER executed archiver|without archiver subagent|scan wiki candidates|DREAM N1-N2|DREAM N3 consolidate'; then
    if ! has 'ARCHIVER subagent|Task\(archiver\)|Launch\(archiver\)'; then
      add_violation "E (P0): main-context-phase found archiver phase work without archiver subagent evidence"
    fi
  fi
}

check_false_positive() {
  local first_trigger_line
  first_trigger_line=$(grep -nEi '(^|[^A-Za-z])(start|begin|adjourn|done|review|report|brief me|convene|close session)([^A-Za-z]|$)' "$OUTPUT_FILE" | head -1 | cut -d: -f1 || true)
  if [[ -n "$first_trigger_line" && "$first_trigger_line" -gt 1 ]]; then
    if has 'paste|quoted|transcript|```|below|following|non-trigger|false positive'; then
      if has 'A1|A2|A3'; then
        add_violation "F (P2): false-positive-check found paste/non-trigger context that should log F instead of A1/A2/A3"
      fi
    fi
  fi
}

check_cortex_gate() {
  # v1.8.0 R-1.8.0-011 pivot: Cortex is now PULL-BASED. The legacy
  # `cortex_enabled: true` flag in `_meta/config.md` and the v1.7-era
  # "Cortex active" / "Step 0.5" transcript markers no longer represent
  # an "active" gate. ROUTER decides per-message whether to launch any of
  # the hippocampus / concept-lookup / soul-check / gwt-arbitrator
  # subagents based on the actual question.
  #
  # The CX checks below only fire when the current transcript ALREADY
  # shows ROUTER chose to launch a Cortex subagent (i.e. there is at
  # least one Task(hippocampus|concept-lookup|soul-check|gwt-arbitrator)
  # invocation visible). If ROUTER skipped Cortex entirely — the common
  # case post-pivot — there is nothing to verify and the gate returns
  # "not applicable" (return 1).
  if has 'Task\(hippocampus\)|Task\(concept-lookup\)|Task\(soul-check\)|Task\(gwt-arbitrator\)|Launch\(hippocampus\)|Launch\(concept-lookup\)|Launch\(soul-check\)|Launch\(gwt-arbitrator\)'; then
    return 0
  fi
  return 1
}

check_cortex_cx1() {
  # Pull-based: only verify per-module evidence if ROUTER actually
  # launched that specific module. Skip silently when the user's
  # question didn't trigger Cortex at all.
  check_cortex_gate || return 0
  local agent
  for agent in hippocampus concept-lookup soul-check; do
    if has "Task\(${agent}\)|Launch\(${agent}\)"; then
      has "${agent} subagent|Task\(${agent}\)|Launch\(${agent}\)|${agent}: null" || add_violation "CX1 (P1): launched Cortex module $agent but missing evidence"
    fi
  done
}

check_cortex_cx2() {
  check_cortex_gate || return 0
  has 'gwt-arbitrator subagent|Task\(gwt-arbitrator\)|Launch\(gwt-arbitrator\)' || add_violation "CX2 (P1): missing GWT arbitrator evidence"
}

check_cortex_cx3() {
  check_cortex_gate || return 0
  has_fixed "[COGNITIVE CONTEXT]" || add_violation "CX3 (P1): missing [COGNITIVE CONTEXT] opening delimiter"
  has_fixed "[END COGNITIVE CONTEXT]" || add_violation "CX3 (P1): missing [END COGNITIVE CONTEXT] closing delimiter"
}

check_cortex_cx4() {
  check_cortex_gate || return 0
  local count
  count=$(awk '/hippocampus_output:/,/^[A-Za-z_-]+_output:/' "$OUTPUT_FILE" | grep -cE 'session_id:' || true)
  [[ "${count:-0}" -le 7 ]] || add_violation "CX4 (P1): hippocampus returned $count sessions; cap is 7"
}

check_cortex_cx5() {
  check_cortex_gate || return 0
  local count
  count=$(awk '/^\[COGNITIVE CONTEXT\]/,/^\[END COGNITIVE CONTEXT\]/' "$OUTPUT_FILE" | grep -cE 'signal_id:|^- ' || true)
  [[ "${count:-0}" -le 5 ]] || add_violation "CX5 (P1): GWT emitted $count signals; cap is 5"
}

check_cortex_cx6() {
  check_cortex_gate || return 0
  if has 'isolation breach|received peer output|hippocampus.*concept_lookup_output|hippocampus.*soul_check_output|concept-lookup.*hippocampus_output|concept-lookup.*soul_check_output|soul-check.*hippocampus_output|soul-check.*concept_lookup_output'; then
    add_violation "CX6 (P0): Cortex information isolation breach evidence found"
  fi
}

check_cortex_cx7() {
  check_cortex_gate || return 0
  if has '(hippocampus|concept-lookup|soul-check|gwt-arbitrator).*(Write\(|Edit\(|MultiEdit\(|apply_patch|wrote to file)'; then
    add_violation "CX7 (P0): read-only Cortex agent write evidence found"
  fi
}

check_cortex_all() {
  check_cortex_cx1
  check_cortex_cx2
  check_cortex_cx3
  check_cortex_cx4
  check_cortex_cx5
  check_cortex_cx6
  check_cortex_cx7
}

check_cortex_status() {
  local saw_retrospective=0

  if has 'Launch\(retrospective\)|RETROSPECTIVE subagent|Pre-Session Preparation|Session Briefing|## 0[.].*Cortex 状态|Cortex|Step 0[.]5'; then
    saw_retrospective=1
  fi

  # Adjourn/archiver transcripts do not need a Cortex status block.
  [[ "$saw_retrospective" -eq 1 ]] || return 0

  if ! has '## 0[.].*Cortex 状态|Cortex|Step 0[.]5'; then
    add_violation "C (P0): cortex-status failed; missing Cortex status marker in briefing"
  fi
  if ! has 'hippocampus|concept-lookup|soul-check|gwt-arbitrator|Cortex.*(active|enabled|skipped|degraded|unavailable|null)|Step 0[.]5.*(active|enabled|skipped|degraded|unavailable|null)'; then
    add_violation "C (P0): cortex-status failed; no Cortex module status or explicit skipped/degraded state found"
  fi
}

case "$SCENARIO" in
  start-session-compliance)
    check_briefing_completeness
    check_version_markers
    check_subagent_launch
    check_cortex_status
    check_placeholder
    ;;
  adjourn-compliance)
    check_briefing_completeness
    check_version_markers
    check_subagent_launch
    check_cortex_status
    check_placeholder
    ;;
  cortex-retrieval)
    check_cortex_all
    ;;
  subagent-launch|subagent-launched)
    check_subagent_launch
    ;;
  directory-check)
    check_directory_check
    ;;
  preflight-check)
    check_preflight_check
    ;;
  fabricate-path-check)
    check_fabricate_path
    ;;
  toolcall-evidence)
    check_toolcall_evidence
    ;;
  version-markers)
    check_version_markers
    ;;
  source-drift)
    check_source_drift
    ;;
  source-stale|status-staleness)
    check_source_stale
    ;;
  numeric-stale)
    check_numeric_stale
    ;;
  briefing-completeness)
    check_briefing_completeness
    ;;
  retrospective-completeness)
    check_retrospective_completeness
    ;;
  fresh-invocation)
    check_fresh_invocation
    ;;
  trail-completeness)
    check_trail_completeness
    ;;
  primary-source-markers)
    has_fixed "[Wiki count: measured" || add_violation "C-brief-incomplete (P1): missing [Wiki count: measured] marker"
    has_fixed "[Sessions count: measured" || add_violation "C-brief-incomplete (P1): missing [Sessions count: measured] marker"
    has_fixed "[Concepts count: measured" || add_violation "C-brief-incomplete (P1): missing [Concepts count: measured] marker"
    has_fixed "status-snapshot" || add_violation "C-brief-incomplete (P1): primary-source marker missing status-snapshot field"
    has_fixed "INDEX-md" || add_violation "C-brief-incomplete (P1): primary-source marker missing INDEX-md field"
    ;;
  banner-check)
    check_banner
    ;;
  output-completeness)
    check_output_completeness
    ;;
  i18n-sync)
    check_i18n_sync
    ;;
  frame-md-resolution)
    check_frame_md_resolution
    ;;
  placeholder-check)
    check_placeholder
    ;;
  cortex-status)
    check_cortex_status
    ;;
  main-context-phase)
    check_main_context_phase
    ;;
  false-positive-check)
    check_false_positive
    ;;
  cortex-cx1)
    check_cortex_cx1
    ;;
  cortex-cx2)
    check_cortex_cx2
    ;;
  cortex-cx3)
    check_cortex_cx3
    ;;
  cortex-cx4)
    check_cortex_cx4
    ;;
  cortex-cx5)
    check_cortex_cx5
    ;;
  cortex-cx6)
    check_cortex_cx6
    ;;
  cortex-cx7)
    check_cortex_cx7
    ;;
  *)
    echo "INFO: no compliance checks defined for scenario '$SCENARIO'; skipping" >&2
    exit 0
    ;;
esac

if [[ ${#VIOLATIONS[@]} -gt 0 ]]; then
  echo "Compliance check FAILED: $SCENARIO ($(basename "$OUTPUT_FILE"))" >&2
  for violation in "${VIOLATIONS[@]}"; do
    echo "  - $violation" >&2
  done
  exit 1
fi

echo "Compliance check PASSED: $SCENARIO ($(basename "$OUTPUT_FILE"))"
exit 0
