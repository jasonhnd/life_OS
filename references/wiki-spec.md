# Wiki Specification

Wiki is the system's knowledge archive — a living collection of reusable conclusions about the world. It lives in the `wiki/` directory of the second-brain.

## Positioning

| Storage | What it records | Example |
|---------|----------------|---------|
| `decisions/` | What you decided (specific, timestamped) | "2026-04-01: decided to use trust structure" |
| `user-patterns.md` | What you do (behavioral patterns) | "Tends to avoid financial dimensions" |
| `SOUL.md` | Who you are (values, personality) | "Risk appetite: medium-high" |
| `wiki/` | What you know — declarative knowledge | "NPO lending in Japan has no 貸金業法 exemption" |
| `_meta/concepts/` | Synaptic graph — how ideas connect (v1.7) | "company-a-holding" node with weighted edges to related concepts |
| `_meta/methods/` | Procedural memory — reusable workflows (v1.7) | "Refine documents in 5 escalating quality rounds" |

Each layer answers a different question. SOUL answers "who you are". Wiki answers "what you know about the world" (declarative). Concepts answer "how ideas connect" (associative). Methods answer "how you work best" (procedural). The four layers must not be mixed — archiver routes candidates to the right layer based on what the candidate is, not based on surface form.

**Not wiki material** (goes elsewhere):
- Identity / values / personal preferences → `SOUL.md`
- Behavioral patterns → `user-patterns.md`
- Procedural workflows → `_meta/methods/`
- Concept-level associations (who connects to whom) → `_meta/concepts/`

---

## Principles

1. **Grows from zero** — wiki/ starts empty. No initialization required.
2. **Evidence-based** — Every entry links to the decisions/experiences that support it.
3. **Auto-written under strict criteria** — Wiki entries are auto-created by archiver and DREAM when strict criteria are met; users nudge by deletion (delete file = retire; say "undo recent wiki" = rollback).
4. **Title = Conclusion** — The title of every entry must be the conclusion itself, not the topic.
5. **One conclusion per file** — No multi-topic compilations.

---

## Auto-Write Criteria (6 rules)

Every candidate conclusion must pass ALL 6 criteria before being auto-written. One failure → discard the candidate, do not write a low-confidence entry.

1. **Cross-project reusable** — The conclusion is useful in projects/domains beyond the session where it was observed.
2. **About the world, not about you** — Facts, rules, or methods. NOT values or personal preferences (those belong in SOUL). NOT behavioral patterns (those belong in user-patterns.md).
3. **Zero personal privacy** — No names, amounts, account numbers, IDs, specific companies, family/friend info, or traceable date+location combinations. If the conclusion requires these to make sense → it isn't wiki material, skip it.
4. **Factual or methodological** — Describes "what happened" or "how to do X". Not feelings or opinions.
5. **Multiple evidence points (≥2 independent)** — At least 2 cases, data points, decisions, or references. Single observations get discarded (they belong in a journal, not the wiki).
6. **No contradiction with existing wiki** — If the new conclusion contradicts an existing entry → increment `challenges: +1` on that entry, do NOT create a new competing entry.

**Initial confidence** (once a candidate passes all 6):
- 3+ independent evidence points → `confidence: 0.5`
- Exactly 2 evidence points → `confidence: 0.3`
- 1 evidence or below → DISCARDED (fails criterion 5)

