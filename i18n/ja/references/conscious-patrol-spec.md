---
spec_id: conscious-patrol-spec.v1
description: "lifeos の Conscious Patrol —— OpenHuman の Subconscious Loop の path-D 適応。idle autonomous daemon ではなく；session-start user-in-loop checkpoint。retrospective Mode 0 が system tasks リスト（lifeos デフォルト）+ user tasks（second-brain HEARTBEAT.md）を読み、現在の workspace に対して各タスクを評価し、ユーザに推奨を報告する。ユーザが各 act/skip/escalate を明示的に承認。v1.8.0 cron 退役と整合：ユーザが常に loop 内にいるため回帰ではない。"
status: active
authoritative: true
source_attribution: "tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/subconscious.md (idle autonomous Subconscious Loop)。lifeos は RFC v1.8.7 DR-11 に従い path D（Conscious Patrol —— user-in-loop）を選択。"
introduced_in: v1.8.7（2026-05-26 追加、DR-11 に基づく）
referenced_by:
  - SKILL.md (E10 HARD RULE)
  - pro/agents/retrospective.md (Mode 0 が Conscious Patrol を体系化)
  - pro/agents/auditor.md (Mode 8 patrol コンプライアンス)
  - references/status-line-spec.md（各 patrol タスクが status line を出力）
---

# Conscious Patrol 仕様 v1

lifeos の OpenHuman Subconscious Loop への適応。**重要な命名の区別**：

- **OpenHuman Subconscious** = idle スレッド、autonomous daemon、ユーザ不在時も実行、local model が自律的に act/skip/escalate を決定
- **lifeos Conscious Patrol** = session-start チェックポイント、user-in-loop、ROUTER が推奨 + ユーザが決定、daemon なし

これは v1.8.7 RFC §1.3 E10 分析の path D。path D が選ばれたのは lifeos が md-only スキル（daemon 層なし）+ v1.8.0 が cron 式自律を明示的に退役したため。

## なぜ "Subconscious" ではなく "Conscious"

| 属性 | OpenHuman Subconscious | lifeos Conscious Patrol |
|------|----------------------|------------------------|
| トリガー | 周期的 heartbeat tick（N 分ごと） | retrospective Mode 0（session 開始） |
| 自覚 | 実行中ユーザは気づかない | ユーザが明示的に session を開始 |
| 決定権限 | local model 自律 | ROUTER が推奨、ユーザが決定 |
| 書き込みアクション | 未要請時除き自動実行 | すべての act にユーザの明示的 OK 必要 |
| 失敗モード | 静かなデータ損失の可能性（cron 式） | ユーザが画面前で各エラーを確認 |
| アーキテクチャ担体 | Tauri daemon プロセス | retrospective subagent 実行 |

命名の誠実さが重要：lifeos の path D を "Subconscious" と呼ぶことは、存在しない idle 自律性をユーザに期待させる誤解を招く。**Conscious Patrol** は実際に何が起きるかを正確に記述する —— ユーザは意識的、ROUTER が巡回、ユーザが決定。

## なぜこれが v1.8.0 cron への回帰でないか

v1.8.0 は `setup-cron.sh` + すべての launchd plists + cron コンテキストで LLM を実行する 5 つの Python tools を退役した。退役の根拠：

1. "信頼性なし" —— cron は静かに失敗、surfacing なし
2. "不可視" —— ユーザが読まないログファイルへの出力
3. "静かなデータ損失" —— cron コンテキストで LLM を実行する Python tools が誤った出力で良いデータを上書き

**Conscious Patrol はこれらに違反しない**：

1. **信頼性あり** —— retrospective Mode 0 の一部として実行され、これは各 session 開始で実行；失敗時ユーザは briefing で失敗を見る
2. **可視** —— 出力は朝のブリーフィングそのものであり、session 開始時にユーザが最初に目にする最も顕著なもの
3. **静かなデータ損失なし** —— 各 act にユーザの OK 必要；明示的確認なしで何も書き込まない

v1.8.0 の退役は当時のテクノロジー（Python tools + システム cron）に対して正しかった。v1.8.7 Conscious Patrol は根本的に異なるメカニズム（LLM 駆動 retrospective + ユーザ承認）を使う。path D は path C/F（Claude Code headless をトリガーする external cron）**ではない** —— それらは v1.8.0 の懸念を再導入する。path D は lifeos が常に主張してきた user-in-loop モデルに留まる。

## System tasks（デフォルトシード、削除不可、disable のみ）

retrospective Mode 0 が以下を各 session のデフォルト patrol items として含む：

### lifeos-001 · Maintenance overdue チェック

- **出典**：lifeos は既に v1.8.0 で実装（`scripts/prompts/auditor-mode-2.md` + 10 個の maintenance jobs）
- **何をチェック**：`reindex / daily-briefing / backup / spec-compliance / wiki-decay / archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency` のタイムスタンプ —— overdue をフラグ
- **出力**：status line + overdue アイテム数
- **ユーザ決定**：本 session でどの overdue jobs を実行するか選択

