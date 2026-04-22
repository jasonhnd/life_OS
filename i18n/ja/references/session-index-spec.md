---
translated_from: references/session-index-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# Session Index 仕様書(Session Index Specification)

Session index は Cortex の hippocampus(クロスセッション検索)のデータソースです。2 つのアーティファクトが生成され、writer(archiver)と compiler(retrospective)の間に厳格な分離があります。

## 1. 目的(Purpose)

session index は、hippocampus サブエージェントがベクトルデータベース、SQLite、またはいかなる非 markdown ランタイムなしに、メッセージごとのクロスセッション検索を実行できるようにするために存在します。`devdocs/architecture/cortex-integration.md` §3.1 に従い、検索はコンパイルされたプレーンテキストインデックス上の LLM 駆動です — スキャンが速く、再生成が安く、完全に markdown-first です。

2 つのアーティファクトが役割を担います:

- **`INDEX.md`** — セッションごとに 1 行、retrospective が Start Session でコンパイル。これは hippocampus が最初に読む fast-scan の表面です。
- **`{session_id}.md`** — YAML frontmatter 付きの構造化されたセッションサマリー、archiver がセッションクローズで書き込む。`INDEX.md` が候補セットを絞り込んだ後に hippocampus によってロードされる。

この 2 tier 設計は脳のアナロジーに一致します: `INDEX.md` は「セッションの gist(要旨)」であり、`{session_id}.md` は「完全な episodic trace」です。hippocampus は最初に gist をスキャンし、次にオンデマンドで trace を取得します。

## 2. ファイルの場所(File Locations)

```
_meta/sessions/
├── INDEX.md                    # retrospective(Mode 0、Start Session)でコンパイル
└── {session_id}.md             # archiver(Phase 1、セッションクローズ)で書き込み
```

**session-id フォーマット**: `{platform}-{YYYYMMDD}-{HHMM}`

例:
- `claude-20260419-1238`
- `gemini-20260420-0915`
- `codex-20260420-1403`

**HARD RULE**(v1.4.4b から継承): archiver は実際のタイムスタンプを取得するために `date` コマンドを実行 MUST。タイムスタンプの捏造はプロセス違反です。archiver はすでに Phase 1 Step 2 でこれを強制しています — session index はその session-id をファイル名として再利用します。

## 3. セッションサマリースキーマ(`{session_id}.md`)(Session Summary Schema)

archiver はセッションごとに正確に 1 つのファイルを書きます。ファイルは書き込み後 immutable です。

### YAML Frontmatter(完全スキーマ)(Complete Schema)

```yaml
---
session_id: string                      # 必須、フォーマット {platform}-{YYYYMMDD}-{HHMM}
date: ISO 8601 date                     # YYYY-MM-DD
started_at: ISO 8601 timestamp          # タイムゾーン付き
ended_at: ISO 8601 timestamp            # タイムゾーン付き
duration_minutes: integer
platform: claude | gemini | codex
theme: en-roman | en-us-gov | en-corporate | zh-classical | zh-cn-gov | zh-corporate | ja-meiji | ja-kasumigaseki | ja-corporate
project: string                         # バインドされたプロジェクトスコープ; セッションバインディング HARD RULE がこれを強制
workflow: full_deliberation | express_analysis | direct_handle | strategist | review
subject: string                         # intent clarification 中に抽出、最大 200 文字
domains_activated:                      # 6 つの domain のうちどれが走ったか
  - PEOPLE
  - FINANCE
  - GROWTH
  - EXECUTION
  - GOVERNANCE
  - INFRA
overall_score: float                    # 0-10、Summary Report から
domain_scores:
  FINANCE: float
  GOVERNANCE: float
  # ...走った domain のみ含める
veto_count: integer                     # REVIEWER 拒否権イベント(初回パスで承認なら 0)
council_triggered: boolean              # COUNCIL 議論が発火?
soul_dimensions_touched:                # REVIEWER によって参照または ADVISOR によって更新された次元
  - string
wiki_written:                           # このセッションで自動書き込みされた wiki エントリ ID
  - entry_id
methods_used:                           # method library から適用された method ID
  - method_id
methods_discovered:                     # archiver によって追加された新規 method
  - method_id
concepts_activated:                     # セッション中に参照された concept ID
  - concept_id
concepts_discovered:                    # archiver Phase 2 によって書き込まれた新規 concept
  - concept_id
dream_triggers:                         # Phase 3 REM で発火したトリガー名
  - trigger_name
keywords:                               # 最大 10、hippocampus Wave 1 スキャン用
  - string
action_items:
  - text: string
    deadline: ISO 8601 date
    status: pending | completed | dropped
compliance_violations: integer          # AUDITOR がフラグした違反、クリーンなら 0
---
```

