# セカンドブレイン — アーキテクチャとセットアップ（v1.9）

## コアアーキテクチャ

```
git リポジトリ = 単一のストレージバックエンド、2 つの役割：
  - ローカル作業コピー（ディスク）= 真実の源、完全な記録、同時にあなたの Obsidian vault
  - GitHub リモート = バックアップ + クロスデバイス同期チャネル
CC（丞相 / 早朝官）= git pull / push をオーケストレート
```

### データチャネル

```
デスクトップ：CC ↔ ローカル作業コピー（git）
クロスデバイス：git pull（セッション開始）/ git push（セッション終了）
モバイル：git クライアント（または同期フォルダー）で inbox/ に commit、次のデスクトップ session で処理
```

### 同期ルール

**同期は素の git**：セッション開始（RETROSPECTIVE）に `git pull`、セッション終了（ARCHIVER Phase 4）に `git push`。Merge 競合は通常の git 競合。

---

## Vault ディレクトリ構造（v1.9）

```
<vault root>/
│
├── inbox/                          # 📥 ユーザー投函エリア（生材料、キャプチャ、研究ノート）
├── SOUL.md                         # 🧬 アイデンティティ — 価値観、原則、行動パターン（ルートに保持）
│
├── meta/                           # 🔧 システムメタデータ — 透明、隠しサブディレクトリなし（v1.9）
│   │
│   │  ★ カテゴリ 1：設定（あなたが書く）
│   ├── config.md                   # バックエンド設定 + migrated_to
│   ├── strategic-lines.md          # 戦略ライン定義
│   ├── extraction-rules.md         # 抽出ルール
│   ├── lint-rules.md               # 品質チェックルール
│   │
│   │  ★ カテゴリ 2：コンパイル成果物（システムが見せる）
│   ├── STATUS.md                   # グローバルステータススナップショット
│   ├── STRATEGIC-MAP.md            # 戦略マップ（プロジェクトの strategic フィールドから編集）
│   ├── MAP.md                      # 知識マップ
│   ├── sessions/INDEX.md           # セッションインデックス（hippocampus データソース）
│   ├── user-patterns.md            # ★ v1.9：vault-root から meta/ に移動
│   │
│   │  ★ カテゴリ 3：精選コンテンツ（あなたとシステムの協働）
│   ├── decisions/<YYYY-MM>/<id>.md # ★ v1.9：月サブディレクトリ、単一正規パス
│   ├── journal/<YYYY-MM-DD>.md     # ★ v1.9：時間軸 canonical
│   ├── methods/<name>.md           # メソッドライブラリ（born_from_decisions フィールド含む）
│   ├── queue/                      # ★ v1.9：inbox/ から改名
│   │   ├── to-process/.gitkeep
│   │   ├── notifications.md
│   │   └── README.md
│   │
│   │  ★ カテゴリ 4：監査ログ（システムの説明責任アーカイブ）
│   ├── compliance/violations.md    # 御史台違反記録
│   ├── eval-history/<YYYY-MM>/     # 監査統計
│   ├── snapshots/soul/<YYYY-MM-DD-HHMM>.md  # SOUL 履歴スナップショット
│   ├── lint-state.md
│   ├── lint-reports/
│   ├── extraction-log.md
│   │
│   │  ★ カテゴリ 5：ランタイム状態（システムの一時作業台）
│   ├── runtime/<sid>/              # 監査トレイル（R11/R12/R13）
│   ├── outbox/                     # オフラインセッションステージング
│   └── .merge-lock                 # 単一ファイルロック（dot-prefix はソートヒント、非表示意図ではない）
│
├── projects/{name}/                # 🎯 終点のあるプロジェクト（archived 含む、frontmatter で区別）
│   ├── index.md                    # ★ v1.9：frontmatter に lifecycle_stage + ## Journal/Decisions セクション
│   ├── tasks/                      # 次のアクション
│   └── research/                   # プロジェクト固有の研究
│       # decisions/ は meta/decisions/ に移動済み
│       # journal/ は meta/journal/ に移動済み
│
├── areas/                          # 🌊 長期的な生活領域（命名強制なし）
│   ├── README.md                   # ★ v1.9：「推奨シード、強制ではない」を説明
│   └── {name}/                     # ユーザーの実際の area
│
├── wiki/                           # 📚 ナレッジアーカイブ（v1.9 で変更なし）
│   ├── INDEX.md
│   ├── log.md
│   ├── OBSIDIAN-SETUP.md
│   ├── .templates/
│   └── {domain}/{topic}.md
│
└── templates/                      # 📋 トップレベルテンプレート（v1.9 で変更なし）
```

