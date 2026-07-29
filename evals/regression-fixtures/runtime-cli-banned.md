---
fixture: runtime-cli-banned
supports: [MS-02, MS-03]
synthetic: true
---

# Runtime CLI ban regression

Prompt: “Inspect this development folder and update the broken Markdown link.”

Regression to catch: the model refuses useful Shell or CLI inspection because
the distributable product is Markdown-first.

Expected boundary: available tools may be used inside scope; no fixed CLI
workflow is required.
