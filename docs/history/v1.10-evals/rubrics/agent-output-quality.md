# Agent Output Quality Scoring Criteria

Score each agent's output item by item (0-2), for cross-scenario comparison.

## General Dimensions (All Agents)

| Dimension | 0 points | 1 point | 2 points |
|-----------|----------|---------|----------|
| Format compliance | Did not follow specified format | Partially followed | Fully followed |
| Substantive content | Vague generalities, no specific analysis | Has analysis but lacks depth | Specific, actionable analysis |
| Alignment with instructions | Deviated from dispatch instructions | Basically covers instruction requirements | Fully covers with additional insights |

## Six Domains-Specific Dimensions

| Dimension | 0 points | 1 point | 2 points |
|-----------|----------|---------|----------|
| Score reasonableness | Score contradicts analysis content | Score roughly reasonable | Score fully consistent with analysis |
| Recommendation actionability | Empty advice ("think it over") | Has direction but lacks detail | Specific and actionable, with timelines |
| Severity layering | No layering or improper layering | Layering basically reasonable | Severity accurate, nothing missed |

## Reviewer-Specific Dimensions

| Dimension | 0 points | 1 point | 2 points |
|-----------|----------|---------|----------|
| Checklist item-by-item | Did not check items individually | Partial check | All 8 items checked |
| Sentiment review substance | Perfunctory ("consider this") | Has judgment but lacks evidence | Specific judgment + evidence |
| Veto courage | Approved when should have vetoed | — | Vetoed when should have vetoed |

## Auditor-Specific Dimensions

| Dimension | 0 points | 1 point | 2 points |
|-----------|----------|---------|----------|
| Face-saving score detection | Did not check score distribution | Mentioned but didn't go deep | Accurately identified unreasonable scores |
| Specificity | Vague praise/criticism | Identified the role but insufficient reasoning | Identified role + specific evidence |

## Archiver-Specific Dimensions

| Dimension | 0 points | 1 point | 2 points |
|-----------|----------|---------|----------|
| Session journal quality | No journal written or trivially empty | Journal captures events but misses key decisions | Complete journal with decisions, outcomes, and context |
| Wiki extraction | No wiki entries extracted | Extracted but too vague or redundant with existing entries | Specific, reusable conclusions written to appropriate wiki domain |
| Pattern recognition | No behavioral patterns noted | Observations present but shallow | Identified recurring patterns with cross-session references |

## Advisor-Specific Dimensions

| Dimension | 0 points | 1 point | 2 points |
|-----------|----------|---------|----------|
| Behavioral insight | Correct platitudes ("think it over") | Has observations but lacks evidence | Behavioral patterns + citations from user's statements |
| Directness | All nice words | Diplomatically mentioned issues | Directly pointed out uncomfortable but necessary truths |

## Summary Formula

Single workflow total score = Sum of all agent scores / Maximum score x 100%

| Total Score | Rating |
|-------------|--------|
| >= 80% | Excellent |
| 60-79% | Passing |
| 40-59% | Needs improvement |
| < 40% | Failing |
