#!/bin/bash
# scripts/verify-release.sh — Release alignment verifier
# ─────────────────────────────────────────────────────────────────────────────
# Checks that the current HEAD, origin/main, the latest annotated tag, and
# the corresponding GitHub Release are all aligned.
#
# Failure mode this catches: pushing a git tag does NOT auto-create a
# GitHub Release. The Releases page can stay frozen on an older version
# (e.g. v1.7.3) even though main + the v1.8.0 tag are up to date. End-users
# clicking "Latest" then download the wrong code.
#
# Run after every release-bumping commit:
#
#     bash scripts/verify-release.sh
#     bash scripts/verify-release.sh v1.8.0   # check a specific tag
#
# Exit 0 = aligned, exit 1 = drift detected.
# ─────────────────────────────────────────────────────────────────────────────

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

TARGET_TAG="${1:-}"
fail=0

echo "── Release alignment check ──"

# 1. Working tree clean?
if [ -n "$(git status --porcelain)" ]; then
  echo "  ⚠️  WORKING TREE DIRTY:"
  git status --short | sed 's/^/      /'
  fail=1
fi

# 2. HEAD == origin/main?
HEAD_SHA="$(git rev-parse HEAD)"
git fetch origin main --quiet 2>/dev/null || true
ORIGIN_SHA="$(git rev-parse origin/main 2>/dev/null || echo "")"
if [ "$HEAD_SHA" != "$ORIGIN_SHA" ]; then
  echo "  ❌ HEAD != origin/main"
  echo "      HEAD:        $HEAD_SHA"
  echo "      origin/main: $ORIGIN_SHA"
  echo "      → run: git push origin main"
  fail=1
else
  echo "  ✅ HEAD == origin/main ($HEAD_SHA)"
fi

# 3. Determine which tag to verify (latest by default)
if [ -z "$TARGET_TAG" ]; then
  TARGET_TAG="$(git tag --sort=-version:refname | head -n 1)"
fi
if [ -z "$TARGET_TAG" ]; then
  echo "  ⚠️  no tags in repo — nothing to verify"
  exit "$fail"
fi
echo "  ── checking tag: $TARGET_TAG ──"

# 4. Tag exists locally and points to HEAD?
TAG_COMMIT="$(git rev-list -n 1 "$TARGET_TAG" 2>/dev/null || echo "")"
if [ -z "$TAG_COMMIT" ]; then
  echo "  ❌ tag $TARGET_TAG does NOT exist locally"
  fail=1
elif [ "$TAG_COMMIT" != "$HEAD_SHA" ]; then
  echo "  ❌ tag $TARGET_TAG points to $TAG_COMMIT, not HEAD ($HEAD_SHA)"
  echo "      → run: git tag -d $TARGET_TAG && git push origin :refs/tags/$TARGET_TAG"
  echo "             git tag -a $TARGET_TAG $HEAD_SHA -m '...' && git push origin $TARGET_TAG"
  fail=1
else
  echo "  ✅ tag $TARGET_TAG → $TAG_COMMIT (== HEAD)"
fi

# 5. Tag pushed to remote?
REMOTE_TAG_OBJ="$(git ls-remote origin "refs/tags/$TARGET_TAG" 2>/dev/null | awk '{print $1}')"
LOCAL_TAG_OBJ="$(git rev-parse "$TARGET_TAG" 2>/dev/null || echo "")"
if [ -z "$REMOTE_TAG_OBJ" ]; then
  echo "  ❌ tag $TARGET_TAG NOT on remote"
  echo "      → run: git push origin $TARGET_TAG"
  fail=1
elif [ "$REMOTE_TAG_OBJ" != "$LOCAL_TAG_OBJ" ]; then
  echo "  ❌ remote tag object differs from local"
  echo "      local:  $LOCAL_TAG_OBJ"
  echo "      remote: $REMOTE_TAG_OBJ"
  fail=1
else
  echo "  ✅ tag $TARGET_TAG pushed to origin"
fi

# 6. GitHub Release exists at this tag?
if ! command -v gh >/dev/null 2>&1; then
  echo "  ⚠️  gh CLI not available — skipping GitHub Release check"
  echo "      → manually verify: https://github.com/jasonhnd/life_OS/releases/tag/$TARGET_TAG"
else
  # gh release view only knows isDraft / isPrerelease — isLatest is only
  # available via gh release list. Use both calls.
  REL_VIEW="$(gh release view "$TARGET_TAG" --json tagName,isDraft,isPrerelease 2>/dev/null || true)"
  if [ -z "$REL_VIEW" ]; then
    echo "  ❌ no GitHub Release exists for tag $TARGET_TAG"
    echo "      → run: gh release create $TARGET_TAG --title '...' --notes-file <FILE> --latest"
    fail=1
  else
    IS_DRAFT="$(echo "$REL_VIEW" | python -c "import sys, json; print(json.load(sys.stdin)['isDraft'])" 2>/dev/null || echo "?")"
    if [ "$IS_DRAFT" = "True" ]; then
      echo "  ❌ GitHub Release for $TARGET_TAG is still DRAFT"
      echo "      → publish via gh release edit $TARGET_TAG --draft=false"
      fail=1
    else
      echo "  ✅ GitHub Release published for $TARGET_TAG"
    fi
    # isLatest comes from gh release list
    LATEST_TAG="$(gh release list --json tagName,isLatest 2>/dev/null \
      | python -c "import sys, json; rs = json.load(sys.stdin); latest = [r for r in rs if r['isLatest']]; print(latest[0]['tagName'] if latest else '')" 2>/dev/null || echo "")"
    if [ "$LATEST_TAG" != "$TARGET_TAG" ]; then
      echo "  ⚠️  GitHub 'Latest' is $LATEST_TAG, not $TARGET_TAG"
      echo "      → run: gh release edit $TARGET_TAG --latest"
      fail=1
    else
      echo "  ✅ marked as 'Latest' on GitHub"
    fi
  fi
fi

echo ""
if [ "$fail" -eq 0 ]; then
  echo "OK: $TARGET_TAG fully aligned (HEAD == origin/main == tag commit, Release published as Latest)."
  exit 0
else
  echo "FAIL: alignment drift detected. Fix the items marked ❌ above before declaring the release done."
  exit 1
fi
