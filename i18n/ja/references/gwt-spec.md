---
title: "GWT Arbitrator Spec · Cortex Layer"
version: 1.7
status: pre-implementation
audience: Life OS implementers
scope: Cortex Pre-Router Cognitive Layer — signal arbitration
translated_from: references/gwt-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
related:
  - references/cortex-spec.md
  - references/hippocampus-spec.md
  - references/concept-spec.md
  - references/soul-spec.md
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
---

# GWT Arbitrator Spec

## 1. 目的(Purpose)

**GWT (Global Workspace Theory) Arbitrator** は、Pre-Router Cognitive Layer のサブエージェントが emit したシグナルを統合し、ROUTER が受け取る **annotated input(注釈付き入力)** を生成します。

これは Stanislas Dehaene の **Global Neuronal Workspace** 理論に基づいています: 多くの専門モジュールが並列に動作し、その出力が中心的なワークスペースを巡って競合し、最も強いシグナルのみがグローバルにブロードキャストされます。この枠組みにおける意識とは、ignition の瞬間 — シグナルが競合に勝ち、他のすべてのモジュールに発信される瞬間 — のことです。

Life OS において、この競合は以下の間で起こります:

- hippocampus から検索された記憶
- concept store からの直接的な概念マッチ
- SOUL dimension シグナル(identity alignment または conflict)

arbitrator は **choke point(絞り込み点)** であり、ROUTER への情報過多を防ぎつつ、意思決定に最も関連するコンテキストを保持します。

---

## 2. トリガー(Trigger)

- すべての Pre-Router 並列サブエージェント(hippocampus、concept lookup、SOUL dimension check)が現在のセッションターンでの作業を完了した **後** に動作します。
- **セッションターンごとに単一の起動。** ループしません。ターン途中で再発火することもありません。
- **タイムアウト予算:** ソフトターゲット 5 秒、ハードシーリング 10 秒。
- ハードシーリングに達した場合、arbitrator はすでにスコアリング済みのシグナルを使用して部分結果を emit します(§13 参照)。

---

## 3. エージェント定義(Agent Definition)

```yaml
---
name: gwt-arbitrator
description: "Cortex GWT arbitration — consolidates Pre-Router signals into annotated ROUTER input"
tools: [Read]
model: opus
---
```

設計上 read-only です。arbitrator は永続ストアに書き込むことはありません。すべての変更(Hebbian 更新、concept 作成、synapse 強化)は ARCHIVER Phase 2 で発生します。これによりセッション中のパスが安価で副作用のないものに保たれます。

---

## 4. 入力コントラクト(Input Contract)

orchestrator は arbitrator に 4 つの入力を渡します:

```
hippocampus_output:      yaml  # retrieved sessions, activated concepts
concept_lookup_output:   yaml  # direct concept matches to current subject
soul_check_output:       yaml  # relevant SOUL dimensions and their status
current_user_message:    string
```

各上流ソースは、統一された envelope を持つ **signals** のリストを生成します(スコアリングは §5、シグナル型は §6 を参照)。ソースの欠落は許容されます — 初回のセッションでは hippocampus 出力が存在しない可能性があり、arbitrator は手元にあるものだけで処理を進めます。

---

## 5. Salience Formula (CRITICAL — 明示的かつ固定)

すべてのシグナルは **単一のスカラー** である `salience` でスコアリングされます:

```
salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2
```

この formula は v1.7 で固定です。各コンポーネントは `[0.0, 1.0]` の float で、以下に定義されます。

### 5.1 urgency

| 値 | 条件 |
|-------|-----------|
| 1.0 | 7 日以内の期限を持つ action item |
| 0.6 | SOUL conflict 警告(`core` dimension が挑戦されている) |
| 0.3 | 繰り返しパターン検出(同一主題が最近 3 回以上確認された) |
| 0.0 | 時間的プレッシャーのない背景コンテキスト |

### 5.2 novelty

| 値 | 条件 |
|-------|-----------|
| 1.0 | シグナルがこれまで浮上したことがない |
| 0.6 | シグナルが過去に 1–2 回浮上した |
| 0.2 | シグナルが 3 回以上浮上した(fatigue — ユーザーはすでに見ている) |
| 0.0 | すでに行動され解決済み |

### 5.3 relevance

シグナルペイロードとユーザーメッセージの現在の主題との間のキーワード / 概念のオーバーラップスコア。arbitrator 内部で **LLM judgment** により計算されます。

LLM はシグナルの内容と現在のユーザーメッセージを受け取り、そのシグナルが手元の意思決定にどれほど直接関連するかを表す `[0.0, 1.0]` の単一の float を生成するよう要求されます。キーワードオーバーラップは、LLM judgment が失敗したときの決定論的フォールバックです(§13 参照)。

