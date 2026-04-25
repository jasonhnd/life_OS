---
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# GWT 仲裁 · 多源シグナルの顕著性競争 / GWT Arbitration

> パンくず: [← Cortex 総覧](./overview.md) · [← 製品入口:ユーザーガイド索引](../index.md)

> メッセージを送るたびに、Cortex は 3 つのシグナル源を並列実行します:hippocampus(歴史 session)、concept lookup(概念グラフ)、SOUL check(人格次元チェック)。これら 3 源は**十数〜数十の**候補シグナルを生む可能性があります。すべてを ROUTER に流すと情報洪水になります。GWT Arbitrator の仕事は、このシグナルの山で**顕著性競争**を行うことです——4 次元で採点し、top-5 を選び ROUTER に届ける、SOUL コア衝突は警告ヘッダーに昇格。この層は Stanislas Dehaene の **Global Neuronal Workspace** 理論から着想を得ています(中国語では「全局神经元工作空间」、日本語では「グローバル・ニューロナル・ワークスペース」と呼ばれます)。

## 一文概説 / One-Line Overview

GWT Arbitrator は Cortex の**シグナル選択器**です——Step 0.5 の最末端で hippocampus / concept / SOUL の 3 つの並列 subagent の出力を受信し、固定式 `salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2` で採点、ランキング、top-5 切り出し、SOUL 衝突昇格処理を行い、最終的な `[COGNITIVE CONTEXT]` ブロックを ROUTER に渡します。

名前の由来: Dehaene の GWT 理論は、脳内には多くの並列特化モジュールが同時に働き、その出力が**競争**して「中央ワークスペース」に入ると主張します。最も強いシグナルだけが「点火」(ignition) し、他のすべてのモジュールにブロードキャストされます。この枠組みでは、意識は競争に勝った瞬間です。

Cortex はこのモデルを借用: hippocampus、concept、SOUL は 3 つの「特化モジュール」、GWT Arbitrator は「競争仲裁器」、ROUTER は「中央ワークスペース」——最終的に ROUTER の `[COGNITIVE CONTEXT]` に入るのが、本 session で**点火**したシグナルです。

---

## なぜこの層を追加するのか / Why Add This Layer

### 問題: 仲裁がないとどうなる?

GWT がなく、3 つの subagent の出力を直接連結して ROUTER に渡すとします:

- hippocampus が 7 の関連 session を返す(各々価値があるが重要度は異なる)
- concept lookup が 9 の概念を活性化(canonical コアもあれば tentative ノイズもある)
- SOUL check が 4 次元状態を返す(2 は tier_1 衝突、2 は tier_2 関連)

ROUTER が見る `[COGNITIVE CONTEXT]` は 20 エントリ:

```
[COGNITIVE CONTEXT]
Related past decisions: [7 エントリ]
Active concepts: [9 個]
SOUL dimensions: [4 エントリ]
[END]
```

**問題**:
- **情報過剰**——ROUTER の triage は秒単位の判断、20 エントリから主要矛盾を拾う能力が落ちる
- **ノイズがシグナルを埋める**——1 つの tier_1_conflict が 15 の無関係な concept に埋もれ、REVIEWER が見逃す可能性
- **cache 汚染**——prompt cache が大量の低価値情報で膨張、後続 turn の cache hit 率低下
- **token 予算爆発**——turn ごとに 20 エントリを詰めると、6 領域それぞれにも配布されるのでコスト ×6

### 脳科学の答え

脳はこの問題を以下のように処理します: **特化モジュールが並列でシグナルを生成、顕著性競争で 1 つまたは数個をブロードキャスト**。視覚皮質はミリ秒ごとにシグナルを生成しますが、「あなたが意識する」のはごくわずか——最も顕著なシグナルだけが ignition を勝ち取るからです。

