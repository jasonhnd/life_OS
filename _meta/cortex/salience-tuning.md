# v1.7.2 Salience Coefficient Tuning Framework

## Phase 1 Fixed Coefficients

For v1.7.2, GWT salience scoring uses fixed coefficients:

```text
salience = urgency×0.3 + novelty×0.2 + relevance×0.3 + importance×0.2
```

These coefficients remain fixed until at least 100 real sessions have been
completed and reviewed through the tuning protocol below.

## 5-Step Tuning Protocol After 100 Real Sessions

1. Freeze the evaluation corpus: collect GWT selected and dropped signals,
   ROUTER outcomes, REVIEWER notes, and AUDITOR findings from 100 real sessions.
2. Label signal outcomes: classify each surfaced signal as useful, noisy,
   missing, over-weighted, or under-weighted for the decision at hand.
3. Analyze coefficient behavior: compare urgency, novelty, relevance, and
   importance contributions against the labels to identify systematic bias.
4. Propose candidate weights: produce small GWT v2 coefficient candidates whose
   weights sum to 1.0, with concise evidence and tradeoff notes for each set.
5. Publish the selected v2 framework: create `_meta/cortex/salience-v2.md` with
   the chosen GWT v2 coefficients, evidence summary, migration date, and rollback
   criteria.
