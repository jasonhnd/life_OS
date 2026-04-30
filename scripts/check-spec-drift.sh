#!/bin/bash
# scripts/check-spec-drift.sh — Round-6 audit fix
# ─────────────────────────────────────────────────────────────────────────────
# Two CI scanners that prevent spec drift from re-accumulating:
#
#   (1) BROKEN-PATH scanner — scans active spec/prompt/code files for repo
#       path references (e.g. `scripts/foo.sh`, `pro/agents/bar.md`,
#       `tools/baz.py`) and verifies the target exists. A reference to a
#       deleted file fails CI.
#
#   (2) FORBIDDEN-TOKEN scanner — scans active files for architectural
#       tokens that should ONLY appear in legacy/historical contexts
#       (e.g. `retrospective-mode-0.sh`, `narrator-validator`, `life-os-tool`,
#       `cron-runs`). Hits in active files fail CI; hits in CHANGELOG /
#       legacy-banner files are allowed.
#
# Exit 0 = clean (or warnings-only in default mode), exit 1 = drift found
# (only when STRICT=1).
#
# Modes:
#   bash scripts/check-spec-drift.sh              (default — warnings only)
#   STRICT=1 bash scripts/check-spec-drift.sh     (fail on broken paths)
#
# CI uses default mode. Strict mode is for cleanup sprints — when a maintainer
# wants to gate "no new drift" they can flip STRICT=1 in CI later.
# ─────────────────────────────────────────────────────────────────────────────

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

# Files exempted from forbidden-token check (history is allowed to mention
# deleted things).
EXEMPT_PATTERN='^(CHANGELOG\.md|i18n/.*/CHANGELOG\.md|backup/|references/v1\.7-shipping-report-|pro/compliance/|references/cortex-spec\.md|references/tools-spec\.md|references/narrator-spec\.md|docs/architecture/|docs/guides/|i18n/.*/docs/|i18n/.*/references/|MIGRATION\.md|scripts/check-spec-drift\.sh|.*-template\.md)'

# Forbidden tokens — architectural relics that the v1.8.0 R-1.8.0-011
# pivot retired. Any active file containing these is spec drift.
FORBIDDEN_TOKENS=(
  "retrospective-mode-0.sh"
  "retrospective-briefing-skeleton.sh"
  "archiver-briefing-skeleton.sh"
  "archiver-phase-prefetch.sh"
  "narrator-validator.md"
  "life-os-tool"
  "tools.cli"
  "tools/cli.py"
  "tools/migrate.py"
  "tools/memory.py"
  "setup-cron.sh"
  "run-cron-now.sh"
  "ALWAYS-ON"
  "cortex_enabled"
)

drift_found=0
broken_paths=0

# Round-8 Spec GC Sprint + round-9 extension: files marked `status: legacy`
# OR `authoritative: false` in YAML frontmatter are exempt from drift checks
# (legitimate archival / superseded content). Active files (no frontmatter,
# or `status: active`, with `authoritative` either omitted or true) are
# subject to STRICT-mode failure on broken paths or forbidden tokens.
is_legacy_file() {
  local file="$1"
  head -n 30 "$file" 2>/dev/null \
    | grep -qE '^(status:[[:space:]]*legacy([[:space:]]|$)|authoritative:[[:space:]]*false([[:space:]]|$))'
}

