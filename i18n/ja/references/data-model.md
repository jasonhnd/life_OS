# 標準データモデル

Life OS のすべてのデータ操作はこれらの標準型とインターフェースを使用します。アダプターがこれらをプラットフォーム固有の呼び出しに変換します。

## データ型

### Decision

> ⚠️ **v1.9 schema が下表を置き換え**（RFC §3.3.2 / §11.2.1 + `hosts/CLAUDE.md` §"Decision Records" 参照）。v1.9 は決定記録 frontmatter の権威ソース；下方の pre-v1.9 フィールドは歴史参照 / レガシーファイル解析用に保持。**フィールド名衝突の注意**：v1.9 は `type` を決定記録の種類（`change` / `no_change` / `escalation` / `superseded`）に再利用し、pre-v1.9 の workflow 種類（`simple` / `3d6m`）**ではない**。新規決定を書く際は v1.9 schema を使う。

**v1.9 正規 schema**（`meta/decisions/<YYYY-MM>/dec-<YYYY-MM-DD>-<NNN>.md`）：

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| id | string | はい | `dec-<YYYY-MM-DD>-<NNN>`（日次連番） |
| title | string | はい | 短いタイトル |
| type | enum | はい | `change` / `no_change` / `escalation` / `superseded` |
| projects | string[] | はい | 所属プロジェクト；`[]` = クロスプロジェクト |
| domains | string[] | はい | 6 functional IDs のサブセット：governance/execution/finance/infra/people/growth |
| reviewed_by | string | はい | agent または human |
| reviewed_at | date | はい | ISO 日付 |
| decision | text | はい | 一文の決定 |
| rationale | text | はい | 理由 |
| reopen_condition | text | 条件付き | `type: no_change` のとき必須 |
| supersedes / superseded_by | string[] / string | いいえ | 決定の系譜 |
| applied_methods | string[] | いいえ | 適用された method（リスト；Opt #8） |
| journal_date | date | いいえ | その日の journal ファイル（Opt #8） |
| content | text | はい | Summary report 全文（本文） |

<details><summary>Pre-v1.9 フィールド（レガシー、新規決定には使用しない）</summary>

| フィールド | 型 | 説明 |
|-------|------|-------------|
| type | enum | `simple` / `3d6m`（workflow —— v1.9 `type` に置き換え） |
| status | enum | `considering` / `decided` / `reversed` |
| category | enum | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | `good` / `neutral` / `bad` / `tbd` |
| score / veto_count | number | 総合スコア / 封駁イベント |
| date / project / area | — | `reviewed_at` / `projects` /（area は project 経由）に置き換え |

</details>

### Task

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| id | string | 自動 | |
| title | string | はい | タスク名 |
| status | enum | はい | `todo` / `in-progress` / `waiting` / `done` / `cancelled` |
| priority | enum | いいえ | `p0` / `p1` / `p2` / `p3` |
| due_date | date | いいえ | 期限 |
| context | enum | いいえ | `computer` / `phone` / `home` / `office` / `call` / `errand` |
| energy | enum | いいえ | `high` / `medium` / `low` |
| project | string | いいえ | 関連プロジェクト |
| area | string | いいえ | 関連エリア |
| last_modified | datetime | 自動 | |

### JournalEntry

> ⚠️ **v1.9 schema が下表を置き換え**（RFC §3.5 Opt #5 タイムライン + §3.8 Opt #8 クロスリファレンス参照）。v1.9 のジャーナルは**1日1ファイル** `meta/journal/<YYYY-MM-DD>.md`（タイムラインが権威ソース；同じ日の複数エントリは当日ファイル内に追記し、既存時は `projects:` でマージ）。下表の pre-v1.9 の per-entry フィールドはレガシー。

