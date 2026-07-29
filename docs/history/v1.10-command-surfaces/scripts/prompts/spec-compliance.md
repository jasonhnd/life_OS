# User-invoked prompt · spec-compliance (v1.8.2 · Obsidian-style)

> Replaces the deleted `tools/spec_compliance_report.py`. ROUTER reads this
> when the user wants to audit "what does the spec promise vs what's
> actually happening".
>
> **v1.8.2 HARD RULE #11**: Compliance report renders in Obsidian. Apply
> `references/obsidian-style.md` — `> [!info]` for the ratio summary,
> `> [!warning]` for unfulfilled promises, `> [!success]` for fulfilled,
> `[[wikilinks]]` for spec refs, nested tags.

## Trigger keywords

- `检查合规` / `spec compliance` / `承诺核对`
- `spec 上写的真的在跑吗`
- retrospective Mode 0 Conscious Patrol reports `spec-compliance Nd` overdue and user says "跑一下"

## Goal

Cross-check what the spec docs (agents/, hosts/CLAUDE.md, references/)
**promise** against what the runtime evidence (meta/eval-history/,
meta/runtime/) actually **shows**. Surface gaps so the user knows what's
written-but-not-running.

This is the v1.8.0 successor to the cron-driven audit; same logic, now
user-invoked.

## Steps

### 1. Scan promises

Glob `agents/*.md`, `hosts/CLAUDE.md`, `references/*.md`. For each file,
Grep for promise keywords:

```
always-on | always run | weekly | monthly | daily | cron | scheduled
| MUST run | enforced | mandatory | periodic | every N days
```

Build promise list: `(file, line, keyword, context_phrase)`.

### 2. Scan evidence

Look for matching evidence in:

```
meta/eval-history/maintenance/*     (current v1.8.0 path; user-invoked maintenance runs)
meta/eval-history/recovery/*        (archiver recovery runs)
meta/eval-history/auditor-patrol/*  (auditor patrol runs)
meta/eval-history/*-{YYYY-MM}.md    (monthly reports)
meta/runtime/*/X.md                 (per-session audit trails, R13 markdown)
```

For each promise, look for evidence file matching the topic + within the
expected interval. Mark as: `met` / `gap` / `unverifiable`.

### 3. Compute compliance ratio

```
compliance = met / (met + gap)
```

Don't count `unverifiable` (e.g., promises about user behavior, not system).

### 4. Write report

Write `meta/eval-history/spec-compliance-{YYYY-MM-DD}.md`:

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
   meta/eval-history/spec-compliance-{date}.md
```

## Output path

- `meta/eval-history/spec-compliance-{YYYY-MM-DD}.md`

## Notes

- This audit is most useful AFTER each architecture change. Run it after
  v1.8.0 pivot to baseline what's still promised vs what got removed.
- Don't auto-fix gaps. Surface them, let user decide (remove promise, or
  implement).

## Final step · Maintenance ledger stamp (v1.10.0)

Per `references/maintenance-ledger-spec.md`: upsert this job's row in
`meta/maintenance-ledger.md` — create the file with its standard header if
missing; if a row for this job exists, replace it in place, otherwise insert
keeping alphabetical order. Never duplicate a row.

`| spec-compliance | 30d | <today YYYY-MM-DD, from a real date command — no fabrication> |`
