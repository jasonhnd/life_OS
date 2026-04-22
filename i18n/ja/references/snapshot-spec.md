---
translated_from: references/snapshot-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# Snapshot 仕様書(Snapshot Specification)

SOUL スナップショットは、すべてのセッションの終わりにキャプチャされる小さく、immutable なメタデータダンプです。次の Start Session での SOUL Health Report が、別のステートマシンを保持せずにセッションをまたいでトレンド矢印(↗↘→)を計算できるようにします。スナップショットは凍結された瞬間です: 時刻 T におけるユーザーのアイデンティティ次元についてシステムが知っていたことです。

## 位置付け(Positioning)

| アーティファクト | 記録内容 |
|----------|----------------|
| `SOUL.md` | 現在の権威あるアイデンティティ状態 |
| `_meta/snapshots/soul/` | **トレンド計算のための歴史的 SOUL 状態(この仕様)** |
| `_meta/concepts/` | Synaptic ネットワーク(`references/concept-spec.md`) |
| `wiki/` | 再利用可能な世界知識 |

スナップショットはメタデータのみ — SOUL 本文コンテンツを複製することは決してありません。時点における SOUL の数値的な形状を記録し、retrospective が「当時」と「現在」を比較できるようにします。

---

## 原則(Principles)

1. **Immutable** — 書き込まれたら、スナップショットは決して編集されない。修正は SOUL.md に行き、歴史的スナップショットではない。
2. **メタデータのみ(Metadata-only)** — スナップショットは次元名、confidence、evidence counts、tier を格納。SOUL 本文テキストは格納しない。
3. **セッションごとに作成(Created every session)** — 些細なセッションでも。スナップショットの欠落はトレンド計算を破壊する。
4. **小さい(Small)** — 各スナップショットは典型的に <5KB。何千ものスナップショットも安価なままである。
5. **積極的にアーカイブ(Archived aggressively)** — アクティブなスナップショットは 30 日間ホットに留まり、その後 `_archive/` に移動し、90 日後に削除される。Git 履歴が完全な監査証跡を保持する。**スナップショットは Notion に同期しない** — ユーザー決定 #12 と `cortex-spec.md` §Anti-patterns に従い、すべての Cortex/`_meta/` データ(concepts、synapses、snapshots)はローカルに留まる。Notion はセッションサマリーと decision レコードのみを受け取る。

---

## ファイルの場所(File Location)

```
_meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md
```

ファイル名のタイムスタンプは **キャプチャ時の実際の `date` コマンドから来なければならない** — 捏造なし(v1.4.4b からの決定)。システムクロックが利用不可の場合、スナップショット書き込みは中止され、失敗は `_meta/cortex/decay-log.md` にログされる。

### 予約パス(Reserved paths)