これは「フィルタ機構」ではなく、**競争機構**です——低顕著性シグナルはワークスペースに**そもそも負けた**、あなたの意識は存在を知ることさえない。Cortex はこのモデルを模倣: GWT Arbitrator が salience でソートし、**top-5 のみを送る**、他は frame md に記録して trace 可能にするが `[COGNITIVE CONTEXT]` には入らない。

---

## ユーザー側に見えるもの / What the User Sees

### シナリオ A: 通常時の `[COGNITIVE CONTEXT]`

質問: 「今四半期、新プロダクトラインをパートナー A に任せるか?」

GWT Arbitrator が 3 源シグナルを受信(例):

| 源 | シグナル | urgency | novelty | relevance | importance | **salience** |
|------|------|---------|---------|-----------|------------|-----------|
| hippocampus | S:claude-20260115-1020 (過去の類似決定) | 0.3 | 0.6 | 0.8 | 0.5 | **0.55** |
| hippocampus | S:claude-20260320-1400 (パートナー関係) | 0.3 | 0.6 | 0.7 | 0.5 | **0.50** |
| concept | C:relationship:partner-a-control | 0.0 | 0.2 | 0.9 | 0.5 | **0.41** |
| concept | C:method:partner-evaluation | 0.0 | 0.2 | 0.6 | 0.3 | **0.26** ← 切り落とし |
| SOUL | 家庭優先よりキャリア (tier_1_conflict) | 0.6 | 1.0 | 0.9 | 1.0 | **0.85** |
| SOUL | 単独リスク (tier_2_relevant) | 0.3 | 0.6 | 0.7 | 0.7 | **0.55** |

ソート + top 5 切り出し: `[SOUL 家庭優先, SOUL 単独リスク, S:過去類似決定, S:パートナー関係, C:partner-a-control]`

**SOUL tier_1_conflict は警告ヘッダーに昇格**。ROUTER が見る `[COGNITIVE CONTEXT]`:

```
[COGNITIVE CONTEXT — reference only, not user input]

⚠️ SOUL CONFLICT: この決定はあなたの「家庭優先よりキャリア」(confidence 0.82) に挑戦

📎 Related past decisions:
- 2026-01-15 | パートナー授権 (score 8.2) — 結論「さらに 3 ヶ月観察」
- 2026-03-20 | パートナー関係再構築 (score 6.5) — finance 懸念

🧬 Active concepts:
- partner-a-control (canonical, weight 42, last activated 4d ago)

🔮 SOUL dimensions:
- 家庭優先よりキャリア (core, ↘ stable): tier_1_conflict
- 単独リスク (secondary, ↗ up): tier_2_relevant

[END COGNITIVE CONTEXT]

User's actual message: 今四半期、新プロダクトラインをパートナー A に任せるか?
```

**`C:method:partner-evaluation` は salience 0.26 で per-signal floor (0.3) により切り落とし**。ROUTER には入らないが、**本 session の frame md には記録**、将来 trace 時に「このシグナルは本 session に存在したが、未点火」と確認可能。

### シナリオ B: 初回上朝 · registry 空

Cortex を新規インストールし migration を完走。初回 session で発話。hippocampus は空を返し、concept lookup も空、SOUL check は 1 エントリかも(「リスク許容度 new」):

GWT 出力:

```
[COGNITIVE CONTEXT]
🔮 SOUL dimensions:
- リスク許容度 (emerging, confidence 0.3): tier_2_relevant
[END]
User's actual message: ...
```

または極端に、signal registry 全体が空: GWT は空テンプレートを compose せず、**空マーカー**を直接返す—— ROUTER は生のユーザーメッセージを見て、v1.6.2a 挙動にフォールバック。

### シナリオ C: 1 つの低 salience シグナルのみ

GWT がすべてのシグナルを採点し、最高値がたった 0.25(floor 0.3 未満)と判明。

`(no high-salience signals)` 単行マーカーを出力、分類ブロックをすべてスキップ:

```
[COGNITIVE CONTEXT]
(no high-salience signals)
[END]
User's actual message: ...
```

ROUTER は「Cortex は走ったが顕著シグナルは出なかった」と認識——「Cortex が走っていない」とは別の状態。

