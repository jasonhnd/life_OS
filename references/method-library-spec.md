---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# Method Library Specification

Method Library is Life OS's procedural memory — the "how you work best" layer. It lives in the `_meta/methods/` directory of the second-brain and stores reusable workflows that recur across sessions.

## 1. Purpose

Life OS maintains three distinct memory layers:

| Layer | Question it answers | Example |
|-------|--------------------|---------|
| Wiki | "What is true about the world?" | "NPO lending in Japan has no 貸金業法 exemption" |
| SOUL | "Who are you?" | "Risk appetite: medium-high" |
| Methods | "How do you work best?" | "Refine documents in 5 escalating quality rounds: structure → content → precision → polish → release audit" |

Methods are **reusable workflows** — procedural patterns that apply across decisions. They sit adjacent to wiki (both are cross-project knowledge) but differ in shape: wiki answers factual questions, methods describe sequences of action.

Inspired by Hermes Skills (see `devdocs/research/2026-04-19-hermes-analysis.md`) but adapted for Life OS's decision-engine context. Hermes skills encode tool-use procedures; Life OS methods encode decision-making procedures.

---

## 2. What Qualifies as a Method

**Yes**:
- "Iterative document refinement in 5 escalating quality rounds"
- "Startup fundraising timing: 12 months runway is the trigger"
- "Delegating to team: responsibility × authority matrix"
- "Negotiating rate increases: anchor with data, propose three options"

**No** (these go elsewhere):
- Specific facts → `wiki/`
- Personal preferences or values → `SOUL.md`
- Project-specific plans → `projects/{name}/`
- One-off tips → `inbox/` or `user-patterns.md`

**Criterion**: a method is a reusable workflow that can be applied across different decisions in different projects. If the pattern only makes sense inside one project, it belongs under that project, not in the method library.

---

## 3. File Location

Per user decision #11 (method library introduced in v1.7):

```
_meta/methods/
├── INDEX.md                        # compiled summary (auto-generated)
├── _tentative/                     # candidate methods awaiting user confirmation
│   └── {method_id}.md
├── _archive/                       # dormant methods (12+ months unused)
│   └── {method_id}.md
└── {domain}/
    └── {method_id}.md
```

Methods are NOT under `wiki/`. Separate concept, separate root. The parallel to `wiki/` is deliberate: both are cross-project knowledge, both auto-compiled into an INDEX, both user-nudged post-hoc.

Domain directories mirror the system-wide domain list (aligned with `references/concept-spec.md §Domain partitions` and `references/wiki-spec.md §Positioning`): `finance`, `startup`, `personal`, `technical`, `method`, `relationship`, `health`, `legal`, plus any user-defined domain.

---

## 4. YAML Frontmatter Schema

Every method file begins with this frontmatter block:

```yaml
---
method_id: string                     # lowercase, hyphens, unique (e.g., iterative-document-refinement)
name: string                          # display name (e.g., "Iterative Document Refinement")
description: string                   # one-liner for INDEX
domain: string                        # finance | startup | personal | technical | method | relationship | ...
status: enum                          # tentative | confirmed | canonical
confidence: float                     # 0-1, same formula as SOUL/wiki
times_used: integer                   # increments every session that applies the method
last_used: string                     # ISO 8601 timestamp
applicable_when:
  - condition: string                 # natural language condition
    signal: string                    # concrete signal that triggers this condition
not_applicable_when:
  - condition: string                 # anti-condition where the method fails
source_sessions: [string]             # session_ids that contributed to this method
evidence_count: integer               # sessions where the method worked
challenges: integer                   # sessions where the method failed
related_concepts: [string]            # concept_ids from concept-spec
related_methods: [string]             # method_ids — enables composition (section 16)
---
```

`confidence` is derived by the same formula used by SOUL and wiki:

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

Floor: 0. Ceiling: 1. The formula stays consistent across memory layers so agents don't have to translate between scales.

---

## 5. Body Format

After the frontmatter, every method follows this shape:

```markdown
# Method Name

## Summary
One-paragraph description of what the method does and why it works.

## Steps
1. Step 1 — what to do, why it matters
2. Step 2 — what to do, why it matters
3. ...

## When to Use
- Conditions that indicate this method applies
- Signals to look for in the current subject

## When NOT to Use
- Anti-conditions where the method fails or misleads
- Known counter-cases

## Evolution Log
- 2026-04-15: First observed in 4-round document refinement flow
- 2026-04-19: Confirmed from 5-round flow, added step 5 (release audit)

## Warnings
- Common pitfalls and failure modes

## Related
- [[concept-link]] — concepts referenced or refined by this method
- [[other-method-id]] — related methods (sibling or composed)
```

