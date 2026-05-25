---
spec_id: self-driven-loops-spec.v1
description: ScheduleWakeup ベースの自己駆動コマンドループ仕様。270s 間隔の根拠（Anthropic prompt cache ウィンドウ）、12-tick ハードキャップ（60 分）、退出条件、ホスト互換性（Claude Code のみ）、非対応ホストの劣化パスを定義。パターンは tinyhumansai/openhuman `.claude/commands/ship-and-babysit.md` から借用。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, .claude/commands/ship-and-babysit.md (ScheduleWakeup 270s + 12 tick パターン)
introduced_in: v1.8.7
referenced_by:
  - .claude/commands/verify-release-and-watch.md
  - .claude/commands/notion-sync-and-watch.md
  - SKILL.md (Self-driven loops セクション)
---

# 自己駆動ループ仕様 v1

slash コマンドが `ScheduleWakeup` を使って反復チェック（ポーリング → 修正 → 再チェック）を自己ペーシングし、終端状態またはハードキャップに到達するまでユーザ介入なしで進行する仕様。

## 自己駆動ループを使う時

自己駆動ループは**すべて**成立する時に適切：

1. **タスクに明確な終端状態がある**（例 "全 9 個の verify-release check が PASS"、"全 Notion アイテム同期済み"）。曖昧な "永遠に監視" は有効ユースケースではない
2. **各イテレーションが安価**（ツール呼び出し 1-2 + 短い LLM 推論、フル subagent 起動ではない）
3. **外部状態がイテレーション間で変化する**（CI 完了、GitHub Release publish、Notion sync 完了、ユーザが修正 push）
4. **ユーザが明示的にループを起動した**（例 `/verify-release-and-watch v1.8.7` 入力）—— 別コマンドから自動的に自己駆動ループを起動しない

不適切ユースケース（以下のために自己駆動ループを構築**しない**）：

- ❌ 明確な退出のない純粋監視（例 "queue を永遠に見る"）
- ❌ ループ中にユーザ入力が必要なタスク（通常の対話コマンドを使う）
- ❌ 各イテレーションが高価（重い LLM 作業）なタスク —— ワンショットコマンドのほうが適合
- ❌ cron 的スケジュールタスク（lifeos は v1.8.0 で cron を廃止；再導入しない）

## 間隔選択：270s（HARD）

自己駆動ループ内の各 `ScheduleWakeup` 呼び出しに `delaySeconds: 270` を使う。根拠（Anthropic Claude Code 挙動より）：

- Anthropic prompt cache TTL は **5 分（300s）**
- 300s を超えて寝ると次の起床でフル対話 context を**キャッシュなし**で読む —— より遅く高価
- 270s はキャッシュウィンドウ **内**で 30s の安全余裕
- "5 分"や他の丸い分単位として考えるな —— 270s はキャッシュウィンドウ最適化、暦間隔ではない

**例外**（より長い遅延を使うのは正当化される場合のみ）：

- 外部状態が 5 分より長い既知のケイデンスで変化するタスク（例 GitHub Release CDN 伝播待ち約 10 分）：600s 使用、キャッシュミス受容
- アイドルフォールバックハートビート（特定信号待ち無し）：1200-1800s 使用、4.5 分ごとに context 焼くより受容

300 から 1200s の間は反最適化 —— キャッシュミスのコストを払いつつ償却しない。

## ハードキャップ：12 ticks（60 分）

すべての自己駆動ループは `tickCount` を追跡必須（作業の有無に関わらず、ループ進入ごとにインクリメント）。12 ticks 後：

- **ループを停止**（再度 ScheduleWakeup を呼ば**ない**）
- **ステータススナップショット**をユーザに出力：現在の状態、何が保留中、なぜタイムアウト
- **ユーザに尋ねる**：どう進めるか（再実行？放棄？エスカレート？）

60 分キャップが反映する：1 時間で外部状態が終端に至っていなければ何かおかしい（CI ハング / Release が Draft で詰まる / Notion 認証期限切れ）、人手が必要。

`tickCount` は各 `ScheduleWakeup` `reason` フィールドで可視必須（例 `"tick 5/12: waiting for GitHub Release publish"`）、tick 間で復元可能でドリフト不可。

## 退出条件

各自己駆動ループが独自の退出条件を定義。一般的パターン：

