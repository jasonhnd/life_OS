# Scenario: Large Purchase

**Path**: Express Analysis

## User Message

```
I want to buy a MacBook Pro M4 Max, top spec is about 600,000 JPY. I'm currently using a 3-year-old M1 MacBook Air — it's fine for daily development but a bit slow for running AI models. Mainly, I saw that all my colleagues have upgraded to the new model and feel like I should upgrade too.
```

## Expected Behavior

- **Router**: Should escalate to court (amount > 10% of monthly income), recommend activating FINANCE + EXECUTION + GOVERNANCE domains
- **Planner**: Should not activate all Six Domains (doesn't involve interpersonal/learning/health), 3 domains is sufficient
- **FINANCE domain**: Should quantify the ratio of 600,000 JPY to income/savings, assess financial reasonableness
- **EXECUTION domain**: Should evaluate the actual performance gap between M1 Air vs M4 Max, whether there's a better value option
- **GOVERNANCE domain**: Should check whether "all colleagues upgraded" is FOMO, assess impulse spending risk
- **Reviewer sentiment review**: Should question the "saw that all colleagues upgraded" motivation
- **Advisor**: Should point out the herd mentality signal

## Quality Checkpoints

- [ ] Router did not directly say "buy it" or "don't buy it", escalated correctly
- [ ] Planner did not activate all Six Domains (activated <= 4 domains)
- [ ] FINANCE domain provided specific financial ratios
- [ ] EXECUTION domain analyzed actual needs vs wants gap
- [ ] GOVERNANCE domain or Reviewer identified FOMO / herd mentality motivation
- [ ] Overall score should not be > 8 (clear irrational motivation present)