### 5.4 importance

ティア名は `references/soul-spec.md` §Tiered Reference by Confidence および `references/snapshot-spec.md` §Tier Mapping と一致します。すべての confidence バンドは半開区間 `[a, b)` を使用します — 下限は inclusive、上限は exclusive。境界値は常に **上位** ティアに属します(例: confidence が正確に 0.3 の場合は `emerging` ではなく `secondary`、正確に 0.7 の場合は `secondary` ではなく `core`)。

| 値 | 条件 |
|-------|-----------|
| 1.0 | SOUL `core` dimension (confidence ∈ `[0.7, 1.0]`) |
| 0.7 | SOUL `secondary` dimension (confidence ∈ `[0.3, 0.7)`) |
| 0.5 | critical-path プロジェクトに関連(concept metadata にタグ付け) |
| 0.3 | SOUL `emerging` dimension (confidence ∈ `[0.2, 0.3)`) |
| 0.2 | identity や project との結びつきのない一般コンテキスト(あるいは `dormant` dimension(confidence ∈ `[0.0, 0.2)`)、コンテキストとしてのみ含まれる) |

複数の条件が適用される場合は、**最も高い** マッチ値を使用します。

---

## 6. 統合されるシグナル型(Signal Types Consolidated)

arbitrator はソース別に以下のシグナル型を認識します:

### hippocampus から

- `decision_analogy` — 現在の主題と類似したパターンを持つ過去の意思決定
- `value_conflict` — SOUL と衝突した過去のセッションで、ここに関連するもの
- `outcome_lesson` — 結果が教訓になる過去の意思決定

### concept lookup から

- `canonical_concept` — 直接言及または暗示された confirmed な概念
- `emerging_concept` — 同じ領域における tentative な概念(まだ canonical ではない)

### SOUL check から

- `tier_1_alignment` — core identity dimension が方向性を支持する
- `tier_1_conflict` — core identity dimension が衝突する(**semi-veto signal**)
- `tier_2_relevant` — secondary dimension が主題に適用される
- `dormant_reactivation` — dormant dimension が今再び関連するようになった

シグナルは `signal_type`、`source`、`payload`、および 4 つのスコアリングコンポーネントを超えて、arbitrator にとって不透明です。arbitrator はペイロードを内省して新しいシグナルを導出することはありません。各シグナルは名前付きのソースを持たなければなりません。

---

## 7. 仲裁アルゴリズム(Arbitration Algorithm)

仲裁は 5 つの決定論的ステップに、1 つの LLM judgment ステップ(relevance)を加えたものです:

1. **Ingest** — orchestrator からすべてのシグナルをメタデータとともに受け取る。
2. **Score** — §5 の formula を用いて各シグナルの `salience` を計算する。relevance は LLM judgment を使用し、他のすべてのコンポーネントはルールベース。
3. **Rank** — salience の降順でシグナルをソートする。
4. **Cap** — 全体で上位 **5** シグナルを取る(ハードキャップ、情報過多を防ぐ)。
5. **Detect conflicts**:
   - 任意の `tier_1_conflict` シグナル → 出力の ⚠️ SOUL CONFLICT ヘッダーに **elevate(昇格)** する。
   - 矛盾する `decision_analogy` シグナル(過去の意思決定が反対の方向を示唆) → パターン観察ブロックで "inconsistent precedent" としてフラグする。
6. **Compose** — §8 に従い注釈付き出力をレンダリングする。

シグナルは arbitrator によって **invent(でっち上げ)** されてはなりません。出力中のすべての項目は、特定の入力シグナルにトレースできなければなりません。

### 7.1 計算例(Worked Example)

上流サブエージェントから 3 つのシグナルが与えられた場合:

| id | type | urgency | novelty | relevance | importance | salience |
|----|------|---------|---------|-----------|------------|----------|
| s1 | `decision_analogy` | 0.3 | 0.6 | 0.8 | 0.5 | 0.55 |
| s2 | `tier_1_conflict` | 0.6 | 1.0 | 0.9 | 1.0 | 0.85 |
| s3 | `canonical_concept` | 0.0 | 0.2 | 0.7 | 0.5 | 0.35 |

ランキング後: `[s2, s1, s3]`。`s2` は SOUL CONFLICT 昇格をトリガーします。3 つすべてが top-5 キャップ内に収まり、出力に構成されます。`s3` は salience 0.35 ですが、シグナル当たりの下限が 0.3 であるため、依然として含まれます。

---

## 8. 出力フォーマット — 注釈付き ROUTER 入力(Output Format — Annotated ROUTER Input)