**v1.9 正規 schema**（`meta/journal/<YYYY-MM-DD>.md`）：

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| date | date | はい | その日（ファイル名でもある） |
| projects | string[] | はい | その日に言及されたプロジェクト；`[]` = なし |
| session_ids | string[] | いいえ | その日にエントリを貢献した session id |
| type_tags | string[] | はい | その日に存在するエントリ種類：`briefing` / `dream` / `advisor` / `auditor` / `migration` / … |
| referenced_decisions | string[] | いいえ | その日に参照された decision id（Opt #8） |
| referenced_methods | string[] | いいえ | その日に適用された method 名（Opt #8） |
| content | text | はい | その日のエントリ（本文；複数セクションを追記） |

<details><summary>Pre-v1.9 フィールド（レガシー per-entry モデル、新規ジャーナルには使用しない）</summary>

| フィールド | 型 | 説明 |
|-------|------|-------------|
| id / title | string | 廃止 —— 日次ファイルは `date` をキーとする |
| type | enum | `morning-court` / `censorate` / `remonstrator` / `inspection` / `manual` —— `type_tags`（リスト）に置き換え |
| mood / energy | enum | v1.9 の日次集約モデルで削除 |
| tags | string[] | `type_tags` に統合 |
| last_modified | datetime | 廃止 |

</details>

### WikiNote

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| id | string | 自動 | |
| title | string | はい | ノートタイトル |
| tags | string[] | いいえ | |
| links | string[] | いいえ | 他のノートへのWikiリンク |
| last_modified | datetime | 自動 | |
| content | text | はい | ノート本文 |

### Project

`projects/{p}/index.md` frontmatter。**v1.9 で `lifecycle_stage`（+ `paused_until` / `archived_*` / `created_at`）を追加**、PARA アーカイブ状態のため（RFC §3.4 Opt #4 + DR-1.9.20 参照 —— 旧 `archive/` ディレクトリを置き換え；アーカイブされたプロジェクトは `projects/{p}/` に残るため wikilink が保持される）。これは workflow `status` とは**別の軸**である：`lifecycle_stage` は「アクティブな PARA 集合か、アーカイブ済みか？」に答え、`status` + `strategic.status_reason` が workflow と戦略マップの停滞検出を駆動する。両者は併存する。

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| project / name | string | はい | プロジェクト名（ディレクトリ名でもある） |
| lifecycle_stage | enum | はい | **v1.9** · アーカイブ軸 —— `candidate` / `active` / `archived` / `superseded` |
| paused_until | date \| null | いいえ | **v1.9** · 期限付きの一時停止（"dormant" を置き換え）；`> today` = 停止中だがアクティブ |
| created_at | date | はい | **v1.9** · 作成日 |
| archived_at | date \| null | 条件付き | **v1.9** · `lifecycle_stage: archived` のとき設定 |
| archived_at_source | enum \| null | 条件付き | **v1.9** · `git-log` / `migrated-unknown` / `manual` / `auto` |
| archived_reason | text | 条件付き | **v1.9** · `lifecycle_stage: archived` のとき必須 |
| superseded_by | string | 条件付き | **v1.9** · `lifecycle_stage: superseded` のとき必須 |
| status | enum | いいえ | Workflow 軸 —— `planning` / `active` / `on-hold` / `done` / `dropped`；戦略マップの停滞検出はこれ + `strategic.status_reason` を読む |
| strategic | object | いいえ | 戦略マップフィールド（`line` / `role` / `flows_to` / `flows_from` / `last_activity` / `status_reason`）—— `references/strategic-map-spec.md` 参照 |
| related_wiki | wikilink[] | いいえ | **v1.9** · `[[wiki/<entry>]]` リンク |
| priority | enum | いいえ | `p0` / `p1` / `p2` / `p3` |
| deadline | date | いいえ | |
| area | string | いいえ | 関連エリア |
| outcome | text | いいえ | 結果の説明 |

### Area

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| id | string | 自動 | |
| name | string | はい | エリア名 |
| description | text | いいえ | |
| status | enum | はい | `active` / `inactive` |
| review_cycle | enum | いいえ | `weekly` / `monthly` / `quarterly` |
| last_modified | datetime | 自動 | |
| goals | text | いいえ | 目標の説明 |

