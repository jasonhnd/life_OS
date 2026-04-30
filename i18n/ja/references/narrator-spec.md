---
title: "Narrator Spec — Grounded Generation Layer for Cortex"
version: v1.7
status: legacy
authoritative: false
superseded_by: pro/agents/narrator.md
scope: references
audience: Life OS maintainers + orchestration implementers
last_updated: 2026-04-20
translated_from: references/narrator-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
related:
  - references/cortex-spec.md
  - references/hippocampus-spec.md
  - references/gwt-spec.md
  - references/eval-history-spec.md
  - devdocs/brainstorm/2026-04-19-cortex-architecture.md
  - devdocs/architecture/cortex-integration.md
  - pro/agents/router.md
  - pro/CLAUDE.md
---

# Narrator Spec · Grounded Generation Layer

> narrator layer は ROUTER の出力ステージです。ユーザー向けテキストを生成しながら hallucination を防ぎます。すべての実質的な主張は、背後にあるシグナルへの引用を携帯します。

---

## 1. 目的(Purpose)

narrator layer は、ユーザー向けテキストを生成しながら hallucination を防ぐ ROUTER の出力ステージです。

この設計は Michael Gazzaniga の **left-brain interpreter** 研究に基づいています。Split-brain 実験は、人間の左半球が、説明を求められている行動の背後にある実際のデータを持っていないときでさえ、self-consistent な物語を作話(confabulate)することを示しました。脳は、流暢で一貫性があり、完全に間違った因果的ナラティブを生成し — そしてそれを誠実に信じ込みます。これは **bug** であり、機能ではありません。Cortex はこれを継承してはなりません。

narrator 出力における実質的な主張はすべて、背後にあるシグナルを引用しなければなりません。引用なしでは、主張は出荷されません。Cortex が grounding なしに emit してはならない例:

- "You've been struggling with commitment." — SOUL シグナルなし。
- "Last time you made a similar decision..." — hippocampus セッションなし。
- "Your Finance domain usually says..." — 過去スコアパターンなし。

シグナルがなければ、主張もありません。これが narrator のコア不変条件です。

---

## 2. 設計原則 · Grounded Generation(Design Principle · Grounded Generation)

narrator 出力内のすべての **substantive claim(実質的な主張)** は `signal_id` 引用を携帯しなければなりません。引用のない主張は validator によって拒絶されます。これは 3 つの失敗モードを防ぎます:

1. **Historical confabulation** — 起こらなかった過去をでっち上げる。
2. **Pattern confabulation** — データが示していない行動トレンドをでっち上げる。
3. **Cross-session confabulation** — つながれたことのない意思決定間のリンクをでっち上げる。

narrator は creativity レイヤーではありません。検証済みのシグナルセットを読みやすい散文に変える **grounded composition layer(根拠に基づく構成レイヤー)** です。

Grounded generation には 2 つの hard requirement があります:

- narrator は現在のセッションの **signal source registry(シグナルソースレジストリ)** にアクセスできなければなりません(§9)。
- すべての substantive な文は、そのレジストリ内の 1 つ以上のエントリを指さなければなりません。

レジストリが空(例: サブエージェントを spawn しない direct-handle)の場合、narrator は pass-through に劣化します(§13)。

---

## 3. Substantive と Connective な主張(Substantive vs Connective Claims)

すべての文に引用が必要というわけではありません。談話の接着剤に機械的に引用をつけると、真理値を加えることなく出力が読みにくくなります。

**Substantive**(引用が必要) — 削除すると事実内容が失われる場合、その文は substantive です:

- Historical: "Last time you did X..."
- Pattern: "You tend to..."
- SOUL: "This aligns with your value Y."
- Decision implications: "The GOVERNANCE concern is..."
- Cross-session linkages: "Related to your decision in project Z."
- 数値 / スコア主張: "Finance scored this 6/10."
- Attribution: "ADVISOR flagged emotional weight."

**Connective**(引用不要) — 談話の接着剤:

- Transitional: "Let me walk through this."
- Framing: "Here's what the analysis shows."
- Meta-commentary: "I'll give a brief summary."
- Opening / closing: "Okay, looking at this..."
- 純粋な言い換え: "In other words..."

**判定ルール**: 文を削除すると事実内容が失われる → substantive。談話の接着剤のみであれば → connective。validator(§8)は引用をチェックする前にこのルールを使用します。

---

