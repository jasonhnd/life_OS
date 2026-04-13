# Wiki Specification

Wiki is the system's knowledge archive — a living collection of reusable conclusions about the world. It lives in the `wiki/` directory of the second-brain.

## Positioning

| Storage | What it records | Example |
|---------|----------------|---------|
| `decisions/` | What you decided (specific, timestamped) | "2026-04-01: decided to use trust structure" |
| `user-patterns.md` | What you do (behavioral patterns) | "Tends to avoid financial dimensions" |
| `SOUL.md` | Who you are (values, personality) | "Risk appetite: medium-high" |
| `wiki/` | What you know (reusable conclusions) | "NPO lending in Japan has no 貸金業法 exemption" |

SOUL manages the person. Wiki manages knowledge. They must not be mixed.

---

## Principles

1. **Grows from zero** — wiki/ starts empty. No initialization required.
2. **Evidence-based** — Every entry links to the decisions/experiences that support it.
3. **User-confirmed** — System proposes candidates, user confirms. Nothing is auto-written.
4. **Title = Conclusion** — The title of every entry must be the conclusion itself, not the topic.
5. **One conclusion per file** — No multi-topic compilations.

---

## Entry Format

Each wiki entry is a standalone markdown file:

```yaml
---
domain: "[domain name]"       # finance / startup / health / legal / tech / project-name...
topic: "[short identifier]"
confidence: 0.0               # 0-1, auto-calculated
evidence_count: 0             # supporting decisions/experiences
challenges: 0                 # contradicting experiences
source: dream                 # dream / session / user
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
---
```

### Conclusion
[One sentence — the reusable takeaway]

### Reasoning
[Evidence and logic supporting this conclusion]

### Applicable When
[In what scenarios should you recall this entry]

### Source
[Which decision, session, or experience produced this knowledge]

---

## Title Convention

Titles must be conclusions, not topics:

- ✅ "NPO lending in Japan has no 貸金業法 exemption"
- ❌ "NPO 貸金業法 research"
- ✅ "MVP validates demand, not product quality"
- ❌ "MVP methodology notes"
- ✅ "16:8 intermittent fasting works well for me"
- ❌ "Intermittent fasting research"

Opening the file tells you the answer immediately — no need to read the full text.

---

## File Path Convention

```
wiki/{domain}/{topic}.md
```

Examples:
- `wiki/finance/lending-law-npo.md`
- `wiki/startup/mvp-validation.md`
- `wiki/health/intermittent-fasting.md`
- `wiki/gcsb/biz-plan-versions.md`

---

## Confidence Calculation

Same formula as SOUL.md:

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| Confidence | Meaning | System Behavior |
|------------|---------|-----------------|
| < 0.3 | Tentative, few data points | Visible in INDEX but not referenced during routing |
| 0.3 – 0.6 | Moderate evidence | Chancellery references during consistency check |
| 0.6 – 0.8 | Well-established | Prime Minister informs user of existing knowledge |
| > 0.8 | Deeply validated | Full system reference — can accelerate decision routing |

---

## Entry Lifecycle

```
1. 🌱 Candidate — DREAM proposes during N3 stage, or extracted during a session
2. ✅ Confirmed — User approves during Start Court (may edit wording)
3. 📈 Strengthened — More evidence accumulates (evidence_count rises, confidence increases)
4. ⚠️ Challenged — Contradicting experience detected (challenges increase, confidence drops)
5. 🔄 Revised — User updates the conclusion based on new evidence
6. 🗄️ Retired — Moved to wiki/_archive/ (low confidence + no activity for 90+ days)
```

---

## Wiki INDEX

`wiki/INDEX.md` is a compiled summary of all wiki entries. The Morning Court Official compiles it during every Start Court from the actual wiki/ files.

### Format

```markdown
# Wiki Index
compiled: YYYY-MM-DD

## Finance
- NPO lending has no 貸金業法 exemption (0.95) → wiki/finance/lending-law-npo.md
- NPO tax deduction conditions (0.82) → wiki/finance/npo-tax-deduction.md

## Startup
- MVP validates demand, not product (0.88) → wiki/startup/mvp-validation.md
- Business plan: internal vs external versions differ fundamentally (0.72) → wiki/gcsb/biz-plan-versions.md

## Health
- 16:8 intermittent fasting works for me (0.80) → wiki/health/intermittent-fasting.md
```

Each line ≤ 80 characters. The entire INDEX is typically 20-100 lines — very cheap to load.

