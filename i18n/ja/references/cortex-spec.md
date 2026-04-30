---
translated_from: references/cortex-spec.md
translator_note: 自動翻訳 2026-04-21、人間校正待ち
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Cortex 仕様書(Cortex Specification)

Cortex は Life OS の認知レイヤーです — pre-router のメカニズムとして、クロスセッションの記憶、概念グラフ、マルチソースのシグナルを、あらゆる意思決定ワークフローにロードします。これは Layer 2 のアーキテクチャアップグレードであり、新しいレイヤーではありません。v1.7 で導入されました。

## 位置付け(Positioning)

Life OS のネーミング体系において、Cortex は他の personal-archive モジュールと並ぶ位置にあります:

| モジュール | 記録内容 | スコープ |
|--------|----------------|-------|
| SOUL | あなたが誰であるか(アイデンティティ、価値観) | Personality |
| Wiki | あなたが世界について知っていること | Knowledge |
| DREAM | オフラインで発見されたもの | Sleep-phase processing |
| STRATEGIC-MAP | あなたがどう位置付けられているか | Cross-project strategy |
| **Cortex** | **あなたがどう考えるか** | **Pre-router cognition** |

Cortex は既存のどのモジュールも置き換えません。ROUTER に注釈付き入力 — ユーザーメッセージに加えて memory、concept、SOUL の各シグナル — を提供することで、下流のエージェントが真空中ではなく文脈の中で動作するようにします。

---

## 原則(Principles)

1. **Layer-2 アップグレードであり、新レイヤーではない** — Life OS はすでに 3 つのレイヤー(Engine + Theme + Locale)を持っています。Cortex は Layer 2 の内部に位置する capability 拡張です。
2. **ROUTER は注釈付き入力を受け取り、raw message は受け取らない** — Cortex が認知アノテーションを生成します。ROUTER の triage ルールは変更されません。
3. **常に Markdown ファースト** — すべての Cortex アーティファクトは `.md + YAML frontmatter` です。SQLite なし、Python ランタイムなし、cron なし、外部秘密情報なし。
4. **Grounded generation** — Cortex 出力におけるすべての実質的な主張は signal_id を引用しなければなりません。confabulation(作話)は許容されません。
5. **Graceful degradation** — いずれかの Cortex サブエージェントが失敗した場合、システムは v1.6.2a の動作(ROUTER への raw message)にフォールバックします。
6. **Universal edition のみ** — プレミアム版や家庭用版のバリエーションは存在しません。すべてのユーザーに対して単一の動作となります。

---

## Cortex が解決する問題(Problem Cortex Solves)

v1.7 以前、Life OS が長期記憶に触れるのはセッションの境界のみでした — 開始時には RETROSPECTIVE が読み、終了時には ARCHIVER が書き込む。この 2 点の間では、すべての意思決定が現在の会話のみから行われていました。16-subagent の checks-and-balances 構造は強固でしたが、それらのエージェントが共有する認知基盤は空でした:

- PLANNER は、ユーザーが過去に類似の主題でどう決定したかを知らずに計画を立てた。
- 6 ドメインは、どの概念がどれにつながっているかを知らずに分析した。
- REVIEWER は、現在の決定の中の一貫性をチェックし、セッションをまたいだ一貫性はチェックしなかった。
- Adjourn 後、トレースを残すのは SOUL と Wiki の自動書き込みのみ — 概念グラフなし、synapse 強化なし。

ユーザーはこれを「AI はセッション内では慎重だが、セッション間では忘れてしまう」として感じ取りました。Cortex は、クロスセッションの記憶と概念グラフをあらゆるワークフローの first-class 入力とすることで、これを修正します。

失敗モードはいずれかの単一のエージェントが弱いということではありません — 16 のエージェントそれぞれがよく仕事をしています。失敗モードは、エージェントたちが他のセッションで学ばれたことを決して見ることがないということです。セッション 412 で金融的な決定に直面した PLANNER は、セッション 198 ですでに同じエンティティについての結論に到達していることを知りません。なぜなら、その結論を引き継ぐものは、raw の `_meta/journal/*.md` ファイル以外には何もなく、それらはユーザーからの明示的なリクエストがない限り誰も読まないからです。Cortex はこの引き継ぎを自動にします。

---

## 4 つの Core Mechanism(Four Core Mechanisms)

Cortex は 4 つのメカニズムから構成されます。それぞれに独自の仕様ファイルがあります。本ドキュメントは全体アーキテクチャです。

### 1. Hippocampus — リアルタイム・クロスセッション検索

すべてのユーザーメッセージが hippocampus サブエージェントをトリガーします(on-demand ではなく、常時動作)。3 段の spreading activation(活性化拡散):

- Wave 1: 直接マッチ(キーワードまたは concept_id ヒット)
- Wave 2: 強い接続(synapse weight ≥ 3)
- Wave 3: sub-threshold pre-activation としての弱い接続(weight < 3)

出力: 関連する過去セッションの上位 5-7 件を memory signal として GWT arbitrator に emit します。

実装は 2 段階スキャンに依存します: ripgrep が `_meta/sessions/INDEX.md`(1 行要約のコンパイル済みフラットファイル)を候補セッションにミリ秒単位で絞り込み、サブエージェントは一致した要約(通常 15-20 行)のみを読み、最終的に上位 5-7 件を返します。1000 セッション × 1 要約 200 文字の規模では(UTF-8 エンコードで CJK 要約 1 件 ≈ 600 バイト、ASCII のみの要約 1 件 ≈ 200 バイト)、フルインデックスはコンテンツ言語に応じて 200KB–600KB 程度 — どちらの場合でもスキャンは自明な負荷です。

完全な仕様: `references/hippocampus-spec.md`。

### 2. GWT Arbitrator — Salience competition(顕著性競合)

Stanislas Dehaene の Global Neuronal Workspace 理論に基づいています。複数の並列モジュールがシグナルを生成し、arbitrator が各シグナルの salience を計算し、top-K をブロードキャストします。最強のシグナルが「ignite」し、ROUTER に渡される cognitive annotation に入ります。

Salience formula (Phase 1、4 つの次元の加重和):

```
salience = urgency × 0.3 + novelty × 0.2 + relevance × 0.3 + importance × 0.2
```

Salience は自己申告ではありません。モジュールは raw スコアを emit し、arbitrator がクロスシグナルの整合性に基づいて調整します。シグナルには型があります — `memory`、`concept_link`、`identity_check`、そして後のフェーズでは `emotion`、`prediction` — 各型には confidence の下限があり、それを下回ると arbitrator はシグナルを完全に破棄します。Inhibitory シグナル(拒否権)は、より厳格なスキーマに従い、reasoning_chain が必須です。

