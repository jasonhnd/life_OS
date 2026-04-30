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

# Files exempted from forbidden-token check.
#
# Round-11 audit fix: removed directory-level exemptions for
# `docs/architecture/`, `docs/guides/`, `i18n/.*/docs/`,
# `i18n/.*/references/`. Those passes were too broad — they let active
# v1.8.0 user-facing docs (e.g. installation in 3 langs, FAQ, getting-
# started, theme system overview) hide active spec drift behind a
# directory regex. The scanner now only exempts:
#   1. Truly historical artifacts that pre-date the spec model entirely
#      (CHANGELOG, backup/, MIGRATION, the scanner itself, *-template.md,
#      pro/compliance/ violation logs).
#   2. Anything else: must declare itself legacy via YAML frontmatter
#      (`status: legacy` or `authoritative: false`), OR have an explanatory
#      8-line context (CONTEXT_ALLOW match in any of the preceding 8 lines
#      or current line).
EXEMPT_PATTERN='^(CHANGELOG\.md|i18n/.*/CHANGELOG\.md|backup/|pro/compliance/|MIGRATION\.md|scripts/check-spec-drift\.sh|.*-template\.md)'

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
  # Round-10 audit follow-up: per-user instruction "不要说多少个 agent 了，
  # 多少个 agent 不重要，就说'多个 agent'就行". Hardcoded counts of agents
  # / subagents / roles are now flagged regardless of value — see the
  # SUBAGENT_COUNT_PATTERNS regex check below the literal-token loop. The
  # legacy frontmatter exemption (status: legacy / authoritative: false)
  # still applies, so v1.7-era spec / archive files describing "16 agents"
  # historically are correctly skipped.
)

# Round-10: regex patterns that match ANY hardcoded count of agents in the
# active surface. Tokens use the same bash adjacent-string concat trick so
# the scanner source itself does not carry the literal substring (a user-side
# `rg "23 subagents"` audit gets 0 hits from this file). Each pattern is an
# ERE matched line-by-line; same CONTEXT_ALLOW + 8-line lookback exemption
# applies as for FORBIDDEN_TOKENS.
#
# NB: count threshold = 13. Smaller numbers (1-12) describe structural
# things — "1-3 domain agents" (Express limit), "2 independent subagent"
# (per-request minimum), "9 themes" (# of cultural variants). Those are
# legitimate constants. Numbers >= 13 are suspicious because the system has
# had 14 → 16 → 22 → 23 subagents over its history; any of those values
# in a current doc indicates drift.
N='(1[3-9]|[2-9][0-9])'
# Nouns considered "subagent count" — covers EN/ZH/JA + structural
# vocabulary the system uses interchangeably (engine ID, 岗位 = "post",
# 角色 = "role", 個 / 个 = counter, etc.).
NOUN='(sub'"agents?|a"'gents?|roles?|individuals?|岗位|角色|功能 ID|ID|engine ID|engine|engine a'"gent|サブエージェント|エージェント|役職|機能 ID)"
SUBAGENT_COUNT_PATTERNS=(
  # ===== EN =====
  "$N (sub""agents?|sub""agent definitions?)"
  "$N (independent )?(sub""agents?|a""gents?)"
  "$N (AI )?(a""gents?|roles?|individuals?)"
  "$N engine ID"
  # ===== ZH =====
  # Tightened to (a) accept inner SPACES (round-12 fix — round-11 regex
  # used [^，。\\s]{0,12} which broke on "16 个 真正独立的 subagent" because
  # the space after "的" terminated the inner-char match) and (b) add the
  # '岗位 / ID alone / 功能' nouns the auditor flagged.
  "$N ?个 ?$NOUN"
  "$N 子 ?(sub""agent|a""gent)"
  # Up to 18 chars (allowing spaces and Chinese particles) between 个 and
  # the target noun. Excludes only commas/periods/newlines so multi-word
  # modifiers like "真正独立的 " match.
  "$N 个[^，。\\n]{0,18}$NOUN"
  "$N 个[^，。\\n]{0,12}(AI 角色)"
  "$N a""gent (制衡|编排|定义|calls|流程)"
  "$N engine a""gent"
  "$N (个|個) (功能|定义|ID)"
  # ===== JA =====
  "$N 個の独立した (sub""agent|a""gent|エージェント|サブエージェント)"
  "$N の(機能 ID|声|エージェント|サブエージェント|独立した|独立 ?サブエージェント|AI 役職|役職|エージェントが)"
  "${N}の(機能 ID|声|エージェント|サブエージェント|独立した|独立 ?サブエージェント|AI 役職|役職|エージェントが)"
  "$N ?個の ?(sub""agent|a""gent|エージェント|サブエージェント|役職|機能 ID)"
  "同じ ?$N ?の ?(役職|エージェント|サブエージェント)"
  "$N sub""agent (並列|フロー)"
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
    # Round-12 paragraph-aware reset: blank lines and H1-H6 headers
    # break the lookback so context only carries within the same
    # paragraph / topical block.
    /^[[:space:]]*$/ || /^#{1,6} / {
      for (i=1; i<=8; i++) recent[i] = ""
      next
    }
    {
      # Check if any of last 8 lines (within same paragraph) or current
      # line matches CONTEXT_ALLOW.
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
        pat = "(^|[^A-Za-z0-9_-])" regex_escape(token) "([^A-Za-z0-9_-]|$)"
      }
      # Round-12 fix: blank lines and H1/H2/H3 markdown headers BREAK the
      # context window. Previously a "v1.7" mention at line N could exempt
      # an unrelated drift line at N+8 even when separated by a blank line
      # and a new H2 — clearly a different paragraph. Now any blank line
      # or `^#{1,6} ` header line clears recent[] so context only carries
      # within the same paragraph / topical block.
      /^[[:space:]]*$/ || /^#{1,6} / {
        for (i=1; i<=8; i++) recent[i] = ""
        next
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

