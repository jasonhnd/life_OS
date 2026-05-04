#!/bin/bash
# Life OS · pre-write-output-redirect.sh (v1.8.2)
# ─────────────────────────────────────────────────────────────────────────────
# Event:   PreToolUse
# Matcher: Write
# Exit:    0 (allow) | 2 (block + redirect suggestion)
# Timeout: 5s
#
# Purpose
#   Catch when a skill or agent tries to write a binary/output file
#   (HTML, PDF, DOCX, XLSX, ZIP, image, audio, video) to a path inside
#   the user's vault or Life OS workspace. Redirect to the OS Downloads
#   folder so user-facing exports land where the user looks for them
#   — not buried inside `_meta/` or vault subdirectories.
#
# Why this exists
#   Some Claude Code skills (PDF generators, HTML report builders, image
#   exporters) default to writing into cwd. Cwd is often the user's vault
#   or Life OS workspace, which then accumulates random binary outputs
#   over time. The user expects exports in `~/Downloads/`, not buried in
#   wiki/ subdirectories.
#
# Behaviour
#   - Reads JSON from stdin (Claude Code hook protocol)
#   - Extracts tool_input.file_path
#   - If extension is binary/output AND path is inside vault → exit 2 with
#     a "please write to ~/Downloads/lifeos-export-<date>/<filename>" hint
#   - Otherwise exit 0 silently (markdown / json / yaml / source code pass
#     through; vault-internal binary that's clearly intentional like
#     wiki/diagram.png stored inside the entry also passes via the
#     KNOWN_VAULT_PATHS_FOR_BINARIES allowlist)
#
# Bypass
#   - export LIFEOS_OUTPUT_REDIRECT_OFF=1 (per-session bypass)
#   - Or write directly to ~/Downloads/... yourself (no redirect needed)
#
# Cross-platform Downloads detection
#   - macOS / Linux: $HOME/Downloads (or $XDG_DOWNLOAD_DIR if set)
#   - Windows MSYS / Git Bash: $USERPROFILE/Downloads (translated to
#     /c/Users/<user>/Downloads in MSYS)
# ─────────────────────────────────────────────────────────────────────────────

set -u

# ─── Bypass switches (early exit) ───────────────────────────────────────────
if [ "${LIFEOS_OUTPUT_REDIRECT_OFF:-0}" = "1" ]; then
  exit 0
fi

INPUT="$(cat)"
if [ -z "$INPUT" ]; then
  exit 0
fi

# ─── Detect parsing tools ───────────────────────────────────────────────────
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  PYTHON=""
fi

# ─── Extract tool_name + file_path ──────────────────────────────────────────
TOOL_NAME=""
FILE_PATH=""
if command -v jq >/dev/null 2>&1; then
  TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null || echo "")"
  FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")"
elif [ -n "$PYTHON" ]; then
  PARSED="$(printf '%s' "$INPUT" | "$PYTHON" -c "
import json, sys
try:
    d = json.load(sys.stdin)
    tn = d.get('tool_name', '') or ''
    fp = d.get('tool_input', {}).get('file_path', '') or ''
    print(tn + '\\x1f' + fp)
except Exception:
    pass
" 2>/dev/null)"
  TOOL_NAME="${PARSED%%$'\x1f'*}"
  FILE_PATH="${PARSED#*$'\x1f'}"
  [ "$FILE_PATH" = "$PARSED" ] && FILE_PATH=""
fi

# Only act on Write (Edit modifies existing files; existing path already approved)
case "$TOOL_NAME" in
  Write) : ;;
  *) exit 0 ;;
esac

# Empty file_path = nothing to check
[ -z "$FILE_PATH" ] && exit 0

# ─── Detect "binary output" extension ───────────────────────────────────────
# Lowercase the extension for matching.
EXT_LOWER="$(printf '%s' "$FILE_PATH" | awk -F. '{print tolower($NF)}')"

# Binary / user-facing output formats. NOT a complete list — only the
# common cases users actually want in Downloads. Add via PR if a real
# case is missed.
BINARY_OUTPUT_EXTS=(
  # documents
  pdf docx xlsx pptx odt ods odp rtf
  # web exports
  html htm
  # archives
  zip tar gz tgz bz2 xz 7z rar
  # images (export, not in-vault inline)
  png jpg jpeg gif svg webp ico bmp tiff tif heic
  # audio
  mp3 wav m4a aac flac ogg opus
  # video
  mp4 webm mov avi mkv
  # ebooks
  epub mobi azw3
  # fonts (rare but possible)
  ttf otf woff woff2
)

IS_BINARY_OUTPUT=0
for ext in "${BINARY_OUTPUT_EXTS[@]}"; do
  if [ "$EXT_LOWER" = "$ext" ]; then
    IS_BINARY_OUTPUT=1
    break
  fi
done

# Not a binary output → pass through (markdown / json / yaml / source code)
[ "$IS_BINARY_OUTPUT" -eq 0 ] && exit 0

