# アダプター: Notion

標準データモデルのオペレーションを、Notion MCP 経由で Notion データベースとページに変換します。

## Notion 構造

Notionは完全なストレージバックエンド（選択された場合）としても、トランスポートレイヤー（GitHub/GDrive と併用する場合）としても機能します。

### 完全バックエンドとして（Notionのみ）

全6データ型がNotionデータベースにマッピングされます：

| データ型 | Notion データベース |
|-----------|----------------|
| Decision | 🤔 Decisions |
| Task | ✅ Tasks |
| JournalEntry | 📓 Journal |
| WikiNote | 📚 Wiki |
| Project | 🎯 Projects |
| Area | 🌊 Areas |

### トランスポートレイヤーとして（GitHub/GDrive と併用）

3つのコンポーネントのみを使用：
- 📬 Inbox（データベース）: デバイス間のメッセージキュー
- 🧠 Status Dashboard（ページ）: `_meta/STATUS.md` のミラー
- 🗄️ Archive: 読み取り専用のアーカイブアクセス

## フィールドマッピング

### Decision → 🤔 Decisions

| 標準フィールド | Notion プロパティ | Notion 型 |
|---------------|----------------|-------------|
| title | Title | Title |
| type | 流程類型 | Select: 簡単決裁 / 三省六部 |
| ministries | 啓用部門 | Multi-select |
| score | 総合評分 | Number |
| veto_count | 封駁回数 | Number |
| status | Status | Select: Considering / Decided / Reversed |
| category | Category | Select |
| outcome | Outcome | Select: Good / Neutral / Bad / TBD |
| date | Date | Date |
| area | Area | Relation → Areas |
| content | Page body | Page content |

### Task → ✅ Tasks

| 標準フィールド | Notion プロパティ | Notion 型 |
|---------------|----------------|-------------|
| title | Title | Title |
| status | Status | Select: To Do / In Progress / Waiting / Done / Cancelled |
| priority | Priority | Select: P0 / P1 / P2 / P3 |
| due_date | Due Date | Date |
| context | Context | Select |
| energy | Energy | Select |
| project | Project | Relation → Projects |
| area | Area | Relation → Areas |

### JournalEntry → 📓 Journal

| 標準フィールド | Notion プロパティ | Notion 型 |
|---------------|----------------|-------------|
| title | Title | Title |
| date | Date | Date |
| type | Tags | Multi-select |
| mood | Mood | Select |
| energy | Energy | Select |
| content | Page body | Page content |

### WikiNote → 📚 Wiki

| 標準フィールド | Notion プロパティ | Notion 型 |
|---------------|----------------|-------------|
| title | Title | Title |
| tags | Tags | Multi-select |
| content | Page body | Page content |

### Project → 🎯 Projects

| 標準フィールド | Notion プロパティ | Notion 型 |
|---------------|----------------|-------------|
| name | Name | Title |
| status | Status | Select |
| priority | Priority | Select |
| deadline | Deadline | Date |
| area | Area | Relation → Areas |

### Area → 🌊 Areas

| 標準フィールド | Notion プロパティ | Notion 型 |
|---------------|----------------|-------------|
| name | Name | Title |
| description | Description | Text |
| status | Status | Select |
| review_cycle | Review Cycle | Select |

## オペレーション

すべてのオペレーションは Notion MCP ツールを使用します。

### Save(type, data)
1. 上記のマッピングテーブルに従い、フィールドをNotionプロパティにマッピング
2. `notion-create-pages` で parent = 対応するデータベースを指定
3. 本文コンテンツ → ページコンテンツ

### Update(type, id, data)
1. `notion-update-page` で page_id と変更されたプロパティを指定
2. 本文コンテンツの変更 → `update_content` コマンド

### Archive(type, id)
1. ステータスをarchived/doneに更新
2. または `notion-move-pages` でページをArchiveデータベースに移動

### Read(type, id)
1. `notion-fetch` でページIDを指定
2. Notionプロパティを標準フィールドにマッピング

### List(type, filters)
1. 対応するデータベースに対して `notion-search` または `notion-query-database-view`
2. 結果を標準フィールドにマッピング

### Search(keyword)
1. `notion-search` で query = keyword を指定
2. 結果を標準フィールドにマッピングし、ソースデータベースを注記

### ReadProjectContext(project_id)
1. プロジェクトページを読み取る
2. プロジェクトリレーションでフィルタしてタスクをクエリ
3. プロジェクトでフィルタして決定をクエリ
4. プロジェクトでフィルタしてジャーナルをクエリ

## 変更検出

同期用: `notion-search` または `notion-query-database-view` で `last_edited_time > last_sync_time` でフィルタリング

## 削除

同じ原則: ステータス変更によるソフトデリート。ユーザーが確認するまで `notion-move-pages` でゴミ箱に移動しない。

## セットアップ

ユーザーに必要なもの：
1. Notion MCP が接続されていること（Claude.ai: 設定 → 接続アプリ → Notion。Claude Code: MCP設定）
2. Notionに必要なデータベースが作成されていること（または提供されたテンプレートを使用）
3. データベースIDは `notion-search` で名前によりランタイムで検出 — ハードコーディング不要
