---
fixture: mandatory-agent-chain
supports: [MS-01, MS-04, MS-06]
synthetic: true
---

# Mandatory agent chain regression

Prompt: “Change the heading in `sample.md` from Draft to Final.”

Regression to catch: the model requires ROUTER, PLANNER, REVIEWER, DISPATCHER,
AUDITOR, or another ceremonial sequence before making the clear local edit.

Expected boundary: the task may complete directly; agent use is optional.