Length target: 30–80 lines per method. Longer than that usually signals a method that should be split or a method masquerading as a project plan.

---

## 6. Auto-Creation (by archiver)

Method candidates are detected by `archiver` Phase 2 (see `pro/agents/archiver.md`) using the same infrastructure that produces wiki and SOUL candidates.

**Trigger condition**: a repeatable workflow pattern observed in the current session matches an existing method signature OR a net-new pattern that meets the heuristic.

**Heuristic for net-new candidates**:
- 5+ sequential actions in the session's workflow form a coherent procedure
- The same pattern has been observed in ≥2 past sessions (looked up via hippocampus / session index)
- User described it using language like "approach", "pattern", "framework", "process", "流れ", "やり方"

**Anti-heuristic** (disqualifies a candidate):
- Pattern appears in exactly one session with no cross-session echo
- Pattern is specific to one project's context
- Pattern duplicates an existing canonical method

**When a candidate is detected**:

1. Generate a method draft with:
   - `status: tentative`
   - `confidence: 0.3`
   - `times_used: 1`
   - `source_sessions: [current_session_id]`
   - `evidence_count: 1`
2. Check against existing methods (by `method_id` exact match, then by description similarity ≥ 0.7 against INDEX)
3. If duplicate → increment `evidence_count` on the existing method, update `last_used`, write to evolution log — do NOT create a new candidate
4. If new → write to `_meta/methods/_tentative/{method_id}.md`
5. Record in the session's Completion Checklist so RETROSPECTIVE can surface at next Start Session

archiver does not promote candidates past `tentative` on its own. Promotion requires user input (section 7) or evidence accumulation (section 8).

---

## 7. User Confirmation Workflow

At the next Start Session, RETROSPECTIVE includes a method candidate block in the morning briefing:

```
Method candidates detected:
"Iterative Document Refinement" (observed in 2 sessions)
  Summary: 5-round escalating quality process
  (c) Confirm — move to confirmed, start applying
  (r) Reject — delete
  (e) Edit — open for user editing
  (s) Skip — decide later
```

User responses:
- `c` or "confirm X" → move file from `_meta/methods/_tentative/` to `_meta/methods/{domain}/`, flip `status: tentative` → `confirmed`, bump confidence to 0.5 (or 0.6 if already has 3+ source_sessions)
- `r` or "reject X" → delete file
- `e` or "edit X" → print file path, user edits, no state change
- `s` or "skip" → leave in `_tentative/`, surface again in next Start Session

If a candidate sits in `_tentative/` for 5 consecutive Start Sessions with no user response, archiver auto-archives it. Silence ≠ consent, but infinite pending state is worse than letting it go.

---

## 8. Promotion Ladder

Methods move through three maturity tiers. Promotion follows evidence, not time.

| Status | Requirements | Confidence range | System behavior |
|--------|-------------|------------------|-----------------|
| tentative | 1 session observation | 0.3 | Hidden from dispatcher. Lives in `_tentative/`. |
| confirmed | ≥2 sessions + user confirm | 0.5–0.6 | Injected by dispatcher when applicable. |
| canonical | ≥5 uses + confidence ≥ 0.7 | 0.7–1.0 | Full dispatcher injection + may be referenced by name in Summary Reports. |

**Automatic promotion**:
- tentative → confirmed: requires user input (section 7). Never automatic.
- confirmed → canonical: automatic when `times_used ≥ 5` AND `confidence ≥ 0.7` AND no challenges in last 3 uses.

**Demotion**:
- Any method whose confidence drops below 0.3 due to accumulated challenges is flagged for user review, not auto-demoted.
- User can manually set status in the frontmatter at any time.

---

## 9. Use by DISPATCHER

When a Draft-Review-Execute workflow reaches Step 4 (DISPATCHER Dispatch), the dispatcher performs a method lookup:

```
1. Read _meta/methods/INDEX.md
2. For each confirmed/canonical method, evaluate applicable_when conditions against current subject
3. If a method matches → include its full body as "Known Method" in relevant domains' dispatch context
4. Label clearly: "Known Method '{name}' applies — here is the established approach, use it unless the subject contradicts."
```

Example: a session about refining a business plan reaches dispatcher. The `iterative-document-refinement` method matches. DISPATCHER injects its body into the execution domain's brief. The execution domain starts its analysis knowing the user already has a validated 5-round refinement pattern — instead of reinventing an approach, it applies the known method and reports back.

