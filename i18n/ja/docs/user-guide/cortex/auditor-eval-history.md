---
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# AUDITOR Eval-History · システムの自己フィードバックループ / AUDITOR Eval-History

> パンくず: [← Cortex 総覧](./overview.md) · [← 製品入口:ユーザーガイド索引](../index.md)

> Life OS は背後の Claude モデルをファインチューニングできませんが、**自身のルールをファインチューニング**できます。AUDITOR は session 終了時に 10 次元で自己採点し、結果を `_meta/eval-history/{date}-{project}.md` に書き込みます。次回 Start Session で RETROSPECTIVE が直近 10 件をスキャンし、システミックなパターンを検出します——連続 3 回 adjourn 不完全?narrator 引用失敗率 >20%?これらは「システミックな問題検出」ブロックとしてブリーフィングに出現します。あなたはシステムのユーザーであるだけでなく、これらのルールを調整する人でもあります。

## 一文概説 / One-Line Overview

Eval-history は Life OS の**構造化自己評価フィードバックループ**です。AUDITOR が書き、RETROSPECTIVE が読み、あなたはサマリーを見ます。これは Hermes RL 訓練ループの spec 層相当——モデルファインチューニングはしないが、「品質シグナルをディスクに書く → 次回 session で人間に露出する」。シグナルは人間の注意を通じてシステム行動を変える、gradient descent ではなく。

---

## なぜこの層を追加するのか / Why Add This Layer

### Hermes から得た教訓

[Hermes Lesson 5](../../../../devdocs/research/2026-04-19-hermes-analysis.md) のコア: **自己評価はシステムにフィードバックされるべき、一回性のレポートであってはならない**。

v1.6.2a の AUDITOR は既に各決定終了時に各 agent を採点していました——**PLANNER の次元網羅性は?REVIEWER の封駁に根拠は?domain スコアと分析は一致?**——しかしこれらの評価は**本 session の Summary Report にのみ存在**。session 終了で蒸発。

**次回 session の AUDITOR は前回 AUDITOR が何を発見したかを知らない**。パターン的品質問題(例えば archiver が直近 3 回 4 phase を完走していない)は全く見えない——各 session が孤立したイベントとして審査される。

### v1.7 の閉ループ

Eval-history は AUDITOR の採点を **`_meta/eval-history/` に永続化**——session ごとに `.md` ファイル、YAML frontmatter に 10 次元スコア、body に 長所 / 短所 / 推奨。

**キーとなる二階機構**: RETROSPECTIVE Mode 0 が Start Session ごとに**直近 10 件**を読み、**5 つの検出ルール**でシステミックパターンを探す。検出された警告はブリーフィングに直接出現:

```
⚠️ システミックな問題検出:
- 退朝完整度連続 3 回 ≤6 → archiver subagent 起動を確認推奨
- Wiki 抽出品質が 4/15 から下降 → 今回重点関注推奨
- Narrator 引用失敗率 25% (閾値 20%) → narrator 層でシグナル幻覚の可能性
```

**これは人間の注意で行う「強化学習」**。モデルは変わらないが、**あなた**が毎回上朝でこれらの警告を見て、config / spec / skill を修正し始める——システムはあなたを通じて進化する。

---

## ユーザー側に見えるもの / What the User Sees

### シナリオ A: 通常 session 終了

全朝議決定を完了したばかり。session が Step 8 AUDITOR に到達。

AUDITOR が本評価を行う同時に、`_meta/eval-history/2026-04-20-passpay.md` を**書き込む**(ファイル名形式:`{YYYY-MM-DD}-{project}.md`、同日同プロジェクト複数回は `-{HHMM}` 追記)。

あなたは直接このファイルを見ませんが、いつでも開けます。内容構造:

```yaml
---
eval_id: 2026-04-20-1432-passpay
session_id: claude-20260420-1432
evaluator: auditor
evaluation_mode: decision-review
date: 2026-04-20T14:32:00+09:00
scores:
  information_isolation: 9
  veto_substantiveness: 8
  score_honesty: 7
  action_specificity: 9
  process_compliance: 10
  adjourn_completeness: 10
  soul_reference_quality: 8
  wiki_extraction_quality: 6
  cognitive_annotation_quality: 7
  citation_groundedness: 9
violations:
  - type: soul_dimension_ignored
    agent: REVIEWER
    severity: medium
    detail: "REVIEWER が dormant 次元 '財務独立' を引用せず、決定と直接関連"
agent_quality_notes:
  PLANNER: "次元分割完整。SOUL 参照到位。"
  REVIEWER: "封駁 1 回合理。ただし dormant 次元を無視。"
  FINANCE: "分析とスコア整合。"
  ...
---

## Summary
全朝議完走。information isolation 良好に維持。主要問題は REVIEWER が dormant
SOUL 次元を漏らしたこと、本決定は財務独立トピックに直接関わる。

## Strengths
- Information isolation 9/10: PLANNER が ROUTER reasoning を引用せず、domains 間に
  交差汚染なし
- Process compliance 10/10: 11 ステップ完走、違反なし
- Adjourn completeness 10/10: archiver 4 phase 全走、Notion 同期実行

## Weaknesses
- soul_reference_quality 8/10: REVIEWER が dormant 次元を漏らした (具体 violations 参照)
- wiki_extraction_quality 6/10: 今回の wiki 候補が既存エントリと高重複、新規再利用可能
  結論なし

## Systemic Pattern Observations
連続 2 回 REVIEWER が dormant 次元を漏らす (前回は 2026-04-17 passpay session)。
次回も漏れる場合、reviewer.md に「dormant 次元の関連性を審査」を明示する調整推奨。

## Recommendations
- REVIEWER: checklist に「本決定は dormant 次元の領域に関わるか?」を追加
- ARCHIVER: wiki 候補重複除去ロジック要審査、現在 canonical との重複を許容している模様
```

**すべてのスコアは 0–10 整数**——半点不可、AUDITOR に commitment を強制。

### シナリオ B: 次回 Start Session でシステミック問題検出

翌朝新 session を開く。RETROSPECTIVE Mode 0 が直近 10 件 eval-history をスキャンし検出:

- `adjourn_completeness` 直近 3 回それぞれ 5, 4, 6(連続 3 回 ≤6)
- `soul_reference_quality` が 2 session で dormant 次元を漏らす
- `citation_groundedness` が直近 10 回で 3 回 <8

ブリーフィングに出現:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Systemic Issue Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- 退朝完整度連続 3 回 ≤6 → archiver subagent が完整起動していない可能性
  (直近値 5, 4, 6 vs 期待 ≥8)
  推奨: archiver agent 定義が ROUTER により分段呼び出しされていないか確認、
  end-to-end 単回 invocation に修復

- REVIEWER が連続 2 回 dormant SOUL 次元を漏らす
  推奨: 本 session 開始前に `SOUL.md` の dormant 次元を手動レビュー、
  または reviewer.md を調整

- Narrator 引用失敗率 25% (閾値 20%) → 直近 10 session で 3 回
  citation_groundedness <7
  推奨: 本 session では奏折中 [S:] [C:] 引用付き claim に重点関注、trace で検証

