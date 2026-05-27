# `meta/` に追加してはいけないもの

> **故意的に近空を保つ原則**：このディレクトリは**ランタイム成果物** + **歴史スナップショット** + **RFC 文書**のためのもの。システムの作業記憶であり、正規 spec や agent 定義の置き場所ではない。

## ここに **属さない** もの

1. **正規仕様** —— 例 "audit trail の動作方式定義"。→ 行き先：`references/<name>-spec.md`（三言語ミラー込み）。
2. **Agent 定義** —— `pro/agents/` 専属。
3. **ユーザ決定または知識** —— 例 "信託構造採用の決定"。→ 行き先（ユーザの second-brain）：`decisions/` または `meta/wiki/`。
4. **SOUL.md または theme ファイル** —— SOUL はユーザ second-brain ルートへ；theme は `themes/` へ。
5. **ビルド出力 / コンパイル成果物** —— lifeos にビルドステップなし（md-only）。`meta/dist/` や `meta/build/` を加えたくなったら、間違った問題を解いている。
6. **forbidden_extensions に一致する任意のファイル** —— `.sql / .json / .sh / .bash / .py / .yml / .yaml / .db / .sqlite`（`SKILL.md` md-only 本体論的制約参照）。DR-10 v1.8.7 により非交渉。

## ここに **属する** もの

- `meta/runtime/<sid>/*.md` —— セッションごとの audit trails（R12 + R13 schema）
- `meta/rfc/v<X.Y>-*.md` —— リリース用 RFC 文書
- `meta/sessions/<sid>.md` —— セッションごとのアーカイブ
- `meta/wiki/` —— ユーザの知識ベース（ユーザ second-brain 内、dev repo にはない）
- `meta/concepts/` —— Cortex シナプスグラフ（ユーザ second-brain 内）
- `meta/snapshots/soul/<sid>.md` —— adjourn 時の SOUL スナップショット
- `meta/journal/` —— DREAM レポート
- `meta/outbox/<sid>/` —— git sync 前の保留書き込み
- `meta/compression/<sid>-compress-<ts>.md` —— 手動 `/compress` 出力
- `meta/release-notes/v<X.Y>.md` —— リリースノート
- `meta/decisions/<id>.md` —— インシデント決定記録（`no-change` 等）

## Dev-repo vs ユーザ second-brain の区別

lifeos **dev repo** の `meta/` には：`rfc/` + `release-notes/` + `methods/` + 歴史 `v1.8.4-snapshot/`。**含まない**：`sessions/` / `concepts/` / `wiki/` —— これらはユーザ second-brain のランタイムにのみ存在。

`meta/` に触れる新 spec や機能を書く際、パスが以下のどちらかを明確に：
- **dev repo** の `meta/`（lifeos ソースコード）—— 例 `meta/rfc/`、`meta/release-notes/`
- **ユーザ second-brain** の `meta/`（ユーザランタイムデータ）—— 例 `meta/sessions/`、`meta/runtime/`、`meta/wiki/`

両者の混同は反復する落とし穴（seed 後の `pro/gotchas.md` 参照）。

## 参照

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- パターン源：`tinyhumansai/openhuman` `.claude/rules/README.md`
- 連携：`SKILL.md` HARD RULE md-only 本体論的制約（DR-10）
