# SOUL Specification

SOUL.md is the user's personality archive — a living document that records who the user is, what they value, and how they think. It lives in the second-brain root directory.

## Principles

1. **Grows from zero** — SOUL.md starts empty. No initialization required.
2. **Evidence-based** — Every entry links to decisions/behaviors that support it.
3. **Auto-written under strict criteria** — ADVISOR auto-updates existing dimensions after every decision. New dimensions auto-write at low initial confidence (0.3) when ≥2 evidence points accumulate. Users nudge post-hoc: edit freely, delete dimensions, or fill in the "What SHOULD BE" field when ready.
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
source: dream             # dream / advisor / strategist / user
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
1. 🌱 Candidate — DREAM or ADVISOR proposes
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
| < 0.3 | Newly written, few data points | Only ADVISOR references |
| 0.3 – 0.6 | Moderate evidence | ADVISOR + REVIEWER reference |
| 0.6 – 0.8 | Strong evidence | + PLANNER references |
| > 0.8 | Deeply validated, low contradiction | Full system reference (including ROUTER) |

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
| **ADVISOR** | After workflow, observes repeated value signals | "You always ask about family impact first" |
| **STRATEGIST** | During deep dialogue, user reveals values through conversation | User tells Socrates "stability matters more than adventure" |
| **User** | Direct input at any time | "Remember: I never compromise on X" |

---

## How Each Role Uses SOUL.md

All roles check if SOUL.md exists before referencing it. If it does not exist or is empty, the role operates normally without SOUL input.

| Role | What they read | How they use it |
|------|---------------|-----------------|
| **ROUTER** | Preferences, red lines | Sharper intent clarification — asks about dimensions the user cares about even if not mentioned |
| **PLANNER** | Value priorities (confidence ≥ 0.6) | Auto-adds relevant dimensions to planning if the user didn't mention them |
| **REVIEWER** | What IS vs What SHOULD BE gap (confidence ≥ 0.3) | Value consistency check — flags when a decision contradicts a stated aspiration |
| **ADVISOR** | All entries, evidence & challenge counts | Behavioral audit — reinforces or challenges SOUL entries, proposes updates |
| **STRATEGIST** | Worldview, unresolved contradictions | Recommends thinkers who address the user's specific tensions |
| **DREAM** | All entries (full read/write proposals) | Discovers new candidates, updates evidence/challenge counts, proposes evolution |

---

## First-Time Initialization

When SOUL.md does not exist:

1. The system operates normally — all roles skip SOUL references
2. At the first Adjourn Court, DREAM's N3 stage scans available data:
   a. `user-patterns.md` (if exists) — behavioral patterns → propose as SOUL candidates
   b. Recent decisions — value signals → propose as SOUL candidates
3. Next Start Court presents candidates: "🌱 SOUL.md doesn't exist yet. Based on your patterns, here are proposed entries:"
4. User confirms → create SOUL.md with confirmed entries
5. If no data available → skip, wait for more sessions to accumulate evidence

SOUL.md is never pre-populated with assumptions. It grows only from observed evidence.

### Bootstrapping from user-patterns.md

If `user-patterns.md` exists but SOUL.md does not, DREAM can propose initial SOUL entries by reading patterns:
- Behavioral patterns → propose as "What IS" (实然)
- Leave "What SHOULD BE" blank for user to fill
- Initial confidence starts low (evidence_count: 1, challenges: 0 → confidence: 1.0 but flagged as 🌱 single-source)

---

## Auto-Write Mechanism (v1.6.2)

SOUL dimensions are auto-created and auto-updated by ADVISOR during every decision workflow. Users nudge the system by editing/deleting, not by pre-approving.

### Auto-Create Criteria

ADVISOR creates a new SOUL dimension when:
1. The observation is about identity/values/principles (not behavior patterns)
2. There are ≥2 decisions as evidence (current session or within last 30 days)
3. No existing dimension covers it

Initial values:
- `confidence: 0.3`
- `What IS`: auto-filled from evidence
- `What SHOULD BE`: EMPTY (user fills)

### Auto-Update (every decision)

After every Three Departments workflow, ADVISOR:
- For each existing dimension (confidence ≥ 0.3): evidence_count +1 if supported, challenges +1 if contradicted
- Recalculates `confidence = evidence_count / (evidence_count + 2 × challenges)`

### User Nudges

Users don't pre-approve, but can:
- Edit `What SHOULD BE` field (aspiration — system never fills this)
- Delete a dimension (removes entry)
- Say "undo recent SOUL" → ADVISOR rolls back latest additions
- Edit confidence manually to override

### Why Auto vs Confirm

Previous version asked for confirmation. v1.6.2 removes this because:
- Users didn't see SOUL "working" — candidates appeared once a week
- Confidence grew too slowly (1 evidence per session)
- Pattern detection delayed by user review overhead

Post-hoc nudges + real-time evolution gives the user a LIVING SOUL archive.

---

## Snapshot Mechanism

SOUL snapshots are small immutable metadata dumps written at session close. RETROSPECTIVE Mode 0 reads the two most recent snapshots to compute trend arrows (↗↘→🌟⚠️💤❗) in the SOUL Health Report.

**Authoritative source**: `references/snapshot-spec.md`. That spec defines:

- File format, YAML schema (`captured_at`, `snapshot_id`, `session_id`, `previous_snapshot`, `dimensions[]`)
- 4-tier mapping derived at capture time using half-open intervals `[a, b)` (boundary values belong to the upper tier): `core` (`[0.7, 1.0]`) / `secondary` (`[0.3, 0.7)`) / `emerging` (`[0.2, 0.3)`) / `dormant` (`[0.0, 0.2)`, excluded from snapshot)
- Delta rules for trend arrows and tier-transition badges
- Archive policy (active 30d → archive 30-90d → delete >90d)
- Invariants (one snapshot per session, metadata only, immutable after write, real timestamps)

**Write trigger**: `archiver` Phase 2 Step 3, after concept extraction / Hebbian update and before housekeeping.

**Read trigger**: RETROSPECTIVE Mode 0 during Start Session briefing.

This SOUL spec deliberately does not duplicate the schema — one authoritative source prevents drift. If a snapshot field changes, it changes in snapshot-spec and the archiver agent file.

### Why Snapshots (vs alternatives)

- Single-file frontmatter (`last_session_evidence`): rejected — no long-term trend data
- Compare-within-session only: rejected — loses cross-session progression
- Full snapshot: chosen — small files (SOUL is tiny), full history, simple reader logic

---

## Health Report Format (every session briefing)

Every Start Session includes a SOUL Health Report in a fixed, prominent position in the briefing (not optional).

### Format

```
🔮 SOUL Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Current Profile:
   Active dimensions (confidence > 0.5): N
   · [Dimension A] 0.8 🟢 ↗ (+2 evidence since last session)
   · [Dimension B] 0.6 🟢 → (no change)
   · [Dimension C] 0.5 🟡 ↘ (+1 challenge — last decision contradicted)

🌱 New dimensions (auto-detected since last session):
   · [Dimension D] 0.3 (based on 2 decisions)
     What IS: [system observation]
     What SHOULD BE: [awaiting your input — fill when you have clarity]

⚠️ Conflict warnings:
   · [Dimension X] last 3 decisions all challenged → needs reflection or revision

💤 Dormant dimensions (30+ days no activation):
   · [Dimension Y] — no related decisions recently

📈 This period's trajectory:
   Net evidence +N, net challenges +M, new dimensions +K
```

### Display Rules

- ALWAYS appears in Mode 0 briefing (Start Session), regardless of SOUL size
- If SOUL is empty → show "SOUL is still gathering initial observations. After a few decisions, your first dimensions will emerge."
- Should be near the TOP of the briefing, before STATUS/project details
- RETROSPECTIVE agent is responsible for generating this from current SOUL.md state

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
- `user-patterns.md` records **what you do** — behavioral patterns observed by the ADVISOR
- `SOUL.md` records **who you are** — values, beliefs, and aspirations confirmed by you
- One is descriptive (patterns), the other is identity (soul)
- They feed each other: patterns reveal values, values contextualize patterns

---

## Tiered Reference by Confidence (v1.6.2)

REVIEWER references SOUL in every decision (HARD RULE). To prevent noise when SOUL has many dimensions, a 4-tier strategy applies. Tier names are aligned with `references/snapshot-spec.md` (§YAML Frontmatter Schema `tier` field) so one vocabulary carries through both the live reference model and the historical snapshot format.

All confidence bands use half-open intervals `[a, b)` — the lower bound is inclusive and the upper bound is exclusive. Boundary values always belong to the **upper** tier (e.g., confidence exactly 0.3 is `secondary`, not `emerging`; confidence exactly 0.7 is `core`, not `secondary`).

| Tier | Confidence | Reference strategy | Limit |
|------|-----------|-------------------|-------|
| **core** · Core Identity | `[0.7, 1.0]` | Reference ALL | No upper limit |
| **secondary** · Active Values | `[0.3, 0.7)` | Reference top N semantically relevant | Max 3 |
| **emerging** · Emerging | `[0.2, 0.3)` | Count only, don't surface (ADVISOR tracks in Delta) | 0 |
| **dormant** | `[0.0, 0.2)` | Retained in history (SOUL.md) but excluded from active reference and from snapshots | — |

Legacy references to "Tier 1 / 2 / 3" in earlier specs map to `core / secondary / emerging` respectively; `dormant` is new in v1.7 and reuses snapshot-spec's name for dimensions below the active floor.

### Relevance Judgment (secondary tier)

REVIEWER reads decision Subject + Summary + PLANNER proposal, then for each `secondary` dimension rates:
- **strong match** (directly relevant) → priority include
- **weak match** (indirectly relevant) → sort by confidence, take top
- **no match** → skip

REVIEWER report must list ALL `secondary` dimensions evaluated + inclusion reason → AUDITOR reviews quality.

### Special States

- Decision challenges a `core` dimension → REVIEWER adds ⚠️ SOUL CONFLICT warning at top of Summary Report (semi-veto signal)
- Dimension crossed 0.7 upward since last snapshot → 🌟 "newly promoted to core"
- Dimension crossed 0.7 downward → ⚠️ "demoted from core"
- All dimensions in `emerging` or `dormant` → REVIEWER outputs "SOUL tracking, not yet referencing"
- >20 active dimensions → `core` no upper limit but compress: top 5 detailed, rest listed by name