## 4. 引用フォーマット(Citation Format)

### インライン構文

```
{claim text} [signal_id] {continued text}
```

1 つの主張が複数の引用を持つことがあります:

```
{claim text} [signal_id_1][signal_id_2] {continued text}
```

引用は、それが根拠づける節の **末尾** に、その節を次と分離する句読点の前に出現します。

### 例

```
Your past "passpay-v06-refinement" session [S:claude-20260419-1238] shows a similar 5-round iteration pattern, with GOVERNANCE scoring 5/10 [D:passpay-governance-score].

This conflicts with your "risk-tolerance" dimension (confidence 0.72) [SOUL:risk-tolerance-v3].

Finance and Execution disagreed by 4 points [D:finance-score-6][D:execution-score-2], triggering COUNCIL debate.
```

### Prefix 規約

引用 ID はソース型を示すために固定の prefix を使用します:

| Prefix  | 意味                        | 例                                         |
|---------|-------------------------------|--------------------------------------------|
| `S:`    | session_id                    | `S:claude-20260419-1238`                   |
| `D:`    | 特定のドメインスコア / フィールド | `D:passpay-governance-score`               |
| `SOUL:` | SOUL dimension                | `SOUL:risk-tolerance-v3`                   |
| `C:`    | concept                       | `C:method:iterative-document-refinement`   |
| `W:`    | wiki entry                    | `W:finance/compound-interest`              |
| `P:`    | user-patterns.md 内のパターン | `P:avoids-family-topic-on-weekends`        |

prefix は **固定** です。narrator は新しい prefix を発明してはなりません。ソース型が上記のいずれにもマップされない場合、narrator はそれを引用してはなりません(そしてしたがって、そもそも実質的な主張を行ってはなりません)。

---

## 5. Narrator の呼び出し(Narrator Invocation)

narrator は pro/CLAUDE.md ワークフローに **Step 7.5** として挿入され、Step 7 Summary Report 構成の後、Step 8 AUDITOR の前に来ます:

```
Step 7: Summary Report (ROUTER composes)
  ↓
Step 7.5: Narrator Layer
  - ROUTER sends Summary Report + signal source list to narrator subagent
  - Narrator rewrites output with citations
  - Validator subagent (Claude Code subagent, not Anthropic API) checks citations
  - If validation fails, narrator regenerates
  ↓
Step 8: AUDITOR
```

Step 7.5 は **Full Deliberation** パスに対してのみ呼び出されます。Express analysis(Step 1E)は Step 7.5 をスキップする brief report を生成します。Direct-handle と STRATEGIST セッションはこれを完全にスキップします(§13)。

---

## 6. Narrator Agent

ROUTER 自身が narrator の役割を担います。**別個の `pro/agents/narrator.md` ファイルはありません**。narrator の動作は pro/CLAUDE.md の orchestration 更新によって設定され、ROUTER の出力構成責務の内部に存在します。

理由: ROUTER はすでに Summary Report の構成を所有しています(Step 7)。narrator はそのステージの拡張であり、新しい役割ではありません。スタンドアロンの narrator エージェントは ROUTER のコンテキストを複製することになります。書き直し + 引用は新しい意思決定ではありません — これを ROUTER の内部に保つことで、ユーザー向け出力の単一所有権が維持されます。

スタンドアロンのサブエージェントとなるのは **validator** のみです(§7)。

---

## 7. Validator サブエージェント(Validator Subagent)

新しいサブエージェントファイルが作成されます: `pro/agents/narrator-validator.md`。

```yaml
---
name: narrator-validator
description: "Validates narrator citations against signal sources (Cortex)"
tools: [Read]
model: sonnet
---
```

### なぜ Claude Code subagent であり、外部 Haiku API ではないのか

ユーザー決定 #9(v1.7 Cortex 設計中に記録):外部の Anthropic Haiku API 呼び出しではなく、Claude Code subagent を使用する。理由:

- **外部 API コストなし** — subagent は同じ Claude Code セッション内で動作し、別個の Haiku API アカウントではなく、ユーザーがすでに支払い済みの Claude プラン予算を消費します。
- **Cortex の限界費用の合計 ≈ 月 $0.20-0.50**(ユーザー決定 #8 予算範囲)。hippocampus(~$0.05-0.10 / 呼び出し) + GWT arbitrator(~$0.01-0.03) + narrator-validator(~$0.01-0.02)に分散します。具体的な数字は v1.7 本番で校正されます。この範囲はハードコントラクトではなくターゲットです。
- **API キー管理なし** — 外部プロビジョニング、ローテーション、予算なし。
- **Life OS スタンスと一貫性がある** — すべての知性はセッション内部で動作します。Haiku API 依存はそれに違反します。
- **十分に高速** — sonnet は引用検証に十分です。レイテンシはパフォーマンス予算内に収まります(§11)。

validator サブエージェントは `Read` のみを持ちます。ファイルの書き込み、MCP ツールの呼び出し、ネットワークへの接続は行いません。

---

## 8. 検証アルゴリズム(Validation Algorithm)

### 入力

validator は以下を受け取ります:

- `narrator_output` — ROUTER の Step 7.5 書き直しで生成された、インライン引用付きの完全な markdown ドキュメント。
- `signal_sources` — 現在のセッションの signal source レジストリ(§9)。

### 手順

`narrator_output` 内の各文について:

1. §3 のルールを使用して文を **substantive** または **connective** として分類する。
2. connective → スキップ。
3. substantive の場合:
   1. 文からすべてのインライン引用 `[signal_id]` を抽出する。
   2. 各引用について:
      1. prefix(S、D、SOUL、C、W、P)をパースする。prefix が不明 → `format_error`。
      2. `signal_sources` で `signal_id` を検索する。欠落 → `missing_signal`。
      3. 参照先のコンテンツ(ファイル / フィールド / dimension)を読み、文の主張がそのコンテンツによってサポートされていることを検証する。コンテンツが主張をサポートしない場合 → `unsupported_claim`。
4. 文が substantive だが **zero** の引用を持つ場合 → `missing_signal`("no citation" としてタグ付け)。

### 出力

```yaml
validation:
  total_citations: integer
  valid: integer
  invalid:
    - position: char_offset_in_narrator_output
      citation: string          # the raw "[signal_id]" token, or "" if missing
      reason: missing_signal | unsupported_claim | format_error
      claim_text: string        # the sentence that contains the problem
  groundedness_score: float     # 0.0–1.0
```

### Groundedness スコア

```
groundedness_score = valid / max(total_citations + missing_citation_count, 1)
```

ここで `missing_citation_count` は、引用ゼロの substantive 文の数です。

### しきい値

narrator 出力を出荷するには `groundedness_score ≥ 0.9` が必要です。しきい値を下回る場合 → narrator はエラーフィードバックとともに再生成します(§10)。

---

## 9. シグナルソースレジストリ(Signal Source Registry)

セッション実行中、各サブエージェントは ID 付きのシグナルを emit します。narrator は Step 7.5 でレジストリを受け取ります。

### レジストリフォーマット

```yaml
signal_sources:
  - id: S:claude-20260419-1238
    type: session
    file: _meta/sessions/claude-20260419-1238.md
    producer: hippocampus
  - id: SOUL:risk-tolerance-v3
    type: soul_dimension
    ref: SOUL.md#risk-tolerance
    producer: soul_check
  - id: C:method:iterative-document-refinement
    type: concept
    file: _meta/concepts/method/iterative-document-refinement.md
    producer: concept_lookup
  - id: D:GOVERNANCE-score-5
    type: domain_score
    value: 5
    producer: governance_agent
  - id: W:finance/compound-interest
    type: wiki
    file: wiki/finance/compound-interest.md
    producer: wiki_index
  - id: P:avoids-family-topic-on-weekends
    type: pattern
    ref: _meta/user-patterns.md#avoids-family-topic-on-weekends
    producer: retrospective
```

### レジストリの構築

レジストリは ROUTER が Step 7.5 の前に組み立てます:

1. Hippocampus、SOUL check、concept lookup シグナル → Step 0.5 で追加。
2. ドメインスコアシグナル → 各ドメインが Step 5 でレポートする際に追加。
3. COUNCIL 審議シグナル → COUNCIL が Step 6 でトリガーされた場合に追加。
4. Wiki / pattern 参照 → DISPATCHER が "known premises" として与えた場合に追加。

レジストリはセッション中は append-only です。シグナルはセッション途中で削除されることはありません。

---

## 10. 再生成プロトコル(Regeneration Protocol)

validator が `groundedness_score < 0.9` を返した場合:

1. validator は `regeneration_feedback` を emit します:
   - 有効な引用を欠く特定の主張。
   - サポートされていない主張ごとに引用すべき `signal_id` の候補(レジストリから)。
   - 任意のフォーマットエラー。
2. narrator (ROUTER) はフィードバックを受け取り、出力を再生成します。推奨された引用を組み込むか、サポートするシグナルが存在しない場合は **主張を削除** します。
3. 最大 **3 回の再生成試行**。
4. 使い切った場合:
   - **引用なしの Summary Report**(Step 7 の raw 出力、書き直しではない)にフォールバック。
   - AUDITOR フラグ `narrator_failed_after_3_attempts` を emit。
   - 後のレビューのために `_meta/eval-history/` に失敗をログ。

ユーザーは依然としてレポートを受け取ります。そのレポートは単に narrate が少ないだけです。

---

## 11. パフォーマンス予算(Performance Budget)

| Stage                          | 予算        |
|--------------------------------|---------------|
| Narrator generation (first pass) | 2–5 秒   |
| Validator scan (single pass)   | 1–3 秒   |
| Regenerate + revalidate cycle (per attempt) | 3–8 秒  |
| **Total worst case (3 retries)** | **18 秒(typical) / 21 秒(max)** |

算術(Arithmetic): 初回の generate + validate パス 1 回(2–5 秒 + 1–3 秒 = 3–8 秒)に加えて、regenerate + revalidate サイクルが最大 3 回、各 3–8 秒。Typical 合計 ≈ 18 秒(中央値 6 秒 × 3 サイクル + リトライ時の初期変動 0 秒)。Maximum 合計 = 21 秒(最悪ケースの初回 8 秒 + 3 回の 4.33 秒リトライ、あるいは再生成上限で抑えられた等価な分配)。

Narrator generation は ROUTER の通常の構成の一部であり、別個のネットワークラウンドトリップではありません。Validator のレイテンシは `references/cortex-spec.md` の Cortex レイテンシ予算内に収まります。**いずれか** のトリガが発火した場合、narrator は引用なしの出力にフォールバックします(§10 の使い切り時と同じフォールバック):

- 累積 wall-clock が **21 秒** を超える、あるいは
- 単一の regenerate-and-revalidate サイクルが **8 秒** を超える。

---

## 12. 品質メトリクス(Quality Metrics)

narrator は eval-history のために AUDITOR に 2 つのメトリクスを供給します:

- `citation_groundedness` (0–10) — `groundedness_score × 10` からスケール。
- `regeneration_count` — narrator が合格するまでの試行回数(0、1、2、または 3)。

**ターゲット** — v1.7 安定化後の `citation_groundedness ≥ 9`。Full Deliberation セッションの 80% 超で `regeneration_count = 0`。

**AUDITOR 退行** — `citation_groundedness < 7` のセッション → quality incident。`regeneration_count > 1` の週次トレンド → narrator drift。

ログとレビューについては `references/eval-history-spec.md` を参照。

---

## 13. エッジケース(Edge Cases)

### ROUTER による Direct-handle(サブエージェントが spawn されない)

ROUTER がユーザーのメッセージを直接処理する場合 — カジュアルなチャット、翻訳、メモ取り、単純なクエリ — サブエージェントは spawn されず、シグナルレジストリは実質的に空です。

動作: narrator は **trivial pass-through(自明なパススルー)**。書き直し、検証、Step 7.5 なし。ROUTER は直接応答を emit します。

### Express analysis(PLANNER / REVIEWER をスキップ)

Express パス(Step 1E)は Summary Report ではなく **brief report** を生成します。hippocampus シグナル(Step 0.5 から)と場合によっては SOUL check シグナルを持ちますが、完全審議からのドメインスコアシグナルは持ちません。

動作: express セッションのレジストリには hippocampus / SOUL / concept 引用のみが含まれるため、narrator は **それらの引用のみを検証** します。ドメインスコア引用は期待されません。

### STRATEGIST セッション(純粋な哲学、意思決定なし)

STRATEGIST セッションは歴史上の思想家との open-ended な対話です。Summary Report もドメインスコアもありません。

動作: narrator は **呼び出されません**。STRATEGIST サブエージェントは自身の出力を生成し、ROUTER はそれを書き直しや引用なしで中継します。

### Full Deliberation にもかかわらずレジストリが空

Full Deliberation が実行されたがレジストリが予期せず空(シグナルプロデューサの失敗)の場合、narrator は §10 の使い切り時と同じように動作します: 引用なしの Summary Report にフォールバックし、AUDITOR をフラグします。

---

## 14. アンチパターン(Anti-patterns)

- **「明白」な主張に対して引用をスキップしない。** 「あなたのプロジェクト X」でさえ `P:` または `S:` 引用が必要です。「明白」とは、作話が隠れる場所そのものです。
- **曖昧なカテゴリを引用しない。** `[S:recent-sessions]` は有効ではありません。単一のファイルまたはフィールドに解決する特定の signal_id を使用してください。
- **事後的にシグナルを生成しない。** シグナルは、通常のワークフロー中にそれを所有するサブエージェントによって生成されなければなりません。narrator が主張を裏付けるためにシグナルをでっち上げることはできません。
- **validator をバイパスしない。** "trust me" モードはありません。検証を無効化するユーザーフラグはありません。
- **サポートされないパターンを主張しない。** "You always do Y" には ≥ 3 引用が必要。"you sometimes do Y" には少なくとも 1 つ。"you might do Y" は推測であり、許可されません。
- **引用 prefix を混在させたりでっち上げたりしない。** 有効なのは `S:`、`D:`、`SOUL:`、`C:`、`W:`、`P:` のみ。prefix をまたいでシグナルをリラベルすることは決してありません。
- **Summary Report 自体を引用しない。** narrator は Summary Report の書き直しです。それをシグナルとして引用するのは循環的です。

---

## 15. ユーザー意思決定監査証跡(User Decision Audit Trail)

Grounded なシステムは inspectable でなければなりません。ユーザーは次のように尋ねることができます: *"主張 X の背後にあるシグナルを見せて。"* システムは引用された `signal_id`、ソースファイルパス(またはフィールド / dimension 参照)、および主張をサポートするコンテンツスニペットで応答します。

例:

```
User: What's the signal behind "Your past passpay-v06-refinement session
shows a similar 5-round iteration pattern"?

System:
- Signal: S:claude-20260419-1238
- Source: _meta/sessions/claude-20260419-1238.md
- Snippet: "Session ran 5 revision rounds on payment gateway spec. Each
  round tightened governance controls. Final GOVERNANCE score 5/10 due
  to incomplete fraud-response plan."
```

これが、Life OS を Gazzaniga スタイルの作話から分離するものです。任意の narrator 出力は、それを生成したシグナルにトレースできます。

ユーザーが connective な文の背後にあるシグナルを求めた場合、システムは応答します: *"That was connective tissue, not a grounded claim. Nothing to cite."*

---

## 16. 関連仕様(Related Specs)

- `references/cortex-spec.md` — Cortex 全体アーキテクチャ
- `references/hippocampus-spec.md` — セッション検索と `S:` シグナル生成
- `references/gwt-spec.md` — シグナル仲裁とブロードキャスト
- `references/eval-history-spec.md` — `citation_groundedness` がどうログされるか
- `references/concept-spec.md` — `C:` prefix で引用される concept ID
- `references/wiki-spec.md` — `W:` prefix で引用される wiki エントリ
- `references/soul-spec.md` — `SOUL:` prefix で引用される SOUL dimension
- `references/session-index-spec.md` — `S:` prefix で引用されるセッション
- `pro/agents/router.md` — narrator の構成は ROUTER の内部に存在する(本 spec §6)

---

## 17. Trace UX · ユーザー向け監査証跡(Trace UX · User-Facing Audit Trail)

Grounded generation は、ユーザーがそれを inspect できる場合にのみ有用です。このセクションは、トレースリクエストがどのように処理されるかを定義します — narrator layer がユーザーに対して負う UX コントラクトです。

### 17.1 トリガー形式

3 つの自然言語トリガーパターン:

1. **Full trace request(完全なトレースリクエスト)** — ユーザーが "why did you say X?" / "trace this" / "这句话怎么来的" / "根拠は?" と言う。
2. **Specific citation inspection(特定引用の検査)** — ユーザーが Summary Report から特定の `[signal_id]` を参照する: "show me `S:claude-20260419-1238`" / "S:claude-20260419-1238 是什么"
3. **Category overview(カテゴリ概観)** — ユーザーが主張のカテゴリを何が駆動したかを尋ねる: "which SOUL dimensions influenced this?" / "list all past sessions that contributed"

ROUTER は intent 分類でこれらを検出します(ROUTER はすでにユーザー入力をパターンマッチしています。トレーストリガーはもう 1 つのパターンファミリを追加します)。

### 17.2 Trace 出力フォーマット

単一の主張に対する完全なトレースリクエスト用:

```
📎 Trace for: "Your past passpay-v06-refinement session shows a similar 5-round iteration pattern"

Cited signals:
1. S:claude-20260419-1238
   Source: _meta/sessions/claude-20260419-1238.md
   Content match: "Session ran 5 revision rounds on payment gateway spec.
     Each round tightened governance controls. Final GOVERNANCE score
     5/10 due to incomplete fraud-response plan."
   Produced by: hippocampus (Step 0.5 Wave 1)

2. D:passpay-governance-score
   Source: session D-scores extracted by ROUTER at Step 7
   Value: 5 (threshold for flag: < 6)
   Produced by: governance_agent

Confidence: groundedness_score = 1.0 (both citations resolve, content supports claim)
```

特定引用の検査では、同じブロックを表示しますが、リクエストされた signal_id のみに対してです。

カテゴリ概観の場合:

```
📎 Category trace: SOUL dimensions that influenced this Summary Report

1. SOUL:risk-tolerance-v3 (core, confidence 0.82)
   Referenced by: narrator (×2), governance_agent (×1)
   Source text: SOUL.md § Risk attitude

2. SOUL:evidence-discipline (secondary, confidence 0.61)
   Referenced by: narrator (×1), execution_agent (×1)
   Source text: SOUL.md § Evidence discipline

3. [...]
```

### 17.3 Trace データソース

トレースは以下から組み立てられます:

- 現在のセッションコンテキストで保持される **signal source registry**(§9)
- 引用されたパスに対するファイル読み込み(validator サブエージェントまたは ROUTER が `Read` ツールを使用)
- トレース本体内には LLM generation なし — トレースは literal な抜粋 + メタデータです。これは再帰的な作話(「トレースがトレースを説明するトレースを説明する…」)を防ぎます

引用されたシグナルがトレース時に解決できない場合(ファイル削除、frontmatter 変更)、トレース行は元の引用を保持したまま `⚠️ signal no longer resolvable` を表示します。

### 17.4 Connective-tissue 応答

ユーザーが validator が **connective** に分類した文(§3)のトレースを求めた場合:

```
That sentence is connective tissue (a transition / framing / rephrasing),
not a grounded claim. No signal stands behind it. If you want to trace a
substantive claim in the same report, let me know which one.
```

これは、真理主張を意図的に担わない文を裏付けるためにシステムがシグナルをでっち上げようとする作話ループを防ぎます。

### 17.5 4 言語テーマシステムにおける Trace

トレース出力は、アクティブなテーマの言語(en / zh / ja)でレンダリングされます。シグナル ID の prefix(`S:` `D:` `SOUL:` `C:` `W:` `P:`)は literal のまま — これらは技術的識別子であり、ローカライズされたテキストではありません。説明的な段落のみが翻訳されます。

### 17.6 Trace はログされない

トレースリクエストは ephemeral(一時的)です。journal に書き込みを **しません**、AUDITOR メトリクスにカウントされ **ません**、何も変更し **ません**。ユーザーは副作用なしに同じトレースを 10 回求めることができます。

根拠: トレースは inspection ツールであり、意思決定を生成するアクションではありません。すべてのトレースリクエストをログすると、journal が肥大化し、真の意思決定履歴が不明瞭になります。

### 17.7 パフォーマンス予算

トレースリクエストは < 2 秒で返されなければなりません(トレースは単一セッション、読み取り専用、本体に LLM generation なしであるため、narrator 予算より厳しい)。トレースリクエストが 2 秒を超える場合、何かが間違っています — おそらく引用されたシグナルが巨大ファイルを指しています。実装はマッチポイントの周囲 500 行のウィンドウにファイル読み込みを切り詰める必要があります。

---

**Spec status**: draft for v1.7。narrator validator サブエージェントが出荷され、`citation_groundedness` データの最初の 1 週間がレビューされた時点で最終化されます。Trace UX(§17)は実セッションデータとの統合テストを必要とします。フォーマットは v1.7 アルファ中のユーザーフィードバックに基づいて調整される可能性があります。

---

> ℹ️ **2026-04-22 更新**:EN R3.1 §11 予算算術の修正を同期

*訳注: 本文は英語版 2026-04-22 スナップショットの翻訳。英語版が権威源で、曖昧な場合は英語版が優先。*
