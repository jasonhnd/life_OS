#!/usr/bin/env bash
# Life OS commit SHA fallback helpers.

_lifeos_sha_clean_value() {
  local value="${1:-}"

  value="$(
    printf '%s' "$value" \
      | tr -d '\r' \
      | sed -E "s/[[:space:]]+#.*$//; s/^[[:space:]]+//; s/[[:space:]]+$//; s/^['\"]//; s/['\"]$//"
  )"
  printf '%s\n' "$value"
}

_lifeos_sha_is_known() {
  local value

  value="$(_lifeos_sha_clean_value "${1:-}")"
  case "$value" in
    ""|unknown|UNKNOWN|Unknown|PLACEHOLDER|placeholder|Placeholder)
      return 1
      ;;
  esac
  return 0
}

_lifeos_sha_from_skill_frontmatter() {
  local root="${1:-.}"
  local skill_path="$root/SKILL.md"

  if [[ ! -f "$skill_path" ]]; then
    return 0
  fi

  awk '
    {
      line = $0
      sub(/\r$/, "", line)
    }
    NR == 1 {
      if (line != "---") {
        exit
      }
      in_frontmatter = 1
      next
    }
    in_frontmatter && line == "---" {
      exit
    }
    in_frontmatter && line ~ /^[[:space:]]*commit_sha[[:space:]]*:/ {
      sub(/^[[:space:]]*commit_sha[[:space:]]*:[[:space:]]*/, "", line)
      print line
      exit
    }
  ' "$skill_path" 2>/dev/null
}

_lifeos_sha_from_install_meta() {
  local root="${1:-.}"
  local meta_path="$root/.install-meta"

  if [[ ! -f "$meta_path" ]]; then
    return 0
  fi

  if command -v jq >/dev/null 2>&1; then
    jq -r '.commit_sha // empty' "$meta_path" 2>/dev/null || true
  else
    sed -n -E 's/.*"commit_sha"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/p' "$meta_path" 2>/dev/null | head -n 1
  fi
}

_lifeos_sha_from_git() {
  local root="${1:-.}"

  if command -v git >/dev/null 2>&1 && git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$root" rev-parse HEAD 2>/dev/null || true
  fi
}

resolve_lifeos_commit_sha() {
  local root="${1:-.}"
  local sha

  sha="$(_lifeos_sha_from_skill_frontmatter "$root")"
  sha="$(_lifeos_sha_clean_value "$sha")"
  if _lifeos_sha_is_known "$sha"; then
    printf '%s\n' "$sha"
    return 0
  fi

  sha="$(_lifeos_sha_from_install_meta "$root")"
  sha="$(_lifeos_sha_clean_value "$sha")"
  if _lifeos_sha_is_known "$sha"; then
    printf '%s\n' "$sha"
    return 0
  fi

  sha="$(_lifeos_sha_from_git "$root")"
  sha="$(_lifeos_sha_clean_value "$sha")"
  if _lifeos_sha_is_known "$sha"; then
    printf '%s\n' "$sha"
    return 0
  fi

  printf 'unknown\n'
}

resolve_lifeos_commit_sha_short() {
  local root="${1:-.}"
  local sha

  sha="$(resolve_lifeos_commit_sha "$root")"
  if ! _lifeos_sha_is_known "$sha"; then
    printf 'unknown\n'
    return 0
  fi

  printf '%.7s\n' "$sha"
}
