#!/usr/bin/env bash
# Read-only prefetch for Archiver Phase 1-4 scriptable facts.
# LLM judgment remains with the archiver subagent: wiki six-criteria review,
# SOUL evidence interpretation, and final archive decisions are not performed
# here.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
SCRIPT_ROOT="$(cd "${SCRIPT_DIR}/.." 2>/dev/null && pwd -P)"
PWD_ROOT="$(pwd -P 2>/dev/null || pwd)"
AUDIT_TRAIL_AVAILABLE=0

for _audit_trail_lib in "$SCRIPT_DIR/lib/audit-trail.sh" "$SCRIPT_ROOT/scripts/lib/audit-trail.sh"; do
  if [[ -r "$_audit_trail_lib" ]]; then
    if . "$_audit_trail_lib"; then
      AUDIT_TRAIL_AVAILABLE=1
    fi
    break
  fi
done
unset _audit_trail_lib
if [[ -z "${LIFEOS_SESSION_ID:-}" ]]; then
  export LIFEOS_SESSION_ID="$(date -u +%Y%m%dT%H%M%S)"
fi

usage() {
  cat <<'EOF'
Usage: archiver-phase-prefetch.sh [--root PATH] [--session-id SID]

Emits read-only Archiver Phase 1-4 fact markers and audit trail entries.
EOF
}

have() {
  command -v "$1" >/dev/null 2>&1
}

abspath() {
  local path="$1"
  if [[ -d "$path" ]]; then
    (cd "$path" 2>/dev/null && pwd -P) || printf '%s\n' "$path"
  else
    local dir
    local base
    dir="$(dirname "$path")"
    base="$(basename "$path")"
    (cd "$dir" 2>/dev/null && printf '%s/%s\n' "$(pwd -P)" "$base") || printf '%s\n' "$path"
  fi
}

is_second_brain() {
  local root="$1"
  [[ -d "$root/_meta" && -d "$root/projects" ]]
}

first_existing_dir() {
  local candidate
  for candidate in "$@"; do
    if [[ -n "$candidate" && -d "$candidate" ]]; then
      abspath "$candidate"
      return 0
    fi
  done
  return 1
}

resolve_data_root() {
  local requested="${1:-}"
  local configured=""

  if [[ -n "$requested" && -d "$requested" ]]; then
    abspath "$requested"
    return 0
  fi

  if is_second_brain "$PWD_ROOT"; then
    printf '%s\n' "$PWD_ROOT"
    return 0
  fi

  configured="$(first_existing_dir \
    "${LIFEOS_SECOND_BRAIN_PATH:-}" \
    "${LIFEOS_SECOND_BRAIN:-}" \
    "${SECOND_BRAIN_PATH:-}" \
    "${SECOND_BRAIN:-}" 2>/dev/null || true)"
  if [[ -n "$configured" ]]; then
    printf '%s\n' "$configured"
    return 0
  fi

  printf '%s\n' "$PWD_ROOT"
}

count_files() {
  local path="$1"
  local pattern="${2:-*}"

  if [[ ! -d "$path" ]] || ! have find; then
    printf '0\n'
    return
  fi

  find "$path" -type f -name "$pattern" 2>/dev/null | wc -l | tr -d '[:space:]'
}

latest_file() {
  local dir="$1"
  local pattern="$2"

  if [[ ! -d "$dir" ]] || ! have find; then
    printf 'none\n'
    return
  fi

  find "$dir" -maxdepth 1 -type f -name "$pattern" 2>/dev/null | sort | tail -n 1 | sed 's#^\./##'
}

git_health() {
  local root="$1"
  local head_hash="unknown"
  local upstream=""
  local ahead="0"
  local behind="0"

  if ! have git; then
    printf 'git_unavailable\n'
    return
  fi

  if ! git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf 'no_git_repo\n'
    return
  fi

  head_hash="$(git -C "$root" rev-parse --short HEAD 2>/dev/null || printf 'unknown')"
  upstream="$(git -C "$root" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
  if [[ -n "$upstream" ]]; then
    ahead="$(git -C "$root" rev-list --count "${upstream}..HEAD" 2>/dev/null || printf '0')"
    behind="$(git -C "$root" rev-list --count "HEAD..${upstream}" 2>/dev/null || printf '0')"
  fi

  printf 'HEAD=%s ahead=%s behind=%s upstream=%s\n' "$head_hash" "${ahead:-0}" "${behind:-0}" "${upstream:-none}"
}

