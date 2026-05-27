---
spec_id: i18n-diff-parity-spec.v1
description: 変更行の三言語整合性検証仕様。`references/*.md` が 2 つの tag 間（または HEAD vs 前回 tag）で変化した時、対応する `i18n/zh/references/<同名>.md` と `i18n/ja/references/<同名>.md` も整合する範囲で変化必須。verify-release check #9 として強制（v1.8.7 で WARN レベル、v1.8.8 で BLOCK 目標）。`pro/compliance/violations.md` で反復する "EN spec 更新したが zh/ja ドリフト" 違反を排除。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman AGENTS.md:118-120 (変更行カバレッジ gate 経由 diff-cover)、"diff カバレッジ" から "diff i18n ミラー" にパターン適応
introduced_in: v1.8.7
referenced_by:
  - .claude/commands/verify-release.md (check 9)
  - pro/agents/auditor.md (Mode 7 M7-5)
---

# i18n Diff 整合性仕様 v1

`references/*.md` の EN spec ファイルが 2 つの tag 間で変化した時、対応する ZH/JA ミラーファイルも整合スコープで変化必須。本仕様が定義する：

1. "変更スコープ" の識別方法
2. EN ↔ zh / EN ↔ ja 対応の検証方法
3. 何が整合（十分）vs ドリフト（失敗）かの定義
4. WARN vs BLOCK エスカレーションタイムライン

## 適用ファイル

すべての三言語ミラー文書：

- `references/*.md` ↔ `i18n/zh/references/*.md` ↔ `i18n/ja/references/*.md`
- `CHANGELOG.md` ↔ `i18n/zh/CHANGELOG.md` ↔ `i18n/ja/CHANGELOG.md`
- `README.md` ↔ `i18n/zh/README.md` ↔ `i18n/ja/README.md`
- `MIGRATION.md` ↔ `i18n/zh/MIGRATION.md` ↔ `i18n/ja/MIGRATION.md`（存在時）

**適用外**（意図的に除外）：

- `SKILL.md` —— 単一ファイル（テーマが出力言語処理）
- `references/hard-rules-index.md` —— 単一ファイル（dev 内部インデックス）
- `pro/gotchas.md` —— 単一ファイル（dev 内部知識ベース）
- `pro/agents/*.md` —— 各 agent 単一ファイル（themes/ が表示処理）
- `pro/*.md`（CLAUDE.md / GEMINI.md / AGENTS.md / GLOBAL.md）—— ホスト固有オーケストレーション、ユーザ向け翻訳ではない
- `meta/**/*` —— ランタイム成果物と RFC
- `themes/*.md` —— theme ファイルはネイティブ文化言語使用

## 変更識別（セクションレベル）

"セクション" は `## ` 二次見出しで識別される。diff 整合性チェックはセクション単位で動作：

1. `git diff <base>..HEAD -- references/<file>.md` で変更行を見つける
2. 各変更行を、最も近い `## ` まで後方に歩いて、その囲み `## ` セクションにマップ
3. ユニークな変更セクション集合を収集
4. 各変更セクションについて、同セクションが `i18n/zh/references/<file>.md` と `i18n/ja/references/<file>.md` でも変化したことを検証

セクションレベル粒度（行レベルではない）は意図的：単語ごとの翻訳は要求されない；**実質的内容整合性** が要求される。

## 対応ルール

### セクション数整合性（HARD）

スコープ内任意のファイルで：

```
count(EN の ## セクション) == count(zh の ##) == count(ja の ##)
```

ドリフト：一言語が他の二言語なしでセクションを追加/削除 = 整合性失敗。

### セクションタイトル整合性（SOFT）

セクションタイトルはネイティブ言語に翻訳**可能**。自動相互参照をサポートするため、翻訳タイトルに英語アンカーを含めることを**奨励**する（v1.8.7 では強制しない）：

- ✅ `## 背景 (Background)` —— タイトル翻訳 + 英語アンカー
- ✅ `## 背景` —— タイトル翻訳、アンカーなし
- ❌ "EN 3 番目セクション" ≠ "zh 3 番目セクション" になるようなセクション並び替え

アンカーあり：アンカーで相互参照。
アンカーなし：**セクション序数位置** で相互参照（1 番目、2 番目、3 番目）。

言語間セクション並び替えは序数相互参照を破壊しフラグ付け対象。

### 変更セクション整合性（HARD）

EN ファイルのセクション N が commit で変更されたら、zh ファイルのセクション N **かつ** ja ファイルのセクション N もその commit **または直前 3 commit** 内で変更必須（翻訳作業のわずかなタイミングオフセット許容）。

