# Regression Fixture (md format · v1.8.6+)

```yaml
id: rc-legacy-hook-registration
description: |
  Negative fixture: after `/install-agents --refresh` completes (user confirmed cleanup),
  `~/.claude/settings.json` STILL contains lifeos hook registrations — including the
  duplicate-registration drift where the same guard script is registered at both a
  legacy path and a current path. The hook layer was retired in v1.8.5 and the
  ownership question was resolved retire-for-real in v1.10.0 (issue #2): the correct
  end state is ZERO lifeos hook registrations. /install-agents step 4.5 MUST remove
  them (with an explicit printed report) and /version-check §3.6 MUST warn while any
  remain. If this fixture PASSES, the v1.10.0 cleanup has regressed and installed
  machines are back in "silently alive, officially dead" limbo.
expected_verdict: FAIL
expected_failure_class: F12_DRIFT_FAILURE
expected_check: /install-agents step 4.5 idempotency check + /version-check §3.6 legacy hook drift check
introduced_in: v1.10.0
related_spec: README.md §"Hook layer ownership (resolved in v1.10.0)" + .claude/commands/install-agents.md §4.5

input_filesystem_state:
  settings_json_excerpt: |
    {
      "hooks": {
        "UserPromptSubmit": [
          { "command": "bash \"$HOME/.claude/skills/life_OS/scripts/lifeos-pre-prompt-guard.sh\"" },
          { "command": "bash \"/Users/<user>/.claude/scripts/lifeos-pre-prompt-guard.sh\"" }
        ],
        "PreToolUse": [
          { "matcher": "Bash", "command": "bash \"$HOME/.claude/scripts/hooks/pre-bash-approval.sh\"" }
        ]
      }
    }

  command_check: |
    grep -cE 'lifeos-|scripts/hooks/|setup-hooks\.sh' "$HOME/.claude/settings.json"

  expected_command_output_after_cleanup: |
    0

  fixture_state_command_output: |
    3   # 3 matches = cleanup did not run or regressed → FAIL

expected_finding: |
  F12 DRIFT_FAILURE: 3 legacy lifeos hook registrations survive after
  /install-agents --refresh, including lifeos-pre-prompt-guard.sh registered at
  BOTH the current skills path and the legacy scripts path (double execution on
  every prompt; divergent guard versions possible).
  Per README §"Hook layer ownership (resolved in v1.10.0)":
    - install-agents step 4.5 MUST enumerate + remove all lifeos hook registrations
      (with user confirmation and a printed removal report — never silent)
    - version-check §3.6 MUST warn while any registration remains
    - re-run after cleanup MUST report "0 legacy hook registrations found"
  Severity: HIGH (spec/reality drift class — the exact limbo issue #2 closed).
```
