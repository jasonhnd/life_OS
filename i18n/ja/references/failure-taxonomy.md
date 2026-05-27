---
spec_id: failure-taxonomy.v1
description: eou-foundry から借用したアーキテクチャレベル失敗分類法 F1-F17。life_OS のプロセス違反分類法（A1/A2/A3/B/C/D/E/F、pro/compliance/violations.md）を補完する。v1.8.5 以降、すべての violations.md エントリは A-F タグと F1-F17 タグの両方を持つ必要がある。
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/failure-taxonomy.yml
introduced_in: v1.8.5
---

# 失敗分類法 F1-F17

> AI agent ガバナンスシステムのアーキテクチャレベル失敗カテゴリ。各カテゴリに definition + canonical repair。life_OS は eou-foundry からこの分類法を借用（Stage 3 Day 6 成果物、`meta/rfc/v1.8.5-cleanup-and-hardening.md` 参照）。

## 既存 life_OS 分類法との関係

| 分類法 | レイヤー | 例 | 記録場所 |
|---|---|---|---|
| **A1/A2/A3/B/C/D/E/F**（`references/compliance-spec.md`）| **プロセス違反**（人/プロセス層）| A1: retrospective Subagent スキップ; B: パス捏造; C: ステップスキップ; D: 自己承認; E: publish 漏れ; F: 出力 PII 漏洩 | `pro/compliance/violations.md` |
| **F1-F17**（本ドキュメント）| **アーキテクチャ失敗**（システム設計層）| F11: ライフサイクル段階ミスマッチ; F12: spec drift; F14: 沈黙判断 | 同じ `violations.md`（Stage 8 で F-code 列追加）|

**両方の分類法は同じインシデントに適用される**。例: "ROUTER が retrospective Subagent をスキップし、パスを捏造した" = `A1`（プロセス）+ `F12_DRIFT_FAILURE`（アーキテクチャ）。

## F1-F17 リファレンス

### F1 — INPUT FAILURE
- **定義**: 必須入力が欠落、不正形式、古い、または曖昧。
- **修復**: 入力 schema を厳格化、または上流で入力を修復。
- **life_OS 例**: ROUTER が空の `$ARGUMENTS` を受け取るが、slash command は `--sid` を要求。

### F2 — CONTEXT FAILURE
- **定義**: 誤った context がロードされた、または正典ソースが省略された。
- **修復**: `context_manifest` を修復。
- **例**: REVIEWER が SOUL.md を読まずに決定; archiver Phase 4 が古い `meta/config.md` を読む。

### F3 — SCHEMA FAILURE
- **定義**: spec、入力、出力、validator schema が乖離。
- **修復**: schema を正規化し、validator を更新。
- **例**: `references/soul-spec.md` v1 と実際の SOUL.md フィールドが drift。

### F4 — SCOPE FAILURE
- **定義**: agent/EOU/skill が広すぎ、狭すぎ、または互換性のないタスクを混在。
- **修復**: 分割、マージ、または再定義。
- **例**: v1.7.3 carve-out 前の archiver が Phase 2 知識抽出と Phase 1 アーカイブの両方を実行、v1.7.2 placeholder 違反を引き起こした。

### F5 — INSTRUCTION FAILURE
- **定義**: ステップが不明、矛盾、または実行不能。
- **修復**: 実行手順を書き直す。
- **例**: pro/agents/retrospective.md の 18 ステップで step 12 が step 7 と矛盾。

### F6 — JUDGMENT FAILURE（サブタイプ）

#### F6a — STRUCTURAL_JUDGMENT
- **定義**: agent が異なる成功基準または異なる責任者を持つ 2 つの判断を混同。アーキテクチャ的に誤り。
- **修復**: 責任分離または分割リファクタ。
- **例**: REVIEWER が一度の呼び出しで否決判断と監査判断の両方を行う。

#### F6b — COVERAGE
- **定義**: 判断フレームは正しいが、検証基準なし。アーキテクチャは正しいが境界が検証不能。
- **修復**: 判断述語、明示的成功基準、回帰ケースを追加。
- **例**: AUDITOR Mode 3 に scenario リストはあるが期待出力 schema がない。

### F7 — VALIDATION FAILURE
- **定義**: Validator が無効出力を通すか、有効出力を拒否する。
- **修復**: 検証ロジックを改善; 境界に回帰ケースを追加。
- **例**: `/check-spec-drift` が broken-path 参照を見逃す; または正当な legacy ファイルを誤検出。

### F8 — TOOL FAILURE
- **定義**: スクリプト、モデル、API、外部ツールがハード失敗。
- **修復**: 依存を分離、フォールバック追加、stop condition 追加。
- **例**: Notion MCP が Phase 4 途中で利用不能; gh CLI が 502 を返す。

### F9 — TRACE FAILURE
- **定義**: 実行を再構築できない; trace が欠落するか宣言されたステップと矛盾。
- **修復**: trace キャプチャを改善; 各ステップを `meta/runtime/<sid>/` に書き込む。
- **例**: archiver Phase 4 が完了したが `notion-sync-*.json` 監査 trail を書かない。

### F10 — RESPONSIBILITY FAILURE
- **定義**: 明確な owner、承認ゲート、エスカレーションパスなし; または同一者が実行と承認の両方を行う。
- **修復**: 責任マッピングを追加; executor/approver を分離。
- **例**: ROUTER が wiki 書き込みを提案かつ自動実行する（REVIEWER 否決チェックなし）。

