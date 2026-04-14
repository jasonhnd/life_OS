# Scenario: Large Purchase

**Path**: 🏃 Express Analysis

## User Message

```
I want to buy a MacBook Pro M4 Max, top spec is about 600,000 JPY. I'm currently using a 3-year-old M1 MacBook Air — it's fine for daily development but a bit slow for running AI models. Mainly, I saw that all my colleagues have upgraded to the new model and feel like I should upgrade too.
```

## Expected Behavior

- **Prime Minister**: Should escalate to court (amount > 10% of monthly income), recommend activating Ministry of Revenue + Ministry of War + Ministry of Justice
- **Secretariat**: Should not activate all Six Ministries (doesn't involve interpersonal/learning/health), 3 ministries is sufficient
- **Ministry of Revenue**: Should quantify the ratio of 600,000 JPY to income/savings, assess financial reasonableness
- **Ministry of War**: Should evaluate the actual performance gap between M1 Air vs M4 Max, whether there's a better value option
- **Ministry of Justice**: Should check whether "all colleagues upgraded" is FOMO, assess impulse spending risk
- **Chancellery sentiment review**: Should question the "saw that all colleagues upgraded" motivation
- **Remonstrator**: Should point out the herd mentality signal

## Quality Checkpoints

- [ ] Prime Minister did not directly say "buy it" or "don't buy it", escalated correctly
- [ ] Secretariat did not activate all Six Ministries (activated <= 4 ministries)
- [ ] Ministry of Revenue provided specific financial ratios
- [ ] Ministry of War analyzed actual needs vs wants gap
- [ ] Ministry of Justice or Chancellery identified FOMO / herd mentality motivation
- [ ] Overall score should not be > 8 (clear irrational motivation present)