### StrategicLine

`meta/strategic-lines.md`（ユーザーのセカンドブレイン）に保存。複数のラインは `---` で区切る。

| フィールド | 型 | 必須 | 説明 |
|-----------|------|------|------|
| id | string | はい | 一意識別子（kebab-case） |
| name | string | はい | 表示名 |
| purpose | text | はい | 一文の正式な目的 |
| driving_force | text | いいえ | このラインへの投資を本当に駆動するもの（purpose と異なる場合がある） |
| health_signals | text[] | いいえ | このラインが健全であることを示すシグナル（AI が提案、ユーザーが確認） |
| time_window | date | いいえ | ライン全体に影響する期限 |
| area | string | いいえ | 関連する生活エリア |
| created | date | 自動 | 作成日 |

### プロジェクト別戦略フィールド

`projects/{p}/index.md` の frontmatter へのオプション拡張。すべてのフィールドのデフォルトは空/null。

| フィールド | 型 | 必須 | 説明 |
|-----------|------|------|------|
| strategic.line | string | いいえ | 戦略ライン ID（`meta/strategic-lines.md` を参照） |
| strategic.role | enum | いいえ | `critical-path` / `enabler` / `accelerator` / `insurance` |
| strategic.flows_to[] | array | いいえ | 出力フロー: [{target, type, description}] |
| strategic.flows_from[] | array | いいえ | 入力フロー: [{source, type, description}] |
| strategic.last_activity | date | 自動 | 最終更新日（ARCHIVERが自動更新） |
| strategic.status_reason | text | いいえ | このプロジェクトが現在のステータスにある理由 |

フロータイプ: `cognition` / `resource` / `decision` / `trust`。役割とフローの定義: `references/strategic-map-spec.md`。

---

## v1.7 Cortex データ型

以下の型は v1.7 で Cortex 認知層のために導入された。各々が独自の権威 spec ファイルを持つ；下表はその短縮形。

### SessionSummary

権威 spec：`references/session-index-spec.md` §3。

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| session_id | string | はい | フォーマット `{platform}-{YYYYMMDD}-{HHMM}` |
| date | date | はい | ISO 8601 日付 |
| started_at | datetime | はい | タイムゾーン付きタイムスタンプ |
| ended_at | datetime | はい | タイムゾーン付きタイムスタンプ |
| duration_minutes | integer | はい | |
| platform | enum | はい | `claude` / `gemini` / `codex` |
| theme | enum | はい | テーマ ID（例 `zh-classical`、`ja-kasumigaseki`） |
| project | string | はい | バインドされたプロジェクト（session-binding HARD RULE を強制） |
| workflow | enum | はい | `full_deliberation` / `express_analysis` / `direct_handle` / `strategist` / `review` |
| subject | string | はい | 抽出された主題（200文字以内） |
| domains_activated | string[] | いいえ | PEOPLE/FINANCE/GROWTH/EXECUTION/GOVERNANCE/INFRA のサブセット |
| overall_score | number | いいえ | Summary Report からの 0-10 |
| domain_scores | map | いいえ | 領域別 0-10 スコア |
| veto_count | integer | いいえ | REVIEWER 封駁イベント |
| council_triggered | boolean | いいえ | COUNCIL 討論が発火したか？ |
| soul_dimensions_touched | string[] | いいえ | 参照された SOUL 次元 ID |
| wiki_written | string[] | いいえ | 本 session で自動書込された wiki エントリ ID |
| methods_used | string[] | いいえ | 適用された Method ID |
| methods_discovered | string[] | いいえ | 新規アーカイブされた Method ID |
| concepts_activated | string[] | いいえ | 参照された Concept ID |
| concepts_discovered | string[] | いいえ | archiver Phase 2 が書込した新規 Concept ID |
| dream_triggers | string[] | いいえ | 発火した DREAM REM trigger 名 |
| keywords | string[] | いいえ | 最大 10 個、hippocampus Wave 1 スキャン用 |
| action_items | array | いいえ | `[{text, deadline, status}]` |
| compliance_violations | integer | いいえ | AUDITOR が標記した違反 |