### F11 — LIFECYCLE FAILURE
- **定義**: agent/EOU/entry が誤った成熟度基準で評価される。
- **修復**: lifecycle_stage を明示的に宣言; 一致する検証レベルを適用。
- **例**: `tentative` 信頼度の SOUL dim が REVIEWER 参照で `confirmed` として扱われる。**A1 COURT-START クラス違反もここにマップ**（Start Session トリガーが retrospective Subagent をスキップ = 誤ったライフサイクルゲート）。

### F12 — DRIFT FAILURE
- **定義**: spec、scripts、docs、validator が乖離; 一層の変更が他層に伝播されていない。
- **修復**: 正典層（`schemas/` または `references/`）を特定し、依存層を調整、CI/audit に語彙同期チェックを追加。
- **例**: pro/agents/router.md が削除された `pro/agents/narrator-validator.md` を参照。**B 捏造パス違反もここにマップ**。

### F13 — PERFORMANCE FAILURE
- **定義**: 正しく実行するがスケール時に劣化。
- **修復**: プロファイル、ボトルネック制限、予算/タイムアウト追加、automation_mode を tier-down、分割または高速ツールに昇格。
- **例**: v1.8.1 Wave 2 で Bash skeleton 削除後、archiver Adjourn が 25-30 分（アーキテクチャ純粋さのため受容したトレードオフ、ただし F13 境界）。

### F14 — SILENT_JUDGMENT_FAILURE（v1.8.5 新規）
- **定義**: agent が `SOUL.md` の domain_value を一切呼び出さずに contested choice を行う。選択は正しいかもしれないが追跡不能 — どの推論が衝突を解決したかの trace 記録なし。**V1（認知完全性）に従い最も危険な agentic-judgment 失敗モード。**
- **修復**: 検出された各 contested case に対し `value_invocations[]` エントリを要求（Stage 7 R12 trail 更新による）。agent 実行を更新し、contested case を明示的に表面化、呼び出しまたはエスカレーションを要求。
- **例**: REVIEWER が「シンガポールへのキャリアチェンジ」を否決するが、決定を駆動した SOUL 次元を引用しない。

### F15 — VALUE_HIERARCHY_FAILURE（v1.8.5 新規）
- **定義**: agent が同じ contested case で高優先度ではなく低優先度の SOUL 次元を呼び出した。
- **修復**: value_invocations エントリの `rule_conflict` を調査; SOUL 優先順位を修正（明示的編集 + RFC）するか、呼び出しを誤りとして扱う（回帰ケース追加）。
- **例**: REVIEWER が高リスク決定で「快適さ」（優先度 6）を「認知完全性」（優先度 1）より上に引用。

### F16 — VALUE_DRIFT_FAILURE（v1.8.5 新規）
- **定義**: 複数 run にわたる agent の呼び出しパターンが、SOUL 修正なしに、SOUL の宣言された優先順位から発散した。**システムは前例によって自身の憲法を密かに書き換えている。**
- **修復**: drift をトリアージ — agent 呼び出し動作をリセット（回帰スイート）するか、drift を明示的 SOUL 修正として形式化する。drift が文書化されないまま続行することを絶対に許さない。
- **例**: 3 連続の REVIEWER 決定が類似 case で優先度 1 より優先度 5 の dim を好み、このパターンをフラグしない。

### F17 — VALUE_HALLUCINATION_FAILURE（v1.8.5 新規）
- **定義**: agent が SOUL.md に宣言されていない value を呼び出した。呼び出された `domain_value_id` が解決しない。
- **修復**: 呼び出し時に `domain_value_id` を SOUL.md に対して検証; 未知 id の呼び出しを拒否。特定の捏造 id パターンに対する回帰ケース追加。prompt/訓練データが捏造 value を導入したか調査。
- **例**: ARCHIVER が `dv-tradition-over-novelty` を引用するが SOUL には `dv-truth-over-comfort` のみ。（直接 B confabulation、F17 にもマップ）

## 診断結果（eou-foundry governance.yml より）

すべての診断された失敗が変更になるわけではない。Stage 7 `no_change_record` プロトコルに従って決定を明示的に記録：

- **change**: ECP（Edit-Change-Proposal）を開いた。`meta/decisions/{id}.change.md` 参照。
- **no_change**: 現在の動作を受け入れる決定。Stage 7 §1 schema に従って `meta/decisions/{id}.no-change.yml` に記録（7 必須フィールド: incident_id / eou_id / diagnosis_summary / decision:no_change / rationale / reviewed_by / reviewed_at / reopen_condition）。**記録の欠落は未調査インシデントと区別がつかない。**

## 使用シーン

- v1.8.5 以降、すべての `pro/compliance/violations.md` エントリは A/B/C/D/E/F タグに加えて F1-F17 タグを持つ（Stage 8 Day 24）。
- AUDITOR Mode 3 は F-code で分類された findings を発行（Stage 7 Day 19 F14 scenario）。
- DREAM REM サイクルは agent/entry v2 frontmatter（Stage 6）の failure_modes.known/warning_signs を使用して早期警告パターンを検出。

## ソース出典

eou-foundry @ e4b12ce — `engine/failure-taxonomy.yml` 98 行。life_OS 向けに適応: F14-F17 は captured_workflow.domain_values ではなく SOUL.md domain_values を使用; 既存 A/B/C/D/E/F プロセス分類法へのマッピング追加。