arbitrator は、ROUTER に到達するときにユーザーメッセージの **前に付加(prepend)** される単一の Markdown ブロックを emit します:

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

⚠️ SOUL CONFLICT: [only if `core` dimension challenged]
This decision challenges your "{dimension_name}" (confidence {X})

📎 Related past decisions:
- {session_id} ({date}): {reason}, score {X}/10

🧬 Active concepts:
- {concept_id} (canonical, weight {X}, last activated {when})

🔮 SOUL dimensions:
- {dimension} ({tier}, {trend}): {support/challenge status}

💡 Pattern observations:
- {any salience ≥ 0.8 signals not covered above}

[END COGNITIVE CONTEXT]

User's actual message: {original}
```

各ブレットは、そのカテゴリーのシグナルが top-5 に **少なくとも 1 つ** ある場合にのみ emit されなければなりません。空のカテゴリーは折りたたまれます(§9 参照)。

---

## 9. シグナル抑制ルール(Signal Suppression Rules)

注釈ノイズを防ぐため:

- スコアリング後に **総シグナル数が 0** の場合、**empty marker(空マーカー)** を emit します — 完全なフレーミングテキストは emit しません。ROUTER は `User's actual message: …` のみを見ます。
- **すべてのシグナルが salience < 0.3** の場合、`(no high-salience signals)` を単一行マーカーとして emit し、カテゴリブロックをスキップします。
- **SOUL CONFLICT** が存在するが関連する過去の意思決定がない場合でも、SOUL ブロックは emit します(衝突自体が load-bearing なため)。
- **カテゴリごとのキャップ:** 関連意思決定 最大 5 件、active concept 最大 5 件、SOUL dimension 最大 5 件。カテゴリごとのキャップは **ブロック単位のローカル極大値** であり、§7 の全体 top-5 を超える追加スロットではありません。§7 の全体 top-5 はハード上限であり、常に最初に適用されます。実運用上: カテゴリキャップが全体 top-5 予算の消費前に到達した場合、残りの全体スロットは空いたままになります。全体 top-5 が先に埋まった場合、カテゴリキャップはそれに上書きされます。「5 つの SOUL dimension が出力を埋める」例は、たまたま 5 つの全体スロットすべてが単一カテゴリ内で最高スコアとなっただけのことです。

---

## 10. 同点処理ルール(Tie-Breaking Rules)

スコアリング後に 2 つのシグナルの **salience が同一** である場合、以下の順序で同点を解消します:

1. **より新しいものを優先** — より最近の `timestamp` を持つシグナルを優先する。
2. **より高い importance** — それでも同点の場合、より高い `importance` を持つシグナルを優先する。
3. **`signal_id` のアルファベット順** — 同じ入力が常に同じランキングを生成するよう、完全に決定論的なフォールバック。

同点処理は決定論的でなければなりません。ランダム化はなし。同じ入力での 2 回の実行は、同じ出力ランキングを生成しなければなりません。

---

## 11. パフォーマンス予算(Performance Budget)

| Stage | ターゲット |
|-------|--------|
| 入力の受信(in-context で渡される) | instant |
| relevance スコアリングのための LLM judgment | ~2 s、~3,000 tokens |
| Composition | < 1 s |
| **Total target** | **< 3 s** |

ソフトタイムアウト(§2)は 5 秒、ハードシーリングは 10 秒。ハードシーリングを超えると、§13 の部分出力失敗モードがトリガーされます。

---

## 12. 注入位置(Injection Location — CRITICAL for prompt caching)

認知コンテキストは、**user role 内部** の **user message への prefix** として注入されます。system prompt に追加されることは **ありません**。

**なぜ:** Anthropic の prompt cache は安定した system prompt に対してのみヒットします。動的な認知アノテーションがそこに注入されると、すべてのケースでキャッシュが無効化されます。動的コンテンツを user role 内に保つことで、ターンをまたいだキャッシュヒット率が維持されます。

**実装:**

1. orchestrator は arbitrator を呼び出し、その出力をキャプチャする。
2. orchestrator は arbitrator のブロックを ROUTER の入力ユーザーメッセージの **先頭に付加(prepend)** する。
3. ROUTER は結合された入力を見る。認知コンテキストを **reference(参照)** として使用し、文字通りのユーザーリクエストとしては使用しない。
4. ROUTER の system prompt は変更されない。

ROUTER の triage ルールは変更されません。COGNITIVE CONTEXT ブロックを、どのドメインエージェントをディスパッチするかを決定する際に **参考にしてもよい** 補助情報として扱います。

---

## 13. 失敗モード(Failure Modes)

