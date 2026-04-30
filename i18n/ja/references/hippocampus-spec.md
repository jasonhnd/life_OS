---
title: "Hippocampus · Agent Contract Spec"
scope: v1.7 Cortex Phase 1
audience: Life OS developers + orchestrator
status: spec
version: v1.7
layer: Cortex Phase 1 (cognitive retrieval)
translated_from: references/hippocampus-spec.md
translator_note: 自動翻訳 2026-04-21、人間校正待ち
related:
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
  - references/cortex-spec.md
  - references/concept-spec.md
  - references/session-index-spec.md
  - references/gwt-spec.md
  - pro/agents/hippocampus.md
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Hippocampus · Agent Contract Spec

> 本ドキュメントは **hippocampus サブエージェント** のコントラクトを規定します: 何を受け取り、何を返し、どのように検索し、どのように失敗するか。エージェント本体は `pro/agents/hippocampus.md` にあります。本仕様はその動作に関する authoritative なソースです。

---

## 1. 目的(Purpose)

**Hippocampus** は、Pre-Router Cognitive Layer(v1.7 ワークフローの Step 0.5)のために、**クロスセッション記憶検索** を行う Claude Code サブエージェントです。

その単一責任: ユーザーの現在のメッセージが与えられると、**関連する過去セッションの概念レベル要約** を生成し、GWT arbitrator が他の Pre-Router 認知シグナルと統合して ROUTER 向けの注釈付き入力にできるようにします。

これは生物学的な **hippocampus** — 新しい経験を episodic memory に結びつけ、要求に応じてエピソードを検索することを担う脳領域 — をモデルにしています。Life OS において、これは「ユーザーが今言ったこと」と「システムが過去のセッションからすでに知っていること」のギャップを橋渡しします。

Hippocampus は以下を **しません**:

- ROUTER triage の置き換え
- セッションファイルや concept ファイルの変更(read-only)
- 現在フレーム外への検索結果の永続化
- 他の Pre-Router Cognitive Layer 出力を知ること(強制された隔離)

---

## 2. トリガー(Trigger)

**頻度**: RETROSPECTIVE のハウスキーピングが完了した後、ROUTER に入るすべてのユーザーメッセージ。

**並列性**: 他の 2 つの Pre-Router Cognitive Layer コンポーネントと並列に動作:

- Concept lookup(`_meta/concepts/INDEX.md` を読む)
- SOUL dimension ヘルスチェック(RETROSPECTIVE の SOUL Health Report を再利用)

**実行予算**:

- Soft timeout: **5 秒** — GWT arbitrator が待つ上限で、この時点を過ぎると部分結果を持って進行する。これは hippocampus に返却を強制**しない**; hippocampus はハードタイムアウトまで動作し続けてよい。5s から 15s の間に到着した結果は事後レビュー用に session trace にログされるが、現在の session の ROUTER 入力には注入**されない**(GWT はすでに統合して引き継ぎ済み)。
- Hard timeout: **15 秒** — hippocampus は持っているものを何でも返して終了しなければならない。5s–15s の間に返される結果は trace のみに入る。

**トリガーされない**:

- Start Session 起動(RETROSPECTIVE Mode 0 がすでに直近コンテキストをロードしている)
- Review Mode(保留中のユーザー判断なし)
- Orchestrator が明示的に `--no-cortex` を要求した場合(degraded モード、デバッグ用)

---

## 3. エージェント定義 Frontmatter(Agent Definition Frontmatter)

実際のエージェントファイル(`pro/agents/hippocampus.md`)は以下を宣言しなければなりません:

```yaml
---
name: hippocampus
description: "Cortex hippocampal retrieval — cross-session memory activation for Pre-Router Cognitive Layer"
tools: [Read, Grep, Glob]
model: opus
---
```

**ツール制約の根拠**:

- `Read`: INDEX.md と個々のセッション markdown ファイルをロード
- `Grep`: LLM 判断の前の INDEX.md の高速 pre-filter
- `Glob`: Wave 2/3 のルックアップのために `_meta/concepts/{domain}/*.md` を列挙
- **Write / Edit なし**: read-only contract を強制する。concept ファイルへの変更は ARCHIVER Phase 2 でのみ発生する

**Model**: `opus`。検索は多様な言い回しを横断する semantic matching を含みます。Haiku は Wave 1 の relevance scoring に十分な判断力を持ちません。v1.7 では Wave 1 パス全体を Opus で実行します。

---

## 4. 入力コントラクト(Input Contract)

