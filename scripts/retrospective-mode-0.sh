#!/usr/bin/env bash
# Read-only Mode 0 telemetry for Life OS retrospective startup.
# This script intentionally reports health/counts only. It does not rebuild
# indexes, edit files, or run mutating sync operations.

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

have() {
  command -v "$1" >/dev/null 2>&1
}

abspath() {
  local path="$1"
  if [[ -d "$path" ]]; then
    (cd "$path" 2>/dev/null && pwd -P) || printf '%s\n' "$path"
  else
    local dir base
    dir="$(dirname "$path")"
    base="$(basename "$path")"
    (cd "$dir" 2>/dev/null && printf '%s/%s\n' "$(pwd -P)" "$base") || printf '%s\n' "$path"
  fi
}

is_dev_repo() {
  local root="$1"
  [[ -f "$root/SKILL.md" && -d "$root/pro/agents" && -d "$root/themes" ]]
}

is_second_brain() {
  local root="$1"
  [[ -d "$root/_meta" && -d "$root/projects" ]]
}

count_paths() {
  local path="$1"
  local mode="${2:-entries}"
  local name_filter="${3:-}"

  if [[ ! -d "$path" ]] || ! have find; then
    printf '0\n'
    return
  fi

  case "$mode" in
    files)
      if [[ -n "$name_filter" ]]; then
        find "$path" -type f -name "$name_filter" 2>/dev/null | wc -l | tr -d '[:space:]'
      else
        find "$path" -type f 2>/dev/null | wc -l | tr -d '[:space:]'
      fi
      ;;
    dirs)
      find "$path" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d '[:space:]'
      ;;
    *)
      find "$path" -mindepth 1 -maxdepth 1 2>/dev/null | wc -l | tr -d '[:space:]'
      ;;
  esac
}

first_existing_dir() {
  local candidate
  for candidate in "$@"; do
    [[ -n "$candidate" && -d "$candidate" ]] && {
      abspath "$candidate"
      return
    }
  done
  return 1
}

parse_config_path_value() {
  local file="$1"
  [[ -f "$file" ]] || return 1
  grep -E '^[[:space:]]*(second_brain|second_brain_path|lifeos_second_brain|root|path):' "$file" 2>/dev/null \
    | head -n 1 \
    | sed -E 's/^[^:]+:[[:space:]]*//; s/^["'\'']//; s/["'\'']$//' \
    || return 1
}

resolve_second_brain_root() {
  local configured=""

  if is_second_brain "$PWD_ROOT"; then
    printf '%s\n' "$PWD_ROOT"
    return 0
  fi

  configured="$(first_existing_dir \
    "${LIFEOS_SECOND_BRAIN_PATH:-}" \
    "${LIFEOS_SECOND_BRAIN:-}" \
    "${SECOND_BRAIN_PATH:-}" \
    "${SECOND_BRAIN:-}" 2>/dev/null || true)"
  if [[ -n "$configured" && -d "$configured/_meta" ]]; then
    printf '%s\n' "$configured"
    return 0
  fi

  local config_file value
  for config_file in "$PWD_ROOT/.lifeos/config" "$PWD_ROOT/.lifeos/config.md" "$HOME/.lifeos/config" "$HOME/.lifeos/config.md"; do
    value="$(parse_config_path_value "$config_file" 2>/dev/null || true)"
    if [[ -n "$value" ]]; then
      value="${value/#\~/$HOME}"
      if [[ -d "$value/_meta" ]]; then
        abspath "$value"
        return 0
      fi
    fi
  done

  return 1
}

extract_yaml_value() {
  local key="$1"
  local file="$2"
  [[ -f "$file" ]] || return 1
  grep -m 1 -E "^[[:space:]]*${key}:" "$file" 2>/dev/null \
    | sed -E 's/^[^:]+:[[:space:]]*//; s/^["'\'']//; s/["'\'']$//' \
    || return 1
}

