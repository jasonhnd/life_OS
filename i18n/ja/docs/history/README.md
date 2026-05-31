# 歴史アーカイブ（凍結された v1.7 時代のドキュメント）

このディレクトリは**凍結された歴史ドキュメント**——v1.7 時代の設計スナップショットとユーザーガイドを保持します。すでに置き換えられていますが、システムがどう進化したかを理解するために残しています。ここの各ファイルは `status: legacy` / `authoritative: false` を持ちます。

**これらは現行ではありません。** 現行の権威は：

- `hosts/CLAUDE.md`（+ `hosts/AGENTS.md` / `hosts/GEMINI.md`）—— オーケストレーション協定
- `agents/*.md` —— サブエージェント定義
- `references/*.md` —— 現行データモデル + 仕様
- `docs/` 内の `history/` **以外**すべて —— 現行ユーザードキュメント

## 内容

- **`cortex/`** —— v1.7 Cortex ユーザーガイド（always-on 設計）。Cortex は **v1.8.0 で pull-based に変更**（現行挙動は `hosts/CLAUDE.md` §0.5）。英語版の完全アーカイブは `docs/history/` にあり、`architecture/`、`v1.7-migration.md` などをさらに含みます。
- **`specs/`** —— 退役済み、または置き換え済みの reference specifications。`references/` から移動し、元の `references/*.md` には薄い archive stub だけを残しています。

## なぜ削除せず残すのか

Git 履歴がすでに削除済みファイルをすべて保存しているため、削除しても何も*失われ*ません。ここでは v1.7 の設計根拠を単一の統合アーカイブとして閲覧可能に保ち、`git show` なしで読めるようにしています。

> **インバウンドリンク注記：** 凍結記録—— CHANGELOG エントリ、`compliance/*`、`_meta/rfc/*` ——は移動*前*の元パスを意図的に参照し続けます。これらは当時のパスの歴史記録であり、意図的に**書き換えません**。現行ドキュメントと仕様は新しい `docs/history/...` パスでここにリンクします。