ストレージ：`meta/sessions/{session_id}.md`。archiver 書込後は不変。

### Concept

権威 spec：`references/concept-spec.md` §YAML Frontmatter Schema。

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| concept_id | string | はい | 小文字 + ハイフン、64文字以内、一意 |
| canonical_name | string | はい | 人間可読の表示名 |
| aliases | string[] | いいえ | 代替の表層形 |
| domain | enum | はい | `finance` / `startup` / `personal` / `technical` / `method` / `relationship` / `health` / `legal` / ユーザー拡張可能 |
| status | enum | はい | `tentative` / `confirmed` / `canonical` |
| permanence | enum | はい | `identity` / `skill` / `fact` / `transient` |
| activation_count | integer | はい | 活動期間中は単調増加 |
| last_activated | datetime | はい | decay pass で使用 |
| created | datetime | はい | 作成タイムスタンプ |
| outgoing_edges | array | いいえ | `[{to: concept_id, weight: 1-100, via: [tag], last_reinforced: ISO}]` |
| provenance.source_sessions | string[] | いいえ | 証拠が出現した session ID |
| provenance.extracted_by | enum | いいえ | `archiver` / `manual` / `dream` |
| decay_policy | enum | はい | `permanence` 層に一致 |

ストレージ：`meta/concepts/{domain}/{concept_id}.md`（confirmed/canonical）または `meta/concepts/_tentative/{concept_id}.md`（tentative）。

### SoulSnapshot

権威 spec：`references/snapshot-spec.md` §YAML Frontmatter Schema。

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| snapshot_id | string | はい | `{YYYY-MM-DD-HHMM}`、ファイル名と一致 |
| captured_at | datetime | はい | システムクロックからの実 ISO 8601 タイムスタンプ |
| session_id | string | はい | `meta/sessions/{session_id}.md` を参照 |
| previous_snapshot | string \| null | はい | 前のファイル名、最初のスナップショットは null |
| dimensions | array | はい | `[{name, confidence: 0-1, evidence_count, challenges, tier}]`、tier ∈ `core`/`secondary`/`emerging` |

ストレージ：`meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md`。メタデータのみ —— SOUL 本文内容なし。不変。

### EvalEntry

権威 spec：`references/eval-history-spec.md` §3。

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| eval_id | string | はい | `{YYYY-MM-DD-HHMM}-{project}` |
| session_id | string | はい | `meta/sessions/` エントリを参照 |
| evaluator | enum | はい | `auditor` / `auditor-patrol` |
| evaluation_mode | enum | はい | `decision-review` / `patrol-inspection` |
| date | datetime | はい | |
| scores | map | はい | 10 次元、各 0-10 整数（eval-history-spec §5 参照） |
| violations | array | いいえ | `[{type, agent, severity, detail}]` |
| agent_quality_notes | map | いいえ | agent 別の一行観察 |

ストレージ：`meta/eval-history/{YYYY-MM-DD}-{project}.md`。ローカルのみ。作成後は不変。移行バックフィルなし。

### Soul

権威 spec：`references/soul-spec.md`。他の v1.7 型と異なり、`Soul` は**実時の `SOUL.md` ファイルのインメモリビュー**であり、per-record ファイルではない。ツールは SOUL.md 全体を読み、この構造に解析し、（archiver 側の自動書込では）書き戻す。

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| path | Path | はい | `SOUL.md` の絶対パス |
| dimensions | `List[SoulDimension]` | はい | 解析されたすべての次元（新規ユーザーは空の場合がある） |
| raw_body | str | はい | 完全な markdown 本文（diff ベース書込用） |