Hippocampus はオーケストレーターから以下を受け取ります(サブエージェントプロンプトに構造化入力として渡される):

```yaml
hippocampus_input:
  current_user_message: string           # raw text, as typed
  extracted_subject: string | null       # non-null if ROUTER already performed intent clarification
  current_project: string                # bound project scope, e.g. "passpay"
  current_theme: string                  # e.g. "zh-classical", "ja-kasumigaseki"
  session_context:
    recent_inbox_items: [string]         # top 3-5 items from _meta/inbox/
    current_strategic_lines: [string]    # line IDs from _meta/strategic-lines.md
  meta:
    invocation_id: string                # UUID for tracing
    timestamp: ISO 8601
    soft_timeout_ms: 5000
    hard_timeout_ms: 15000
```

**明示的に受け取らないもの**(orchestrator が強制する — 違反 = 情報隔離侵害):

- 他の Pre-Router Cognitive Layer 出力(concept lookup 結果、SOUL check 結果)
- 前セッションのトランスクリプト(INDEX.md 経由の要約のみ)
- SOUL.md のフルコンテンツ(プライバシー境界 — hippocampus は concept tag を見るが、identity narrative は見ない)
- `current_theme` を超えるユーザーのプラットフォーム / 環境の詳細
- 他のエージェントの思考プロセス(`pro/CLAUDE.md` の Information Isolation テーブルに従う)

この隔離が重要な理由: hippocampus は **独立したシグナル** を生成しなければならず、それを GWT が他のシグナルに対して重みづけできるようにします。もし SOUL check 出力をすでに見ていれば、補完的ながら異なる検索アングルを浮上させる能力を失います。競合には独立性が必要です。

---

## 5. 検索アルゴリズム (3-Wave Spreading Activation)

アルゴリズムは、Life OS の markdown-first 制約に適応された生物学的な **spreading activation**(Collins & Loftus, 1975)をモデルにしています。3 つの波、それぞれが検索ネットを広げますが、信頼度は減衰します。

### Wave 1 — Direct Match(直接マッチ)

