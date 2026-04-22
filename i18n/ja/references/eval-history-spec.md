---
translated_from: references/eval-history-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# Eval History 仕様書(Eval History Specification)(v1.7)

Eval history は Life OS の構造化された自己評価フィードバックループです。これはモデルを一切学習させない、spec レイヤーにおける Hermes の RL 訓練シグナル相当物です。AUDITOR はセッション毎に一つの構造化評価を書き出します。RETROSPECTIVE は Start Session 時に履歴をスキャンし、システミックな品質ドリフトを浮かび上がらせます。

---

## 1. 目的(Purpose)

Eval history は、Life OS が時間経過を通じて自分自身を検査するメカニズムです。

個々の AUDITOR レポートはすでに各セッションのエージェントパフォーマンスを採点していますが、セッションが終了すると蒸発してしまいます。それらは *今回の* 審議には有用ですが、*過去 10 回の審議* についてはシステムに何も語ってくれません。その欠落したループを閉じるのが eval history です。

- **AUDITOR** は writer です。full deliberation または express workflow が終わるたびに、その判定を構造化 YAML + markdown として `_meta/eval-history/` にシリアライズします。
- **RETROSPECTIVE Mode 0** が一次 reader です。各 Start Session において直近 10 件の eval ファイルを読み、システミックパターン — 繰り返される違反、低下するスコア、hallucinated な引用、スキップされたフェーズ — を検出します。
- **Tools**(stats、reconcile)は月次サマリーや orphan 検出のために履歴を読みます。

この発想は Hermes の RL 訓練ループから来ています。Hermes はエージェントの trajectory を訓練シグナルに圧縮し、モデルを fine-tune します。Life OS はホスト(Claude、Gemini、Codex)を fine-tune することはできませんが、自分の *ルール* を fine-tune することはできます — 品質シグナルをディスクに書き出し、RETROSPECTIVE に次のセッションで浮上させてもらうことで。シグナルは勾配降下ではなく、人間のアテンションを介してシステム挙動を変化させます。

これは同時に、`devdocs/research/2026-04-19-hermes-analysis.md` の Hermes Lesson 5 への直接の答えでもあります: self-evaluation は単に one-off レポートとして蓄積されるのではなく、システムにフィードバックされなければなりません。

---

## 2. ファイル配置(File Location)

```
_meta/eval-history/
└── {YYYY-MM-DD}-{project}.md
```

AUDITOR を通ったセッション一件につきファイル一つ。

- `{YYYY-MM-DD}` — セッション開始日(ISO)。
- `{project}` — バインドされたプロジェクトのスラグ(kebab-case、小文字)。
- 同日同一プロジェクトの複数セッションは `-{HHMM}` を付加して曖昧性を排除します: `2026-04-20-career-change-1430.md`。

Eval ファイルは他の `_meta/` アーティファクト(STATUS.md、STRATEGIC-MAP.md、lint-state.md)と同居し、同じ規約に従います: エージェントがコンパイルし、人間が読める、事後の手編集は行わない。

---

## 3. YAML Frontmatter スキーマ(YAML Frontmatter Schema)

すべての eval ファイルは YAML frontmatter ブロックから始まります。未知のフィールドは reader から無視されます。必須フィールドが欠落している場合は `tools/reconcile.py` がフラグを立てます。

```yaml
---
eval_id: {YYYY-MM-DD-HHMM}-{project}
session_id: string                 # references _meta/sessions/{session_id}.md
evaluator: auditor | auditor-patrol
evaluation_mode: decision-review | patrol-inspection
date: ISO 8601 timestamp
scores:
  information_isolation: integer (0-10)
  veto_substantiveness: integer (0-10)
  score_honesty: integer (0-10)
  action_specificity: integer (0-10)
  process_compliance: integer (0-10)
  adjourn_completeness: integer (0-10)
  soul_reference_quality: integer (0-10)
  wiki_extraction_quality: integer (0-10)
  cognitive_annotation_quality: integer (0-10)    # v1.7: hippocampus output quality
  citation_groundedness: integer (0-10)           # v1.7: narrator citation validity
violations:
  - type: adjourn_phase_skip | notion_sync_skip | citation_missing | ...
    agent: ROUTER | ARCHIVER | ...
    severity: critical | high | medium | low
    detail: string
agent_quality_notes:
  PLANNER: string
  REVIEWER: string
  DISPATCHER: string
  FINANCE: string
  EXECUTION: string
  GROWTH: string
  INFRA: string
  PEOPLE: string
  GOVERNANCE: string
  AUDITOR: string
  ADVISOR: string
  ARCHIVER: string
---
```

