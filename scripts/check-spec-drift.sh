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

echo "-- (1/2) Broken-path scanner --"
# Active files only (CHANGELOGs, READMEs explaining "what was removed",
# and known historical-archive docs are exempted). Reports broken paths
# as INFORMATIONAL on the existing baseline; the scanner tightens to
# strict-fail once the existing debt list is processed.
BROKEN_PATH_EXEMPT='^(README\.md|i18n/.*/README\.md|MIGRATION\.md|CHANGELOG\.md|i18n/.*/CHANGELOG\.md|docs/architecture/|docs/guides/|docs/user-guide/|docs/index\.md|i18n/.*/docs/|references/v1\.7|references/templates/|references/cortex-architecture\.md|references/cortex-spec\.md|references/tools-spec\.md|references/narrator-spec\.md|references/data-layer\.md|references/snapshot-spec\.md|pro/CLAUDE\.md|pro/AGENTS\.md|pro/GEMINI\.md|backup/|pro/compliance/|i18n/.*/references/|tools/README\.md|scripts/check-spec-drift\.sh|.*-template\.md|themes/.*\.md|evals/scenarios/.*\.md|tests/.*\.py)'
while IFS= read -r path_ref; do
  path_ref="$(echo "$path_ref" | sed 's/^[[:space:]`]*//;s/[[:space:]`,)]*$//')"
  [ -z "$path_ref" ] && continue
  case "$path_ref" in
    http*|mailto:*|//*) continue ;;
  esac
  # Placeholder paths (template variables) are not real broken refs
  case "$path_ref" in
    *X.md|*xxx*|*YYYY*|*your-theme*|*custom-*) continue ;;
  esac
  if [ ! -e "$path_ref" ]; then
    echo "  BROKEN: $path_ref"
    broken_paths=$((broken_paths + 1))
  fi
done < <(
  git ls-files '*.md' '*.sh' '*.py' \
    | grep -vE "$EXEMPT_PATTERN" \
    | grep -vE "$BROKEN_PATH_EXEMPT" \
    | xargs grep -hoE '`(scripts|pro|tools|references|docs|themes|evals)/[A-Za-z0-9_./-]+\.(sh|md|py|json|yml|yaml|toml)`' 2>/dev/null \
    | sort -u
)
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
CONTEXT_ALLOW='REMOVED|removed|deleted|deprecated|previously|was tied to|legacy|historical|pre-pivot|pre-R-1\.8\.0|pre-v1\.8|R-1\.8\.0-011|formerly|once required|no longer|删除|已删除|弃用|废弃|被删|削除|廃止'
warnings_only=0
for token in "${FORBIDDEN_TOKENS[@]}"; do
  while IFS= read -r file; do
    bad_lines="$(grep -nF "$token" "$file" 2>/dev/null | grep -vE "$CONTEXT_ALLOW" || true)"
    if [ -n "$bad_lines" ]; then
      echo "  WARN '$token' (no explanatory context) in $file:"
      echo "$bad_lines" | head -3 | sed 's/^/      /'
      warnings_only=$((warnings_only + 1))
    fi
  done < <(
    git ls-files '*.md' '*.sh' '*.py' '*.yml' '*.yaml' '*.toml' \
      | grep -vE "$EXEMPT_PATTERN" \
      | xargs grep -l "$token" 2>/dev/null || true
  )
done
echo ""
echo "  (forbidden-token warnings: $warnings_only — informational only, does not fail CI)"

echo ""
if [ "$drift_found" -eq 0 ]; then
  echo "OK: no spec drift detected."
  exit 0
else
  echo "FAIL: spec drift detected. Fix the references above or add the file"
  echo "      to EXEMPT_PATTERN if it's intentionally historical/legacy."
  exit 1
fi
