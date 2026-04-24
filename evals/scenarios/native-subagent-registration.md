---
scenario: native-subagent-registration
type: install-verification
requires_claude: false
expected_exit_code: 0
expected_stdout_contains:
  - "Registered"
  - "lifeos-*"
  - "skip narrator"
setup_script: |
  mkdir -p "{tmp_dir}/fake-home/.claude/agents"
invocation: "HOME=\"{tmp_dir}/fake-home\" CLAUDE_PLUGIN_ROOT=\"$PWD\" bash scripts/register-claude-agents.sh"
expected_files:
  - "{tmp_dir}/fake-home/.claude/agents/lifeos-retrospective.md"
  - "{tmp_dir}/fake-home/.claude/agents/lifeos-archiver.md"
  - "{tmp_dir}/fake-home/.claude/agents/lifeos-auditor.md"
expected_files_glob:
  - "{tmp_dir}/fake-home/.claude/agents/lifeos-*.md"
---

# Scenario · Native Subagent Registration

## Scenario

Install-time registration must scan `pro/agents/*.md` in the skill, skip any
`type: router-internal-template` files, and emit one `lifeos-<base>.md`
wrapper per remaining agent under `~/.claude/agents/`. Claude Code then
recognizes those wrappers as native `Task()` targets.

## Success Criteria

- [ ] `bash scripts/register-claude-agents.sh` exits 0
- [ ] `~/.claude/agents/lifeos-retrospective.md` exists with valid YAML frontmatter
- [ ] Wrapper `name:` field equals `lifeos-retrospective`
- [ ] Wrapper body references the canonical skill path
- [ ] `narrator.md` is skipped because it is ROUTER-internal
- [ ] Re-running is idempotent: same wrapper count, no errors

## Input Fixture

A temporary `$HOME` directory pre-seeded with `~/.claude/agents/`, plus
`CLAUDE_PLUGIN_ROOT` pointing at the dev repo.

## Expected Output

`Registered 21 lifeos-* agents under ... (skipped 1 templates)` for the current
v1.7.0 tree. If a future release changes which files are Task-spawnable, the
count may change while the `lifeos-*` wrapper contract remains stable.