1. **Read** `_meta/sessions/INDEX.md`(エディタ生成の 1 セッション 1 行インデックス;形式は `references/session-index-spec.md` を参照)。
2. **Grep pre-filter**: `extracted_subject` が利用可能な場合、大文字小文字を区別しない regex パスを INDEX.md 全体にかけて、1000+ エントリを <50 候補に削減。不可能な場合、完全な INDEX で LLM ステップへスキップ。
3. **LLM judgment**(ユーザー判断 #3 — embedding なし、vector DB なし): pre-filter されたインデックス行を以下のプロンプトで Opus に供給:
   > "Current subject: `{subject}`. Below are past session summaries. Return the top 3-5 whose subject is semantically related to the current one. Return JSON only."
4. 各候補の **Read full content** を `_meta/sessions/{session_id}.md` から。
5. **Score**: `score_wave1 = 0.6 * subject_similarity + 0.4 * keyword_overlap`。両サブスコアは Opus が 0-1 で判定。
6. 上位 3-5 セッションを保持。

**Wave 1 の出力**: `[{session_id, score, matched_concepts}]` — 下流 wave のためのシードセット。

### Wave 2 — Strong Neighbors(強い近傍)

Wave 1 セッションから、**concept graph** に沿って展開し、表面キーワードを共有しないために Wave 1 が見逃した関連セッションを見つけます。

1. 各 Wave 1 セッションについて、その YAML frontmatter から `concepts_activated` と `concepts_discovered` リストを抽出。
2. 各 concept ID について、**Read** `_meta/concepts/{domain}/{concept}.md`。
3. その concept の `outgoing_edges` リストから、**weight ≥ 3 のエッジをたどる**(strong synapse — weight セマンティクスは `references/concept-spec.md` を参照)。
4. 各 neighbor concept について、その `provenance.source_sessions` フィールドをルックアップ — これにより neighbor concept が activate されたセッションが得られる。
5. Wave 1 セットに対して **deduplicate**、composite スコアでランク付けした **上位 2-3 の新セッションを保持**:
   ```
   score_wave2 = 0.5 * edge_weight_normalized + 0.3 * concept_overlap + 0.2 * recency_decay
   ```
   ここで `recency_decay = exp(-days_since_session / 90)`。

**Bounded by design**: Wave 2 は最大 3 セッションを追加します。これは concept-graph fan-out が検索予算を爆発させるのを防ぎます。

### Wave 3 — Weak Neighbors(弱い近傍)

グラフをもう一度、低 weight しきい値で拡張します。これは Wave 1(surface)でも Wave 2(strong edge)でも浮上しない「予期しないが有用」な接続をキャッチします。

1. Wave 2 セッションの concept から、**weight ≥ 1**(アクティブなエッジ)のエッジをたどる。
2. Wave 2 と同じ provenance ルックアップを適用。
3. Deduplicate、上位 1-2 を保持。
4. Score:
   ```
   score_wave3 = 0.3 * edge_weight_normalized + 0.4 * concept_overlap + 0.3 * recency_decay
   ```
   raw エッジ強度への重みを弱め、semantic overlap により重みを置く。

**Explicit cap**: Wave 3 は最大 2 セッションを寄与し、検索セット全体は **合計 5-7 セッションを超えてはなりません**。それを超えると GWT arbitration の品質が劣化します(重みづけするシグナルが多すぎる)。

### 最終出力(Final Output)

すべての検索されたセッションを wave 内スコアでランク付けしますが、**各セッションがどの wave から来たかを annotate** します — GWT は salience を校正するためにその provenance を必要とします。

---

## 6. 出力コントラクト(Output Contract)

Hippocampus はオーケストレーターへの最終メッセージとして、構造化された YAML ブロックを返します:

```yaml
hippocampus_output:
  current_subject: string
  retrieved_sessions:
    - session_id: string
      date: ISO 8601
      relevance_score: float              # 0-1, wave-calibrated
      reason: string                      # one sentence, why this matched
      wave: 1 | 2 | 3
      summary: string                     # 1-2 sentences, the session's core substance
      key_decisions: [string]             # 1-3 decision titles from the session
      applicable_signals:
        - signal_type: "decision_analogy" | "value_conflict" | "pattern_match"
          detail: string
  activated_concepts:
    - concept_id: string
      activation_strength: float          # 0-1, how strongly this retrieval activated the concept
  meta:
    sessions_scanned: integer             # total INDEX lines considered
    llm_tokens_used: integer              # estimated
    execution_time_ms: integer
    waves_completed: [1, 2, 3]            # partial if hard-timeout hit
    degraded: boolean                     # true if any wave skipped
    degradation_reason: string | null
```

**Signal type セマンティクス**:

- `decision_analogy` — 過去セッションが構造的に類似した決定に直面した(「以前 X 対 Y を検討した」)
- `value_conflict` — 過去セッションがここで関連する SOUL レベルの緊張を浮上させた
- `pattern_match` — 過去セッションが、ユーザーが再び気づくべき行動パターンを示した

---

## 7. 出力注入(Output Injection)

Hippocampus 出力は ROUTER には **直接** 行きません。**GWT arbitrator** に流れ、concept lookup 出力と SOUL check 出力と統合されて単一の「annotated input」になります。

最終的な注釈付き入力は、ユーザーメッセージの一部として明確に区切られて ROUTER に届きます:

```markdown
[COGNITIVE CONTEXT — reference only, not user input]

Related past decisions (hippocampus):
- 2026-04-19 | passpay | 技术白皮书 v0.6 (score 8.2) — similar refinement pattern
- 2026-03-28 | passpay | 合规架构评估 (score 6.5) — GOVERNANCE scored low, may repeat
- 2026-04-15 | passpay | 商业白皮书 v1.0 (score 7.8) — same project cluster, recent

[END COGNITIVE CONTEXT]

User's actual message: {original_message}
```

**配置の根拠**(重要 — 相談なしに変更しないこと):

- 認知コンテキストは **ユーザーメッセージ** に入り、システムプロンプトには入りません。システムプロンプトはキャッシュされます。volatile な per-session 検索は毎ターン prompt cache を破壊します。
- ROUTER は認知コンテキストを無視することを選択できます(例: ユーザーが明示的に「履歴を無視し、最初から再検討して」と言う)。アノテーションは **advisory であり、authoritative ではありません**。
- `[COGNITIVE CONTEXT]` 区切り子はリテラルです — ROUTER はこれをパースして advisory コンテンツを実際のユーザー入力から分離します。

---

## 8. パフォーマンス予算(Performance Budget)

| Step | Target | Notes |
|------|--------|-------|
| Read `INDEX.md` | <100ms | 2000 セッションでファイルサイズ <1MB |
| Grep pre-filter | <50ms | INDEX.md 上の Ripgrep |
| LLM judgment on filtered index | 2-3s | Opus 上で約 5000 tokens |
| Read 3-5 session files | <300ms | 並列 read |
| Wave 2 concept lookup | 1-2s | Opus がエッジ関連性を判定 |
| Wave 3 extension | 1s | より狭いスコープ |
| **Total target** | **<7 秒** | 15s ハードタイムアウトを十分下回る |

**タイムアウト意味合いに関する注記**: <7s の合計は**通常ケースのターゲット** — つまりパイプラインが典型的な起動で達成するよう設計された予算です。§2 の 5s ソフト / 15s ハードの境界は**テール挙動**を記述しています: ソフト境界は GWT が待つのをやめる時点(hippocampus が動作を止める時点ではない)で、ハード境界は hippocampus が何があっても終了する絶対上限です。5s を超えた実行も完了して session trace にログされますが、その出力は現在の ROUTER サイクルに再投入されません。

**スケーラビリティノート**: 2000+ セッションで INDEX.md は 2MB に向けて成長します。月別ページング(`INDEX-2026-04.md`)を検討し、その領域ではデフォルトで直近 6 ヶ月のみを読みます。Phase 1 はページングを実装しません。

**トークン予算**:

- LLM judgment コール: 約 5000 tokens 入力 + 約 500 出力
- Wave 2 エッジ関連性: 約 1500 tokens 入力 + 約 200 出力
- 起動あたり合計: 8000 tokens 未満

起動あたりコスト(Opus pricing にて): session-context サイズに応じて約 $0.05-0.10。これはブレインストーミング §10 の generic-version コストターゲットと一致します。

---

## 9. 失敗モード(Failure Modes)

Hippocampus は gracefully に degrade しなければなりません — 失敗した検索が意思決定ワークフローをブロックすることは決してあってはなりません。

| Failure | Behavior |
|---------|----------|
| `_meta/sessions/INDEX.md` が存在しない | 利用可能なら Bash 経由で `tools/reindex.py` を実行;それ以外なら `degraded: true, degradation_reason: "INDEX_MISSING"` で空の出力を返す |
| INDEX.md は存在するが空(新規 second-brain) | 空の `retrieved_sessions` を返し、「first session — no cross-session memory yet」を記す |
| LLM judgment コールが失敗(API エラー、レート制限) | INDEX.md 上の純粋なキーワードマッチにフォールバック(semantic scoring なし)、`degraded: true` を設定 |
| Wave 2 ターゲット用の concept ファイルが missing | その特定のブランチをスキップ、残りのブランチで Wave 2 を継続 |
| concept グラフ全体が missing | Wave 2-3 をスキップ、Wave 1 結果を `waves_completed: [1]` で返す |
| ハードタイムアウト(>15s) | 部分結果(完了した wave 何でも)を返す、インシデントを `_meta/eval-history/hippocampus-{date}.md` にログ |
| セッションファイル上の Read エラー | そのセッションをスキップ、`degradation_reason` に記す |

**すべての失敗は `_meta/eval-history/` にログされ**、AUDITOR がセッション終了パトロール中に読みます。同じ種類の失敗の繰り返しは「モジュール品質劣化」フラグをトリガーします — ブレインストーミング §6 の Escalate rate limit と同じメカニズムです。

---

## 10. キャッシング (v1.7 のスコープ外)

すべての起動で INDEX.md を再スキャンし、concept ファイルを再読み込みします。2000 セッションでもこれは 2MB 未満の I/O と 7 秒未満の合計レイテンシなので、**v1.7 ではキャッシングなし**。

キャッシングは v1.7 のスコープ外です。INDEX.md が 5MB を超えるか、hippocampus の p95 レイテンシが v1.7 運用中に 10s を超えた場合、`session-index-spec.md` §8 のスケールトリガーが発火します(まず INDEX を月別にシャーディングし、その後別の仕様改訂としてキャッシングを検討)。

---

## 11. 品質メトリクス(Quality Metrics)

Hippocampus は 3 次元に沿って評価されます。各次元は session-end で AUDITOR が計算し、`_meta/eval-history/cognitive-annotation-{date}.md` に追記されます。

### 11.1 `retrieved_session_count`

何か見つけたか? second-brain が 30 セッションを超えてからの健全な baseline は、起動あたり 3-5 検索です。十分な履歴がありながら persistent にゼロ検索 = バグシグナル。

### 11.2 `relevance_score_distribution`

top-ranked 結果は実際に関連性があるか? AUDITOR がヒューリスティクスを使って self-evaluate: 「ROUTER は推論でこのセッションを引用したか?」

Healthy: top-1 relevance score の中央値 ≥ 0.7。中央値が 2 週間 0.5 を下回ると、Wave 1 LLM プロンプトの retuning が必要です。

### 11.3 `user_signals_used`

ROUTER / 下流エージェントが、検索されたコンテンツを **実際に参照した** か? AUDITOR は Summary Report とドメイン出力を検索し、検索されたセッション ID の言及を確認します。検索されたセッションの 20% 未満しか参照されていなければ、hippocampus は価値を提供せずコストを払っていることになります — AUDITOR がパターンを eval-history でレビュー用に浮上させます。

### Composite score

これらは AUDITOR の `cognitive_annotation_quality` メトリック(0-1)に供給され、すべての eval-history エントリに書き込まれます。このメトリックで persistent に低いスコアは、AUDITOR の patrol inspection で浮上し、通常の仕様改訂プロセスを通じてモジュールレベルのレビューをトリガーします。

---

## 12. アンチパターン(Anti-patterns)

明示的な禁止事項 — 違反はプロセスエラーであり、AUDITOR がフラグを立てます。

- **すべてのセッションを検索しない。** 網羅的検索は目的を打ち破ります(そしてトークン予算を吹き飛ばします)。Wave の上限は理由があって存在します。
- **embedding や vector database を使わない。** ユーザー判断 #3: markdown-first、LLM 判断のみ。ベクトルストアの追加はアーキテクチャを変えます — 別の承認を要します。
- **セッションファイルや concept ファイルを変更しない。** Hippocampus は read-only です。すべての書き込みは ARCHIVER Phase 2 で発生します(`pro/agents/archiver.md` を参照)。
- **検索されたコンテンツを SYSTEM PROMPT に注入しない。** volatile すぎて prompt cache を破壊し、長いセッションでシステムプロンプトを膨張させます。検索されたコンテンツは常に `[COGNITIVE CONTEXT]` で区切られたユーザーメッセージに入ります。
- **隔離をスキップしない。** 他の Pre-Router Cognitive Layer 出力を読まないこと。入力にそれを見たら、コントラクト違反として扱い、エラーを返します。
- **検索コンテンツにない主張を合成しない。** Hippocampus は検索エージェントであり、reasoner ではありません。各検索セッションの `reason` フィールドは、そのセッションの markdown の内容をパラフレーズしなければならず、それを超えて推論してはなりません。
- **合計 7 セッションを超えて検索しない。** それを超えると GWT arbitration 品質が劣化します。
- **LLM コールを silent にリトライしない。** 一時的なエラーでは 1 回のリトライが許容されます;さらなる劣化は `degraded: true` を設定しログしなければなりません。
- **hippocampus の失敗でワークフローをブロックしない。** ソフトタイムアウト到達 = 部分結果;ハードタイムアウト到達 = 空の結果。決して stall しないこと。
- **raw セッションコンテンツをリークしない。** `summary` フィールドは最大 1-2 文;セッション全体のトランスクリプトを貼り付けないこと。プライバシー境界。

---

## 13. 関連仕様(Related Specs)

- **`references/cortex-spec.md`** — 全体 Cortex アーキテクチャ、hippocampus がどうフィットするか
- **`references/concept-spec.md`** — concept markdown スキーマ、エッジ weight、permanence tier
- **`references/session-index-spec.md`** — `_meta/sessions/INDEX.md` 形式、1 行の規約
- **`references/gwt-spec.md`** — hippocampus 出力を消費する GWT arbitrator
- **`devdocs/architecture/cortex-integration.md`** — Step 0.5 が 11 ステップワークフローにどう plug するか
- **`devdocs/brainstorm/2026-04-19-cortex-architecture.md`** — オリジナルの設計議論、ユーザー判断、トレードオフ

---

## 14. バージョン履歴(Version History)

| Version | Date | Change |
|---------|------|--------|
| v1.7 | 2026-04-20 | Cortex Phase 1 の初回仕様。Wave 1-3 検索、read-only contract、7s 予算。 |

---

**ドキュメントステータス**: v1.7 Cortex Phase 1 のアクティブ仕様。変更には明示的なバージョン bump と、プロジェクト HARD RULE に従った `pro/agents/hippocampus.md`、`references/cortex-spec.md`、3 言語 CHANGELOG エントリの更新が必要です。

---

> ℹ️ **2026-04-22 更新**:EN R1 で修正された §2 + §8 ソフト/ハードタイムアウトの意味合わせを同期

本文は [英語版](../../../references/hippocampus-spec.md) 2026-04-21 スナップショットの翻訳です。英語版が権威源で、曖昧な場合は英語版が優先します。