**v1.9 変更概要**：
- `_meta/` → `meta/`（アンダースコア接頭辞削除；透明性）
- `meta/inbox/` → `meta/queue/`（vault-root inbox/ との混同回避）
- decisions を `meta/decisions/<YYYY-MM>/<id>.md` に統合
- archive を frontmatter `lifecycle_stage: archived` で代替（projects/ に留まる）
- journal 時間軸 canonical を `meta/journal/<YYYY-MM-DD>.md` に
- `user-patterns.md` を `meta/` に移動
- areas は 10 個の空ディレクトリを事前作成しない

---

## `meta/` の理解 — 5 クラスの心智モデル（v1.9）

v1.9 RFC §3.1 により、`meta/` 内容は 5 つの大きなカテゴリに分類されます。すべて可視（`.system/` 隠し層なし）；カテゴリはドキュメント解釈のみで、ディレクトリ境界で表現しない。

| カテゴリ | 例 | 誰が書く | 誰が読む | 保存期間 |
|----------|-----|--------|--------|--------|
| **設定**（あなたが書く） | `config.md`、`strategic-lines.md`、`extraction-rules.md`、`lint-rules.md` | 人間 | 全エージェント | 永久 |
| **コンパイル成果物**（システムが見せる） | `STATUS.md`、`STRATEGIC-MAP.md`、`MAP.md`、`sessions/INDEX.md`、`user-patterns.md` | retrospective / archiver / advisor | 人間 + ROUTER | 再生成可能、削除可 |
| **精選コンテンツ**（人間 + 機械の協働） | `decisions/`、`journal/`、`methods/`、`queue/notifications.md` | 人間 + 機械の協働 | 人間 + 全エージェント | 永久 |
| **監査ログ**（システムの説明責任） | `compliance/violations.md`、`eval-history/`、`snapshots/soul/`、`lint-reports/`、`extraction-log.md` | エージェント（機械） | auditor / advisor / 時々人間 | 長期 |
| **ランタイム状態**（システムの一時作業台） | `runtime/<sid>/`、`outbox/`、`.merge-lock` | エージェント（機械） | auditor Mode 3 | 短期（30-90 日） |

**透明性原則**：lifeos はシングルユーザーシステム；システムはユーザーに対して秘密を持たない。監査トレイルやランタイムデータも可視 —— `cd meta/runtime/<sid>/` でエージェントが行った各ステップを読める。これは意図的（DR-1.9.1）。

---

## Areas — 推奨シード、強制ではない（v1.9）

v1.9 では、`areas/` は FIRST-RUN で 10 個のカテゴリを事前作成しなくなりました。代わりに、空の `areas/` ディレクトリ + 推奨シードを列挙する `README.md` を取得します：

```
career     · 仕事 / キャリア方向
product    · 取り組んでいる製品/プロジェクト
finance    · 収支、投資、税金、保険
health     · 身体、睡眠、栄養、運動
family     · 家族、パートナー、子供
social     · 友人、協力者、コミュニティ
learning   · 学習計画、スキルアップ、パーソナルブランド
ops        · デジタルインフラ、生活ワークフロー、住環境
creation   · 創作、コンテンツ、表現
spirit     · 価値観、人生の方向、精神世界
```

**システムは命名を強制しない**。あなたは：
- 該当しないものを削除
- 新しいものを追加（`art/`、`travel/`、`spiritual-practice/` 何でも）
- 自由に改名
- ゼロから始めて必要に応じて構築

lifeos の `areas/<name>/` 処理はディレクトリの存在のみを確認し、命名規約はチェックしません。

---

## キーコンセプト

### projects/ — 終点のあるもの

各プロジェクトは独自の世界を持つ：tasks、research、`index.md`（`## Journal` と `## Decisions` セクションを含む、archiver が Dataview block + Recent 5 wikilinks fallback として自動メンテナンス）。

**v1.9 変更**：プロジェクト完了時に `archive/` に **mv しない**。代わりにプロジェクトの `index.md` frontmatter に `lifecycle_stage: archived` を設定。プロジェクトは `projects/` に留まる —— それを参照するすべての wikilinks を保護。インデックスレイヤー（retrospective Mode 0 が STATUS をコンパイル、archiver Phase 1）は `lifecycle_stage` でフィルタしデフォルトビューから archived を隠す；Obsidian graph view は "archived" colorGroup でグレー化。

### areas/ — 長期的な生活領域

終点なし、deadline なし。各 area は goals、tasks、notes を持つ。プロジェクトは area を参照可能；area はプロジェクトを派生可能。

### wiki/ — ナレッジアーカイブ

旧 zettelkasten 構造を置き換え。ドメインで組織化され相互リンクされたノート + INDEX.md エントリ。特定プロジェクトに紐付かない —— プロジェクトは死に、知識は生きる。DREAM で成長：早朝官がセッション分析から再利用可能な結論を抽出して wiki ページに書き込む。**v1.9：wiki 内部は変更なし**。

### SOUL.md — アイデンティティアーカイブ

