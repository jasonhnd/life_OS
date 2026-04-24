#!/usr/bin/env bash
set -euo pipefail

program=${0##*/}
original_home=${HOME:-}

usage() {
  cat <<'EOF'
Usage: skills-test-setup.sh [--no-cache] [--root DIR | DIR] [--home DIR]

Creates an isolated HOME containing Life OS skill-observability fixtures.

Inputs:
  DIR                         Fixture root; HOME is created as DIR/home.
  --root DIR                  Same as positional DIR.
  --home DIR                  Explicit isolated HOME to populate.
  --no-cache                  Do not create skills-upstream.json.

Environment:
  LIFE_OS_FIXTURE_ROOT        Fixture root used when no DIR is passed.
  LIFE_OS_FIXTURE_HOME        Explicit isolated HOME used when --home is absent.
  TMPDIR                      Parent for the default mktemp fixture root.
  LIFE_OS_SKILLS_FIXTURE_NO_CACHE=1
                              Same as --no-cache.

The script writes DIR/skills-fixture.env with exports for eval runners.
EOF
}

die() {
  printf '%s: %s\n' "$program" "$*" >&2
  exit 1
}

absolute_path() {
  local path=$1

  [ -n "$path" ] || return 1
  case "$path" in
    /*|[A-Za-z]:/*|[A-Za-z]:\\*) printf '%s\n' "$path" ;;
    *) printf '%s\n' "$(pwd -P)/$path" ;;
  esac
}

strip_trailing_slashes() {
  local path=$1

  while [ "$path" != "/" ] && [ "${path%/}" != "$path" ]; do
    path=${path%/}
  done
  printf '%s\n' "$path"
}

is_root_like() {
  local path

  path=$(strip_trailing_slashes "$1")
  case "$path" in
    ''|'/'|'\'|[A-Za-z]:|[A-Za-z]:/|[A-Za-z]:\\) return 0 ;;
  esac
  return 1
}

is_truthy() {
  case "${1:-}" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
  esac
  return 1
}

make_temp_root() {
  local base fallback

  base=${TMPDIR:-/tmp}
  base=${base%/}
  if command -v mktemp >/dev/null 2>&1; then
    mktemp -d "$base/life-os-skills-fixture.XXXXXX"
  else
    fallback="$base/life-os-skills-fixture.$$"
    mkdir -p "$fallback"
    printf '%s\n' "$fallback"
  fi
}

write_export() {
  local name=$1
  local value=$2

  printf 'export %s=%q\n' "$name" "$value"
}

fixture_root=${LIFE_OS_FIXTURE_ROOT:-}
fixture_home=${LIFE_OS_FIXTURE_HOME:-}
no_cache=0

if is_truthy "${LIFE_OS_SKILLS_FIXTURE_NO_CACHE:-}"; then
  no_cache=1
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --no-cache)
      no_cache=1
      ;;
    --root)
      shift
      [ "$#" -gt 0 ] || die '--root requires a directory'
      [ -z "$fixture_root" ] || die 'fixture root was provided more than once'
      fixture_root=$1
      ;;
    --home)
      shift
      [ "$#" -gt 0 ] || die '--home requires a directory'
      [ -z "$fixture_home" ] || die 'fixture home was provided more than once'
      fixture_home=$1
      ;;
    --)
      shift
      [ "$#" -eq 0 ] || die 'unexpected arguments after --'
      ;;
    -*)
      die "unknown option: $1"
      ;;
    *)
      [ -z "$fixture_root" ] || die 'fixture root was provided more than once'
      fixture_root=$1
      ;;
  esac
  shift
done

if [ -n "$fixture_home" ]; then
  home_dir=$(absolute_path "$fixture_home") || die 'fixture home must not be empty'
  if [ -z "$fixture_root" ]; then
    fixture_root=$(dirname "$home_dir")
  fi
else
  if [ -z "$fixture_root" ]; then
    fixture_root=$(make_temp_root)
  else
    fixture_root=$(absolute_path "$fixture_root") || die 'fixture root must not be empty'
  fi
  home_dir="$fixture_root/home"
fi

fixture_root=$(strip_trailing_slashes "$(absolute_path "$fixture_root")")
home_dir=$(strip_trailing_slashes "$home_dir")

is_root_like "$home_dir" && die "refusing root-like fixture HOME: $home_dir"

if [ -n "$original_home" ]; then
  original_home_abs=$(strip_trailing_slashes "$(absolute_path "$original_home")")
  if [ "$home_dir" = "$original_home_abs" ]; then
    tmp_base=$(strip_trailing_slashes "$(absolute_path "${TMPDIR:-/tmp}")")
    case "$home_dir/" in
      "$tmp_base"/*) ;;
      *) die "refusing to use the current real HOME as fixture HOME: $home_dir" ;;
    esac
  fi
fi

marker="$home_dir/.life-os-fixture-home"
if [ ! -f "$marker" ]; then
  if [ -e "$home_dir/.claude" ] || [ -e "$home_dir/.cache/life-os" ]; then
    die "refusing to overwrite an existing HOME without fixture marker: $home_dir"
  fi
fi

mkdir -p "$home_dir"
printf 'life-os skills eval fixture\n' > "$marker"

export HOME=$home_dir
export LIFE_OS_SKILLS_DIR="$HOME/.claude/skills"
export LIFE_OS_PLUGINS_DIR="$HOME/.claude/plugins"
cache_dir="$HOME/.cache/life-os"
cache_file="$cache_dir/skills-upstream.json"
env_file="$fixture_root/skills-fixture.env"

rm -rf "$HOME/.claude/skills" "$HOME/.claude/plugins" "$cache_dir"
mkdir -p \
  "$LIFE_OS_SKILLS_DIR/imagegen" \
  "$LIFE_OS_SKILLS_DIR/openai-docs" \
  "$LIFE_OS_SKILLS_DIR/broken-skill" \
  "$LIFE_OS_SKILLS_DIR/local-only" \
  "$LIFE_OS_PLUGINS_DIR/imagegen" \
  "$cache_dir"

cat > "$LIFE_OS_SKILLS_DIR/imagegen/SKILL.md" <<'EOF'
---
name: imagegen
version: 1.2.0
installed-at: 2026-04-20T10:00:00+09:00
source: github://alchaincyf/huashu-design
description: Generate or edit raster images for Life OS work products.
triggers:
  - image
  - edit picture
  - create illustration
  - mockup
---
# imagegen
EOF

cat > "$LIFE_OS_SKILLS_DIR/openai-docs/SKILL.md" <<'EOF'
---
name: openai-docs
version: 0.9.0
installed-at: 2026-04-10T10:00:00+09:00
source: npm://openai-docs
description: Use official OpenAI documentation for API and model questions.
triggers:
  - OpenAI API
  - docs
  - model
  - prompt migration
---
# openai-docs
EOF

cat > "$LIFE_OS_SKILLS_DIR/broken-skill/SKILL.md" <<'EOF'
---
name: broken-skill
version: 0.0.1
installed-at: 2026-04-18T10:00:00+09:00
source: pypi://broken-skill
description: Fixture whose upstream cache is stale and therefore check-failed.
triggers:
  - broken
  - timeout
  - diagnose
  - recover
---
# broken-skill

This fixture is parseable; its stale cache evidence exercises graceful
check-failed behavior without triggering data-source corruption.
EOF

cat > "$LIFE_OS_SKILLS_DIR/local-only/SKILL.md" <<'EOF'
---
name: local-only
version: 0.1.0
installed-at: 2025-12-15T10:00:00+09:00
source: local
description: Local-only fixture with no upstream cache entry.
triggers:
  - start
  - 上朝
  - begin
  - local ceremony
---
# local-only
EOF

cat > "$LIFE_OS_PLUGINS_DIR/imagegen/SKILL.md" <<'EOF'
---
name: imagegen
version: 0.8.0
installed-at: 2026-04-01T10:00:00+09:00
source: plugins://imagegen
description: Shadowed plugin copy that must not override skills://imagegen.
triggers:
  - plugin image
  - legacy image
  - raster
---
# imagegen plugin copy
EOF

if [ "$no_cache" -eq 0 ]; then
  cat > "$cache_file" <<'EOF'
{
  "cache_path": "~/.cache/life-os/skills-upstream.json",
  "schema_version": 1,
  "generated_at": "2026-04-22T10:00:00+09:00",
  "ttl_seconds": 86400,
  "entries": {
    "github://alchaincyf/huashu-design": {
      "latest_version": "1.2.0",
      "fetched_at": "2026-04-22T10:00:00+09:00",
      "url": "https://api.github.com/repos/alchaincyf/huashu-design/releases/latest"
    },
    "npm://openai-docs": {
      "latest_version": "1.0.0",
      "fetched_at": "2026-04-22T10:00:00+09:00",
      "url": "https://registry.npmjs.org/openai-docs/latest"
    },
    "pypi://broken-skill": {
      "latest_version": "0.0.1",
      "fetched_at": "2026-01-14T10:00:00+09:00",
      "url": "https://pypi.org/pypi/broken-skill/json"
    }
  },
  "skills": {
    "imagegen": {
      "latest": "1.2.0",
      "fetched_at": "2026-04-22T10:00:00+09:00",
      "result": "success"
    },
    "openai-docs": {
      "latest": "1.0.0",
      "fetched_at": "2026-04-22T10:00:00+09:00",
      "result": "success"
    },
    "legacy-local": {
      "latest": "0.2.0",
      "fetched_at": "2025-12-01T00:00:00+09:00",
      "result": "expired"
    },
    "broken-skill": {
      "latest": "0.0.1",
      "fetched_at": "2026-01-14T10:00:00+09:00",
      "result": "expired",
      "last_error": "timeout"
    }
  }
}
EOF
else
  rm -f "$cache_file"
fi

if command -v touch >/dev/null 2>&1; then
  touch -t 202604201000.00 "$LIFE_OS_SKILLS_DIR/imagegen/SKILL.md" || true
  touch -t 202604101000.00 "$LIFE_OS_SKILLS_DIR/openai-docs/SKILL.md" || true
  touch -t 202604181000.00 "$LIFE_OS_SKILLS_DIR/broken-skill/SKILL.md" || true
  touch -t 202512151000.00 "$LIFE_OS_SKILLS_DIR/local-only/SKILL.md" || true
  touch -t 202604011000.00 "$LIFE_OS_PLUGINS_DIR/imagegen/SKILL.md" || true
  [ "$no_cache" -eq 1 ] || touch -t 202604221000.00 "$cache_file" || true
fi

{
  printf '# Source this file before running skill-observability evals.\n'
  write_export HOME "$HOME"
  write_export USERPROFILE "$HOME"
  write_export LIFE_OS_FIXTURE_ROOT "$fixture_root"
  write_export LIFE_OS_SKILLS_DIR "$LIFE_OS_SKILLS_DIR"
  write_export LIFE_OS_PLUGINS_DIR "$LIFE_OS_PLUGINS_DIR"
  write_export LIFE_OS_SKILLS_UPSTREAM_CACHE "$cache_file"
  write_export LIFE_OS_SKILLS_FIXTURE_ENV "$env_file"
} > "$env_file"

printf 'fixture_root=%s\n' "$fixture_root"
printf 'home=%s\n' "$HOME"
printf 'skills_dir=%s\n' "$LIFE_OS_SKILLS_DIR"
printf 'plugins_dir=%s\n' "$LIFE_OS_PLUGINS_DIR"
if [ "$no_cache" -eq 0 ]; then
  printf 'cache=%s\n' "$cache_file"
else
  printf 'cache_absent=%s\n' "$cache_file"
fi
printf 'env_file=%s\n' "$env_file"
