#!/bin/bash
# scripts/wiki/wiki-link-audit.sh — v1.8.1 F2 (replaces deleted wiki_decay.py auditor side)
# ─────────────────────────────────────────────────────────────────────────────
# Pure bash + awk + grep wiki link/freshness audit. Runs against a
# user's second-brain vault (NOT the Life OS dev repo). No Python, no
# external dependencies.
#
# Usage (from inside vault root):
#
#     bash ~/.claude/skills/life_OS/scripts/wiki/wiki-link-audit.sh
#
# Output:
#
#     _meta/eval-history/wiki-link-audit-YYYY-MM-DD.md
#
# Report sections:
#   1. Counts: entries / wikilinks / markdown-links / orphans / broken
#   2. Broken wikilinks (with source file + target name)
#   3. Broken markdown-links (with source file + target path)
#   4. Orphan entries (no inbound or outbound link)
#   5. Stale entries (last_updated > 180 days old)
#   6. Low-confidence entries (confidence < 0.5)
#
# This replaces the wiki-decay-style auditing that the deleted v1.7
# `tools/wiki_decay.py` used to do — but stripped to the things you can
# realistically act on. The accompanying maintenance prompt at
# `scripts/prompts/wiki-decay.md` is the LLM-driven half (read this report,
# propose deprecations / merges / freshness updates).
# ─────────────────────────────────────────────────────────────────────────────

set -u

if [ ! -d "wiki" ] || [ ! -d "_meta" ]; then
  echo "ERROR: cwd doesn't look like a second-brain vault." >&2
  echo "       cd into vault root first, then re-run." >&2
  exit 1
fi

DATE_TODAY="$(date +%Y-%m-%d)"
REPORT_DIR="_meta/eval-history"
REPORT="$REPORT_DIR/wiki-link-audit-$DATE_TODAY.md"
mkdir -p "$REPORT_DIR"

echo "🔍 wiki-link-audit v1.8.1 — vault: $(pwd)"

# ─── Collect file list (exclude infrastructure files) ───────────────────────
WIKI_FILES="$(find wiki -type f -name '*.md' \
  -not -name 'INDEX.md' \
  -not -name 'SCHEMA.md' \
  -not -name 'log.md' \
  -not -name 'OBSIDIAN-SETUP.md' \
  -not -path 'wiki/.templates/*' 2>/dev/null \
  | sort)"
TOTAL_ENTRIES="$(printf '%s\n' "$WIKI_FILES" | grep -c . || true)"
echo "   found $TOTAL_ENTRIES wiki entries"

# ─── Counters ────────────────────────────────────────────────────────────────
WIKILINK_COUNT=0
MDLINK_COUNT=0
BROKEN_WIKILINKS=""
BROKEN_MDLINKS=""

# Build a set of "all valid targets" (basenames + slugs). We use both
# the bare filename (for `[[name]]`) and full relative paths (for `[t](path)`).
VALID_BASENAMES_FILE="$(mktemp)"
VALID_PATHS_FILE="$(mktemp)"
trap 'rm -f "$VALID_BASENAMES_FILE" "$VALID_PATHS_FILE"' EXIT

# Bare basenames without .md (Obsidian wikilinks resolve by basename in default settings)
printf '%s\n' "$WIKI_FILES" | while IFS= read -r f; do
  [ -z "$f" ] && continue
  basename "$f" .md
done | sort -u > "$VALID_BASENAMES_FILE"

# Full relative paths (markdown links use these)
printf '%s\n' "$WIKI_FILES" > "$VALID_PATHS_FILE"

# ─── Per-file scan ───────────────────────────────────────────────────────────
# We accumulate orphan candidates by tracking: (a) did this file appear as a
# target of another file's link? (incoming), (b) does this file have any
# outgoing link? Orphan = both no.
INCOMING_FILE="$(mktemp)"
OUTGOING_FILE="$(mktemp)"
trap 'rm -f "$VALID_BASENAMES_FILE" "$VALID_PATHS_FILE" "$INCOMING_FILE" "$OUTGOING_FILE"' EXIT

