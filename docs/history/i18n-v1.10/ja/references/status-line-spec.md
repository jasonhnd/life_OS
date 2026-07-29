---
spec_id: status-line-spec.v1
description: Life OS subagent の 8 enum status line 出力契約。ばらばらな状態表示を grep しやすい先頭行フォーマットへ統一する。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md
introduced_in: v1.8.7
referenced_by:
  - SKILL.md (E9 HARD RULE)
  - agents/auditor.md (Mode 8 status line verification)
  - agents/*.md (per-agent Status Output section)
---

# Status Line Specification v1

すべての `agents/*.md` subagent は、可視出力の最初の行として **status line** を出力しなければならない。status line は閉じた 8 enum keyword と canonical emoji を使い、agent id の後に短い説明を付けられる。

## Output Contract

subagent 出力の最初の非空行は次の形式に一致しなければならない：

```text
<emoji> <status> · <agent-id> · <one-line description>
```

各フィールド：

- `<emoji>` は status に対応する canonical emoji。
- `<status>` は下表の 8 enum keyword のいずれか。
- `<agent-id>` は subagent の `name:` frontmatter 値。例：`archiver`、`retrospective`、`memory-keeper`。
- `<one-line description>` は自由テキスト。現在のステップを 100 文字程度以内で説明する。

1 回の invocation 内で状態が複数回変わる場合、それぞれ新しい status line を出力する。例：起動時は `starting`、長い読み取りや reasoning 中は `evaluating`、具体的な成果物の後は `acted`。

## The 8 Statuses

| Status | Emoji | Semantics | Typical use |
|--------|-------|-----------|-------------|
| `starting` | 🚀 | subagent が開始した；launch 後の最初の動作 | すべての subagent invocation の先頭行 |
| `evaluating` | 🔍 | 読み取り、context 構築、reasoning 中 | 長い step、検索、検査 |
| `acted` | ✅ | 具体的な成果物を出した | phase 完了、plan 出力、write 完了 |
| `skipped` | ⏭️ | 正当な no-op | 関連 signal なし、候補なし、条件不成立 |
| `escalated` | ⚖️ | より上位の権限へ渡した | REVIEWER veto、COUNCIL debate、user approval |
| `awaiting_user` | 🟡 | 明示的な user input 待ち | approval gate、override decision |
| `failed` | ❌ | 完了できない | tool failure、必須 file 欠落、blocking spec violation |
| `silent_pass` | 🟢 | user に出す価値が低い clean pass | auditor clean pass、関連 Cortex signal なし |

## Examples

```text
🚀 starting · archiver · fresh adjourn invocation, trigger 1, Phase 1-5 starting
🔍 evaluating · archiver · Phase 0 runtime readiness
✅ acted · archiver · Phase 0 complete, hook layer retired and inline enforcement active
🔍 evaluating · archiver · Phase 2 knowledge extraction
✅ acted · archiver · Phase 2 complete: 3 wiki, 2 SOUL, 1 concept
⏭️ skipped · archiver · Phase 3 light sleep, no significant patterns
✅ acted · archiver · Phase 4 git push complete, commit abc1234
🚀 starting · memory-keeper · Phase 5 invoked by archiver
✅ acted · memory-keeper · 3 candidates, 1 merged, 2 appended, gotchas.md total 17
✅ acted · archiver · all five phases complete, completion checklist follows
```

ROUTER と AUDITOR は `^🚀 starting` で launch、`^❌ failed` で failure、`^🟡 awaiting_user` で user 待ちの作業を grep できる。

## Per-Agent Semantics

各 `agents/*.md` file は `## Status Output (E9)` section を持ち、その agent における 8 status の意味を宣言しなければならない。template：

```markdown
## Status Output (E9 · v1.8.7)

| Status | When emitted | Example description |
|--------|--------------|---------------------|
| `starting` | First line after launch | "fresh invocation, trigger N, mode M" |
| `evaluating` | Agent-specific long-running steps | "reading source files" |
| `acted` | Deliverable produced | "planning document emitted" |
| `skipped` | Legitimate no-op | "no candidates found" |
| `escalated` | Handing off | "requires reviewer veto loop" |
| `awaiting_user` | Approval gate | "waiting for explicit override" |
| `failed` | Blocking failure | "required file missing" |
| `silent_pass` | Clean pass | "no violations found" |
```

その agent に適用されない status は、省略せず `N/A · <reason>` と宣言する。

## Validation

AUDITOR Mode 8 は次を検証する：

| Check | Description | Failure class |
|-------|-------------|---------------|
| M8-1 | すべての subagent transcript が形式どおりの `^🚀 starting` で始まる | `F3 SCHEMA_FAILURE` |
| M8-2 | すべての status line が 8 enum keyword のいずれかを使う | `F4 SCOPE_FAILURE` |
| M8-3 | emoji と status keyword の対応が表と一致する | `F3 SCHEMA_FAILURE` |
| M8-4 | agent の Status Output section が 8 status すべてを宣言する | `F3 SCHEMA_FAILURE` |
| M8-5 | multi-step invocation が重要な transition で status line を出す | `F8 SILENT_FAILURE` |
| M8-6 | `failed` が failure class を含む、または参照する | `F10 RESPONSIBILITY_FAILURE` |

## Anti-Patterns

| Anti-pattern | Why bad | Correct form |
|--------------|---------|--------------|
| `The archiver has completed Phase 1` | enum ではなく grep しにくい | `✅ acted · archiver · Phase 1 complete: N decisions archived` |
| `🚀 Started!` | agent id と説明がない | `🚀 starting · archiver · fresh adjourn invocation` |
| `evaluating` から始める | M8-1 違反 | 必ず最初に `🚀 starting` を出す |
| `thinking` を発明する | enum closure を壊す | 8 status のいずれかを使うか RFC を出す |

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.8 E9 + DR-11
- `references/conscious-patrol-spec.md`
- `agents/auditor.md` Mode 8