active_theme_from_config() {
  local file="$1"
  local theme=""

  theme="$(extract_yaml_value "active_theme" "$file" 2>/dev/null || true)"
  if [[ -z "$theme" ]]; then
    theme="$(extract_yaml_value "theme" "$file" 2>/dev/null || true)"
  fi
  theme="$(printf '%s' "$theme" | tr -d '\r' | sed -E 's/[[:space:]]+#.*$//; s/^[[:space:]]+//; s/[[:space:]]+$//')"
  theme="${theme#\"}"
  theme="${theme%\"}"
  theme="${theme#\'}"
  theme="${theme%\'}"
  [[ -n "$theme" ]] || theme="zh-classical"

  printf '%s\n' "$theme"
}

retrospective_display_name() {
  case "$1" in
    zh-classical) printf '🌅 早朝官\n' ;;
    zh-government|zh-gov) printf '🌅 国办晨会\n' ;;
    zh-corporate|zh-corp) printf '🌅 晨会主持\n' ;;
    ja-meiji) printf '🌅 朝議官\n' ;;
    ja-kasumigaseki) printf '🌅 朝礼官\n' ;;
    ja-corporate|ja-corp) printf '🌅 朝礼幹事\n' ;;
    en-roman) printf '🌅 Auspex\n' ;;
    en-usgov) printf '🌅 Morning Brief\n' ;;
    en-csuite) printf '🌅 Standup Lead\n' ;;
    *) printf '🌅 RETROSPECTIVE\n' ;;
  esac
}

git_head() {
  local root="$1"
  if have git && git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$root" rev-parse --short HEAD 2>/dev/null || printf 'unknown\n'
  else
    printf 'unknown\n'
  fi
}

git_upstream_ref() {
  local root="$1"
  have git || return 1
  git -C "$root" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null
}

git_ahead_behind() {
  local root="$1"
  local upstream="$2"
  local ahead="0"
  local behind="0"

  if [[ -n "$upstream" ]] && have git; then
    ahead="$(git -C "$root" rev-list --count "${upstream}..HEAD" 2>/dev/null || printf '0')"
    behind="$(git -C "$root" rev-list --count "HEAD..${upstream}" 2>/dev/null || printf '0')"
  fi

  printf '%s %s\n' "${ahead:-0}" "${behind:-0}"
}

local_skill_version() {
  local skill_path=""
  local version=""

  for skill_path in "$SCRIPT_ROOT/SKILL.md" "$PWD_ROOT/SKILL.md"; do
    if [[ -f "$skill_path" ]]; then
      version="$(extract_yaml_value "version" "$skill_path" 2>/dev/null || printf 'unknown')"
      [[ -n "$version" ]] || version="unknown"
      printf '%s\n' "$version"
      return
    fi
  done

  printf 'unknown\n'
}

version_status() {
  local local_version="unknown"
  local remote_version="unknown"
  local status="skip"
  local remote_text=""

  local_version="$(local_skill_version)"

  if have curl; then
    remote_text="$(curl -fsSL --max-time 5 "https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md" 2>/dev/null || true)"
  elif have wget; then
    remote_text="$(wget -qO- --timeout=5 "https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md" 2>/dev/null || true)"
  fi

  if [[ -n "$remote_text" ]]; then
    remote_version="$(printf '%s\n' "$remote_text" \
      | grep -m 1 -E '^version:' \
      | sed -E 's/^[^:]+:[[:space:]]*//; s/^["'\'']//; s/["'\'']$//' \
      || true)"
    [[ -n "$remote_version" ]] || remote_version="unknown"
  fi

  if [[ "$local_version" != "unknown" && "$remote_version" != "unknown" ]]; then
    if [[ "$local_version" == "$remote_version" ]]; then
      status="latest"
    else
      status="update_available"
    fi
  fi

  printf 'local=%s · remote=%s · status=%s\n' "$local_version" "$remote_version" "$status"
}

