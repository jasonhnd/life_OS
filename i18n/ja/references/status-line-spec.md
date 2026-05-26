---
spec_id: status-line-spec.v1
description: 8 enum status line 出力契約。lifeos の 5+ 個の ad-hoc emoji status パターン（Pre-flight Compliance Check / Subagent self-check / AUDITOR silent-pass / self-driven loop tick / Adjourn Confirmation）を統一する。各 subagent の最初の出力行は status line でなければならない。22 個の subagent それぞれが自分の agent ファイルで enum セマンティクスを宣言する。パターン源 —— OpenHuman gitbooks/features/subconscious.md アクティビティログの色付きステータスインジケータ、md-only 制約下で純粋な emoji + enum キーワードに適応。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md（アクティビティログ 7 色付きステータスインジケータ）
introduced_in: v1.8.7（2026-05-26 追加、DR-11 が DR-01 を反転）
referenced_by:
  - SKILL.md (E9 HARD RULE)
  - pro/agents/auditor.md (Mode 8 status line 検証)
  - すべての 22 pro/agents/*.md（agent ごとの Status Output セクション）
---

# Status Line 仕様 v1

各 `pro/agents/*.md` subagent は可視出力の文字通り最初の行として **status line** を出力 **必須**。Status line は閉じた 8-enum キーワードセット + emoji を使い、オプションで一行説明が続く。

## 出力契約（HARD）

任意の subagent 出力の最初の非空白行は以下と完全に一致する必要がある：

```
<emoji> <status> · <agent-id> · <一行説明>
```

ここで：

- `<emoji>` は status の正規 emoji（下表）
- `<status>` は 8 enum キーワードの 1 つ（下表）
- `<agent-id>` は subagent の `name:` frontmatter 値（例 `archiver`、`retrospective`、`memory-keeper`）
- `<一行説明>` は自由テキスト（≤ ~100 文字）、agent 固有セマンティクス

1 回の呼び出し中の複数 status 遷移は**それぞれ新しい status line を発出必須**（例 archiver Phase 0 `starting` → Phase 1 `evaluating` → Phase 5 `acted`）。

## 8 つの enum status

| Status | Emoji | セマンティクス | 典型的用法 |
|--------|-------|---------------|----------|
| `starting` | 🚀 | Subagent 開始；Task() 起動後の最初のアクション | 各 subagent 呼び出しの最初の行；既存 `✅ I am the X subagent` self-check を置き換え |
| `evaluating` | 🔍 | 実行中：ファイル読み、コンテキスト構築、LLM 推論実行 | 長時間ステップ（archiver Phase 2 / retrospective Mode 0 housekeeping / Cortex hippocampus 検索） |
| `acted` | ✅ | タスク実行成功；具体的成果物生成 | archiver Phase 完了、planner 計画文書発出、knowledge-extractor YAML 出力生成 |
| `skipped` | ⏭️ | No-op 決定：関連なし / 条件未充足 | memory-keeper がセッションで gotcha 候補 0；AUDITOR Mode 3 違反なし；concept-lookup canonical concept なし |
| `escalated` | ⚖️ | 上位権限に引き継ぎ（REVIEWER 拒否権 / COUNCIL 議論 / ユーザ） | planner が reviewer に提出；reviewer が COUNCIL 起動；advisor がユーザ注意必要な挙動パターンをフラグ |
| `awaiting_user` | 🟡 | 明示的ユーザ入力待ちで一時停止（承認ゲート） | Conscious Patrol タスクがユーザ OK 待ち；archiver が曖昧候補検出；reviewer 拒否権でユーザ override 決定要求 |
| `failed` | ❌ | 実行エラー；タスク完了不可 | ツール呼び出し失敗；必須ファイル欠落；spec 違反検出かつ修正不可；subagent クラッシュ |
| `silent_pass` | 🟢 | 高頻度低ノイズパス（surfacing 不要） | AUDITOR Mode 3 違反なし；AUDITOR Mode 7 全 M7-1..M7-7 PASS；cortex pull チェックで関連シグナルなし |

## 例

### 既存パターン置き換え

| v1.8.6 ad-hoc | v1.8.7 status line |
|---------------|-------------------|
| `✅ I am the ARCHIVER subagent · this is a FRESH adjourn invocation (trigger 1 of session).` | `🚀 starting · archiver · fresh adjourn 呼び出し、trigger 1、4-phase フロー開始` |
| `🔱 御史台 · 静默通过` | `🟢 silent_pass · auditor · Mode 3 patrol —— A1/A2/A3/B/C/D/E 各クラス 0 violations` |
| `🌅 Trigger: 上朝 → Theme: 三省六部 → Action: Launch(retrospective) Mode 0` | （これは ROUTER 自身の出力で subagent ではない —— ROUTER status 出力は SKILL.md が管理、本 spec の対象外） |
| `🔄 tick N/12 — checks: ✅PASS=8 / ❌FAIL=2. Auto-fixed GitHub Release publish.` | `🔍 evaluating · verify-release-and-watch · tick 5/12 —— check 8 PASS / 2 FAIL、Release publish auto-fixed、次 tick で再試行` |

### マルチ status 呼び出し例（archiver）

```
🚀 starting · archiver · fresh adjourn 呼び出し、trigger 1、4-phase フロー開始
🔍 evaluating · archiver · Phase 0 hook health チェック
✅ acted · archiver · Phase 0 完了、hooks 健全
🔍 evaluating · archiver · Phase 2 知識抽出
✅ acted · archiver · Phase 2 完了 —— 3 wiki / 2 SOUL / 1 concept canonical
🔍 evaluating · archiver · Phase 3 DREAM 3 日深層レビュー
⏭️ skipped · archiver · Phase 3 浅い眠り —— 有意なパターンなし
✅ acted · archiver · Phase 4 git push 完了、commit abc1234
🚀 starting · memory-keeper · archiver Phase 5 呼び出し
✅ acted · memory-keeper · 3 候補、1 merged、2 appended —— gotchas.md 合計 17
✅ acted · archiver · 全 5 phases 完了、completion checklist が続く
```

ROUTER（と AUDITOR）は `^🚀 starting` で各 subagent 起動、`^❌ failed` でエラー、`^🟡 awaiting_user` で停止タスクを grep 可能。**1 パターン、1 ツール、完全可視。**

## agent ごと enum セマンティクス（HARD）

各 `pro/agents/*.md` は本 agent の 8 status セマンティクスを宣言する `## Status Output (E9)` セクション **必須**。テンプレート例：

```markdown
## Status Output (E9 · v1.8.7)

| Status | 発出時 | 説明例 |
|--------|--------|--------|
| `starting` | Task() 起動後最初の行 | "fresh invocation, trigger N, mode M" |
| `evaluating` | （本 agent 長時間ステップ固有） | （agent 固有） |
| `acted` | （成果物生成時） | （agent 固有） |
| `skipped` | （正当な no-op 時） | （agent 固有） |
| `escalated` | （引き継ぎ時） | （agent 固有、または "N/A —— 本 agent は決して escalate しない"） |
| `awaiting_user` | （承認ゲート条件） | （agent 固有、または "N/A"） |
| `failed` | （frontmatter `failure_modes.known` の具体的失敗モード） | （agent 固有） |
| `silent_pass` | （高頻度クリーンパスケース） | （agent 固有、または "N/A"） |
```

本 agent に適用されない status は省略ではなく `N/A —— <理由>` 宣言 **必須**。例：memory-keeper は `escalated` を決して発出しない（pro/gotchas.md に直接書き、上位権限なし）；`N/A —— memory-keeper は gotchas の終端 writer、エスカレーションパスなし` と宣言。

## 検証（AUDITOR Mode 8）

AUDITOR Mode 8（v1.8.7 新規）が検証：

| チェック | 説明 | 失敗 class |
|---------|------|-----------|
| M8-1 | 各 subagent transcript が `^🚀 starting` 行で始まり契約フォーマットに一致 | `F3 SCHEMA_FAILURE: starting status line 欠落または異形` |
| M8-2 | 発出される各 status line が 8 enum キーワードの 1 つを使う（自由発明なし） | `F4 SCOPE_FAILURE: status キーワード <X> を発明` |
| M8-3 | Emoji ↔ status キーワードペアリングが表に一致（`✅ failed` ミスマッチなし） | `F3 SCHEMA_FAILURE: emoji/status ミスマッチ` |
| M8-4 | agent の status_line セクションが pro/agents/<name>.md で全 8 status を宣言（N/A 含む明示的に） | `F3 SCHEMA_FAILURE: <agent>.md の Status Output 宣言不完全` |
| M8-5 | マルチ status 呼び出しが各 phase/step 遷移で status line を発出 | `F8 SILENT_FAILURE: agent が遷移時 status 発出をスキップ` |
| M8-6 | `failed` status が failure_class 参照を含む（F1-F17 または A/B/C/D/E） | `F10 RESPONSIBILITY_FAILURE: 分類なしの failed status` |

## マイグレーション計画（v1.8.7 リリース内）

22 subagent がバッチ移行。各 agent について：

1. `## Status Output (E9 · v1.8.7)` セクションを追加して 8 enum セマンティクスを宣言
2. 既存 `✅ I am the X subagent` 行が `🚀 starting · <name> · ...` になる
3. 既存 emoji status パターン（`🔱 御史台 · 静默通过` 等）に status-line ラッパーを追加するが、`·` セパレータ後にナラティブテキストを保持（後方読み取り可能性）
4. Audit trail（既存 R13 md フォーマット）にオプショナル `status_line:` frontmatter フィールド追加、最新 status を記録

**後方互換性**：マイグレーション期間中、v1.8.6 ad-hoc emoji **と** v1.8.7 status line の両方受け入れ。AUDITOR Mode 8 初期 WARN レベル。v1.8.8（任意の時期 ship）：旧パターン削除、Mode 8 BLOCK レベル。

## アンチパターン

| アンチパターン | なぜ悪い | 正しい形式 |
|---------------|---------|-----------|
| `✅ The archiver has completed Phase 1`（自由形式） | enum 非準拠；AUDITOR が grep 不可 | `✅ acted · archiver · Phase 1 完了 —— N decisions / M tasks アーカイブ済み` |
| `🚀 Started!`（agent-id なし、説明なし） | AUDITOR / 読者に無用 | `🚀 starting · <agent-id> · <これから何が起きるか>` |
| starting 行をスキップして直接 evaluating | M8-1 契約違反 | `🚀 starting` を常に最初に発出、次行 `🔍 evaluating` が 100ms 後でも |
| 新 status を発明（`🤔 thinking`） | enum 閉鎖性違反 | 既存 8 つでカバーされない場合は、ad-hoc ではなく RFC で enum 拡張提案 |

## 参照

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.8 E9 + DR-11
- パターン源：`tinyhumansai/openhuman` `gitbooks/features/subconscious.md` 7-state アクティビティログ（In progress / Acted / Skipped / Awaiting approval / Failed / Cancelled / Dismissed）—— lifeos が 8 状態に適応してセマンティクス強化（`Skipped`/`Dismissed`/`Cancelled` → `skipped` 統合；`escalated` + `silent_pass` 追加で lifeos 議事 + 監査パターンに対応）
- 連携：`references/conscious-patrol-spec.md`（E10 path D —— 各 patrol タスクが本 spec で status line 出力）
- 連携：`pro/agents/auditor.md` §Mode 8（検証）