**Privacy Filter** — applied before every write:
- Strip names (unless public figures directly relevant to the conclusion)
- Strip specific amounts, account numbers, ID numbers
- Strip specific company names (unless it's a public case study)
- Strip family/friend references
- Strip traceable date+location combinations
- If stripping these leaves the conclusion meaningless → discard (it wasn't really reusable, it was a personal note dressed up as knowledge)

**User-facing evidence paste** — every evaluated candidate must be visible in the ARCHIVER adjourn report, not only used internally. Passing candidates must show `Criteria check: 6/6 passed`; discarded candidates must show `Criteria check: X/6 -> discarded with reason: [reason]`. Every candidate must show `Privacy filter: stripped <items>`; use `Privacy filter: stripped nothing` if nothing was removed.

---

## User Nudges (post-write)

Users don't pre-approve wiki entries. They nudge the system post-hoc:

- Delete `wiki/{domain}/{topic}.md` → retire the entry
- Say "undo recent wiki" in a session → archiver (next invocation) rolls back the most recent auto-writes
- Edit confidence manually to reject (set to 0 or below 0.3) → entry stays but not referenced

---

## Entry Format

Each wiki entry is a standalone markdown file:

```yaml
---
domain: "[domain name]"       # finance / startup / personal / technical / method / relationship / health / legal / project-name...
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
- `wiki/startup/biz-plan-versions.md`

---

## Confidence Calculation

Same formula as SOUL.md:

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| Confidence | Meaning | System Behavior |
|------------|---------|-----------------|
| < 0.3 | Tentative, few data points | Visible in INDEX but not referenced during routing |
| 0.3 – 0.6 | Moderate evidence | REVIEWER references during consistency check |
| 0.6 – 0.8 | Well-established | ROUTER informs user of existing knowledge |
| > 0.8 | Deeply validated | Full system reference — can accelerate decision routing |

---

## Entry Lifecycle

```
1. ✅ Auto-written — archiver (Phase 2) or DREAM (N3) passes all 6 criteria → writes directly to wiki/{domain}/{topic}.md
2. 📈 Strengthened — More evidence accumulates (evidence_count rises, confidence increases)
3. ⚠️ Challenged — Contradicting experience detected (challenges increase, confidence drops)
4. 🔄 Revised — User updates the conclusion based on new evidence
5. 🗑️ Nudged out — User deletes the file manually (= retire) or says "undo recent wiki" in a session (archiver rolls back most recent auto-writes)
6. 🗄️ Retired — Moved to wiki/_archive/ (low confidence + no activity for 90+ days, or user-deleted)
```

---

## Wiki INDEX

`wiki/INDEX.md` is a compiled summary of all wiki entries. The RETROSPECTIVE compiles it during every Start Court from the actual wiki/ files.

### Format

```markdown
# Wiki Index
compiled: YYYY-MM-DD

## Finance
- NPO lending has no 貸金業法 exemption (0.95) → wiki/finance/lending-law-npo.md
- NPO tax deduction conditions (0.82) → wiki/finance/npo-tax-deduction.md

## Startup
- MVP validates demand, not product (0.88) → wiki/startup/mvp-validation.md
- Business plan: internal vs external versions differ fundamentally (0.72) → wiki/startup/biz-plan-versions.md

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
| **Session** | During a Draft-Review-Execute workflow, a ministry produces a reusable finding | Journal entries marked `wiki_candidate: true` |
| **User** | Direct input at any time | "Remember this fact: X" |

---

## Wiki Candidate Format

When archiver or DREAM discovers knowledge worth recording, every evaluated candidate is pasted to the user in the adjourn report. If all 6 Auto-Write Criteria pass, the entry is written directly (no candidate confirmation). This structure is a user-facing contract, not an internal-only scratchpad:

```
📚 Wiki Auto-Write Evidence:
- Domain: [domain name]
- Topic: [short identifier]
- Conclusion: [one sentence — the reusable takeaway]
- Evidence:
  - [date] [decision/behavior] — [description]
  - [date] [decision/behavior] — [description]
- Applicable when: [in what scenarios to recall this]
- Criteria check: 6/6 passed
- Privacy filter: stripped <items>
```

Discarded candidates use the same structure, but the final lines MUST be:

```
- Criteria check: X/6 -> discarded with reason: [which criteria failed and why]
- Privacy filter: stripped <items>
```

If nothing was stripped, write `Privacy filter: stripped nothing`. Do not omit the privacy line.

If all 6 criteria pass → write directly to `wiki/{domain}/{topic}.md`. Otherwise → discard with reason logged in Completion Checklist.

---

## How Each Role Uses Wiki

All roles check if wiki/INDEX.md exists before referencing it. If it does not exist or is empty, the role operates normally without wiki input.

| Role | What they read | How they use it |
|------|---------------|-----------------|
| **ROUTER** | wiki/INDEX.md (full index) | Scans for domain match — if high-confidence entries exist, informs user "we already know X" and offers to skip redundant research |
| **DISPATCHER** | Relevant wiki entries (passed by ROUTER) | Includes in dispatch context as "known premises — start from here" |
| **Six Domains** | Wiki entries in their dispatch context | Start analysis from established conclusions, not from zero |
| **REVIEWER** | wiki/INDEX.md | Consistency check — flags when new conclusions contradict existing high-confidence wiki entries |
| **AUDITOR** | wiki/ directory (during patrol) | Wiki health audit — stale entries, contradictions, knowledge gaps |
| **DREAM** | wiki/INDEX.md + wiki/ entries | N3: propose new candidates + update evidence/challenges for existing entries. REM: cross-domain connections using wiki as material |
| **RETROSPECTIVE** | wiki/ directory | Compiles INDEX.md at Start Court. Surfaces "undo recent wiki" flags when user asked for rollback in previous session. |

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

When the RETROSPECTIVE detects that wiki/ is empty or has no INDEX.md:

1. Report in briefing: "📚 Wiki is not yet initialized. Would you like to bootstrap from existing decisions?"
2. If user agrees:
   a. Scan `decisions/` and `_meta/journal/` for extractable conclusions (same logic as DREAM N3 Q2)
   b. Apply the 6 Auto-Write Criteria + Privacy Filter to each candidate
   c. Auto-write all passing candidates to `wiki/{domain}/{topic}.md` with proper front matter
   d. Compile `wiki/INDEX.md`
   e. Report: "Auto-wrote N entries, discarded M (reasons: ...). Delete any file you disagree with."
3. If user declines → skip, remind next Start Court

This only triggers once. After INDEX.md exists, normal wiki flow takes over.

---

## Legacy Migration

When wiki/ contains files that don't match the spec format (no front matter, no domain subdirectory, title ≠ conclusion):

1. Report in briefing: "📚 Found N legacy wiki files not matching current spec. Migrate?"
2. If user agrees:
   a. Read each legacy file
   b. Extract 1-3 reusable conclusions per file
   c. Apply the 6 Auto-Write Criteria + Privacy Filter to each extracted conclusion
   d. Auto-write passing conclusions to `wiki/{domain}/{topic}.md`
   e. Move original file to `wiki/_archive/` (preserve, don't delete)
   f. Recompile INDEX.md
   g. Report: "Migrated N entries, discarded M (reasons: ...). Delete any file you disagree with."
3. If user declines → leave as-is, don't block normal flow

Legacy files in wiki/ root (without front matter) are ignored by INDEX.md compilation.

---

## Constraints

- **Auto-written only when all 6 criteria pass** — see Auto-Write Criteria section. Anything less → discard, don't write a low-confidence entry
- **Privacy filter applied before every write** — names, amounts, IDs, specific companies, family/friend references, traceable date+location combos get stripped; if stripping makes the conclusion meaningless → discard
- **Users nudge post-hoc, not pre-approve** — delete the file to retire; say "undo recent wiki" to rollback; set confidence below 0.3 to suppress without deletion
- **INDEX.md is compiled, not authored** — regenerated from wiki/ files at every Start Court
- **One conclusion per file** — do not create "topic compilation" files
- **Title = conclusion** — opening the file gives you the answer
- ~~**No cross-references within wiki** — each entry is self-contained~~ — **SUPERSEDED by R-1.8.0-013**: wiki entries MAY use Obsidian `[[wikilinks]]` to other wiki entries, concepts, people, comparisons. See "Page Taxonomy + Wikilink Convention" section below.
- **Conciseness** — a wiki entry should be 10-30 lines, not a research paper

---

## Page Taxonomy + Wikilink Convention (v1.8.0 R-1.8.0-013)

Borrowed from llm_wiki — a clearer split between page types so archiver knows where to route, hippocampus can score type affinity, and Obsidian graph view shows distinct colors.

### Taxonomy

| Type | Path | What goes here | Spec |
|---|---|---|---|
| `wiki` | `wiki/<slug>.md` | General reusable knowledge / conclusions / 50-100 char facts | this file |
| `concept` | `_meta/concepts/<domain>/<id>.md` | Theories, methods, frameworks (LLM-grounded vocabulary) | `references/concept-spec.md` |
| `people` | `_meta/people/<id>.md` | Persons in user's life — relationships, history, patterns | `references/people-spec.md` |
| `comparison` | `_meta/comparisons/<id>.md` | "X vs Y" decision artifacts with options/criteria/outcome | `references/comparison-spec.md` |
| `method` | `_meta/methods/<id>.md` | Reusable procedures / workflows | `references/method-library-spec.md` |
| `session` | `_meta/sessions/<sid>.md` | Per-session summary | `references/session-index-spec.md` |
| `snapshot` | `_meta/snapshots/soul/<date>.md` | SOUL trajectory snapshot | `references/snapshot-spec.md` |

### Routing rules (archiver Phase 2 candidates)

- Person (named individual user interacts with) → `_meta/people/`
- "X vs Y" decision with options + criteria + decision → `_meta/comparisons/`
- Reusable theory / method / framework → `_meta/concepts/<domain>/`
- Procedure user can re-execute → `_meta/methods/`
- General fact / conclusion that doesn't fit above → `wiki/`

### Wikilink convention (HARD RULE for new writes)

All cross-references in **body text** use Obsidian `[[]]` syntax:

```
- [[concept-id]]               → link to concept
- [[wiki-entry-slug]]          → link to wiki entry
- [[person-id]]                → link to person
- [[comparison-id]]            → link to comparison
- [[session-id]]               → link to session summary
- [[concept-id|Display Name]]  → wikilink with display alias
```

Obsidian's `newLinkFormat: shortest` resolves these by filename match across the vault — no full path needed.

**Frontmatter arrays remain YAML** (machine-parseable):

```yaml
concepts_activated: [concept-1, concept-2]   # YAML strings, NOT wikilinks
related: [[[concept-1]], [[wiki-entry-1]]]   # exception: explicit wikilink arrays
```

When a frontmatter field semantically references another page (`source_session`, `superseded_by`, `related`, `concepts_linked` in people/comparison pages), use wikilink syntax for Obsidian navigability.

### Existing content migration

User runs `scripts/prompts/migrate-to-wikilinks.md` to migrate old wiki entries (plain text references) to wikilink format. The prompt reads each wiki/ entry, identifies references to other pages, rewrites with `[[]]`, preserves semantics. Decision: `4，全，完整` — full migration is the chosen approach.