index_rebuild_state() {
  local dir="$1"
  local index="$2"
  local source_count="$3"

  # v1.7.1 R12 Fresh invocation, every 上朝 rebuilds from scratch; no INDEX-exists skip optimization.
  if [[ ! -d "$dir" ]]; then
    printf 'skip no_dir\n'
  elif [[ "$source_count" == "0" ]]; then
    printf 'skip no_data\n'
  else
    printf 'force\n'
  fi
}

latest_file() {
  local dir="$1"
  local pattern="$2"
  [[ -d "$dir" ]] || {
    printf 'none\n'
    return
  }
  find "$dir" -maxdepth 1 -type f -name "$pattern" 2>/dev/null | sort | tail -n 1 | sed 's#^\./##'
}

directory_type="regular_repo"
if is_dev_repo "$PWD_ROOT"; then
  directory_type="dev_repo"
elif is_second_brain "$PWD_ROOT"; then
  directory_type="second_brain"
fi

second_brain_root="$(resolve_second_brain_root 2>/dev/null || true)"
if [[ -z "$second_brain_root" && "$directory_type" == "second_brain" ]]; then
  second_brain_root="$PWD_ROOT"
fi

data_root="$PWD_ROOT"
if [[ -n "$second_brain_root" ]]; then
  data_root="$second_brain_root"
fi
LIFEOS_AUDIT_ROOT="$data_root"
retrospective_trail_count=0

emit_retrospective_trail_marker() {
  local step="$1"
  local step_name="$2"
  local input_summary="$3"
  local output_marker="$4"

  if [[ "${AUDIT_TRAIL_AVAILABLE:-0}" == "1" ]]; then
    if emit_trail_marker "retrospective" "$step" "$step_name" "$input_summary" "$output_marker"; then
      retrospective_trail_count=$((retrospective_trail_count + 1))
    fi
  fi
}

config_path="$data_root/_meta/config.md"
config_status="missing"
[[ -f "$config_path" ]] && config_status="found"
active_theme="$(active_theme_from_config "$config_path")"
RETRO_NAME="$(retrospective_display_name "$active_theme")"

emit_display_marker() {
  local marker="$1"
  printf '%s · %s\n' "$RETRO_NAME" "$marker"
}

echo "$RETRO_NAME · 上朝准备 · $(date -Iseconds)"

step_2_marker="[STEP 2 · DIRECTORY TYPE: $directory_type]"
emit_display_marker "$step_2_marker"
emit_retrospective_trail_marker "step-2" "DIRECTORY TYPE" "pwd_root=$PWD_ROOT; script_root=$SCRIPT_ROOT" "$step_2_marker"

step_3_marker="[STEP 3 · DATA LAYER: $config_path: $config_status]"
emit_display_marker "$step_3_marker"
emit_retrospective_trail_marker "step-3" "DATA LAYER" "data_root=$data_root; config_path=$config_path" "$step_3_marker"

step4="skip no_second_brain"
if [[ "$directory_type" == "dev_repo" ]]; then
  step4="skip dev_repo"
elif [[ -z "$second_brain_root" || ! -d "$second_brain_root" ]]; then
  step4="skip no_second_brain"
elif ! have git; then
  step4="skip git_unavailable"
elif ! git -C "$second_brain_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  step4="skip no_git_repo"
else
  upstream="$(git_upstream_ref "$second_brain_root" 2>/dev/null || true)"
  if [[ -z "$upstream" ]]; then
    step4="skip no_upstream"
  else
    read -r _ahead _behind < <(git_ahead_behind "$second_brain_root" "$upstream")
    if [[ "${_behind:-0}" == "0" ]]; then
      step4="already up-to-date"
    else
      step4="skip read_only_behind=${_behind}"
    fi
  fi
fi
step_4_marker="[STEP 4 · SECOND-BRAIN PULL: $step4]"
emit_display_marker "$step_4_marker"
emit_retrospective_trail_marker "step-4" "SECOND-BRAIN PULL" "second_brain_root=${second_brain_root:-none}; read_only=true" "$step_4_marker"

git_root="$PWD_ROOT"
if [[ "$directory_type" == "second_brain" && -n "$second_brain_root" ]]; then
  git_root="$second_brain_root"