### 本文(Body)

本文は短く、構造化され、人間が読めるものです。raw メッセージコンテンツはありません。

```markdown
## Subject

{1 段落の拡張された subject。これは「このセッションが何についてだったか」の答えです。
自立していなければなりません — この段落のみを見た読者がセッションの
スコープを理解できるべきです。最大 500 文字。}

## Key Decisions

1. {Decision one — 1 文、行動志向}
2. {Decision two}
3. {Decision three}

## Outcome

{何が決定されたまたは達成されたかの 1 段落サマリー。Summary Report からの
全体評価を含める。最大 400 文字。}

## Notable Signals

- {narrator レイヤーが将来の参照用に重要とマークしたもの}
- {archiver が surface したクロスセッションパターン}
- {再訪する価値のある未解決の緊張}
```

**本文ルール**:
- 生のメッセージ引用なし
- PII なし(名前、金額、口座番号)— archiver の Phase 2 プライバシーフィルターに従う
- どのエージェントからも thinking-process ダンプなし

## 4. INDEX.md フォーマット(INDEX.md Format)

セッションごとに 1 行、最新が最初、月ごとにグループ化。これは hippocampus のスキャン表面です。

### 行フォーマット(Line format)

```
{date} | {project} | {subject-truncated-80chars} | {overall_score}/10 | [{keywords-top3}] | {session_id}
```

### 例(Example)

```markdown
# Session Index

## 2026-04

2026-04-19 | passpay | Technical whitepaper v0.5 to v0.6 refinement | 8.2/10 | [whitepaper, refinement, evidence] | claude-20260419-1238
2026-04-17 | life-os | v1.6.2 SOUL auto-write and DREAM 10 triggers design | 9.1/10 | [architecture, soul, dream] | claude-20260417-0902
2026-04-15 | passpay | Go-to-market positioning for Q3 launch | 7.8/10 | [gtm, positioning, launch] | claude-20260415-1510

## 2026-03

2026-03-28 | ledger-io | Schema migration risk review | 8.0/10 | [schema, migration, risk] | claude-20260328-1143
2026-03-22 | life-os | Theme system expansion to 9 themes | 8.6/10 | [theme, i18n, design] | claude-20260322-0834
```

### フォーマットルール(Formatting rules)

- 月見出し `## YYYY-MM` — ジャンプナビゲーションと将来のシャーディングを可能にする
- 月内のセッションは `date desc` でソート(最新が最上部)
- `subject` を 80 文字に切り詰め、切り詰めた場合は省略記号を付加
- Keywords は括弧内のカンマ区切りリストで表示、最大 3(完全な keyword セットはセッションサマリーに存在)
- 末尾の空白なし; 月セクション間に 1 つの空行

## 5. 書き込みフロー(Write Flow)

### セッションサマリー作成(archiver Phase 1 が session-id を生成; Phase 2 がファイルを書く)

archiver は書き込みの両端を所有します。session-id 生成は **Phase 1** に残ります(セッションクローズで実際の `date` 呼び出しが必要)。**ファイル書き込みは Phase 2 の最後に移動** します。なぜなら、サマリーの YAML frontmatter は Phase 2 の出力(`wiki_written`、`methods_used`、`methods_discovered`、`concepts_activated`、`concepts_discovered`)を参照し、それらは Phase 1 実行時にはまだ存在しないからです。Phase 2 のステップリストについては `references/cortex-spec.md` Step 10 を参照。

