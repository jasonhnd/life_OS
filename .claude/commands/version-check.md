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

### 3.5 Cross-version upgrade hints (v1.8.7+)

After the match/mismatch line, if local version is older than remote AND specific cross-version paths apply, append the corresponding upgrade hint:

| Local | Remote | Hint |
|-------|--------|------|
| `1.8.6` | `≥1.8.7` | `✅ v1.8.7 upgrade is zero-friction: git pull + /install-agents --refresh installs 2 new watch commands. archiver first wrap-up auto-creates gotchas.md with ≥10 seed entries. No migration command needed. Details: meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` |
| `1.8.5` | `≥1.8.7` | `⚠️ You're 2 versions behind. v1.8.6 added md-only ban on .yml/.json (no action needed if you didn't add those files). v1.8.7 then added .sql/.db/.sqlite ban + 7 new features. Same upgrade flow: git pull + /install-agents --refresh.` |
| `1.8.4` or earlier | `≥1.8.7` | `⚠️ You're ≥3 versions behind. See MIGRATION.md for the cumulative changes. Each minor patch was non-breaking but added HARD RULES. Recommended: read v1.8.5 RFC (hook retirement) + v1.8.6 + v1.8.7 release notes before upgrading.` |
| `1.7.x` | `≥1.8.0` | `⚠️ Major architectural change: v1.8.0 "100% LLM-native" pivot removed Python tools entirely. v1.8.5+ removed remaining bash hooks. See MIGRATION.md and RFCs for cumulative changes.` |

The hint is generated at command runtime (LLM compares versions and emits the appropriate row). Do NOT hardcode all versions — only the current set in this table is supported.

### 4. (Optional) Cache result for daily reuse

Write the result to `$HOME/.cache/lifeos/version-check-$(date +%Y%m%d)` so re-invocation within the same day uses cache. Cache invalidates if the GitHub `main` branch SHA changed (compare via `curl -sf https://api.github.com/repos/jasonhnd/life_OS/branches/main`).

If `$ARGUMENTS` contains `--force`, skip cache and refetch.

## Use cases

- SessionStart automation (now invoked by retrospective Mode 0 instead of v1.8.4 hook)
- Manual: user types `/version-check` to verify they're on latest

## v1.8.5 changes vs v1.8.4 scripts/lifeos-version-check.sh

- v1.8.4: bash script with explicit daily cache file, run from SessionStart hook
- v1.8.5: LLM runs `curl + grep` directly via Bash tool. Cache logic optional (only worth it if version-check is invoked > 5× per day, which is rare). retrospective Mode 0 may invoke this as one of its housekeeping steps instead of relying on a hook.