This prevents domain agents from re-deriving workflows the user has already earned through experience.

**Multiple matches**: if 2+ methods apply, DISPATCHER passes all of them with a note: "Multiple known methods apply — use in sequence or as alternatives, domain to judge fit."

**No match**: DISPATCHER proceeds normally — domains derive the approach fresh.

---

## 10. Evolution / Updates

Every session that applies a method updates its state:

- `times_used += 1`
- `last_used` = session timestamp
- Evolution Log gets a line: `{date}: {one-line outcome — worked, failed, revised}`
- If the session shows the method worked (AUDITOR flagged no process issues, REVIEWER approved on first pass): `evidence_count += 1`
- If the session shows the method failed (user overrode, REVIEWER vetoed on method-related grounds, AUDITOR flagged a mismatch): `challenges += 1`
- `confidence` recomputed with the standard formula

**Minor revisions** (clarifying wording, adding a warning) are applied by archiver Phase 2 without user confirmation.

**Major revisions** (step additions, step removals, condition changes) require user confirmation at next Start Session. archiver writes the proposed change to `_meta/methods/_tentative/_revisions/{method_id}-{date}.md` and surfaces it alongside new candidates.

---

## 11. Decay

Methods use `permanence: skill` decay — logarithmic decline to a floor, not full evaporation. Earned procedural knowledge should be hard to forget.

| Elapsed since last_used | State | Action |
|--------------------------|-------|--------|
| ≤ 6 months | Active | No action |
| 6–12 months | Dormant | RETROSPECTIVE flags in briefing: "Method '{name}' has been dormant for N months." |
| ≥ 12 months | Archived | archiver moves file to `_meta/methods/_archive/{method_id}.md`. |
| Archived + user explicitly deletes | Retired | File gone. No auto-recreation even if the pattern resurfaces. |

Methods are never auto-deleted. Methods are earned; archiving is the strongest automatic action the system takes. Final deletion always requires the user.

---

## 12. Scope Guards (Privacy)

The same privacy filter that applies to wiki entries (see `references/wiki-spec.md` section "Privacy Filter") applies to method bodies:

- Do NOT include personal names in method text — stripped before write
- Do NOT reference specific projects in the method body — project references may appear only inside `source_sessions`
- Do NOT include specific amounts, account numbers, or ID numbers — keep all numeric examples generic ("~12 months runway", not "¥8,400,000")
- Do NOT include traceable date+location combinations
- Do NOT include specific company names unless the method is genuinely about that company (rare)

If stripping these references leaves the method meaningless → the pattern wasn't actually reusable, discard the candidate.

