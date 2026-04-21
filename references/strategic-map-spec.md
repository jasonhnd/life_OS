# Strategic Map Specification

The Strategic Map is the relationship layer between projects — recording how they group, flow, and affect each other. It enables Life OS to reason at the portfolio level, not just the project level.

Designed based on cognitive science research: Goal Systems Theory (Kruglanski 2002), Recognition-Primed Decision model (Klein 1998), and Predictive Coding framework (Friston 2005).

## Design Principles

1. **Two-layer architecture**: structural (user-defined, slow-changing) + dynamic (system-computed, refreshed at each Start Court)
2. **Single source of truth**: `projects/{project}/index.md` frontmatter stores per-project strategic data; `_meta/strategic-lines.md` stores line definitions; `_meta/STRATEGIC-MAP.md` is compiled (never hand-edited)
3. **Grows from zero**: if no strategic data exists, the system operates normally — the feature is dormant until the user defines relationships
4. **User-confirmed structural changes**: new strategic lines, project roles, and flow relationships require user confirmation (like SOUL/wiki candidates)
5. **Pattern matching + narrative assessment**: no numerical scores — match health archetypes and write a story about what's happening, what it means, and what to do
6. **Cross-layer integration**: Strategic Map works with SOUL.md, wiki/, and DREAM as one cognitive system

## Data Structures

### Strategic Line (`_meta/strategic-lines.md`)

Lives in the user's second-brain (not the Life OS repo). Multiple lines separated by `---`. Created when the user first defines a strategic grouping.

```yaml
---
type: strategic-line
id: "market-expansion"
name: "Market Expansion Pipeline"
purpose: "Build market presence in target segment"
driving_force: "Establish first-mover advantage in target segment before market consolidation"
health_signals:
  - "Key milestones progressing"
  - "Partner onboarding on track"
  - "Legal review turnaround within expected windows"
time_window: 2026-09-30
area: "ventures"
created: 2026-04-15
---
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique identifier (kebab-case) |
| name | string | yes | Display name |
| purpose | text | yes | One-sentence formal purpose |
| driving_force | text | no | What truly drives your investment in this line (can differ from purpose) |
| health_signals | text[] | no | What signals indicate this line is healthy (AI proposes based on driving_force, user confirms) |
| time_window | date | no | Deadline affecting the entire line |
| area | string | no | Associated life area |
| created | date | auto | Creation date |

#### About `driving_force`

Based on Goal Systems Theory (Kruglanski 2002) and self-deception research (von Hippel & Trivers 2011): humans often pursue goals with a stated reason and a deeper motivating force. `purpose` is the formal positioning; `driving_force` is what actually drives your effort allocation.

- If driving_force = purpose, leave it empty (system treats them as identical)
- driving_force affects which health signals matter — a line driven by "relationships" should watch social activity, not code commits
- The ADVISOR checks if your behavior aligns with driving_force, not just purpose

#### About `health_signals`

- First time a strategic line is created, the RETROSPECTIVE proposes health signals based on driving_force
- User confirms or modifies
- Confirmed signals are stored and used for subsequent assessments
- DREAM may propose signal updates as the line evolves

### Per-Project Strategic Fields (`projects/{project}/index.md`)

Added to the existing frontmatter. All fields are optional and default to empty/null.

```yaml
strategic:
  line: "market-expansion"
  role: "critical-path"
  flows_to:
    - target: "project-beta"
      type: "cognition"
      description: "Certification results reused"
  flows_from:
    - source: "project-gamma"
      type: "cognition"
      description: "Industry knowledge input"
  last_activity: 2026-04-12
  status_reason: "Waiting for legal review, expected next month"
