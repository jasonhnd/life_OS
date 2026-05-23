---
description: Check if local lifeos installation is up to date with GitHub remote. Replaces v1.8.4 scripts/lifeos-version-check.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[--force]  (default: cached if checked today)"
allowed-tools:
  - Bash
  - Read
---

# /version-check

Compare the local `SKILL.md` `version:` field against the GitHub remote and report.

## Procedure

### 1. Read local version
```bash
grep -m1 '^version:' "$HOME/.claude/skills/life_OS/SKILL.md" 2>/dev/null \
  || grep -m1 '^version:' SKILL.md
```
Extract the quoted value (e.g. `version: "1.8.5"` → `1.8.5`).

If file not found → emit `[Life OS] Skill not found at $HOME/.claude/skills/life_OS/SKILL.md` and exit.

### 2. Read remote version (3-second timeout)
```bash
curl -sf --max-time 3 "https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md" 2>/dev/null \
  | grep -m1 '^version:'
```
Extract the quoted value.

If curl fails (network unavailable / timeout) → emit `[Life OS] v<LOCAL> (version check skipped — network unavailable)` and exit.

### 3. Compare and report

- **Match**: `[Life OS] v<LOCAL> ✅ (latest)`
- **Mismatch**: `[Life OS] ⬆️ Update available: v<LOCAL> → v<REMOTE>` plus instruction `Run: /install-skill https://github.com/jasonhnd/life_OS`

### 4. (Optional) Cache result for daily reuse

Write the result to `$HOME/.cache/lifeos/version-check-$(date +%Y%m%d)` so re-invocation within the same day uses cache. Cache invalidates if the GitHub `main` branch SHA changed (compare via `curl -sf https://api.github.com/repos/jasonhnd/life_OS/branches/main`).

If `$ARGUMENTS` contains `--force`, skip cache and refetch.

## Use cases

- SessionStart automation (now invoked by retrospective Mode 0 instead of v1.8.4 hook)
- Manual: user types `/version-check` to verify they're on latest

## v1.8.5 changes vs v1.8.4 scripts/lifeos-version-check.sh

- v1.8.4: bash script with explicit daily cache file, run from SessionStart hook
- v1.8.5: LLM runs `curl + grep` directly via Bash tool. Cache logic optional (only worth it if version-check is invoked > 5× per day, which is rare). retrospective Mode 0 may invoke this as one of its housekeeping steps instead of relying on a hook.
