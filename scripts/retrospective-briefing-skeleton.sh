#!/usr/bin/env bash
# v1.7.2.3 · briefing skeleton — Bash output, LLM cannot omit.
# Read-only: emits the fixed six-H2 Start Session frame with measured facts.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
SCRIPT_ROOT="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd -P)"

for _sha_fallback_lib in "$SCRIPT_DIR/lib/sha-fallback.sh" "$SCRIPT_ROOT/scripts/lib/sha-fallback.sh"; do
  if [[ -r "$_sha_fallback_lib" ]]; then
    . "$_sha_fallback_lib" || true
    break
  fi
done
unset _sha_fallback_lib

PWD_ROOT="${1:-$(pwd -P 2>/dev/null || pwd)}"
cd "$PWD_ROOT" 2>/dev/null || {
  printf 'ERROR: cannot cd to %s\n' "$PWD_ROOT" >&2
  exit 1
}
PWD_ROOT="$(pwd -P 2>/dev/null || pwd)"

trim_count() {
  tr -d '[:space:]'
}

yaml_value() {
  local key="$1"
  local file="$2"
  [[ -f "$file" ]] || return 1
  grep -m1 -E "^[[:space:]]*${key}:" "$file" 2>/dev/null \
    | sed -E 's/^[^:]+:[[:space:]]*//; s/[[:space:]]+#.*$//; s/^[[:space:]]+//; s/[[:space:]]+$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//'
}

count_files() {
  local dir="$1"
  local pattern="$2"
  [[ -d "$dir" ]] || {
    printf '0\n'
    return
  }
  find "$dir" -type f -name "$pattern" 2>/dev/null | wc -l | trim_count
}

count_dirs() {
  local dir="$1"
  [[ -d "$dir" ]] || {
    printf '0\n'
    return
  }
  find "$dir" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | trim_count
}

print_first_files() {
  local dir="$1"
  local pattern="$2"
  local label="$3"
  if [[ ! -d "$dir" ]]; then
    printf "  - %s: none (directory missing)\n" "$label"
    return
  fi
  local printed=0
  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    printed=$((printed + 1))
    printf '  - %s #%s: %s\n' "$label" "$printed" "$path"
  done < <(find "$dir" -type f -name "$pattern" ! -name '.gitkeep' ! -name 'INDEX.md' 2>/dev/null | sort | head -5)
  [[ "$printed" -gt 0 ]] || printf "  - %s: none\n" "$label"
}

print_first_dirs() {
  local dir="$1"
  local label="$2"
  if [[ ! -d "$dir" ]]; then
    printf "  - %s: none (directory missing)\n" "$label"
    return
  fi
  local printed=0
  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    printed=$((printed + 1))
    printf '  - %s #%s: %s\n' "$label" "$printed" "$path"
  done < <(find "$dir" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | head -5)
  [[ "$printed" -gt 0 ]] || printf "  - %s: none\n" "$label"
}

ACTIVE_THEME=""
if [[ -f "_meta/config.md" ]]; then
  ACTIVE_THEME="$(yaml_value "active_theme" "_meta/config.md" 2>/dev/null || true)"
  [[ -n "$ACTIVE_THEME" ]] || ACTIVE_THEME="$(yaml_value "theme" "_meta/config.md" 2>/dev/null || true)"
fi
[[ -z "$ACTIVE_THEME" ]] && ACTIVE_THEME="zh-classical"

case "$ACTIVE_THEME" in
  zh-classical)     RETRO_NAME="🌅 早朝官" ;;
  zh-government)    RETRO_NAME="🌅 国办晨会" ;;
  zh-gov)           RETRO_NAME="🌅 国办晨会" ;;
  zh-corporate)     RETRO_NAME="🌅 晨会主持" ;;
  zh-corp)          RETRO_NAME="🌅 晨会主持" ;;
  ja-meiji)         RETRO_NAME="🌅 朝議官" ;;
  ja-kasumigaseki)  RETRO_NAME="🌅 朝礼官" ;;
  ja-corporate)     RETRO_NAME="🌅 朝礼幹事" ;;
  ja-corp)          RETRO_NAME="🌅 朝礼幹事" ;;
  en-roman)         RETRO_NAME="🌅 Auspex" ;;
  en-usgov)         RETRO_NAME="🌅 Morning Brief" ;;
  en-csuite)        RETRO_NAME="🌅 Standup Lead" ;;
  *)                RETRO_NAME="🌅 RETROSPECTIVE" ;;
esac

LOCAL_VER="$(yaml_value "version" "SKILL.md" 2>/dev/null || printf 'unknown')"
LOCAL_SHA=""
if command -v resolve_lifeos_commit_sha >/dev/null 2>&1; then
  LOCAL_SHA="$(resolve_lifeos_commit_sha "$SCRIPT_ROOT" 2>/dev/null || true)"
fi
if [[ -z "$LOCAL_SHA" || "$LOCAL_SHA" == "unknown" ]]; then
  LOCAL_SHA="$(git -C "$SCRIPT_ROOT" rev-parse HEAD 2>/dev/null || printf 'unknown')"
