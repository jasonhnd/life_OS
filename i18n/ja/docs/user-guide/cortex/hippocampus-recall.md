---
translator_note: 自動翻訳 2026-04-22、人間校正待ち
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Hippocampus · クロスセッション記憶検索(Hippocampus · Cross-Session Memory Recall)

> パンくず: [← Cortex 総覧](./overview.md) · [← 製品入口:ユーザーガイド索引](../index.md)

> 新しい session を開いて発言するたびに、Hippocampus はバックグラウンドで自動的に過去の session を見返し、「あなたが今聞いていること」に関連する数条を探し出します——違う言い回しでも、どれだけ時間が経っていても構いません。ROUTER があなたのメッセージを受け取るとき、既にこれらの「関連記憶」が参考として添付されています。上朝の体感が変わります: システムが**覚えている**ようになります。

## 一言概説(One-line summary)

Hippocampus は Cortex 認知層の**クロスセッション検索器**です。メッセージを送るたびに、ROUTER 分診前の 5–7 秒間で: session インデックスをスキャン → 直接マッチを探す → 概念グラフに沿って拡散 → top 5–7 の関連履歴 session を提出。ROUTER が見るのはあなたの原文ではなく、**原文 + 一段の `[COGNITIVE CONTEXT]` 注釈**です。

名前は生物学から来ています——脳内で新経験を「エピソード記憶」に紐付けし、必要に応じて検索する脳領域が hippocampus(海馬体)と呼ばれます。Cortex のこの subagent がすることは非常に似ています: **「あなたが今言ったこと」と「システムが既に知っている過去」を橋渡しする**。

---

## なぜこれを追加するのか(Why add this)

### v1.6.2a の痛点

新しい session を開いて尋ねます:「前回話したあの信託構造案、日本でコンプライアンス通ると思う?」

システム: 「本セッションのコンテキストがありません、詳細をご提供ください。」

あなた(目を回す):**前回既に 2 時間かけてこの件を議論した**——具体的にどの信託か、なぜそれを選んだか、当時どんな懸念があったか。しかし新 session の ROUTER はゼロから始まり、**この一言**しか見えません。

選択肢は二つだけ:
1. 手動で `decisions/` から前回の意思決定ファイルを探し出し、対話に貼る(煩雑)
2. 最初から説明し直す(無駄、しかもあなたの記述はシステム自身の自分のノートほど正確でないかもしれない)

### Hippocampus の約束

**貼る必要も、説明する必要も、「前回話した」と思い出させる必要もありません**。Hippocampus は自動的に `_meta/sessions/INDEX.md` ——各履歴 session 一行要約のコンパイル済みインデックス——をクエリし、最も関連する 3–5 条を見つけ、詳細 summary を読み取り、さらに概念グラフに沿って別の 1–2 条の「表面的には関連が見えないがグラフ上で隣接する」 session に拡散します。

**結果**: ROUTER は最初から、あなたの言う「あの信託構造案」が何を指すか、以前どう推論したか、GOVERNANCE 領域が何点つけたかを知っています——だから PLANNER は繰り返し考えず、六領域は同じ次元を再分析せず、REVIEWER は「これは不可逆な意思決定ですか」とあなたに聞きません(既に知っている、前回議論した)。

---

## ユーザー側で何が見えるか(What the user sees)

### 直接見えるもの: メッセージの前に `[COGNITIVE CONTEXT]` ブロックが追加される

Step 0.5 終了後、ROUTER が受け取る**実際の入力**はこうなります(通常この層は見えませんが、システムに表示要求できます):

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

📎 Related past decisions:
- 2026-03-15 | 信託アーキテクチャ v2 評価 (score 7.8, wave 1) — 日本 NPO 構造の貸金業法免除問題を議論、GOVERNANCE 8/10
- 2026-02-28 | 越境資産隔離 (score 6.5, wave 1) — 同ドメイン意思決定、finance が信託税務影響を懸念
- 2026-03-22 | パートナーシップ構造比較 (score 5.1, wave 2) — 概念グラフ隣人、via "fiduciary-structure"

