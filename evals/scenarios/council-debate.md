# Scenario: Council Debate

## User Message

```
I received an offer to go to Singapore, with my salary doubling to the JPY equivalent of 16 million. But my wife is 4 months pregnant, her parents are in Tokyo, and my parents are back in China. She says she supports me but I can tell she's not really happy about it. The offer requires starting next month.
```

## Design Intent

To have at least two domains produce directionally conflicting assessments: FINANCE domain (salary doubling = strong positive) vs PEOPLE/INFRA domain (relocating during pregnancy + away from parents + spouse's true feelings in doubt = strong negative). This conflict should trigger a Council debate.

## Expected Behavior

- **Router**: Should escalate (multi-area + irreversible + affects family), recommend activating all Six Domains or at least 5
- **FINANCE domain**: Likely high score (7-9), salary doubling is a strong positive signal
- **PEOPLE domain**: Likely low score (3-6), relocating during pregnancy + away from both sets of parents + spouse's true feelings in doubt
- **INFRA domain**: Likely low score (3-5), international relocation during pregnancy poses significant physical and mental health risks
- **GOVERNANCE domain**: Should flag "she says she supports me but I can tell she's not happy" as a signal of insufficiently informed consent
- **Reviewer final review**: Should identify the directional conflict in scores, recommend or trigger Council
- **Council debate**:
  - Round 1: Each side states their position
  - Round 2: Should see concessions or conditional proposals (e.g., "delay start by 3 months", "negotiate remote transition period")
  - Round 3: Should converge on consensus points and irreconcilable disagreements
- **Planner synthesis**: Consensus and disagreements should be clearly separated

## Quality Checkpoints

- [ ] At least 2 domains have a score gap >= 3 points
- [ ] Reviewer final review explicitly identified the conflict
- [ ] Council debate was triggered (not skipped)
- [ ] 3 rounds of debate show progression: Round 2 is not a repeat of Round 1
- [ ] Round 2 or Round 3 produced conditional proposals ("if...then...")
- [ ] Planner synthesis lists consensus and disagreements separately
- [ ] Final Summary Report reflects the Council debate results
- [ ] Action items include "have an in-depth conversation with spouse to confirm true feelings"