完全な仕様: `references/gwt-spec.md`。

### 3. Narrator Layer — Grounded generation with citations(根拠に基づく生成と引用)

Summary Report がユーザーに表示される前に、narrator layer が実質的な主張を signal_id 引用でラップします。これにより、Gazzaniga の left-brain-interpreter 失敗モード(意思決定について、もっともらしい説明を作話する)を防ぎます。

出力の 2 カテゴリ:

- **Substantive claim(実質的な主張)** — signal_id 引用を必須とします。例: 「あなたは歴史的に、類似の意思決定において保守的でした。」
- **Connective tissue(接続組織)** — 引用は不要です。例: 「これを一緒に見てみましょう。」

validator サブエージェント(Sonnet ティアの Claude Code サブエージェント — 外部 API なし)が、レポート公開前に引用をチェックします。無効な引用は書き直しをトリガーします。

substantive と connective の分割はプラグマティックな判断であり、理論的なものではありません。すべての文に引用を要求すると、法律文書のような機械印字された出力になります。引用の規律は load-bearing な主張 — ユーザーが反論できる断定 — についてのものであり、会話のつなぎについてのものではありません。Phase 2 は claim ごとの粒度で動作します。実運用で過剰注釈に感じられる場合は、反作話保証を弱めることなく、粒度を段落ごとに粗くすることができます。

完全な仕様: `references/narrator-spec.md`。

### 4. Synapses + Hebbian — Use-it-or-lose-it 強化の概念グラフ

各概念は `_meta/concepts/{domain}/{concept}.md` 配下の markdown ファイルです。エッジ(synapse)は概念自身の frontmatter に存在します。同時活性化でエッジ weight が +1(Hebbian ルール)、長期間使われないエッジは減衰します。

4 段の permanence tier — identity、skill、fact、transient — が減衰曲線の形を決定します。減衰は各 adjourn ごとに実行され、ARCHIVER Phase 2 が駆動します。

各概念は 3 段の status を持ちます: `tentative`(first-seen、未確定)、`confirmed`(複数の activation、安定したアイデンティティ)、`canonical`(高頻度 activation、広くクロスリファレンスされている)。通常運用下では昇格は一方向ですが、three-tier undo メカニズム(Design Principles を参照)によって降格が可能です。逆方向エッジインデックス(`SYNAPSES-INDEX.md`)は、すべての Hebbian 更新ごとに再構築されます。これはコンパイル済みアーティファクトであり、手編集されることはありません。

完全な仕様: `references/concept-spec.md`。

---

## ワークフロー統合(Workflow Integration)

Cortex は既存の 11 ステップワークフローに 2 つのステップを追加します。既存のステップ番号は変更されません。

```
Step 0:    Pre-Session Preparation (ROUTER + RETROSPECTIVE parallel) — 変更なし
Step 0.5:  Pre-Router Cognitive Layer — 新規
Step 1:    ROUTER Triage — 注釈付き入力を受け取る
Step 2-6:  変更なし
Step 7:    Summary Report — 変更なし
Step 7.5:  Narrator validation — 新規 (Phase 2、Full Deliberation のみ)
Step 8-9:  変更なし
Step 10:   ARCHIVER Phase 2 — 拡張(下記参照)
Step 11:   STRATEGIST (オプショナル) — 変更なし
```

### Step 0.5 — Pre-Router Cognitive Layer

Pre-Session Preparation の直後、ROUTER Triage の前に spawn されます。3 つのサブエージェントが並列で動作します:

1. **hippocampus** — `_meta/sessions/INDEX.md` をスキャンし、上位 5-7 件の memory signal を返す
2. **concept lookup** — `_meta/concepts/` をスキャンし、直接マッチする概念ノードを返す
3. **SOUL dimension check** — RETROSPECTIVE の SOUL Health Report を再利用し、identity_check signal を emit する

3 つの出力ストリームが **gwt-arbitrator** に供給され、salience formula が適用され、シグナルがランク付けされ、ROUTER 向けに単一の annotated-input ブロックが生成されます:

```
[USER MESSAGE]
[COGNITIVE ANNOTATION]
- Relevant history: [5-7 session summaries with signal_ids]
- Concept graph: [matched concepts + 1-hop neighbours]
- SOUL context: [tier-1 dimensions + any conflict warnings]
```

ROUTER はアノテーションを参照することも無視することもできます — その triage ルールは変更されません。Step 0.5 がいずれかの時点で失敗した場合(サブエージェントのタイムアウト、ファイルアクセス不能)、orchestrator は raw message 入力にフォールバックし、v1.6.2a の動作を継続します。

**Express path interaction。** ROUTER が Express path(1-3 ドメインエージェント、PLANNER / REVIEWER なし)を取る場合、Step 0.5 は依然として実行されますが、縮小形式となります: hippocampus サブエージェントのみが spawn されます。Concept lookup と SOUL check は、Express の速度予算を保つためにスキップされます。Express path の注釈付き入力は、完全な 3 セクションブロックではなく、1 行の memory summary です。シグナル源が 1 つしかない場合、gwt-arbitrator は呼び出されません。

**Direct-handle interaction。** ROUTER が自明なメッセージ(例: 「ありがとう」「ok」)に直接応答し、ワークフローが Step 1 で終了する場合、Step 0.5 は完全にスキップされます。orchestrator は ROUTER の triage 決定をチェックすることでこれを検出します — direct-handle 応答は認知アノテーションを必要としません。

### Step 7.5 — Narrator Validation (Phase 2 のみ)

Summary Report が表示される前に、narrator-validator(Sonnet ティアの Claude Code サブエージェント — 現在のセッション内で動作し、外部 API なし)が、signal store に対してすべての実質的な主張をチェックします。無効または未引用の主張は、書き直しのために narrator に返されます。Connective tissue は無視されます。このステップは Full Deliberation でのみ実行されます — Express path と direct-handle 応答はこれをスキップします。

### Step 10 — ARCHIVER Phase 2 拡張

ARCHIVER Phase 2 はすでに wiki と SOUL の自動書き込みを処理しています。v1.7 では、以下も実行します:

- **Concept extraction** — セッション素材から新しい概念をスキャンし、permanence tier を分類し、`_meta/concepts/{domain}/{concept}.md` に書き込む
- **Hebbian update** — セッション内で co-activated されたペア (A, B) それぞれについて、A→B のエッジ weight を +1 する。エッジが存在しない場合は weight 1 で新規作成する
- **SYNAPSES-INDEX.md regeneration** — weight 更新後に逆方向インデックスを再構築する
- **SOUL snapshot dump** — 既存の v1.6.2 メカニズム、Cortex 下でも継続
- **Session summary write** — subject、key decisions、activated concepts、および hippocampus が後の読み込みで消費する 1 行 YAML summary フィールドを持った `_meta/sessions/{session_id}.md` を emit する

すべての書き込みは単一の ARCHIVER 起動内で発生します。orchestrator はフェーズ間で書き込みをインターリーブしません。これにより、`pro/CLAUDE.md` で定義される Adjourn ステートマシンが保持されます — ARCHIVER は全フェーズ完了時に 1 つの Completion Checklist を emit し、セッションは終了します。

### Step 0 と Step 11 は保持される

Pre-Session Preparation も STRATEGIST も変更されません。SOUL Health Report は引き続き RETROSPECTIVE によってコンパイルされます。STRATEGIST はユーザーの明示的な同意があった場合のみ呼び出されます。

---

## データ構造(Data Structures)

すべての Cortex データは markdown の中にあります。v1.7 で新規導入されるディレクトリ:

```
_meta/
├── concepts/
│   ├── INDEX.md                         ← コンパイル済み 1 行インデックス
│   ├── SYNAPSES-INDEX.md                ← コンパイル済み逆方向エッジインデックス
│   ├── _tentative/                      ← 確認待ちの概念
│   ├── _archive/                        ← 引退した概念
│   ├── finance/
│   │   └── {concept_id}.md
│   ├── career/
│   └── personal/
├── sessions/
│   ├── INDEX.md                         ← コンパイル済みセッション要約インデックス
│   └── {platform}-{YYYYMMDD-HHMM}.md    ← YAML 付きセッションごとの要約
├── snapshots/
│   └── soul/                            ← SOUL スナップショット (v1.6.2、継続)
├── eval-history/                        ← AUDITOR 評価履歴
└── cortex/
    ├── config.md                        ← しきい値とスイッチ
    ├── bootstrap-status.md              ← マイグレーション状態
    └── decay-log.md                     ← 減衰アクション
```

各メカニズムのデータ形式は、それぞれの仕様ファイルで定義されます。本ドキュメントはそれらの定義を重複させません。

- Concept ファイル形式 → `references/concept-spec.md`
- Session summary 形式 → `references/session-index-spec.md`
- Signal と arbitration record 形式 → `references/gwt-spec.md`
- Hippocampus 出力形式 → `references/hippocampus-spec.md`
- SOUL snapshot 形式 → `references/snapshot-spec.md`(v1.6.2 から継続)

### Cortex Runtime Files (schemas)

4 つの markdown アーティファクトが Cortex ランタイム状態を追跡します。いずれも source of truth ではありません — config(ユーザー編集可)またはコンパイル/ログアーティファクト(archiver が書き込む)のいずれかです。すべて `_meta/cortex/` 配下(最初の 3 つ)、または `_meta/ambiguous_corrections/` 配下(4 つ目)にあります。

#### `_meta/config.md`

ユーザー編集可能なしきい値とスイッチ。hippocampus、gwt-arbitrator、narrator-validator、および減衰パスが読み取ります。欠落している場合、各 consumer はハードコードされたデフォルト(下記にインライン記載)にフォールバックします。

```yaml
---
file: _meta/config.md
version: 1.7
---

# Cortex Config

## Feature switches
cortex_enabled: true              # master switch; false degrades to v1.6.2a behaviour
hippocampus_enabled: true
gwt_arbitrator_enabled: true
narrator_validator_enabled: true
concept_extraction_enabled: true

## Salience formula (gwt-arbitrator)
salience_weights:
  urgency: 0.3
  novelty: 0.2
  relevance: 0.3
  importance: 0.2
per_signal_floor: 0.3             # signals with salience < floor are dropped
top_k_signals: 5                  # hard cap of signals broadcast to ROUTER

## Decay curves (archiver Phase 2 decay pass)
decay_curves:
  identity: none                  # no decay
  skill: logarithmic              # decays to a steady baseline, never zero
  fact: exponential               # half-life 90 days
  transient: cliff                # zero at expiry

## Three-tier undo thresholds
escalate_rate_limit: 5            # per rolling 7-day window
ambiguous_correction_confidence_bands:
  high: 0.85                      # ≥ apply immediately
  mid_low: 0.5                    # mid-band lower bound (write to _meta/ambiguous_corrections/)
  low_floor: 0.0                  # logged but not acted

## Performance budgets (seconds, soft/hard)
hippocampus_timeout: [5, 15]
gwt_timeout: [5, 10]
narrator_validator_timeout: [3, 10]
```

このファイルを編集するユーザーは、クロスデバイスのドリフトを追跡するために git へコミットすることが推奨されます。変更は次のセッション開始時に有効になります(retrospective Mode 0 が config を読む)。

#### `_meta/cortex/bootstrap-status.md`

`tools/migrate.py` によって一度だけ書き込まれます。retrospective Mode 0 が Cortex の準備ができているかを判定するために読みます。

```yaml
---
file: _meta/cortex/bootstrap-status.md
---

# Cortex Bootstrap Status

migration_completed_at: 2026-04-20T14:32:10+09:00
from_version: v1.6.2a
to_version: v1.7
scope_months: 3

journal_entries_scanned: 127
sessions_synthesized: 38
concepts_extracted:
  tentative: 42
  confirmed: 18
  canonical: 7
snapshots_synthesized: 15
methods_extracted: 5
eval_history_backfilled: 0        # per spec: no backfill

errors: []                        # list of per-file parse failures
warnings:
  - "4 journal entries missing platform metadata; defaulted to 'claude'"
```

このファイルが欠落している場合、retrospective Mode 0 は Start Session ブリーフィングの先頭で「Cortex not bootstrapped — run `uv run tools/migrate.py`」と警告します。Cortex は動作し続けますが、空のグラフでの動作(cold-start mode)になります。

#### `_meta/cortex/decay-log.md`

各 adjourn の終わりに archiver Phase 2 が書き込む追記専用ログ。セッションごとに日付付きブロックを 1 つ追加します。

```yaml
---
file: _meta/cortex/decay-log.md
rolling_window_days: 90
---

# Cortex Decay Log

## 2026-04-20 session claude-20260420-1432
edges_decayed: 14
edges_pruned: 2                   # weight reached 0
concepts_demoted:
  - C:finance:quarterly-yield     # canonical → confirmed (90-day dormancy)
concepts_retired:
  - C:transient:2026-q1-event     # transient cliff
new_tentative: 3
new_confirmed: 1
new_canonical: 0

## 2026-04-19 session claude-20260419-1238
...
```

