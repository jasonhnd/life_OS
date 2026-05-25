# `themes/` に追加してはいけないもの

> **故意的に近空を保つ原則**：このディレクトリは**表示層プレゼンテーション**のみ。各 theme は 9 テーマ（3 言語 × 3 文化設定）の表示名、emoji、tone を定義する。新 theme 追加は lifeos で最も高価な操作の一つ —— 以降の新 agent / spec / コマンドすべてが、その役割名コストを払う必要がある。

## ここに **属さない** もの

1. **エンジンロジック** —— 例 "archiver phase 2 で何をするか"。→ 行き先：`pro/agents/archiver.md`。
2. **Spec 内容** —— 例 "session frontmatter 定義"。→ 行き先：`references/session-index-spec.md`。
3. **Agent 挙動の翻訳** —— theme は**表示名のみ**を翻訳、**挙動は翻訳しない**。挙動は theme 間で完全同一。
4. **"とりあえず追加"の新文化設定** —— 下記 "新 theme 追加前" 参照。
5. **サブドメインの theme バリアント** —— 例 "zh-classical-finance" で金銭フォーカス表示名。Theme はセッション全体、ドメイン単位ではない。
6. **ユーザごとカスタマイズ** —— ユーザは `_meta/config.md` を編集して theme を切り替える；新 theme を追加するわけではない。

## ここに **属する** もの

以下すべてを含む完全 theme ファイル：
- `Role Mapping` テーブル —— SKILL.md の全エンジン役割を表示名 + emoji + レポートラベルにマップ
- `Domain Mapping` テーブル —— 6 ドメインを theme 等価物にマップ
- `Trigger Words` —— theme 固有の起動語（zh-classical の "上朝" 等）
- `Tone` —— theme が使うナラティブ声

いずれかが欠けると theme は不完全で、エンジン ID にフォールバック（醜い）。

## 新 theme 追加前 — 高ハードル

新 theme は以下を意味する：
- 既存全 agent の表示名翻訳必要
- 将来の全 agent（v1.8.7 の memory-keeper 等）が本 theme に行追加必須
- Trigger words 慎重選択（既存 theme と衝突不可）
- Tone / 文化フレーミングが 22+ agent 全体で内部整合
- 三言語整合（既存 theme の翻訳の場合）

**追加前の真の質問**：ユーザ（またはコミュニティ）が実際にこの theme を求めているのか、それともエンジニアリングのためのエンジニアリングか？後者なら追加しない。

## 現在出荷中の theme（9 個）

| 言語 | Themes |
|------|--------|
| 英語 | `en-roman.md`（ローマ共和国）/ `en-usgov.md`（米国政府）/ `en-csuite.md`（企業 C-Suite） |
| 中文 | `zh-classical.md`（三省六部）/ `zh-gov.md`（中国政府）/ `zh-corp.md`（公司部门） |
| 日本語 | `ja-meiji.md`（明治政府）/ `ja-kasumigaseki.md`（霞が関）/ `ja-corp.md`（企業） |

10 番目 theme 追加にはユーザ向け正当化 + RFC エントリ + 保守コミットメントが必要。

## 参照

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12 + §9 Q3（memory-keeper を全 9 theme に同時追加 —— コストを示す）
- パターン源：`tinyhumansai/openhuman` `.claude/rules/README.md`
- 連携：SKILL.md `## Theme System`
