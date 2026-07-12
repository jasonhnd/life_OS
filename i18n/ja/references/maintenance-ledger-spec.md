---
spec_id: maintenance-ledger-spec.v1
description: meta/maintenance-ledger.md のフォーマットとプロトコル —— 各メンテナンスジョブが最後にいつ実行されたかを記録する vault 内の単一ファイル。すべての scripts/prompts/*.md ジョブが完了時にスタンプする；session 開始時にスタンプを宣言された cadence と比較し、最大 3 行の overdue 行を提示する（nudge のみ、決して自動実行しない）。「cadence ルールは紙の上にだけ存在し、ドリフトが静かに複利する」ギャップを閉じる（issue #1 A2）。
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - agents/retrospective.md (Step 0.5 maintenance-overdue marker + Mode 2 item 7)
  - hosts/CLAUDE.md (§session-start status scan)
  - scripts/prompts/*.md (final "ledger stamp" step in every job)
---

# Maintenance Ledger Specification v1

v1.8.0 pivot が cron を除去して以来、すべてのメンテナンスはユーザー起動である。あるジョブが最後にいつ実行されたかを記録するものはなく、期限超過を促すものもなかった —— 本番での証拠：「>4h → light patrol」ルールが 7 日以上のギャップと共存し、月次 deep patrol は約 13 日遅れで実行され、wiki インデックスのドリフトはパトロールが捕捉するまでに +60 エントリに達した。この spec は、cron を復活させることも v1.8.0 の「自走メンテナンス禁止」スタンスに違反することもなく、陳腐化を**人間の在席が保証される唯一の瞬間 —— session 開始時 —— に可視化**する。

## ファイルフォーマット

vault ごとに 1 ファイル：`meta/maintenance-ledger.md`。単一の markdown テーブル、ジョブごとに 1 行、ジョブ名のアルファベット順にソート：

```markdown
# Maintenance Ledger

Stamped by each `scripts/prompts/<job>.md` on completion. Read by session start
(retrospective Step 0.5). Cadences per `references/maintenance-ledger-spec.md`.

| job | cadence | last_run |
|-----|---------|----------|
| auditor-mode-2 | 7d | 2026-07-01 |
| backup | 7d | 2026-06-28 |
| wiki-link-audit | 7d | 2026-06-20 |
```

フィールドルール：

- **job** —— プロンプトの basename から `.md` を除いたもの（例 `wiki-link-audit`）。
- **cadence** —— `<N>d`（日数値）、`on-demand`、`once` のいずれか。各ジョブのプロンプトがスタンプする cadence を宣言する；ledger の行はそれをコピーし、overdue の計算がこの 1 ファイルだけで済むようにする。
- **last_run** —— 実際の `date` コマンドによる `YYYY-MM-DD`（捏造禁止 —— SOUL スナップショットと同じ契約）。

## スタンププロトコル（すべてのジョブ、最終ステップ）

すべての `scripts/prompts/*.md` ジョブは ledger スタンプステップで終わる：

1. `meta/maintenance-ledger.md` を読む。存在しない場合、上のヘッダーと 0 行で作成する。
2. **自分の行を upsert する** —— このジョブの行が存在すればその場で置き換える；なければアルファベット順を保って挿入する。ジョブの行を決して重複させない。
3. `| <job> | <cadence> | <today> |` を書き込む。

スタンプは冪等であり、コストは Read 1 回 + Write 1 回。`cadence: once` や `on-demand` のジョブもスタンプする —— その行はジョブが実行されたことを記録するだけで、決して overdue にはならない。

## Session 開始時の overdue チェック（nudge のみ）

session 開始時（retrospective Mode 0 Step 0.5；Mode 2 Review item 7 でも）：

1. `meta/maintenance-ledger.md` を読む。ファイルがない場合 → `Maintenance ledger: not yet initialized (jobs stamp it on completion)` を出力してスキップ —— 読み取り時に作成してはならない（do NOT）。
2. 日数値 cadence `<N>d` を持つ各行について：`days_overdue = (today - last_run) - N`。`on-demand` / `once` の cadence の行は決して overdue にならない。
3. いずれかの `days_overdue > 0` の場合：**最大 3 行**（HARD CAP）の `## Overdue maintenance` ブロックを、overdue 比率 `(today - last_run) / N` の降順で出力する：

   ```
   ⚠️ overdue: wiki-link-audit (12d since last run, cadence 7d)
   ⚠️ overdue: auditor-mode-2 (9d since last run, cadence 7d)
   (+2 more — see meta/maintenance-ledger.md)
   ```

   overdue のジョブが 3 個を超える場合、3 行目は `(+N more …)` のロールアップになる。
4. 何も overdue でない場合：**沈黙**（ブロックなし、「all fresh」行もなし —— 健全パスではゼロノイズ）。

**Overdue = nudge のみ。overdue チェックからメンテナンスジョブを自動実行することは決してしない（NEVER）。** 何を起動するかはユーザーが決める。自動実行は、v1.8.0 pivot が除去した自走メンテナンスをまさに再導入することになる。

## v1.10 以前のメカニズムとの関係

v1.10 以前、retrospective Step 0.5 は「10 個のメンテナンスジョブの最終実行タイムスタンプをそれぞれの保存場所から」読んでいた —— すなわち各ジョブのレポートパス（例 `meta/eval-history/wiki-link-audit-*.md` の mtime）であり、たまたま日付付きレポートを書くジョブしかカバーせず、boot ごとに N 回の glob を要した。ledger はそれを置き換える：**1 ファイル、1 Read、書き込み時維持** —— v1.9.2 の session INDEX 変更と同じ、scan-time より write-time を取る動きである。旧来のジョブごとのレポートパスは証拠として残るが、もはや overdue チェックの真実の源ではない。

## Eval アンカー

`evals/scenarios/v1.10-maintenance-ledger.md` —— 陳腐化した ledger → nudge ブロックが出現する（≤3 行）；新鮮な ledger → ブロックは出力されない。