| 失敗 | 動作 |
|---------|----------|
| **Pre-Router 入力なし**(初回セッション) | empty marker を emit。ROUTER は raw user message のみを見る。 |
| **単一入力ソース**(例: hippocampus が何も返さなかった) | シグナルを返したソースだけで処理を進める。 |
| **relevance のための LLM judgment が失敗 / タイムアウト** | relevance スコアとして、シグナルペイロードとユーザーメッセージの間の **キーワードオーバーラップ** にフォールバックする。 |
| **Arbitrator 全体タイムアウト**(ハードシーリング) | これまでに得られたベストスコアのシグナルを用いて、top-5 にキャップして部分出力を emit。ブロックに `(partial — timed out)` という単一行を追加する。 |
| **上流からの malformed signal** | そのシグナルをスキップ。クラッシュしない。AUDITOR レビュー用に内部でログを残す。 |

Graceful degradation は交渉の余地なし: arbitrator の失敗は ROUTER をブロックしては **なりません**。疑わしい場合、orchestrator は v1.6.2a の動作(raw user message を直接 ROUTER へ)に fall through します。

---

## 13.1 劣化階層(Degradation Hierarchy)

複数の失敗が積み重なった場合、以下の順序で適用します:

1. ソース欠落 → 存在するもので進める。
2. LLM relevance 失敗 → キーワードオーバーラップにフォールバック。
3. ハードタイムアウト → 部分出力。
4. arbitrator の壊滅的失敗 → empty marker + 生の ROUTER 動作への fall-through。

すべてのステップで、出力は依然として有効な注釈ブロックです(空であっても)。ROUTER が ill-formed または half-closed なブロックを受け取ることは決してあってはなりません。

---

## 14. 品質メトリクス(Quality Metrics)

AUDITOR の `eval-history` トラック用:

- **`cognitive_annotation_quality` (0–10)** — ROUTER がアノテーションを生産的に参照したか?
  - 具体的には: REVIEWER はアノテーションを引用したか? いずれかのドメインエージェントは審議中にそれを参照したか?
- **`annotation_utilization_rate`** — 少なくとも 1 つの下流エージェントがアノテーションの `signal_id` を使用したセッションの割合。
- **`suppression_precision`** — arbitrator が SOUL CONFLICT 警告を emit したとき、REVIEWER が独立して同じ問題をフラグした頻度。

AUDITOR は低スコアのセッションをレビューのために surface します。アノテーション品質が 30 日間下降トレンドにある場合、AUDITOR の patrol inspection は eval-history でパターンをフラグし、モジュールレベルのスコープ変更は通常の spec 改訂プロセスを経て進行します。

---

## 15. アンチパターン(Anti-patterns)

- **シグナルをでっち上げない。** 出力中のすべてのシグナルは、名前付きソースと上流ペイロードを持たなければなりません。
- **SOUL ティアだけでランク付けしない。** importance は salience の 4 コンポーネントのうちの 1 つです。高い urgency と高い novelty を持つ `emerging` シグナルは、低い urgency を持つ `core` シグナルを正当に上回り得ます。
- **生のサブエージェント出力をアノテーションに含めない。** コンセプト参照と短い要約に統合します。完全なペイロードはトレーサビリティのため frame md に残ります。
- **system prompt を変更しない。** すべての動的コンテンツは user role のメッセージに置かれます(§12 参照)。
- **カテゴリあたり 5 シグナル、全体で 5 シグナルを超えない。** 情報過多は失敗モードであり、機能ではありません。
- **arbitrator の内部から hippocampus や concept lookup を呼び出さない。** 上流サブエージェントが真実の情報源であり、arbitrator は純粋な consumer です。

---

## 16. 関連仕様(Related Specs)

- `references/cortex-spec.md` — Cortex 全体アーキテクチャ
- `references/hippocampus-spec.md` — シグナルソース: クロスセッション検索
- `references/concept-spec.md` — シグナルソース: concept store と synapse graph
- `references/soul-spec.md` — SOUL ティア定義と confidence バンド
- `devdocs/brainstorm/2026-04-19-cortex-architecture.md` — 設計根拠(§3 schema、§4 salience debate)
- `devdocs/architecture/cortex-integration.md` — arbitrator が 11 ステップワークフローの Step 0.5 にどう接続するか

---

**Document status:** pre-implementation spec, v1.7。ここに符号化された動作は規範的(normative)です。逸脱する場合は、コードの前に本 spec を更新する必要があります。

---

> ℹ️ **2026-04-22 更新**:EN R3.2 §5.4 tier 境界 + §9 per-category cap 表現の修正を同期

*訳注: 本文は英語版 2026-04-22 スナップショットの翻訳。英語版が権威源で、曖昧な場合は英語版が優先。*
