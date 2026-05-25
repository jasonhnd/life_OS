---
spec_id: memory-tree-spec.v1-proposal
status: proposal
authoritative: false
implementation_target: v1.9 または v2.0（TBD —— Jason の second-brain 実データ検証待ち）
description: 提案 —— lifeos sessions/wiki メモリの cascade seal アーキテクチャ。L0（生、≤30 日）→ L1（週ダイジェスト）→ L2（月ダイジェスト）→ L3（年ダイジェスト）の bucket-seal cascade による折りたたみを定義。パターンは tinyhumansai/openhuman Memory Tree（`gitbooks/features/obsidian-wiki/memory-tree.md`）から借用。v1.8.7 では未実装 —— spec を v2.0 アーキテクチャアンカーとして凍結；archiver 挙動は v1.8.6 から変更なし。
source_attribution: tinyhumansai/openhuman @ b7b8ba6, gitbooks/features/obsidian-wiki/memory-tree.md（3 つの tree / L0→L1 cascade seal / hotness 駆動トピック実体化）
introduced_in: v1.8.7（仕様のみ）
referenced_by:
  - references/wiki-spec.md（v2.0 方向参照）
  - references/session-index-spec.md（v2.0 方向参照）
  - _meta/rfc/v1.8.7-openhuman-borrowed-patterns.md §2.6 A1
---

# Memory Tree 仕様（提案 · v1.9 / v2.0 目標）

> **ステータス：提案のみ**。v1.8.7 はこの仕様を将来の方向アンカーとして ship。`archiver` 挙動は v1.8.6 から変更なし。ユーザランタイムには L0/L1/L2/L3 ディレクトリレイアウトは存在しない。cascade seal ロジックは動作しない。この仕様は将来の実装に明確なターゲットを持たせるため凍結 —— これらデータ構造と閾値の検証は Jason の実際の second-brain で数週間/月にわたって走らせる必要があり、v1.8.7 dev サイクルには含まれない。

## なぜ cascade seal アーキテクチャ（動機）

現在の lifeos sessions/wiki 構造（v1.8.6 時点）：

- `_meta/sessions/<sid>.md` —— フラットディレクトリ、全 session が永遠に蓄積
- `_meta/wiki/<topic>/<entry>.md` —— トピック毎フラット、自動圧縮なし
- `_meta/concepts/<concept>.md` —— フラット、hotness カウントあるが派生要約ファイルなし

何年も蓄積後の問題：

- `archiver` の "過去 30 日" 読み込みは OK；"過去 2 年" 読み込みは高価に
- `hippocampus` が数千 session で活性化拡散すると線形に遅くなる
- ユーザが `_meta/sessions/` を閲覧して 1000+ ファイル、ナビゲーションなし
- 50 sessions を経て成長した wiki エントリにコンパクトな "この概念は今何を意味するか" の要約がない

OpenHuman の Memory Tree は L0 → L1 → L2 cascade 要約でこれを解決。パターンを借用（実装は借用しない —— OpenHuman は SQLite、lifeos は DR-10 により md-only 維持）。

## 提案レイアウト

```
_meta/sessions/
├── L0/                          # 生 session、過去 30 日
│   ├── 2026-05-25-<sid>.md
│   └── ...
├── L1-weekly/                   # 週ダイジェスト、過去 12 週（~3 か月）
│   ├── 2026-W21.md              # 2026 年第 21 週 —— その週の L0 sessions のダイジェスト
│   └── ...
├── L2-monthly/                  # 月ダイジェスト、過去 12 か月
│   ├── 2026-05.md
│   └── ...
└── L3-yearly/                   # 年ダイジェスト、全年
    ├── 2026.md
    └── ...
```

`_meta/wiki/`（seal された wiki エントリ）と `_meta/concepts/`（canonical concept ロールアップ）に同じパターン。

## L0 → L1 cascade seal アルゴリズム

```
各 archiver Adjourn 時（v1.9 / v2.0 で）：

1. L0 buffer 状態をチェック：
   - _meta/sessions/L0/ のファイル数カウント
   - 最古ファイルタイムスタンプチェック

2. "L0 → L1 seal" トリガー条件：
   - Buffer 数 ≥ 30 sessions、または
   - 最古 L0 session > 30 日

3. Seal トリガー時：
   a. Seal される週を決定（L0 内で >0 session を持つ最古週）
   b. その週の全 L0 session ファイルを読む
   c. Sealing prompt で chat model を呼ぶ → 週ダイジェスト生成
   d. _meta/sessions/L1-weekly/<YYYY>-W<NN>.md に書く
   e. Seal 済み L0 ファイルを _meta/sessions/_archive/L0-pre-seal/ に移動
   f.（削除しない；監査用に保存）

4. L1 buffer が閾値に達したら L2 にカスケード：
   - L1 buffer 数 ≥ 12 週ダイジェスト（~3 か月）、最古月を L2 に seal
   - 同手順：その月の L1 weeklies を読む → L2 monthly 生成 → seal 済み L1 をアーカイブに移動

5. L2 が 12 月ダイジェストに達したら L3 yearly にカスケード
```

