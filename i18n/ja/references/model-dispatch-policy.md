---
spec_id: model-dispatch-policy.v1
description: タスク↔モデル階層のディスパッチポリシー。3 つの能力階層（judgment / execution / batch）を宣言し、すべてのエージェントとメンテナンスジョブをその最低階層にマッピングし、weak-model ディスパッチ命令フォーマットを定義し、階層→モデルのバインディングを単一のマッピングテーブルに集約する。「フロンティアモデルは常に利用可能」という前提を閉じる（issue #1 A1）。
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - hosts/CLAUDE.md (model statement + fallback)
  - hosts/GEMINI.md (model mapping table)
  - hosts/AGENTS.md (model mapping table)
  - agents/dispatcher.md (§Weak-Model Dispatch Mode)
  - references/agent-spec.md (frontmatter `model:` field)
  - .claude/commands/run-eval.md (--tier flag, per issue #4 D2)
---

# Model Dispatch Policy v1

Life OS はフロンティアモデルの読解力を前提に書かれ、24 のエージェント定義のうち 23 が `model: opus` にバインドされ、劣化パスが存在しなかった —— フロンティアモデルが利用不能なとき（quota ウィンドウ、プラン変更、プロバイダ障害、安価なセットアップ）、システムは「完全に動く」から一気に「使えない」へ劣化していた。この spec は欠けていた中間を導入する：タスクごとに宣言された**能力フロア（capability floor）**であり、`authority_level`（書き込み権限を統べるもので、必要な知能ではない）とは別物である。

## 3 つの階層

| 階層 | カバー範囲 | 弱いモデルでの失敗コスト | フロンティア必須？ |
|------|----------------|--------------------------------|--------------------|
| **judgment** | Router トリアージ、計画、レビュー/veto、ドメインスコアリング、council 討議、行動/価値観分析 | もっともらしいが誤った結論が実際の意思決定を誤誘導 —— 出力なしより悪い | **はい —— フロンティア固定** |
| **execution** | Archiver の機械的処理、session 起動、インデックス維持、フォーマット正規化、検索スキャン、翻訳の初稿 | 回復可能な機械的エラー、チェック/パトロールで捕捉される | いいえ —— 中位階層で許容 |
| **batch** | Grep 一括走査、リンク監査、ファイル移動、件数照合、ledger スタンプ | 検出は自明；ジョブは再実行可能 | いいえ —— 最弱階層で許容 |

## HARD RULE · 無言のフォールスルー禁止

**judgment 階層の作業は、フロンティア未満のモデルで無言のまま実行してはならない（MUST NOT）。** 必要な階層が利用不能なときの正しい振る舞いは、`⚠️ this requires a frontier session — deferring <task>` と言って停止することである。もっともらしいが誤った veto、ドメインスコア、トリアージ判断は、延期された判断より厳密に悪い。無言の劣化は F12 DRIFT_FAILURE であり、AUDITOR がフラグを立てる。

execution 階層と batch 階層の作業は、そのフロア以上のどの階層でも実行してよい（MAY）。batch 作業をフロンティアモデルで実行することは許される（単に無駄なだけ）；judgment 作業を batch モデルで実行することは禁止される。

## 階層 → モデルマッピング（モデルバインディングが存在する唯一の場所）

| 階層 | Claude Code バインディング（`model:` frontmatter エイリアス） | Gemini CLI / Antigravity | Codex CLI |
|------|--------------------------------------------------|--------------------------|-----------|
| judgment | `opus` | 利用可能な最強（自動選択） | 利用可能な最強（自動選択） |
| execution | `sonnet` | 中位階層 | 中位階層 |
| batch | `haiku` | 最安/最速階層 | 最安/最速階層 |

ルール：

- `opus` / `sonnet` / `haiku` は**ホストエイリアス**（階層の間接参照）であり、バージョン付きモデル名ではない。ホストが現行世代のモデルに解決する。
- **バージョン付きモデル ID（例 `claude-*-4-*`、日付付きスナップショット）はこのリポジトリのどこにも出現してはならない（MUST NOT）** —— エージェント frontmatter にも、docs の例にも、spec にも。モデル名は数か月ごとに変わる；このテーブルが単一の変更点である。`/check-spec-drift` は、このファイル外のバージョン付きモデル ID をドリフトとして扱う。
- エージェント frontmatter の `model:` 値は、下のテーブルをコンパイルした Claude Code バインディングである。バインディングを変更するとは、まずここのエージェント行を変更し、その後に frontmatter を変更することを意味する。

## エージェント → 最低階層テーブル（完全、24 エージェント）

`min_tier` は能力の**フロア** —— そのエージェントの出力がまだ安全である最弱の階層。Claude Code の `model:` frontmatter は*デフォルト*をバインドする；フロアより上に置いてよい（下は決して不可）。

| エージェント | min_tier | デフォルトバインディング | 備考 |
|-------|----------|-----------------|-------|
| router | judgment | opus | トリアージエラーは下流のすべてを誤ルーティングする |
| planner | judgment | opus | |
| reviewer | judgment | opus | Veto 権限；感情監査 |
| dispatcher | judgment | opus | 依存関係検出 + B5 ゲート；weak-model 命令を起草する |
| council | judgment | opus | 構造化討議 |
| auditor | judgment | opus | 8 モードにわたる違反判定 |
| advisor | judgment | opus | 行動パターン分析 |
| strategist | judgment | opus | 思想家の声 |
| people / finance / growth / execution / governance / infra | judgment | opus | 独立ドメインスコアリング（6 エージェント） |
| gwt-arbitrator | judgment | opus | サリエンス調停 |
| soul-check | judgment | opus | 価値観アラインメント分類 |
| knowledge-extractor | judgment | opus | SOUL/wiki を自動書き込み —— ゲート品質はアイデンティティに関わる |
| narrator | judgment | (router-internal) | ROUTER 内部テンプレート；router の階層に従う |
| retrospective | execution | opus | Mode 0 はほぼ機械的な読み取り + 組み立て；Steps 15-18 のナラティブは緩やかに劣化する（助言であり、意思決定ではない） |
| archiver | execution | opus | Outbox 移動、git 同期、レポート組み立て；DREAM の所見は候補であり、意思決定ではない |
| hippocampus | execution | opus | INDEX 上の機械的な拡散活性化スキャン |
| concept-lookup | execution | opus | INDEX 直接マッチ |
| monitor | execution | opus | 閲覧・起動オペレーションコンソール |
| memory-keeper | execution | sonnet | 既に中位階層にバインド済み（v1.10 以前の唯一の例外） |

## メンテナンスジョブ → 最低階層テーブル（完全、scripts/prompts/ + scripts/commands/）

| ジョブ（`scripts/prompts/`） | min_tier | Cadence（`meta/maintenance-ledger.md` 用） |
|--------------------------|----------|--------------------------------------------|
| advisor-monthly | judgment | 30d |
| research | judgment | on-demand |
| strategic-consistency | judgment | 30d |
| archiver-recovery | execution | on-demand |
| auditor-mode-2 | execution | 7d |
| bulk-ingest (v1.10.0) | execution | on-demand |
| daily-briefing | execution | on-demand |
| doctor | execution | on-demand |
| extract-concepts | execution | on-demand |
| inbox-process | execution | 7d |
| migrate-from-v1.6 / migrate-v1.9 | execution | once |
| review-queue | execution | 7d |
| spec-compliance | execution | 30d |
| wiki-decay | execution | 30d |
| backup | batch | 7d |
| eval-history-monthly | batch | 30d |
| migrate-confidence / migrate-to-wikilinks / wiki-obsidian-upgrade | batch | once |
| rebuild-concept-index | batch | 30d |
| rebuild-session-index | batch | on-demand |
| reindex | batch | 7d |
| snapshot-cleanup | batch | 30d |
| verify-v1.9 | batch | once |

| コマンド（`scripts/commands/`） | min_tier |
|-------------------------------|----------|
| research | judgment |
| compress / inbox-process / method / monitor | execution |
| memory / search | batch |

## Weak-model ディスパッチ命令フォーマット（フロンティア未満への命令）

作業がフロンティア未満の階層（execution または batch）にディスパッチされるとき、ディスパッチ命令は**ルックアップテーブル形式**に絞り込まなければならない（MUST）：

1. **明示的なファイルリスト** —— 読み書きするすべてのファイルをパスで列挙する。「関連ファイルをスキャンせよ」は不可。
2. **機械的な番号付きステップ** —— 各ステップは具体的なツールアクション（Read X、Y 内でパターン P を Grep、Write Z）であり、期待される形が明記される。
3. **開かれた判断はゼロ** —— "use your judgment"、"as appropriate"、"if it seems"、"decide whether" という語句は出現してはならない（MUST NOT）。あらゆる判断点は、命令内で事前決定されているか、「STOP して報告」として列挙される。
4. **ハードな機械的受け入れチェック** —— 完了は grep 検証可能 / カウント可能な条件（例 "0 lines match pattern P"、"row count == manifest count"）で定義される。「完了しているように見える」では決して定義しない。
5. **エスカレーション条項** —— あるステップの前提条件が失敗したとき weak model が何をすべきかを 1 行で明記する：停止して報告する、決して即興しない。

ディスパッチャー側の契約は `agents/dispatcher.md` §"Weak-Model Dispatch Mode" を参照。

## 必要な階層が利用不能なときのフォールバック挙動

| 状況 | 挙動 |
|-----------|----------|
| フロンティア利用不能、judgment 階層タスクが要求された | `⚠️ this requires a frontier session` と言って停止する（上記 HARD RULE）。進行可能な execution/batch 作業のリストをユーザーに提示する。 |
| フロンティア利用不能、execution/batch タスクが要求された | タスクのフロア以上の利用可能な階層で続行する。 |
| 中位階層も利用不能（batch モデルのみ） | 上のテーブルの batch 階層の行のみ実行してよい。それ以外はすべて延期する。 |
| 現在のモデルの階層が不明 | batch として扱う（最も保守的なフロア）。 |

## 劣化安全性の証拠（issue #4 D2 リンク）

上のテーブルの階層クレームは直感ではなく経験的に検証される：eval シナリオは `min_model_tier:` frontmatter フィールドを持ち、`/run-eval --tier <tier>` がその階層にマップされたモデルで実行し、`docs/evals/tier-matrix.md` は実際の実行結果から再生成される。宣言された階層で失敗するシナリオは spec のバグである —— このテーブルが楽観的すぎるか、プロンプトの単純化が必要かのいずれかである。
