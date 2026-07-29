# SOUL · {your name or identifier}

> Personal identity archive. Each dimension represents a value, belief, or aspiration with two sides: what IS (observed from your decisions) and what SHOULD BE (your stated aspiration).
>
> Auto-updated by ADVISOR after every decision. Manual edits welcome — the system respects them. Delete a dimension to retire it.

---

## Dimension: Example Dimension Name

```yaml
dimension_id: example-dimension
created: 2026-04-21
last_updated: 2026-04-21
confidence: 0.5
evidence_count: 3
challenges: 0
tier: secondary
```

### What IS (observed)

One paragraph describing the pattern observed from your past decisions. Written by ADVISOR; you can edit.

Evidence:
- {decision_id_1} — brief excerpt showing this dimension
- {decision_id_2} — ...

### What SHOULD BE (aspiration)

Your stated aspiration for this dimension. ADVISOR leaves this **empty** when auto-creating — fill in when you're ready.

### Tension

Optional: one sentence describing the gap between IS and SHOULD BE — this is where growth happens.

---

## Dimension: Another Example

```yaml
dimension_id: another-dimension
confidence: 0.85
evidence_count: 12
challenges: 2
tier: core
```

### What IS

...

### What SHOULD BE

...

---

**Template usage**: this is the file format for `SOUL.md` at the root of your second-brain. New dimensions are auto-added by ADVISOR after every decision (when ≥2 evidence points accumulate). Tier is derived from confidence at runtime:
- `core` (≥ 0.7) — referenced by REVIEWER in every decision
- `secondary` (0.3 - 0.7) — top 3 most-relevant referenced
- `emerging` (0.2 - 0.3) — counted but not surfaced
- `dormant` (< 0.2) — excluded from snapshots, surfaced in briefing if 30+ days inactive

Confidence formula: `evidence_count / (evidence_count + challenges × 2)`

See `references/soul-spec.md` for full lifecycle + auto-write rules.
