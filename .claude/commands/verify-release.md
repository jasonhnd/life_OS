---
description: Verify a release tag is fully aligned (HEAD == origin/main == tag commit, GitHub Release published as Latest, regression fixtures all FAIL, no .py/.sh in repo). Replaces v1.8.4 scripts/verify-release.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[tag-name]  (default: latest tag)"
allowed-tools:
  - Bash
  - Read
---

# /verify-release

You are verifying that a release is fully shipped, not just tagged. **HARD RULE per pro/AGENTS.md**: `git push --tags` does NOT auto-create a GitHub Release. The Releases page can stay frozen on an older version even though main + the new tag are up to date.

## Inputs

- `$ARGUMENTS` (optional) — specific tag name (e.g. `v1.8.5`). If empty, check the latest annotated tag.

## Procedure

Run the following commands and paste their **literal stdout** (do not summarize or rewrite). Then evaluate the 8 checks below. **Any ❌ means the release is NOT done.**

### 1. Working tree state
```bash
git status --short
```
- **PASS** if output is empty.
- **FAIL** otherwise → report which files are dirty.

### 2. HEAD == origin/main
```bash
git fetch origin main --quiet 2>/dev/null
HEAD_SHA=$(git rev-parse HEAD)
ORIGIN_SHA=$(git rev-parse origin/main)
echo "HEAD: $HEAD_SHA"
echo "origin/main: $ORIGIN_SHA"
```
- **PASS** if both SHAs match.
- **FAIL** otherwise → user must `git push origin main`.

### 3. Determine target tag
```bash
TARGET_TAG="${1:-$(git tag --sort=-version:refname | head -n 1)}"
echo "Verifying tag: $TARGET_TAG"
```
If no tags exist → abort with "no tags in repo, nothing to verify".

### 4. Tag points to HEAD
```bash
TAG_COMMIT=$(git rev-list -n 1 "$TARGET_TAG" 2>/dev/null)
echo "Tag commit: $TAG_COMMIT"
echo "HEAD: $(git rev-parse HEAD)"
```
- **PASS** if equal.
- **FAIL** otherwise → tag pointing to wrong commit, delete + recreate.

### 5. Tag on remote
```bash
git ls-remote origin "refs/tags/$TARGET_TAG"
```
- **PASS** if output non-empty AND object hash matches `git rev-parse $TARGET_TAG`.
- **FAIL** otherwise → user must `git push origin $TARGET_TAG`.

### 6. GitHub Release exists and not Draft
```bash
gh release view "$TARGET_TAG" --json tagName,isDraft,isPrerelease
```
- **PASS** if returns JSON with `"isDraft": false`.
- **FAIL** if errors with "release not found" → user must `gh release create $TARGET_TAG --title '...' --notes-file <FILE> --latest`.
- **FAIL** if `"isDraft": true` → user must `gh release edit $TARGET_TAG --draft=false`.

### 7. Marked as Latest
```bash
gh release list --json tagName,isLatest --limit 20
```
Look for the entry where `"isLatest": true` — the tagName must equal `$TARGET_TAG`.

- **PASS** if Latest tag == target.
- **FAIL** otherwise → user must `gh release edit $TARGET_TAG --latest`.

### 8. (v1.8.5+) No .py / .sh in repo
```bash
find . -type f \( -name '*.py' -o -name '*.sh' \) \
  -not -path './.git/*' -not -path './backup/*' -not -path './.venv/*' | head -20
```
- **PASS** if output is empty.
- **FAIL** otherwise → list found files; user must convert to slash commands or markdown spec.

### 9. (v1.8.5+) All regression fixtures FAIL
```bash
ls evals/regression-fixtures/*.yml 2>/dev/null | wc -l
```
- Then run `/run-regression` slash command and verify all fixtures marked "should-fail" actually fail when run through validators.
- **PASS** if 100% of regression fixtures FAIL as expected.
- **FAIL** otherwise → report which fixtures passed when they should have failed.

## Output format

After running all 9 checks, emit a summary:

```
── /verify-release · $TARGET_TAG ──
1. Working tree clean: ✅/❌
2. HEAD == origin/main: ✅/❌
3. Target tag identified: $TARGET_TAG
4. Tag points to HEAD: ✅/❌
5. Tag on remote: ✅/❌
6. GitHub Release exists (not Draft): ✅/❌
7. Marked as Latest: ✅/❌
8. No .py/.sh in repo: ✅/❌
9. All regression fixtures FAIL: ✅/❌

VERDICT: PASS / FAIL
[if FAIL: list specific fix commands for each ❌]
```

## HARD RULES

- **Paste literal `git` and `gh` output, do not summarize.** Summarizing creates space for the LLM to fabricate clean results when checks actually failed.
- **Any ❌ means the release is NOT done.** Do not declare success with a partial pass.
- **Cannot be skipped.** Per pro/AGENTS.md HARD RULE "GitHub Release alignment", every release-bumping commit must complete `/verify-release` before being considered shipped.
