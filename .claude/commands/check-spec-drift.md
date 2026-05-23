---
description: Scan active spec/prompt/code files for (1) references to deleted files (broken paths) and (2) architectural tokens retired in past pivots (forbidden tokens). Replaces v1.8.4 scripts/check-spec-drift.sh as part of v1.8.5 hook layer retirement.
argument-hint: "[--strict]  (default: warnings-only; --strict fails on any drift)"
allowed-tools:
  - Bash
  - Grep
  - Glob
  - Read
---

# /check-spec-drift

You are scanning the repository for spec drift — references to files/tokens that have been retired by past pivots. Run two scanners and report findings.

## Mode

- Default: **warnings-only** (report findings, exit 0)
- `--strict`: **fail on any drift** (exit 1 if any finding)

## Files in scope (active files)

Scan all `.md`, `.yml`, `.yaml`, `.json` under repo root, **excluding**:
- `CHANGELOG.md` and `i18n/*/CHANGELOG.md`
- `backup/` (gitignored clone)
- `pro/compliance/` (violation logs are historical)
- `MIGRATION.md`
- `*-template.md`
- Files with YAML frontmatter declaring `status: legacy` or `authoritative: false`

## Scanner 1 · Broken paths

For every matching file, find references like `scripts/foo.sh`, `pro/agents/bar.md`, `tools/baz.py`, etc. Then `Read` each referenced path. Any reference whose target file does NOT exist is a **broken-path drift**.

Example grep:
```bash
grep -rEhn '(scripts|pro/agents|tools|references|themes|evals/scenarios|evals/rubrics|i18n/[a-z]+/references)/[a-zA-Z0-9_/.-]+\.(sh|py|md|yml|yaml)' \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.json' \
  | grep -vE '^(CHANGELOG|MIGRATION|backup/|pro/compliance/)'
```

For each match: check if the referenced file exists. Missing → flag as broken-path.

## Scanner 2 · Forbidden tokens

Search active files for these retired architectural tokens. Any hit in an active file (not exempted) is **forbidden-token drift**.

**Forbidden tokens (retired in v1.7-v1.8 pivots):**
- `retrospective-mode-0.sh` (Bash skeleton, removed v1.8.0)
- `retrospective-briefing-skeleton.sh`
- `archiver-briefing-skeleton.sh`
- `archiver-phase-prefetch.sh`
- `narrator-validator.md` (subagent deleted v1.8.0)
- `16-agents.md` (hardcoded count; per user "agent 数量不重要，就说'多个 agent'")
- `all-16-agents`
- `life-os-tool`
- `tools.cli`
- `tools/cli.py`
- `tools/migrate.py`
- `tools/memory.py`
- `setup-cron.sh`
- `run-cron-now.sh`
- `ALWAYS-ON`
- `cortex_enabled` (flag retired v1.8.0)

**v1.8.5 NEW forbidden tokens (hook layer retired):**
- `scripts/hooks/`
- `scripts/lib/`
- `tests/hooks/`
- `lifeos-compliance-check.sh`
- `lifeos-pre-prompt-guard.sh`
- `setup-hooks.sh`
- `pre-prompt-guard.sh`
- `post-response-verify.sh`
- `pre-notion-write.sh`
- `pre-bash-approval.sh`
- `pre-write-scan.sh`
- `pre-read-allowlist.sh`
- `stop-session-verify.sh`
- `session-start-inbox.sh`
- `pre-task-launch.sh`
- `post-task-audit-trail.sh`
- `pre-write-output-redirect.sh`

**Regex for agent count drift** (per user "多个 agent 就行"):
```regex
\b(16|17|18|19|20|21|22|23)\s*(个)?\s*(agent|agents|subagent|subagents|role|roles|角色)\b
```
Any hit in active file = drift.

## Output format

```
── /check-spec-drift · mode=warnings|strict ──

Broken-path findings: N
  file:line  →  missing reference: <path>
  ...

Forbidden-token findings: M
  file:line  →  token: <token>
  ...

Hardcoded-count findings: K
  file:line  →  match: "<excerpt>"
  ...

VERDICT: CLEAN / WARN / FAIL
```

- **CLEAN** if all three scanners return 0 findings.
- **WARN** if findings exist but mode is default (exit 0).
- **FAIL** if findings exist and mode is `--strict` (exit 1).

## When to invoke

- Manually before releasing a new version
- Automatically by `/verify-release` (called from inside as a pre-check)
- During AUDITOR Mode 3 patrol (every session end per Stage 7 改造)