## Buffer 閾値（根拠）

| 層 | 次の層 seal をトリガーする閾値 | 根拠 |
|----|----------------------------|------|
| L0 → L1 | 30 sessions または 最古 30 日 | "先月" 認知地平に合致；archiver は L0 を自由に読む |
| L1 → L2 | 12 週ダイジェスト（~3 か月） | 四半期は自然なレビュー単位 |
| L2 → L3 | 12 月ダイジェスト | 年は最大の実用認知単位 |
| L3 → (なし) | これ以上 seal しない | 年がトップ —— lifeos が世代的にならない限り L4 なし |

Buffer 数は実装時に調整可能；重要なのは cascade 構造。

## Flush_stale（部分 buffer 強制 seal）

Buffer が長時間閾値に達せず座っていたら（例：ユーザがサバティカル 6 か月、L0 に 5 sessions のみ）、それでも強制 seal：

- L0 → L1 強制 seal：60 日超の任意 L0 ファイル（通常閾値の 2x）
- L1 → L2 強制 seal：180 日超の任意 L1 週
- L2 → L3 強制 seal：24 か月超の任意 L2 月

部分週が L0 に永遠に座る stale-buffer 病理を防止。

## Sealing prompt（LLM 駆動）

各 seal レベルがレベル固有 prompt を使用：

- **L0 → L1（週ダイジェスト）**："今週の session を要約。決定事項、反復テーマ、未解決問題、活性化された主要 concept を抽出。目標長：800-1500 tokens。"
- **L1 → L2（月ダイジェスト）**："これら週ダイジェストから月次レビュー作成。月次テーマ、硬化/軟化した決定、canonical 閾値を超えた concept 活性化、反復する人物を識別。目標：1500-2500 tokens。"
- **L2 → L3（年ダイジェスト）**："月ダイジェストから年次レビュー生成。年の中心ナラティブ、最長未解決スレッド、SOUL 進化エビデンス、戦略線変化を識別。目標：3000-5000 tokens。"

Prompt は `pro/seal-prompts/L0-to-L1.md` 等に存在（場所 TBD、v1.8.7 で構築せず）。

## v1.8.7 が**しない**こと

明示的に：

- ❌ `_meta/sessions/L0/` ディレクトリ作成なし（既存フラットレイアウト維持）
- ❌ archiver cascade seal ロジックなし
- ❌ Seal prompt ファイルなし
- ❌ 自動 L1/L2/L3 生成なし
- ❌ 既存 session 用マイグレーションスクリプトなし

v1.8.7 が**する**こと：
- ✅ この仕様を `status: proposal` として凍結
- ✅ `wiki-spec.md` + `session-index-spec.md` からこの仕様への参照を v2.0 方向として追加
- ✅ 将来の実装ターゲットとして構築可能を維持

## 未解決の質問（実装 RFC で解決）

以下は意図的に本提案で**解決しない** —— 実データで検証必要：

1. L3 yearly はさらに cascade すべきか（10 年単位？生涯）？多分しない、しかし 3 年蓄積後にチェック
2. cascade 内で `_meta/snapshots/soul/` SOUL スナップショットをどう扱うか —— 独立ケイデンスか統合か？
3. L1 週ダイジェストは vault に書く（Obsidian 可視）か `_meta/sessions/` に残す（dev 内部）か？
4. Seal された L1/L2 ファイルが新しいコンテキストの session と衝突した時（ユーザが "5 月のその週" を参照するが L1 が実際何が起きたかを paraphrase 済み）、provenance はどう回復するか？L0 アーカイブパスへのアクセス維持必須
5. コスト較正：L1 週ダイジェスト ~$0.50-$2（1500 tokens を最先端モデルレートで）、L2 月次 ~$2-$10。アクティブユーザの年間コスト：sealing だけで LLM 請求 $300-$800/年。価値あるか？

これら質問が v1.8.7 を仕様のみに留める理由。実データ試行が回答する。

## マイグレーションパス（将来 v1.9/v2.0 実装時）

将来バージョンが実装する時：

1. 既存フラットレイアウトに触れず新ディレクトリ追加
2. ワンタイムバックフィル実行：`/seal-backfill` slash コマンドが既存フラット `_meta/sessions/` を歩いて append-only 方式で L1/L2/L3 を生成
3. バックフィル後、将来の archiver Adjourn が増分 seal を実行
4. 既存ファイルは下位互換のため `_meta/sessions/<sid>.md` パスに残る（移動しない）—— 新 session のみ直接 L0 buffer へ

このマイグレーションは非破壊的で可逆。

## 参照

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.6 A1
- パターン源：`tinyhumansai/openhuman` `gitbooks/features/obsidian-wiki/memory-tree.md`（3 つの tree / L0→L1 cascade seal）
- 実装メモ：OpenHuman は SQLite `memory_tree/chunks.db` + tokio task pool を使用。lifeos は DR-10（`SKILL.md` HARD RULE）により md-only 維持 —— 上記ディレクトリレイアウトは lifeos の基板
- 連携：`references/concept-spec.md` §Hotness 閾値（cascade seal トリガー + hotness 実体化は姉妹概念）