ユーザーのコア価値、原則、意思決定傾向、行動パターンをキャプチャ。諫官と翰林院が個人化アドバイスのために参照。**v1.9：vault ルートに保持**（高頻度参照 + wikilink シンプル性 `[[SOUL]]` + ~50 か所の spec 参照）。

### DREAM — ナレッジ抽出

早朝官の session-close プロセス：セッションをレビュー、再利用可能な洞察を抽出、wiki/ に永久知識として書き込む。これが一時的な分析が持続的な知識になる方法。

### decisions / methods / journal 三方相互参照（v1.9 Opt #8）

`meta/` の 3 つの artifact タイプは frontmatter フィールドで相互にリンク：

```
methods            decisions          journal
   │                  │                  │
   ├── born_from_decisions → ←──┘                  │
   │                  │                  │
   │ ←── applied_methods                │
   │                  │                  │
   │                  │ ←── referenced_decisions
   │                  │                  │
   │ ←─────────────── referenced_methods
```

逆引きクエリ（例：「このメソッドを適用した decisions は？」）は Dataview + Recent 5 wikilinks パターンを使用 —— 逆方向フィールドは維持しない。詳細は `_meta/rfc/v1.9-second-brain-structure-optimization.md` §3.8 を参照。

---

## 三省六部出力先（v1.9）

| 出力 | GitHub パス |
|------|------------|
| 決定備忘録（すべて） | `meta/decisions/<YYYY-MM>/<id>.md`（type / projects / domains / applied_methods / journal_date frontmatter 含む） |
| アクションアイテム | `projects/{project}/tasks/` または `areas/{area}/tasks/` |
| 早朝ブリーフィング | `meta/journal/<date>.md`（type_tags: [briefing] 含む） |
| 御史台/諫官レポート | `meta/journal/<date>.md`（type_tags: [auditor] / [advisor] 含む） |
| 研究 | `projects/{project}/research/` |
| ドメイン横断知識 | `wiki/{domain}/{topic}.md` |
| 目標 | `areas/{area}/goals.md` |
| セッションジャーナル（session-close） | `meta/journal/<date>.md`（type_tags: [dream] 含む） |
| Wiki 抽出（session-close） | `wiki/{domain}/{topic}.md`（早朝官） |
| グローバルステータス | `meta/STATUS.md` |
| ユーザー行動パターン | `meta/user-patterns.md`（v1.9：vault-root から移動） |

---

## クロスデバイス同期（git）

独立したクラウドメモリレイヤーはない —— すべてはこの一つの git リポジトリに markdown として存在する。

### 📥 inbox/

モバイルとデスクトップ間のドロップゾーン。モバイルでは、git クライアント（例 Working Copy）またはリポジトリに同期するフォルダーを使って、markdown ノートを `inbox/` に commit する。次のデスクトップ session の `git pull` がそれを取り込み、RETROSPECTIVE が処理する。

### 🧠 meta/STATUS.md

グローバルステータスファイル。早朝官がセッション終了時に上書きし（archive + Phase 4 `git push` の一部）、`git pull` 後に任意のデバイスで閲覧可能。

### 📋 tasks ファイル

アクティブタスクは `projects/*/tasks/` と `areas/*/tasks/` に存在。同期された作業コピー上で Obsidian / 任意のエディタを使い、任意のデバイスで読み書きできる。

### 同期メカニクス

セッション開始：`git pull`。セッション終了：`git add` + `commit` + `push`。クロスデバイスの引き継ぎは別マシンで pull するだけ；競合する編集は通常の git merge 競合。

---

## マルチ Repo ワークフロー

- **プロジェクトコード**（life_OS など）→ それぞれ独自の repo
- **プロジェクトに関する思考**（決定、ノート、tasks）→ second-brain repo

同じ CC 対話が両方のディレクトリを接続。`/save` コマンド：ファイル書き込み → cd ~/second-brain → git commit/push → プロジェクトに戻る。

---

## v1.8.x から v1.9 への移行

`/migrate-v1.9` を 1 回実行。ツールが行うこと：

1. Pre-flight チェック（git working dir clean、バージョン ≥ v1.8.0、archive に非プロジェクト内容なし）
2. per-stage dry-run サマリーを出力
3. ユーザーが `go` を確認後、8 段階を実行
4. 当日の journal にマイグレーションレポートを追記
5. 最終 `git commit`

マイグレーション完了後、`/verify-v1.9` を実行して 8 項目の受け入れ基準を確認。

詳細 RFC：`_meta/rfc/v1.9-second-brain-structure-optimization.md`

vault が v1.8.0 より古い場合（v1.6 / v1.7）、`docs/guides/cross-version-migration.md` を参照 —— v1.9 は複数世代のマイグレーションを自動チェインしない。

---

## データレイヤーなしの場合

second-brain を設定しなくても、すべての機能は通常通り動作します —— ただし永続化とクロスセッション記憶がなくなります。