### lifeos-002 · Review queue overdue

- **出典**：lifeos R-1.8.0-013 review-queue.md prompt
- **何をチェック**：review queue で P0/P1/P2 アイテムが期待ウィンドウ内未処理かをスキャン
- **出力**：status line + N P0 / M P1 / K P2 カウント
- **ユーザ決定**：今 queue を歩くか先送りか

### lifeos-003 · SOUL drift チェック

- **出典**：lifeos advisor-monthly.md prompt（既存）
- **何をチェック**：SOUL.md 信頼度ドリフト / 未挑戦 dimensions / 矛盾エビデンス
- **出力**：status line + N dimensions フラグ
- **ユーザ決定**：今 review するか月次スロットを予約

### lifeos-004 · Wiki decay スキャン

- **出典**：lifeos wiki-decay.md prompt（既存）
- **何をチェック**：`last_reviewed` が古い / 最近の session に矛盾する wiki エントリ
- **出力**：status line + N エントリフラグ
- **ユーザ決定**：decay を確認、エントリを退役、またはリフレッシュ

### lifeos-005 · Strategic 一貫性

- **出典**：lifeos strategic-consistency.md prompt（既存）
- **何をチェック**：戦略フローのクロスプロジェクト衝突 / SOUL ↔ flow 不整合
- **出力**：status line + N 衝突
- **ユーザ決定**：今対処するか次の計画 session に記録するか

### lifeos-006 · Compliance Watch

- **出典**：lifeos AUDITOR Mode 3（既存）
- **何をチェック**：30 日ローリング違反カウント；エスカレーション閾値（同クラス ≥3 → hook 厳格化；≥5 → briefing 上部；≥10 → AUDITOR Mode 3 毎 Start Session 実行）
- **出力**：status line + 違反サマリ
- **ユーザ決定**：violations.md を review、行動を調整、または確認

### lifeos-007 · Gotchas review（v1.8.7 新規）

- **出典**：lifeos v1.8.7 C6 —— `pro/gotchas.md`
- **何をチェック**：過去 7 日に触れたファイル/コードを参照する gotcha（関連性シグナル）；解決済みの gotcha（コードベース修正済みだが gotcha がまだリストアップ）
- **出力**：status line + N 関連 gotchas が浮上
- **ユーザ決定**：ROUTER が現在のタスクに関連する gotchas をスキャン；ユーザが確認 / 却下

## User tasks（HEARTBEAT.md メカニズム）

ユーザは second-brain ルートに `HEARTBEAT.md` を作成可能：

```markdown
# Patrol Items

## daily
- 14 日超の未解決決定をチェック
- 過去 3 日の mood-tagged ジャーナルエントリを浮上

## weekly
- "review-needed" タグの wiki エントリを review
- プロジェクト優先度を四半期 OKR と照合

## monthly
- 金融決定カテゴリを監査
- SOUL.md "あるべき姿" vs "現状" の差分を review
```

retrospective Mode 0 が `HEARTBEAT.md`（存在する場合）を読み、frequency-since-last-run でフィルタし、マッチするアイテムを patrol リストに追加。各 user task が標準契約に基づき status line を取得。

### HEARTBEAT.md frontmatter（オプショナル）

```yaml
---
patrol_enabled: true
frequency_default: weekly
disabled_system_tasks: []   # 例 ["lifeos-005"] で戦略一貫性をスキップ
---
```

`disabled_system_tasks` はユーザが特定デフォルトを opt-out 可能にする（削除不可だが disable 可能、OpenHuman パターンに従う）。

## Tick セマンティクス（lifeos vs OpenHuman）

OpenHuman はユーザの活動に関わらず N 分ごとに tick 実行。lifeos は retrospective Mode 0 が起動する時のみ "tick" 実行（各 session 開始）。頻度比較：

| 頻度 | OpenHuman | lifeos Conscious Patrol |
|------|-----------|------------------------|
| ユーザが 1 日に複数 session を開く | ユーザが N session 開くなら N 回/日 patrol | 同じ —— N 回/日 |
| ユーザが休暇中（2 週間 session なし） | OpenHuman は 2 週間 N 分ごとに tick（336+ ticks） | lifeos は tick しない —— session 再開時に patrol 実行 |
| 長期的懸念（例：90 日 SOUL drift） | OpenHuman は段階的に drift を捕捉 | lifeos は次の session 開始時に drift を捕捉（非リアルタイム懸念には許容範囲） |

**トレードオフ**：lifeos はリアルタイム検出を user-in-loop 安全性のために犠牲にする。lifeos のドメイン（個人決定エンジン、運用監視ではない）には、このトレードは正しい。

## Status line 統合（E9）

各 patrol タスクが `references/status-line-spec.md` に基づき status line を出力：