```

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| strategic.line | string | references strategic-line id | Which strategic line this project belongs to |
| strategic.role | enum | `critical-path` / `enabler` / `accelerator` / `insurance` | Role within the line |
| strategic.flows_to[] | array | objects: {target, type, description} | Outgoing flows to other projects |
| strategic.flows_from[] | array | objects: {source, type, description} | Incoming flows from other projects |
| strategic.last_activity | date | ISO date | Last modification date (auto-updated by ARCHIVER) |
| strategic.status_reason | text | free text | Why this project is in its current status (critical for distinguishing controlled wait vs uncontrolled stall) |

### Role Definitions

| Role | Meaning | Constraint |
|------|---------|------------|
| `critical-path` | If this stalls, the line stalls | Exactly one per line |
| `enabler` | Must complete before critical-path can proceed | Multiple allowed |
| `accelerator` | Makes the line faster but is not blocking | Multiple allowed |
| `insurance` | Reduces risk if primary approach fails | Multiple allowed |

### Flow Type Definitions

| Type | Meaning | Urgency when blocked |
|------|---------|---------------------|
| `cognition` | Conclusions or knowledge inform another project's decisions | Medium (async, carried via wiki entries) |
| `resource` | Artifacts, assets, code, or deliverables flow to another project | High (concrete dependency) |
| `decision` | A decision constrains or invalidates choices in another project | Critical (must sync immediately) |
| `trust` | Relationship capital built in one project benefits another | Low (long-term accumulation) |

## Assessment Method

### Health Archetypes (not numerical scores)

Based on Klein's Recognition-Primed Decision model: experts assess situations through pattern matching against experienced cases, producing narrative assessments — not by computing weighted averages.

| Archetype | Signals | Meaning |
|-----------|---------|---------|
| 🟢 Steady progress | active + recent activity + tasks on track | No intervention needed |
| 🟡 Controlled wait | on-hold + has status_reason + within expected window | Normal, but monitor the time window |
| 🟡 Momentum decay | active but activity declining + tasks accumulating | Possible attention drift |
| 🔴 Uncontrolled stall | on-hold + no status_reason or past expected window | Needs intervention |
| 🔴 Direction drift | active but behavior misaligned with driving_force | Doing the wrong things |
| ⚪ Dormant | insurance role + long inactive | Expected, not alarming |

Assessment process per strategic line:
1. Read all signals (status, activity, tasks, status_reason, driving_force, health_signals)
2. Match to archetype
3. Mental simulation: if we continue like this, where will this line be in 3 weeks?
4. Write narrative: current state + what it means + what to watch
5. Flag blind spots: what information is missing?

### Decay Thresholds

| Role | Warn | Alert |
|------|------|-------|
| critical-path | 7 days inactive | 14 days |
| enabler | 14 days | 30 days |
| accelerator | 30 days | 60 days |
| insurance | 60 days | no alert (expected dormant) |

### Decision Propagation

When a decision is made in a project, check flows_to for downstream impact:

| Flow type | Downstream impact | Severity |
|-----------|-------------------|----------|
| `decision` | Downstream project's premises may be invalidated | Critical — flag immediately |
| `cognition` | Changed conclusions affect downstream analysis | Medium — note for review |
| `resource` | Deliverable changes affect downstream inputs | Medium — verify downstream still has what it needs |
| `trust` | Relationship changes affect downstream trust capital | Low — note for awareness |

Checked by:
- **REVIEWER**: during review (pre-decision, as a veto criterion)
- **ARCHIVER**: during Phase 2 (post-decision, as a warning in outbox)
- **RETROSPECTIVE**: during compilation (stale warnings from previous sessions)

### Blind Spot Detection

Based on Predictive Coding (Friston 2005) and Kahneman's research on absence neglect: the most dangerous cognitive failure is not noticing what's missing.

| Blind spot type | Detector | When |
|----------------|----------|------|
| Undefined relationships (projects not in any line) | RETROSPECTIVE | Start Court — scan unaffiliated projects |
| Driving force neglect (behavior misaligned with driving_force) | ADVISOR | After every Draft-Review-Execute flow |
| Dimension gaps (life areas absent from all strategic lines) | DREAM REM | 3-day scan — check life dimension coverage |
| Approaching time windows with no preparation | RETROSPECTIVE + EXECUTION domain | Start Court briefing + execution assessment |
| Broken flows (defined but not actually flowing) | REVIEWER + ARCHIVER | Review — check wiki references; Adjourn — check session materials |

## Cross-Layer Integration

### SOUL × Strategic Map

`driving_force` is essentially "what part of SOUL does this strategic line serve."

- If SOUL.md says "family > career" (confidence 0.8) but all strategic lines have career-related driving forces → flag as SOUL-strategy misalignment
- REVIEWER checks: does this decision's strategic line align with SOUL dimensions?
- DREAM REM checks: are driving forces consistent with SOUL over time?

### wiki × Strategic Map

Cognition flows between projects are carried by wiki content.

- If a cognition flow is defined (A → B) and wiki has entries from A's domain, those entries ARE the substance of the flow
- RETROSPECTIVE cross-checks: does the cognition flow's wiki domain have content? Has the downstream project referenced it?
- A "broken flow" = wiki entries exist but downstream project never cited them

### DREAM × Strategic Map

DREAM is the synthesis engine across all three knowledge layers.

Without Strategic Map: DREAM REM asks open-ended "any cross-project connections?"
With Strategic Map: DREAM REM has scaffolding:
- **Structural checks**: Are defined flows still valid? Any stale or broken?
- **SOUL × strategy**: Are driving forces consistent with SOUL dimensions?
- **Patterns × strategy**: Is user behavior aligned with strategic priorities?
- **wiki × flows**: Is knowledge actually being transferred between projects?
- **Beyond structure**: What connections exist that the strategic map hasn't captured yet?

## Compiled Output: `_meta/STRATEGIC-MAP.md`

Compiled by the RETROSPECTIVE at every Start Court (step 8.5). Never hand-edited.

### Compilation Algorithm

```
1. Read _meta/strategic-lines.md → all line definitions
2. Read all projects/*/index.md → collect strategic fields
3. For each line:
   a. Collect projects with matching strategic.line, sort by role
   b. Match health archetype (using status + activity + tasks + status_reason + health_signals)
   c. Write narrative assessment
   d. Detect line-level blind spots
4. Cross-layer verification:
   a. SOUL × driving_force alignment
   b. wiki × cognition flow completeness
   c. user-patterns × strategic priorities
5. List unaffiliated projects
6. Build flow graph from all flows_to/flows_from
7. Generate action recommendations (leverage ranking + safe-to-ignore + decisions needed)
8. Write _meta/STRATEGIC-MAP.md
```

### Output Format

```markdown
# Strategic Map
compiled: YYYY-MM-DD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺️ Strategic Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[emoji] [line-name]                    [archetype indicator]
   Window: [deadline or open-ended] ([N weeks remaining])
   Driving: [driving_force]

   [project]   [role]   [status indicator]
   [project]   [role]   [status indicator]

   Narrative:
     [What's happening + what it means + what to watch]

   → Action implication: [what this means for today]


📌 Unaffiliated
   [project] — [status] [priority]
   → Oversight or intentionally independent?

🕳️ Blind Spots
   · [dimension gaps]
   · [broken flows]
   · [SOUL-strategy misalignment]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Today
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 [Highest leverage action]
   Leverage: [why this matters most]
   Effort: [estimated time] | Cost of inaction: [what happens if you don't]

🥈 [Worth attention]
   Leverage: [why]
   Cost of inaction: [what happens]

🟢 Safe to ignore
   · [project] — [reason]

❓ Decisions needed
   · [structural question for user]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flow Graph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[project-a] →([flow-type])→ [project-b]
...
```

## Action Recommendation Logic

Based on Shenhav, Botvinick & Cohen (2013): the brain computes "expected value of control" — not just importance, but importance weighted by effort cost and opportunity cost.

### Highest Leverage Selection

```
1. Is there a strategic line with a closing time window (< 4 weeks)?
   → That line's unfinished work gets top priority

2. Is there a critical-path project that's stalled?
   → Can something else in that line be advanced during the wait?
   → If yes → advance the enabler/accelerator (exploit the waiting period)

3. Is there a driving_force being neglected?
   → Behavior patterns show avoidance of a strategic priority → flag

4. None of the above → advance the healthiest line's next step
   (momentum is valuable — don't waste a good streak)
```

### Safe to Ignore

Active suppression of low-priority items (Desimone & Duncan 1995: attention works primarily by suppressing irrelevant signals).

A project is safe to ignore when:
- It is on track (🟢 archetype) AND not on critical path
- It is insurance role AND primary approach shows no failure signs
- It is in another strategic line that is healthy

### Decisions Needed

Generated when the system detects structural gaps:
- Projects not assigned to any line
- Projects with flows but no role
- Strategic lines with no critical-path project
- health_signals not yet confirmed by user

## Cold Start

If `_meta/strategic-lines.md` does not exist:
- RETROSPECTIVE skips strategic compilation silently
- Briefing falls back to original Area Status flat list format
- After 3+ sessions with multiple projects, DREAM REM may propose: "You have N active projects but no strategic relationships defined. Would you like to map how they relate?"
- The user can define relationships at any time by telling the ROUTER

First-time setup flow:
1. User says "let's map my projects" (or DREAM proposes)
2. ROUTER guides conversation: "Which projects serve the same purpose?" → "What flows between them?" → "What's really driving you on this?"
3. ARCHIVER writes strategic-lines.md + index-delta.md with strategic fields
4. RETROSPECTIVE proposes health_signals based on driving_force → user confirms
5. Next Start Court → first Strategic Map compilation

## Graceful Degradation

- No strategic-lines.md → skip entirely, fallback to flat Area Status
- strategic-lines.md exists but no projects have strategic fields → compile empty map, skip in briefing
- A flow references a project that no longer exists → flag as stale in Warnings
- A strategic line has only one project → not an error, note "single-project line"
- Critical-path project changes to done → flag: "Line may need new critical-path assignment"
- SOUL.md doesn't exist → skip SOUL × strategy alignment checks
- wiki/ doesn't exist → skip wiki × flow verification