| パターン | 例 |
|---------|----|
| 全チェックパス | "全 9 個の verify-release check PASS" → 退出 |
| 空キュー | "Notion sync アイテムキュー空" → 退出 |
| ユーザ解決 | "ユーザがブロッカを手動完了" → 退出 |
| ハードキャップ | "tickCount > 12" → ステータススナップショット付き退出 |

混合退出条件は許可されるが、各コマンド spec で明示列挙必須。

退出条件成立時：
- `ScheduleWakeup` を呼ば**ない**
- URL / 成果物パスを含む最終一行サマリ出力
- 対話が自然終了 —— ユーザが最終結果を見る

## ホスト互換性（Claude Code のみ）

`ScheduleWakeup` は Claude Code 固有ツール。他の lifeos サポートホスト（Gemini CLI / OpenAI Codex CLI）は v1.8.7 時点で同等機能を**持たない**。

各自己駆動ループコマンドは宣言必須：

```yaml
---
description: <one-liner>
argument-hint: <args>
requires_host: claude-code
allowed-tools:
  - Bash
  - Read
  - Edit
  - ScheduleWakeup
---
```

非 Claude Code ホストで呼ばれた時：

1. ROUTER はホスト検出必須（SKILL.md 既存ホスト検出経由）
2. 単一エラーメッセージ出力：
   ```
   ⚠️ `/<command>` は Claude Code が必要（自己駆動ループに ScheduleWakeup 使用）。
      あなたは <host> 上。代わりに `/<base-command>` を実行（手動再実行）。
   ```
3. ループ本体を実行**しない**

手動フォールバックパス：各自己駆動ループには非-watch 兄弟コマンドが必須（例 `/verify-release` は `/verify-release-and-watch` の非 watch 版）。非 watch 版はどのホストでも動作、ユーザが手動再実行。

## 必須コマンド構造

自己駆動ループコマンドファイル（`.claude/commands/<name>-and-watch.md`）は以下のセクションを含む必須：

```markdown
---
description: <one-liner>
argument-hint: <args>
requires_host: claude-code
allowed-tools: [Bash, Read, Edit, ScheduleWakeup, ...]
---

# /<command>-and-watch

<目的段落：このループが達成すること、終端状態で退出する内容>

## 入力

- `$ARGUMENTS`（オプショナル/必須）—— 説明

## ループ本体（1 tick）

1. **tickCount を読む** —— 前回 ScheduleWakeup reason から抽出、なければ 1
2. **退出条件チェック** —— 退出なら最終サマリ出力して STOP（ScheduleWakeup を呼ばない）
3. **イテレーション作業実行** —— チェック実行、発見した問題を修正
4. **次状態決定** —— 退出 / 継続 / ハードキャップ到達
5. **ペーシング**：
   - 退出 → 停止
   - ハードキャップ到達（tickCount ≥ 12）→ ステータススナップショット出力、ユーザに尋ねる、STOP
   - それ以外 → `ScheduleWakeup({delaySeconds: 270, prompt: "/<command>-and-watch <args>", reason: "tick <N+1>/12: <保留中>"})` 呼び出し

## 退出条件（列挙）

- 全チェック PASS → リンク付き退出
- ハードキャップ → スナップショット付き退出
- ユーザキャンセル信号 → 退出
- 致命的エラー → エラー付き退出（リトライしない）

## 失敗処理

- <コマンド固有失敗モードと復旧>

## ホスト互換性

非 Claude Code ホスト：spec に従いエラー、手動再実行用に `/<base-command>` を指す。
```

## Audit trail

自己駆動ループの各イテレーションは `_meta/runtime/<sid>/<command>-tick-<N>.md` に書き込み**推奨**：

- tickCount（現在）
- タイムスタンプ
- 実行したチェック + 結果
- 行った決定（継続 / 退出 / 適用した修正）
- 次のアクション（いつまで sleep / 最終退出）

audit trail はループが N tick かかった理由や、なぜ途中で抜けたかの事後再構築を可能にする。

## 参照

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.2 B4
- パターン源：`tinyhumansai/openhuman` `.claude/commands/ship-and-babysit.md`（Phase 4 babysit ループ）
- 連携：`SKILL.md` "Self-driven loops with ScheduleWakeup" セクション