90 日より古いブロックは、次回 adjourn 書き込み時に末尾の `# Archive` セクションにコンパクト化されます。過去のアーカイブは git 履歴に存在します — 削除なし、Notion 同期なし。

#### `_meta/ambiguous_corrections/{correction_id}.md`

保留中の mid-confidence ユーザー訂正ごとに 1 ファイル。three-tier undo メカニズム(§Design Principles → Three-tier undo)が 0.5–0.85 バンドの confidence を持つ訂正を検出したときに作成されます: 即座に適用するには不十分で、ログして無視するには高すぎる場合。

```yaml
---
correction_id: 2026-04-20-concept-company-a-merge
target: C:finance:company-a-holding
target_type: concept              # concept | soul_dimension | method
correction_type: demotion | merge | split | alias_add | permanence_change
proposed_change: "demote from canonical to confirmed; merge alias 'Company-A HK'"
user_confidence: 0.72             # from correction heuristic (0.5-0.85 band)
signal_refs:
  - S:claude-20260420-1034
detected_at: 2026-04-20T10:34:12+09:00
surfaces_when: "next activation of C:finance:company-a-holding"
status: pending                   # pending | applied | dismissed
---

# Context

{One short paragraph quoting the user's language that triggered the
correction, plus a one-line archiver note explaining why confidence
landed in the mid-band rather than the high band. Max 30 lines.}
```

**Surfacing**: ターゲットが次に activate されたとき(hippocampus 出力における concept、check における SOUL dimension、dispatcher ルックアップにおける method)、retrospective Mode 0 または ROUTER は、処理を続行する前に保留中の訂正を提示します。ユーザーが確認 → `status: applied`、訂正は通常の three-tier undo メカニズムを通じて伝播します。ユーザーが却下 → `status: dismissed`、ファイルは削除され、却下を記す行が `decay-log.md` に追加されます。

**Retention**: applied/dismissed ファイルは削除されます。保留ファイルは 30 日間 activation がなければ(ユーザーが二度とターゲットにヒットしない — 訂正は stale)、`decay-log.md` に要約行としてコンパクト化されます。

---

## 実行モデル(Execution Model)

すべての Cortex コンポーネントは `pro/agents/*.md` で定義される Claude Code サブエージェントです。実行ルールは既存の 16 サブエージェントと同じです。

- **外部 API コールなし** — すべての LLM 処理は現在の Claude Code セッション内で発生します。Anthropic API key なし、Claude API プロキシなし、OpenAI SDK なし。
- **データベースなし** — ストレージ判断 ADR(`docs/architecture/markdown-first.md`)が authoritative です。Markdown が source of truth です。SQLite およびその他のデータベースはスコープ外です。
- **独立したバックグラウンドジョブなし** — cron なし、デーモンなし、scheduled worker なし。データ更新は ARCHIVER Phase 2 書き込み内で発生します。
- **外部秘密情報なし** — Claude Code がすでに提供しているもの以外の環境変数なし。Vercel なし、GitHub Actions なし、CI/CD パイプラインなし。
- **Concept decay はすべての adjourn ごとに実行される** — タイマーではなく。Adjourn フローが正規のメンテナンスウィンドウです。
- **必要な場合の Bash 実行 Python ツールはローカルで動作する** — マイグレーションヘルパー(`tools/migrate.py`)は Claude Code セッションから Bash 経由で呼び出されます。サービスではありません。

v1.7 で新規導入されるエージェントファイル:

| Agent | 目的 |
|-------|---------|
| `pro/agents/hippocampus.md` | クロスセッション検索、memory signal を emit |
| `pro/agents/gwt-arbitrator.md` | Salience competition、注釈付き入力を emit |
| `pro/agents/narrator-validator.md` | Sonnet Claude Code サブエージェント — 引用バリデーター(Phase 2) |

Narrator は新規のエージェントファイルではありません — narrator の動作は ROUTER 内部に存在します(`references/narrator-spec.md` §6 を参照)。Concept extraction は新規のエージェントファイルではありません — ARCHIVER Phase 2 内部に存在します(`references/concept-spec.md` §Hebbian Update Algorithm を参照)。

既存エージェントへの拡張:

- `pro/agents/archiver.md` Phase 2 — concept extraction、Hebbian update、method-candidate detection、decay pass、session summary write、index rebuild を追加
- `pro/agents/retrospective.md` Mode 0 — `_meta/concepts/INDEX.md` と `_meta/sessions/INDEX.md` を再生成、dormant concept にフラグを立てる
- `pro/agents/router.md` — 入力に cognitive annotation を受け入れる、Step 7.5 における narrator composition を所有

Claude Code は spawn 時に各エージェント定義を読みます。呼び出し間でランタイム状態は永続化されません。

### Information isolation additions(情報隔離の追加)

`pro/CLAUDE.md` 内の既存の Information Isolation テーブルに、v1.7 で 3 つの新しい行が追加されます。同じ原則 — 各エージェントは仕事に必要なものだけを受け取る — が維持されます:

| Role | 受け取るもの | 受け取らないもの |
|------|----------|------------------|
| hippocampus | ユーザーメッセージ + `_meta/sessions/INDEX.md` + 現在のセッションコンテキスト | 他のエージェントの思考プロセス、完全な概念グラフ |
| gwt-arbitrator | hippocampus / concept-lookup / soul-check からのシグナルファイル | ユーザーの raw message(シグナルのみで動作) |
| narrator-validator | Summary Report ドラフト + signal store | エージェントの思考プロセス、ユーザーのプライベートデータ |

gwt-arbitrator が raw message から隔離されるのは意図的です — salience 計算は、会話表面にバイアスされるのではなく、構造化シグナルに対して動作すべきです。narrator-validator が思考プロセスから隔離されるのは、循環バリデーションを防ぐためです。

---

## 設計原則(Design Principles)

### Grounded generation(根拠に基づく生成)

Cortex 出力におけるどの主張も、signal_id 引用なしではできません。これは作話に対する主要な防衛線です。バリデーターサブエージェントは、引用されたシグナルを取得し、narrator の言い換えが忠実かをチェックすることで、これを強制します。いずれかの実質的な主張に引用が欠けている場合、または引用が主張を支持しない場合、narrator は書き直します。