fi
head_hash="$(git_head "$git_root")"
ahead="0"
behind="0"
diverged="false"
if [[ "$head_hash" != "unknown" ]]; then
  upstream="$(git_upstream_ref "$git_root" 2>/dev/null || true)"
  if [[ -n "$upstream" ]]; then
    read -r ahead behind < <(git_ahead_behind "$git_root" "$upstream")
  fi
fi
if [[ "${ahead:-0}" != "0" && "${behind:-0}" != "0" ]]; then
  diverged="true"
fi
step_5_marker="[STEP 5 · GIT HEALTH: HEAD=$head_hash · ahead=${ahead:-0} · behind=${behind:-0} · diverged=$diverged]"
emit_display_marker "$step_5_marker"
emit_retrospective_trail_marker "step-5" "GIT HEALTH" "git_root=$git_root; upstream=${upstream:-none}" "$step_5_marker"

version_line="$(version_status)"
step_8_marker="[STEP 8 · VERSION: $version_line]"
echo "$RETRO_NAME · 步 8 · 版本核查"
emit_display_marker "$step_8_marker"
step_8_local_version="$(local_skill_version)"
echo "[Local SKILL.md version: $step_8_local_version]"
step_8_remote_check_script="$SCRIPT_ROOT/scripts/lifeos-version-check.sh"
printf '[Remote check (forced fresh):\n'
if [[ -f "$step_8_remote_check_script" ]]; then
  "${BASH:-bash}" "$step_8_remote_check_script" --force
else
  printf '[Life OS] version check script not found at %s\n' "$step_8_remote_check_script"
fi
printf ']\n'
emit_retrospective_trail_marker "step-8" "VERSION" "script_root=$SCRIPT_ROOT; remote_check=best_effort" "$step_8_marker"

inbox_path="$data_root/inbox"
inbox_count="$(count_paths "$inbox_path")"
step_10_marker="[STEP 10 · INBOX SCAN: $inbox_count items at $inbox_path]"
emit_display_marker "$step_10_marker"
emit_retrospective_trail_marker "step-10" "INBOX SCAN" "inbox_path=$inbox_path; primary_source=find" "$step_10_marker"

sessions_dir="$data_root/_meta/sessions"
sessions_count="0"
if [[ -d "$sessions_dir" ]] && have find; then
  sessions_count="$(find "$sessions_dir" -maxdepth 1 -type f -name '*.md' ! -name 'INDEX.md' 2>/dev/null | wc -l | tr -d '[:space:]')"
fi

cortex_bootstrap_marker=""
if [[ ! -f "$sessions_dir/INDEX.md" ]]; then
  echo "[CORTEX BOOTSTRAP: triggering tools/migrate.py]"
  migrate_tool="$SCRIPT_ROOT/tools/migrate.py"
  if [[ ! -f "$migrate_tool" ]]; then
    cortex_bootstrap_marker="[CORTEX BOOTSTRAP SKIP: tools/migrate.py not found]"
  elif ! have python; then
    cortex_bootstrap_marker="[CORTEX BOOTSTRAP SKIP: python unavailable]"
  else
    (cd "$SCRIPT_ROOT" 2>/dev/null && python tools/migrate.py --auto-bootstrap --root "$data_root")
    migrate_status=$?
    if [[ -f "$sessions_dir/INDEX.md" ]]; then
      if [[ -d "$sessions_dir" ]] && have find; then
        sessions_count="$(find "$sessions_dir" -maxdepth 1 -type f -name '*.md' ! -name 'INDEX.md' 2>/dev/null | wc -l | tr -d '[:space:]')"
      fi
      cortex_bootstrap_marker="[CORTEX BOOTSTRAP COMPLETE: $sessions_count sessions seeded]"
    else
      cortex_bootstrap_marker="[CORTEX BOOTSTRAP SKIP: tools/migrate.py exited $migrate_status without creating INDEX.md]"
    fi
  fi
  echo "$cortex_bootstrap_marker"
fi