### シナリオ D: 部分タイムアウト

hippocampus がソフトタイムアウト 5 秒でもまだ返ってこないが、concept と SOUL は完了。GWT の選択肢:

- ハードタイムアウト 10 秒まで待ち、hippocampus がまだ返らなければ、partial output を送る(concept + SOUL シグナルのみ)+ 追加単行 `(partial — timed out)`
- hippocampus が soft timeout から hard timeout の間に返れば、依然として追加

出力:

```
[COGNITIVE CONTEXT]
🧬 Active concepts:
- partner-a-control (canonical, weight 42)
🔮 SOUL dimensions:
- 家庭優先よりキャリア (core, ↘ stable): tier_1_conflict
(partial — timed out)
[END]
User's actual message: ...
```

---

## 顕著性公式 · 4 次元 / The Salience Formula

**salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2**

この公式は **v1.7 で固定**。各次元は `[0.0, 1.0]` の浮動小数点。

### urgency(緊急度)

| 値 | 条件 |
|---|------|
| **1.0** | 7 日内の deadline 関連 action item |
| **0.6** | SOUL 衝突警告(core 次元が挑戦される) |
| **0.3** | 反復パターン(同一トピックが直近 3+ 回出現) |
| **0.0** | 時間圧力のない背景 context |

緊急度の重みが最高 (0.3)——**deadline があることは必ず先に見せるべき**、importance が低くても。

### novelty(新奇度)

| 値 | 条件 |
|---|------|
| **1.0** | シグナルが過去に出現したことがない |
| **0.6** | 1–2 回出現 |
| **0.2** | 3+ 回出現(**fatigue — 既に見た**) |
| **0.0** | 既に処理・解決済み |

novelty は「反スクロール疲れ」——同じシグナルが繰り返し活性化されると、salience は自然減衰。ROUTER が毎回同じ歴史を見ることを防ぎます。

### relevance(関連度)

**LLM が判断する唯一の次元**——他はルールベース。

LLM は `(signal content, current user message)` のペアを受け取り、`[0.0, 1.0]` の浮動小数点を返します。これが「このシグナルと現在の決定の直接関連度」を表します。

LLM 失敗時、**deterministic fallback としてキーワード重複率に後退**。

relevance の重み 0.3、urgency と並び最高。

### importance(重要度)

SOUL 次元等級 + 戦略プロジェクトタグのマッピング:

| 値 | 条件 |
|---|------|
| **1.0** | SOUL `core` 次元 (confidence ≥ 0.7) |
| **0.7** | SOUL `secondary` 次元 (0.3 ≤ confidence < 0.7) |
| **0.5** | critical-path プロジェクトに関連(concept metadata に tag あり) |
| **0.3** | SOUL `emerging` 次元 (0.2 ≤ confidence < 0.3) |
| **0.2** | 一般 context、身分またはプロジェクト束縛なし |

複数条件同時マッチ時、**最高値を取る**。

---

## シグナルタイプ / Signal Types

GWT は 9 種類のシグナルタイプを認識、源ごとにグループ化:

### From hippocampus

- `decision_analogy` — 過去と現在のトピックが構造的に類似した決定
- `value_conflict` — 過去 session で SOUL と衝突、ここでも関連
- `outcome_lesson` — 過去の決定結果が教訓的意味を持つ

### From concept lookup

- `canonical_concept` — 直接言及または含意された confirmed concept
- `emerging_concept` — 同領域の tentative concept(まだ canonical ではない)

### From SOUL check

- `tier_1_alignment` — core 次元が現在方向を支持
- **`tier_1_conflict`** — core 次元衝突(**半 veto シグナル、昇格**)
- `tier_2_relevant` — secondary 次元適用
- `dormant_reactivation` — 休眠次元がちょうど再関連

**シグナルは arbitrator にとって opaque**——`signal_type`, `source`, `payload`, 4 採点次元のみを見る。**arbitrator は payload から**新シグナルを推論しない——各シグナルは名前付き source を必ず持つ。

