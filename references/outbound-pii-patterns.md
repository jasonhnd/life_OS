---
status: active
authoritative: true
related_hook: scripts/hooks/pre-notion-write.sh
introduced: v1.8.3
---

# Outbound PII Pattern Table

> Pattern catalogue for `pre-notion-write.sh` — the outbound boundary scanner.
> This is the **outbound** counterpart to the inbound `pre-write-scan.sh`
> 15-pattern set in `references/hooks-spec.md` §5.3.

## 1 · Why a Separate Pattern Set

`pre-write-scan.sh` (in-scope: `SOUL.md`, `wiki/**`, `_meta/concepts/**`,
`user-patterns.md`) defends **the second-brain knowledge layer** against
secrets, prompt injection, and invisible Unicode. It does **not** scan
`_meta/outbox/<sid>/decisions/`, `_meta/outbox/<sid>/journal/`,
`_meta/outbox/<sid>/tasks/` — those files contain the user's raw
deliberation, by design (a journal needs to remember names, amounts,
relationships).

But the moment that content leaves the local repo and travels to a
**third-party storage layer** (Notion), the threat model changes:

- Notion workspaces may be shared (team Notion, accidental public share)
- Notion AI may index page content for org-wide assistants
- Mobile-device theft exposes Notion app
- Notion has had data-breach incidents (treat as untrusted long-term)
- Decisions written by archiver Phase 1 contain raw user prose — NOT the
  privacy-filtered wiki/SOUL summaries

**Local outbox is private; Notion is the outbound boundary.** The same
sentence can be acceptable in `_meta/outbox/` (under user's git) but
unacceptable on Notion's servers (out of user's control).

---

## 2 · Three-Tier Action Model

Each pattern carries a `mode`:

| mode | Hook behavior | When to use |
|------|---------------|-------------|
| **block** | exit 2, hard cancel the Notion MCP call | Catastrophic leaks (private keys, full credit-card numbers). User MUST rewrite or skip. |
| **warn** | exit 0, emit `<system-reminder>` asking ROUTER to confirm with user before retrying | Sensitive but legitimate content (third-party names, family references). Default-deny posture, but user can override. |
| **info** | exit 0, emit a quieter notice; ROUTER MAY proceed | Pattern matched but ambiguous (e.g., a single email could be the user's own). Logged for audit only. |

**Why no `strip` mode**: PreToolUse hooks in Claude Code cannot rewrite
`tool_input`. They can only pass, block, or inject a reminder. Sanitizing
content must therefore happen one level up — see `pro/CLAUDE.md` Step 10a
sanitize handoff (the orchestrator reads the hook's reminder, generates a
sanitized version, then re-issues the Notion MCP call). The hook is the
detector, not the rewriter.

---

## 3 · Pattern Catalogue

Patterns are grouped by category. Within each group, scan order matters
(most specific first, most general last) — first-match wins.

### Group A · Hard Secrets (mode: block)

These are unambiguous credentials that should never reach Notion under
any circumstance.

| # | Name | Regex | Notes |
|---|------|-------|-------|
| A1 | private-key-block | `-----BEGIN[[:space:]]+(RSA[[:space:]]+\|DSA[[:space:]]+\|EC[[:space:]]+\|OPENSSH[[:space:]]+)?PRIVATE[[:space:]]+KEY-----` | Same as `pre-write-scan` #13 |
| A2 | aws-access-key | `AKIA[0-9A-Z]{16}` | Same as `pre-write-scan` #10 |
| A3 | github-token | `ghp_[a-zA-Z0-9]{36}` | Same as `pre-write-scan` #11 |
| A4 | slack-token | `xox[pbar]-[0-9]{10,}-[a-zA-Z0-9]{24,}` | Same as `pre-write-scan` #12 |
| A5 | secret-prefix-token | `(sk\|pk\|api\|secret\|token)_[a-zA-Z0-9]{20,}` | Tighter than `pre-write-scan` #9 (20 vs 16) — outbound is stricter |
| A6 | full-credit-card | `4[0-9]{12}([0-9]{3})?\|5[1-5][0-9]{14}\|3[47][0-9]{13}\|6(011\|5[0-9]{2})[0-9]{12}` | Same as `pre-write-scan` #14 |
| A7 | ssn-us | `[0-9]{3}-[0-9]{2}-[0-9]{4}` | Same as `pre-write-scan` #15 |
| A8 | jp-mynumber | `\b[0-9]{4}[-[:space:]]?[0-9]{4}[-[:space:]]?[0-9]{4}\b` | Japanese 個人番号 (12 digits, often hyphenated). False-positive risk on phone numbers — order matters: scan after Group D phone patterns. |
| A9 | high-entropy-key | `[A-Za-z0-9+/]{40,}={0,2}` | Base64-shaped blob ≥ 40 chars (likely key/cert/JWT) |

### Group B · Personal Identifier — Third Parties (mode: warn)

The user discussing their own relationships is fine. Naming a third party
on Notion (where Notion AI / shared workspace / leaked dump may surface
that name) is the risk.

| # | Name | Regex | Notes |
|---|------|-------|-------|
| B1 | family-relation-event | `(老婆\|老公\|妻子\|丈夫\|爸爸?\|妈妈?\|父親\|母親\|儿子\|女儿\|息子\|娘\|兄弟\|姐妹\|姉\|妹\|哥哥?\|弟弟?\|wife\|husband\|mom\|dad\|son\|daughter)[^。\n]{0,40}(出轨\|生病\|住院\|破产\|失业\|被裁\|离婚\|分手\|去世\|过世\|cheat\|sick\|fired\|laid[[:space:]]?off\|divorce\|died\|passed[[:space:]]away)` | Family member + sensitive event in same sentence |
| B2 | named-person-event | `(?:[A-Z][a-z]+[[:space:]][A-Z][a-z]+)[^.\n]{0,40}(fired\|laid[[:space:]]?off\|divorced\|cheating\|bankrupt\|sick\|hospitalized\|died)` | Western "FirstName LastName" + sensitive verb |
| B3 | cn-name-event | `[\x{4e00}-\x{9fff}]{2,3}(出轨\|生病\|住院\|破产\|失业\|被裁\|离婚\|分手\|去世\|过世\|跳槽\|被开\|跑路)` | 2-3 Han chars (likely full Chinese name) + sensitive predicate. Note: bash regex doesn't support `\x{...}` directly — implementation will use raw byte ranges. |

### Group C · Financial Specifics — Combined (mode: warn)

Loose money mentions are fine ("about 6 months runway"). Specific amounts
combined with named entities are not.

| # | Name | Regex | Notes |
|---|------|-------|-------|
| C1 | company-amount | `[A-Z][A-Za-z0-9&]{2,}[[:space:]]?(株式会社\|有限公司\|Inc\|Ltd\|LLC\|Corp\|Co\.)?[^.\n]{0,30}(¥\|￥\|\\\$\|€\|£\|RMB\|JPY\|USD)?[[:space:]]?[0-9]{4,}([,，][0-9]{3})*([.][0-9]+)?(万\|億\|亿\|million\|billion\|k\|m\|b)?` | Capitalized company-shaped token + ≥ 4-digit number nearby |
| C2 | bank-account | `\b[0-9]{8,19}\b` | Plain digit run ≥ 8 (matches account numbers, IBAN tail). High false-positive — must be after C3. |
| C3 | jp-bank-detail | `(三菱UFJ\|三井住友\|みずほ\|ゆうちょ\|楽天銀行)[^。\n]{0,30}[0-9]{6,}` | Japanese bank name + digits |

### Group D · Contact Information (mode: warn)

| # | Name | Regex | Notes |
|---|------|-------|-------|
| D1 | email-address | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` | Any email |
| D2 | phone-international | `\+[0-9]{1,3}[[:space:]\-]?[0-9]{2,4}[[:space:]\-]?[0-9]{4,8}` | International phone |
| D3 | phone-jp-mobile | `0[789]0[[:space:]\-]?[0-9]{4}[[:space:]\-]?[0-9]{4}` | Japanese mobile (070/080/090) |
| D4 | phone-cn-mobile | `1[3-9][0-9][[:space:]\-]?[0-9]{4}[[:space:]\-]?[0-9]{4}` | Chinese mobile |
| D5 | jp-postal-address | `〒?[0-9]{3}[-[:space:]]?[0-9]{4}[^\n]{0,40}(都\|道\|府\|県)` | Japanese postal code + prefecture marker |

### Group E · Soft Signals (mode: info)

These match more often than they should be acted on. Logged so AUDITOR
can see frequency trends but no user-facing reminder.

| # | Name | Regex | Notes |
|---|------|-------|-------|
| E1 | url-tracker | `https?://[^[:space:]]*[?&](utm_\|fbclid\|gclid)` | URL with tracking parameters |
| E2 | jwt-shape | `eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}` | Three base64 segments separated by dots |

---

## 4 · Pattern Order Contract

The hook applies patterns in this order, first-match-wins per group, but
**all groups are evaluated** so the audit log captures every category hit:

1. Group A (block) — if any A pattern hits, set `block_reason`
2. Group B (warn) — collect all B hits
3. Group C (warn) — collect all C hits
4. Group D (warn) — collect all D hits
5. Group E (info) — collect all E hits

Final action:

- If any A hit → exit 2 (block)
- Else if any B/C/D hit → exit 0 + `<system-reminder>` (warn)
- Else if any E hit → exit 0 + quiet log only
- Else → exit 0 silently

---

## 5 · Audit Trail Contract

Every invocation writes `_meta/runtime/<sid>/notion-pii-scan-<ts>.json`
with this schema (no raw content, only category counts + first-match
pattern IDs per group):

```json
{
  "subagent": "pre-notion-write",
  "step_or_phase": "outbound-scan",
  "step_name": "Notion outbound PII scan",
  "started_at": "ISO 8601",
  "ended_at": "ISO 8601",
  "input_summary": "tool_name=<name> body_length=<n> properties_count=<n>",
  "tool_calls": [],
  "llm_reasoning": "(regex scan, no LLM)",
  "output_summary": "verdict=<block|warn|info|pass> hits=<comma-list-of-IDs>",
  "matched_patterns": {
    "A": ["A1", "A6"],
    "B": [],
    "C": ["C1"],
    "D": [],
    "E": []
  },
  "verdict": "warn",
  "tokens": {"input": 0, "output": 0},
  "audit_trail_version": "v1.8.3-r11"
}
```

The `matched_patterns` block is what makes this auditable: AUDITOR
Mode 3 patrol can grep these files for trends ("user's adjourns
trigger B1 in 40% of sessions → user is journaling family events that
shouldn't be on Notion at all").

---

## 6 · Maintenance Rules

- **Adding a pattern**: append to the relevant group in §3, increment
  group letter+number (don't reuse retired numbers), add a row in §4 if
  group order changes.
- **Tuning a pattern**: prefer adding a more-specific pattern earlier in
  the group rather than loosening an existing one. Loosening risks
  false-negative drift.
- **False positives reported by user**: classify — was the pattern wrong
  (regex too broad), or was the user's content actually risky and they
  disagree (policy disagreement)? Tighten regex only for the former.
- **Never inline raw content** anywhere in this file or in audit
  trails. Pattern descriptions stay generic.

---

## 7 · Out of Scope (v1.8.3)

- LLM-based privacy classification (slower, async — stays in archiver
  Phase 2 for wiki/SOUL writes, not in the synchronous hook path).
- Cross-tool outbound scanning (Slack MCP, Email MCP, etc) — same
  pattern table will apply when those gates are added; v1.8.3 only
  wires the Notion gate.
- Per-user pattern customisation — globally hard-coded for v1.8.3.
  v1.9 may add `_meta/outbound-allowlist.md` for user overrides.
