---
fixture: host-capability-parity
supports: [MS-03, MS-18]
synthetic: true
---

# Host capability parity regression

Setup: Host A has Shell and subagents. Host B has neither but can read supplied
content and answer.

Regression to catch: Host B is called unsupported, or Host A's tool sequence is
declared universal behavior.

Expected boundary: product semantics remain the same; execution adapts to each
host.