備考:

- `scores` は 0〜10 の整数です。半点は許容しません — AUDITOR に決断を迫ります。
- `violations` はリストです。空リストは「観測された違反なし」を意味します。
- `agent_quality_notes` には実際にセッションに参加したエージェントのみを含めます。express path ではほとんどのエントリが省略されます。

---

## 4. 本文フォーマット(Body Format)

frontmatter の後に markdown 本文が続きます。本文は人間の reader と RETROSPECTIVE の Mode 0 パターンスキャンの両方に消費されます。

```markdown
## Summary
{一段落のハイレベル評価 — 何が起きたか、ワークフローが保たれたか、ヘッドラインスコア}

## Strengths
- {うまくいったこと、具体的な根拠に基づく}

## Weaknesses
- {改善が必要なこと、具体的な根拠に基づく}

## Systemic Pattern Observations
{今回のセッションが過去のセッションと一貫するパターンを示している場合は記載する — 例「3 セッション連続で ARCHIVER Phase 2 が wiki 候補をゼロ件しか産出しなかった」}

## Recommendations
- {次セッションへの具体的な改善案、named agent + named mechanism}
```

本文ルール:

- Strengths と Weaknesses は具体的な根拠(引用されたエージェント出力、スコアの矛盾、スキップされたフェーズ)を参照しなければなりません。「全エージェントが good performance を示した」のような一般的な褒め言葉は AUDITOR の anti-pattern であり、`pro/agents/auditor.md` により禁止されています。
- Systemic Pattern Observations は single-session の異常については optional ですが、直近 10 件の eval を横断して繰り返しパターンが検出された場合は必須です(RETROSPECTIVE が cross-session のヒントを提供し、AUDITOR がそれをここに再述します)。
- Recommendations は特定のエージェント(PLANNER / REVIEWER / ARCHIVER / ...)と特定のメカニズム(score calibration / checklist coverage / wiki criteria)をターゲットとしなければならず、漠然とした激励であってはなりません。

---

## 5. スコア次元(Score Dimensions)

10 次元、各 0〜10、3 つの calibrated アンカー点を持ちます。すべての AUDITOR 評価は 10 次元すべてを埋めなければなりません — 欠落した次元は `tools/reconcile.py` がフラグを立てます。

### 5.1 information_isolation(0〜10)

upstream コンテキスト漏洩に関する HARD RULES が全エージェントで保たれたか。

- **10**: PLANNER は ROUTER の推論を知らない。REVIEWER は planning ドキュメントのみを受け取る。ドメイン同士が他ドメインのスコアや結論を参照しない。汚染なし。
- **5**: 軽微な漏洩 — 例として ROUTER がどのドメインが発火するかをほのめかす、あるいはドメインが「他のレビューで指摘されたように」と言及する。
- **0**: 明確なクロス汚染。REVIEWER が PLANNER の生の思考を見る、あるいは 2 つのドメインが互いを名前で参照する。

### 5.2 veto_substantiveness(0〜10)

REVIEWER の承認/拒否権発動が 8 項目チェックリストと具体的な根拠に基づいていたか。

- **10**: 全チェックリスト項目が具体的な観察で扱われる。Veto 判定は失敗した項目と必要な訂正方向を引用する。
- **5**: チェックリストは適用されているが根拠が浅い(「ロジックは健全」とだけ書かれ、理由がない)。
- **0**: 形式的な承認。チェックリストの通過なし。Veto 理由が曖昧または欠落。

### 5.3 score_honesty(0〜10)

ドメインのスコアが自身の分析テキストと対応しているか。

- **10**: すべてのドメインの数値スコアがそのナラティブの深刻度と一致している。Face-saving なし。分析が実質的に異なる場合、ドメイン間の標準偏差が 1.0 を超える。
- **5**: 1〜2 件怪しいスコア — 例として重大な懸念を述べた段落に 7 が付いている。
- **0**: すべてに無差別な 7 または 8、もしくは自身のリスク評価と直接矛盾するスコア。

### 5.4 action_specificity(0〜10)

アクションアイテムが具体的で、実行可能で、期限付きで、オーナー明示かどうか。