(具体的にどの session か見るには _meta/eval-history/ を確認)
```

**このブロックは DREAM Auto-Triggers の直下、Strategic Overview の前に配置**——固定位置、強制可視。システミック問題がないときは**全ブロック省略**(placeholder 非表示)。

### シナリオ C: 特定次元を能動クエリ

「直近の adjourn_completeness のトレンド」が知りたい:

```bash
grep -h "adjourn_completeness" _meta/eval-history/*.md | tail -10
```

結果:

```
  adjourn_completeness: 10
  adjourn_completeness: 9
  adjourn_completeness: 5
  adjourn_completeness: 4
  adjourn_completeness: 6
  adjourn_completeness: 10
  ...
```

3 連低スコア問題が明確に見える——いつから始まり、いつ修復され、修復前後で何が変わったか。

---

## 10 採点次元 / The 10 Scoring Dimensions

### v1.6.2a から継承した 8 つ

| # | 次元 | 測るもの |
|---|------|---------|
| 1 | `information_isolation` | 上流 context 漏洩は起きていない?PLANNER は ROUTER reasoning を見ていないか? |
| 2 | `veto_substantiveness` | REVIEWER の封駁は 8 項 checklist 実証ベースか、rubber-stamp か? |
| 3 | `score_honesty` | domain スコアは自身の分析テキストと一致? |
| 4 | `action_specificity` | action item に owner / deadline / 具体動作があるか? |
| 5 | `process_compliance` | 状態機は end-to-end 完走?ステップ飛ばしは? |
| 6 | `adjourn_completeness` | archiver 4 phase 全走?Completion Checklist は TBD ではない? |
| 7 | `soul_reference_quality` | REVIEWER が引用する SOUL 次元は完整か(dormant + conflict を含むか)? |
| 8 | `wiki_extraction_quality` | wiki 候補が再利用可能、privacy クリーン、domain 正しいか? |

### v1.7 新規 2 つ

| # | 次元 | 測るもの |
|---|------|---------|
| 9 | `cognitive_annotation_quality` | hippocampus 検索した session と concept は決定で本当に使われたか?関連度採点と実際の影響は一致? |
| 10 | `citation_groundedness` | narrator 引用は実在 + 内容が claim を支持する artifact を指すか? |

各次元には**3 つのアンカー**(0 / 5 / 10)、AUDITOR に具体例参照を提供。例えば `information_isolation`:

- **10**: PLANNER に ROUTER reasoning の認識なし。REVIEWER は規画ドキュメントのみ受取。交差汚染なし。
- **5**: 軽度漏洩——ROUTER がどの domain がトリガーされるか示唆、またはある domain が「前述審査で言及された」と発言。
- **0**: 明白な cross-contamination。REVIEWER が PLANNER の raw 思考を見る、または 2 domain が相互言及。

---

## システミック問題検出 · 5 つのルール / Systemic Issue Detection

RETROSPECTIVE Mode 0 が直近 10 件 eval-history をスキャンし適用:

### ルール 1 · adjourn_completeness 連続低スコア

**3+ 回連続 session で `adjourn_completeness < 6`** → 警告: 「archiver subagent が完整起動していない可能性」

これは典型的な v1.6.x バグ——ROUTER が ARCHIVER の各 phase 間に割り込む split flow。3 回繰り返しは偶発ではなく構造的問題。

### ルール 2 · wiki_extraction_quality 下降トレンド

**5+ 回連続 session で `wiki_extraction_quality` が下降トレンド** → 警告: 「ARCHIVER Phase 2 がこっそり extraction をスキップしている可能性」

下降トレンドは「低スコア」より重要——9 から 5 への下降は何かが変わった証、5 がまだ低スコアでなくても。

### ルール 3 · citation_groundedness 高失敗率

**直近 10 session で citation resolution 失敗 >20%** → 警告: 「narrator 層がシグナルを幻覚している」

narrator の最も危険な失効モード——引用が存在しない artifact を指す。[narrator-citations.md](./narrator-citations.md) 参照。

### ルール 4 · cognitive_annotation_quality 持続低

**5+ 回連続 session で `cognitive_annotation_quality < 5`** → 警告: 「hippocampus 検索の調整が必要」

INDEX.md が古い、Wave 1 prompt 失調、または concept graph が過度に疎な可能性。

### ルール 5 · process_compliance 反復違反

**同一 `violations[].type` が直近 30 日で 3+ 回出現** → **user-patterns.md に昇格**

最も teeth のあるルール: 同類違反(例えば "adjourn_phase_skip")が繰り返し出現すると、eval-history から「卒業」して `user-patterns.md` の tracked behavioral pattern になる。次回 session の **ADVISOR** はそれを観察として直接 surface:

> 「観察: 直近 1 ヶ月で 4 回、adjourn 前に操作を挿入しています——これは archiver phase を中断します。今回は先に adjourn を完走してから操作しますか?」

システム自体が変わる——eval-history の静黙採点から、ADVISOR の能動提醒へ。

### 問題検出 ≠ 自動修復

**AUDITOR は決してあるモジュールを自動閉鎖したり spec を改変したりしない**。ユーザー決定 #4: **預設 kill criteria なし**。ルール 1–4 の警告はすべて advisory——**あなた**が reviewer.md を改変するか、cortex config を調整するか、eval-history の誤判定を手動クリーンアップするかを決定。

---

## 書き込みタイミングと条件 / Write Timing & Conditions

### AUDITOR が eval-history を書くタイミング

- **全朝議 Step 8** 終了時 (end-to-end 決定完了)
- **Express 快速レーン**が十分深い Brief Report を生んだ場合 (毎回の Express で書くわけではない——浅層クエリには評価対象がない)
- **Patrol Inspection** トリガー時 (RETROSPECTIVE Mode 0 が `lint-state.md >4h` 検出、巡検開始、書き込み時 `evaluation_mode: patrol-inspection`)

### AUDITOR が書かない場面

- **ROUTER direct-handle**(雑談、翻訳、簡単なクエリ——subagent ワークなく評価対象なし)
- **STRATEGIST session**(異なる評価領域——思想家対話品質であって決定品質ではない)
- **初回 session / second-brain 空**(決定発生なし)
- **session が PLANNER 産出前に abort**(評価内容なし)

### 書き込み失敗の容錯

eval-history 書き込み失敗(ディスク満杯、権限エラー、パス欠落)時:

- AUDITOR が Decision Review で失敗を報告
- **session 継続走行**——ADVISOR や ARCHIVER をブロックしない
- 失敗自体は次回 session の `process_compliance violation` として記録

---

## Immutability · 永不編集 / Never Edit

**Eval ファイルは作成後決して編集しない**。ある評価が誤りと発見した場合:

- **元ファイル改変せず**
- **次回 session** に AUDITOR が新 eval ファイルを書き、反論説明を含める
- 元ファイルは履歴として**保持**

これは重要です——履歴評価を編集できるなら、RETROSPECTIVE のシステミック検出は信頼できなくなります。AUDITOR の自己審査は append-only、論理的にブロックチェーンのように。

---

## ストレージとアーカイブ / Storage & Archival

| 特性 | 詳細 |
|-----|------|
| **単ファイルサイズ** | ~5KB |
| **1000 session の総占有** | ~5MB |
| **保持ポリシー** | **永久保持**、自動削除なし |
| **アーカイブトリガー** | ファイル >6 ヶ月 + 明示 `tools/stats.py --compress-old` |
| **アーカイブ先** | `_meta/eval-history/_digest/{YYYY-Q}.md`(四半期サマリー)、元ファイル → `_meta/eval-history/_archive/` |
| **digest 内容** | ヘッダースコア + システミックパターン、個別 session 依然アクセス可 |
| **Notion 同期** | **同期なし**(ユーザー決定 #12——ローカル内省資産、Notion に push すると mobile view にノイズが多く消費者なし) |

---

## ユーザーアクション · できること / User Actions

### 1. 直近トレンドの確認

```bash
ls -t _meta/eval-history/*.md | head -10
```

1 件開き、frontmatter の scores ブロックを確認、自身の期待と対比。

### 2. 特定次元のトレンド確認

```bash
# 直近 10 件の cognitive_annotation_quality 値
grep -h "cognitive_annotation_quality" _meta/eval-history/*.md | tail -10

# 直近 10 件の全 violations
grep -A 3 "violations:" _meta/eval-history/*.md | tail -40
```

### 3. tools/stats.py で月次レポート

```bash
uv run tools/stats.py --month 2026-04
```

その月のスコア分布、システミックパターン、violation type 統計を出力。

### 4. tools/reconcile.py でオーファンを確認

```bash
uv run tools/reconcile.py
```

検出:
- session あるが eval なし
- eval あるが session_id が存在しないファイルを指す
- YAML schema フィールド欠落
- violations の agent 名が既知リスト外

### 5. システミック問題警告への応答

ブリーフィングでシステミック問題を見たら:

- **本 session で標的関注**——警告が「本 session で X に重点関注」と言っている、従う
- **agent spec を改変**——例えばシステムが REVIEWER が dormant 次元を繰り返し漏らすと言うなら、`pro/agents/reviewer.md` を編集して checklist 項目を追加
- **cortex config を改変**——例えばシステムが hippocampus retrieval 品質が低いと言うなら、`_meta/cortex/config.md` で `top_k_signals` や `per_signal_floor` 調整を検討
- **手動反論**——システミックパターン検出に同意しない場合(例えば narrator 失敗率高いが暫定的問題でシステミックではないと思う)、現 session で「この検出は誤報と考える」と言う、AUDITOR が記録、後続 pattern 監視は継続だが重み下がる

### 6. パターンで user-patterns.md に昇格された behavior のクリーンアップ

ある behavior が昇格されたが同意しない場合、`user-patterns.md` を開き該当記録を直接削除。user-patterns は**あなたが所有するファイル**、AUDITOR / ADVISOR は読むのみ、強制保持しない。

---

## いつ skill 設定を改変すべきか / When to Modify Configuration

ユーザーから最も多い質問:**eval-history でどのデータを見たら、改変に動くべきか?**

### 赤信号(即時行動)

- **同一 `violations[].type` が 30 日で 3+ 回出現** → 既にルール 5 で user-patterns.md に昇格。**システムが「これは安定したパターン」と表明** → 対応 agent spec を改変
- **`process_compliance` 連続 3 回 <5** → 状態機が壊れている。優先度最高、他は待てるがこれは待てない
- **`citation_groundedness` 単回 <5** + trace 検証で本当に narrator 捏造 → `pro/agents/narrator-validator.md` を編集してより厳格なチェックを追加、または registry 自体に漏れがないか検討

### 黄信号(観察 + 予備)

- **ある次元が 2 回閾値に近いが未到達**——3 回目を先に観察。連続性問題なら AUDITOR がトリガー
- **新導入 agent 定義が初回稼働で分数が明らかに該 agent 歴史より低い**——新版 spec に回帰、review diff で原因探す
- **RETROSPECTIVE がシステミック警告を出したが偶然と考える**——先に AUDITOR に 1 週間観察させる。7 日データでトレンド明瞭

### 緑信号(定常状態)

- 全次元 ≥7
- システミック警告なし
- violations 数 ≤1 per session

これがあなたの期待する常態。長期緑信号だが、**能動最適化**したい(例 8 点から 10 点へ)場合、リスクに慎重——「動いているものは少し改変」。

---

## よくある質問 / Common Questions

### なぜ整数 0–10、小数ではなく?

AUDITOR に commitment を強制。**半点は逃避**——「7.5 と感じる」は実は「両側に恨みを買いたくない」。10 ランク整数で AUDITOR に片側を選ばせる。

長期的に、**10 ランクで十分精細**——3 ヶ月ある次元の走りを見れば、8 から 7 から 6 への下降は明確なシグナル、8.5 から 7.5 のようなレベルは不要。

### AUDITOR が自分に 10 点をつけたら(自己称賛)?

Eval-history の anti-patterns に明言:

> **Do not** allow face-saving in AUDITOR's own evaluation. If `score_honesty: 3` is warranted, write 3 — AUDITOR evaluating itself with uniform 7s is the exact anti-pattern AUDITOR was built to detect in others.

実務上: AUDITOR の spec (`pro/agents/auditor.md`) は「blanket 7s or 8s」を禁止、各次元は**具体的証拠**(quoted agent output、score contradiction、skipped phase)を必須。AUDITOR の body に「all agents performed well」のような一般賛美があれば、それが自身禁止の anti-pattern、次回 AUDITOR が歴史スキャン時に自身の問題を flag。

これは二階の自己モニタリング: **AUDITOR が AUDITOR を検出**。完璧でないが、ないよりまし。

### v1.7 新インストール初日で eval-history がない、システム健康をどう知る?

**前 3 session はシステミック警告が出ない**——検出ルールは最低 3 件レコードが必要。

前 3 回は:
- eval-history ファイル内容を手動チェック、スコアが期待範囲内か確認
- AUDITOR 自身が Decision Review で surface する即時問題に注意(v1.6.2a から存在)

3 回後 RETROSPECTIVE がスキャン開始、システミックシグナルが出現。

### Migration は v1.6.2a の歴史 AUDITOR レポートを回填する?

**しない**(spec 明記 §11)。

理由: v1.6.2a の AUDITOR レポートは**非構造化散文**、v1.7 の YAML schema に合わない。強制回填は低信号ノイズを生み、**システミック検出**を汚染——connection 3 回低分ルールが誤トリガーし、本当の問題が埋もれる。

**eval-history は v1.7 day 1 から再スタート**。v1.6.2a 歴史を見たい?`_meta/journal/` の session レポートを直接読む。

### eval-history のスコアを編集するとどうなる?

ファイルは**編集禁止**(spec 硬ルール)。**技術的には改変可能**だが:

- RETROSPECTIVE Mode 0 と tools/reconcile.py は「ファイル未改変」と仮定
- 歴史スコア改変でシステミック検出結果が歪む
- 長期的に、eval-history が「真の自己評価」としての価値を失う

正しい方法:改変しない。ある評価に同意しないなら、**次回 session** で言う、AUDITOR に新しい反論 eval ファイルを書かせる。

### patrol-inspection と decision-review の違いは?

2 種類の `evaluation_mode`:

| Mode | トリガー | 評価対象 |
|------|------|----------|
| `decision-review` | 全朝議決定 Step 8 ごと | 本決定のワークフロー品質 |
| `patrol-inspection` | RETROSPECTIVE が `lint-state.md >4h` 検出 | 直近複数 session の横断面健康(wiki オーファン、concept 孤立辺、SOUL 矛盾累積) |

`patrol-inspection` は**巡検**、特定 session に対応しない——「しばらく間を置いて全局をチェック」。両 eval とも同じディレクトリに書き、`evaluation_mode` フィールドで区別。

### eval-history に深刻な violation(例えば adjourn 完整度 2/10)が出たら、即時何をすべき?

panic しない。優先度順:

1. **body の Weaknesses と Recommendations を読む**——AUDITOR が通常具体的修復方向を提示
2. **直近 session journal** を確認、adjourn が本当に broken か(ARCHIVER 4 phase 完走したか、Completion Checklist に TBD があるか)
3. **構造的問題**(archiver が分段実行)なら、Recommendations に従い ARCHIVER の prompt / `pro/CLAUDE.md` の状態機制約を改変
4. **偶発**(ある Claude API 揺れで phase 中断)なら、記録、次回 session で正常 adjourn で復旧

即時 rollback や Cortex 再インストールは不要——eval-history 自体は**診断**であり**災害**ではない。

---

## トラブルシューティング / Troubleshooting

### 「eval-history ディレクトリのファイルが少ない、session 数より遥かに少ない」

診断:

```bash
# session ファイル数
ls _meta/sessions/*.md | wc -l

# eval ファイル数
ls _meta/eval-history/*.md | wc -l
```

比率は 50–80% が妥当(direct-handle / Express 短 / STRATEGIST は書かないため)。比率 <30% なら:

1. AUDITOR が複数 session で書き込み失敗(ディスク、権限)——session journal の AUDITOR 部に "eval write failed" メッセージがないか確認
2. `pro/agents/auditor.md` の spec で「どのシナリオで書くか」の判定が厳しすぎる——Express の brief report がすべて「深度不足」でスキップされた可能性

対処:
```bash
uv run tools/reconcile.py
```
が「session あるが eval なし」の orphan をリスト、どの session がスキップされたか調査可能。

### 「Systemic warning が連続して出るが、設定を改変済み」

設定改変後、**eval-history の古いデータは残る**——ルール 1–4 は「直近 10 件」ベース、改変後**新 session 10 件**で古いデータが完全に入れ替わる。前数回の session で警告は継続。

緊急で警告を消したい場合(システム健康をデモ中など):

```bash
# 古い eval を _archive/ にアーカイブ(削除しない)
mkdir -p _meta/eval-history/_archive/
mv _meta/eval-history/2026-03-*.md _meta/eval-history/_archive/
```

RETROSPECTIVE は `_meta/eval-history/*.md` トップレベルのみ読み、`_archive/` は読まない。

### 「warning block がずっと出ないが、データに明らかな下落が見える」

可能な原因:

1. **ルール閾値が未トリガー**——「下落」と「連続 N 回閾値以下」は別。具体ルールの N 値を確認
2. **RETROSPECTIVE Mode 0 の eval-history 読み込み失敗**——session 起動時の briefing に「⚠️ トレンド対比利用不可」類似の提示があれば、読み込み失敗
3. **`_meta/eval-history/` が最近作成、数件のみ**——ルール 1/2/3 すべて 5–10 件レコードが必要、3 件未満ではトリガーせず

---

## 深堀りの読書 / Further Reading

同ディレクトリ ユーザードキュメント:

- [overview.md](./overview.md) — Cortex 総覧、eval-history は 4 機構の**二階モニタリング**
- [hippocampus-recall.md](./hippocampus-recall.md) — `cognitive_annotation_quality` が hippocampus 品質を監視
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — `wiki_extraction_quality` が archiver Phase 2 を監視
- [narrator-citations.md](./narrator-citations.md) — `citation_groundedness` が narrator 引用を監視
- [gwt-arbitration.md](./gwt-arbitration.md) — `cognitive_annotation_quality` / `suppression_precision` が仲裁品質を監視

Spec 層(英語):

- `references/eval-history-spec.md` — 完全 spec: schema、システミックルール、ストレージ、移行
- `references/cortex-spec.md` §Open Questions — eval-history 駆動の spec revision フロー
- `references/hooks-spec.md` — `process_compliance` 違反ログ源
- `pro/agents/auditor.md` — 唯一の eval-history 書き込み者
- `pro/agents/retrospective.md` — Mode 0 の pattern detection

その他:

- `tools/stats.py` — 月次/四半期サマリー
- `tools/reconcile.py` — orphan 検出
- `devdocs/research/2026-04-19-hermes-analysis.md` — Hermes Lesson 5(自己評価はフィードバックされるべき)

---

**前ページ**: [gwt-arbitration.md — 顕著性競争](./gwt-arbitration.md)

**総覧に戻る**: [overview.md — Cortex 総覧](./overview.md)

---

### 訳者注 / Translator's Note

本ドキュメントは中国語版 (`docs/user-guide/cortex/auditor-eval-history.md`) からの自動翻訳版です(2026-04-22 作成)。技術用語(AUDITOR, RETROSPECTIVE, eval-history, Hermes RL, decision-review, patrol-inspection, information_isolation, veto_substantiveness, score_honesty, action_specificity, process_compliance, adjourn_completeness, soul_reference_quality, wiki_extraction_quality, cognitive_annotation_quality, citation_groundedness, tier_1_conflict, graceful degradation, immutability, anti-pattern 等)は原文の英語表記を保持しています。「退朝」「上朝」「奏折」などの中国語の朝廷メタファーは Life OS 独自用語として日本語文脈でも保持しました。人間校正待ち。