`SoulDimension` サブレコード：

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| name | str | はい | 次元名（例 "risk-tolerance"） |
| confidence | float | はい | 0-1、`evidence_count / (evidence_count + challenges × 2)` で自動計算 |
| evidence_count | int | はい | |
| challenges | int | はい | |
| source | enum | はい | `dream` / `advisor` / `strategist` / `user` |
| created | date | はい | YYYY-MM-DD |
| last_validated | date | はい | YYYY-MM-DD |
| tier | enum | 自動 | `core`（≥0.7）/ `secondary`（0.3-0.7）/ `emerging`（0.2-0.3）/ `dormant`（<0.2）—— 読取時に派生 |
| what_is | str | いいえ | 本文セクション "What IS (实然)" |
| what_should_be | str | いいえ | 本文セクション "What SHOULD BE (应然)" |
| gap | str | いいえ | 本文セクション "Gap (差距)" |
| evidence | `List[str]` | いいえ | 本文 "Evidence" の項目 |
| challenges_list | `List[str]` | いいえ | 本文 "Challenges" の項目 |

ストレージ：second-brain ルートの単一ファイル `SOUL.md`。すべての主要ロールが読む；ARCHIVER Phase 2（soul-spec の自動書込基準）とユーザーが直接書込。

### Method

権威 spec：`references/method-library-spec.md` §4。

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| method_id | string | はい | 小文字 + ハイフン、一意 |
| name | string | はい | 表示名 |
| description | string | はい | INDEX.md 用の一文 |
| domain | enum | はい | Concept と同じ domain 語彙 |
| status | enum | はい | `tentative` / `confirmed` / `canonical` |
| confidence | number | はい | 0-1、式 `evidence_count / (evidence_count + challenges × 2)` |
| times_used | integer | はい | 方法を適用するたびに session ごとに増加 |
| last_used | datetime | いいえ | ISO 8601 |
| applicable_when | array | いいえ | `[{condition, signal}]` |
| not_applicable_when | array | いいえ | `[{condition}]` |
| source_sessions | string[] | いいえ | 貢献した session_id |
| evidence_count | integer | はい | 方法が機能した session 数 |
| challenges | integer | はい | 方法が失敗した session 数 |
| related_concepts | string[] | いいえ | concept_id |
| related_methods | string[] | いいえ | method_id（ソフト合成） |

ストレージ：`meta/methods/{domain}/{method_id}.md` または `meta/methods/_tentative/{method_id}.md`。ローカルのみ。

---

## 標準オペレーション

すべてのエージェントがこれらのオペレーションを使用します。アダプターがプラットフォーム固有の呼び出しに変換します。

| オペレーション | シグネチャ | 説明 |
|-----------|-----------|-------------|
| **Save** | `Save(type, data)` | 新規レコードの作成 |
| **Update** | `Update(type, id, data)` | 既存レコードの変更 |
| **Archive** | `Archive(type, id)` | **v1.9 セマンティクス変更**（DR-1.9.4）：プロジェクトの場合、frontmatter に `lifecycle_stage: archived` + `archived_at` + `archived_at_source` を設定；ディレクトリを物理的に移動**しない**（wikilink を保持）。他の型（decisions/sessions）はレガシーのアーカイブセマンティクスが引き続き適用。 |
| **Read** | `Read(type, id)` | 単一レコードの取得 |
| **List** | `List(type, filters)` | フィルタに一致するレコードの取得。**v1.9**：`List(Project, ...)` はデフォルトで `lifecycle_stage != archived` をフィルタ；`include_archived: true` を渡すと上書き。 |
| **Search** | `Search(keyword)` | 全型にわたる全文検索 |
| **ReadProjectContext** | `ReadProjectContext(project_id)` | バッチ読取: プロジェクトインデックス + タスク +（v1.9 更新）projects フィールド経由で `meta/decisions/<YYYY-MM>/` からクロスリファレンスされた決定 + projects フィールド経由で `meta/journal/` からのジャーナル |

### v1.9 archive セマンティクス（RFC §3.4 + DR-1.9.4 参照）