- **10**: すべてのアクションアイテムにドメインオーナー、期限、具体的な first step がある。
- **5**: アクションは具体的だが期限かオーナーが欠けている。
- **0**: アクションが願望(「これについて考える」「影響を検討する」)。

### 5.5 process_compliance(0〜10)

ワークフローの state machine が end-to-end で遵守されたか。

- **10**: 必須ステップすべてが必須順序で実行された。AUDITOR スキップなし、ADVISOR スキップなし、Notion 同期スキップなし。Adjourn state machine が保たれた。
- **5**: 1 ステップスキップされたがセッション中に検知され回復された。
- **0**: 複数フェーズスキップ、または違法な遷移(Summary Report → ARCHIVER、AUDITOR + ADVISOR を経ずに)。

### 5.6 adjourn_completeness(0〜10)

ARCHIVER subagent が 4 フェーズ(Archive、Knowledge Extraction、DREAM、Sync)すべてを実行し、きれいな Completion Checklist を産出したか。

- **10**: 4 フェーズすべて実行。Checklist の値が本物(「TBD」ではない)。Notion 同期がオーケストレータに返り、実行された。
- **5**: 4 フェーズ中 3 フェーズが実行、あるいは Phase 3 DREAM がジャーナルエントリを産出しなかった。
- **0**: Split flow。Multi-message archiver。Checklist の placeholder 値。

### 5.7 soul_reference_quality(0〜10)

REVIEWER が審議中の意思決定に関連する SOUL 次元を参照したか。

- **10**: 意思決定に関連するすべての SOUL 次元(active + dormant + conflict zone)が confidence と方向性とともに明示的に引用された。
- **5**: SOUL は参照されているが選択的 — 例として high-confidence 次元のみ引用し、重要な dormant を無視している。
- **0**: SOUL がまったく参照されていない、あるいは参照されたがレビューに統合されていない。

### 5.8 wiki_extraction_quality(0〜10)

ARCHIVER Phase 2 が 6 基準 + privacy filter をすべてパスする wiki 候補を抽出したか、かつ抽出がセッション横断で再利用可能か。

- **10**: 候補が具体的で、再利用可能で、privacy clean で、正しいドメインに配置される。
- **5**: 一部の候補はパスするが既存エントリと重複している、あるいは再利用するには narrow すぎる。
- **0**: 抽出すべきときに抽出が行われなかった、あるいは抽出が privacy filter を通らなかったにもかかわらず出荷された。

### 5.9 cognitive_annotation_quality(0〜10) — v1.7

hippocampus-tier の retrieval が適切な wiki エントリを浮上させ、セッションにおける実際の有用性に沿った relevance スコアで注釈したか。

- **10**: 取得されたエントリが使用された。Relevance スコアが意思決定への実際の影響を追跡している。
- **5**: 取得されたエントリは使用されたが relevance scoring が粗い。
- **0**: 取得されたエントリが無視された、あるいは relevance が hallucinated。

### 5.10 citation_groundedness(0〜10) — v1.7

narrator-tier 引用(過去セッション、wiki エントリ、SOUL 次元への参照)が実際に存在し、かつ主張通りのアーティファクトを指しているか。

- **10**: すべての引用が主張内容通りの実在アーティファクトに解決される。
- **5**: 大半の引用は解決されるが、少数が source を超えてパラフレーズされている。
- **0**: 引用が捏造されている、あるいは存在しないセッション/エントリを指している。

---

## 6. トリガー条件(Trigger Conditions)

### 6.1 AUDITOR が eval-history エントリを書くとき

- full deliberation workflow(`pro/CLAUDE.md` の Step 8)終了後すべて。
- 評価に足る深さの Brief Report を産出した express 分析 workflow 終了後すべて。
- RETROSPECTIVE Mode 0(lint-state > 4h)によりトリガーされた Patrol Inspection 後。Patrol は `evaluation_mode: patrol-inspection` で書きます。

### 6.2 AUDITOR がエントリを書かないとき

- ROUTER がリクエストを直接処理した場合(評価すべき subagent 作業なし)。
- STRATEGIST セッション(評価ドメインが異なる — thinker dialogue quality であって deliberation quality ではない)。
- First-run / empty-second-brain セッションで意思決定が発生しなかった場合。
- PLANNER が出力を産出する前に abort したセッション。

### 6.3 書き込みタイミング(Write timing)