# Round-10: regex-based subagent-count drift detection. Same context-window
# rules apply (8-line lookback for CONTEXT_ALLOW exemption + legacy
# frontmatter exemption). The patterns are EREs already, no escape needed.
for pat in "${SUBAGENT_COUNT_PATTERNS[@]}"; do
  while IFS= read -r file; do
    is_legacy_file "$file" && continue
    bad_lines="$(awk -v pat="$pat" -v ctx="$CONTEXT_ALLOW" '
      BEGIN { for (i=1; i<=8; i++) recent[i] = "" }
      # Paragraph-aware reset (round-12): blank lines and H1-H6 headers
      # break the lookback window so context only carries within the
      # same paragraph / topical block.
      /^[[:space:]]*$/ || /^#{1,6} / {
        for (i=1; i<=8; i++) recent[i] = ""
        next
      }
      {
        line_has_match = ($0 ~ pat)
        line_has_ctx = ($0 ~ ctx)
        any_recent_ctx = line_has_ctx
        for (i=1; i<=8; i++) if (recent[i] ~ ctx) any_recent_ctx = 1
        if (line_has_match && !any_recent_ctx) print NR ":" $0
        for (i=8; i>1; i--) recent[i] = recent[i-1]
        recent[1] = $0
      }
    ' "$file" 2>/dev/null)"
    if [ -n "$bad_lines" ]; then
      echo "  WARN regex /$pat/ (subagent-count drift, no explanatory context) in $file:"
      echo "$bad_lines" | head -3 | sed 's/^/      /'
      warnings_only=$((warnings_only + 1))
      active_token_hits=$((active_token_hits + 1))
    fi
  done < <(
    git ls-files '*.md' '*.sh' '*.py' '*.yml' '*.yaml' '*.toml' \
      | grep -vE "$EXEMPT_PATTERN" \
      | grep -vE "$BROKEN_PATH_EXEMPT" \
      | xargs grep -lE "$pat" 2>/dev/null || true
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