---

## 仲裁アルゴリズム · 6 ステップ / The Arbitration Algorithm

1. **Ingest** — 3 源シグナル受信(metadata 付き)
2. **Score** — 公式で salience 計算。relevance は LLM、他はルール
3. **Rank** — salience 降順でソート
4. **Cap** — **top 5** を取る(ハード上限、情報過剰防止)
5. **Detect conflicts**:
   - 任意の `tier_1_conflict` → **昇格**して `⚠️ SOUL CONFLICT` ヘッダー
   - 反対方向の `decision_analogy`(過去に矛盾する決定があった)→ pattern observations ブロックに "inconsistent precedent" flag
6. **Compose** — §8 出力形式でレンダリング

**arbitrator はシグナルを「発明」しない**。出力のすべての項目は入力シグナルに**追跡可能**。

---

## 出力形式 · `[COGNITIVE CONTEXT]` ブロック / Output Format

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

⚠️ SOUL CONFLICT: [core 次元が挑戦されるときのみ]
This decision challenges your "{dimension_name}" (confidence {X})

📎 Related past decisions:
- {session_id} ({date}): {reason}, score {X}/10

🧬 Active concepts:
- {concept_id} (canonical, weight {X}, last activated {when})

🔮 SOUL dimensions:
- {dimension} ({tier}, {trend}): {support/challenge status}

💡 Pattern observations:
- {salience ≥ 0.8 だが他のカテゴリに属さないシグナル}

[END COGNITIVE CONTEXT]

User's actual message: {original}
```

**抑制ルール**:

- **シグナル総数 0** → 空マーカー、ROUTER は `User's actual message: ...` のみ見る
- **全シグナル < 0.3** → 単行マーカー `(no high-salience signals)`、分類ブロックをスキップ
- **SOUL CONFLICT あり、関連歴史なし** → SOUL ブロックを依然 emit(衝突は独立した重み)
- **カテゴリごと最大 5、全体 top 5**——二重上限の重畳

---

## 注入位置 · なぜ user role であって system prompt でない / Injection Point

**cognitive context は user role メッセージの先頭に prepend、system prompt に追加しない**。

**理由**: Anthropic の prompt cache は system prompt が安定しているときのみヒットします。turn ごとに動的な cognitive annotation を system prompt に追加すると、**turn ごとに cache bust**。user role に残せば cache ヒットに影響なし。

**実装**:

1. Orchestrator が arbitrator を呼び出し、出力を受信
2. Orchestrator が ROUTER の user-role メッセージの先頭に **prepend**
3. ROUTER が合成入力を見る、`[COGNITIVE CONTEXT]` ブロックを**参照**として扱う、リテラルなユーザーリクエストとして扱わない
4. ROUTER の system prompt は変わらない

**ROUTER の triage ルールは不変**——`[COGNITIVE CONTEXT]` を**補助情報**として扱う、どの domain agent を派遣するか決める際**参考にも無視にもできる**。

---

## ユーザーアクション · 仲裁結果への介入方法 / User Actions

### 1. `[COGNITIVE CONTEXT]` を無視するよう要求

> cognitive context を無視、ゼロから再分析して

ROUTER は本決定で `[COGNITIVE CONTEXT]` ブロックを**積極的に無視**——cognitive annotation は advisory、authoritative ではない。

### 2. 元 cognitive context の表示を要求

> 今回の cognitive context を見せて

システムが完全な `[COGNITIVE CONTEXT]` ブロックを貼ります。

### 3. 各引用を trace で確認

`📎 Related past decisions: - 2026-01-15 ...` を見て、言う:

> trace S:claude-20260115-1020

元の session summary + 関連度評価 + 選ばれた理由を取得。[narrator-citations.md](./narrator-citations.md) 参照。

### 4. SOUL CONFLICT 昇格への反論

システムが「この決定はあなたの家庭優先次元に挑戦」と言うが、本決定の焦点が家庭方向でないと感じる場合:

> 今回の SOUL CONFLICT は適用外——本決定は家庭の時間配分に関わらない

ROUTER は:
- Summary Report の修正段にあなたの反論を記録
- AUDITOR が eval-history に `suppression_precision` 失調を記録([auditor-eval-history.md](./auditor-eval-history.md) 参照)
- 同類誤判定が繰り返されると、AUDITOR が「SOUL check 次元マッチが過広」と flag、retuning が必要かも

### 5. salience 閾値の調整

`_meta/config.md` を編集:

```yaml
salience_weights:
  urgency: 0.3
  novelty: 0.2
  relevance: 0.3
  importance: 0.2
per_signal_floor: 0.3       # この値未満のシグナルは破棄
top_k_signals: 5            # ハード上限、ブロードキャストするシグナル数
```

**重み合計は 1.0 を保つこと**(現 0.3+0.2+0.3+0.2=1.0)。編集後 git commit、次回 Start Session で有効。

**v1.7 段階で調整は推奨しません**——これらの数値は Phase 1 placeholder、3 ヶ月の実データでどう調整すべきか判明。調整する場合、保守的に(±0.05)、eval-history の `cognitive_annotation_quality` トレンドを観察。

---

## よくある質問 / Common Questions

### なぜ 4 次元?5 次元ではなく?

過去版で第 5 次元 emotion(感情重み付け)を議論しましたが、v1.7 は**追加しない**決定。理由:

- 感情評価には追加の subagent が必要、新たな failure mode を導入
- SOUL に「感情敏感度」のような次元があれば、既に importance の形で融合済み
- Phase 2 で `emotion` と `prediction` のシグナルタイプを導入する可能性あり、しかし依然 4 次元公式を走る(公式を変えず、シグナル源のみ拡張)

したがって **v1.7 公式は 4 次元で固定**。

### Top-5 で重要シグナルを見逃さない?

あり得ますが、**受け入れ可能なトレードオフ**:

- v1.6.2a ではシグナルがそもそもなし、20 シグナル 0 個 ROUTER 到達 = 100% 漏れ
- v1.7 では top-5 が入ることを保証、95% の salience ≥ 0.6 シグナルが top-5 に入る
- 残り 5% のエッジケースは、AUDITOR の `cognitive_annotation_quality` がパターンを捕捉(ある類の重要シグナルが長期的に切られ続けると retuning flag)

また: **切られたシグナルは依然 session frame md に記録**、trace 時に確認可能。ROUTER が見える `[COGNITIVE CONTEXT]` に入らないだけ。

### SOUL 次元は 4 採点次元の 1 つにすぎないのに、なぜ `tier_1_conflict` だけ昇格?

**他のシグナルとの対称性が誤判定を起こす**から:

- `tier_1_conflict` が importance 1.0 の普通シグナルとして扱われると、他の高 urgency / 高 novelty シグナルが共同で top-5 から押し出す可能性
- しかし core 衝突は**意思決定レベルの警告**——見なければコア価値観と衝突する決定を下す可能性
- 対称ランキングではこの類の「重要だが urgency/novelty が低くない」シグナルがシステム的に無視される

昇格機構はこれに対する構造的修正: **`tier_1_conflict` が存在する限り、何位であれ、`⚠️ SOUL CONFLICT` ヘッダーブロックとして単独 emit**。これは「破格」でなく、「タイプ専属」。

### Arbitrator 自身はチートできる?

arbitrator は `Read` 権限のみ、**ファイルを書かない**。失敗モード:

- Salience 計算失調(LLM の relevance 判定失敗)→ deterministic fallback(キーワード重複)へ
- タイムアウト → partial 出力
- クラッシュ → 空マーカー + v1.6.2a にフォールバック

「チート」の余地なし——入力は 3 subagent の固定出力、出力は ranked list、中間に自由裁量なし。これは**純 consumer**、producer ではない。

### 同じ subject を繰り返し質問すると、novelty で「システムが学び悪くなる」?