# ─── Resolve target path to absolute (best effort) ──────────────────────────
case "$FILE_PATH" in
  /*) ABS_PATH="$FILE_PATH" ;;          # already absolute Unix path
  ?:[/\\]*) ABS_PATH="$FILE_PATH" ;;    # Windows drive letter (D:\... or D:/...)
  *)
    # Relative — resolve against cwd
    ABS_PATH="$(pwd 2>/dev/null)/$FILE_PATH"
    ;;
esac

# Normalize backslashes to forward slashes (Windows path interop)
ABS_PATH="$(printf '%s' "$ABS_PATH" | tr '\\' '/')"

# ─── Detect Downloads folder (cross-platform) ───────────────────────────────
DOWNLOADS_DIR=""

# 1. XDG_DOWNLOAD_DIR (Linux, freedesktop.org spec)
if [ -n "${XDG_DOWNLOAD_DIR:-}" ] && [ -d "$XDG_DOWNLOAD_DIR" ]; then
  DOWNLOADS_DIR="$XDG_DOWNLOAD_DIR"
fi

# 2. macOS / Linux default
if [ -z "$DOWNLOADS_DIR" ] && [ -n "${HOME:-}" ] && [ -d "$HOME/Downloads" ]; then
  DOWNLOADS_DIR="$HOME/Downloads"
fi

# 3. Windows via USERPROFILE (works in Git Bash / MSYS)
if [ -z "$DOWNLOADS_DIR" ] && [ -n "${USERPROFILE:-}" ]; then
  # Translate Windows path (C:\Users\name) to MSYS form (/c/Users/name) if needed
  WIN_DOWNLOADS="$USERPROFILE/Downloads"
  WIN_DOWNLOADS_MSYS="$(printf '%s' "$WIN_DOWNLOADS" | sed 's|^\([A-Za-z]\):|/\L\1|; s|\\|/|g')"
  if [ -d "$WIN_DOWNLOADS_MSYS" ]; then
    DOWNLOADS_DIR="$WIN_DOWNLOADS_MSYS"
  elif [ -d "$WIN_DOWNLOADS" ]; then
    DOWNLOADS_DIR="$WIN_DOWNLOADS"
  fi
fi

# 4. Fallback: $HOME/Downloads even if dir doesn't exist (we suggest it)
if [ -z "$DOWNLOADS_DIR" ] && [ -n "${HOME:-}" ]; then
  DOWNLOADS_DIR="$HOME/Downloads"
fi

# 5. Last resort
[ -z "$DOWNLOADS_DIR" ] && DOWNLOADS_DIR="/tmp"

# ─── Already heading for Downloads? Pass through ────────────────────────────
DOWNLOADS_NORM="$(printf '%s' "$DOWNLOADS_DIR" | tr '\\' '/')"
case "$ABS_PATH" in
  "$DOWNLOADS_NORM"/*) exit 0 ;;
  */Downloads/*) exit 0 ;;     # any path containing /Downloads/
esac

# ─── Allowlist: in-vault binaries that are intentional ──────────────────────
# `wiki/<entry>/<image>.png` and `wiki/.attachments/` are vault-internal
# images intentionally stored alongside entries (referenced via `![[...]]`).
# Don't redirect these.
case "$ABS_PATH" in
  */wiki/.attachments/*) exit 0 ;;
  */wiki/*/attachments/*) exit 0 ;;
  */_meta/inbox/to-process/*) exit 0 ;;   # user can drop anything in inbox
  */_meta/inbox/archive/*) exit 0 ;;
  */assets/*) exit 0 ;;                   # repo-root assets/ for skill assets
esac

# ─── Build redirect suggestion ──────────────────────────────────────────────
BASENAME="$(basename "$FILE_PATH")"
DATE_TAG="$(date +%Y-%m-%d 2>/dev/null || echo unknown-date)"
SUGGESTED="$DOWNLOADS_DIR/lifeos-export-$DATE_TAG/$BASENAME"

# ─── Emit fail-CLOSED block + redirect suggestion ───────────────────────────
cat >&2 <<EOF
📁 Life OS · output redirect (v1.8.2 HARD RULE)

  Blocked Write: $FILE_PATH
  Reason: ".$EXT_LOWER" is a binary / user-facing output format. These
          should land in the OS Downloads folder so the user can find
          them — not inside the vault or workspace.

  Suggested target:
    $SUGGESTED

  How to proceed:
    a) Re-issue the Write with file_path = "$SUGGESTED" (recommended)
    b) Pick another path under your Downloads folder
    c) Bypass for this session: export LIFEOS_OUTPUT_REDIRECT_OFF=1
       (then retry; only do this if the file genuinely belongs in the vault)

  In-vault binary exceptions (these are NOT redirected):
    - wiki/.attachments/<file>     (image stored alongside wiki entries)
    - wiki/*/attachments/<file>
    - _meta/inbox/to-process/<file> (user drop zone)
    - _meta/inbox/archive/<file>
    - assets/<file>                (repo-root skill assets)

  Style guide: references/obsidian-style.md (HARD RULE #11)
EOF
exit 2
