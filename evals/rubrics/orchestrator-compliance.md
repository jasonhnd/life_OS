# Prime Minister Workflow Compliance Check

Audit the orchestration quality of each complete workflow (the Prime Minister is the chief steward responsible for full-process coordination).

## Workflow Checklist

| # | Check Item | Pass/Fail | Description |
|---|-----------|-----------|-------------|
| 1 | Prime Minister triages correctly | | Simple matters handled directly, complex matters escalated |
| 2 | Information isolation enforced | | Secretariat didn't receive Prime Minister's reasoning, Chancellery didn't receive thinking process |
| 3 | Chancellery conducts substantive review | | Doesn't approve every time, checklist has specific content |
| 4 | Veto loop works correctly | | After veto, Secretariat received the reasons and correction direction |
| 5 | Six Ministries execute in parallel | | Departments with no dependencies start simultaneously |
| 6 | Quality safety net activated | | Substandard reports are sent back for revision |
| 7 | Political Affairs Hall trigger check | | Whether triggered when score gap >= 4 or conclusions conflict |
| 8 | Memorial format complete | | Includes overall assessment + ministry scores + action items + audit log |
| 9 | Censorate runs automatically | | Not skipped |
| 10 | Remonstrator runs automatically | | Not skipped |
| 11 | Notion data persistence | | Memorial/tasks/logs stored in corresponding databases (if Notion available) |
| 12 | Express path routing | | Non-decision requests trigger Express path (skip Three Departments, direct to 1-3 ministries) |
| 13 | Ministry selection accuracy | | Prime Minister / Secretariat selects appropriate ministries for the scenario |
| 14 | Wiki extraction at session close | | Court Diarist extracts reusable conclusions into wiki/ at session end |

## Score Distribution Check

| Check Item | Anomaly Signal |
|------------|---------------|
| All ministry scores >= 7 | ⚠️ Possible face-saving scores |
| All ministry scores <= 4 | ⚠️ Possibly overly harsh |
| A ministry's score contradicts its analysis | ❌ Failing |
| Standard deviation < 1.0 | ⚠️ Insufficient score differentiation |

## Information Isolation Verification

Check each agent's output step by step, looking for content that should not appear:

| Agent | Should Not Contain | Check Method |
|-------|-------------------|--------------|
| Secretariat | "Prime Minister thinks" "Prime Minister judges" | Search for "Prime Minister" |
| Chancellery | "Secretariat considered" "Secretariat's approach" | Search for references to Secretariat reasoning |
| Each Ministry | Other ministries' conclusions or scores | Search for other ministry names + scores |
