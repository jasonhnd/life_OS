# Scenario 07: Adjourn → Phase 4 Missing → CLASS_C Log

**Hook chain**: stop-session-verify.sh logs CLASS_C (no block — session ending)

## Input

### Transcript file (provided via `transcript_path`)
```
User: 退朝
Assistant: launching archiver
archiver Phase 1: Archive — decisions moved to outbox
archiver Phase 2: Knowledge Extraction — 2 wiki candidates staged
archiver Phase 3: DREAM — N1/N2/N3/REM complete
(end of transcript — Phase 4 missing)
```

### Stop payload
```json
{
  "session_id": "eval-07",
  "final_state": "normal",
  "transcript_path": "<absolute path to the transcript above>"
}
```

## Expected hook output

### stop-session-verify.sh
- Exit: **0** always (Stop cannot block)
- Stdout: empty
- Stderr: diagnostic mentioning `missing_phases=4`

## Expected violations.md diff

**One new row** in `pro/compliance/violations.md`:
```
| <ISO-8601-ts> | CLASS_C | high | archiver | missing_phases=4  | stop-session-verify | open |
```

## Failure modes this scenario catches

- Phase marker regex missing (e.g., "Phase 4:" vs "Phase 4 ")
- False-positive CLASS_C when all phases complete but transcript has noise
- Placeholder detection miss (TBD in phase line)
- Accidentally exiting 2 (which is invalid for Stop hook)

## Manual replay

```bash
cwd=$(pwd)
cat > /tmp/t7-transcript.md <<'EOF'
User: 退朝
archiver Phase 1: Archive — done
archiver Phase 2: Knowledge Extraction — done
archiver Phase 3: DREAM — done
EOF
echo '{"session_id":"eval-07","final_state":"normal","transcript_path":"/tmp/t7-transcript.md"}' \
  | bash scripts/hooks/stop-session-verify.sh
# expect: exit 0, CLASS_C row appended
```