```
Phase 1:
1. セッション終了 → orchestrator が archiver サブエージェントを起動
2. archiver Phase 1 が実際の `date` コマンド経由で session-id を生成
3. archiver はすでに集められるメタデータをステージ:
   - タイムスタンプ(started_at / ended_at / duration_minutes)
   - orchestrator のトレースからの workflow タイプ
   - Summary Report からの domain scores と overall_score
   - AUDITOR トレースからの veto_count と council_triggered
   - ADVISOR レポートからの SOUL dimensions touched
   - 発火した DREAM triggers(Phase 3 triggered_actions YAML ブロックから — Phase 3 は Phase 2 より前に走る)

Phase 2(wiki/SOUL 自動書き込み、concept 抽出 + Hebbian 更新、
method-candidate 検出、SYNAPSES-INDEX 再生成、SOUL スナップショットダンプの後):
4. archiver が Phase 2 出力をステージされたメタデータにポピュレート:
   - wiki_written エントリ(wiki 自動書き込みから)
   - methods_used、methods_discovered(method-candidate 検出から)
   - concepts_activated、concepts_discovered(concept 抽出から)
5. archiver が keywords を抽出(§7)— 最大 10
6. archiver が _meta/outbox/{session_id}/sessions/{session_id}.md を書き込む
7. ファイルは他のセッションアーティファクトと並んでアトミックな git commit 用に outbox ディレクトリに追加される
```

**Immutability(不変性)**: archiver がファイルを書いたら、決して再編集されません。修正が必要な場合(まれ)、元のものを変更するのではなく `corrections/{session_id}.md` ノートを追加します。これは journal エントリの不変性と並行します — append-only、決して書き直されない。

**outbox 下の配置**: archiver の Phase 1 中、新規ファイルは最初に `_meta/outbox/{session_id}/sessions/{session_id}.md` に着地します。outbox マージ(retrospective Mode 0 Step 7)がそれを canonical な `_meta/sessions/{session_id}.md` の位置へ移動します。これは decision、task、journal エントリの既存の outbox パターンにマッチします。

**失敗モード(Failure modes)**:

- `date` コマンドが利用不可(極めてまれ)→ archiver は明確なエラーで Phase 1 を停止; セッションは実際のタイムスタンプなしに安全にアーカイブできない
- Outbox ディレクトリへの書き込みが失敗(ディスクフル、権限)→ archiver は `_meta/sync-log.md` にログ、セッションサマリーファイルは作成されず、その後の retrospective コンパイルステップはそのセッションを INDEX から単に省略
- 部分的な frontmatter(例: Summary Report が欠けている)→ archiver は必須フィールドをセンチネル値(`overall_score: null`、空配列)で埋め、続行; retrospective のパーサーは null スコアを INDEX で `n/a` として扱う

### INDEX コンパイル(retrospective Mode 0)(INDEX compilation)

retrospective はコンパイルします — セッションごとのファイルは書きません。既存の Mode 0 フロー(`pro/agents/retrospective.md` 参照)を拡張:

```
1. Start Session がトリガー
2. retrospective が _meta/sessions/*.md を列挙(glob パターン: INDEX.md を除く *.md)
3. 各ファイルについて、YAML frontmatter をパース — 抽出:
   - date
   - project
   - subject(80 文字に切り詰め)
   - overall_score(null なら n/a としてレンダー)
   - keywords(最初の 3 つ)
   - session_id
4. date desc でソート(セカンダリソート: 同日タイブレーカーに started_at desc)
5. date フィールドから派生した YYYY-MM でグループ化
6. _meta/sessions/INDEX.md をコンパイルされた出力で上書き
7. コンパイルが構造的に異なる出力を生成した場合、
   retrospective の Start Session レポートに差分サイズをノート("📚 Session Index: N sessions indexed")
```

**コンパイルは冪等(idempotent)**。2 回走らせるとバイト単位で同一の出力を生成します(同じ入力ファイルで)。これは重要です、なぜなら retrospective は Start Session ごとに走るからです — インクリメンタルロジックは不要です。冪等性はデバッグも簡素化します: インデックスが間違って見える場合、削除して再コンパイルしてもデータは失われません。

**パース失敗**: `{session_id}.md` ファイルの YAML が不正形式の場合、retrospective はファイル名を `_meta/sync-log.md` にログし、続行します。破損したセッションは INDEX から省略されますが、ファイル自体は手動検査用に保持されます。これは v1.6.2 のスナップショット破損に対する姿勢にマッチします — gracefully 劣化し、決して Start Session ブリーフィングをブロックしない。

## 6. 読み取りフロー(Hippocampus)(Read Flow)

