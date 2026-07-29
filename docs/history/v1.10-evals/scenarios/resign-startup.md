# Scenario: Resign to Start a Business

**Path**: Full Court

## User Message

```
I'm a software engineer at a Japanese company, earning 8 million JPY per year, and I've been working in Tokyo for 3 years. Lately I've been feeling more and more bored, and I want to quit to build my own SaaS product. I have about 5 million JPY in savings. No co-founder, and I haven't decided what product to build — I just feel like I should take the leap while I'm still young.
```

## Expected Behavior

- **Router**: Should escalate to court (involves career + finances + irreversible change), should not handle directly
- **Planner**: Should activate all Six Domains, covering at least finance/capability/network/execution/risk/lifestyle — 6 dimensions
- **Reviewer reviews the plan**: Should flag "haven't decided what product to build" as a critical gap
- **FINANCE domain**: 5 million JPY / Tokyo monthly living costs ≈ 20-25 months runway, but need to subtract startup costs
- **GOVERNANCE domain**: Should check non-compete clauses (common in Japanese companies), visa implications (if on work visa)
- **EXECUTION domain**: Should point out "no specific direction" as the biggest execution obstacle
- **INFRA domain**: Should address physical and mental health and quality of life during the startup period
- **Reviewer final review**: Scores should not all be >= 7 ("haven't decided what to build" is a clear weakness)
- **Advisor**: Should examine whether "take the leap while I'm still young" is a cognitive bias

## Quality Checkpoints

- [ ] Router did not handle directly, escalated correctly
- [ ] Planner activated >= 5 domains
- [ ] Reviewer questioned at least one dimension
- [ ] FINANCE domain provided a specific runway figure
- [ ] GOVERNANCE domain mentioned non-compete clause or visa issues
- [ ] At least one domain scored < 6
- [ ] Action items include "determine product direction first"
- [ ] Advisor provided substantive counsel (not platitudes)
- [ ] Auditor identified at least one area for improvement
