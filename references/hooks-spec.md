# Shell Hooks Contract Specification (v1.7)

> Authoritative contract for the five shell hooks that enforce Life OS HARD RULE compliance at runtime. Each hook is a self-contained bash script that communicates with the Claude Code host via stdin JSON, stdout text, and exit codes. Bash + jq only — no Python runtime, no non-stdlib dependencies.

---

## 1 · Purpose

Shell hooks exist because documentation is not enforcement. LLMs drift. The 2026-04-19 COURT-START-001 incident proved that writing "HARD RULE" in a markdown file does not make the rule hard — the orchestrator itself can skip subagent launches, fabricate file paths, and salami-slice corrections across user turns. Hooks catch that drift at runtime.

A hook runs in a subprocess outside the LLM context. The LLM cannot bribe it, forget it, or rationalize around it. When a hook fires, it either:

- Passes through silently (exit 0) — the LLM never sees the hook ran
- Injects a system reminder (exit 0 with stdout) — the text is inserted into the LLM context as authoritative
- Blocks the action (exit 2 with stderr) — the tool call is cancelled and the LLM is told why

This spec defines the five hooks required for v1.7, their contracts, their regex patterns, and the violation-logging mechanism.

---

## 2 · Platform Support

**Claude Code only (v1.7).** The hook system described here exists natively in Anthropic's Claude Code CLI. Gemini CLI and Codex CLI do not expose an equivalent hook surface in v1.7 — they fall back to prompt-level enforcement (SKILL.md HARD RULE statements) without the runtime backstop.

When Gemini / Codex publish compatible hook specs, the same five scripts can be registered there. Until then, Life OS on non-Claude-Code hosts gets only Layer 1 (documentation) and Layer 2 (subagent isolation). This is documented in `docs/architecture/execution-layer.md`.

---

## 3 · Hook System Architecture

### 3.1 Claude Code hook types

Hooks are declared in `~/.claude/settings.json` under `hooks`. Four events matter:

| Event | When it fires | Typical use |
|-------|---------------|-------------|
| `UserPromptSubmit` | Before the LLM processes each user message | Detect triggers, inject HARD RULE |
| `PreToolUse` | Before any tool call | Validate args, block dangerous paths |
| `PostToolUse` | After any tool call | Verify LLM actually did what it claimed |
| `Stop` | When the session ends | Validate completion checklists |

Matching is by tool name (`PreToolUse` / `PostToolUse`) or wildcard (`UserPromptSubmit` / `Stop`).

### 3.2 Hook mechanics

Claude Code invokes each hook as a subprocess, writes a JSON context object to stdin, reads stdout as an injected `system_reminder`, reads stderr for user-facing diagnostics (only shown on block), and checks the exit code:

- `0` — pass through. Non-empty stdout becomes a system reminder.
- `2` — block. The tool call is cancelled; stdout + stderr shown to the LLM as the block reason.
- anything else — hook error. Claude Code logs it and continues without blocking.

### 3.3 Input JSON schema

**`UserPromptSubmit`**: `{prompt, session_id, cwd}`
**`PreToolUse` / `PostToolUse`**: `{tool_name, tool_input, tool_result, session_id, cwd, recent_user_message}`
**`Stop`**: `{session_id, final_state, transcript_path}`

Every hook parses with `jq -r` and treats values as untrusted data — a malicious prompt can contain shell metacharacters.

---

## 4 · Strict Block on Violation (User Decision #6)

When a hook detects a HARD RULE violation:

1. Exit with code `2` (cancel the tool call or prompt)
2. Write an explanation to stdout — this becomes the `system_reminder` the LLM must read
3. Append a structured row to `{compliance_path}/violations.md` (path auto-detected per §6)

The LLM can then retry correctly. The user sees the block explanation in their terminal. The violation stays under git.

**Why strict block instead of advisory:** COURT-START-001 proved documentation-level HARD RULE gets ignored. A hard block forces re-planning. User decision #6.

---

## 5 · The Five v1.7 Hooks

All hook scripts live in `scripts/hooks/` inside the Life OS skill package, installed to `~/.claude/skills/life_OS/scripts/hooks/` at skill-install time.

### 5.1 `pre-prompt-guard.sh`

- **Event:** `UserPromptSubmit`, matcher `*`
- **Purpose:** Detect trigger words; inject the HARD RULE mandating a subagent launch.
- **Solves:** COURT-START-001 — ROUTER running retrospective steps in main context.