"3 commit ウィンドウ" 許容は：EN spec が先に commit、次の 1-2 commit で zh + ja 翻訳が続く —— すべて同じ論理 PR / リリース内、というケース用。

## 検証実装（verify-release check 9）

`.claude/commands/verify-release.md` 内（LLM 駆動、lifeos が md-only —— 実シェルスクリプトなし）、check 9 LLM 手順：

1. base tag（前回リリース tag）と HEAD を決定
2. スコープ内変更ファイルすべてリスト：`git diff --name-only <base>..HEAD -- references/ i18n/zh/references/ i18n/ja/references/ CHANGELOG.md i18n/zh/CHANGELOG.md i18n/ja/CHANGELOG.md README.md i18n/zh/README.md i18n/ja/README.md MIGRATION.md i18n/zh/MIGRATION.md i18n/ja/MIGRATION.md`
3. 変更された各 EN ファイルについて：
   a. 変更セクション識別（diff の行範囲解析、最も近い `## ` まで後方歩く）
   b. 各変更セクションが zh と ja ミラーでも diff を持つことを検証
   c. セクション数整合性を検証（EN セクション数 == zh 数 == ja 数）
4. 発見集約：
   - **PASS**：各変更 EN セクションに対応する zh+ja セクション diff があり、数が揃う
   - **WARN**（v1.8.7 デフォルト）：一部セクションがドリフトするが、EN ファイルの `referenced_by:` が小さい / 修正は待てる
   - **FAIL**：セクションがドリフト、特に HARD RULE を持つ spec

v1.8.7 では、出力は深刻度に関わらず WARN レベル。v1.8.8 は主要ドリフトを BLOCK にエスカレーションを目標。

## WARN vs BLOCK エスカレーションタイムライン

**v1.8.7 ship**（現在）：check 9 は WARN。初回実行は騒音が多い可能性（歴史的ドリフト）；目標は表面化、ブロックではない。

**v1.8.8 目標**（v1.8.7 ship 後 4 週間）：v1.8.7 WARN 出力が安定すれば（ドリフトタイプ列挙可能、誤検出率 <20%）、check 9 を以下カテゴリで BLOCK レベルに昇格：

- `authoritative: true` frontmatter を持つ spec（真実源 spec）
- README + CHANGELOG（ユーザ向けドキュメント）
- MIGRATION（ユーザアップグレード重要）

他の低リスクドリフトは WARN のまま。

**永久 WARN**：セクション並び替え問題 + 実質的内容に影響しない軽微な表現変更。

## 一般的ドリフトパターンと修正

### パターン 1：「次の PR で zh+ja 翻訳する」

EN spec が着地；zh+ja ドリフトが残る。**修正**：PR テンプレートで三言語全て、または明示的 "deferred-to: <PR/issue>" 期限付きを要求。`references/agent-spec.md` v2 により、spec はマージ前に三言語整合性が必要。

### パターン 2：「EN に 1 セクション追加、zh+ja 忘れた」

セクション数が発散。**修正**：マージ前 AUDITOR Mode 7 M7-5 が捕捉。PR は整合性が復元されるか明示的 `i18n-drift-allowed: <reason>` frontmatter 例外があるまで着地不可。

### パターン 3：「EN がセクション名変更、ミラーは未変更」

セクション序数整合性破綻。**修正**：英語アンカー `## 背景 (Background)` を奨励、変名がアンカーマッチで検出可能。

### パターン 4：「EN で実質的内容書き換え、ミラーは typo 修正のみ」

ミラー diff は存在するが浅い。**修正**：check 9 はこの深さ違いを自動捕捉しない —— v1.8.8 で行数比ヒューリスティック導入まで PR レビューで手動フラグ。

## 例外

整合性が要求されない 3 つの正当な例外：

1. **英語アンカーのみ調整** 翻訳タイトル —— 実質変更ではない、ミラー diff 不要
2. **翻訳のみ commit** —— EN を変えずに zh/ja typo を修正 —— commit 自体が整合性復元、違反ではない
3. **`status: legacy` spec** —— legacy 標識された歴史的 spec は継続的整合性不要（内容凍結）

例外は frontmatter で記録：

```yaml
i18n_parity_exception: anchor-only|translation-only|legacy
```

AUDITOR Mode 7 M7-5 がこれら例外を尊重。

## 参照

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.3 F11
- パターン源：`tinyhumansai/openhuman` AGENTS.md:118-120（変更行カバレッジ diff-cover 経由）—— i18n ミラーに適応
- `pro/compliance/violations.md` —— 本仕様が防止を目指す歴史的ドリフト事件
