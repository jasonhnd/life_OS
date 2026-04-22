---
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# Cortex 総覧 · v1.7 認知層概要(Cortex Overview)

> パンくず: [← 製品入口:ユーザーガイド索引](../index.md)

> v1.7 は Life OS に「認知基盤」を一枚追加しました—— Cortex。これは新しい役割でも、新しいコマンドでもありません。あなたが発言するたびに、システムが自動的に履歴を見返し、関連概念を活性化させ、SOUL と照合するようにするものです。本文は Cortex の 6 篇のユーザーガイドの入口です。

## Cortex とは(What is Cortex)

Cortex は v1.7 で新しく導入された **Pre-Router Cognitive Layer**(予ルーティング認知層)で、Life OS の命名体系では SOUL / Wiki / DREAM / STRATEGIC-MAP と並列に位置付けられます:

| モジュール | 何を記録するか | 範囲 |
|------|---------|------|
| SOUL | あなたは誰か(アイデンティティ、価値観) | 人格 |
| Wiki | あなたが知っていること(世界の事実) | 知識 |
| DREAM | オフライン睡眠段階で発見したこと | 深度処理 |
| STRATEGIC-MAP | 現在のあなたの布陣 | クロスプロジェクト戦略 |
| **Cortex** | **あなたがどう考えるか** | **上朝前の認知** |

Cortex はどのモジュールも置き換えません。それがすることはただ一つ: **ROUTER があなたのメッセージを見る前に、メッセージに「認知注釈」を一枚貼る**——関連する履歴、概念グラフで点灯しているノード、SOUL 衝突シグナルを一緒に持たせ、後続のすべての役割(PLANNER、六領域、REVIEWER……)が**ゼロから始まらないようにする**ことです。

---

## なぜ Cortex を追加するのか(Why add Cortex)

v1.7 以前、Life OS の長期記憶は二つのノードでしか触れられませんでした:

- **Start Session** —— RETROSPECTIVE が一度読む
- **Adjourn** —— ARCHIVER が一度書く

**その間のすべての意思決定は、現在の対話だけで行われていました**。16 個の subagent の checks-and-balances がどれほど厳密でも、全員の脳内にある「共有の下地」は空でした:

- PLANNER は先月ほぼ同じ意思決定をしたことを知らない
- 六領域分析時に概念間の関連が見えない
- REVIEWER は本意思決定の内部一貫性だけをチェックし、クロスセッションはチェックしない
- Adjourn 後、SOUL と Wiki の自動書き込み以外、何の痕跡も残らない

ユーザー体感は: **「この AI は一回のセッション内ではかなり慎重だが、新セッションを開くと全部忘れる。」**

Cortex が解決しようとするのはこの問題です—— クロスセッション記憶、概念グラフ、自己フィードバックを各 workflow の「一等公民入力」に変えます。

---

## ユーザー側体験変化の総覧(User-side experience changes)

v1.7 にアップグレードしても、**使用習慣を変える必要はありません**。すべての新機能はバックグラウンドで自動的に動作します。ただし 6 つの可視変化があり、次回の上朝で現れます:

### 1. 上朝時に「Cognitive Context」ブロックが追加される

ROUTER はあなたのメッセージを受け取ると同時に、一段の `[COGNITIVE CONTEXT]` 注釈を先に見ます——関連する履歴 session、点灯した概念、SOUL 衝突リマインダー。あなたは奏上書で間接的に感じます: 提案がより思いやりがあり、次元がより全面的で、「以前類似のことをどう処理したか」をあまり聞かれません(システムが自分でチェック済みだから)。

→ 詳細は [hippocampus-recall.md](./hippocampus-recall.md)

### 2. Adjourn 後、システムが「概念」と「手法」を自動蓄積し始める