**INDEX.md is a compiled artifact** — never hand-edit it. It is regenerated from wiki/ files.

---

## Four Sources

| Source | How | When |
|--------|-----|------|
| **DREAM** | N3 stage discovers reusable conclusions from 3-day activity | After every Adjourn Court |
| **Session** | During a Three Departments workflow, a ministry produces a reusable finding | Journal entries marked `wiki_candidate: true` |
| **User** | Direct input at any time | "Remember this fact: X" |

---

## Wiki Candidate Format

When DREAM discovers knowledge worth recording:

```
📚 Wiki Candidate:
- Domain: [domain name]
- Topic: [short identifier]
- Conclusion: [one sentence — the reusable takeaway]
- Evidence:
  - [date] [decision/behavior] — [description]
  - [date] [decision/behavior] — [description]
- Applicable when: [in what scenarios to recall this]
```

The user confirms, edits, or rejects during the next Start Court.

---

## How Each Role Uses Wiki

All roles check if wiki/INDEX.md exists before referencing it. If it does not exist or is empty, the role operates normally without wiki input.

| Role | What they read | How they use it |
|------|---------------|-----------------|
| **Prime Minister** | wiki/INDEX.md (full index) | Scans for domain match — if high-confidence entries exist, informs user "we already know X" and offers to skip redundant research |
| **Dept. of State Affairs** | Relevant wiki entries (passed by Prime Minister) | Includes in dispatch context as "known premises — start from here" |
| **Six Ministries** | Wiki entries in their dispatch context | Start analysis from established conclusions, not from zero |
| **Chancellery** | wiki/INDEX.md | Consistency check — flags when new conclusions contradict existing high-confidence wiki entries |
| **Censorate** | wiki/ directory (during patrol) | Wiki health audit — stale entries, contradictions, knowledge gaps |
| **DREAM** | wiki/INDEX.md + wiki/ entries | N3: propose new candidates + update evidence/challenges for existing entries. REM: cross-domain connections using wiki as material |
| **Morning Court Official** | wiki/ directory | Compiles INDEX.md at Start Court, presents wiki candidates for user confirmation |

---

## Wiki in the Second-Brain

```
second-brain/
├── SOUL.md              ← who you are (personality)
├── user-patterns.md     ← what you do (behavior)
├── wiki/                ← what you know (knowledge)
│   ├── INDEX.md         ← compiled summary (auto-generated)
│   ├── finance/
│   │   ├── lending-law-npo.md
│   │   └── npo-tax-deduction.md
│   ├── startup/
│   │   └── mvp-validation.md
│   ├── health/
│   │   └── intermittent-fasting.md
│   └── _archive/        ← retired entries
├── inbox/
├── _meta/
├── projects/
├── areas/
└── archive/
```

---

## First-Time Initialization

When the Morning Court Official detects that wiki/ is empty or has no INDEX.md:

1. Report in briefing: "📚 Wiki is not yet initialized. Would you like to set it up?"
2. If user agrees:
   a. Scan `decisions/` and `_meta/journal/` for extractable conclusions (same logic as DREAM N3 Q2)
   b. Present top 5 candidates as wiki entries for user confirmation
   c. For each confirmed entry: create `wiki/{domain}/{topic}.md` with proper front matter
   d. Compile `wiki/INDEX.md`
3. If user declines → skip, remind next Start Court

This only triggers once. After INDEX.md exists, normal wiki flow takes over.

---

## Legacy Migration

When wiki/ contains files that don't match the spec format (no front matter, no domain subdirectory, title ≠ conclusion):

1. Report in briefing: "📚 Found N legacy wiki files not matching current spec. Migrate?"
2. If user agrees:
   a. Read each legacy file
   b. Extract 1-3 reusable conclusions per file → propose as new wiki entries
   c. User confirms each → write to `wiki/{domain}/{topic}.md`
   d. Move original file to `wiki/_archive/` (preserve, don't delete)
   e. Recompile INDEX.md
3. If user declines → leave as-is, don't block normal flow

Legacy files in wiki/ root (without front matter) are ignored by INDEX.md compilation.

---

## Constraints

- **User confirms all writes** — wiki entries are never auto-created
- **INDEX.md is compiled, not authored** — regenerated from wiki/ files at every Start Court
- **One conclusion per file** — do not create "topic compilation" files
- **Title = conclusion** — opening the file gives you the answer
- **No cross-references within wiki** — each entry is self-contained
- **Conciseness** — a wiki entry should be 10-30 lines, not a research paper
