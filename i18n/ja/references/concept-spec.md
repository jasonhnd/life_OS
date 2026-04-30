---
translated_from: references/concept-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Concept Specification

Concept ファイルは、Cortex の synaptic network におけるノードです。各ファイルは、セッションをまたいで活性化できる 1 つの再利用可能なアイデア、エンティティ、またはパターンを表します。概念間の synapse エッジは、別個のグラフデータベースではなく、concept ファイル自体の YAML frontmatter 内に存在します。これにより、ネットワーク全体がテキストエディタで inspectable であり、プレーンな git でポータブルになります。

## 位置付け(Positioning)

| ストレージ | 何を記録するか | 例 |
|---------|----------------|---------|
| `decisions/` | 何を決定したか(特定、タイムスタンプ付き) | "2026-04-01: chose trust structure" |
| `user-patterns.md` | 何を行うか(行動パターン) | "Tends to avoid financial dimensions" |
| `SOUL.md` | あなたが誰であるか(価値観、人格) | "Risk appetite: medium-high" |
| `wiki/` | あなたが知っていること(再利用可能な世界結論) | "NPO lending has no 貸金業法 exemption" |
| `_meta/concepts/` | **何と何が接続するか(synaptic graph)** | "company-a-holding" ノード + 他の概念へのエッジ |

SOUL は人を管理します。Wiki は知識を管理します。Concepts は、「A が活性化されたら、他に何が点灯すべきか」をシステムが知るためのグラフを管理します。これらは混在させてはなりません。

---

## 原則(Principles)

