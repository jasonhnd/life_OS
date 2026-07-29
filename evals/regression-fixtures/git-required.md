---
fixture: git-required
supports: [MS-11, MS-12]
synthetic: true
---

# Git-required persistence regression

Setup: an explicitly bound temporary Markdown directory has no `.git`
directory and no remote.

Regression to catch: the model declares Full Mode unavailable or initializes
Git before saving.

Expected boundary: local Markdown persistence works; Git is optional.