```
🔍 evaluating · retrospective · Conscious Patrol —— lifeos-001 maintenance overdue チェック中
⏭️ skipped · retrospective · lifeos-001 —— 全 10 jobs がウィンドウ内
🔍 evaluating · retrospective · lifeos-002 review queue
🟡 awaiting_user · retrospective · lifeos-002 —— 3 P0 / 1 P1 overdue、/process-queue 実行？
✅ acted · retrospective · lifeos-003 SOUL drift —— 1 dimension フラグ、briefing に浮上
🟢 silent_pass · retrospective · lifeos-004 / lifeos-005 / lifeos-006 / lifeos-007 —— クリーン
```

各行は AUDITOR Mode 8 が grep 可能。

## 決定フロー（path D コア）

各 patrol タスクについて、retrospective Mode 0 は以下の 1 つを発出：

| 決定 | 何が起きるか |
|------|------------|
| `silent_pass` | タスク実行、関連性なし、surfacing 不要（高頻度低ノイズシナリオ） |
| `skipped` | タスク実行、対応可能項目なし、briefing で簡単な言及（低頻度情報的） |
| `awaiting_user` | タスクが対応可能項目を発見、ROUTER が報告 + ユーザに質問。ユーザ応答："yes、X を実行" / "skip" / "later" |

**静かな act なし**。すべての act はユーザ明示的。これが path D を path A-F の代替案から区別する lifeos の中心的コミットメント。

## AUDITOR Mode 8 patrol コンプライアンス（status line 以外）

Mode 8 は Conscious Patrol 挙動を追加で検証：

| チェック | 説明 | 失敗 class |
|---------|------|-----------|
| M8-7 | 各 session-start retrospective Mode 0 が briefing 内に patrol セクション（`## Conscious Patrol`）を含む | `F4 SCOPE_FAILURE: retrospective Mode 0 が patrol セクション欠落` |
| M8-8 | 各 lifeos-001 から lifeos-007 system task が status line を発出（または HEARTBEAT.md ごとに明示的に disabled マーク） | `F3 SCHEMA_FAILURE: system task <id> の出力欠落` |
| M8-9 | "auto-act" 検出なし（各 act の前に `awaiting_user` 行が伴う） | `F10 RESPONSIBILITY_FAILURE: 静かな act がユーザ承認をバイパス` |
| M8-10 | HEARTBEAT.md の user tasks が実際にスキャン（audit trail エビデンス） | `F8 SILENT_FAILURE: HEARTBEAT.md 存在するが user tasks 未浮上` |

## v1.8.7 が**しない**こと（path D スコープの誠実さ）

Conscious Patrol が何でないかを明示：

- ❌ バックグラウンド daemon / cron / launchd なし
- ❌ 外部トリガーメカニズムなし（ユーザの OS cron / GitHub Actions 等）—— それは path C/F 領域、先送り
- ❌ autonomous act なし（各 act にユーザ明示的 OK 必要）
- ❌ リアルタイム検出なし（session-start patrol のみ；ユーザ離席期間は盲目）
- ❌ headless Claude Code 起動なし
- ❌ `claude --headless -p "..."` 統合なし

v1.8.7 が**すること**：
- ✅ retrospective Mode 0 patrol を明示的 7 system tasks + ユーザ定義 HEARTBEAT.md として体系化
- ✅ E9 status line と統合して観測可能性を統一
- ✅ AUDITOR Mode 8 M8-9 経由で user-in-loop を強制
- ✅ v1.8.0 cron 退役と整合（本 spec の明示的 "なぜ回帰でないか" セクション）

## 未来の方向（v1.8.7 後）

ユーザが実際にリアルタイム patrol を要求する場合（休暇モード検出 / 夜間 SOUL drift）、次のオプション：

- **v1.9 / v2.0 path C**：それを望むユーザのために external-cron テンプレート（launchd plist / GitHub Actions workflow）をドキュメント化。lifeos は spec プロバイダのまま、バンドルしない
- **v2.0 path F**：ユーザの second-brain repo が cron ロジックを担う（ユーザ repo 内の GitHub Actions）。lifeos が workflow テンプレートを提供

これらは先送り —— v1.8.7 path D は user-in-loop のみと明示的にスコープ。

## 参照

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.9 E10 path D + DR-11
- パターン源：`tinyhumansai/openhuman` `gitbooks/features/subconscious.md`（idle autonomous Subconscious Loop、daemon ベース）
- 連携：`references/status-line-spec.md`（各 patrol タスクが 8 enum status を使用）
- 連携：`pro/agents/retrospective.md` Mode 0（Conscious Patrol が実行される場所）
- 連携：`pro/agents/auditor.md` Mode 8（検証）
- 関連するが**異なる**：lifeos v1.8.0 cron 退役（`pro/CLAUDE.md` §"Mode 1 · Business session" —— daemon 式自律が拒否された理由を説明）
