# `scripts/` に追加してはいけないもの

> **故意的に近空を保つ原則**：このディレクトリは 2 サブディレクトリのみ保持 —— `commands/`（ユーザの `~/.claude/commands/` にインストールされる slash コマンド md ソース）と `prompts/`（ROUTER がインライン読み取り実行する保守ジョブ prompt）。両者とも v1.8.5/v1.8.6 以降 md-only。

## ここに **属さない** もの

1. **任意の `.sh` / `.bash` shell スクリプト** —— `SKILL.md` md-only 本体論的制約（DR-10 v1.8.7）に従う。v1.8.5 は bash hook 層全体を退役；v1.8.7 はその退役を永久化。禁止拡張子：`.sh / .bash / .py / .yml / .yaml / .json / .sql / .db / .sqlite`。
2. **任意の `.py` Python スクリプト** —— 同上。
3. **"自分用だけ"の新 slash コマンド** —— slash コマンドはユーザ向け；明確な name + argument-hint + description が必要、リリースの一部として出荷必須。個人的な一回限りの自動化はあなたの `~/.claude/commands/` に直接置く（本 repo には入れない）。
4. **起動語なしの新保守 prompt** —— `scripts/prompts/*.md` ファイルは `hosts/CLAUDE.md` で文書化された自然言語パターンで ROUTER が起動する。起動語が文書化されていない prompt は死コード。
5. **ユーザ向けドキュメント** —— `docs/` と `gitbooks/` が担当。
6. **ヘルパー関数 / ライブラリ** —— scripts/ にヘルパーライブラリなし；コマンドと prompt は自己完結 LLM 駆動 md ファイル。

## ここに **属する** もの

### `scripts/commands/<name>.md`

ユーザ向け slash コマンド。各々が `description:` と `argument-hint:` frontmatter を持つ単一 md ファイル。`/install-agents` または類似手段で `~/.claude/commands/<name>.md` にインストール。

現在：`compress.md`、`inbox-process.md`、`memory.md`、`method.md`、`monitor.md`、`research.md`、`search.md`。

### `scripts/prompts/<name>.md`

ROUTER がインライン読み取りする内部保守 prompt（インストールステップなし）。`hosts/CLAUDE.md` §"自動起動ルール" で文書化された自然言語パターンで起動。

現在 21+ prompt（advisor-monthly、archiver-recovery、auditor-mode-2、backup、daily-briefing、eval-history-monthly、extract-concepts、inbox-process、migrate-confidence、migrate-from-v1.6、migrate-to-wikilinks、rebuild-concept-index、rebuild-session-index、reindex、research、review-queue、snapshot-cleanup、spec-compliance、strategic-consistency、wiki-decay、wiki-link-audit、wiki-obsidian-upgrade）。

## 新コマンドまたは prompt 追加前 — Minimality Rule チェック

`hosts/CLAUDE.md` Minimality Rule に従う：

1. **ROUTER がネイティブ処理**できるか（新コマンド不要）？
2. **既存コマンド/prompt 拡張**で達成できるか？
3. **agent の既存手順**で吸収できるか？
4. **回帰 fixture** + AUDITOR mode で達成できるか？

どれか一つでも yes ならそれを優先。新コマンド = 永久保守 + インストール/アンインストールロジック + クロスホスト互換性（Claude Code / Gemini CLI / Codex CLI）。

## 参照

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- `SKILL.md` HARD RULE md-only 本体論的制約（DR-10）
- パターン源：`tinyhumansai/openhuman` `.claude/rules/README.md`