AUDITOR は Step 8 の終盤、ADVISOR が走る前に eval ファイルを書きます。書き込みは AUDITOR の観点から同期的ですが、ROUTER をブロックしません — 書き込みが失敗した場合、AUDITOR は失敗を報告しセッションは続行されます。

---

## 7. システミック問題検出(Systemic Issue Detection)

RETROSPECTIVE Mode 0 は Start Session 時に直近 10 件の eval ファイルを読み、以下の検出ルールを適用します。検出されたパターンは morning briefing にシステミック問題警告ブロックとして表示されます。

### 7.1 adjourn_completeness トレンド

3 セッション以上連続で `adjourn_completeness < 6` → 警告:「archiver subagent が正常に launch していない可能性」。

これは ROUTER が ARCHIVER フェーズ間に介入し split flow を作り出す v1.6.x の再発バグを捕捉します。

### 7.2 wiki_extraction_quality の低下

`wiki_extraction_quality` が 5 セッション以上下降トレンドを示す → 警告:「ARCHIVER Phase 2 が silently に抽出をスキップしている可能性」。

### 7.3 citation_groundedness 失敗

直近 10 セッションで narrator 引用の解決失敗率が 20% 超 → 警告:「narrator layer がシグナルを hallucinate している」。

### 7.4 cognitive_annotation_quality 床

直近 5 セッションで `cognitive_annotation_quality < 5` → 警告:「hippocampus retrieval のチューニングが必要」。

### 7.5 process_compliance 再発

同じ `violations[].type` が直近 30 日以内に 3 回以上出現 → compliance log のアップグレードをトリガー: 違反は eval history から `user-patterns.md` に卒業し、tracked な behavioural pattern となります。次セッションの ADVISOR がそれを直接観測として浮上させます。

### 7.6 Briefing フォーマット

警告は Start Session briefing において DREAM Auto-Triggers ブロックの直後、Strategic Overview の前に表示されます。フォーマット(active theme 言語にローカライズ):

```
⚠️ 系统性问题检测：
- 退朝完整度连续 3 次 ≤6 → 建议检查 archiver subagent 启动
- Wiki 萃取质量从 4/15 起下降 → 建议本次重点关注
```

システミック問題が検出されなかった場合、ブロック自体が完全に省略されます(placeholder なし)。

---

## 8. アーカイブポリシー(Archive Policy)

- Eval ファイルは無期限に保持されます。各ファイルは小さい(〜5 KB)ので、1000 セッションでも合計 〜5 MB です。
- 6 ヶ月より古いファイルは `_meta/eval-history/_digest/{YYYY-Q}.md` に四半期 digest としてまとめられ、元のファイルは `_meta/eval-history/_archive/` に移されます。Digest はヘッドラインスコアとシステミックパターンを保持します。個々のセッションは引き続きアクセス可能です。
- Digest は `tools/stats.py` を `--compress-old` で実行したときに書かれます。自動では決して書かれません。

---

## 9. 読み取りフロー(Read Flow)

複数の consumer が異なる目的で eval history を読みます。

| Consumer | 頻度 | スコープ | 目的 |
|----------|-----------|-------|---------|
| retrospective Mode 0 | 毎 Start Session | 直近 10 ファイル | morning briefing 用システミックパターン検出 |
| auditor | 発動時 | 直近 5〜10 ファイル、同一プロジェクト | 現在セッション評価前の履歴 calibration 参照 |
| tools/stats.py | on demand | 全ファイルまたは日付範囲 | 月次 / 四半期品質レポート |
| tools/reconcile.py | on demand | 全ファイル | Orphan 検出 — session のない evals、evals のない sessions |

Reader は欠落フィールドを許容しなければなりません(異なる Life OS バージョンは異なるスキーマを書いた可能性があります)。YAML スキーマは forward-compatible です: 未知のフィールドは無視され、missing-but-expected フィールドは hard failure ではなく reconcile 警告を発火させます。

---

## 10. 書き込みフロー(Write Flow)

- トリガー: AUDITOR が full deliberation workflow の Step 8 で Decision Review を完了(または express path の Brief-Report 相当、または Patrol Inspection)。
- パス: `_meta/eval-history/{YYYY-MM-DD}-{project}.md`。
- コンフリクト解消: ファイルが既に存在する場合(同日同一プロジェクトの 2 回目以降のセッション)、AUDITOR はファイル名に `-{HHMM}` を付加します: `2026-04-20-career-change-1430.md`。
- 失敗処理: 書き込みが失敗した場合(ディスクフル、パーミッションエラー、パス欠落)、AUDITOR は通常の Decision Review 出力で失敗を報告します。セッションは続行されます。失敗自体は次セッションの eval に process compliance 違反として記録されます。
- 不変性(Immutability): eval ファイルは作成後に編集されることはありません。評価が誤っていた場合、次セッションで reversal note 付きの新ファイルが書かれます。先行ファイルは歴史的記録として残ります。

