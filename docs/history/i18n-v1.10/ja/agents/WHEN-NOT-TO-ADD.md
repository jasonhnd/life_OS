# `agents/` に追加してはいけないもの

> **故意的に近空を保つ原則**：このディレクトリは **subagent 定義** のみを置く。各 `*.md` は v2 agent-spec frontmatter を持つ Task で起動可能な役割を定義する。非 agent ファイルを加えるとディレクトリ用途を希薄化し、ROUTER の役割発見を誤導する。

## ここに **属さない** もの

1. **汎用ヘルパー / ユーティリティ prompt** —— 例 "commit message 起草を手伝う markdown"。→ 行き先：`.claude/commands/`（slash コマンド）または `scripts/prompts/`（保守 prompt）。
2. **Spec / schema ドキュメント** —— 例 "audit trail ファイルがどう見えるか"。→ 行き先：`references/<topic>-spec.md`。
3. **ユーザ向け参照ドキュメント** —— 例 "auditor agent の使い方"。→ 行き先：`docs/` または `gitbooks/`（再導入時）。
4. **セッションごとの状態、audit trails、gotchas** —— 例 "このセッションの archiver 出力"。→ 行き先：`meta/runtime/<sid>/`（audit trails）または `gotchas.md`（教訓）。
5. **Theme ファイル（display 名 / emoji / tone）** —— 例 "中世設定の新 theme"。→ 行き先：`themes/<name>.md`。
6. **v2 agent-spec frontmatter なしの agent** —— 役割が正当でも、`references/agent-spec.md` v2（6 facets + operating_hypothesis + context_manifest + blast_radius + failure_modes）に準拠してから着地すること。

## ここに **属する** もの

以下を満たす subagent 定義：
- Task で起動可能（Claude Code が `Task(<name>)` で起動できる）
- 責任が一意で重複しない（本ディレクトリの既存 agent と照合）
- v2 agent-spec frontmatter 完備
- blast radius 明示（書き込み許可 / 禁止ファイル宣言）
- 失敗モード + 復旧アクションが文書化されている

## 新 agent 追加前 — Minimality Rule チェック

`hosts/CLAUDE.md` Minimality Rule（v1.8.5 Stage 7）に従い、まず 6 つの質問：

1. **ルール**（`hosts/CLAUDE.md` 内）で達成できるか？
2. **schema フィールド**（`references/*-spec.md` frontmatter 内）で達成できるか？
3. **バリデータ**（slash コマンドまたは AUDITOR mode）で達成できるか？
4. **回帰ケース**（`evals/scenarios/*.md`）で達成できるか？
5. 既存 agent 実行フロー内の **stop condition** で達成できるか？
6. 関連ドキュメントに**人手チェックリスト**追加で達成できるか？

どれか一つでも yes なら、低コスト選択肢を優先。新 agent = 高コスト（永久保守、AUDITOR ターゲット、9 theme での名前、三言語 spec、audit trail schema、blast radius 強制）。コスト/便益閾値は高い。

## 参照

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12
- パターン源：`tinyhumansai/openhuman` `.claude/rules/README.md`（"This directory is intentionally near-empty. Stale rules actively mislead agents."）
- 連携 spec：`references/agent-spec.md`（v2 frontmatter 標準）