🧬 Activated concepts:
- trust-structure-japan (canonical, activation 15)
- npo-lending-exemption (confirmed, activation 7)

[END COGNITIVE CONTEXT]

User's actual message: 前回話したあの信託構造案、日本でコンプライアンス通ると思う?
```

**`wave 1`** = キーワードまたは概念の直接マッチ
**`wave 2`** = 強接続隣人(synapse エッジ重み ≥ 3)
**`wave 3`** = 弱接続隣人(エッジ重み < 3、大半は最終 top 5–7 に入らない)

### 間接的に感じるもの: システムが「覚えている」

ROUTER の奏上書は自然に履歴を引用します:

> あなたの 2026-03-15 の「信託アーキテクチャ v2 評価」[S:claude-20260315-1432]を基に、GOVERNANCE は当時 8/10 をつけ、主な懸念は NPO 免除条項に集中していました。今回この話題を継続、以下に焦点を推奨……

その `[S:claude-...-1432]` の角括弧マークに注意——それが **narrator の citation** です。ROUTER が「過去にこうだった」と言うとき、**真実に存在する session ファイルを指さなければならず**、さもなくば narrator-validator が差し戻して書き直します。

### 能動的に要求すると見えるもの: trace 機構

いつでも聞けます:

> この「前回 GOVERNANCE は当時 8/10 をつけた」は何に基づく?

システムは返答します:

```
📎 Trace for: "前回 GOVERNANCE は当時 8/10 をつけた"

Cited signal: S:claude-20260315-1432
Source: _meta/sessions/claude-20260315-1432.md
Content match: "GOVERNANCE 8/10 — 日本 NPO は貸金業法免除を享受しないが
  今回の信託構造 B には無影響、信託自体が貸付を行わないため。"