novelty 減衰は反スクロール疲れ機構であり、「関連情報を隠す」ものではない。具体的に:

- 同一シグナルが 3+ 回出現 → novelty が 0.2 に下がる
- しかし urgency / relevance / importance は不変——シグナルが本質的に高関連 + 高重要性なら、novelty が低くても top-5 に入れる
- fatigue は「同じ無関係歴史が繰り返し推奨される」のを避ける機構、真に重要なシグナルを埋めない

例外: あるトピックで無限ループしている場合(「転職するか」を週 5 回質問)、novelty トリガー 3 回後、システムが `decision_fatigue` DREAM トリガーで「最近 3 日で N 個の同類決定」と flag(DREAM ドキュメント参照)。

### Tie-breaking ルールは?

2 シグナルの salience が完全同一のとき、順に:

1. **新しい方優先**——timestamp が近い方勝ち
2. **importance 高い方優先**——依然タイなら
3. **alphabetical by signal_id**——完全確定の fallback、「同一入力は常に同一ランキング」を保証

**ランダム化なし**——Cortex の仲裁は **reproducible** でなければならない。同一入力は 2 回とも同一出力、debug と eval に便利。

### AUDITOR は仲裁品質をどう評価する?

3 つの指標([auditor-eval-history.md](./auditor-eval-history.md) 参照):

- **`cognitive_annotation_quality` (0–10)**——ROUTER はこの注釈を「使ったか」?
- **`annotation_utilization_rate`**——下流 agent が少なくとも 1 シグナルを引用した session の割合は?
- **`suppression_precision`**——arbitrator が SOUL CONFLICT 警告を出したとき、REVIEWER は独立に同じ問題を flag したか?

低分の長期トレンド → RETROSPECTIVE がブリーフィングで "hippocampus retrieval tuning needed" や "GWT weight retuning needed" を surface。

### 多源が同時に失敗したら?

**Degradation hierarchy**(複数 failure 重畳時、順に処理):

1. source 欠落(hippocampus 空)→ 既存 source で継続
2. LLM relevance 判定失敗 → キーワード重複へフォールバック
3. ハードタイムアウト(10s)→ partial output 送信
4. Arbitrator 全体 crash → 空マーカー + ROUTER 元モードにフォールバック

**各ステップで、出力は valid な annotation block**(空でも)——ROUTER は「半端または畸形」ブロックを受け取らない。graceful degradation は交渉不可の設計原則。

---

## トラブルシューティング / Troubleshooting

### 「毎回 `[COGNITIVE CONTEXT]` が表示されない」

可能な原因(可能性順):

1. **普段 direct-handle や Express しか使わない**——これらのシナリオは Step 0.5 を走らない
2. **migration を走らせていない**——INDEX.md / concepts は空、signal registry に並べる物がなく、GWT が空マーカーを送る
3. **全シグナル salience < 0.3**——GWT は `(no high-salience signals)` マーカーを送ったが見えていない(ROUTER が「その他」に折りたたんだ可能性)
4. **cortex_enabled: false**——`_meta/config.md` で切られている

診断:

```bash
# 本 session の arbitration record を確認(session frame md に記録)
grep -l "gwt_arbitration" _meta/sessions/$(ls -t _meta/sessions/ | head -1)
```

### 「SOUL CONFLICT が繰り返し誤昇格」

診断: 直近 10 回の eval-history で `suppression_precision` の値を確認。持続的に低い (<5) 場合、GWT が報告する SOUL CONFLICT と REVIEWER 自身の判断が**一致しない**——GWT の警告が偽陽性の可能性。

対処:
- 短期: 誤昇格時に反論(「今回の SOUL CONFLICT は適用外」)、AUDITOR に証拠を蓄積させる
- 長期: AUDITOR が retuning 需要を flag 後、SOUL check subagent の次元マッチ閾値を調整する可能性あり——`_meta/config.md` レベルの調整、ユーザー決定 #4 では「モジュールを自動で閉じる」はトリガーしないが、あなたが手動調整を決定可能