**Contract:** Parse `prompt` from stdin. If matched against the trigger table, emit a `<system-reminder>` to stdout and exit 0. Otherwise exit 0 with no output. This hook never exits 2 — it only injects guidance.

**Trigger table:**

| Pattern | Subagent | Mode |
|---------|----------|------|
| `上朝` / `start` / `begin` / `はじめる` / `開始` / `朝廷開始` / `閣議開始` | `retrospective` | Start Session |
| `退朝` / `adjourn` / `done` / `end` / `お疲れ` / `終わり` / `结束` | `archiver` | Adjourn 4-phase |
| `复盘` / `review` / `早朝` / `振り返り` / `レビュー` | `retrospective` | Review Mode |
| `朝堂议政` / `debate` / `討論` | `council` | 3-round debate |
| `quick` / `快速分析` / `クイック` | — | ROUTER Express |

**Example stdout when `上朝` is detected:**

```
<system-reminder>
HARD RULE · Trigger "上朝" detected.

Required output (exactly 2 lines):
Line 1: theme-appropriate greeting
Line 2: Agent tool call for retrospective Mode 0

You MUST:
- Read pro/agents/retrospective.md BEFORE the Agent call
- Launch(retrospective) as an independent subagent
- NOT execute any step of retrospective in main context
- NOT simulate subagent output

Any deviation = HARD RULE violation, logged to compliance/violations.md.
Precedent: COURT-START-001 (2026-04-19).
</system-reminder>
```

### 5.2 `post-response-verify.sh`

- **Event:** `PostToolUse`, matcher `Task|Bash|Write|Edit`
- **Purpose:** Verify the LLM actually launched the correct subagent after a trigger word.
- **Solves:** ROUTER claiming "let me launch retrospective" but then running Bash / Read directly.

**Contract:** Parse `tool_name`, `tool_input`, `recent_user_message`. If `recent_user_message` matched a trigger and `tool_name != Task` (or `Task` targets a wrong subagent), log violation and exit 2 with a corrective reminder. Otherwise exit 0.

**Detection rules:**

| Recent trigger | Expected tool | Violation if... |
|----------------|---------------|-----------------|
| `上朝` / `start` | `Task(retrospective)` | `Bash` reading `_meta/`, `Read` on config, direct `Write` to journal |
| `退朝` / `adjourn` | `Task(archiver)` | Any `git` command, `Write` to `_meta/decisions/`, Notion MCP call before archiver returns |
| `复盘` / `review` | `Task(retrospective)` | Direct `Read` of `_meta/sessions/INDEX.md` without subagent |

### 5.3 `pre-write-scan.sh`

- **Event:** `PreToolUse`, matcher `Write|Edit`
- **Purpose:** Fast regex scan of content destined for SOUL / wiki / concepts / user-patterns.
- **Solves:** LLM-generated content containing injection payloads (malicious or accidental) reaching long-term knowledge files.

**Contract:** Parse `file_path` + `content` (or `new_string` for Edit). If `file_path` is outside the scoped set (`SOUL.md`, `wiki/**`, `_meta/concepts/**`, `user-patterns.md`), exit 0 pass-through. Inside the set, run the 15-pattern regex scan + the invisible-Unicode scan. On any match, log violation, exit 2 with the pattern flag.