Produced by: hippocampus (Step 0.5 Wave 1)
```

**これが Hippocampus のコア価値です: 「AI が作り上げたもっともらしい歴史」ではなく、「AI があなた本人のノートの原文を指し返す」**。

---

## 3 波の拡散活性化(3-wave spreading activation)

Hippocampus の検索モデルは「検索エンジンのマッチ + ランキング」ではなく——脳の **spreading activation** を模倣した 3 波拡散です:

### Wave 1 · 直接マッチ

1. `_meta/sessions/INDEX.md` を読む(コンパイル済みの一行要約インデックス、2000 sessions で ~1MB、秒単位でスキャン)
2. ROUTER が既に subject 抽出済みなら、まず **ripgrep** で高速フィルターし、1000+ 条を <50 条の候補に圧縮
3. 候補を Opus LLM に渡して**意味判断**(embedding なし、vector DB なし——ユーザー決定 #3): 「以下のうちどの session の subject が現在の意味と関連しているか?」
4. top 3–5 の完全 summary ファイルを読む
5. Wave 1 の種集合を出力

### Wave 2 · 強接続隣人

Wave 1 の session からその `concepts_activated` リストを取得し、各 concept に対して:
- `_meta/concepts/{domain}/{concept_id}.md` を読む
- `outgoing_edges` に沿って進む——**ただし重み ≥ 3 の強エッジのみ**
- 各隣人 concept の `provenance.source_sessions` を見つける——これらが「概念グラフを通じて間接的に関連する」 session
- 重複除去(Wave 1 と重ならない)、ランキング、**最大 2–3 条追加**

Wave 2 が捕捉するシーン: 前回「信託アーキテクチャ」を議論した session と、今回「パートナーシップ構造」を議論したい session は、**表面キーワードは重ならない**が、グラフ上で「fiduciary-structure」という概念が両者の共通隣人です。Wave 1 では漏れますが、Wave 2 が拾い上げます。

### Wave 3 · 弱接続隣人(sub-threshold pre-activation)

引き続き拡散、ただし今回は**重み ≥ 1 の任意のエッジを受け入れる**。Wave 3 は直接 top 5–7 に入りません——それがすることは**サブ閾値前活性化**: これらの概念を本セッション残り時間で後続の frame により活性化されやすくします。

類比: 今日「company-A holding」を話すと、Wave 3 が「company-A subsidiary」を前活性化します——次の frame であなたが「company-A」を繰り返さずその子会社を聞いても、システムは応答できます。これは脳内の「priming effect」です。

### 最終上限

検索セット全体の**ハード上限は 5–7 条 session**。多いほど良いわけではありません:
- Token 予算が爆発する
- GWT 仲裁器は 4 次元で >7 条のシグナルに精細にスコアリングできない
- ROUTER が受け取る context が多すぎると、少なくても精なほうがよい

---

## 性能とコスト(Performance and cost)

| 段階 | 目標 | 説明 |
|------|------|------|
| INDEX.md を読む | <100ms | 2000 session インデックスでも ~1MB |
| Grep 前フィルター | <50ms | INDEX.md 上の ripgrep |
| LLM 意味判断(Wave 1) | 2–3s | Opus で ~5000 tokens |
| 3–5 個の session ファイルを読む | <300ms | 並列読み |
| Wave 2 概念検索 | 1–2s | Opus がエッジ関連性を判断 |
| Wave 3 拡散 | 1s | 範囲がより狭い |
| **総目標** | **< 7 秒** | ハード上限 15 秒 |

**コスト**: 一度の hippocampus 呼び出しで約 **$0.05–0.10**(Opus 価格)。Cortex 層全体で月合計目標 $0.20–0.50 ——あなたのメイン session のコストと比較して無視できるほど。

---

## ユーザーアクション · どう介入できるか(User actions · how you can intervene)

### 1. Cognitive Context が何かを見る

直接要求:

> 今回 ROUTER が受け取った cognitive context を見せて

システムは `[COGNITIVE CONTEXT]` ブロックを完全に貼り出します。

### 2. 履歴を無視して再考を要求

履歴検索が ROUTER の判断を歪めたと疑うとき、またはあることを「ゼロから見直したい」とき:

> cognitive context を無視して、この問題を再分析して

ROUTER は本意思決定で `[COGNITIVE CONTEXT]` ブロックを**能動的に無視**します——cognitive annotation は **advisory** であり **authoritative** ではありません。

### 3. 任意の引用を trace

奏上書で `[S:claude-...-1432]` のようなマークを見たら、いつでも:

> trace [S:claude-20260315-1432]

システムは原始 session ファイルの要約段落を返します。

### 4. 能動的に reindex(インデックスが古い場合)

理論上、archiver Phase 2 は adjourn のたびに INDEX.md を自動再構築します。しかし session ファイルを大量に手動変更した場合、または他のデバイスから同期したインデックスが不一致の場合:

```bash
uv run tools/reindex.py
```

### 5. 閾値調整(慎重に)

`_meta/config.md` 内:

項目の権威定義は `references/cortex-spec.md` §`_meta/config.md` にあります。ここでは hippocampus recall に最も関係する設定だけを抜粋します。

```yaml
top_k_signals: 5               # ROUTER にブロードキャストする最大シグナル数
per_signal_floor: 0.3          # salience がこの値未満のシグナルは破棄
hippocampus_timeout: [5, 15]   # ソフトタイムアウト/ハードタイムアウト(秒)
```

変更は git にコミットしてクロスデバイスドリフトを追跡。次の Start Session で有効。

---

## よくある疑問(FAQ)

### Hippocampus は私のプライバシーデータを検索しますか?

**`_meta/sessions/*.md` の YAML summary のみ読みます** ——これらの要約は archiver Phase 2 での書き込み時に既にプライバシーフィルターを通過しています。具体的な個人詳細(人名、金額、口座)**は summary に現れません**ので、cognitive context にも入りません。

また hippocampus の出力契約では各 `summary` フィールド**最大 1–2 文**——session 原文全段を ROUTER に貼る可能性をシャットアウトします。

### INDEX.md が存在しない場合どうなりますか?

退化フロー(順番に):

1. Hippocampus が `tools/reindex.py` を走らせてみる——通れば、インデックス再構築
2. 通らない → 空出力を返す、`degraded: true, degradation_reason: "INDEX_MISSING"` をマーク
3. GWT 仲裁器が hippocampus シグナルを受け取れず、空マーカーフローを通る(詳細は [gwt-arbitration.md](./gwt-arbitration.md))
4. ROUTER が見るのは**原始メッセージ**、動作は v1.6.2a に退化

**あなたの session はブロックされません** ——すべての Cortex コンポーネントの原則は「降級、クラッシュしない」です。

### 検索した session に既に古い内容がある場合、システムは私を誤導しますか?

二重のフォールバック:

1. **Recency decay は既にスコアリングに参加** —— Wave 2/3 のスコアリング式には `0.2 * recency_decay` 重みがあり、`recency_decay = exp(-days_since_session / 90)`。90 日前の session は自動的に減価されます。
2. **Migration はデフォルトで最近 3 ヶ月のみスキャン** ——より古い journal には触れません。古いプロジェクト、降格された価値観、書き直された意思決定は**自然に**概念グラフと session インデックスに入りません。

もし**明示的に** Cortex により古い履歴を引き入れたいなら:

```bash
uv run tools/migrate.py --since 2024-01-01
```

ただし一般的に推奨しません——古い context の当下の意思決定への貢献値は通常新 session ほど良くありません。

### Hippocampus は「能動的に学習」できるのか? なぜベクトルデータベースを使わないのか?

ユーザー決定 #3 で明確に禁止: **markdown-first, LLM-judgment-only**。

理由:
- **検査可能性** ——各 session summary、各 concept ノードは `.md` + YAML で、いつでも開いて見られる。ベクトルデータベースはブラックボックス。
- **移植可能性** —— second-brain を新マシンに git clone すれば、Hippocampus は即座に走れる。ベクトルデータベースはインデックス再構築が必要。
- **外部依存なし** —— Chroma / Pinecone / pgvector のような runtime なし。
- **LLM 意味判断で十分** —— 2000 session 規模で、Opus で 5000 token INDEX.md を一度スキャンで十分、しかもより正確(Opus は本当に「subject 関連」を理解する、embedding は「ベクトル類似」しか理解しない)。

規模トリガーは `session-index-spec.md` に定義: INDEX.md が 5MB を超えるか p95 レイテンシが >10s の場合、**まず月別シャーディング**、それからキャッシュを議論。ベクトルデータベースルートは明確に考慮外。

### 同じ session が繰り返し検索される場合、「疲労」しますか?

はい—— GWT 仲裁器の **novelty** 次元が専門的にこれを処理します(詳細は [gwt-arbitration.md](./gwt-arbitration.md)):

| Novelty 値 | 条件 |
|-----------|------|
| 1.0 | これまで出現したことのないシグナル |
| 0.6 | 以前 1–2 回出現 |
| 0.2 | 3+ 回出現(**fatigue —— 既に見た**) |
| 0.0 | 既に処理済み解決済み |

したがって一つの履歴 session が繰り返し活性化されると、その salience は自然に減衰し、スクリーンを埋めません。

### Hippocampus が失敗し GWT が成功した場合、ROUTER は何を見ますか?

GWT 仲裁器は**単一源の失敗**を許容できます——初回 session、hippocampus タイムアウト、INDEX ファイル破損、すべて可。concept lookup と SOUL check のシグナル組み合わせで cognitive annotation を作れます。ROUTER が見る `[COGNITIVE CONTEXT]` には**`📎 Related past decisions` セクションがない**可能性がありますが、`🧬 Active concepts` と `🔮 SOUL dimensions` はあります。

---

## Troubleshooting

### 「ROUTER が履歴を引用していない、でも先週類似の意思決定をしたはず」

可能な原因(可能性順):

1. **先週のそれは全朝議を通っていない** —— Express 快速車線と direct-handle は `_meta/sessions/{session_id}.md` を書かないので、INDEX.md にそのエントリがありません。解決: あの対話に対してシステムに retrospective を補完させる、または手動で `_meta/journal/` から対応記録を探す。
2. **subject がマッチしない** —— Wave 1 の LLM 判断が今回の subject と先週のそれが**十分に意味的関連していない**と考えた可能性(例: 先週聞いたのは「共同創業者の分担」、今週聞くのは「権限委譲の境界」)。解決: 直接貼る——「2026-03-15 の共同創業者の分担議論を参照」。
3. **migration を走らせていない** —— v1.7 新規インストール後に `uv run tools/migrate.py` を走らせておらず、INDEX.md は空。解決: まず migration を走らせる。
4. **時間窓の外** —— デフォルト 3 ヶ月。前回の意思決定が 100 日前なら、デフォルトスキャン範囲に入りません。解決: `uv run tools/migrate.py --since YYYY-MM-DD` で範囲を拡大。

### 「検索結果が画面いっぱいの無関係履歴」

可能な原因:

- **Wave 1 LLM judgement 失調** ——連続 2 週 median top-1 relevance が 0.5 未満 = Wave 1 prompt の再チューニングが必要。これは AUDITOR の `cognitive_annotation_quality` 指標が捕捉するパターン(詳細は [auditor-eval-history.md](./auditor-eval-history.md))。
- **概念グラフに「hub」ノード**(一つの concept が数十の強エッジを接続)が存在し Wave 2 拡散が制御不能。`_meta/concepts/SYNAPSES-INDEX.md` を確認、edge count が特に高いノードを探し、分割を検討。
- **短期間のトピック重複** ——一週間に 5 回類似の質問をしたら、hippocampus は同じ session 集合を繰り返し返します。GWT novelty 次元が重みを下げますが、fatigue がまだ発動していなければ、うるさく見える可能性。数回上朝すればスムーズになります。

### 「Trace に '⚠️ signal no longer resolvable' が表示」

ある `signal_id` が指すファイルが削除または改名されました。よくある原因:

- `_meta/sessions/` 内のある履歴 session ファイルを手動で削除した
- Git ブランチ切り替え後にインデックスが不一致
- 概念が `_meta/concepts/_archive/` に retire された

解決: trace でこの警告が出ても、原始 citation は保持されます——**どこを指しているか**はわかる、ただそのファイルが一時的/永久に消えただけ。意図せず削除したなら git 履歴から復旧; アーカイブなら内容は依然として `_archive/` に残り手動で見られる。

---

## 深入り読書(Further reading)

製品入口:

- [What is Life OS](../../getting-started/what-is-life-os.md) — Life OS 全体の位置付け
- [Quickstart](../../getting-started/quickstart.md) — 初回上朝フロー

同ディレクトリのユーザー文書:

- [overview.md](./overview.md) — Cortex 総覧、hippocampus が四機構での位置を理解
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — Wave 2/3 が依存する概念グラフ
- [gwt-arbitration.md](./gwt-arbitration.md) — hippocampus シグナルが SOUL / concept シグナルとどう競争するか
- [narrator-citations.md](./narrator-citations.md) — `[S:xxx]` 引用フォーマットの完全意味論
- [auditor-eval-history.md](./auditor-eval-history.md) — `cognitive_annotation_quality` のスコア方法

Spec 層(最も権威、英語):

- `references/hippocampus-spec.md` — Agent 契約、入出力 schema、性能予算、failure modes
- `references/session-index-spec.md` — `INDEX.md` 一行要約フォーマット、シャーディングトリガー
- `references/concept-spec.md` — Wave 2/3 が通る `outgoing_edges` 重み意味論
- `references/gwt-spec.md` — hippocampus 出力が下流 arbitrator にどう消費されるか
- `references/cortex-spec.md` §Hippocampus — 全体アーキテクチャ内の位置

Agent 定義(深度ユーザー向け):

- `pro/agents/hippocampus.md` — 実際の subagent 定義、tool 制約、model 選択

---

**前篇**: [overview.md — Cortex 総覧](./overview.md)
**次篇**: [concept-graph-and-methods.md — 概念グラフと手法ライブラリ](./concept-graph-and-methods.md)