1. **ゼロから成長する** — `_meta/concepts/` は空で開始します。初期化は不要です。
2. **1 概念 = 1 ファイル(厳格)** — マルチトピックの編纂はありません。単一の概念を複数ファイルに分割することは禁止されています(anti-pattern、§10 参照)。
3. **エッジはノードと共に存在** — Outgoing synapse エッジはソース concept の YAML frontmatter に格納されます。逆方向インデックスは `SYNAPSES-INDEX.md` にコンパイルされます(手書きは決してしません)。
4. **厳格な基準のもとで自動書き込み** — 概念は、エビデンスが蓄積されたときに `archiver` Phase 2 によって自動作成されます。ユーザーは削除または「undo recent concept」と言うことでナッジします。
5. **Permanence が decay を決定する** — 各概念は、その decay curve を決定する permanence tier を携帯します(user decision #9、brainstorm §7)。
6. **Reversible なライフサイクル** — `tentative → confirmed → canonical` は一方向の昇格パスですが、降格は常に可能です(user decision #10)。

---

## ファイルの場所(File Location)

```
_meta/concepts/{domain}/{concept_id}.md
```

| パスセグメント | 意味 |
|--------------|---------|
| `_meta/concepts/` | concept network のルート |
| `{domain}/` | テーマパーティション(下記参照) |
| `{concept_id}.md` | 1 ファイル 1 概念、ID で命名される |

### Domain パーティション

Domain は、concept のためのトップレベルのテーマスロットです。最小セット(`wiki-spec.md` および `method-library-spec.md` と整合):

- `finance/` — 金融エンティティ、金融商品、概念
- `startup/` — venture、プロダクト、グロース概念
- `personal/` — パーソナルライフ領域の概念(identity ではない — identity は SOUL に属する)
- `technical/` — エンジニアリング、アーキテクチャ、実装パターン
- `method/` — 方法論、ワークフロー、手順
- `relationship/` — 組織および非個人の関係エンティティ
- `health/` — 健康、フィットネス、医療概念
- `legal/` — 法的フレームワーク、コンプライアンス、規制概念
- `writing/` — writing craft、document-refinement 方法論、editorial パターン

ユーザーは second-brain が成長するにつれて新しい domain ディレクトリを追加できます。スキーマで強制されるホワイトリストはありません — archiver が最初の concept 割り当て時にディレクトリを作成します。

### 予約パス

- `_meta/concepts/INDEX.md` — すべての concept のコンパイル済み 1 行要約(`retrospective` Mode 0 で再生成)
- `_meta/concepts/SYNAPSES-INDEX.md` — コンパイル済みの逆方向エッジインデックス(`archiver` Phase 2 で再生成)
- `_meta/concepts/_tentative/` — confidence しきい値未満の concept のステージングエリア
- `_meta/concepts/_archive/` — 引退した concept(監査用に保持、activation 時には無視)

---

## YAML Frontmatter スキーマ(YAML Frontmatter Schema)

すべての concept ファイルは YAML frontmatter で始まります。すべてのフィールドがリストされており、オプションフィールドにはマークが付いています。

```yaml
---
concept_id: string                # required, unique across the network
canonical_name: string            # display name (human-readable)
aliases: [string]                 # other surface forms this concept may appear as
domain: string                    # finance | startup | personal | technical | method | relationship | ...
status: enum                      # tentative | confirmed | canonical
permanence: enum                  # identity | skill | fact | transient
activation_count: integer         # how many times referenced across sessions
last_activated: ISO 8601          # timestamp of last activation
created: ISO 8601                 # creation timestamp
outgoing_edges:
  - to: concept_id
    weight: integer               # 1-100, Hebbian-strengthened
    via: [tag]                    # what triggered this connection (free-form tags)
    last_reinforced: ISO 8601
provenance:
  source_sessions: [session_id]   # sessions where evidence appeared
  extracted_by: enum              # archiver | manual | dream
decay_policy: enum                # matches permanence tier (see §5)
---

# Canonical Name

Body content (markdown, optional but encouraged)...

## Evidence / Examples
- [link to source session or decision]

## Related Concepts
- [[other-concept-id]]
```

### フィールド制約

| フィールド | 制約 |
|-------|-----------|
| `concept_id` | Lowercase、hyphen のみ、letter で開始、最大 64 chars(§7 参照) |
| `canonical_name` | 任意の human-readable 文字列 |
| `aliases` | 0 個以上。concept-resolver が raw テキストを ID にマップする際に使用 |
| `domain` | concept の親ディレクトリと一致しなければならない |
| `status` | `tentative` → `confirmed` → `canonical`。このフィールドを通じたダウングレードはなし — 降格は decay log を経由 |
| `permanence` | `identity` | `skill` | `fact` | `transient` |
| `activation_count` | 非負整数、アクティブライフ中は単調増加 |
| `last_activated` | decay pass が dormancy を判定するために使用 |
| `outgoing_edges.weight` | 100 に上限(runaway reinforcement を防ぐキャップ) |
| `decay_policy` | `permanence` と一致しなければならない — §5 参照 |

---

## ライフサイクル(Lifecycle)

```
1. 🌱 Creation — archiver Phase 2 がセッションから ≥2 evidence points を持つ concept を抽出し、tentative ファイルを作成します
2. 📈 Reinforcement — 各セッションの activation が activation_count をインクリメントし、last_activated を更新し、エッジを強化します
3. ✅ Promotion — tentative → confirmed(≥3 independent sessions)→ canonical(user-pin または ≥10 independent sessions)
4. 📉 Decay — archiver が Adjourn ごとに decay pass を実行します(user decision #10)
5. 💤 Retirement — last_activated > 90 days + all outgoing edges weight < 1.0 + permanence ≠ identity → move to _meta/concepts/_archive/ (activation_count preserved, never decremented)
6. ↩️ Undo — ユーザーが「undo recent concept」と言う、あるいはファイルを手動削除します
```

### Creation

`archiver` Phase 2(セッション Adjourn 時、wiki / SOUL 自動書き込みの後に動作):

1. セッションフレームをスキャンし、反復する名詞句、エンティティ言及、メソッド名を探す
2. 各候補について、**6 つの creation 基準すべて** を適用します:
   1. **Frequency ≥ 2 mentions** — セッション内で 2 回以上出現(1 回のみのものは一時的すぎる)
   2. **≥ 2 個の独立したエビデンスポイント** — 別個のフレーム、別個のレポート、あるいは別個の意思決定(同じ文を 2 回引用したものは不可)
   3. **Identity beyond this session** — 候補が将来のセッションで再利用可能と思われる(LLM judgment)
   4. **人物、価値、特性、手順ではない** — 人々は SOUL / user-patterns に属し、価値 / 特性は SOUL に属し、手順は method library に属する
   5. **Privacy filter clears** — 氏名(公人でない限り)、具体的な金額 / 口座 / ID、家族・友人への言及、追跡可能な日時+場所の組み合わせを除去する。除去後に候補が意味を失う場合 → 破棄(それは個人メモであり、再利用可能な概念ではなかった)
   6. **Domain routing succeeds** — LLM が §File Location Domain partitions にリストされた domain の 1 つを選ぶ(あるいは新しい domain ディレクトリを作成する)。どの domain にもルーティングできない候補はまだ concept ではない
3. 6 つすべて合格 → `_meta/concepts/_tentative/{domain}/{concept_id}.md` にファイルを作成
4. いずれかの基準が不合格 → 破棄し、後の監査のため `decay-log.md` に記録

> 実装: `pro/agents/archiver.md` §Phase 2 Mid-Step(Concept Extraction + Hebbian Update)と `tools/migrate.py` は同じ 6 基準の列挙を使用します。本 spec が変更される際は、これらも lock-step で更新する必要があります。

### Promotion

| From → To | トリガー |
|-----------|---------|
| `tentative → confirmed` | Concept が **≥3 個の独立したセッション** にわたって活性化された。ファイルは `_tentative/` から `{domain}/` に移動 |
| `confirmed → canonical` | ユーザーが手動でピン留めするか(frontmatter の `status: canonical`)、または concept が **≥10 個の独立したセッション** にわたって活性化された |

Promotion は `_meta/cortex/decay-log.md` にタイムスタンプとトリガーセッションと共に記録されます。

### Reinforcement

セッション中の各 activation:
- `activation_count += 1`
- `last_activated = {current ISO timestamp}`
- A と B の両方が同じフレームで co-activated されたエッジ (A → B) について: `weight += 1`(100 で上限)、`last_reinforced = today`

### Decay

Archiver Phase 2 は、すべての Adjourn で decay pass を実行します(user decision #10)。Decay は permanence tier ごとに適用されます:

| Permanence | Decay 動作 | 根拠 |
|-----------|-----------------|-----------|
| `identity` | decay なし | SOUL 隣接の価値観は決して色あせない |
| `skill` | 床までの対数減衰 | スキルは一度学ばれると保持され、ほとんど忘れられない |
| `fact` | 指数減衰 | コンテキスト依存の事実は時間とともに関連性を失う |
| `transient` | ゼロへの崖型減衰 | イベント依存の概念はハードに期限切れる |

エッジ weight は、concept の dormancy と共に decay します。`weight ≤ 0` になると、そのエッジは次の Adjourn pass で削除されます。

### Retirement

Retirement は **dormancy + エッジ weight の崩壊** によって駆動されるものであり、`activation_count` をデクリメントすることによってではありません。`activation_count` フィールドは concept のアクティブライフ全体を通じて **単調非減少** のまま維持されます(§Reinforcement 参照);retirement は異なるシグナルによってトリガされるライフサイクル遷移です:

1. **Dormancy しきい値** — `last_activated` が **90 日** より古い(その期間内にどのセッションでも再活性化されていない)、**かつ**
2. **エッジ weight の崩壊** — 現在の Adjourn の decay pass 後に `outgoing_edges` のすべてのエッジが `weight < 1.0` である(つまり concept がライブグラフから切断された)、**かつ**
3. **Permanence ティアが `identity` ではない** — identity ティアの concept は決して retire しない(§5 Decay テーブル参照)

3 つすべての条件が満たされた場合、concept は次の Adjourn pass で `_meta/concepts/_archive/{domain}/{concept_id}.md` に移動されます。アーカイブされた concept は:
- 依然として git 履歴の中にある(データロスなし)
- 活性化時に hippocampus によって無視される
- patrol 中に AUDITOR から見える
- `activation_count` は最終の単調値で保持される(履歴監査用)

将来の再活性化(同じ主題が再浮上)では、concept は `_archive/` から `{domain}/` に復元され、`activation_count` は中断した地点からインクリメントを継続します。

### Undo

2 つの undo パス:

1. **手動削除** — ユーザーがファイルを削除する → 次の `archiver` 実行が `SYNAPSES-INDEX.md` を再構築し、dangling エッジを prune する
2. **言語的 undo** — ユーザーがセッション中に「undo recent concept」と言う → archiver の次の呼び出しが、最新の自動書き込みをロールバックする(wiki undo と同じパターン、`references/wiki-spec.md` 参照)

---

## Hebbian 更新アルゴリズム(Hebbian Update Algorithm)

`archiver` Phase 2 内で、wiki/SOUL 自動書き込みの直後、SYNAPSES-INDEX 再生成の前に実行されます。

注：以下 2 つのアルゴリズム擬似コードは、EN spec・テスト・実装と行単位で照合しやすいよう英語原文のまま保持します。ローカライズするのは説明文のみです。

```
1. Extract the set of concepts activated in the session (from frame md files)
2. For each ordered pair (A, B) that co-occurred in at least one frame:
     - Find or create edge A → B in A's outgoing_edges
     - Find or create edge B → A in B's outgoing_edges
     - weight += 1 (capped at 100)
     - last_reinforced = today
3. For each new concept (not in any existing file):
     - 6 条件チェックを通過(クロスセッション候補 + ≥2 evidence points)
     - On pass → create tentative entry with initial frontmatter
     - On fail → log in decay-log.md, do not create
4. For each activated concept (existing file):
     - activation_count += 1
     - last_activated = now
5. Decay pass (see §5 Decay)
     - Apply per-permanence decay curve
     - Remove edges with weight ≤ 0
6. Recompile SYNAPSES-INDEX.md from all concept files
```

Hebbian 更新は単一セッション内で idempotent(べき等) — pass を再実行しても同じ結果を生成します(co-occurrence カウントは、エージェント呼び出しではなく、セッションによって bound されています)。

---

## 活性化拡散ルール(Spreading Activation Rules)

Pre-Router Cognitive Layer(Step 0.5、`devdocs/architecture/cortex-integration.md` §4 参照)で `hippocampus` サブエージェントによって使用されます。活性化拡散は、現在のメッセージに対してシステムが「warm」と見なす concept のリストを生成します。

```
Wave 1 — Direct match
  - Concepts whose canonical_name or aliases match the user message
  - No ranking adjustment — these are the seeds

Wave 2 — Strong neighbours
  - For each seed, follow outgoing edges with weight ≥ 3
  - Collect destinations, preserve edge weight for ranking

Wave 3 — Weak neighbours
  - For each seed, follow outgoing edges with weight ≥ 1 and < 3
  - Used only for sub-threshold pre-activation (brainstorm §8.5)
```

3 つの wave の後、結果は `relevance × edge_weight × concept.activation_count` でランク付けされ、**合計 top 5-7 concept にバウンドされます**(ハードキャップ — 認知的洪水を防ぐ)。

Sub-threshold pre-activation: top 5-7 に入らなかった Wave 3 からの concept は、それでもセッションの残り期間 `salience = 0.5 × edge_weight / 10` でキャッシュされます。自分自身では発火しませんが、後続のフレームがそれらを強化した場合、しきい値を越えることができます。

---

## Concept ID 生成(Concept ID Generation)

canonical な concept ID は:
- Lowercase ASCII と hyphen のみ(例: `iterative-document-refinement`)
- letter で開始しなければならない
- 最大 64 文字
- concept network 内でグローバルに一意

### ID の導出

archiver は raw canonical name から、lowercase 化し、非英数字の連続を単一のハイフンに置換し、先頭/末尾のハイフンをトリムし、64 文字に切り詰めます。例:

| Canonical name | Concept ID |
|----------------|-----------|
| "Iterative Document Refinement" | `iterative-document-refinement` |
| "Company-A (Holding)" | `company-a-holding` |
| "三省六部" | (untransliterable CJK → falls back to transliteration or an explicit alias, see below) |

### 衝突解決

導出された ID が **異なる** canonical concept に対してすでに存在する場合、archiver は domain をサフィックスとして追加します:

```
iterative-document-refinement            → existing, method domain
iterative-document-refinement--writing   → new, writing domain
```

(ダブルハイフンが domain サフィックスを分離し、ハイフンを含む単語との衝突を避けます。)

### CJK および非ラテン入力

raw canonical name にラテン表現がない場合、archiver は:
1. 明らかな場合は短いローマ字/ピンイン音訳を使用する
2. 意味的な英語ラベル(三省六部に対して `cabinet-three-departments`)にフォールバックし、原文を alias として保存する

ID は技術的識別子であり、display name ではありません — `canonical_name` と `aliases` がユーザー可視形式を携帯します。

---

## プライバシー(Privacy)

Concept ファイルは **クロスセッションで再利用可能な知識** を保存するのであり、個人情報ではありません。

| concept に属する | 他に属する |
|---------------------|-------------------|
| `mvp-validation-methodology` | 個人の名前 → SOUL / user-patterns(concept には決して入れない) |
| `trust-structure-in-japan` | 特定の銀行口座番号 → どこにも保存しない |
| `pre-mortem-technique` | 家族メンバーの名前 → SOUL(プライバシーフィルタ付き) |

**LLM privacy filter**(`references/wiki-spec.md` 参照)は、concept が作成される前に実行されます:
- 名前を除去(結論に直接関連する公人を除く)
- 特定の金額、口座番号、ID 番号を除去
- 特定の企業名を除去(パブリックドメインのケーススタディである場合を除く)
- 家族/友人への言及を除去
- トレーサブルな日付+場所の組み合わせを除去
- 除去した結果 concept が無意味になる場合 → 破棄する(それは再利用可能ではなく、個人的なメモだった)

個人情報は concept ではなく SOUL.md に流れます。個々の人々(同僚、家族、友人)についての concept は明示的に禁止されています — その領域は SOUL です(user decision #8)。

---

## v1.6.2a からのマイグレーション(Migration from v1.6.2a)

v1.7 以前には concepts ディレクトリがありません。v1.7 へのマイグレーションは一度だけ実行され、`tools/migrate.py` によってオーケストレーションされます(user decision #7):

1. `_meta/journal/` エントリの **直近 3 ヶ月** をスキャン(バウンドされたウィンドウ — より古い材料は触らない)
2. archiver の Hebbian pass と同じアルゴリズムで候補 concept を抽出
3. 6 基準チェックとプライバシーフィルタを通過した各候補について:
   - `_meta/concepts/_tentative/{domain}/{concept_id}.md` にファイルを作成
   - 初期 `activation_count` = concept が出現した独立セッション数(10 で上限)
4. 同じ journal エントリでの co-occurrence から初期 synapse weight を計算(10 で上限)
5. `activation_count ≥ 3` の concept を `_tentative/` から `{domain}/` に移動し、`status: confirmed` を設定
6. `activation_count ≥ 10` の concept は `status: canonical` を取得
7. 最初の `SYNAPSES-INDEX.md` と `INDEX.md` を生成
8. マイグレーション結果を `_meta/cortex/bootstrap-status.md` にログ

マイグレーションは idempotent — 既にマイグレーション済みのツリーに対して再実行しても追加ファイルは生成されません。

---

## アンチパターン(Anti-patterns)

以下は spec によって禁止されており、archiver が書き込み時に拒絶しなければなりません:

1. **手動で `outgoing_edges` を編集する** — archiver がエッジ状態を所有します。ユーザー編集は次の Adjourn で上書きされます。接続を断つには、concept ファイルの 1 つを削除するか「undo recent concept」と言ってください。
2. **個々の人々についての concept を作成する** — それは SOUL のテリトリーです(user decision #8)。個人的関係は SOUL.md に属し、`relationship/` domain は組織および非個人エンティティ用に予約されています。
3. **単一の concept を複数ファイルに分割する** — concept は 1 ファイルです。concept が 1 ファイルで記述できないほど大きい場合、それは実際には別個のエントリとそれらの間の明示的なエッジが必要な複数の concept です。
4. **`SYNAPSES-INDEX.md` を手書きする** — これはコンパイルされたアーティファクトで、Adjourn ごとに再生成されます。手編集は上書きされます。
5. **ダブルハイフンサフィックスなしに domain をまたいで ID を再利用する** — archiver が一意性を強制します。衝突は §7 のルールで解決されます。
6. **concept の body や evidence セクションに個人データを保存する** — プライバシーフィルタが実行されなければなりません。フィルタされていないテキストは spec に違反します。

---

## 各役割が concept をどう使うか(How Each Role Uses Concepts)

すべての役割は、参照する前に `_meta/concepts/INDEX.md` が存在するかをチェックします。存在しないまたは空の場合、その役割は concept 入力なしで通常通り動作します。

| 役割 | 読むもの | 使い方 |
|------|---------------|-----------------|
| **hippocampus** | `_meta/concepts/INDEX.md` + 活性化拡散パス上のファイル | GWT 仲裁用の「warm concepts」シグナルを生成 |
| **gwt-arbitrator** | hippocampus が生成した concept-link シグナル | concept シグナルを salience スカラーに重み付け |
| **ROUTER** | warm concepts を含む注釈付き入力 | より鋭い意図分類 — warm concept を事実ではなくコンテキストとして扱う |
| **Six Domains (Pro)** | dispatch コンテキストで渡される concept エントリ | 再導出ではなく、確立されたアイデアから分析を開始 |
| **REVIEWER** | `_meta/concepts/INDEX.md` | 一貫性チェック — 新しい結論が canonical な concept と衝突する場合にフラグ |
| **AUDITOR** | `_meta/concepts/` ディレクトリ(patrol 中) | Concept ヘルス — stale ノード、孤立エッジ、プライバシー違反 |
| **DREAM** | `_meta/concepts/INDEX.md` + `SYNAPSES-INDEX.md` | N3 はグラフをクロスドメイン連想に使用、REM は creative な接続 |
| **archiver** | セッションフレーム + 既存 concept ファイル | Phase 2 で Hebbian 更新アルゴリズム + decay pass を実行する(`outgoing_edges`、`SYNAPSES-INDEX.md` を書き込み、`activation_count` / `last_activated` を更新する) |
| **retrospective** | すべての concept ファイル(Mode 0 中) | `INDEX.md` を再生成する(read-only。decay は archiver の書き込み責務、§Decay 参照)。briefing で dormant concept をフラグする。 |

---

## 制約(Constraints)

- **1 ファイルにつき 1 concept** — 分割は禁止
- **archiver が `outgoing_edges` への書き込みを所有する** — ユーザー編集は上書きされる
- **プライバシーフィルタによって個人データは除外される** — 個々の人々は SOUL に属する
- **エッジ weight は 100 で上限** — runaway reinforcement はバウンドされる
- **活性化拡散は top 5-7 でバウンド** — 認知的洪水を防ぐ
- **Concept ID ≤ 64 chars、lowercase + hyphen、letter で開始**
- **マイグレーションは `_meta/journal/` の直近 3 ヶ月のみを読む** — より古い材料は触らない
- **SYNAPSES-INDEX.md と INDEX.md はコンパイルされる** — 決して手書きしない
- **ローカル専用 — Notion sync なし** — concept は `_meta/` に留まる(user decision #12)

---

## 関連仕様(Related Specs)

- `references/cortex-spec.md` — 全体 Cortex アーキテクチャ。concept は Four Core Mechanisms の 1 つ
- `references/hippocampus-spec.md` — 活性化拡散出力の consumer(Wave 2/3 は `outgoing_edges` をたどる)
- `references/gwt-spec.md` — arbitrator が concept lookup から導出される `canonical_concept`/`emerging_concept` シグナルを消費
- `references/session-index-spec.md` — セッション frontmatter が concept ファイルにマップバックする `concepts_activated` / `concepts_discovered` を追跡
- `references/snapshot-spec.md` — sibling の `_meta/` アーティファクト。markdown-first + ローカル専用制約を共有
- `references/method-library-spec.md` — method はこのネットワークを指す `related_concepts: [concept_id]` を携帯
- `references/wiki-spec.md` — wiki エントリは concept エビデンスを anchor できる。プライバシーフィルタはそこで定義されている
- `references/soul-spec.md` — SOUL 境界(個人的な人々はそこに属し、concept には属さない)
- `references/eval-history-spec.md` — AUDITOR の `cognitive_annotation_quality` は concept-graph シグナルを消費
- `pro/agents/archiver.md` — Phase 2 が Hebbian 更新、decay pass、SYNAPSES-INDEX 再生成、tentative 書き込みを所有
- `pro/agents/retrospective.md` — Mode 0 が `INDEX.md` を再生成し dormant concept をフラグ
- `devdocs/architecture/cortex-integration.md` — Step 0.5 Pre-Router Cognitive Layer コンテキスト

---

> ℹ️ **2026-04-22 補完**:Lifecycle コードブロックの Step 1/2/3/4/6 + §Creation 6-criteria 括注の翻訳漏れを補完
>
> ℹ️ **2026-04-22 更新**:EN R3.2 §Creation 6-criteria / §Retirement / §Conflict の修正を同期

*訳注: 本文は英語版 2026-04-22 スナップショットの翻訳。英語版が権威源で、曖昧な場合は英語版が優先。*
