# User-invoked prompt · research (v1.8.1)

> Multi-agent parallel research → synthesized wiki draft with built-in
> counter-bias check. ROUTER reads this when the user wants to seed a
> new wiki entry from external sources.

## Trigger keywords

- `调研一下 X` / `深挖 X` / `多角度研究 X`
- `research X` / `deep dive X`
- `/research <topic>` (slash command escape hatch with arguments)

## Argument parsing

ROUTER extracts:
- `topic` (required, free-form string)
- `depth` ∈ {`normal`, `deep`} (default `normal` = 5 agents; `deep` = 8)
- `thesis` (optional string; if provided, agents weigh for/against)

If natural language ambiguity (e.g. "research stablecoins"), ROUTER may
ask 1 clarifying question (which angle, what scope) before launching.
Limit clarification to ONE round to keep total time ≤ 7 minutes.

## Pre-flight

1. Verify cwd is a second-brain repo (`_meta/` + `wiki/` exist). If not,
   refuse and tell user `/research` writes wiki entries; must run inside
   a second-brain vault.
2. Read `wiki/SCHEMA.md` to confirm frontmatter contract.
3. List `wiki/` domain directories. Cache list — synthesis must place the
   draft under one of these (or explicitly create new with user approval).
4. Estimate cost upfront: tell user "Spawning N agents — estimated 5-7
   min and ~$0.30-0.80 in API tokens. Continue?" Wait for "yes" or "go".
   (Skip estimate prompt if user explicitly typed `/research`; that's
   already opt-in.)

## Phase 1 · Decompose (main context, ~30 sec)

Decompose `<topic>` into N angles where N=5 (normal) or N=8 (deep):

**Normal (5 angles)**:
1. **academic** — peer-reviewed papers, formal definitions, established models
2. **practitioner** — industry blog posts, conference talks, current implementations
3. **contrarian** — known critiques, failed implementations, opposing schools
4. **origin** — historical first-principles, who coined the concept and why
5. **adjacent** — neighboring fields that touch the topic from outside

**Deep adds (3 more)**:
6. **mechanistic** — how does it actually work at the mechanism level (math, data flow, protocol)
7. **data-statistics** — quantitative evidence, benchmark results, market sizes
8. **meta-review** — what surveys / systematic reviews already exist

