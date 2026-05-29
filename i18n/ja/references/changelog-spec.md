---
spec_id: changelog.v1
description: CHANGELOG.md entry schema v1（v1.8.5+ 有効）。eou-foundry ECP YAML frontmatter パターンを借用 —— 各 release entry が構造化された YAML frontmatter（version、breaking_changes、alternatives_considered、ordering_dependency、regression_cases_added）+ markdown 本文を持つ。v1.8.5 前のエントリは叙述的のまま（legacy）。
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, self-evolution/ecp/ YAML schema
introduced_in: v1.8.5
---

# CHANGELOG 仕様書 v1

CHANGELOG.md エントリは v1.8.5 以降、構造化された YAML frontmatter + markdown 本文を持つ。v1.8.5 前のエントリは叙述的のまま変更なし（legacy）。

## なぜ構造化 frontmatter

v1.8.4 CHANGELOG エントリは叙述的 —— 人間には有用だが機械パース不可能。eou-foundry が浮き彫りにした 3 つの問題：

1. **alternatives_considered なし**: エントリは何をしたかを記録するが、何を考慮して拒否したかを記録しない。「なぜ X をしなかったか」は歴史から失われる。
2. **ordering_dependency なし**: コホート release（例 ECPs 0015-0017 が一緒に land しなければならない）に明示的宣言がない。cherry-pick が問題を引き起こした。
3. **regression_cases_added なし**: 「これを修正した」から「再発防止のために回帰テストを追加した」へのリンクが暗黙的でしばしば欠落。

v1.8.5+ schema がこれらを修正。

## v1.8.5+ Entry Schema

```markdown
---
version: 1.8.5
date: 2026-05-23
type: major | minor | patch | prerelease
breaking_changes:                          # 箇条書きリスト
  - "SOUL.md schema v1 → v2（X-over-Y formulation 必須）"
  - "wiki entry schema v1 → v2（active+ エントリで outlier slot 必須）"
  - "21 agent frontmatter v1 → v2（authority_level / blast_radius 必須）"
new_features:
  - "F1-F17 失敗分類法（references/failure-taxonomy.md）"
fixes: []

# v1.8.5+ 必須: 少なくとも 1 つの拒否されたオプションと理由
alternatives_considered:
  - option: "v1.8 のまま、6 ヶ月で 30 個の minor patch として ship"
    rejected_because: "30 個の独立した release = 30 個の移行パス；ユーザーは 1 回のアップグレードを希望"
  - option: "叙述的 CHANGELOG を保持（YAML frontmatter なし）"
    rejected_because: "grep 可能性とコホート依存追跡を失う"

# v1.8.5+ 必須: クロス release 依存宣言
ordering_dependency:
  blocked_by: []                           # 先に land しなければならない SHA / version ref
  must_coexist_with:                       # 一緒に ship しなければならない他の commits/refs
    - Stage 0（failure-taxonomy + refactoring-patterns）
    - Stage 1（SOUL v2）
    - Stage 2（wiki v2）

# v1.8.5+ 必須: この release で追加された回帰ケース
regression_cases_added:
  - rc-soul-no-priority
  - rc-soul-no-outlier
  - rc-soul-strawman-y
  - rc-wiki-no-outlier
  - rc-wiki-no-hypothesis
  - rc-agent-no-authority
  - rc-agent-blast-radius-violation
---

## v1.8.5 — Hook Retirement + EOU Hardening · 2026-05-23

> 1 段落の release 概要。

### ハイライト

- ユーザーが見える項目のリスト

### 移行

- ユーザーが前のバージョンからアップグレードする方法
- 実行する slash command（例 `/migrate-soul-v2`）
- 後方互換性ノート（D3 12 ヶ月 legacy 共存）

### 謝辞 / 背景

- （オプションの叙述セクション）
```

## v1.8.5+ 必須 YAML フィールド

v1.8.5 以降の各 release entry:

1. **version**: semver 文字列、例 `"1.8.5"`
2. **date**: ISO YYYY-MM-DD
3. **type**: `major | minor | patch | prerelease` のいずれか
4. **breaking_changes**: 配列（非破壊的 release では空可；空でも必須フィールド）
5. **alternatives_considered**: `option` + `rejected_because` を持つ ≥1 エントリ。「他に何も考慮しなかった」は有効値ではない。
6. **ordering_dependency**: `blocked_by` 配列 + `must_coexist_with` 配列（独立 patch では空可）
7. **regression_cases_added**: `rc-*` id 配列（回帰ケースなしで空可だがレビューすべき —— ほとんどの修正は回帰カバレッジに値する）

`new_features` と `fixes` は推奨だが必須ではない。

## 検証

AUDITOR Mode 7（Stage 10 で追加、v1.8.5 release で計画中）が検証:
- v1.8.5+ の各 release entry が 7 つの必須フィールドすべてを持つ
- `alternatives_considered` が ≥1 実質的エントリ（LLM 啟發式: rejected_because ≥20 文字 + 非自明）
- `ordering_dependency.must_coexist_with` 参照が実際の commits/PRs/Stages に解決
- `regression_cases_added` 参照が `evals/regression-fixtures/` に存在

## Legacy entries（v1.8.5 前）

v1.8.5 前の CHANGELOG エントリ（v1.0.0 から v1.8.4）は叙述的のまま。遡及的移行不要。Schema は v1.8.5 entry から適用。

## 三言語同期

HARD RULE `三言語ドキュメント同期` に従い、YAML frontmatter schema はすべての 3 CHANGELOG ファイルに適用:
- `CHANGELOG.md`（EN）
- `i18n/zh/CHANGELOG.md`（ZH）
- `i18n/ja/CHANGELOG.md`（JA）

3 つすべてが同じ v1.8.5+ entry を同じ YAML frontmatter で持つ必要がある（翻訳された本文だが同じ構造化フィールド）。

## ソース出典

eou-foundry @ e4b12ce — `self-evolution/ecp/*.yml` YAML schema（各 ECP は id / target_eou / target_version_from / target_version_to / problem / proposed_change / alternatives_considered / ordering_dependency を持つ）。life_OS CHANGELOG 向けに適応（release-level vs ECP-level）: 7 フィールドに簡略化、最も重要な 3 つを保持（alternatives_considered / ordering_dependency / regression_cases_added）。