session が終わるたびに、ARCHIVER Phase 2 が対話をスキャンし、繰り返し現れる概念ノード、5+ ステップのワークフローを候補として抽出します。次回の Start Session の朝報で、RETROSPECTIVE が尋ねます: 「候補概念 2 個と候補手法 1 個を検出、確認しますか?」

→ 詳細は [concept-graph-and-methods.md](./concept-graph-and-methods.md)

### 3. 奏上書に `[S:xxx][D:yyy][SOUL:zzz]` のような引用が現れ始める

Narrator 層は奏上書の「実質的な断言」(例:「以前もこの問題に遭遇した」)に強制的に引用を追加します。これは装飾ではありません——「この文を trace して」と言えば、システムは元の signal とサポートテキストを見せてくれます。目的: **AI がもっともらしい歴史を捏造するのを防ぐ**。

→ 詳細は [narrator-citations.md](./narrator-citations.md)

### 4. 複数源シグナルが衝突する際、システムは「顕著性」(salience)で最重要を選んで提示

GWT 仲裁器(Global Workspace Theory arbitrator)は 4 次元でスコアリング—— **urgency / novelty / relevance / importance** ——可能な数十条のシグナルから top-5 を選んで提示。最高スコアのものが SOUL コア衝突なら、特別に赤字マークされます。

→ 詳細は [gwt-arbitration.md](./gwt-arbitration.md)

### 5. Start Session 朝報に「システム性問題検出」ブロックが現れる可能性

AUDITOR は session 終了時に自分で 10 次元のスコアをつけ、`_meta/eval-history/` に書き込みます。RETROSPECTIVE は毎回 Start Session で直近 10 件を読みます。「連続 3 回 adjourn 不完全」「narrator 引用失敗 >20%」などのパターンを検出すると、朝報 DREAM ブロックの後に警告を出します。

→ 詳細は [auditor-eval-history.md](./auditor-eval-history.md)

### 6. 概念ノードが「ヘブ式」(Hebbian)に強化または衰退する

session で概念を使うたびに、その活性化カウント +1、関連エッジ重み +1。連続して使わないと、permanence レベル別に衰退(identity は衰退せず / skill は対数衰退 / fact は指数衰退 / transient は期限切れでクリア)。**使うほど強く、使わなければ徐々にフェードアウト**——脳と同じです。

→ 詳細は [concept-graph-and-methods.md](./concept-graph-and-methods.md)

---

## 推奨読書順序(Recommended reading order)

v1.6.2a からアップグレードしてきて、**初めて Cortex を聞いた**人は、この順序で読むのが最も効率的です:

1. **本文**(総覧 + 体験変化)← あなたはここ
2. [**hippocampus-recall.md**](./hippocampus-recall.md) — クロスセッション検索(Cortex が何をするか最も直感的に理解できる入口)
3. [**concept-graph-and-methods.md**](./concept-graph-and-methods.md) — 概念グラフと手法ライブラリ(システムがどう「知恵を蓄積する」かを理解)
4. [**narrator-citations.md**](./narrator-citations.md) — Narrator 引用機構(奏上書に角括弧マークが増えた理由を理解)
5. [**gwt-arbitration.md**](./gwt-arbitration.md) — GWT 仲裁(複数源シグナルの衝突と勝者選びを理解)
6. [**auditor-eval-history.md**](./auditor-eval-history.md) — AUDITOR 自己評価データ(システムの自己監視方法を理解)

---

## Cortex が変えないもの(What Cortex does not change)

懸念を払拭するため、先に**変わらないこと**をリスト化します:

- **11 ステップ workflow は変更なし** —— Cortex が追加するのは Step 0.5(ROUTER の前)と Step 7.5(Narrator 検証)、旧 Step 1–11 の番号は全く動かしません
- **ROUTER の分診ロジックは変更なし** —— Cortex は ROUTER により良い入力を与えるだけ、ROUTER は参考にも無視にもできます
- **情報隔離は変更なし** —— PLANNER は依然として ROUTER の推論を見えず、REVIEWER は依然として計画文書のみを見ます、この安全モデル表は v1.7 で**3 行追加しただけ**(hippocampus、gwt-arbitrator、narrator-validator 各 1 行)、旧行は動かしません
- **Markdown-first は変更なし** —— すべての新データは `.md + YAML frontmatter`。新データベースなし、Python runtime なし、cron なし、外部 API key なし
- **Notion 同期範囲は変更なし** —— Cortex データ**は Notion に同期しません**。概念グラフ、session 要約、eval-history はすべてローカル `_meta/` 下の内省資産です
- **降級フォールバック** —— Cortex の任意の subagent が失敗(タイムアウト、ファイル読めない)、orchestrator は自動的に v1.6.2a 動作に退化(原始メッセージ直接 ROUTER へ)、session は通常通り進行

**言い換えれば: Cortex は加算層であり、破壊的アップグレードではありません**。Cortex が全部壊れても、あなたの Life OS は依然として馴染みのある Life OS で、ただ履歴検索と引用が減るだけです。

---

## 初回アップグレードで何をすべきか(What to do on first upgrade)

短い答え: **migrate を一つ走らせれば終わり**。

```
uv run tools/migrate.py
```

このスクリプトは:

1. あなたの**最近 3 ヶ月**の `_meta/journal/*.md` をスキャン——より古い内容は**触れません**(古い journal には期限切れプロジェクトや降格価値観がよく含まれ、引き入れても概念グラフを汚染するだけ)
2. 各履歴 session に対して要約を生成し `_meta/sessions/{session_id}.md` に書き込み
3. 繰り返し現れる実体と手法を候補 concept として抽出、`_meta/concepts/_tentative/` に投入
4. `SYNAPSES-INDEX.md` と `INDEX.md` を再構築
5. 一部の SOUL snapshot を補完
6. プロセスを `_meta/cortex/bootstrap-status.md` に書き込み

スクリプトは**冪等的**です——二度走らせても重複作成しません。migrate が失敗したら、orchestrator は v1.6.2a 動作に退化、後で再試行できます。

### journal ゼロの新規ユーザーの場合

Cortex は **cold-start mode** に入ります—— `[COGNITIVE CONTEXT]` は基本空で、十分な session が蓄積されるまで内容が出ません。システム使用を妨げるものは何もなく、最初の数十回の上朝ではクロスセッション記憶の増分を得られないだけです。

---

## Cortex が「静か」になる(動作しない)とき(When Cortex stays silent)

三つのシーンで、**Step 0.5 はスキップまたは簡略化されます**:

| シーン | Cortex 動作 |
|------|-----------|
| **ROUTER 直接処理**(挨拶、翻訳、簡単な照会) | **完全スキップ** ——認知注釈なし、narrator 検証なし、ROUTER が直接返答 |
| **Express 快速車線**(領域レベル分析、意思決定なし) | **簡略化** —— hippocampus のみ実行、concept lookup と SOUL check は実行しない; 出力は一行、三段ではない |
| **STRATEGIST 群賢堂** | **完全スキップ** —— STRATEGIST は Draft-Review-Execute を通らず、narrator も介入しない |

理由: これらのシーンは履歴を見返す時間をかける必要がありません。Cortex の設計目標は「**全朝議**意思決定時に記憶を引き入れる」ことで、入力のたびに再スキャンすることではありません。

---

## 四つのコア機構を一言で(Four core mechanisms in one sentence each)

Cortex 内部は四つの機構で構成されています。それぞれ自分の spec と user-guide ページがあります:

1. **Hippocampus** — クロスセッション検索。3 波の拡散活性化: 直接マッチ → 強エッジ隣人 → 弱エッジ隣人。top 5–7 関連 session を「記憶シグナル」として。
2. **GWT Arbitrator** — 複数源シグナルの顕著性競争。4 次元スコアリング、top-5 ブロードキャスト、`tier_1_conflict` は SOUL CONFLICT 警告に昇格。
3. **Narrator Layer** — 根拠ある生成。奏上書の実質的断言は `signal_id` 引用必須。validator subagent が強制チェック、3 回の書き直しで通らなければ無引用版に退化。
4. **Synapses + Hebbian** — 概念グラフ + 使うほど強いエッジ重み。4 レベル permanence が衰退曲線を決定。Adjourn のたびに ARCHIVER Phase 2 が decay を一度実行。

---

## よくある疑問(FAQ)

### Cortex は遅くなりますか?

Step 0.5 の総予算は **< 7 秒**(hippocampus 5s ソフトタイムアウト + concept lookup と SOUL check 並列)。Step 7.5 の narrator 検証は **2–5 秒**(書き直し 1 回で 2–5 秒追加、最大 3 回リトライ、ハード上限 15 秒)。

**全朝議 1 回の意思決定はもともと六領域 + COUNCIL を走らせる必要があり、この数秒はほとんど感じません**。Express と direct-handle は hippocampus のみ実行か完全スキップで、遅くなりません。

### Cortex をオフにできますか?

できます。`_meta/cortex/config.md` を編集し、`cortex_enabled: true` を `false` に変更、次の Start Session で v1.6.2a 動作に退化します。各サブ機能にも個別スイッチがあります: `hippocampus_enabled`、`gwt_arbitrator_enabled`、`narrator_validator_enabled`、`concept_extraction_enabled`。

ただし**長期間オフにすることは推奨しません**——数回上朝するうちに、システムが「以前どう決めたか」に対する敏感度が顕著に向上するのを発見し、オフにすると逆に AI が退化したと感じるでしょう。

### Cortex が記憶違いしたら? 私の履歴が誤って要約されたら?

二つのフォールバック:

1. **Narrator 層の citation は真の signal を強制引用** ——narrator が「過去 5 回の意思決定はすべて保守的」と言うなら、5 個の真実の session ファイルを指さなければならず、さもなくば validator が直接差し戻して書き直します。角括弧引用付きの任意の断言に対して「この文を trace して」と言えば、システムが原文を見せてくれます。
2. **Three-tier 取消機構** ——ある概念が誤って昇格された場合、「直近の concept を取り消し」と言うか `_meta/concepts/{domain}/{concept_id}.md` を直接削除すれば、archiver が次回 SYNAPSES-INDEX を再構築し宙ぶらりんエッジを剪定します。

より深刻な矛盾(例: SOUL 次元が誤って書き込まれた)は SOUL 自体の取消フローを通り、Cortex 層の事ではありません。

### 私のプライバシーデータが概念グラフに書き込まれますか?

いいえ。ARCHIVER Phase 2 は概念を抽出する前に**プライバシーフィルター**を走らせます(wiki のそれと同じ):

- 人名(公人かつ結論と直接関連する場合を除く) → 剥離
- 具体的な金額、口座、ID → 剥離
- 具体的な会社名(公開事例を除く) → 剥離
- 家族友人 → 剥離
- 追跡可能な日付 + 場所の組み合わせ → 剥離
- フィルター後に概念に意味がなくなれば → **破棄**(それは本来個人ノートであり、再利用可能概念ではないことを示す)

さらに、**個人(人)は concept になれません** ——それは SOUL の領地であり、概念グラフには `personal/{someone}.md` すら許されません。

---

## 深入り読書(Further reading)

製品入口:

- [What is Life OS](../../getting-started/what-is-life-os.md) — Life OS とは何か、その中での Cortex の位置付け
- [Quickstart](../../getting-started/quickstart.md) — 初回上朝フロー

ユーザー文書(本ディレクトリ 5 兄弟):

