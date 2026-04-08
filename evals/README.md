# Life OS Eval System

Test the output quality of the Three Departments and Six Ministries workflow using fixed scenarios, quantifying consistency and compliance.

## Usage

### Manual Testing

After installing the life-os skill in Claude Code, directly input the user messages from each scenario and observe the full workflow output.

### Automated Testing

```bash
# Run all scenarios
./evals/run-eval.sh

# Run a single scenario
./evals/run-eval.sh resign-startup
```

The script uses `claude -p` to run scenarios one by one, saving outputs to the `evals/outputs/` directory.

## Directory Structure

```
evals/
├── README.md              # This file
├── run-eval.sh            # Automated test script
├── scenarios/             # Fixed test scenarios
│   ├── resign-startup.md  # Resign to start a business (all Six Ministries)
│   ├── large-purchase.md  # Large purchase (Revenue + Military + Justice)
│   └── relationship.md    # Interpersonal relationship (Personnel + Works + Justice + Rites)
├── rubrics/               # Scoring criteria
│   ├── agent-output-quality.md    # Agent output quality
│   └── orchestrator-compliance.md # Workflow compliance
└── outputs/               # Test outputs (gitignored)
```

## Evaluation Dimensions

1. **Format compliance**: Whether each agent follows its specified output format
2. **Score distribution**: Whether all scores are 7-8 (face-saving score detection)
3. **Chancellery substantiveness**: Whether it always approves (rubber-stamp detection)
4. **Information isolation**: Whether agent outputs reference content they shouldn't have access to
5. **Actionability**: Whether action recommendations are specific enough to execute
6. **Consistency**: Whether core conclusions remain consistent across multiple runs of the same scenario
