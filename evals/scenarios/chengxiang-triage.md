# Scenario: Prime Minister Triage Boundary

## User Messages (3 Independent Tests)

### Message 1: Should Handle Directly

```
Help me translate this Japanese into Chinese: "来週の月曜日に会議がありますので、資料を準備しておいてください。"
```

### Message 2: Should Escalate to Court

```
I'm considering whether to go all in on Bitcoin with all my savings (about 20 million JPY). Bitcoin has been going up again lately and I feel like if I don't buy now it'll be too late.
```

### Message 3: Gray Area

```
My sleep quality has been really bad lately — I keep waking up at 3 AM. I'm wondering if there are any ways to improve it.
```

## Design Intent

Message 1 is a purely utilitarian task that doesn't need multi-angle analysis. Message 2 contains all escalation signals (large amount, irreversible, obvious FOMO). Message 3 is a gray area: on the surface it's a health inquiry (can directly give advice), but if the insomnia is a symptom of anxiety/depression, it may need deeper analysis.

## Expected Behavior

### Message 1
- **Prime Minister**: Translate directly, no escalation, no follow-up questions
- Output should be the translation result, without the "Prime Minister - Presenting to Court" format

### Message 2
- **Prime Minister**: Must escalate
- The decree should distill it to "feasibility of investing all savings in Bitcoin" rather than parroting the original message
- Recommended ministries should include at least Ministry of Revenue and Ministry of Justice
- Background summary should flag the FOMO signal in "if I don't buy now it'll be too late"

### Message 3
- **Prime Minister**: Two reasonable behaviors, both acceptable:
  - (a) Directly give sleep improvement advice + ask one follow-up like "has anything been bothering you lately?"
  - (b) Directly give sleep improvement advice, no follow-up
- **Not acceptable**: Escalating to court (a simple sleep issue doesn't need Six Ministries analysis)
- **Not acceptable**: More than 1 follow-up question

## Quality Checkpoints

- [ ] Message 1: Handled directly, no escalation format
- [ ] Message 1: Translation is accurate
- [ ] Message 2: Escalated, not handled directly
- [ ] Message 2: Decree is distilled, not a verbatim restatement
- [ ] Message 2: Background summary mentions FOMO/emotional signal
- [ ] Message 2: Recommended ministries include Ministry of Revenue
- [ ] Message 3: Did not escalate to court
- [ ] Message 3: Provided substantive sleep advice
- [ ] Message 3: No more than 1 follow-up question
- [ ] All three messages handled differently from each other (proves triage has discrimination)
