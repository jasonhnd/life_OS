---
spec_id: agent-spec.v2
description: すべての pro/agents/*.md subagent 定義ファイルの標準 frontmatter schema。eou-foundry から 6 facets classification + operating_hypothesis + context_manifest + blast_radius + failure_modes を借用。すべての 23 subagent に適用（router、retrospective、archiver、planner、reviewer、dispatcher、advisor、auditor、strategist、monitor、council、hippocampus、gwt-arbitrator、concept-lookup、soul-check、narrator、narrator-validator、knowledge-extractor + 6 domain agent）。
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, schemas/eou.schema.yml + engine/eou-contract.md
introduced_in: v1.8.5
---

# Agent 仕様 v2

すべての `pro/agents/*.md` subagent 定義ファイルは v2 標準に準拠する YAML frontmatter を**必ず持たなければならない**。v1.8.5 Stage 6 は既存の 23 agent すべてを移行する。

> **なぜ v2**: v1 agent frontmatter には `name + description + tools + model`（4 フィールド）のみ。v2 は eou-foundry から借用した 6 つの構造化フィールドを追加 —— agent 境界が grep 可能、blast radius が明示的、failure modes が文書化される。RFC `_meta/rfc/v1.8.5-cleanup-and-hardening.md` Stage 6 に従う。

## v2 標準 Frontmatter

```yaml
---
# v1 フィールド（保持 — Claude Code Task() ツールがこれらを読む）
name: <agent-id>                       # 小文字、ハイフン区切り、例 retrospective
description: "<1 段落の役割説明>"
tools: Read, Grep, Glob, Bash, Write, Edit, Task   # ツール許可リスト
model: opus|sonnet|haiku|haiku-4-5

# v2 新規: アイデンティティ & バージョン
id: agent-<name>                       # canonical、例 agent-retrospective
version: "1.0.0"                       # semver；実質的な役割変更で bump

# v2 新規: 6 facets classification（eou-foundry eou.schema.yml より借用）
classification:
  function: generate|specify|validate|diagnose|promote|refactor|audit|propose|activate|implement|retire
  target_object: "<この agent が作用するもの、例 'user decision workflow' または 'session archive'>"
  automation_mode: deterministic|LLM_assisted|human_executed|hybrid
  authority_level: suggest_only|draft_only|write_candidate|write_inactive|mutate_active|approve|publish
  risk_level: low|medium|high|critical
  lifecycle_stage: candidate|draft|simulated|pilot|active|monitored|stable|deprecated|retired

# v2 新規: operating_hypothesis（Given/can/within）
operating_hypothesis: |
  Given <トリガー条件>, this agent should produce <出力タイプ> within <risk r>.

# v2 新規: context_manifest（eou eou-contract.md §context_manifest）
context_manifest:
  source_of_truth:     # この agent が authoritative として読むファイル
    - pro/CLAUDE.md
    - pro/GLOBAL.md
  supporting:          # 二次的 context
    - references/relevant-spec.md
  forbidden:           # 読んではいけない — pro/CLAUDE.md §Information Isolation に従う
    - pro/agents/other-peer.md

# v2 新規: blast_radius（eou eou-contract.md §blast_radius）
blast_radius:
  allowed_scope:       # この agent が書ける可能なファイル/パス
    - _meta/runtime/<sid>/<name>-*.json
    - <wiki/SOUL/specific-output-path>
  forbidden_scope:     # この agent が修正してはいけないファイル
    - SOUL.md          # ARCHIVER Phase 2 のみが SOUL candidate を書く
    - foundry/eous/    # 該当する場合
    - pro/agents/      # agent 定義は自己修正してはならない

# v2 新規: failure_modes（eou eou-contract.md §failure_modes）
failure_modes:
  known:              # この agent が文書化された失敗方法
    - "ユーザーメッセージが短いときに必須ステップをスキップ"
    - "context が曖昧なときにパス参照を捏造"
  warning_signs:      # 失敗が起きている観察可能シグナル
    - "出力に 'as discussed before' があるが具体的な引用がない"
    - "出力ステップ数が予期ステップ数 < 期待"
  repair_actions:     # 失敗時に何をするか
    - "agent を明示的なステップリストリマインダーで再起動"
    - "AUDITOR Mode 3 を実行して違反を記録"
---
```

## 必須 v2 フィールド（HARD）

各 `pro/agents/*.md` の frontmatter は以下を**必ず持たなければならない**:

1. **すべての v1 フィールド**: `name`, `description`, `tools`, `model`
2. **アイデンティティ**: `id`, `version`
3. **classification**: 6 facets すべて入力；`target_object` 非空文字列
4. **operating_hypothesis**: 非空、≥30 文字、Given/can/within 形式
5. **context_manifest**: 3 キー存在；`source_of_truth` 非空
6. **blast_radius**: `allowed_scope` と `forbidden_scope` の両方が非空
7. **failure_modes**: 3 キー存在；list は初期空可だが DREAM / AUDITOR 観察を通じて蓄積されるべき

## 検証（AUDITOR Mode 6 —— Stage 6 で追加）

Stage 6 Day 17 で新 AUDITOR mode を追加。チェック:
- **A1**: すべての agent がすべての v2 必須フィールドを持つ
- **A2**: `tools` リストが agent の実際の使用と一致（tools に `Read` がないが agent が Read 呼び出しをする = drift）
- **A3**: `forbidden_scope` がバイパスされていない（agent の `_meta/runtime/<sid>/` 出力 trail が forbidden パスへの書き込みなしを示す）
- **A4**: agent の `failure_modes.known` が `pro/compliance/violations.md` の中でこの agent が関与する任意の違反クラスを含む

発見は `references/failure-taxonomy.md` に従って分類。

## A/B Test Day 15（RFC Stage 6 Day 15 に従う）

D4 に従い、20 agent の一括更新前に 3 つの重要 agent でテスト:
- `retrospective.md`（最重 agent、18 ステップ）
- `archiver.md`（4 phases、breaking changes が起きやすい）
- `reviewer.md`（否決権、judgment が重い）

eval scenarios を実行:
- `evals/scenarios/start-session-compliance.md`（retrospective Mode 0）
- `evals/scenarios/adjourn-compliance.md`（archiver 4 phases）
- `evals/scenarios/reviewer-veto.md`（reviewer judgment 品質）

合格率基準（D4）:
- ≥ 95% baseline: 残り 20 agent の一括更新を続行
- 90-95%: frontmatter を簡略化（最重フィールドを削除、再試行）
- < 90%: その agent の v2 frontmatter をロールバック、理由を `_meta/rfc/v1.8.5-stage6-rollback.md` に文書化

## 各 agent の authority_level ガイド

| Agent | function | authority_level | risk_level |
|---|---|---|---|
| router | propose | suggest_only + write_inactive | medium |
| retrospective | specify | suggest_only + write_inactive | low |
| archiver | publish | publish（最高 — git push + Notion sync を実行）| medium |
| planner | specify | write_candidate | low |
| reviewer | validate | approve（否決権）| high（judgment）|
| dispatcher | implement | mutate_active（domain に dispatch）| medium |
| advisor | diagnose | suggest_only | low |
| auditor | audit | suggest_only + write_inactive（violations.md を書く）| low |
| strategist | propose | suggest_only | low |
| monitor | audit | suggest_only（読み取り専用 ops console）| low |
| council | diagnose | suggest_only | low |
| hippocampus | propose | suggest_only（読み取り専用検索）| low |
| gwt-arbitrator | propose | suggest_only | low |
| concept-lookup | propose | suggest_only | low |
| soul-check | audit | suggest_only | low |
| narrator | specify | suggest_only（ROUTER-internal、テンプレートのみ）| low |
| narrator-validator | validate | suggest_only（v1.8.0 削除、legacy テンプレートとして保持）| low |
| knowledge-extractor | propose | write_candidate（`_meta/runtime/<sid>/extraction/` に書く）| medium |
| 6 domain agents（people/finance/growth/execution/governance/infra）| diagnose | write_candidate（domain report を書く）| medium |

risk_level の根拠: REVIEWER ゲートなしで最終出力を生成する agent はリスクが高い（archiver publish、reviewer veto）。提案/読み取りのみの agent はリスクが低い。

## 各 agent の `lifecycle_stage`（v1.8.5 初期）

すべての 23 agent は v1.8.5 リリースでデフォルト `active`。例外:
- `narrator.md` と `narrator-validator.md` は v1.8.0 R-1.8.0-011 ピボットに従い `deprecated`（citation discipline は ROUTER にインライン化済）；テンプレートとして保持

## 移行

各 agent は手動移行。slash command なし —— agent 定義は十分に安定しており、ユーザー/maintainer による単一 agent の対話的編集で十分。

各 agent のテンプレート:
1. 現在の agent ファイルを読む
2. frontmatter を v2 標準で置換（v1 フィールドを保持、v2 フィールドを追加）
3. agent の実際の動作に従って `classification`、`operating_hypothesis`、`context_manifest`、`blast_radius`、`failure_modes` を入力
4. AUDITOR Mode 6 を実行して検証

## ソース出典

eou-foundry @ e4b12ce。借用:
- 6 facets classification: `schemas/eou.schema.yml` 22-76 行
- operating_hypothesis: `engine/eou-contract.md` 34 行
- context_manifest 三層: `engine/eou-contract.md` 39-42 行
- blast_radius: `engine/eou-contract.md` 75-77 行（allowed_scope/forbidden_scope）
- failure_modes 三件套: `engine/eou-contract.md` 60-63 行

life_OS 向けに適応: agent は Claude Code Task() 起動可能な subagent（EOU ではない）；`tools` フィールドは v1 から保持（Claude Code がツールゲーティングに使用）；A/B テストプロセスは `references/lifecycle-gates.md` pilot→active ゲートから。