This regex scan is the cheap first-pass. The LLM-based privacy check (user decision #5) runs later in archiver's knowledge extraction — the regex is the fast first line of defense.

**The 15 regex patterns:**

| # | Pattern name | Regex |
|---|--------------|-------|
| 1 | Prompt injection — ignore instructions | `(?i)ignore (all )?(previous\|above) (instructions\|rules)\|disregard (all \|the )?system` |
| 2 | Prompt injection — reveal system | `(?i)(reveal\|output\|print\|show) (your\|the) (system prompt\|hidden instructions\|initial prompt)` |
| 3 | Prompt injection — role override | `(?i)you are now\|from now on you are\|new identity\|forget you are claude` |
| 4 | Shell injection — command substitution | `\$\([^)]{1,100}\)` |
| 5 | Shell injection — backticks | `` `[^`]{1,100}` `` |
| 6 | SQL injection — UNION / DROP / DELETE | `(?i)union\s+select\|drop\s+table\|delete\s+from\s+\w+\s+where\s+\d` |
| 7 | SQL injection — OR 1=1 | `('\|")\s*OR\s*('\|")?\d+('\|")?\s*=\s*('\|")?\d+` |
| 8 | Secret — high-entropy key | `\b[A-Z0-9]{32,}\b` |
| 9 | Secret — common prefixes | `(sk\|pk\|api\|secret\|token)_[a-zA-Z0-9]{16,}` |
| 10 | Secret — AWS access key | `\bAKIA[0-9A-Z]{16}\b` |
| 11 | Secret — GitHub token | `\bghp_[a-zA-Z0-9]{36}\b` |
| 12 | Secret — Slack token | `\bxox[pbar]-[0-9]{10,}-[a-zA-Z0-9]{24,}\b` |
| 13 | Private key block | `-----BEGIN (RSA \|DSA \|EC \|OPENSSH )?PRIVATE KEY-----` |
| 14 | Credit card | `\b(4\d{12}(\d{3})?\|5[1-5]\d{14}\|3[47]\d{13}\|6(?:011\|5\d{2})\d{12})\b` |
| 15 | PII — SSN | `\b\d{3}-\d{2}-\d{4}\b` |

**Invisible-Unicode scan:** blocks U+200B, U+200C, U+200D, U+2060, U+FEFF (mid-file), and U+202A–U+202E (BIDI overrides). These are common in injection attacks hiding payload from human review.

### 5.4 `stop-session-verify.sh`

- **Event:** `Stop`, matcher `*`
- **Purpose:** Verify the adjourn flow completed with a full Completion Checklist.
- **Solves:** Archiver half-completion — Phase 1 runs, Phase 4 gets skipped.

**Contract:** Parse `transcript_path` from stdin. Grep transcript for adjourn triggers. If no adjourn fired, exit 0. If adjourn fired, verify all four archiver phases (`Phase 1: Archive`, `Phase 2: Knowledge Extraction`, `Phase 3: DREAM`, `Phase 4: Sync`) appear with non-placeholder values, plus the orchestrator's post-archiver Notion sync block. Missing or `TBD` → log violation. Cannot block (session already ending) — log only, exit 0.

### 5.5 `pre-read-allowlist.sh`

- **Event:** `PreToolUse`, matcher `Read`
- **Purpose:** Prevent reads outside Life OS scope, especially credential files.
- **Solves:** Accidental or injected reads of `~/.ssh/`, `~/.aws/credentials`, `/etc/passwd`.

**Contract:** Resolve `file_path` to absolute. If inside `cwd` or the explicit allowlist → exit 0. If matches the denylist → exit 2 with reminder. Otherwise → exit 0 (trust LLM outside the denylist).

**Denylist:** `~/.ssh/**`, `~/.aws/**`, `~/.gcp/**`, `~/.azure/**`, `~/.docker/config.json`, `~/.kube/config`, `~/.npmrc`, `~/.pypirc`, `/etc/passwd`, `/etc/shadow`, `/etc/sudoers*`, `**/id_rsa`, `**/id_ed25519`, `**/.env`, `**/.env.*`.

**Allowlist (overrides anything):** `$cwd/**`, `~/.claude/skills/life_OS/**`, `~/.claude/scripts/**`, `~/.cache/lifeos/**`.

---

## 6 · Compliance Path Auto-Detection (User Decision #14)

Life OS runs in two distinct repo contexts: the dev repo (skill codebase) and the user's second-brain (data repo). Each has its own log.

```bash
detect_compliance_path() {
  if [ -f "pro/agents/retrospective.md" ]; then
    echo "pro/compliance/violations.md"       # dev repo
  elif [ -d "_meta/" ] && [ -f "_meta/config.md" ]; then
    echo "_meta/compliance/violations.md"     # second-brain
  else
    echo "/dev/null"                          # skip logging
  fi
}
```

- `pro/agents/retrospective.md` = dev-repo marker
- `_meta/config.md` = second-brain marker
- Any other `cwd` gets `/dev/null` — we do not create compliance directories in unrelated repos

Both `violations.md` files are git-tracked; violations travel with the repo. Neither path writes to `~/.claude/` — that would violate the "all state is markdown + git" principle established after COURT-START-001.

---

## 7 · Violations Log Format

**Header** (created by retrospective Mode 0 on first run):

```markdown
# Compliance Violations Log

> Rolling 90-day window. Older rows archived to `archive/{year}-Q{n}.md` by `backup.py`.

| Timestamp | Type | Severity | Agent | Detail | Hook | Resolved |
|-----------|------|----------|-------|--------|------|----------|
```

**Row example:**

```
| 2026-04-20T14:32:10+09:00 | CLASS_A | critical | ROUTER | Start trigger but no retrospective subagent launched | pre-prompt-guard | open |
```

**Columns:**

| Column | Values | Notes |
|--------|--------|-------|
| Timestamp | ISO 8601 with timezone | `date -Iseconds` |
| Type | `CLASS_A` / `B` / `C` / `D` / `E` | See §8 |
| Severity | `critical` / `high` / `medium` / `low` | Per §8 |
| Agent | `ROUTER` / `archiver` / `retrospective` / `unknown` | Inferred from tool_name |
| Detail | One-line metadata description | No user prompt content — PII safety |
| Hook | Script name | For debugging |
| Resolved | `open` / `resolved-<date>` | Flipped by AUDITOR or manual |

**Anti-patterns for `Detail`:** never include user prompt content, file contents, or secrets (even "redacted"). Use metadata only — pattern ID, file path category, hook name.

---

## 8 · Escalation Ladder

Hooks append rows; `stats.py` (Layer 4) drives escalation decisions.

**30-day rolling window, same-type count:**

| Count | Action |
|-------|--------|
| ≥ 3 | 🚨 warning banner at top of next `retrospective` Start Session briefing |
| ≥ 5 | AUDITOR forced into Patrol Inspection mode every session start |
| ≥ 10 | Systemic issue — flag in `eval-history.md` for next-version spec revision |

**Severity mapping:**

| Type | Severity | Example |
|------|----------|---------|
| `CLASS_A` | critical | ROUTER skips subagent launch after trigger word |
| `CLASS_B` | critical | Agent fabricates file path / chapter / HARD RULE source |
| `CLASS_C` | high | Adjourn ends without Completion Checklist |
| `CLASS_D` | critical | Injection pattern in proposed Write to SOUL/wiki |
| `CLASS_E` | high | Read attempt on denylist path |

Escalation is deterministic: `stats.py` computes it on demand from `violations.md`; hooks only append rows. This keeps hooks fast (< 100ms) and escalation inspectable.

---

## 9 · Archive Policy

`violations.md` capped at rolling 90 days. Older rows rotate quarterly, moved by `backup.py` (not a hook — hooks don't move data).

```
pro/compliance/                          # dev repo
├── violations.md                        # current 90 days
├── archive/2026-Q2.md                   # rotated quarterly
└── 2026-04-19-court-start-violation.md  # major incident dossiers (permanent)

_meta/compliance/                        # second-brain, same structure
├── violations.md
└── archive/
```

Row-level violations rotate. Major incident dossiers (anything triggering a rebuild) stay indefinitely.

---

## 10 · Installation

v1.6.2's `setup-hooks.sh` installs one SessionStart version-check hook. v1.7 extends it to register all five hooks atomically.

**Settings JSON structure added by v1.7:**

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-prompt-guard.sh\"", "timeout": 5}],
      "id": "life-os-pre-prompt-guard"
    }],
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-write-scan.sh\"", "timeout": 5}],
        "id": "life-os-pre-write-scan"
      },
      {
        "matcher": "Read",
        "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-read-allowlist.sh\"", "timeout": 3}],
        "id": "life-os-pre-read-allowlist"
      }
    ],
    "PostToolUse": [{
      "matcher": "Task|Bash|Write|Edit",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/post-response-verify.sh\"", "timeout": 5}],
      "id": "life-os-post-response-verify"
    }],
    "Stop": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/stop-session-verify.sh\"", "timeout": 10}],
      "id": "life-os-stop-session-verify"
    }]
  }
}
```

**Pre-flight checks** (inherited from v1.6.2 `setup-hooks.sh`):

1. `jq` is installed
2. Existing `settings.json` is valid JSON
3. All five hook scripts exist in `scripts/hooks/` and are executable
4. All five are idempotent (installing twice is a no-op)

On failure: print reason, don't modify `settings.json`, exit 1. On success: write atomically via `settings.json.tmp` + `mv`.

**Timeouts:** 3s for pre-read (pure path matching), 5s for prompt / write / post checks (regex scans), 10s for stop-verify (transcript parse). If a hook hangs, Claude Code kills it and treats it as a hook error — the tool call is not blocked.

---

## 11 · Uninstall / Disable

**Remove one hook:**

```bash
jq '.hooks.UserPromptSubmit = [.hooks.UserPromptSubmit[] | select(.id != "life-os-pre-prompt-guard")]' \
   ~/.claude/settings.json > ~/.claude/settings.json.tmp \
   && mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