For each angle, write a 1-sentence brief (e.g. "academic: find peer-reviewed
papers from 2020-2026 on X; identify the 2-3 most-cited"). Cache angles for
phase 2 + show user the angle list before launching agents (1 line each).

## Phase 2 · Parallel research (5-8 subagents, ~5 min hard cap)

In a SINGLE message, launch all N subagents in parallel (one Task tool call
per agent within the same message — Claude Code parallelism requirement).

Subagent type: `general-purpose`

Each subagent receives:

```
You are conducting one angle of a multi-agent research run on:

Topic: <topic>
Your angle: <angle name> — <angle brief>
Depth: <normal|deep>
Thesis (if any): <hypothesis to weigh evidence around, or "none">

Your job:
1. Use WebSearch (2-4 queries) + WebFetch (1-3 fetches) to gather
   evidence specific to your angle.
2. Time budget: 5 minutes hard cap. If you can't find substantive
   sources in 5 min, return what you have with a clear "thin coverage"
   note — DO NOT fabricate.
3. Output format (≤ 500 words):

   ## <angle name>

   ### Key findings (3-5 bullets)
   - ...

   ### Sources (3-5 URLs with 1-line each)
   - <url> — <what's there>

   ### If thesis-driven — supports / contradicts thesis?
   - support: ...
   - contradict: ...
   - neutral: ...

   ### Coverage confidence
   - sources-count, source-quality, contradiction-resolved? (one line)

Constraints:
- Do NOT write to any file. Output is text only — main context will
  synthesize.
- Do NOT call other subagents.
- Do NOT include your reasoning trace; the 500-word output IS your reply.
- If WebSearch / WebFetch rate-limits, retry once with backoff, then
  report partial coverage.
```

After all N subagents return (or 5-min hard cap hits), proceed to phase 3.
Track failures: if ≥40% of agents failed, abort with a clear error rather
than synthesizing from a thin base.

## Phase 3 · Synthesize (main context, ~90 sec)

Combine the N agent outputs into ONE wiki draft.

### Domain decision

Pick the wiki domain by inspecting agent outputs + the cached domain list.
If the topic clearly belongs to an existing domain (e.g. "稳定币 B2B" →
`fintech`), use that. If it spans multiple domains, pick the dominant
angle (the one with the most agent coverage). If no existing domain fits,
ASK the user which existing domain to use OR confirm creating a new
domain. Never invent silently.

### Slug

Lowercase kebab-case, ≤ 50 chars, derived from the topic.

### Frontmatter (SCHEMA-compliant)

```yaml
---
title: "<one-line title; max 80 chars>"
domain: <domain>
created: <YYYY-MM-DD>            # today
last_updated: <YYYY-MM-DD>       # same as created
confidence: 0.65                 # default; bump to 0.75 if 4+ agents converge
tags: [<domain>, research-generated]
status: candidate
source: |
  - <url-1> (<angle-1>)
  - <url-2> (<angle-2>)
  - ...
research_run:
  agents: <N>
  depth: <normal|deep>
  thesis: "<thesis if any, else null>"
  date: <YYYY-MM-DD>
---
```

### Body (≤ 1200 words first version)

```markdown
# <title>

## TL;DR
<2-3 sentence summary distilled from all N agents>

## Key facts
- <fact-1, with source ref>
- <fact-2, with source ref>
- <fact-3, with source ref>
(5-8 bullets total; each ≤ 25 words)

## Mechanism / How it works
<2-4 paragraphs. Pull from `practitioner` + `mechanistic` (if deep) angles>

## Origin & evolution
<1-2 paragraphs. Pull from `origin` angle>

## Current landscape
<1-2 paragraphs. Pull from `practitioner` + `data-statistics` (if deep) angles>

## Counterpoints
<2-4 bullets. Pull from `contrarian` angle. THIS SECTION IS MANDATORY —
even if all agents converged, write "No substantive opposition found in
this run; agents <list> all aligned. Re-test in 3 months for new
critiques.">

## Open questions
<2-4 bullets — questions the research couldn't answer. Honest gaps.>

## Sources
<full URL list grouped by angle, deduplicated>
```

## Phase 3.5 · Counter-bias check (default ON; off only if `--no-bias-check`)

After synthesis, scan the draft:
- If `Counterpoints` section is empty or trivial ("none, all sources
  converge"), AND
- the topic is one where reasonable disagreement exists (not pure
  factual lookups like "what is the capital of France"),

then launch ONE additional subagent with this prompt:

```
The following wiki draft was synthesized from N parallel research agents.
Find substantive opposing evidence — papers, blog posts, practitioner
reports — that contradicts or weakens the core claims.

Time budget: 3 minutes hard cap.

If you find substantive opposition, output:
  ## Opposing evidence
  - <claim being challenged>: <opposing source URL> — <1-sentence why>

If after 3 min you genuinely find nothing substantive, output:
  ## Opposing evidence
  No substantive opposition found in 3-min counter-search. Tried queries:
  - <q1>
  - <q2>
  - <q3>

Draft:
<paste full draft>
```

If counter-bias agent returns substantive opposition, splice it into the
`Counterpoints` section of the draft and BUMP `confidence` DOWN by 0.1.
If it returns "none found", leave the draft confidence as-is and keep the
honest "no substantive opposition found" note in `Counterpoints`.

## Phase 4 · User review (interactive)

Show user:

```
🔬 /research complete — N agents, M minutes elapsed

Proposed wiki entry: wiki/<domain>/<slug>.md

[paste full frontmatter + body here]

Sources used: <count> URLs across <N> angles
Counter-bias check: <found-opposition | no-opposition-found | skipped>

Choose:
  accept       — write file, append wiki/log.md, update wiki/INDEX.md
  edit <X>     — re-show with X changed (e.g. "edit confidence=0.55",
                 "edit domain=banking", "edit drop counterpoints-section-3")
  reject       — discard; nothing written
  defer        — write to _meta/inbox/to-process/<date>_research-<slug>.md
                 with full draft for later /inbox-process review

Type your choice:
```

Wait for explicit choice. Do NOT execute on assumption.

## Phase 5 · Write (only on accept)

1. Write `wiki/<domain>/<slug>.md` (Write tool, full content from synthesized
   draft).
2. Append `wiki/log.md`:
   ```
   - [HH:MM] created  | wiki/<domain>/<slug>.md | research(N agents): <one-line topic>
   ```
3. Update `wiki/INDEX.md` to add the entry under its domain section.
4. Report:
   ```
   ✅ Wrote wiki/<domain>/<slug>.md
      confidence: <X>
      tags: [<domain>, research-generated]
      sources: <N> URLs
      counter-bias: <result>
   ```

If accept fails (disk full, permissions, schema validation): rollback
both the file write and the log append; report the failure cleanly so
user can retry.

## Failure modes

- **All / most agents fail**: abort phase 3; tell user "research aborted
  — N/M agents failed; common cause: rate limit / network. Retry in 5
  min or run with --depth normal".
- **WebSearch unavailable**: skip phase 2 entirely; tell user research
  needs WebSearch; suggest running with explicit URLs they want fetched.
- **Topic too narrow** (agents return "no sources found" for 4+ angles):
  abort; tell user the topic may need broader framing.
- **Topic too broad** (agents return wildly divergent material):
  synthesize anyway but flag in `Open questions`; suggest a narrower
  follow-up `/research`.

## Cost guidance

Rough estimates:
- 5 agents × (2-4 WebSearch + 1-3 WebFetch each) ≈ 15-35 tool calls
- Plus 1 synthesis + 1 counter-bias = ~20-40 LLM calls total
- Token usage: ~80k-150k input + ~10k-20k output
- USD cost: ~$0.30-0.80 per `/research` run (Claude opus pricing)

If user runs `/research` 10x/day, that's $3-8/day. Budget accordingly.
