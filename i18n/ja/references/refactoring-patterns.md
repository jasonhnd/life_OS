---
spec_id: refactoring-patterns.v1
description: life_OS agent/spec/skill 進化のための規範的リファクタパターンライブラリ。8 つの主パターン + 2 つの補助 + 1 つの最小化ルール。planner、architect クラスの subagent、ROUTER が構造的変更を検討する際に使用。
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/refactoring-patterns.yml
introduced_in: v1.8.5
---

# リファクタパターン

> 8 つの規範的リファクタパターン + 2 つの補助 + 1 つの最小化ルール。各パターンに `use_when`（診断条件）と `output`（成果物）。planner と architect クラスの agent が構造的変更を計画する際、カスタムアプローチを発明する前に、このカタログを**必ず**参照する。

## 主パターン

### 1. SPLIT（分割）
- **使用時**: 1 つの agent/EOU/spec が複数の主成功基準を持つ、または 2 つの異なる責任が 1 つの単位にまとめられている。
- **成果**: 単一の成功基準を持つ、より狭い単位 2 つ以上。
- **life_OS 例**: v1.7.3 carve-out が archiver Phase 2 を独立した `knowledge-extractor` subagent（知識抽出）+ 残りの archiver（4 phases）に分割。v1.7.2 placeholder 違反を引き起こした過負荷を軽減。

### 2. MERGE（マージ）
- **使用時**: 2 つの単位が常に一緒に走り、同じ成功基準を共有、独立に存在する有用性がない。
- **成果**: 統一された成功基準を持つ単一の結合単位。
- **例**: `narrator` + `narrator-validator` が常に一緒に呼ばれ「引用付きサマリーを生成する」基準を共有していた場合、それらをマージする（v1.8.0 がやったこと —— narrator-validator を削除し、チェックを ROUTER にインライン化）と協調オーバーヘッドが削減される。

### 3. SCOPE-REDUCTION（範囲縮小）
- **使用時**: 単位の `authority_level`、`blast_radius`、`target_object` が実際の機能要件より広い; または宣言された目的の外のファイルを読み書きする。
- **成果**: authority_level を厳格化、allowed_scope を狭め、target_object を縮小。
- **例**: ROUTER は元々 SOUL.md を直接 mutate できた。範囲縮小により ROUTER は SOUL に対して `suggest_only + write_inactive` になった —— SOUL candidate を書けるのは ARCHIVER Phase 2 のみ。

### 4. AUTHORITY-DOWNGRADE（権限降格）
- **使用時**: `automation_mode` が `LLM_assisted` または `deterministic` だが、そのステップが `human_executed` のままであるべき責任の重い判断を担う; または authority_level が機能の要件を超える。
- **成果**: automation_mode または authority_level を下げる; 明示的な `require_human_when` 条件を追加。
- **例**: 高リスク領域（`references/risk-domains.md` の finance/health/legal）での REVIEWER 否決は `LLM_assisted` だが、自動実行ではなく明示的な人類確認を必要とする。

### 5. STEP-EXTRACTION（ステップ抽出）
- **使用時**: agent/EOU 内のステップを deterministic に（slash command に昇格）するか、独自の blast radius とガバナンスを持つサブ agent として分離できる。
- **成果**: 抽出されたステップを処理する新しい slash command（`.claude/commands/*.md`）または子 subagent（`pro/agents/*.md`）; 親は抽出された単位を参照。
- **例**: archiver Phase 4 Notion sync が `/notion-sync` slash command に抽出（v1.8.5）。Phase 4 は slash を呼び出し、audit-trail 書き込みを再実装しない。

### 6. VALIDATOR-ADDITION（バリデータ追加）
- **使用時**: 既知の失敗モードに検証ゲートがない; 出力品質が未検証の前提に依存; 過去のインシデントに再発防止の回帰ケースがない。
- **成果**: 新しい deterministic チェック（slash command）、schema 制約（`references/*-spec.md` v2 frontmatter）、または回帰ケース（`evals/regression-fixtures/rc-*.yml`）。
- **例**: v1.8.0 R-1.8.0-019（GitHub Release Latest ミスマッチインシデント）後、`/verify-release` 6 チェックシーケンス + pro/CLAUDE.md HARD RULE 追加。