**Uninstall all Life OS hooks:** `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh --uninstall`. The `--uninstall` flag (added in v1.7) removes every hook whose `id` starts with `life-os-`. Does not touch other skills.

**Manual edit:** open `~/.claude/settings.json` and delete entries. Always safe — hooks are purely additive.

**Disable without uninstalling:** rename `pre-prompt-guard.sh` → `pre-prompt-guard.sh.disabled`. Claude Code logs the missing executable as a hook error and continues without blocking.

---

## 12 · Testing

Hook behavior is covered by `evals/scenarios/hook-compliance/`:

| # | Scenario | Expected |
|---|----------|----------|
| 1 | User says "上朝", LLM launches retrospective correctly | pre-prompt-guard injects reminder, post-response-verify passes |
| 2 | User says "上朝", LLM runs Bash to read `_meta/sessions/INDEX.md` | pre-prompt-guard injects, post-response-verify blocks (CLASS_A) |
| 3 | Write to `wiki/notes.md` with "ignore all previous instructions" | pre-write-scan blocks with pattern #1 |
| 4 | Write to `projects/work/index.md` (out of scope) | pre-write-scan passes through |
| 5 | Read `~/.ssh/id_rsa` | pre-read-allowlist blocks (CLASS_E) |
| 6 | Read `$cwd/projects/foo.md` | pre-read-allowlist passes through |
| 7 | "退朝", archiver runs, session ends without Phase 4 | stop-session-verify logs CLASS_C |
| 8 | Arbitrary prompt "what's the weather" | pre-prompt-guard exits 0 silently |