Gazzaniga の left-brain-interpreter 実験は、人間が意識的に行っていない決定について、もっともらしい説明を作話することを示しています。もし Cortex がこのメカニズムを再現したなら、それは self-deceiving なシステムになります — 意思決定はその時点で最も大きなシグナルによって駆動され、事後的に一貫して見える narrative に合理化されます。Grounded generation は構造的な答えです: バリデーターは signal store への読み取り専用アクセスを持つ別のサブエージェントとして動作するため、迂回できません。signal_id を捏造する narrator は、取得時にバリデーションで失敗します。

### Transient state を含む 3-tier concept permanence + 1(Three-tier concept permanence with a fourth for transient state)

| Permanence | 減衰の形 | 例 |
|-----------|-------------|----------|
| Identity | 減衰しない | SOUL コアバリュー、長く続く人間関係 |
| Skill | 安定したベースラインへの対数減衰 | 「Python の書き方」 |
| Fact | 指数減衰 | 「去年の Q2、プロジェクト X の予算は Y だった」 |
| Transient | 満了時にゼロへ cliff 減衰 | イベント特有、一回限りの参照 |

Permanence は ARCHIVER Phase 2 の concept extraction 中、最初の activation で割り当てられます。ユーザーは permanence を明示的に固定できます。Meta-cognition は、概念が downgrade を「試され」ても減衰に抵抗した場合、permanence を上昇させることができます。

### Spreading activation, not exhaustive retrieval(活性化拡散であり、網羅的検索ではない)

hippocampus はすべてのセッションファイルをスキャンしません。Wave 1 には ripgrep を使用し、Wave 2 には 1-hop synapse 探索を、Wave 3 には sub-threshold pre-activation を使用します。クエリごとの合計スコープは制限されます: 上位 50 の concept ノードが最大。これは、脳の中で spreading activation が動く仕組み — 強度がグラフ距離とともに減衰する — と一致します。

Wave 3 は pre-activation であり、検索ではありません。Sub-threshold の概念は、同じセッションの後のフレームがしきい値を超えて押し上げない限り、出力には現れません。これは脳の priming 動作を再現します: 最近 activate された概念の近傍は、直接的な証拠がなくても、次のフレームでトリガーされやすくなります。運用上の効果は、「company-A holding」についての質問でセッションを開くと、ユーザーが parent 名を繰り返さなくても、「company-A subsidiary」についての後の質問により反応しやすくなるということです。

### Salience competition, not rule-based priority(ルールベース優先度ではなく、salience competition)

シグナルには固定優先度はありません。すべてのフレームで salience formula を介して競合します。文脈が認める場合、高 urgency の memory signal は、高 importance の identity signal を上回ることができます。どのシグナルが ignite するかを決定するのは arbitrator だけです。

### 推論チェーン付きの構造化拒否(Structured veto with reasoning chain)

これはブレインストーミングの Path B です。Inhibitory signal(拒否権)は単なる strength-based 抑制ではありません — claims、evidence_signals、confidence を持つ reasoning_chain を携えなければなりません。これにより、拒否が監査可能になります。シグナルの同じペアが同一の競合を 2 度生成する(新しい証拠なしの rebuttal loop)と、システムは自動的にユーザーへエスカレートします。

代替案(Path A — suppression-by-strength)は却下されました。なぜなら、ソフトウェアシステムの中の inhibitory signal には、それを裏付ける進化的ヒューリスティクスがないからです。脳は不透明な拒否を許容できます — 何十億年の進化が拒否ニューロンを調整したためです。ソフトウェアモジュールにはそのような基盤はありません。モジュールからの不透明な拒否は、単なる Opus の直感です。reasoning_chain を要求することで、すべての拒否はユーザーが検査でき、必要であれば覆せるものになります。これは、Life OS の原則 — システムはユーザーの instrument であり、ユーザーに対する authority ではない — を保持します。

### Three-tier undo(3 段の取り消し)

訂正できないシステムは有用ではありません。Cortex は 3 つの訂正経路を提供します:

1. **Passive decay** — 使われていない canonical concept は時間とともに降格します(90 日後に fact ティアへ)。ユーザーのアクションは不要です。
2. **User correction** — 「これは間違いだった」が、影響を受ける synapse すべてにカスケードマーキングを伴う concept_demotion 修正をトリガーします。
3. **Meta-cognitive audit** — 週次監査が、疑わしい drift(競合する salience、頻度低下、繰り返されるユーザー訂正)を `_meta/audit/suspicious.md` に浮上させます。ユーザーが降格前に確認します。

ユーザー訂正の confidence は階層的です: 高 confidence(>0.85)訂正は即座に適用されます。中 confidence(0.5-0.85)訂正は `_meta/ambiguous_corrections/` に書き込まれ、次の関連 activation 時に明示的な確認のために浮上します。低 confidence(<0.5)訂正はログに記録されますが、実行されません。初期しきい値は意図的に保守的です — 偽陰性(訂正を見逃す)は、偽陽性(ユーザーが降格を望まなかったものを降格させる)よりコストが低いためです。

Meta-cognitive audit にはレート制限があります: ローリング 7 日ウィンドウで **5 回を超えるエスカレーション** があると、モジュール品質自体の二次監査がトリガーされます。前提は、正しく機能しているシステムはめったにユーザーに競合を浮上させる必要がないということです。頻繁なエスカレーションは、個別の訂正ニーズではなく、モジュールレベルの drift を示します。

#### `_meta/audit/suspicious.md` 形式

Meta-cognitive audit は単一のローリング markdown ファイルに書き込みます。Archiver Phase 2 が候補を追記し、retrospective Mode 0 が未解決行を Start Session ブリーフィングで浮上させ、ユーザーが確認または却下します。形式:

```yaml
---
file: _meta/audit/suspicious.md
rolling_window_days: 30
last_compacted: ISO 8601
---

# Audit · Suspicious Drift

| Detected | Candidate | Reason | Signal refs | Status |
|----------|-----------|--------|-------------|--------|
| 2026-04-18 | C:finance:company-a-holding | 4 user corrections in 2 weeks; salience stable | S:claude-20260418-0934, S:claude-20260416-1520 | open |
| 2026-04-17 | C:method:iterative-refinement | Activation dropped 80% vs 90-day baseline | S:claude-20260417-1400 | dismissed 2026-04-19 |
```

Columns:

- **Detected** — archiver が drift をフラグ立てした ISO 日付
- **Candidate** — 疑いのある concept / SOUL dimension / method の完全 prefix 付き signal_id
- **Reason** — 4 つのヒューリスティクスのいずれかからの 1 行説明: `conflicting_salience`、`frequency_drop`、`repeated_user_correction`、`canonical_contradiction`
- **Signal refs** — 検出を支持する signal_id のカンマ区切りリスト(`narrator-validator` 形式の検証用)
- **Status** — `open` / `confirmed YYYY-MM-DD` / `dismissed YYYY-MM-DD`