Pre-v1.9：`Archive(Project, id)` = `mv projects/{id}/ archive/{id}/` —— `[[projects/{id}/...]]` を指すすべての wikilink を破壊した。

v1.9：`Archive(Project, id)` = `Update(Project, id, {lifecycle_stage: archived, archived_at: <today>, archived_at_source: auto, archived_reason: <description>})`。プロジェクトは `projects/{id}/` に残る。すべての wikilink は解決可能なまま。

Index コンパイラ（retrospective Mode 0 → STATUS.md / STRATEGIC-MAP.md、archiver Phase 1 → STATUS 更新）はデフォルトで `lifecycle_stage: archived` をフィルタする。Obsidian graph view は colorGroup でアーカイブ済みプロジェクトをくすんだグレーで表示する。wiki/INDEX は**フィルタしない**（歴史的知識は可視のまま）。

`archived_at_source` enum（4 値、DR-1.9.26 参照）：
- `git-log` —— `/migrate-v1.9` Stage 3 が git log タイムスタンプから導出
- `migrated-unknown` —— `/migrate-v1.9` が git log から何も返らなかった場合のフォールバック
- `manual` —— ユーザーが frontmatter を手動編集
- `auto` —— archiver/REVIEWER が通常の session フローで自動アーカイブ

---

## ストレージバックエンド（GitHub + ローカル作業コピー）

Life OS は**単一のストレージバックエンド**を使用する：一つの git リポジトリ。セカンドブレインはディスク上のローカル作業コピーとして存在し（同時にあなたの Obsidian vault）；GitHub はそれをバックアップしクロスデバイス同期するリモートである。primary/sync の分割も、バックエンドごとの探測も、クロスバックエンドの競合層もない —— git がバージョン管理・バックアップ・マルチデバイス同期をネイティブに提供する。

> 以前は Google Drive と Notion も、マルチバックエンド同期プロトコル付きの選択可能なバックエンドとして提供していた；両者は削除済み——ストレージは GitHub のみ。

### 読取 / 書込

- **読取** —— ローカル作業コピー（ディスク上のファイル）から。
- **書込** —— ローカル作業コピーへ。GitHub リモートへの永続化は session 終了時に git 経由で行われる（ARCHIVER Phase 4）。

---

## 同期プロトコル

同期は素の git —— MCP 探測も、primary/sync 分離も、プラットフォームごとの `last_sync` 記帳もない。git 履歴が「前回以降に何が変わったか」の記録である。

### セッション開始（RETROSPECTIVE のハウスキーピング）

```
1. `git pull`（fetch + merge）でセカンドブレインリポジトリを更新し、他デバイスからプッシュされた変更を取り込む。
2. git リポジトリでない / リモート未設定 → ローカル作業コピーのみで操作；「💾 ストレージ：ローカルのみ（リモートなし）」と注記。
3. pull 時の merge 競合 → 競合ファイルをユーザーに提示して解決させる（単一ユーザー vault ではめったに起きない）。
```

### セッション終了（ARCHIVER Phase 4）

```
1. session outbox をメイン構造にマージ（制約事項 · outbox パターン参照）。
2. session の変更を `git add` + `git commit`。
3. リモートへ `git push`。push 失敗（オフライン / リモートなし）→「⚠️ 未プッシュ —— 次の session で同期」と注記、コミットはローカルに保持。
```

---

## 競合解決

単一バックエンドはクロスバックエンドの分岐がないことを意味する。唯一の競合源は、2台のデバイスが同期の間に同一ファイルを編集したケースで、それは `git pull` 時に **git merge 競合**として表面化する：

| 状況 | アクション |
|-----------|--------|
| クリーンな pull（重複なし） | fast-forward / 自動マージ、続行 |
| 同一ファイルが2台のデバイスで編集された | git merge 競合 → ROUTER が競合ファイルを提示、ユーザーが解決、解決結果をコミット |