### 7. STOP-CONDITION-INJECTION（停止条件注入）
- **使用時**: agent/EOU が無効、曖昧、または無権限の状態で停止して報告するのではなく、実行を継続している。
- **成果**: `execution.stop_conditions` に観察可能なトリガー基準を持つ新しい停止条件 1 つ以上。
- **例**: archiver は `meta/config.md` に 0 個の Notion entity が設定されていても Phase 4 Notion sync を実行していた。停止条件追加: 0 entity → Phase 4 を静かにスキップし、スキップ理由を監査 trail に記録（pro/CLAUDE.md Step 10a R-1.8.0-022 修正による）。

### 8. RESPONSIBILITY-SEPARATION（責任分離）
- **使用時**: 同じ当事者が実行と承認の両方を行う、または 2 つの異なる承認権限が 1 つの単位で処理される。
- **成果**: executor と approver 役割を分離; 各承認権限に別個の subagent または人類ゲート。
- **例**: AUDITOR（Mode 3）は他の agent を監査するが自分自身は監査できない。ADVISOR は REVIEWER 決定をレビューするが再決定はしない。各役割には self-approve できないハード境界がある。

## 補助パターン

### 9. ADD_CONTEXT_MANIFEST（context マニフェスト追加）
- **使用時**: agent パフォーマンスが暗黙的または実行間で一貫しない方法でロードされる context（プロジェクト状態、SOUL、schema バージョン）に依存。
- **成果**: agent の v2 frontmatter（Stage 6）に `context_manifest.source_of_truth + supporting + forbidden` リストを明示的に列挙。
- **例**: hippocampus subagent は元々「必要に応じて」`meta/sessions/` からロードしていた。v2 frontmatter は明示的リストを強制: source_of_truth=[INDEX.md]、supporting=[最近 7 snapshot]、forbidden=[完全 transcript]。

### 10. RETIRE_UNIT（単位の引退）
- **使用時**: 単位が時代遅れ（より良いものに代替）、重複（既存でカバー）、またはネガティブ（コストが運用価値を超過）。
- **成果**: lifecycle を `deprecated` → `retired` に遷移; spec frontmatter を `status: legacy` にマーク; 消費者のための移行パスを文書化。
- **例**: v1.8.0 は `narrator-validator.md` subagent を引退（引用規則は今 ROUTER にインライン化）。v1.8.5 はフック層全体を引退（11 hooks → 0）。

## 最小化ルール（新 agent/spec/skill 作成の HARD RULE）

新しい agent、spec、skill、または HARD RULE を作成する前に、以下 6 つの質問に必ず答える：

1. **ルール**（pro/AGENTS.md または pro/CLAUDE.md 内）で達成できるか？
2. **schema フィールド**（references/*-spec.md frontmatter 内）で達成できるか？
3. **バリデータ**（slash command または AUDITOR Mode 3 scenario）で達成できるか？
4. **回帰ケース**（evals/regression-fixtures/*.yml）で達成できるか？
5. **停止条件**（既存 agent の実行フロー内）で達成できるか？
6. **人類 checklist**（関連ドキュメントに追加）で達成できるか？

**いずれかの**回答が「はい」の場合、新しい単位を作成するよりも低コストオプションを優先する。新 agent/spec/skill 作成は最も高コストのオプション — 1-6 がすべて「いいえ、これは新しい一級単位が必要」と答える場合のみ使用。

## このカタログを呼び出す時

- **planner subagent**: Phase 1 チェック — 構造的変更を提案する前に、少なくとも 1 つのパターンを名前で参照する（または適用されない理由を明示的に正当化する）。
- **アーキテクチャレベル決定**: agent 定義、spec schema、HARD RULES に影響するあらゆる変更。
- **DREAM REM サイクル**: 繰り返し摩擦（3+ 類似インシデント）を検出した場合、パターン 1-10 と照合してリファクタを提案。
- **ECP/RFC 起草**: `proposed_change` セクションで関連パターンを参照。

## ソース出典

eou-foundry @ e4b12ce — `engine/refactoring-patterns.yml` 53 行（8 パターン + 2 補助 + minimality_rule）。適応: 例を life_OS 固有のケースに置換; life_OS には複数の一級単位タイプがあるため "EOU" 用語を "agent/EOU/spec/skill" にマッピング。
