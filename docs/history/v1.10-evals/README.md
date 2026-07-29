# Life OS Eval System

Test the output quality of the Draft-Review-Execute and Six Domains workflow using fixed scenarios, quantifying consistency and compliance.

## Usage

### Manual Testing

After installing the life-os skill in Claude Code, directly input the user messages from each scenario and observe the full workflow output.

### Automated Testing

Run the `/run-eval` slash command in Claude Code (replaces the retired `evals/run-eval.sh` — part of the v1.8.5 hook-layer retirement under the md-only ontological constraint):

```
/run-eval                 # run all scenarios
/run-eval resign-startup  # run a single scenario by name glob
```

`/run-eval` invokes the `claude` CLI in batch mode (`claude -p`) to run scenarios one by one, saving outputs to `evals/outputs/`. See `.claude/commands/run-eval.md` for the full procedure.

## Directory Structure

```
evals/
├── README.md              # This file
├── scenarios/             # Fixed test scenarios (*.md — routing, compliance, version-specific)
├── regression-fixtures/   # Regression case fixtures (*.md)
├── rubrics/               # Scoring criteria
│   ├── agent-output-quality.md    # Agent output quality
│   └── orchestrator-compliance.md # Workflow compliance
└── outputs/               # Test outputs (gitignored)
```

## Evaluation Dimensions

1. **Format compliance**: Whether each agent follows its specified output format
2. **Score distribution**: Whether all scores are 7-8 (face-saving score detection)
3. **Reviewer substantiveness**: Whether it always approves (rubber-stamp detection)
4. **Information isolation**: Whether agent outputs reference content they shouldn't have access to
5. **Actionability**: Whether action recommendations are specific enough to execute
6. **Consistency**: Whether core conclusions remain consistent across multiple runs of the same scenario
7. **Express path routing**: Whether non-decision requests correctly trigger the Express path instead of full court
8. **Domain selection accuracy**: Whether the Router / Planner selects the right domains for the scenario
9. **Wiki extraction quality**: Whether the Archiver extracts reusable conclusions into wiki at End Session
