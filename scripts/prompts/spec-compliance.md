# User-invoked prompt · spec-compliance (v1.8.0)

> Replaces the deleted `tools/spec_compliance_report.py`. ROUTER reads this
> when the user wants to audit "what does the spec promise vs what's
> actually happening".

## Trigger keywords

- `检查合规` / `spec compliance` / `承诺核对`
- `spec 上写的真的在跑吗`
- session-start-inbox hook reports `spec-compliance Nd` and user says "跑一下"

## Goal

Cross-check what the spec docs (pro/agents/, pro/CLAUDE.md, references/)
**promise** against what the runtime evidence (_meta/eval-history/,
_meta/runtime/) actually **shows**. Surface gaps so the user knows what's
written-but-not-running.

This is the v1.8.0 successor to the cron-driven audit; same logic, now
user-invoked.

## Steps

### 1. Scan promises

Glob `pro/agents/*.md`, `pro/CLAUDE.md`, `references/*.md`. For each file,
Grep for promise keywords:

```
always-on | always run | weekly | monthly | daily | cron | scheduled
| MUST run | enforced | mandatory | periodic | every N days
```

Build promise list: `(file, line, keyword, context_phrase)`.

### 2. Scan evidence

Look for matching evidence in:

```
_meta/eval-history/cron-runs/*       (legacy from before v1.8.0 pivot)
_meta/eval-history/recovery/*        (archiver recovery runs)
_meta/eval-history/auditor-patrol/*  (auditor patrol runs)
_meta/eval-history/*-{YYYY-MM}.md    (monthly reports)
_meta/runtime/*/X.json               (per-session audit trails)
```

For each promise, look for evidence file matching the topic + within the
expected interval. Mark as: `met` / `gap` / `unverifiable`.

### 3. Compute compliance ratio

```
compliance = met / (met + gap)
```

Don't count `unverifiable` (e.g., promises about user behavior, not system).

### 4. Write report

Write `_meta/eval-history/spec-compliance-{YYYY-MM-DD}.md`:

```markdown
# Spec compliance audit · {YYYY-MM-DD}

## Summary
- Promises detected: {N}
- Evidence found:    {M}
- Gaps:              {K}
- Compliance ratio:  {ratio}%

## Met ({M})
- {file:line} · "{keyword}" · evidence: {evidence_path}
...

## Gap ({K})
- {file:line} · "{keyword}" · {context_phrase} · last evidence: never / {age}
...

## Unverifiable ({J})
- {file:line} · {keyword} · reason: {why}
...

## Recommended actions
- {gap → either implement, remove the promise, or move to "aspirational"}
```

### 5. Report to user

```
🔍 spec-compliance done · {ratio}% compliance
   {N} promises · {M} met · {K} gap
   _meta/eval-history/spec-compliance-{date}.md
```

## Output path

- `_meta/eval-history/spec-compliance-{YYYY-MM-DD}.md`

## Notes

- This audit is most useful AFTER each architecture change. Run it after
  v1.8.0 pivot to baseline what's still promised vs what got removed.
- Don't auto-fix gaps. Surface them, let user decide (remove promise, or
  implement).