Each scenario is a markdown file with input, expected hook output, and expected `violations.md` diff. The eval harness replays them deterministically — no LLM in the hook test path, so hook behavior is verified independently of LLM drift.

---

## 13 · Anti-Patterns

- **Don't be slow.** Default timeout 5s (3s for pre-read). A hook doing a web request or filesystem walk is broken. Hooks run on every relevant event.
- **Don't write to the compliance path without checking existence.** Use the `/dev/null` fallback from §6 rather than creating arbitrary directories in random repos.
- **Don't block read-only operations unless the denylist matches.** False-positive blocks are worse than missed warnings for reads.
- **Don't log the user's prompt content.** PII risk. Log metadata only: trigger word, pattern ID, hook name. User prompt stays in Claude Code transcript, never in git-tracked compliance logs.
- **Don't require Python.** Bash + jq only. Python is Layer 4 (background workers), not a prerequisite for Layer 3.
- **Don't exit 1 when blocking.** Exit 1 = "hook error, continue" per Claude Code semantics. Exit 2 = "block." Getting this wrong turns hard blocks into silent warnings.
- **Don't emit ANSI color codes in stdout.** stdout becomes a system reminder — keep it plain markdown. Use stderr for decoration, only visible on block.
- **Don't trust stdin JSON values as shell tokens.** Always `jq -r` and quote expansions. A malicious prompt containing `$(rm -rf ~)` must not execute.

---

## 14 · Related Specs

- `references/data-layer.md` — data-layer boundaries; `compliance/violations.md` lives here alongside other `_meta/` surfaces
- `references/eval-history-spec.md` — AUDITOR eval-history dimension `process_compliance` consumes violation patterns flagged by hooks
- `references/tools-spec.md` — Python Layer 4 tools (`stats.py`, `backup.py`, `reconcile.py`) that complement hooks
- `references/cortex-spec.md` — overall Cortex architecture; hooks protect its markdown-first invariants
- `pro/compliance/2026-04-19-court-start-violation.md` — the founding incident that justified this spec
- `docs/architecture/execution-layer.md` — full Layer 3 (hooks) + Layer 4 (Python tools) architecture
- `scripts/setup-hooks.sh` — v1.6.2 installer template that v1.7's extended installer inherits from
- `scripts/lifeos-version-check.sh` — v1.6.2's only hook; reference for "pre-flight, idempotent, atomic" pattern

The `violations.md` data model is defined in §7 of this spec (format, columns, escalation ladder); it is NOT defined in cortex-spec.

**END**
