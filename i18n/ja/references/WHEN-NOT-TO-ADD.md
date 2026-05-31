# `references/` に追加してはいけないもの

> **故意的に近空を保つ原則**：このディレクトリは**正規仕様**（`*-spec.md`）と**共有参照テーブル**（`domains.md`、`failure-taxonomy.md` など）のためのもの。"agent に読ませたい任意のドキュメント"を投げ込む場所ではない。

## ここに **属さない** もの

1. **セッションごとのレポート、ランタイム成果物、audit trails** —— 例 "2026-05-25 archiver 出力"。→ 行き先：`meta/runtime/<sid>/` または `meta/sessions/<sid>.md`。
2. **ユーザ向けチュートリアル / クイックスタート** —— 例 "lifeos インストール方法"。→ 行き先：`README.md` / `docs/` / `gitbooks/`。
3. **内部設計メモ / ブレインストーミング / ドラフト** —— 例 "v2.0 cascade seal のアイデア"。→ 行き先：`meta/rfc/v<X.Y>-*.md`（RFC）または `meta/workpad/`（導入されれば）。
4. **Agent 定義または theme ファイル** —— それぞれ `agents/` と `themes/` の専属領域。
5. **規範性のない純粋なナラティブ** —— 例 "lifeos 各バージョンの歴史"。→ 行き先：`CHANGELOG.md` / RFC 参考。
6. **三言語ミラーなしの spec** —— 各 `references/*-spec.md` はマージ前に `i18n/zh/references/<同名>.md` と `i18n/ja/references/<同名>.md` を準備必須。不完全な spec は不可。
7. **`spec_id` / `status` / `authoritative` frontmatter なしの spec** —— 既存 spec を参考に必須 schema を確認。

## ここに **属する** もの

以下を満たす正規仕様：
- ≥2 agent が参照する schema、フォーマット、契約を定義
- `spec_id: <name>.v<N>`、`status: active|legacy|proposal`、`authoritative: true|false`、`introduced_in: v<X.Y>` frontmatter 含む
- 三言語ミラー準備済（`i18n/zh/references/` + `i18n/ja/references/`）
- `referenced_by:` 存在（少なくとも 1 つの agent / コマンド / SKILL.md からの前方リンク）
- 該当トピックの**唯一の真実源**（他所に重複 spec なし）

## 新 spec 追加前 — Minimality Rule チェック

`hosts/CLAUDE.md` Minimality Rule（v1.8.5 Stage 7）に従い、まず 6 つの質問：

1. **ルール**（`hosts/CLAUDE.md` または SKILL.md 内）で達成できるか？
2. 既存 spec に **schema フィールド追加**で達成できるか？
3. 既存 spec に**セクション追加**で達成できるか？
4. **回帰ケース**（`evals/scenarios/*.md`）で達成できるか？
5. **AUDITOR audit rule** で達成できるか？
6. `hosts/CLAUDE.md` に**人手チェックリスト追加**で達成できるか？

どれか一つでも yes なら、低コスト選択肢を優先。新 spec = 3 ファイル（EN + zh + ja）+ 永久 referenced_by グラフ保守 + i18n diff parity チェック義務。

## 参照

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- パターン源：`tinyhumansai/openhuman` `.claude/rules/README.md`
- 連携：`references/i18n-diff-parity-spec.md`（v1.8.7 が本ディレクトリ全ファイル三言語整合を保証）