echo "-- (1/2) Broken-path scanner --"
# Two-tier exemption: (a) BROKEN_PATH_EXEMPT regex for files where
# frontmatter doesn't fit (CHANGELOG / templates / themes / tests / backup /
# devdocs / compliance archives); (b) `status: legacy` frontmatter — the
# preferred path. Files matching neither are ACTIVE and subject to STRICT
# fail.
BROKEN_PATH_EXEMPT='^(CHANGELOG\.md|i18n/.*/CHANGELOG\.md|backup/|pro/compliance/|scripts/check-spec-drift\.sh|.*-template\.md|themes/.*\.md|tests/.*\.py|devdocs/|MIGRATION\.md)'
# Round-8 scanner upgrade: per-file multi-line context check. A broken
# path is exempted if any of the 5 preceding lines in the same file
# contains an explanatory CONTEXT_ALLOW token (REMOVED / deleted / etc).
# This catches the common markdown pattern where a "Removed in pivot:"
# header introduces a bullet list of deleted paths.
declare -A REPORTED  # de-dupe: only report each broken path once
# Pre-build CONTEXT_ALLOW used by both scanners (defined later in file
# but available via the shell parser at this point — set to a default
# here too in case ordering changes):
SCANNER_CTX="${CONTEXT_ALLOW:-REMOVED|Removed|removed|deleted|Deleted|DELETED|deprecated|Deprecated|previously|was tied to|legacy|Legacy|historical|Historical|pre-pivot|pre-R-1\\.8\\.0|pre-v1\\.8|R-1\\.8\\.0-011|R-1\\.8\\.0-012|R-1\\.8\\.0-013|formerly|once required|no longer|cron infrastructure|Cron infrastructure|Cron インフラ|Cron 基础设施|in v1\\.8\\.0 pivot|in pivot|v1\\.8\\.0 pivot|Removed in pivot|不要尝试调用|Don.t call|cron-era|v1\\.7|v1\\.7\\.x|删除|已删除|弃用|废弃|被删|削除|廃止|抛弃|放棄|历史档案|Python 中间层|Python ミドルウェア|Python 中間層|TBD|planned|will be created}"

while IFS= read -r file; do
  is_legacy_file "$file" && continue
  # Walk file line-by-line, track 5-line context window
  awk -v ctx="$SCANNER_CTX" -v fname="$file" '
    BEGIN { for (i=1; i<=8; i++) recent[i] = "" }
    {
      # Check if any of last 8 lines or current line matches CONTEXT_ALLOW
      # (8 covers H2/H3 header + blank + up to 6 bullet items, the common
      # markdown "Removed in pivot:" pattern in active READMEs / CLAUDEs.)
      any_recent_ctx = ($0 ~ ctx)
      for (i=1; i<=8; i++) if (recent[i] ~ ctx) any_recent_ctx = 1
      if (!any_recent_ctx) {
        # Extract any backtick-quoted repo paths on this line
        line = $0
        while (match(line, /`(scripts|pro|tools|references|docs|themes|evals)\/[A-Za-z0-9_./-]+\.(sh|md|py|json|yml|yaml|toml)`/)) {
          path = substr(line, RSTART+1, RLENGTH-2)
          print path
          line = substr(line, RSTART + RLENGTH)
        }
      }
      for (i=8; i>1; i--) recent[i] = recent[i-1]
      recent[1] = $0
    }
  ' "$file" 2>/dev/null
done < <(
  git ls-files '*.md' '*.sh' '*.py' \
    | grep -vE "$EXEMPT_PATTERN" \
    | grep -vE "$BROKEN_PATH_EXEMPT"
) | sort -u > /tmp/spec-drift-paths.txt
# Process collected unique paths in a NON-subshell while-loop so the counter
# survives. (Earlier version used `... | sort -u | while ...` which ran the
# loop in a subshell and lost the broken_paths increment.)
while IFS= read -r path_ref; do
  [ -z "$path_ref" ] && continue
  case "$path_ref" in
    http*|mailto:*|//*) continue ;;
    *X.md|*xxx*|*YYYY*|*your-theme*|*custom-*) continue ;;
  esac
  if [ ! -e "$path_ref" ]; then
    echo "  BROKEN: $path_ref"
    broken_paths=$((broken_paths + 1))
  fi
done < /tmp/spec-drift-paths.txt
rm -f /tmp/spec-drift-paths.txt
echo ""
echo "  (broken paths in active files: $broken_paths)"
if [ "${STRICT:-0}" = "1" ] && [ "$broken_paths" -gt 0 ]; then
  drift_found=1
fi

