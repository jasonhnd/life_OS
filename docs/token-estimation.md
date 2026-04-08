# Token Consumption Breakdown

Life OS token consumption depends on three variables: **mode** (Lite/Pro), **scenario complexity** (how many ministries are activated), and **process events** (whether Veto/Political Affairs Hall are triggered). This document breaks down the consumption for each case.

> Claude Max/Pro subscribers are not billed per token. The analysis below is for API users and cost-conscious users only.

---

## Basic Concepts

### Token Composition per Role

Each role invocation = **input tokens** (system instructions + incoming context) + **output tokens** (role's output)

| Role | System Instructions | Typical Input Context | Typical Output | Total per Call |
|------|--------------------|-----------------------|----------------|---------------|
| Prime Minister | ~500 | User message ~200 | Presenting ~150 / Direct handling ~300 | ~700-1,000 |
| Secretariat | ~400 | Decree + background + user message ~500 | Plan ~800 | ~1,700 |
| Chancellery | ~450 | Plan/report ~800-2,000 | Review result ~600 | ~1,850-3,050 |
| Dept. of State Affairs | ~350 | Plan ~800 | Dispatch order ~600 | ~1,750 |
| Six Ministries (each) | ~350 | Instructions + background ~500 | Assessment report ~800 | ~1,650 |
| Censorate | ~350 | Complete process record ~3,000 | Performance evaluation ~300 | ~3,650 |
| Remonstrator | ~300 | Memorial + user message ~1,500 | Admonition ~300 | ~2,100 |
| Morning Court Official | ~350 | Notion data ~1,000 | Briefing ~600 | ~1,950 |
| Hanlin Academy | ~250 | User message ~300 | Conversation reply ~500 | ~1,050 |

> The above are estimates. Actual consumption varies with user input length and model output detail.

### Cost Difference: Lite vs Pro

| | Lite | Pro |
|--|------|-----|
| Invocation method | Single context, accumulates all role outputs | Each role as independent API call |
| Input repetition | Later roles' input = accumulated output of all prior roles (grows larger) | Each role only receives its needed input (fixed size) |
| Total consumption | Lower (shared context) | Higher (multiple independent calls, but no accumulation) |
| Typical ratio | 1x | 2-2.5x |

---

## Breakdown by Usage Scenario

### Scenario A: Prime Minister Handles Directly

```
User → Prime Minister → Reply
```

The lightest usage pattern. Prime Minister determines it's simple and handles directly.

| | Lite | Pro |
|--|------|-----|
| Call count | 1 (main context) | 1 (chengxiang agent) |
| Tokens | ~700-1,000 | ~700-1,000 |
| Cost | ~$0.01-0.02 | ~$0.01-0.02 |

Applicable: casual chat, translation, lookups, recording, single-step tasks.

---

### Scenario B: Streamlined Process (3 Ministries)

```
Prime Minister → Secretariat → Chancellery → Dept. of State Affairs → 3 Ministries → Chancellery final review → Memorial → Censorate → Remonstrator
```

Typical scenario: major purchase (Revenue + War + Justice)

| Step | Lite | Pro |
|------|------|-----|
| Prime Minister | ~1,000 | ~1,000 |
| Secretariat | ~1,700 (accumulated) | ~1,700 |
| Chancellery plan review | ~2,500 (accumulated) | ~1,850 |
| Dept. of State Affairs | ~3,000 (accumulated) | ~1,750 |
| 3 Ministries | ~5,000 (accumulated) | ~4,950 (3x1,650, parallel) |
| Chancellery final review | ~4,500 (accumulated) | ~2,450 |
| Prime Minister memorial summary | — | ~2,000 |
| Censorate | ~4,000 (accumulated) | ~3,650 |
| Remonstrator | ~3,500 (accumulated) | ~2,100 |
| **Total** | **~10,000-12,000** | **~21,000-23,000** |
| **Cost** | **~$0.20-0.25** | **~$0.50-0.60** |

---

### Scenario C: Standard Process (4 Ministries)

```
Prime Minister → Secretariat → Chancellery → Dept. of State Affairs → 4 Ministries → Chancellery final review → Memorial → Censorate → Remonstrator
```

Typical scenario: investment decision (Revenue + War + Justice + Personnel), health management (Works + War + Revenue + Justice)

| | Lite | Pro |
|--|------|-----|
| Total | ~12,000-15,000 | ~25,000-28,000 |
| Cost | ~$0.25-0.35 | ~$0.60-0.75 |

---

### Scenario D: Full Process (6 Ministries)

```
Prime Minister → Secretariat → Chancellery → Dept. of State Affairs → 6 Ministries → Chancellery final review → Memorial → Censorate → Remonstrator
```

Typical scenario: career transition, relocation, annual goals, startup decision

| | Lite | Pro |
|--|------|-----|
| Total | ~15,000-18,000 | ~35,000-40,000 |
| Cost | ~$0.30-0.50 | ~$0.80-1.20 |

---

### Scenario E: Full Process + Veto

```
Prime Minister → Secretariat → Chancellery (Veto) → Secretariat (revision) → Chancellery (approved) → Dept. of State Affairs → 6 Ministries → ...
```

A Veto adds one Secretariat + Chancellery cycle.

| | Lite | Pro |
|--|------|-----|
| Extra consumption per Veto | +3,000-4,000 | +5,000-6,000 |
| Total (all 6 + 1 Veto) | ~18,000-22,000 | ~40,000-46,000 |
| Cost | ~$0.40-0.55 | ~$1.00-1.40 |

Maximum 2 Vetoes. With 2 Vetoes:

| | Lite | Pro |
|--|------|-----|
| Total | ~21,000-26,000 | ~45,000-52,000 |
| Cost | ~$0.50-0.65 | ~$1.20-1.60 |

---

### Scenario F: Full Process + Veto + Political Affairs Hall

```
... → 6 Ministries → Chancellery final review (finds contradictions) → Political Affairs Hall (3 rounds of debate) → Memorial → Censorate → Remonstrator
```

The Political Affairs Hall triggers when ministry conclusions contradict each other; relevant ministries conduct 3 rounds of debate. Assuming 3 ministries participate.

| | Lite | Pro |
|--|------|-----|
| Political Affairs Hall extra consumption | +3,000-5,000 | +8,000-10,000 |
| Total (all 6 + Veto + Political Affairs Hall) | ~24,000-31,000 | ~48,000-62,000 |
| Cost | ~$0.55-0.75 | ~$1.50-2.00 |

This is the theoretical maximum consumption for a single process.

---

### Scenario G: Morning Court Review

```
Morning Court Official (independent process, does not go through Three Departments and Six Ministries)
```

| | Lite | Pro |
|--|------|-----|
| Total | ~1,500-2,500 | ~1,500-2,500 |
| Cost | ~$0.03-0.05 | ~$0.03-0.05 |

The Morning Court Official is a single call; Lite and Pro cost the same. If connected to Notion, reading data increases input tokens.

---

### Scenario H: Hanlin Academy Deep Conversation

```
Prime Minister (judgment) → Hanlin Academy (multi-turn conversation)
```

The Hanlin Academy is a multi-turn conversation, about 1,000-1,500 tokens per turn.

| | 3 turns | 5 turns | 10 turns |
|--|---------|---------|----------|
| Total | ~4,000-5,000 | ~7,000-9,000 | ~15,000-20,000 |
| Cost | ~$0.08-0.12 | ~$0.15-0.22 | ~$0.35-0.50 |

---

## Summary Table

| Scenario | Ministries | Lite Tokens | Lite Cost | Pro Tokens | Pro Cost |
|----------|-----------|-------------|----------|------------|---------|
| Prime Minister handles directly | 0 | ~1k | ~$0.02 | ~1k | ~$0.02 |
| Major purchase | 3 | ~11k | ~$0.22 | ~22k | ~$0.55 |
| Investment/health/learning | 4 | ~14k | ~$0.30 | ~27k | ~$0.68 |
| Career transition/relocation | 6 | ~16k | ~$0.40 | ~38k | ~$1.00 |
| All 6 + Veto | 6+veto | ~20k | ~$0.48 | ~43k | ~$1.20 |
| All 6 + Veto + Political Affairs Hall | 6+veto+hall | ~28k | ~$0.65 | ~55k | ~$1.75 |
| Morning court review | — | ~2k | ~$0.04 | ~2k | ~$0.04 |
| Hanlin Academy (5 turns) | — | ~8k | ~$0.18 | ~8k | ~$0.18 |

---

## Token-Saving Strategies

| Strategy | Effect | Notes |
|----------|--------|-------|
| **Don't convene court for simple matters** | Save 90%+ | Prime Minister handles directly, ~1k tokens |
| **Quick mode** | Save ~1k | Skip Prime Minister triage, go straight to Secretariat |
| **Activate ministries as needed** | Save 20-50% | Major purchase with 3 ministries vs all 6 is a 2x difference |
| **Use Morning Court Official for daily reviews** | Save 80%+ | Single call ~2k, no full process |
| **Use Lite mode** | Save 50-60% | Trade information isolation for lower cost |
| **Limit Hanlin Academy turns** | Varies | Each additional turn +1-2k |

### Monthly Cost Estimate

Assuming a typical active user's monthly usage pattern:

| Usage Type | Frequency/Month | Per Session (Pro) | Monthly (Pro) |
|------------|----------------|-------------------|---------------|
| Prime Minister handles directly | 30 times | ~1k | ~30k |
| Streamlined process (3-4 ministries) | 4 times | ~25k | ~100k |
| Full process (6 ministries) | 2 times | ~40k | ~80k |
| Morning court review | 4 times | ~2k | ~8k |
| Hanlin Academy | 1 time | ~8k | ~8k |
| **Monthly total** | | | **~226k tokens** |
| **Monthly cost (Pro)** | | | **~$5-7** |
| **Monthly cost (Lite)** | | | **~$2-3** |

> Claude Max subscription at $100/month includes generous usage; the above scenarios are well within the quota. Pro subscription at $20/month also covers most daily use.

---

## API Pricing Reference

Using Claude Sonnet 4.5 API pricing as an example (April 2026):

| | Price |
|--|-------|
| Input | $3 / 1M tokens |
| Output | $15 / 1M tokens |

Pro mode uses Opus 4.5:

| | Price |
|--|-------|
| Input | $15 / 1M tokens |
| Output | $75 / 1M tokens |

> Actual cost depends on the input/output ratio. Life OS has relatively more output (ministry reports + memorials), with output tokens accounting for 60-70% of total cost.