printf '%s\n' "$WIKI_FILES" | while IFS= read -r f; do
  [ -z "$f" ] && continue

  # Wikilinks: [[target]] (Obsidian) — capture target between [[ ]].
  # Use grep -oE; awk for cleaner extraction across systems.
  wikilinks="$(grep -oE '\[\[[^]|#]+(\|[^]]*)?\]\]' "$f" 2>/dev/null \
    | sed 's/^\[\[//; s/\]\]$//; s/|.*//; s/#.*//' \
    | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' \
    || true)"

  if [ -n "$wikilinks" ]; then
    # outgoing link from this file
    echo "$f" >> "$OUTGOING_FILE"
    # check each wikilink target — does basename exist in VALID_BASENAMES_FILE?
    while IFS= read -r tgt; do
      [ -z "$tgt" ] && continue
      WIKILINK_COUNT=$((WIKILINK_COUNT + 1))
      if ! grep -qxF "$tgt" "$VALID_BASENAMES_FILE"; then
        BROKEN_WIKILINKS="$BROKEN_WIKILINKS  · $f → [[$tgt]] (target file not found)\n"
      else
        # record that target file is incoming-linked
        # find the actual file path for tgt
        tgt_path="$(printf '%s\n' "$WIKI_FILES" | grep -E "/${tgt}\.md$" | head -n 1 || true)"
        [ -n "$tgt_path" ] && echo "$tgt_path" >> "$INCOMING_FILE"
      fi
    done <<< "$wikilinks"
  fi

  # Markdown links: [text](path/to/file.md) — must resolve to a real path.
  mdlinks="$(grep -oE '\[[^]]+\]\([^)[:space:]]+\.md\)' "$f" 2>/dev/null \
    | sed 's/^\[[^]]*\](//; s/)$//' \
    | sed 's/#.*//' \
    || true)"

  if [ -n "$mdlinks" ]; then
    echo "$f" >> "$OUTGOING_FILE"
    while IFS= read -r raw_tgt; do
      [ -z "$raw_tgt" ] && continue
      MDLINK_COUNT=$((MDLINK_COUNT + 1))

      # Resolve relative to the source file's directory (best-effort; we
      # don't fully simulate Obsidian's resolution rules — just check
      # whether the joined path exists)
      src_dir="$(dirname "$f")"
      case "$raw_tgt" in
        /*)
          # absolute-from-vault-root link
          resolved="${raw_tgt#/}"
          ;;
        http*|//*|mailto:*)
          # external; not a wiki link
          continue
          ;;
        *)
          # relative to source dir
          resolved="$src_dir/$raw_tgt"
          ;;
      esac

      if [ ! -f "$resolved" ]; then
        BROKEN_MDLINKS="$BROKEN_MDLINKS  · $f → [text]($raw_tgt) (resolved: $resolved — not found)\n"
      else
        # only record incoming if target is a wiki file
        case "$resolved" in
          wiki/*) echo "$resolved" >> "$INCOMING_FILE" ;;
        esac
      fi
    done <<< "$mdlinks"
  fi

done

# Note: counters set inside the `while` subshell are LOST on POSIX bash 3.x.
# Recompute outside the loop using the recorded files (process substitution
# would also work but is bash 4+).
WIKILINK_COUNT="$(grep -c . "$OUTGOING_FILE" 2>/dev/null || echo 0)"  # imprecise; recount more carefully:

# Recount wikilinks + mdlinks across all files (not summing, but scanning anew — cheaper than fixing the subshell var loss)
WIKILINK_COUNT="$(printf '%s\n' "$WIKI_FILES" | xargs -I{} grep -oE '\[\[[^]|#]+(\|[^]]*)?\]\]' {} 2>/dev/null | wc -l | tr -d '[:space:]')"
MDLINK_COUNT="$(printf '%s\n' "$WIKI_FILES" | xargs -I{} grep -oE '\[[^]]+\]\([^)[:space:]]+\.md\)' {} 2>/dev/null | wc -l | tr -d '[:space:]')"

# Compute broken counts (count newlines in the accumulated strings)
BROKEN_WIKILINK_COUNT=0
BROKEN_MDLINK_COUNT=0
[ -n "${BROKEN_WIKILINKS}" ] && BROKEN_WIKILINK_COUNT="$(printf '%b' "$BROKEN_WIKILINKS" | grep -c '^  · ' || true)"
[ -n "${BROKEN_MDLINKS}" ] && BROKEN_MDLINK_COUNT="$(printf '%b' "$BROKEN_MDLINKS" | grep -c '^  · ' || true)"

# Orphans: files with no incoming AND no outgoing link
sort -u "$INCOMING_FILE" -o "$INCOMING_FILE" 2>/dev/null || true
sort -u "$OUTGOING_FILE" -o "$OUTGOING_FILE" 2>/dev/null || true

ORPHANS=""
ORPHAN_COUNT=0
printf '%s\n' "$WIKI_FILES" | while IFS= read -r f; do
  [ -z "$f" ] && continue
  has_in="0"
  has_out="0"
  grep -qxF "$f" "$INCOMING_FILE" 2>/dev/null && has_in="1"
  grep -qxF "$f" "$OUTGOING_FILE" 2>/dev/null && has_out="1"
  if [ "$has_in" = "0" ] && [ "$has_out" = "0" ]; then
    echo "  · $f"
  fi
done > /tmp/wiki_orphans_$$.txt
ORPHANS="$(cat /tmp/wiki_orphans_$$.txt 2>/dev/null || true)"
ORPHAN_COUNT="$(printf '%s' "$ORPHANS" | grep -c '^  · ' || echo 0)"
rm -f /tmp/wiki_orphans_$$.txt

# Stale: last_updated > 180 days old (per file frontmatter)
NOW_EPOCH="$(date +%s)"
STALE_CUTOFF=$((NOW_EPOCH - 180 * 86400))
STALE=""
STALE_COUNT=0
printf '%s\n' "$WIKI_FILES" | while IFS= read -r f; do
  [ -z "$f" ] && continue
  lu="$(awk '/^---/{n++; next} n==1 && /^last_updated:/ {gsub(/^last_updated:[[:space:]]*/, "", $0); gsub(/[[:space:]]+$/, "", $0); gsub(/"|'\''/, "", $0); print; exit}' "$f" 2>/dev/null || true)"
  [ -z "$lu" ] && continue
  # parse YYYY-MM-DD into epoch (portable: try GNU date -d, fall back to BSD date -j -f)
  lu_epoch=""
  if lu_epoch="$(date -d "$lu" +%s 2>/dev/null)"; then
    :
  elif lu_epoch="$(date -j -f "%Y-%m-%d" "$lu" +%s 2>/dev/null)"; then
    :
  else
    continue
  fi
  if [ "$lu_epoch" -lt "$STALE_CUTOFF" ]; then
    age_days=$(( (NOW_EPOCH - lu_epoch) / 86400 ))
    echo "  · $f (last_updated: $lu, ${age_days}d old)"
  fi
done > /tmp/wiki_stale_$$.txt
STALE="$(cat /tmp/wiki_stale_$$.txt 2>/dev/null || true)"
STALE_COUNT="$(printf '%s' "$STALE" | grep -c '^  · ' || echo 0)"
rm -f /tmp/wiki_stale_$$.txt

# Low-confidence: confidence < 0.5
LOWCONF=""
LOWCONF_COUNT=0
printf '%s\n' "$WIKI_FILES" | while IFS= read -r f; do
  [ -z "$f" ] && continue
  conf="$(awk '/^---/{n++; next} n==1 && /^confidence:/ {gsub(/^confidence:[[:space:]]*/, "", $0); gsub(/[[:space:]]+$/, "", $0); print; exit}' "$f" 2>/dev/null || true)"
  [ -z "$conf" ] && continue
  # numeric compare (awk handles float)
  if awk -v c="$conf" 'BEGIN { exit !(c+0 < 0.5) }'; then
    echo "  · $f (confidence: $conf)"
  fi
done > /tmp/wiki_lowconf_$$.txt
LOWCONF="$(cat /tmp/wiki_lowconf_$$.txt 2>/dev/null || true)"
LOWCONF_COUNT="$(printf '%s' "$LOWCONF" | grep -c '^  · ' || echo 0)"
rm -f /tmp/wiki_lowconf_$$.txt

# ─── Write report ────────────────────────────────────────────────────────────
{
  echo "# Wiki link audit · $DATE_TODAY"
  echo ""
  echo "Generated by \`scripts/wiki/wiki-link-audit.sh\` (v1.8.1)."
  echo ""
  echo "## Summary"
  echo ""
  echo "| Metric | Count |"
  echo "|---|---|"
  echo "| Total wiki entries | $TOTAL_ENTRIES |"
  echo "| Wikilinks (\`[[...]]\`) | $WIKILINK_COUNT |"
  echo "| Markdown links (\`[t](path.md)\`) | $MDLINK_COUNT |"
  echo "| Broken wikilinks | $BROKEN_WIKILINK_COUNT |"
  echo "| Broken markdown links | $BROKEN_MDLINK_COUNT |"
  echo "| Orphan entries (no in or out links) | $ORPHAN_COUNT |"
  echo "| Stale entries (> 180 days) | $STALE_COUNT |"
  echo "| Low confidence (< 0.5) | $LOWCONF_COUNT |"
  echo ""
  echo "## Broken wikilinks"
  echo ""
  if [ "$BROKEN_WIKILINK_COUNT" -gt 0 ]; then
    printf '%b' "$BROKEN_WIKILINKS"
  else
    echo "  none — all \`[[wikilinks]]\` resolve to a wiki file."
  fi
  echo ""
  echo "## Broken markdown links"
  echo ""
  if [ "$BROKEN_MDLINK_COUNT" -gt 0 ]; then
    printf '%b' "$BROKEN_MDLINKS"
  else
    echo "  none — all \`[text](path.md)\` links resolve."
  fi
  echo ""
  echo "## Orphan entries (no incoming or outgoing wiki link)"
  echo ""
  if [ "$ORPHAN_COUNT" -gt 0 ]; then
    echo "$ORPHANS"
  else
    echo "  none — every entry is connected to at least one other entry."
  fi
  echo ""
  echo "## Stale entries (last_updated > 180 days old)"
  echo ""
  if [ "$STALE_COUNT" -gt 0 ]; then
    echo "$STALE"
  else
    echo "  none — all entries updated within the last 180 days."
  fi
  echo ""
  echo "## Low-confidence entries (confidence < 0.5)"
  echo ""
  if [ "$LOWCONF_COUNT" -gt 0 ]; then
    echo "$LOWCONF"
  else
    echo "  none — all entries have confidence ≥ 0.5."
  fi
  echo ""
  echo "---"
  echo ""
  echo "Recommended next step: run \`/wiki-decay\` (or say \"扫一下 wiki\") to"
  echo "have ROUTER walk this report and propose deprecate / merge / refresh"
  echo "actions per \`scripts/prompts/wiki-decay.md\`."
} > "$REPORT"

echo "✅ wrote $REPORT"
echo ""
echo "   total entries:        $TOTAL_ENTRIES"
echo "   wikilinks / markdown: $WIKILINK_COUNT / $MDLINK_COUNT"
echo "   broken:               $BROKEN_WIKILINK_COUNT (wikilinks) + $BROKEN_MDLINK_COUNT (markdown)"
echo "   orphans:              $ORPHAN_COUNT"
echo "   stale (>180d):        $STALE_COUNT"
echo "   low-confidence (<.5): $LOWCONF_COUNT"
echo ""
exit 0