- [hippocampus-recall.md](./hippocampus-recall.md) — クロスセッション記憶検索のユーザー体験
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — 概念グラフ + 手法ライブラリ
- [narrator-citations.md](./narrator-citations.md) — 引用フォーマットと trace UX
- [gwt-arbitration.md](./gwt-arbitration.md) — 顕著性競争
- [auditor-eval-history.md](./auditor-eval-history.md) — 自己フィードバックデータ

アーキテクチャ層(Cortex がどう構築されているかを見たい読者向け):

- `devdocs/architecture/cortex-integration.md` — 11 ステップ workflow 内の Step 0.5 / Step 7.5 挿入点
- `docs/architecture/markdown-first.md` — なぜ `.md + YAML` を堅持し、データベースを導入しないのか

Spec 層(最も権威、ただし英語・技術志向):

- `references/cortex-spec.md` — 全体アーキテクチャ、四機構の位置付け、データ構造
- `references/hippocampus-spec.md` — 検索アルゴリズム 3 波拡散
- `references/concept-spec.md` — 概念ファイル schema、Hebbian 更新アルゴリズム
- `references/method-library-spec.md` — 手法ライブラリ schema、三段 maturity ladder
- `references/narrator-spec.md` — 引用フォーマット、validator アルゴリズム、trace UX
- `references/gwt-spec.md` — 顕著性公式、仲裁アルゴリズム
- `references/eval-history-spec.md` — 10 次元スコア表、システム性問題検出

---

## 一つの実例(A real example)

あなたは決めました: 「この四半期、新製品ラインを共同創業者 A に任せるべきか?」

### v1.6.2a のフロー

```
あなた → ROUTER 分診 → PLANNER 計画(六次元)→ ...
```

PLANNER はゼロから考えます。今回のテーマを知っていて、SOUL を知っていて、紐づくプロジェクトを知っています——**しかし知らない**:
- 先四半期ほぼ同じ問題を問うていて、答えは「あと 3 ヶ月様子見」だった
- 「共同創業者 A」の概念はシステムに 12 回出現、edge weight と「コントロール権」が極めて強い
- あなたの「家族優先>事業」(confidence 0.82)と「単独リスク」(SOUL tier-1)が衝突する可能性

### v1.7 のフロー

```
あなた → Step 0.5 (Cortex) → ROUTER 分診 → PLANNER 計画 → ...
```

Step 0.5 は、あなたが Enter を押して ROUTER がメッセージを見るまでの**< 7 秒**以内に:
- Hippocampus が先四半期のあの意思決定を発見 → `S:claude-20260115-1020`
- Concept lookup が「共同創業者 A」ノードと強エッジを発見 → `C:relationship:partner-a-control`
- SOUL check が「家族優先」次元の tier_1_conflict シグナルを発見
- GWT arbitrator が顕著性順にソート、`tier_1_conflict` salience 0.85 → SOUL CONFLICT 警告に昇格

ROUTER が見るメッセージはこうなります:

```
[COGNITIVE CONTEXT]
⚠️ SOUL CONFLICT: この意思決定はあなたの「家族優先」(confidence 0.82)に挑戦
📎 Related past decisions:
- 2026-01-15 | 共同創業者権限委譲 (score 8.2) — 前回のあなたの結論は「あと 3 ヶ月様子見」
🧬 Active concepts:
- partner-a-control (canonical, weight 42, last activated 4d ago)
🔮 SOUL dimensions:
- 家族優先>事業 (core, ↘ stable): tier_1_conflict
- 単独リスク (secondary, ↗ up): tier_2_relevant
[END COGNITIVE CONTEXT]

User's actual message: この四半期、新製品ラインを共同創業者 A に任せるべきか?
```

PLANNER が受け取るのは**context 付きの計画入力**です。先四半期の結論を忘れず、SOUL 衝突を無視せず、「共同創業者 A」が誰かを再発見しません。

これが Cortex が存在する全ての理由です。

---

**次篇**: [hippocampus-recall.md — クロスセッション記憶検索](./hippocampus-recall.md)