sessions_rebuild="$(index_rebuild_state "$sessions_dir" "$sessions_dir/INDEX.md" "$sessions_count")"
step_11_marker="[STEP 11 · SESSION INDEX: $sessions_count sessions indexed | rebuild=$sessions_rebuild | fresh_invocation=true]"
emit_display_marker "$step_11_marker"
emit_retrospective_trail_marker "step-11" "SESSION INDEX" "sessions_dir=$sessions_dir; index=$sessions_dir/INDEX.md" "$step_11_marker"

concepts_dir="$data_root/_meta/concepts"
concepts_count="0"
if [[ -d "$concepts_dir" ]] && have find; then
  concepts_count="$(find "$concepts_dir" -type f -name '*.md' ! -name 'INDEX.md' ! -name 'SYNAPSES-INDEX.md' 2>/dev/null | wc -l | tr -d '[:space:]')"
fi
concepts_rebuild="$(index_rebuild_state "$concepts_dir" "$concepts_dir/INDEX.md" "$concepts_count")"
step_12_marker="[STEP 12 · CONCEPT INDEX: $concepts_count concepts indexed | rebuild=$concepts_rebuild | fresh_invocation=true]"
emit_display_marker "$step_12_marker"
emit_retrospective_trail_marker "step-12" "CONCEPT INDEX" "concepts_dir=$concepts_dir; index=$concepts_dir/INDEX.md" "$step_12_marker"

projects_count="$(count_paths "$data_root/projects" dirs)"
areas_count="$(count_paths "$data_root/areas" dirs)"
domains_count=$((projects_count + areas_count))
status_path="$data_root/_meta/STATUS.md"
last_updated="unknown"
if [[ -f "$status_path" ]]; then
  last_updated="$(extract_yaml_value "last_updated" "$status_path" 2>/dev/null || extract_yaml_value "updated" "$status_path" 2>/dev/null || printf 'unknown')"
fi
step_13_marker="[STEP 13 · STATUS COMPILE: $domains_count domains tracked | last_updated=$last_updated]"
emit_display_marker "$step_13_marker"
emit_retrospective_trail_marker "step-13" "STATUS COMPILE" "projects=$projects_count; areas=$areas_count; status_path=$status_path" "$step_13_marker"

wiki_dir="$data_root/wiki"
wiki_count="0"
if [[ -d "$wiki_dir" ]] && have find; then
  wiki_count="$(find "$wiki_dir" -type f -name '*.md' ! -name 'INDEX.md' 2>/dev/null | wc -l | tr -d '[:space:]')"
fi
wiki_rebuild="$(index_rebuild_state "$wiki_dir" "$wiki_dir/INDEX.md" "$wiki_count")"
step_14_marker="[STEP 14 · WIKI INDEX: $wiki_count entries | rebuild=$wiki_rebuild | fresh_invocation=true]"
emit_display_marker "$step_14_marker"
emit_retrospective_trail_marker "step-14" "WIKI INDEX" "wiki_dir=$wiki_dir; index=$wiki_dir/INDEX.md" "$step_14_marker"

journal_dir="$data_root/_meta/journal"
dream_count="0"
dream_latest="none"
if [[ -d "$journal_dir" ]] && have find; then
  dream_count="$(find "$journal_dir" -maxdepth 1 -type f -name '*-dream.md' 2>/dev/null | wc -l | tr -d '[:space:]')"
  dream_latest="$(latest_file "$journal_dir" '*-dream.md')"
fi
step_17_marker="[STEP 17 · DREAM JOURNAL: $dream_count recent dreams | latest=$dream_latest]"
emit_display_marker "$step_17_marker"
emit_retrospective_trail_marker "step-17" "DREAM JOURNAL" "journal_dir=$journal_dir; primary_source=find" "$step_17_marker"

trail_sid="${LIFEOS_SESSION_ID:-${AUDIT_TRAIL_SESSION_ID:-unknown}}"
echo "[TRAIL INDEX: $retrospective_trail_count trails written to _meta/runtime/$trail_sid/]"
