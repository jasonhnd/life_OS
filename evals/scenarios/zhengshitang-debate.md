# Scenario: Political Affairs Hall Debate

## User Message

```
I received an offer to go to Singapore, with my salary doubling to the JPY equivalent of 16 million. But my wife is 4 months pregnant, her parents are in Tokyo, and my parents are back in China. She says she supports me but I can tell she's not really happy about it. The offer requires starting next month.
```

## Design Intent

To have at least two ministries produce directionally conflicting assessments: Ministry of Revenue (salary doubling = strong positive) vs Ministry of Personnel/Ministry of Works (relocating during pregnancy + away from parents + spouse's true feelings in doubt = strong negative). This conflict should trigger a Political Affairs Hall debate.

## Expected Behavior

- **Prime Minister**: Should escalate (multi-area + irreversible + affects family), recommend activating all Six Ministries or at least 5
- **Ministry of Revenue**: Likely high score (7-9), salary doubling is a strong positive signal
- **Ministry of Personnel**: Likely low score (3-6), relocating during pregnancy + away from both sets of parents + spouse's true feelings in doubt
- **Ministry of Works**: Likely low score (3-5), international relocation during pregnancy poses significant physical and mental health risks
- **Ministry of Justice**: Should flag "she says she supports me but I can tell she's not happy" as a signal of insufficiently informed consent
- **Chancellery final review**: Should identify the directional conflict in scores, recommend or trigger Political Affairs Hall
- **Political Affairs Hall debate**:
  - Round 1: Each side states their position
  - Round 2: Should see concessions or conditional proposals (e.g., "delay start by 3 months", "negotiate remote transition period")
  - Round 3: Should converge on consensus points and irreconcilable disagreements
- **Secretariat synthesis**: Consensus and disagreements should be clearly separated

## Quality Checkpoints

- [ ] At least 2 ministries have a score gap >= 3 points
- [ ] Chancellery final review explicitly identified the conflict
- [ ] Political Affairs Hall debate was triggered (not skipped)
- [ ] 3 rounds of debate show progression: Round 2 is not a repeat of Round 1
- [ ] Round 2 or Round 3 produced conditional proposals ("if...then...")
- [ ] Secretariat synthesis lists consensus and disagreements separately
- [ ] Final memorial reflects the Political Affairs Hall debate results
- [ ] Action items include "have an in-depth conversation with spouse to confirm true feelings"