- `_meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md` — アクティブなスナップショット(30 日以内)
- `_meta/snapshots/soul/_archive/{YYYY-MM-DD-HHMM}.md` — アーカイブされたスナップショット(30-90 日)
- 90 日より古いスナップショットはファイルシステムから削除される; 監査証跡は git 履歴にのみ残る(スナップショットはユーザー決定 #12 に従いローカルのみ)

---

## YAML Frontmatter スキーマ(YAML Frontmatter Schema)

```yaml
---
snapshot_id: {YYYY-MM-DD-HHMM}      # ファイル名に一致、ユニーク
captured_at: ISO 8601               # 実際のキャプチャタイムスタンプ
session_id: string                  # このスナップショットを生成したセッション
previous_snapshot: string | null    # 前のファイル名、または最初の場合は null
dimensions:
  - name: string                    # SOUL 次元名
    confidence: float               # 0-1、キャプチャ時に SOUL.md からコピー
    evidence_count: integer         # 支持する decisions
    challenges: integer             # 矛盾する decisions
    tier: enum                      # core | secondary | emerging | dormant
---

# SOUL Snapshot · {YYYY-MM-DD}

(本文はオプション — frontmatter が権威あるコンテンツ。人間可読のテーブルがデバッグ用に含まれてもよいが、必須ではない。)
```

### フィールド制約(Field constraints)

| フィールド | 制約 |
|-------|-----------|
| `snapshot_id` | ファイル名のステムと完全に一致しなければならない |
| `captured_at` | システムクロックからの実際の ISO 8601 タイムスタンプでなければならない |
| `session_id` | `_meta/sessions/` 内の有効な session ID でなければならない |
| `previous_snapshot` | 前のスナップショットのファイル名、または最初の場合 `null` |
| `dimensions` | `confidence > 0.2` の次元のみ含める(ノイズをスキップ) |
| `dimensions[].tier` | confidence から導出(以下の Tier Mapping 参照) |

### Tier マッピング(Tier Mapping)

Tier はキャプチャ時に導出され、SOUL.md に別途格納されません。

すべての confidence 帯は半開区間 `[a, b)` を使用します — 下限は inclusive、上限は exclusive です。境界値は常に**上位** tier に属します(例: confidence がちょうど 0.3 の場合は `secondary` であり `emerging` ではない; ちょうど 0.7 の場合は `core` であり `secondary` ではない)。これは `references/soul-spec.md` §Tiered Reference by Confidence および `references/gwt-spec.md` §5.4 に準拠します。

| Tier | Confidence 範囲 |
|------|------------------|
| `core` | `[0.7, 1.0]` |
| `secondary` | `[0.3, 0.7)` |
| `emerging` | `[0.2, 0.3)` |
| `dormant` | `[0.0, 0.2)`(スナップショットから除外) |

スナップショットは意図的に `dormant` 次元を省略し、ファイルを小さく保ちます。スナップショットにおける次元の不在は意味を持ちます — これはトレンドアルゴリズムが退場または降格を検出する方法です。

---

## 作成(Creation)

スナップショット作成は `archiver` Phase 2 が所有し、concept 抽出後に実行されます(セッション中に強化された concept がすでに永続化されるため)。シーケンスは:

```
archiver Phase 2
    ├── Step 1 — wiki / SOUL 自動書き込み(既存)
    ├── Step 2 — concept 抽出 + Hebbian 更新(concept-spec.md)
    ├── Step 3 — SOUL スナップショットダンプ(この仕様)
    │   1. 実際のキャプチャタイムスタンプを取得するために `date` を実行
    │   2. 現在の SOUL.md を読む
    │   3. confidence > 0.2 の各次元について:
    │        - confidence から tier を決定
    │        - name、confidence、evidence_count、challenges をコピー
    │   4. 最新の既存スナップショットを見つける → `previous_snapshot` を設定
    │   5. _meta/snapshots/soul/{YYYY-MM-DD-HHMM}.md を書く
    │   6. 書き込み後にファイルは read-only になる(編集しない)
    └── Step 4 — ハウスキーピング(Archive Policy 参照)
```

### Invariants(不変条件)

- 些細なセッション(decisions なし)でもスナップショットを生成する。スナップショットの欠落はトレンド計算を破壊し、バグとして扱われる。
- スナップショットは同じセッションに対して 2 回書かれることはない。`archiver` がすでにスナップショットを持つセッションに対して再実行される場合、書き込みはスキップされ、ログされる。
- スナップショットは additive — 新規スナップショットを書くことは決して前のものを削除または編集しない。

---

## トレンド計算(Trend Computation)

次の Start Session で、`retrospective` は **最新の 2 つのスナップショット** を読み、次元ごとの delta を計算します。トレンド矢印は SOUL Health Report に現れます(`soul-spec.md` Health Report Format 参照)。

### Delta ルール(Delta rules)

| 条件 | トレンドマーカー |
|-----------|--------------|
| `confidence_Δ > +0.05` | ↗ rising |
| `confidence_Δ < -0.05` | ↘ falling |
| `|confidence_Δ| ≤ 0.05` | → stable |
| 現在のスナップショットにあるが前にはない次元 | 🌱 new |
| 前のスナップショットにあるが現在にはない次元 | 💤 dormant |

### 特殊状態(Special states)

retrospective は tier 遷移と衝突検出のためのバッジも emit します:

| 遷移 | バッジ | 条件 |
|------------|-------|-----------|
| 0.7 を上向きに越えた | 🌟 promoted to core | 前の tier < `core`、現在の tier = `core` |
| 0.7 を下向きに越えた | ⚠️ demoted from core | 前の tier = `core`、現在の tier < `core` |
| 衝突ゾーン | ❗ evidence ≈ challenges | `|evidence_count − challenges| ≤ 1` **かつ** `evidence_count ≥ 3` |

バッジはトレンドマーカーとスタックする — 次元は同時に ↗ と 🌟 になり得る(上昇中に promoted)。

### 最初のスナップショットの処理(Handling the first snapshot)

前のスナップショットがない場合(ブートストラップ後の最初の Start Session、または真新しい second-brain の最初のセッション)、すべての次元は 🌱 としてレンダリングされ、トレンド矢印は計算されません。Health Report ヘッダーは "First snapshot — trends will appear next session." をノートします。

---

## アーカイブポリシー(Archive Policy)

`archiver` Phase 2 Step 4 はスナップショット作成後にハウスキーピングを実行します:

1. `_meta/snapshots/soul/` 内の各ファイルで `captured_at` が **30 日より古い** ものは: `_meta/snapshots/soul/_archive/` へ移動(ファイル名を保存)
2. `_meta/snapshots/soul/_archive/` 内の各ファイルで `captured_at` が **90 日より古い** ものは: ファイルシステムから削除
3. ハウスキーピングは冪等 — 2 回走らせると同じ結果を生成

削除が安全な理由:
- Git 履歴はすべての削除されたファイルを無期限に保存する
- トレンド計算は最新の 2 つのスナップショットのみを必要とする; 深い履歴は監査用であり、アクティブなアルゴリズム用ではない
- スナップショットはローカルのみ(Notion に同期されない); 完全な監査証跡は git に存在する

---

## サイズ制約(Size Constraints)

- 各スナップショットは **典型的に <5KB** — 20 のアクティブ次元を持つ SOUL は ~2KB の YAML を生成
- 1000 スナップショット(数年の毎日セッション)≈ **合計 5MB** — git と Notion にとって無視できる
- 本文コンテンツはオプション; 空に保つとファイルサイズが半分になる
- 画像なし、バイナリデータなし、埋め込み添付なし — スナップショットは純粋な YAML + オプションの markdown

スナップショットが 10KB を超える場合、archiver は warning をログします — 通常は SOUL.md が異常な形状(>50 アクティブ次元)に成長したことを意味し、それ自体がユーザーの注意に値します。

---

## マイグレーション(Migration)

v1.7 以前にはスナップショットはありません(v1.6.2 がメカニズムを導入; v1.6.2a が安定化)。v1.6.2 以前の second-brain について:

1. `tools/migrate.py` は `_meta/journal/` をスキャンして SOUL delta ブロック(ADVISOR によって emit された `🔮 SOUL Delta` セクション)を探す
2. SOUL delta を含む各 journal エントリについて、journal エントリの date でタイムスタンプされたスナップショットを合成
3. 合成スナップショットは frontmatter に `provenance: synthetic` を持ち、retrospective がそれらを自然なスナップショットと区別できるようにする
4. マイグレーションは直近 3 ヶ月内の最も早い journal エントリで停止(ユーザー決定 #7 — 他のすべてのマイグレーションスコープと整合)。より深い履歴は再構築されない; シグナルが劣化しすぎる。
5. マイグレーション結果を `_meta/cortex/bootstrap-status.md` にログ

マイグレーションは冪等。合成スナップショットはトレンドアルゴリズムによって自然なものと同一に扱われる — `provenance` フィールドは監査用にのみ存在する。

---

## 読み取り側の責任(Reader Responsibilities)

`retrospective` は Start Session 中のスナップショットの唯一の reader です。その契約:

1. `_meta/snapshots/soul/` 内のファイルを `captured_at` 降順でソートしてリスト
2. トップ 2 ファイル(現在と前)を取る
3. スナップショットが 2 つ未満の場合、"first snapshot" 動作にフォールバック(すべての次元が 🌱 としてレンダリング)
4. 両方の YAML frontmatter をパース
5. §5 のルールに従い delta を計算
6. SOUL Health Report ブロックを emit(フォーマットは `soul-spec.md` で定義)

retrospective は通常動作中にアーカイブされたスナップショットを読みません。`_archive/` はユーザーが明示的に長期トレンドを求めた場合にのみ参照されます(例: "過去 1 年の core アイデンティティ進化を見せて")。

---

## Anti-patterns

これらは仕様により禁止されています:

1. **作成後のスナップショットファイルの編集** — スナップショットは immutable。修正は SOUL.md に行き、次のスナップショットがそれを反映する。
2. **スナップショットに SOUL 本文コンテンツを格納** — メタデータのみ。スナップショットファイルが 10KB を超えて成長する場合はバグ。
3. **「些細な」セッションのスナップショット作成をスキップ** — すべてのセッションはスナップショットを作成する。トレンドアルゴリズムは連続的な履歴に依存する; ギャップは dormancy と区別不能。
4. **タイムスタンプの捏造** — ファイル名と `captured_at` は書き込み時の実際のシステムクロックから来なければならない。手動のタイムスタンプなし、マイグレーションを除いて合成された時刻なし(マイグレーションでは `provenance: synthetic` が必須)。
5. **アクティブなスナップショットを手動削除** — アーカイブポリシーが保持を所有する。手動削除は "two most recent" reader 契約を破壊する。
6. **retrospective の外でスナップショットを読む** — 他のロールは retrospective の Health Report 出力を通らなければならない。他のエージェントによる直接読み取りは情報隔離モデルを破壊する。

---

## 制約(Constraints)

- **セッションごとに 1 つのスナップショット** — 決して 2 つではなく、決してゼロではない
- **作成後 immutable** — read-only として扱う
- **メタデータのみ** — SOUL 本文コンテンツなし
- **ファイル名のタイムスタンプ = 実際のキャプチャ時刻** — 捏造なし
- **confidence > 0.2 の次元のみ含める** — ノイズをスキップ
- **典型的に <5KB、ハード warning 閾値 <10KB**
- **30 日ホット、30-90 日アーカイブ、>90 日削除** — アーカイブポリシーは冪等
- **`archiver` Phase 2 が書き込みを所有、`retrospective` Mode 0 が読み取りを所有** — 他のロールはスナップショットファイルに触れない
- **ローカルのみ — Notion 同期なし** — スナップショットは Cortex/`_meta/` データ; 監査証跡は git に存在する

---

## 関連仕様(Related Specs)

- `references/soul-spec.md` — SOUL スキーマ、次元ライフサイクル、Health Report フォーマット消費者
- `references/session-index-spec.md` — `session_id` フィールドは `_meta/sessions/` のエントリを参照
- `references/cortex-spec.md` — 全体的な Cortex アーキテクチャ; スナップショットは v1.7 の 5 つのコアアーティファクトの 1 つ
- `references/concept-spec.md` — 兄弟 `_meta/` データレイヤー; 同じ markdown-first 原則とローカルのみ制約
- `references/eval-history-spec.md` — AUDITOR の `soul_reference_quality` 次元はスナップショット由来のトレンドシグナルを消費
- `pro/agents/archiver.md` — Phase 2 Step 3 がスナップショット書き込みを所有
- `pro/agents/retrospective.md` — Mode 0 が Health Report 用のスナップショット読み取りを所有

---

> ℹ️ **2026-04-22 更新**:EN R4.3 で修正された Tier 表の半開区間形式(gwt-spec §5.4 準拠)を同期

*本文は英語版 2026-04-22 スナップショットの翻訳。英語版が権威源。*