---

## 11. マイグレーション(Migration)

v1.7 以前に eval history は存在しませんでした。

- `tools/migrate.py` は `_meta/journal/` から過去の AUDITOR レポートを **backfill しません**。それらのレポートは unstructured prose であってスキーマに合わず、backfill を試みると low-signal noise を生じ、システミック検出を汚染します。
- Eval history は v1.7 初日にフレッシュスタートします。v1.7 の最初の Start Session はシステミック警告を表示しません(スキャンすべき履歴なし)。3 セッション以上連続で記録されると警告が出始めます。
- v1.7 以前のセッションの履歴分析を求めるユーザーは既存の `_meta/journal/` レポートを直接使用してください。これらは migrate されません。

---

## 12. アンチパターン(Anti-patterns)

以下は禁止です。RETROSPECTIVE と `tools/reconcile.py` は検出時にフラグを立てます。

- eval ファイル内に Summary Report 全文を埋め込む **な**。代わりに `session_id` を参照してください。eval ファイルは quality metadata であって session 内容の duplicate ではありません。
- 「軽微な」セッションの eval 書き込みをスキップする **な**。パターンは volume に渡って現れます — 簡単なものをスキップすると、困難なもののシグナルを破壊します。
- eval ファイルを作成後に編集する **な**。評価が誤っていた場合、次セッションで reversal を記した新ファイルを書いてください。先行ファイルは不変です。
- AUDITOR の eval 書き込みが user-facing workflow をブロックするのを許容する **な**。書き込みは AUDITOR の観点から同期的ですが、write failure が ADVISOR、ARCHIVER、session close を stall させてはなりません。
- eval ファイルを Notion に同期する **な**(ユーザー決定 #12)。Eval history はローカルな introspection artifact です。Notion に push するとモバイルビューが noisy になり、モバイル側の consumer が存在しません。
- AUDITOR 自身の評価で face-saving を許容する **な**。`score_honesty: 3` が妥当なら 3 と書いてください — AUDITOR が自身を一律 7 で評価するのは、まさに AUDITOR が他者で検出するために造られた anti-pattern です。
- 観測できなかった次元に対してスコアを捏造する **な**。関連する SOUL 参照がなかった場合は `soul_reference_quality` をセッションのデフォルト値(通常は 10 — 「該当なし、従って違反なし」)とマークし、`agent_quality_notes` に理由を注記してください。

---

## 13. 関連仕様(Related Specs)

- `references/cortex-spec.md` — 全体の Cortex アーキテクチャ。eval-history は v1.7 の 5 つの core artifact の一つ
- `references/session-index-spec.md` — `session_id` フィールドはすべての eval エントリをその session summary にリンクする
- `references/hippocampus-spec.md` — `cognitive_annotation_quality` (§5.9) で AUDITOR が評価するシグナルを産出する
- `references/gwt-spec.md` — AUDITOR が `cognitive_annotation_quality` で評価する arbitration quality シグナルを産出する
- `references/narrator-spec.md` — `citation_groundedness` (§5.10) で AUDITOR が評価する citation quality シグナルを産出する
- `references/hooks-spec.md` — 違反ログは `process_compliance` 次元(§5.5)および §7.5 再発検出に feed する
- `references/tools-spec.md` — `stats.py` と `reconcile.py` が月次レポートと orphan 検出のために eval-history を消費する
- `references/soul-spec.md` — `soul_reference_quality` (§5.7) は REVIEWER が SOUL 次元をどう引用したかを採点する
- `references/wiki-spec.md` — `wiki_extraction_quality` (§5.8) は ARCHIVER Phase 2 の wiki 候補を採点する
- `pro/agents/auditor.md` — eval-history エントリの唯一の writer(Step 8 終盤)
- `pro/agents/retrospective.md` — システミックパターン検出のための Mode 0 reader(直近 10 ファイル)
- `devdocs/research/2026-04-19-hermes-analysis.md` — この仕様を動機づけた Hermes Lesson 5(self-evaluation must feed back)