hippocampus サブエージェントは session index を消費します。`devdocs/architecture/cortex-integration.md` §3.1 と 3 波アクティベーションモデルに従い:

```
1. Hippocampus がユーザーの現在の subject を受け取る(Step 0.5 から)
2. Hippocampus が _meta/sessions/INDEX.md を読む(1 ファイル、速い)
3. LLM 判断がトップ 5-7 の意味的に関連するセッションを識別
   - Wave 1: keywords 列に対する直接キーワードマッチ
   - Wave 2: subject への意味的近接(80 文字の subject 短文に対する LLM 判断)
   - Wave 3: 強い synapse 近傍からの sub-threshold アクティベーション(concept グラフが利用可能な場合)
4. 選択された各セッションについて、hippocampus が完全な {session_id}.md を読む
5. GWT arbitrator に concept レベルのサマリーを返す(ROUTER に直接ではない)
```

**メッセージごとの読み取り予算**: 1 回の `INDEX.md` 読み取り(常に)+ 最大 7 回の `{session_id}.md` 読み取り(生き残った候補のみ)。典型的なサイズで、これはメッセージごとに <50KB のコンテキストを消費し、§8 のスケール目標で <3 秒の LLM スキャン時間です。

**このアーキテクチャが意図的に使わないもの**(cortex brainstorm からのユーザー決定 #3):

- **No embeddings** — 意味的類似度は LLM 判断であり、ベクトル計算ではない。これは embedding モデルドリフト、embedding プロバイダロックイン、およびスキーマ変更ごとに re-embed する必要性を回避します。
- **No FTS5 or any database** — markdown-first HARD RULE(`docs/architecture/markdown-first.md` 参照)。すべての検索基質はプレーンテキストかつ git バージョン管理されている。
- **No background indexing daemon** — インデックスは Start Session でのみコンパイルされる; 読み取りはメッセージごとだが markdown I/O に限定される。cron なし、watchdog なし、長時間実行プロセスなし。

パフォーマンス計算(§8 参照)は、シャーディングが必要になる前にこれが数千セッションまで十分スケールすることを確認します。

**Failure fallback**: hippocampus が `INDEX.md` を読めない場合(ファイル欠損、破損、空)、`confidence: 0` で空のシグナルを GWT arbitrator に返し、ワークフローは v1.6.2a の動作に劣化します — ROUTER はクロスセッション注釈なしの raw ユーザーメッセージを見ます。これは `devdocs/architecture/cortex-integration.md` §5 Phase 1 kill-switch 設計の Cortex 劣化ポリシーにマッチします。

## 7. Keyword 抽出ルール(Keyword Extraction Rules)

Keywords は hippocampus の Wave 1 フィルターです。archiver Phase 1 はこの手続きで最大 10 個の keywords を選択:

1. **プロジェクト名** — 常に含める(1 スロット)
2. **Domain 名** — `domains_activated` からの各エントリを含める(最大 6 スロット)
3. **Subject 内容語** — LLM が subject 文字列からトップ 3 の内容語を抽出; ストップワード、動詞、一般的な名詞を除外(最大 3 スロット)
4. **新規 concepts** — `concepts_discovered` から最大 3 エントリを含める(最大 3 スロット)
5. **合計キャップ** — 最大 10 keywords。ステップ 1-4 で 10 を超える場合、次の順で drop: 新規 concepts(最古から)、subject 単語(最低 salience から)、domain 名(最低スコアから)。プロジェクト名は決して drop されない。

**出力形状**: 小文字の文字列、keyword 内にスペースなし(ハイフンを使用)、各カテゴリ内でアルファベット順。例: `[passpay, finance, governance, whitepaper, refinement, evidence, zk-proof]`。

## 8. スケール制限(Scale Limits)

パフォーマンスはこの設計の load-bearing です — hippocampus はすべてのユーザーメッセージで走ります。スケール予算は `docs/architecture/markdown-first.md` §2 にマッチします:

| セッション数 | INDEX.md サイズ | LLM スキャン時間 | 決定 |
|---------------|----------------|---------------|------------------------------------------------|
| 500 | ~500 行、30KB | <3 秒 | 高速スキャン、最適化不要 |
| 2000 | ~2000 行、120KB | ~10 秒 | まだ管理可能、テールレイテンシを監視 |
| 5000+ | ~5000+ 行、300KB+ | >10 秒 | INDEX を年でシャード; データベース議論をトリガー |

**シャーディングトリガー**: `INDEX.md` が 300KB に近づくとき、`INDEX-{YYYY}.md` ファイル(年ごとに 1 つ)+ それらへのリンクを持つ `INDEX.md` マニフェストを導入。hippocampus はその後、現在の年を最初に読み、Wave 1 が失敗した場合のみ以前の年を読む。

**データベースエスカレーショントリガー**: シャーディングが極端なスケール(年あたり数百セッション、Wave 1 ヒット率低下)でスキャンレイテンシを 10 秒以下に戻さない場合、明示的な決定のためにユーザーに surface。v1.7 はデータベースを自動導入しません; markdown-first ルールはユーザーが明示的に別の選択をしない限り保持されます。

## 9. v1.6.2a からのマイグレーション(Migration from v1.6.2a)

v1.7 以前は `_meta/sessions/` ディレクトリは存在しません。マイグレーションは best-effort かつ一度限りです、cortex brainstorm からのユーザー決定 #7 に従い:

`tools/migrate.py` は直近 3 ヶ月の `_meta/journal/` をスキャン:

```
1. 直近 90 日に作成された _meta/journal/*.md を列挙
2. 各 journal エントリについて:
   a. メタデータをパース(date、project、decision タイトル)
   b. YAML frontmatter を合成 — best-effort、ギャップを認める:
      - overall_score: 存在すれば Summary Report 見出しから抽出、なければ null
      - domain_scores: 存在すれば Summary Report テーブルから抽出、なければ空
      - veto_count、council_triggered: トレースセクションをパース、デフォルト 0/false
      - soul_dimensions_touched、wiki_written、methods_used: 空のまま
        (pre-v1.7 セッションはこれらを生成しなかった)
      - concepts_activated、concepts_discovered: 空のまま(v1.7 のみ)
      - dream_triggers: タイムスタンプマッチなら -dream.md journals から抽出
      - keywords: decision タイトル + project からの LLM 抽出
   c. decision サマリーと outcome 行から本文セクションを合成
   d. _meta/sessions/{synthesized-session-id}.md を書き込む
3. すべてのファイルを書き込んだ後、_meta/sessions/INDEX.md を再コンパイル
```

**マイグレーションされたエントリの session-id**: journal の変更タイムスタンプを使った `{platform}-{YYYYMMDD}-{HHMM}`。元のプラットフォームが推論できない場合、`claude` にデフォルト。

**3 ヶ月より古いセッションはバックフィルされません**。ユーザー決定 #7 はこれを検索価値の逓減として重み付けしました — セッションが 3 ヶ月以上古くなる頃には、検索ターゲットとしての価値は限界的であり、合成品質は低くなる(pre-v1.7 journal はスキーマが期待する構造化フィールドを欠いている)。

マイグレーションは冪等: 2 回走らせると同じ session-id の以前にマイグレーションされたファイルを上書きするので、再実行は安全。

## 10. Anti-patterns

してはならないこと:

- **既存のセッションサマリーファイルを編集する** — archiver 書き込み後は immutable。修正は `corrections/{session_id}.md` に存在。セッションサマリーを変更することは、元のものから読む下流の分析(トレンドレポート、DREAM 時代のパターン検出)を無効化します。
- **Keyword 抽出をスキップする** — keywords がゼロのセッションは hippocampus Wave 1 スキャンに不可視。Phase 1 archiver は常に少なくとも 1 つの keyword(プロジェクト名フォールバック)を生成しなければならない。
- **archiver 中に INDEX をコンパイルする** — コンパイルは retrospective の仕事。責任を分割すると、2 つのプラットフォームが同時にセッションをクローズするときに競合状態が生じ、adjourn レイテンシがコンパイルコストに結合する。
- **セッションサマリーに生のメッセージコンテンツを含める** — 構造化された抽出のみ(subject、key decisions、outcome、signals)。生のメッセージは `_meta/journal/` に属し、ここではない。検索焦点のサマリーは journal エントリより短くあるべきで、そのコピーではない。
- **`_meta/sessions/` を Notion に同期する** — ユーザー決定 #12 に従い、Cortex データはローカルに留まる。Notion はユーザーのモバイルフレンドリーなビュー(STATUS、Todo、Working Memory、Inbox)を保持する; 認知基質は保持しない。
- **archiver に session-id 生成をリトライさせる** — `date` HARD RULE はセッションあたり 1 つの `date` 呼び出しを意味する。リトライはファイル名と `started_at` タイムスタンプの間のドリフトのリスク。
- **INDEX をインクリメンタルにコンパイルする** — 常に上書き。冪等性は設計特性; 小さなパフォーマンスゲインのためにトレードしない。
- **ソートにファイル修正時刻に頼る** — `date` frontmatter フィールドでソート。ファイル mtime は git 操作またはクロスデバイス同期後にドリフトできる。
- **§3 スキーマにない任意のメタデータを埋め込む** — 新しいシグナルが追跡する価値がある場合、この仕様と archiver を一緒に更新。自由形式の frontmatter 拡張は retrospective のパーサーを破壊し、エージェント間のサイレントドリフトを生む。
- **`{session_id}.md` を journal の代替として扱う** — journal エントリはロールごとの詳細なレポート(AUDITOR、ADVISOR、dream)を記録する; セッションサマリーは検索ベイト。両者は共存する。
- **プラットフォームごとに異なる session-id フォーマットを使う** — スキーム `{platform}-{YYYYMMDD}-{HHMM}` は claude / gemini / codex で固定。プラットフォーム固有のプレフィックスは最初のセグメントにエンコードされ、フォーマット自体ではない。

## 11. クロスプラットフォームと並行性(Cross-Platform and Concurrency)

Life OS は Claude、Gemini、Codex で、そしてユーザーあたり複数のデバイスで走ります。session index は 2 つのプラットフォームがほぼ同時にセッションをクローズするときに sensible に動作しなければなりません。

### 衝突回避(Collision avoidance)

`{platform}-{YYYYMMDD}-{HHMM}` session-id は分単位の解像度を持ちます。同じプラットフォーム上の 2 つのセッションが同じ分内にクローズすると衝突します。実際にはこれは非常にまれです(1 ユーザー、プラットフォームあたり 1 つのアクティブセッション)、ルールは:

- archiver は既存のファイルを上書きしてはならない。`Write` の前にファイル名の衝突をチェック。
- 衝突時、archiver は秒精度のサフィックスを付加: `{platform}-{YYYYMMDD}-{HHMMSS}`。
- 衝突ケースは後のレビュー用に `_meta/sync-log.md` にログ。

### Outbox マージ並行性(Outbox merge concurrency)

次の Start Session が始まるときに 2 つのデバイスが両方ともアーカイブ中かもしれません。retrospective Mode 0 Step 7 はすでに `_meta/.merge-lock` でこれを扱います。session index は便乗します:

- 各 outbox ディレクトリは独自の `sessions/{session_id}.md` を持つ。
- マージは一度に 1 つずつ `_meta/sessions/` に移動。
- 両方の outbox が同じ session-id を生成した場合、マージは秒サフィックスを遡及的に付加することで両方を保持し、衝突をログ。

### クロスデバイス git 衝突(Cross-device git conflicts)

各セッションサマリーは独自のファイルなので、2 つのデバイスからの同時書き込みは独立したファイルを生成します — git は衝突なしにマージします。これは journal エントリが共同執筆に安全であることを可能にするのと同じ設計原則です。

2 つのエッジケース:

- **`INDEX.md` マージ衝突** — 常に再生成で解決。retrospective Mode 0 は `INDEX.md` をコンパイルされたアーティファクトとして扱う; 決して手動編集せず、決して 3 方向マージを試みない。衝突検出時、ファイルを削除し、次の Start Session で再コンパイルさせる。
- **デバイス間のクロックスキュー** — 2 つのデバイスがクロック同期していない場合、session-id が INDEX で順序外に見えるかもしれない。§5 の Step 4 のソートは `date` フィールド(タイブレーカーとして `started_at`)を使うので、小さなスキューは吸収される。大きなスキュー(>1 時間)はこの仕様のスコープ外のデバイス設定問題。

## 12. 実例(Worked Example)

ユーザーは `passpay` プロジェクトで whitepaper の洗練について 90 分の熟議を行う。archiver が生成:

ファイル名: `_meta/outbox/claude-20260419-1238/sessions/claude-20260419-1238.md`

```yaml
---
session_id: claude-20260419-1238
date: 2026-04-19
started_at: 2026-04-19T12:38:04+09:00
ended_at: 2026-04-19T14:09:17+09:00
duration_minutes: 91
platform: claude
theme: zh-classical
project: passpay
workflow: full_deliberation
subject: Technical whitepaper v0.5 to v0.6 refinement — evidence chain tightening
domains_activated: [FINANCE, GROWTH, GOVERNANCE]
overall_score: 8.2
domain_scores:
  FINANCE: 7.8
  GROWTH: 8.4
  GOVERNANCE: 8.4
veto_count: 1
council_triggered: false
soul_dimensions_touched: [evidence-discipline, quality-over-speed]
wiki_written: [finance/zk-proof-verification-cost]
methods_used: [evidence-laddering-v2]
methods_discovered: []
concepts_activated: [zk-proof, whitepaper, evidence-chain]
concepts_discovered: [modular-evidence-scaffolding]
dream_triggers: []
keywords: [passpay, finance, governance, growth, whitepaper, refinement, evidence, zk-proof]
action_items:
  - text: Tighten Section 4.2 evidence chain with three concrete citations
    deadline: 2026-04-22
    status: pending
  - text: Replace Figure 3 with simpler proof-cost chart
    deadline: 2026-04-21
    status: pending
compliance_violations: 0
---
```

retrospective のコンパイルステップが次の `INDEX.md` 行を生成:

```
2026-04-19 | passpay | Technical whitepaper v0.5 to v0.6 refinement — evidence chain | 8.2/10 | [passpay, finance, governance] | claude-20260419-1238
```

翌朝、ユーザーが whitepaper の evidence rigor について質問する。hippocampus は INDEX を読み、`whitepaper` + `evidence` の Wave 1 キーワードマッチでこのセッションを識別し、GWT arbitrator に伝えるために完全なサマリーをロードする。

## 13. 運用プレイブック(Operational Playbook)

一般的な操作のクイックリファレンス:

| 状況 | アクション |
|-----------|--------|
| 新規セッションが正常にクローズ | archiver Phase 1 が `{session_id}.md` を書き込む; retrospective が次の Start Session で INDEX を再コンパイル |
| ユーザーがセッションサマリーを編集(禁止) | AUDITOR が変異をフラグ; ユーザーは git 経由で元に戻す; 元に戻すまでシステム動作は未定義 |
| ユーザーがセッションサマリーを削除 | ファイルが git から削除; 次の Start Session コンパイルが INDEX から行を drop; セッションは検索不可能になる |
| v1.6.2a からのマイグレーション | `tools/migrate.py` を一度走らせる; journal に対するスポットチェックで検証; 単一の "v1.7 session index backfill" コミットで結果をコミット |
| クロックバグが間違ったタイムスタンプを生成 | 編集しない; `corrections/{session_id}.md` にノート; オプションで修正された時刻を指す手動修正エントリを追加 |
| INDEX.md が破損 | ファイルを削除; 次の Start Session が source-of-truth の `{session_id}.md` ファイルから再コンパイル |
| ディスク圧迫が近づく | §8 シャーディングトリガー参照; 明示的なユーザー決定なしに古いセッションサマリーを削除しない |

## 14. 関連仕様(Related Specs)

- `references/soul-spec.md` — SOUL 次元ライフサイクル、スナップショットメカニズム(並列パターン: セッションごとのファイル + INDEX コンパイル)
- `references/concept-spec.md` — `_meta/concepts/` 下の concept ストレージ、hippocampus が session index と並んで参照
- `references/hippocampus-spec.md` — このアーティファクトの消費者; 3 波アクティベーションを定義
- `references/gwt-spec.md` — hippocampus 出力を受け取る GWT arbitrator
- `devdocs/architecture/cortex-integration.md` §3.1 — アーキテクチャコンテキストとスキャンコスト見積もり
- `docs/architecture/markdown-first.md` §2 と §4 — パフォーマンスベースラインとファイルレイアウトルール
- `pro/agents/archiver.md` — `{session_id}.md` の writer、Phase 1 スコープ
- `pro/agents/retrospective.md` — `INDEX.md` の compiler、Mode 0 Start Session 責任

---

*本文は英語版 2026-04-22 スナップショットの翻訳。英語版が権威源。*