30 日以上経過し `status: open` の行は、archiver Phase 2 実行時に末尾の「# Archive」セクションにコンパクト化されます。Dismissed/confirmed 行は 90 日後にコンパクト化されます。ファイルはアクティブで約 300 行を超えることはありません。コンパクションが読み取りレイテンシを境界化します。

#### Escalate rate limit(エスカレートレート制限)

週 5 回のしきい値は、AUDITOR が patrol inspection 中に監視します(フックや Python ツールではなく、セッション内に留まります)。超過した場合、AUDITOR は `_meta/eval-history/{date}-{project}.md` に `violations[].type: escalate_rate_exceeded` 付きの高優先度エントリを書き、パターンを retrospective Mode 0 の次のブリーフィングで浮上させます。自動的にカットされるモジュールはありません(ユーザー判断 #4 — 事前に commit された kill criteria なし)。基盤となるメカニズムにチューニングが必要かはユーザーが判断します。

---

## 既存コンポーネントとの関係(Relationship to Existing Components)

Cortex はどの既存 Life OS コンポーネントも置き換えません — それらを augment します。下表は、v1.7 下で各既存サーフェスがどのように形を得る(または保つ)かを要約します。

| 既存コンポーネント | Cortex 下の役割 | 変化の性質 |
|-------------------|-------------------|------------------|
| SOUL.md | Identity レイヤー、identity_check シグナルの source | 変更なし。SOUL 自動書き込みは継続。Health Report が Step 0.5 に供給。 |
| wiki/ | Concept anchor 素材、ARCHIVER Phase 2 concept extraction の証拠源 | 変更なし。Wiki エントリは concept ノードとは別のまま。しかし anchor となることができる。 |
| DREAM | Offline sleep-phase パターンプロセッサ | 構造的には変更なし。REM cross-domain leap のために concept graph を消費できる。 |
| RETROSPECTIVE | セッション開始ハウスキーピング + SOUL Health Report | Mode 0 は減衰チェックと concept INDEX rebuild を含むよう拡張。 |
| ARCHIVER | セッションクロージャー、4-phase closer | Phase 2 は concept extraction、Hebbian update、session summary write を含むよう拡張。 |
| ROUTER | Triage と report オーケストレーション | 入力形式の変更(raw ではなく注釈付き入力)、triage ルールは変更なし。 |
| 16 subagents | Deliberation cast (PLANNER / REVIEWER / 6 ドメインなど) | 変更なし。ROUTER が注釈付き入力を forward した場合に richer context を消費。 |

3 つの不変条件が保持されます: (1) Cortex は ROUTER により良い入力を与えるが、ROUTER に代わってメッセージを解釈しない。(2) Cortex は ARCHIVER に追加の書き込みターゲットを与えるが、ARCHIVER の single-invocation 規律をバイパスしない。(3) Cortex は 16-agent deliberation の周りに認知を加えるが、checks-and-balances 構造を変更しない。エージェントは依然として仕事に必要なものだけを見ます。

---

## Archiver Candidate Routing (Phase 2 disambiguation)

archiver Phase 2 がセッションコンテンツから候補を抽出するとき、**各候補がどのナレッジレイヤーに属するか** を決定しなければなりません。決定は任意ではありません — 各レイヤーは異なる問いに答えるため、誤ルーティングは silent drift を生みます(事実が価値観として格納される、手順が概念として格納される、アイデンティティが wiki に格納される)。

これは authoritative な decision tree です。いずれかの仕様がこの tree と反する場合、この tree が勝ちます。

### 4 つのナレッジレイヤー + 1 つのアイデンティティレイヤー

| Layer | 問い | 候補例 | パス |
|-------|---------|-------------------|------|
| SOUL | あなたが誰か(アイデンティティ / 価値観 / 好み) | 「ユーザーは一貫してキャリア成長より家族を優先する」 | `SOUL.md`(1 ファイル、次元は内部) |
| Wiki | 世界について何を知るか(declarative) | 「日本における NPO 貸付には 貸金業法 例外がない」 | `wiki/{domain}/{slug}.md` |
| Concept | アイデアがどうつながるか(associative graph node) | 「Company-A」は、weighted edge を介して他の概念とつながるエンティティ | `_meta/concepts/{domain}/{concept_id}.md` |
| Method | 最善の仕事の仕方(procedural memory) | 「5 段のエスカレーティング品質ラウンドで文書を洗練する」 | `_meta/methods/{domain}/{method_id}.md` |
| user-patterns | あなたが何をするか(観察された behavioral pattern、ADVISOR ドメイン) | 「最初の明確化ラウンド後に意思決定が速くなる」 | `user-patterns.md`(1 ファイル、エントリは内部) |

### Decision tree

Archiver Phase 2 は各候補をこの tree に通します。最初にマッチした分岐が勝ちます — 候補は複数の primary レイヤーにルーティングされることはありません。

```
候補はユーザーのアイデンティティ、価値観、好み、あるいは red line に関するものか?
├── YES → SOUL
│         (evidence は現在セッション、あるいは直近 30 日から 2 件以上の決定;
│          新しい次元は信頼度 0.3 で自動書き込み、What SHOULD BE は空)
│
└── NO → それは behavioral pattern か(ユーザーが「何をする」か、「誰であるか」ではない)?
    ├── YES → user-patterns.md (patterns-delta 経由で追記)
    │         (ADVISOR がこれを浮上させる;SOUL ではない)
    │
    └── NO → それは再利用可能な WORKFLOW か(一連のアクション、method 的)?
        ├── YES → Method
        │         (5 以上の sequential action、2 以上のセッションでの cross-session echo、
        │          ユーザー言語は「approach/pattern/framework/流れ/やり方/手順」;
        │          _meta/methods/_tentative/ に status: tentative で着地)
        │
        └── NO → それは他とつながる recurring ENTITY / CONCEPT か?
            ├── YES → Concept
            │         (2 回以上の activation + 2 つ以上の独立した証拠点;
            │          _meta/concepts/_tentative/ に着地、promotion まで;
            │          個人 → skip、または SOUL にルーティング(privacy filter が判断))
            │
            └── NO → それは世界についての FACTUAL conclusion か?
                ├── YES → Wiki
                │         (6 基準: cross-project-reusable、about-the-world、
                │          zero-privacy、factual-or-methodological、2 以上の evidence、
                │          no-contradiction-with-existing;wiki-spec §Auto-Write Criteria を参照)
                │
                └── NO → Discard (再利用不可能;セッションジャーナルのみに留まる)
```

### 曖昧性解消の例(Disambiguation examples)

| 候補 | ルート | 理由 |
|-----------|-------|-----|
| 「ユーザーは速度より品質を優先する」 | SOUL | アイデンティティ / 価値観の記述 |
| 「ユーザーは月曜日の金融議論を避ける傾向」 | user-patterns | 行動パターン(何をするか)、アイデンティティではない |
| 「MVP 検証は 5 段エスカレーティング品質ラウンドを使う」 | Method | 再利用可能な手続き型ワークフロー |
| 「Company-A と Company-B は、Project-X の board に座るディレクターを共有」 | Concept (+ edge) | エンティティを持つグラフ構造 |
| 「日本における NPO 貸付には 貸金業法 例外がない」 | Wiki | 世界についての事実的結論 |
| 「反復的な文書洗練は、各ラウンドが 1 つの focus を持つときに最善」 | Method | 手続き型 how-to |
| 「越境プロダクト決定でガバナンス懸念は 30% の重みを持つべき」 | Wiki | Declarative conclusion |
| 「Finance と Execution エージェントは前セッションで 4 ポイント差で対立」 | Discard | 単一セッション観察、クロスセッション再利用可能ではない |
| 「ユーザーの特定の家族 A の好み」 | Skip(または privacy filter 付き SOUL) | 個人は Concept にルーティングされない;SOUL の privacy filter が、SOUL が受け入れるか破棄するかを判断 |

### Ambiguous cases(曖昧なケース)

**Fact with procedural edge**: 「rate increase を交渉するときは、データでアンカリング」は、method(手順)あるいは wiki conclusion(世界についての事実)として読み得ます。ルール: 候補が **ユーザーアクションのシーケンス** を記述している場合、それは method。**世界の特性** を記述している場合、それは wiki。真に曖昧な場合、**wiki** にデフォルトで倒します — method はより強い証拠(2 以上のセッションにわたる 5 以上の sequential step)を要求します。

**Concept with SOUL overlap**: 関係的な次元としての「trust」は、SOUL(価値観)または concept(関係エンティティタイプ)になり得ます。ルール: concept は **世界の中の、他のものとつながる事物** に関するもの。SOUL は **ユーザーの、事物への志向** に関するもの。「ユーザーはビジネス関係における信頼を大切にする」 → SOUL。「信頼は、プロジェクト間を流れる関係資本のタイプ」 → concept(`_meta/concepts/relationship/` に入る)。

**Wiki with method flavour**: 世界の事実的記述(ユーザーが選んだワークフローではない)であるステップバイステップレシピ → wiki。ユーザーが意識的にそれを自分の method として採用した場合 → method。ヒューリスティクス: archiver は「ユーザーはこのワークフローを所有しているか?」と問います — yes なら method、no(単なる既知の技法)なら wiki。

### ルーティング信頼度と保留状態(Routing confidence and pending state)

Archiver Phase 2 は各候補にルーティング信頼度を割り当てます:

- **High (>0.85)** — ターゲットレイヤーに `status: tentative`(concepts/methods の場合)で進む、あるいは SOUL に信頼度 0.3 / wiki に信頼度 0.3-0.5 で自動書き込み
- **Mid (0.5-0.85)** — `_meta/ambiguous_corrections/` に、次の関連 activation 時のユーザー確認待ちのルーティング決定訂正として書き込み
- **Low (<0.5)** — 理由付きで「routing-rejected candidate」として `_meta/cortex/decay-log.md` にログ、どこにも書き込まれない

これは three-tier undo メカニズム(§Design Principles → Three-tier undo)を反映しています — archiver は不確実な場合は慎重な側に倒します。False negative(見逃された候補)は、False positive(後で外科的な逆転が必要な wrong-layer 書き込み)よりコストが低いです。

### アンチパターン(Anti-patterns)

- **同じ候補を 2 つのレイヤーにルーティングする** — 厳密に 1 つの primary 宛先。Concept は `anchors_in_wiki: [slug]` 経由で wiki エントリを参照 MAY ですが、それはクロスリファレンスであり、重複書き込みではありません。
- **個人のための concept を作成する** — concept-spec §9(Privacy)違反。個人は privacy filter 適用済み SOUL に属します。
- **2 つ以上の独立セッションでパターンを示さずに method を書く** — method-library-spec §6(heuristic)違反。Cross-session echo は証拠の最低基準です。
- **6 基準のいずれかに失敗した wiki エントリを書く** — wiki-spec §Auto-Write Criteria 違反。6 つすべて、あるいは破棄。
- **ルーティング中に SOUL を直接 mutate する** — SOUL 自動書き込みはそれ独自の 3 基準ゲート(identity-scope + 2 以上の evidence + 既存次元なし)を使います。ルーティングは提案する;SOUL 自動書き込みが受諾します。

---

## アンチパターン(Anti-patterns)

Cortex は以下を MUST NOT 行います:

- **Source of truth としてのデータベース** — authoritative な store は markdown です。SQLite、Postgres、あるいは任意のリレーショナルインデックスはスコープ外です。
- **Cortex データを Notion へ同期する** — concept ノード、synapse、frame record は Notion をラウンドトリップしません。Notion は session summary と decision record のみを受け取ります — v1.6.2a と同じです。
- **外部 API key を要求する** — Claude API なし、OpenAI SDK なし、サードパーティ embedding なし。すべての intelligence は Claude Code 内部で動作します。
- **データ源のない signal を作り出す** — どのモジュールから emit される signal も、その payload がどこから来たかを引用しなければなりません。合成された証拠は禁止です。
- **narrator が引用なしに claim を行う** — 実質的 claim は引用必須です。バリデーター強制はオプショナルではありません。
- **永続デーモンとして動作する** — Cortex は現在セッションの中で動作します。セッション間で markdown 以外は何も永続化されません。
- **premium edition を構築する** — 普遍版が 1 つあります。ユーザー tier に基づく feature-gating はありません。

---

## バージョンとマイグレーション(Version & Migration)

Cortex は **v1.7** で導入されます。ブレインストーミングでその rollout が 4 つの内部ステージ(A から D)に分割され、そのうち最初のステージ(A)はさらに 3 つのフェーズ(A1/A2/A3)に細分化されましたが、それらはすべて v1.7 内に着地します — v1.8 / v1.9 / v2.0 にまたがりません。バージョン番号は統一されます。

v1.7 内部ステージ:

| Stage | スコープ |
|-------|-------|
| A — Data structure | `_meta/concepts/`、`_meta/sessions/INDEX.md`、ARCHIVER Phase 2 が concept extraction を獲得(Hebbian off) |
| B — Cognitive pre-router online | hippocampus + gwt-arbitrator サブエージェント稼働、Step 0.5 配線、Hebbian on |
| C — Narrator + undo メカニズム | Step 7.5 アクティブ、three-tier undo 稼働、escalate rate limit |
| D — 完全 cortex + Hermes 実行レイヤー | downgrade されたモジュールの backfill、完全な実行レイヤー |

4 つのステージすべては v1.7 内にシップされます。staging は内部の sequencing であり、incremental release ではありません。ステージがそもそも存在する理由は、それぞれが後に続くもののための自然なチェックポイントであるためです: ステージ B は、ステージ A が十分な concept とセッションデータを生成するまで、有用に機能できません。ステージ C の narrator は、ステージ B が生成しなかった signal に対してバリデーションできません。ステージ D は、ステージ B と C が機能することを示したものを洗練します。ステージは自然な依存関係ゲートです — 外部リリースポイントではありません。

ステージ A は 3 つのフェーズに細分化されます: A1(データ構造着地)、A2(migrate.py backfill)、A3(seed.py bootstrap)。A1 が着地すれば、A2 と A3 は並列実行できます。ステージ B、C、D は単一フェーズのままです。完全な内部シーケンスは A1 → (A2+A3 parallel) → B → (C+D parallel) であり、すべてが v1.7 としてシップされます。

AUDITOR は、`eval-history` エントリ(`references/eval-history-spec.md`)を通じてシップ後の品質を追跡します。品質 regression は eval-history パターンとして浮上します。モジュールレベルのスコープ変更は、事前 commit された数値しきい値ではなく、通常の仕様改訂を通じて発生します。

### v1.6.2a からのマイグレーション

Cortex は hippocampus が何かを取得できる前に、セッションインデックスの backfill を要求します。マイグレーションは直近 3 ヶ月の `_meta/journal/*.md` を引き、セッションごとの要約を生成します。

```
Script: tools/migrate.py
Input:  _meta/journal/*.md           (existing session journals)
Output:
  - _meta/sessions/{session_id}.md   (one file per historical session)
  - _meta/sessions/INDEX.md          (compiled one-liner index)
  - _meta/concepts/**/*.md           (seed concepts from journal entities)
  - _meta/snapshots/soul/**          (backfilled SOUL snapshots when possible)
```

マイグレーションスクリプトは Claude Code から Bash 経由で呼び出されます。冪等です — 再実行は、concept を重複させることなくコンパイル済みインデックスを上書きします。マイグレーション後、ユーザーは Cortex 有効で 1 セッションを実行します。注釈付き入力が正しく感じられれば、Cortex は定常状態に promote されます。

マイグレーションが失敗した場合、orchestrator は raw message 入力にフォールバックし、警告をログします。ユーザーはマイグレーションがリトライされるまで v1.6.2a と同様に動作します。

3 ヶ月スコープは意図的なデフォルトです: 古いジャーナルはしばしば outdated context(引退したプロジェクト、降格された価値観、SOUL 以前の決定)を含み、それは concept graph を汚染するでしょう。より豊富な履歴を持つユーザーは、マイグレーションスクリプトに `--since YYYY-MM-DD` を渡すことでスコープを override できます。ジャーナル履歴のない初回ユーザーは Cortex を「cold start」モードで実行します — 注釈付き入力は、十分なセッションが蓄積するまで minimal です。システム利用をブロックするものは何もありません。

---

## 未解決の問い(Open Questions)

以下の仕様は、実装中に解決するために意図的に残されています — 忘れられているからではなく、正しくチューニングするために具体的なデータが必要だからです。

- **Salience formula weight tuning** — Phase 1 の重み(urgency 0.3、novelty 0.2、relevance 0.3、importance 0.2)は placeholder です。検証には 3 ヶ月の実 annotated-input データが必要です。
- **Concept permanence classification heuristics** — ARCHIVER Phase 2 の concept extraction は、first activation においてヒューリスティックルールを使います。skill と fact の境界はあいまいです。3 ヶ月の実使用後の修正が見込まれます。
- **Narrator citation density** — 文ごと対段落ごと。Phase 2 は per-substantive-claim から始まります。出力が機械印字的に感じられれば、粒度が粗くなる可能性があります。
- **Multi-device concurrency** — single device / distributed sync / active-lock — 3 オプション、Phase 1 ローンチで 1 つが選択されます。
- **Frame trigger policy** — v1.7 ではすべてのユーザーメッセージが Step 0.5 をトリガーします。外部イベント(scheduled prompts、inbox arrivals)は v1.7 の frame trigger のスコープ外です — ユーザーメッセージのみが Step 0.5 をトリガーします。
- **Cold-start behaviour** — ジャーナル履歴のない新規ユーザーは、Cortex を degraded モードで実行します。Cortex が cold-start から定常状態へ遷移する厳密なポイント(セッション数、concept 数、あるいはヒューリスティクス)はまだ選ばれていません。

---

## References

- 全体アーキテクチャ議論 → `devdocs/brainstorm/2026-04-19-cortex-architecture.md`
- 統合ブリッジドキュメント → `devdocs/architecture/cortex-integration.md`
- Markdown-first ADR → `docs/architecture/markdown-first.md`
- Hippocampus メカニズム → `references/hippocampus-spec.md`
- GWT arbitrator メカニズム → `references/gwt-spec.md`
- Narrator layer メカニズム → `references/narrator-spec.md`
- Concept graph + Hebbian ルール → `references/concept-spec.md`
- Session index 形式 → `references/session-index-spec.md`
- SOUL snapshot 形式 → `references/snapshot-spec.md`
- AUDITOR 評価履歴 → `references/eval-history-spec.md`
- ワークフローオーケストレーション → `pro/CLAUDE.md`
- データレイヤー境界 → `references/data-layer.md`
- SOUL メカニズム → `references/soul-spec.md`
- Wiki メカニズム → `references/wiki-spec.md`
- DREAM メカニズム → `references/dream-spec.md`

---

> ℹ️ **2026-04-22 更新**：EN R1 で修正された 3 箇所を同期(Archiver Candidate Routing / Hippocampus size 計算 / Stage A 階層構造)

本文は [英語版](../../../references/cortex-spec.md) 2026-04-21 スナップショットの翻訳です。英語版が権威源で、曖昧な場合は英語版が優先します。
