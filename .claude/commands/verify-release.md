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

### 8. (v1.8.5+ / v1.8.7 expanded) No forbidden extensions in repo
```bash
find . -type f \( -name '*.py' -o -name '*.sh' -o -name '*.bash' -o -name '*.yml' -o -name '*.yaml' -o -name '*.json' -o -name '*.sql' -o -name '*.db' -o -name '*.sqlite' \) \
  -not -path './.git/*' -not -path './backup/*' -not -path './.venv/*' | head -20
```
- **PASS** if output is empty.
- **FAIL** otherwise → list found files; user must convert to slash commands or md spec.
- **v1.8.7 expansion (DR-10 ontological constraint)**: now scans 9 extensions (added `.bash` / `.yml` / `.yaml` / `.json` / `.sql` / `.db` / `.sqlite` on top of v1.8.5's `.py` / `.sh`). See `SKILL.md` HARD RULE md-only ontological constraint.

### 9. (v1.8.7 NEW) i18n diff parity (WARN level in v1.8.7, BLOCK target v1.8.8)
Per `references/i18n-diff-parity-spec.md`. Verify that EN spec changes between `<base>..HEAD` have matching changes in zh + ja mirrors.

```bash
# 1. List changed EN spec files
git diff --name-only <base>..HEAD -- references/ CHANGELOG.md README.md MIGRATION.md 2>/dev/null

# 2. For each changed EN file, list corresponding mirror files that ALSO changed
git diff --name-only <base>..HEAD -- i18n/zh/references/ i18n/zh/CHANGELOG.md i18n/zh/README.md i18n/zh/MIGRATION.md i18n/ja/references/ i18n/ja/CHANGELOG.md i18n/ja/README.md i18n/ja/MIGRATION.md 2>/dev/null
```

LLM procedure (per i18n-diff-parity-spec §"Verification implementation"):
- For each changed EN file: identify changed sections by walking back to nearest `## `
- For each changed section, verify same section also has a diff in zh and ja mirrors
- Verify section count parity: EN section count == zh count == ja count
- **PASS** if all changed sections aligned across three languages
- **WARN** (v1.8.7 default — does NOT block release) if drift detected — output list of drifted (file, section) pairs
- v1.8.8 target: escalate to BLOCK for HARD RULE-bearing specs + README/CHANGELOG/MIGRATION

### 10. (v1.8.7 NEW · DR-10 audit) No forbidden extensions in commit diff
Tighter scope than check 8: ensures no forbidden extension was introduced **since the previous tag** (catches sneak-in even if repo somehow gets cleaned later).

```bash
PREV_TAG=$(git tag --sort=-creatordate | sed -n '2p')   # second-most-recent tag
git diff --name-only "$PREV_TAG"..HEAD | grep -E '\.(py|sh|bash|yml|yaml|json|sql|db|sqlite)$' || echo "none"
```

- **PASS** if output is `none` (or empty).
- **FAIL** if any path matched → release MUST NOT proceed; remove the file or revert the commit that introduced it.
- This is the diff-scoped enforcement complementing check 8's full-repo scan. Together they prevent both "file slipped in" (check 8) and "file added in this release window" (check 10).

### 11. (v1.8.5+, renumbered v1.8.7) All regression fixtures FAIL
```bash
ls evals/regression-fixtures/*.md 2>/dev/null | wc -l
```
- Then run `/run-eval` slash command and verify all fixtures marked "should-fail" actually fail when run through validators.
- **PASS** if 100% of regression fixtures FAIL as expected.
- **FAIL** otherwise → report which fixtures passed when they should have failed.
- Note: v1.8.7 fixture extension changed from `.yml` → `.md` per md-only ontological constraint (DR-10). Older `*.yml` fixtures already converted in v1.8.5 Stage 9 / v1.8.6.

## Output format

After running all 11 checks, emit a summary:

```
── /verify-release · $TARGET_TAG ──
1. Working tree clean: ✅/❌
2. HEAD == origin/main: ✅/❌
3. Target tag identified: $TARGET_TAG
4. Tag points to HEAD: ✅/❌
5. Tag on remote: ✅/❌
6. GitHub Release exists (not Draft): ✅/❌
7. Marked as Latest: ✅/❌
8. No forbidden extensions in repo: ✅/❌
9. i18n diff parity (WARN level v1.8.7): ✅/⚠️
10. No forbidden extensions in commit diff: ✅/❌
11. All regression fixtures FAIL: ✅/❌

VERDICT: PASS / WARN / FAIL
[if FAIL: list specific fix commands for each ❌]
[if WARN only: release CAN proceed, but record warning for follow-up]
```

## HARD RULES

- **Paste literal `git` and `gh` output, do not summarize.** Summarizing creates space for the LLM to fabricate clean results when checks actually failed.
- **Any ❌ means the release is NOT done.** Do not declare success with a partial pass.
- **Cannot be skipped.** Per pro/AGENTS.md HARD RULE "GitHub Release alignment", every release-bumping commit must complete `/verify-release` before being considered shipped.