### 「annotation_utilization_rate が長期 <20%」

これは cortex の出力が ROUTER / 6 領域に**あまり使われていない**——7 秒かけて annotation したが、下流 agent がほぼ引用していない。

診断: これは AUDITOR が最も気にする「コスパ」指標。可能な原因:

1. **ROUTER prompt が cognitive context 使用を十分誘導していない**——`pro/agents/router.md` に「`[COGNITIVE CONTEXT]` ブロックを参照すべき」をより明確にする必要があるかも
2. **Hippocampus 品質低**——検索した session が本当に無関係、下流 agent が使えない
3. **質問タイプ自体が歴史と関連薄い**——多くの質問が孤立した新問題なら、cortex は元々役に立てない

対処: AUDITOR が eval-history で具体的に何を flag しているか見て、症状に応じて対処。

### 「Top-5 が無関係 concept で埋まる」

Concept lookup が**過度に広くマッチ**の可能性——すべての concept が活性化、relevance 0.7 を取り、SOUL の 0.85 を 2 位に押しやり、他の重要シグナルが切られる。

診断: ある session の arbitration record を見て、各 concept の relevance スコアを確認。すべて 0.7 付近なら、concept lookup subagent の関連度判定が甘すぎる。

対処:
- 短期: この類の問題は AUDITOR が `cognitive_annotation_quality` 低で flag
- 中期: concept-lookup の prompt 最適化を待つ(v1.7 spec で open question と明言)
- 臨時回避: `_meta/config.md` で `per_signal_floor` を 0.3 から 0.5 に上げ、中程度関連ノイズを濾過

---

## 深堀りの読書 / Further Reading

同ディレクトリ ユーザードキュメント:

- [overview.md](./overview.md) — Cortex 総覧
- [hippocampus-recall.md](./hippocampus-recall.md) — hippocampus が生む `decision_analogy` / `value_conflict` シグナル
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — concept lookup が生む `canonical_concept` / `emerging_concept` シグナル
- [narrator-citations.md](./narrator-citations.md) — top-5 シグナルが Summary Report の `[signal_id]` 引用にどう変わるか
- [auditor-eval-history.md](./auditor-eval-history.md) — `cognitive_annotation_quality` / `suppression_precision` / `annotation_utilization_rate` の長期モニタリング

Spec 層(英語):

- `references/gwt-spec.md` — 完全 spec: 公式、シグナルタイプ、アルゴリズム、失敗モード、tie-breaking
- `references/cortex-spec.md` §GWT Arbitrator — 全体アーキテクチャ内の位置
- `references/hippocampus-spec.md` — hippocampus 出力形式(GWT の入力源の一つ)
- `references/concept-spec.md` — concept 出力形式
- `references/soul-spec.md` §Tiered Reference by Confidence — tier 定義
- `devdocs/architecture/cortex-integration.md` §4 — Step 0.5 3 源並列フロー

Agent 定義(深度ユーザー):

- `pro/agents/gwt-arbitrator.md` — agent 定義、tool 制約、model 選択

---

**前ページ**: [narrator-citations.md — Narrator 引用と trace](./narrator-citations.md)
**次ページ**: [auditor-eval-history.md — AUDITOR 自己フィードバックデータ](./auditor-eval-history.md)

---

### 訳者注 / Translator's Note

本ドキュメントは中国語版 (`docs/user-guide/cortex/gwt-arbitration.md`) からの自動翻訳版です(2026-04-22 作成)。技術用語(GWT, Global Neuronal Workspace, Arbitrator, salience, ignition, urgency, novelty, relevance, importance, tier_1_conflict, hippocampus, concept lookup, SOUL check, COGNITIVE CONTEXT, signal registry, graceful degradation 等)は原文の英語表記を保持しています。Dehaene の Global Neuronal Workspace 理論は意識科学の代表的モデルで、本稿では英語原語を基本とし日本語補足を添えました。人間校正待ち。