outbox パターン（session ごとに1ディレクトリ）により、並行するローカル session があっても同一ファイル競合はめったに起きない。

---

## 削除ルール

- 削除は通常の git 操作（`git rm` / ファイル削除 + コミット）。他の変更と同様、次の push/pull で伝播する。
- ソフトデリート `_deleted: true` の墓標も、クロスバックエンド削除プロンプトもない —— あれらは複数バックエンドを調整するためだけに存在していた。

---

## 障害処理

| シナリオ | 処理 |
|----------|---------|
| session 終了時にリモート到達不能 | ローカルにコミット、push をスキップ、⚠️ を注記。次の session の `git push` が追いつく。 |
| pull 時の merge 競合 | 競合ファイルを提示；ユーザーが解決してから続行。 |
| git リポジトリでない / リモートなし | ローカル作業コピーのみで操作；何もプッシュしない。出力は会話に表示される。 |
| 新しいデバイス | セカンドブレインリポジトリを `git clone` → 準備完了。セカンドブレインがない場合 → セッションレベルの設定。 |

---

## 設定

git リモートはリポジトリ自身の `.git/config` に存在する —— Life OS はそれを重複保存しない。`meta/config.md` はもはや `storage.backends` リストやプラットフォームごとの `last_sync` タイムスタンプを持たない（git 履歴が「前回以降に何が変わったか」の真実の源である）。

```yaml
# meta/config.md（storage セクション）
storage:
  remote: github          # 単一バックエンド；"none" = ローカルのみの作業コピー
```

セカンドブレインがない場合 → ROUTER は session ローカルで操作する（永続化なし）。

---

## 制約事項

- **複数の session が同時にセカンドブレインを操作できる** outbox パターンを使用。各 session は自身の outbox ディレクトリ（`meta/outbox/{session-id}/`）に書き込む。次に上朝する session が全 outbox をメイン構造にマージする。共有ファイル（STATUS.md、meta/user-patterns.md、index.md）への直接書き込みは、上朝時の Outbox マージステップでのみ行われる。
- **session-id フォーマット**：`{platform}-{YYYYMMDD}-{HHMM}`、退朝時に生成（session 開始時ではない）。タイムスタンプは date コマンドでシステムクロックから取得すること、捏造禁止。例：`claude-20260412-1700`、`gemini-20260412-1900`。
- **Outbox マージロック**：マージ中は `meta/.merge-lock` を書き込む。存在し5分未満の場合はマージをスキップして通常通り続行する。マージ完了後に削除する。
- **空の session**：session に出力がない場合（意思決定、タスク、ジャーナルエントリがない）、outbox を作成しない。
- モバイルキャプチャはユーザー自身の git ワークフロー（モバイル git クライアント / 同期フォルダー）経由で `inbox/` に着地し、構造化データへ直接書き込まない；次のデスクトップ session で処理される
- すべてのアダプターは7つの標準オペレーションをサポートしなければならない

### Outbox manifest フォーマット

各 outbox ディレクトリには `manifest.md` が含まれる：

```yaml
---
session_id: "claude-20260412-1700"
platform: claude-code
model: opus
projects: [project-a, project-b]
adjourned: "2026-04-12T17:00:00+09:00"
outputs:
  decisions: 2
  tasks: 5
  journal: 3
  dream: 1
  index_delta: true
  patterns_delta: true
---
```

### Index Delta フォーマット

`index-delta.md` は `projects/{p}/index.md` に適用する変更を記録する：

```markdown
# Index Delta

## Target: projects/my-project/index.md
## Fields to update:
- Phase: "v5.4 deployed"
- Current focus: "打磨计划书到对外版本"
```

### Patterns Delta フォーマット

`patterns-delta.md` は `meta/user-patterns.md` に追記する内容を記録する：

```markdown
# Patterns Delta — append to meta/user-patterns.md

### [2026-04-12] New pattern: decision speed increasing
Source: Remonstrator
Observation: Last 3 decisions made after first round of clarification.
```