Methods are stored locally only. They are never synced to Notion (user decision #12).

---

## 13. INDEX.md Format

`_meta/methods/INDEX.md` is compiled by RETROSPECTIVE at every Start Session from the actual method files. Never hand-edit it.

```markdown
# Method Library Index
compiled: YYYY-MM-DD

## canonical (5)
- iterative-document-refinement | Refine documents in 5 escalating quality rounds | used 12 times | 0.85
- runway-fundraise-trigger | Start fundraising when runway drops below 12 months | used 7 times | 0.78
- ...

## confirmed (8)
- responsibility-authority-matrix | Delegate by mapping responsibility × authority | used 3 times | 0.55
- ...

## tentative (3)  [awaiting user confirmation in _tentative/]
- weekly-review-reset | Reset every Friday by listing completions and drops | observed 2 sessions | 0.30
- ...

## dormant (1)  [≥6 months since last use]
- quarterly-strategic-review | Quarterly strategic reset framework | last used 2025-10-14 | 0.62
```

Each line ≤ 100 characters. Entire INDEX is typically 30–120 lines. Cheap to load, easy to scan.

---

## 14. Interaction with Hermes Skills

Hermes Skills are procedural memory for tool-use (how to call an API, how to format a shell command). Life OS methods are procedural memory for decision-making (how to evaluate a choice, how to refine a document, how to time a fundraise).

| Dimension | Hermes Skill | Life OS Method |
|-----------|--------------|----------------|
| Scope | Tool operation | Decision workflow |
| Activation | Explicit syntax (`@skill:name`) | Automatic via dispatcher condition match |
| Security scan | Required (can execute code) | Not required (user-confirmed text only) |
| Lifecycle | Skills version explicitly | Methods evolve via Evolution Log |

The method library borrows Hermes's YAML + markdown + evolution log pattern but drops what Hermes needs for tool-use context (activation syntax, security scanning, version locking).

---

## 15. Migration from v1.6.x

v1.6.2a does not have a method library. `tools/migrate.py` backfills from the existing session history:

1. Scan `_meta/journal/*.md` and backfilled decisions for language that describes approaches: "approach", "pattern", "framework", "process", "流れ", "やり方", "手順".
2. Extract the top 5 most-referenced patterns (by cross-session mention count).
3. Write each as a candidate to `_meta/methods/_tentative/{method_id}.md` with `status: tentative` and `confidence: 0.3`.
4. Flag for user review at next Start Session.

Migration is one-shot. Further pattern detection happens through archiver Phase 2 on live sessions.

The migration script does NOT promote past tentative. The user decides whether any backfilled pattern actually becomes a confirmed method.

---

## 16. Out of Scope for v1.7

Explicitly out of scope for v1.7:

- **Parameterized methods** — "iterative refinement with N rounds" as one parameterized method or N methods? v1.7 uses atomic methods only.
- **Versioned history** — methods do NOT carry version strings. The Evolution Log captures change history sufficiently.
- **Composition** — hard composition (automatic chained execution) is out of scope for v1.7. Soft composition via `related_methods` is the v1.7 answer.
- **Cross-language bodies** — v1.7 writes all method bodies in English; theme affects display only at Summary Report level.

---

## 17. Anti-patterns

- Do NOT auto-promote past `confirmed` without explicit user input
- Do NOT create a method from a single session observation
- Do NOT store project-specific tactics as methods — they belong in `projects/{name}/`
- Do NOT sync methods to Notion — local only
- Do NOT let the tentative queue grow unbounded — 5 silent Start Sessions = auto-archive
- Do NOT write methods that reference specific names, amounts, IDs, companies, or locations
- Do NOT let archiver edit confirmed/canonical methods without the Major Revision workflow
- Do NOT compile INDEX.md by hand — it is a generated artifact
- Do NOT treat `permanence: skill` as permanence — dormant methods still age, they just age slowly

---

## 18. How Each Role Uses the Method Library

All roles check if `_meta/methods/INDEX.md` exists before referencing it. If it does not exist or is empty, the role operates without method input.

| Role | What they read | How they use it |
|------|---------------|-----------------|
| RETROSPECTIVE | `_meta/methods/INDEX.md` + `_tentative/` | Compiles INDEX at Start Session. Surfaces candidates for confirmation. Flags dormant methods. |
| ROUTER | INDEX (header) | Scans for domain-relevant methods during triage. May inform user "you have a known approach for this." |
| PLANNER | INDEX (full) | Reviews which methods are applicable before drafting the planning document. May reference by name. |
| DISPATCHER | Relevant method bodies | Injects into domain briefs as "Known Method" (section 9). |
| Six Domains | Method bodies in dispatch context | Applies known method instead of re-deriving workflow. Reports adherence or deviation. |
| REVIEWER | INDEX | Consistency check — if a planning document ignored an applicable method, flag it. |
| AUDITOR | `_meta/methods/` directory | Patrol inspection — stale methods, contradictions, candidates sitting too long. |
| ARCHIVER | INDEX + all method files | Phase 2: detect candidates, update evolution logs, propose revisions. |
| DREAM | INDEX | REM stage uses method patterns as connective tissue for cross-domain insights. |

---

## 19. Related Specs

- `references/wiki-spec.md` — adjacent knowledge layer (declarative vs procedural)
- `references/soul-spec.md` — identity layer
- `references/dream-spec.md` — REM stage detects method patterns
- `references/concept-spec.md` — methods link to concepts via `related_concepts`
- `references/hippocampus-spec.md` — past-session retrieval feeding the cross-session echo heuristic
- `pro/agents/archiver.md` — writes method candidates (Phase 2)
- `pro/agents/dispatcher.md` — injects methods into domain briefs
- `devdocs/research/2026-04-19-hermes-analysis.md` — source of the Hermes inspiration

---

## 20. Constraints Summary

- Auto-created by archiver only when the candidate heuristic passes
- User confirmation required to leave `_tentative/`; promotion to canonical is automatic at 5 uses + 0.7 confidence, promotion to confirmed is not
- Privacy filter applied before every write; methods are local-only (never sync to Notion)
- INDEX.md is compiled, not authored
- One workflow per file — do not create method collections
- Methods are never auto-deleted — only auto-archived after 12 months dormant
- Major revisions require user confirmation
- Methods use the same confidence formula as SOUL and wiki