fi
REMOTE_SHA="$(git ls-remote origin HEAD 2>/dev/null | awk '{print $1}' | head -1)"
[[ -n "$REMOTE_SHA" ]] || REMOTE_SHA="unknown"

INBOX_COUNT="$(count_files "inbox" "*.md")"
PROJECT_COUNT="$(count_dirs "projects")"
WIKI_COUNT="$(count_files "wiki" "*.md")"
SESSION_COUNT="$(count_files "_meta/sessions" "*.md")"
CONCEPT_COUNT="$(count_files "_meta/concepts" "*.md")"

SOUL_DIM_COUNT=0
LATEST_SNAPSHOT=""
if [[ -f "SOUL.md" ]]; then
  SOUL_DIM_COUNT="$(grep -cE '^### ' SOUL.md 2>/dev/null || printf '0')"
  LATEST_SNAPSHOT="$(find _meta/snapshots/soul -name '*.md' 2>/dev/null | sort -r | head -1)"
fi
[[ -n "$LATEST_SNAPSHOT" ]] || LATEST_SNAPSHOT="none"

DREAM_COUNT="$(count_files "_meta/journal" "*-dream.md")"
LATEST_DREAM="$(find _meta/journal -name '*-dream.md' 2>/dev/null | sort -r | head -1)"
[[ -n "$LATEST_DREAM" ]] || LATEST_DREAM="none"

WORKTREE_COUNT="$(git status --short 2>/dev/null | wc -l | trim_count)"

echo "${RETRO_NAME} · 朝议简报 · $(date -Iseconds)"
echo
echo "## 0. ${RETRO_NAME} · 上朝准备"
echo
echo "- Life OS: local v${LOCAL_VER}"
echo "- [Local SKILL.md version: ${LOCAL_VER}]"
echo "- [Remote check (forced fresh): see Step 8 detail]"
echo "- [Local commit SHA: ${LOCAL_SHA}]"
echo "- [Remote commit SHA: ${REMOTE_SHA}]"
if [[ "$LOCAL_SHA" != "unknown" && "$REMOTE_SHA" != "unknown" && "$LOCAL_SHA" != "$REMOTE_SHA" ]]; then
  echo "- ⚠️ SHA gap: local commit differs from remote despite version string match"
  echo "  Run: git fetch origin --tags --force && git pull --rebase"
  echo "  Or:  git reset --hard origin/main (if force-pushed)"
fi
echo "- Cortex Step 0.5: pre-render skeleton emitted; detailed module status comes from retrospective-mode-0.sh."
echo
echo "## 1. 第二大脑同步状态"
echo
echo "- Inbox: ${INBOX_COUNT} 项"
print_first_files "inbox" "*.md" "Inbox"
echo "- Projects: ${PROJECT_COUNT} 个 active candidates"
print_first_dirs "projects" "Project"
echo "- Wiki: ${WIKI_COUNT} entries"
print_first_files "wiki" "*.md" "Wiki"
echo "- Sessions: ${SESSION_COUNT} files"
echo "- Concepts: ${CONCEPT_COUNT} files"
echo "- 二脑健康综评: Bash skeleton measured primary-source counts only; sync freshness remains orchestrator-owned."
echo
echo "## 2. SOUL Health 报告"
echo
if [[ -f "SOUL.md" ]]; then
  echo "- SOUL: ${SOUL_DIM_COUNT} dimensions · Latest snapshot: ${LATEST_SNAPSHOT}"
  echo
  echo "**完整 SOUL.md 内容**(Bash paste · LLM 不能压缩):"
  echo
  echo '```markdown'
  cat SOUL.md
  echo '```'
  echo
  echo "**LLM 解读**(基于上面 SOUL 全文):"
  echo "- Confidence trend (changed dimensions only): <!-- LLM_FILL: soul_confidence_trend -->"
  echo "- 新候补: <!-- LLM_FILL: soul_candidates_if_any -->"
else
  echo "- SOUL.md not present (会在累积足够 evidence 后由 archiver 自动初次写入)"
fi
echo
echo "## 3. DREAM / 隔夜更新"
echo
echo "- ${DREAM_COUNT} dream reports · Latest: ${LATEST_DREAM}"
if [[ "$LATEST_DREAM" != "none" && -f "$LATEST_DREAM" ]]; then
  echo
  echo "**完整最新 DREAM 报告**(Bash paste · LLM 不能压缩):"
  echo
  echo '```markdown'
  cat "$LATEST_DREAM"
  echo '```'
  echo
  echo "**LLM 解读**(基于上面 DREAM 全文):"
  echo "- Today implications: <!-- LLM_FILL: dream_implications_for_today -->"
else
  echo "- 无隔夜 DREAM(下次退朝会跑 Phase 3 DREAM 写新报告)"
fi
echo
echo "## 4. Today's Focus + 待陛下圣裁"
echo
echo "<!-- LLM_FILL: today_focus_and_pending_decisions -->"
echo "(LLM judgment based on inbox/projects/SOUL/DREAM data above)"
echo
echo "## 5. 系统状态"
echo
echo "- 御史台静默 · 系统健康"
echo "- 工作树: ${WORKTREE_COUNT} 文件待处理"
echo "- 违规详情如需查看: /audit 或 violations.md"

exit 0