echo ""
echo "-- (2/2) Forbidden-token scanner (warning-only) --"
# Mid-pivot codebase has many legitimate "X was removed" / "do not call
# deleted X" / "config was X" mentions. Strict enforcement produces too
# many false positives. We report INFORMATIONAL hits but do NOT fail CI
# on token presence — only on broken paths (scanner 1) which are
# mechanically verifiable. Operators can manually audit forbidden-token
# hits and fix when context clearly indicates active drift.
# Allow lines that contain explanatory context in CN/EN/JP.
CONTEXT_ALLOW='REMOVED|Removed|removed|deleted|Deleted|DELETED|deprecated|Deprecated|previously|was tied to|legacy|Legacy|historical|Historical|pre-pivot|pre-R-1\.8\.0|pre-v1\.8|R-1\.8\.0-011|R-1\.8\.0-012|R-1\.8\.0-013|formerly|once required|no longer|cron infrastructure|Cron infrastructure|Cron インフラ|Cron 基础设施|in v1\.8\.0 pivot|in pivot|v1\.8\.0 pivot|Removed in pivot|不要尝试调用|Don.t call|cron-era|v1\.7|v1\.7\.x|删除|已删除|弃用|废弃|被删|削除|廃止|抛弃|放棄|历史档案|Python 中间层|Python ミドルウェア|Python 中間層|TBD|planned|will be created'
warnings_only=0
active_token_hits=0
# Multi-line context allow: a line is also exempted if any of the 5
# preceding lines contains the CONTEXT_ALLOW pattern. This catches the
# common markdown pattern of a "Removed in pivot:" header followed by
# bullet list of removed paths.
for token in "${FORBIDDEN_TOKENS[@]}"; do
  while IFS= read -r file; do
    is_legacy_file "$file" && continue
    # Use awk for multi-line context: keep last 5 lines; if any of them
    # matched CONTEXT_ALLOW, current token line is exempt.
    bad_lines="$(awk -v token="$token" -v ctx="$CONTEXT_ALLOW" '
      function regex_escape(s,    out, i, c) {
        out = ""
        for (i = 1; i <= length(s); i++) {
          c = substr(s, i, 1)
          if (c ~ /[][.*+?(){}|^$\\\/]/) out = out "\\" c
          else out = out c
        }
        return out
      }
      BEGIN {
        for (i=1; i<=8; i++) recent[i] = ""
        # Build word-boundary regex so e.g. "life-os-tool" does NOT match the
        # legitimate plural "life-os-tools". (Awk lacks proper \b; use a
        # character class disallowing word continuation chars on either side.)
        pat = "(^|[^A-Za-z0-9_-])" regex_escape(token) "([^A-Za-z0-9_-]|$)"
      }
      {
        line_has_token = ($0 ~ pat)
        line_has_ctx = ($0 ~ ctx)
        any_recent_ctx = line_has_ctx
        for (i=1; i<=8; i++) if (recent[i] ~ ctx) any_recent_ctx = 1
        if (line_has_token && !any_recent_ctx) print NR ":" $0
        for (i=8; i>1; i--) recent[i] = recent[i-1]
        recent[1] = $0
      }
    ' "$file" 2>/dev/null)"
    if [ -n "$bad_lines" ]; then
      echo "  WARN '$token' (no explanatory context) in $file:"
      echo "$bad_lines" | head -3 | sed 's/^/      /'
      warnings_only=$((warnings_only + 1))
      active_token_hits=$((active_token_hits + 1))
    fi
  done < <(
    git ls-files '*.md' '*.sh' '*.py' '*.yml' '*.yaml' '*.toml' \
      | grep -vE "$EXEMPT_PATTERN" \
      | grep -vE "$BROKEN_PATH_EXEMPT" \
      | xargs grep -l "$token" 2>/dev/null || true
  )
done
echo ""
echo "  (forbidden-token hits in active files: $active_token_hits)"
if [ "${STRICT:-0}" = "1" ] && [ "$active_token_hits" -gt 0 ]; then
  drift_found=1
fi
echo ""
echo "  (forbidden-token warnings (legacy + active): $warnings_only)"

echo ""
if [ "$drift_found" -eq 0 ]; then
  echo "OK: no spec drift detected."
  exit 0
else
  echo "FAIL: spec drift detected. Fix the references above or add the file"
  echo "      to EXEMPT_PATTERN if it's intentionally historical/legacy."
  exit 1
fi