emit_archiver_trail_marker() {
  local phase="$1"
  local phase_name="$2"
  local input_summary="$3"
  local output_marker="$4"

  if [[ "${AUDIT_TRAIL_AVAILABLE:-0}" == "1" ]]; then
    emit_trail_marker "archiver" "$phase" "$phase_name" "$input_summary" "$output_marker" || true
  fi
}

requested_root=""
requested_sid=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      if [[ $# -lt 2 ]]; then
        printf 'Missing value for --root\n' >&2
        exit 2
      fi
      requested_root="${2:-}"
      shift 2
      ;;
    --session-id)
      if [[ $# -lt 2 ]]; then
        printf 'Missing value for --session-id\n' >&2
        exit 2
      fi
      requested_sid="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -n "$requested_sid" ]]; then
  export LIFEOS_SESSION_ID="$requested_sid"
  LIFEOS_AUDIT_SESSION_ID="$requested_sid"
fi

data_root="$(resolve_data_root "$requested_root")"
LIFEOS_AUDIT_ROOT="$data_root"

outbox_dir="$data_root/_meta/outbox"
outbox_files="$(count_files "$outbox_dir" '*.md')"
session_candidates="0"
if [[ -d "$outbox_dir" ]] && have find; then
  session_candidates="$(find "$outbox_dir" -type f -path '*/sessions/*.md' 2>/dev/null | wc -l | tr -d '[:space:]')"
fi
phase_1_marker="[PHASE 1 · ARCHIVER · OUTBOX PREFETCH: outbox=$outbox_dir files=$outbox_files session_candidates=$session_candidates]"
echo "$phase_1_marker"
emit_archiver_trail_marker "phase-1" "OUTBOX PREFETCH" "data_root=$data_root; read_only=true" "$phase_1_marker"

wiki_dir="$data_root/wiki"
concepts_dir="$data_root/_meta/concepts"
soul_path="$data_root/SOUL.md"
wiki_entries="$(count_files "$wiki_dir" '*.md')"
concept_entries="0"
if [[ -d "$concepts_dir" ]] && have find; then
  concept_entries="$(find "$concepts_dir" -type f -name '*.md' ! -name 'INDEX.md' ! -name 'SYNAPSES-INDEX.md' 2>/dev/null | wc -l | tr -d '[:space:]')"
fi
soul_status="missing"
[[ -f "$soul_path" ]] && soul_status="found"
phase_2_marker="[PHASE 2 · ARCHIVER · KNOWLEDGE PREFETCH: wiki_entries=$wiki_entries concepts=$concept_entries soul=$soul_status judgment=deferred]"
echo "$phase_2_marker"
emit_archiver_trail_marker "phase-2" "KNOWLEDGE PREFETCH" "wiki_dir=$wiki_dir; concepts_dir=$concepts_dir; soul_path=$soul_path; llm_judgment=deferred" "$phase_2_marker"

journal_dir="$data_root/_meta/journal"
dream_count="0"
dream_latest="none"
if [[ -d "$journal_dir" ]] && have find; then
  dream_count="$(find "$journal_dir" -maxdepth 1 -type f -name '*-dream.md' 2>/dev/null | wc -l | tr -d '[:space:]')"
  dream_latest="$(latest_file "$journal_dir" '*-dream.md')"
fi
phase_3_marker="[PHASE 3 · ARCHIVER · DREAM PREFETCH: journal=$journal_dir dreams=$dream_count latest=$dream_latest judgment=deferred]"
echo "$phase_3_marker"
emit_archiver_trail_marker "phase-3" "DREAM PREFETCH" "journal_dir=$journal_dir; llm_judgment=deferred" "$phase_3_marker"

config_path="$data_root/_meta/config.md"
notion_config="missing"
if [[ -f "$config_path" ]] && grep -qiE '^[[:space:]]*(\[notion\]|notion:)' "$config_path" 2>/dev/null; then
  notion_config="found"
fi
sync_log="$data_root/_meta/notion-sync-log.md"
sync_log_status="missing"
[[ -f "$sync_log" ]] && sync_log_status="found"
git_status="$(git_health "$data_root")"
phase_4_marker="[PHASE 4 · ARCHIVER · SYNC PREFETCH: git=$git_status notion_config=$notion_config sync_log=$sync_log_status]"
echo "$phase_4_marker"
emit_archiver_trail_marker "phase-4" "SYNC PREFETCH" "data_root=$data_root; config_path=$config_path; sync_log=$sync_log" "$phase_4_marker"
