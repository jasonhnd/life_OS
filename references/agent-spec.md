---
title: Optional Agent Template Reference
status: reference
authoritative: false
runtime_authority: SKILL.md
introduced_in: v1.11.0
---

# Optional Agent Templates

Agent files are reusable perspectives, not a closed role registry or required
execution graph.

## Suggested Template Shape

```yaml
---
id: example
status: optional-template
authoritative: false
runtime_authority: SKILL.md
purpose: One sentence describing the perspective.
---
```

A useful template can describe:

- its purpose;
- situations where the perspective adds value;
- situations where direct work is better;
- suggested inputs;
- useful questions or analytical lenses;
- possible output shapes;
- relevant safety or privacy considerations.

These are quality prompts, not required headings.

## Runtime Use

The model may:

- use no template;
- use one template;
- combine several templates;
- adapt a template to the task;
- create a task-specific role not present in `agents/`.

Every role inherits the user's authorized scope, data boundary, privacy
constraints, and completion standard. It should return conclusions and evidence
useful to the parent task rather than a status line, compliance receipt, or
proof-of-invocation file.

Templates must not require their own invocation, fixed tools, fixed phases,
nested launches, isolated files the host cannot actually guarantee, or writes
unrelated to the requested outcome.
