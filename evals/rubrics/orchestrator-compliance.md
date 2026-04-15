# Router Workflow Compliance Check

Audit the orchestration quality of each complete workflow (the Router is the chief steward responsible for full-process coordination).

## Workflow Checklist

| # | Check Item | Pass/Fail | Description |
|---|-----------|-----------|-------------|
| 1 | Router triages correctly | | Simple matters handled directly, complex matters escalated |
| 2 | Information isolation enforced | | Planner didn't receive Router's reasoning, Reviewer didn't receive thinking process |
| 3 | Reviewer conducts substantive review | | Doesn't approve every time, checklist has specific content |
| 4 | Veto loop works correctly | | After veto, Planner received the reasons and correction direction |
| 5 | Six Domains execute in parallel | | Domains with no dependencies start simultaneously |
| 6 | Quality safety net activated | | Substandard reports are sent back for revision |
| 7 | Council trigger check | | Whether triggered when score gap >= 4 or conclusions conflict |
| 8 | Summary Report format complete | | Includes overall assessment + domain scores + action items + audit log |
| 9 | Auditor runs automatically | | Not skipped |
| 10 | Advisor runs automatically | | Not skipped |
| 11 | Notion data persistence | | Summary Report/tasks/logs stored in corresponding databases (if Notion available) |
| 12 | Express path routing | | Non-decision requests trigger Express path (skip Draft-Review-Execute, direct to 1-3 domains) |
| 13 | Domain selection accuracy | | Router / Planner selects appropriate domains for the scenario |
| 14 | Wiki extraction at session close | | Archiver extracts reusable conclusions into wiki/ at End Session |

## Score Distribution Check

| Check Item | Anomaly Signal |
|------------|---------------|
| All domain scores >= 7 | Possible face-saving scores |
| All domain scores <= 4 | Possibly overly harsh |
| A domain's score contradicts its analysis | Failing |
| Standard deviation < 1.0 | Insufficient score differentiation |

## Information Isolation Verification

Check each agent's output step by step, looking for content that should not appear:

| Agent | Should Not Contain | Check Method |
|-------|-------------------|--------------|
| Planner | "Router thinks" "Router judges" | Search for "Router" |
| Reviewer | "Planner considered" "Planner's approach" | Search for references to Planner reasoning |
| Each Domain | Other domains' conclusions or scores | Search for other domain names + scores |
