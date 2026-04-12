# SOUL Specification

SOUL.md is the user's personality archive — a living document that records who the user is, what they value, and how they think. It lives in the second-brain root directory.

## Principles

1. **Grows from zero** — SOUL.md starts empty. No initialization required.
2. **Evidence-based** — Every entry links to decisions/behaviors that support it.
3. **User-confirmed** — System proposes, user confirms. Nothing is auto-written.
4. **Contradictions are valuable** — Don't resolve them; surface them.

---

## Entry Format

Each entry in SOUL.md follows this structure:

```yaml
---
dimension: "[dimension name]"
confidence: 0.0          # 0-1, auto-calculated
evidence_count: 0         # supporting decisions/behaviors
challenges: 0             # contradicting behaviors
source: dream             # dream / remonstrator / hanlin / user
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
---
```

### What IS (实然)
[Observed behavioral pattern, based on data]

### What SHOULD BE (应然)
[User's stated aspiration or preference]

### Gap (差距)
[Description of the gap between reality and aspiration]

### Evidence (证据)
- [date] [decision/behavior] — [description]

### Challenges (矛盾)
- [date] [contradicting behavior] — [description]

---

## Entry Lifecycle

```
1. 🌱 Candidate — DREAM or Remonstrator proposes
2. ✅ Confirmed — User approves (may edit wording)
3. 📈 Strengthened — More evidence accumulates (confidence rises)
4. ⚠️ Challenged — Contradicting behaviors detected
5. 🔄 Evolved — User updates based on new evidence or DREAM suggestion
6. 🗄️ Retired — User explicitly removes (moved to archive)
```

---

## Confidence Calculation

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

Confidence determines how much influence a SOUL entry has on the system:

| Confidence | Condition | System Behavior |
|------------|-----------|----------------|
| < 0.3 | Newly written, few data points | Only Remonstrator references |
| 0.3 – 0.6 | Moderate evidence | Remonstrator + Chancellery reference |
| 0.6 – 0.8 | Strong evidence | + Secretariat references |
| > 0.8 | Deeply validated, low contradiction | Full system reference (including Prime Minister) |

Confidence is auto-calculated — the user does not manage it.

---

## Dimensions

SOUL entries are organized by dimension. Common dimensions include:

- **Risk attitude** — conservative ↔ aggressive
- **Decision style** — data-driven ↔ intuitive
- **Priority** — family ↔ career ↔ freedom ↔ security ↔ growth
- **Communication style** — direct ↔ diplomatic
- **Conflict handling** — confrontational ↔ avoidant
- **Time orientation** — present-focused ↔ future-focused
- **Red lines** — absolute boundaries (things the user will never do)
- **Core beliefs** — fundamental worldview assumptions

Users may define their own dimensions. The system does not impose categories.

---

## Four Sources

| Source | How | Example |
|--------|-----|---------|
| **DREAM** | During dreaming, discovers patterns from 3-day behavior data | "4 of 5 recent decisions prioritized control over profit" |
| **Remonstrator** | After workflow, observes repeated value signals | "You always ask about family impact first" |
| **Hanlin Academy** | During deep dialogue, user reveals values through conversation | User tells Socrates "stability matters more than adventure" |
| **User** | Direct input at any time | "Remember: I never compromise on X" |

---

## How Each Role Uses SOUL.md

All roles check if SOUL.md exists before referencing it. If it does not exist or is empty, the role operates normally without SOUL input.

| Role | What they read | How they use it |
|------|---------------|-----------------|
| **Prime Minister** | Preferences, red lines | Sharper intent clarification — asks about dimensions the user cares about even if not mentioned |
| **Secretariat** | Value priorities (confidence ≥ 0.6) | Auto-adds relevant dimensions to planning if the user didn't mention them |
| **Chancellery** | What IS vs What SHOULD BE gap (confidence ≥ 0.3) | Value consistency check — flags when a decision contradicts a stated aspiration |
| **Remonstrator** | All entries, evidence & challenge counts | Behavioral audit — reinforces or challenges SOUL entries, proposes updates |
| **Hanlin Academy** | Worldview, unresolved contradictions | Recommends thinkers who address the user's specific tensions |
| **DREAM** | All entries (full read/write proposals) | Discovers new candidates, updates evidence/challenge counts, proposes evolution |

---

## SOUL.md in the Second-Brain

SOUL.md lives at the root of the second-brain directory:

```
second-brain/
├── SOUL.md              ← personality archive
├── user-patterns.md     ← behavioral patterns (different: what you DO)
├── _meta/
├── projects/
├── areas/
└── ...
```

**SOUL.md vs user-patterns.md**:
- `user-patterns.md` records **what you do** — behavioral patterns observed by the Remonstrator
- `SOUL.md` records **who you are** — values, beliefs, and aspirations confirmed by you
- One is descriptive (patterns), the other is identity (soul)
- They feed each other: patterns reveal values, values contextualize patterns
