# 標準データモデル

Life OS のすべてのデータ操作はこれらの標準型とインターフェースを使用します。アダプターがこれらをプラットフォーム固有の呼び出しに変換します。

## データ型

### Decision

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| id | string | 自動 | 一意識別子（ファイル名またはデータベースID） |
| title | string | はい | 件名（20文字以内） |
| type | enum | はい | `simple` / `3d6m`（三省六部） |
| ministries | string[] | いいえ | 起動された部門 |
| score | number | いいえ | 総合スコア（1-10） |
| veto_count | number | いいえ | 門下省の封駁回数 |
| status | enum | はい | `considering` / `decided` / `reversed` |
| category | enum | いいえ | `career` / `finance` / `product` / `tech` / `family` / `life` / `health` |
| outcome | enum | いいえ | `good` / `neutral` / `bad` / `tbd` |
| date | date | はい | 決定日 |
| project | string | いいえ | 関連プロジェクト |
| area | string | いいえ | 関連エリア |
| last_modified | datetime | 自動 | 最終更新タイムスタンプ |
| content | text | はい | 奏折全文（本文） |

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

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| id | string | 自動 | |
| title | string | はい | エントリタイトル |
| date | date | はい | エントリ日 |
| type | enum | はい | `morning-court` / `censorate` / `remonstrator` / `inspection` / `manual` |
| mood | enum | いいえ | `great` / `good` / `neutral` / `low` / `bad` |
| energy | enum | いいえ | `high` / `medium` / `low` |
| tags | string[] | いいえ | |
| last_modified | datetime | 自動 | |
| content | text | はい | レポート全文（本文） |

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

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| id | string | 自動 | |
| name | string | はい | プロジェクト名 |
| status | enum | はい | `planning` / `active` / `on-hold` / `done` / `dropped` |
| priority | enum | いいえ | `p0` / `p1` / `p2` / `p3` |
| deadline | date | いいえ | |
| area | string | いいえ | 関連エリア |
| last_modified | datetime | 自動 | |
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

---

## 標準オペレーション

すべてのエージェントがこれらのオペレーションを使用します。アダプターがプラットフォーム固有の呼び出しに変換します。

| オペレーション | シグネチャ | 説明 |
|-----------|-----------|-------------|
| **Save** | `Save(type, data)` | 新規レコードの作成 |
| **Update** | `Update(type, id, data)` | 既存レコードの変更 |
| **Archive** | `Archive(type, id)` | アーカイブへ移動 |
| **Read** | `Read(type, id)` | 単一レコードの取得 |
| **List** | `List(type, filters)` | フィルタに一致するレコードの取得 |
| **Search** | `Search(keyword)` | 全型にわたる全文検索 |
| **ReadProjectContext** | `ReadProjectContext(project_id)` | バッチ読取: プロジェクトインデックス + タスク + 決定 + ジャーナル |

---

## マルチバックエンドルール

### バックエンド選択

ユーザーは1つ、2つ、または3つのバックエンドを選択します。複数選択時は、1つが自動的に**プライマリ**（読取 + 書込）に指定され、残りは**同期**（書込のみ）となります。

**自動選択ルール**: GitHub > Google Drive > Notion

| 構成 | プライマリ | 同期 |
|--------|---------|------|
| GitHub のみ | GitHub | — |
| GDrive のみ | GDrive | — |
| Notion のみ | Notion | — |
| GitHub + Notion | GitHub | Notion |
| GitHub + GDrive | GitHub | GDrive |
| GDrive + Notion | GDrive | Notion |
| 全3つ | GitHub | GDrive + Notion |

### 書込順序

1. まずプライマリバックエンドに書き込む
2. 次に各同期バックエンドに順番に書き込む
3. いずれかの同期バックエンドが失敗した場合 → `⚠️ [バックエンド] 書込失敗` と注記し、`_meta/sync-log.md` にログを記録し、他のバックエンドへの処理を続行する
4. 次のセッションで失敗した書込を自動リトライする

### 読取順序

1. プライマリバックエンドから読み取る
2. プライマリが利用不可または検索結果が空の場合 → 同期バックエンドを順番に試行する
3. 検索結果にはどのバックエンドからのものかを注記する

---

## 同期プロトコル

### セッション開始（早朝官のハウスキーピング）

```
0. _meta/config.md を読取 → バックエンドリストと最終同期タイムスタンプを取得
1. 設定済みの各バックエンドの利用可能性を確認：
   - GitHub: git リポジトリにアクセス可能か確認（git status）
   - GDrive: Google Drive MCP が接続されているか確認（list を試行）
   - Notion: Notion MCP が接続されているか確認（search を試行）
   利用不能なバックエンドは今 session では SKIPPED とマーク。
   プライマリが利用不能な場合、次の利用可能なバックエンドを暫定的に昇格させる。
   ログ: 「💾 バックエンド: GitHub ✅ | GDrive ❌ (MCP未接続) | Notion ✅」
2. 利用可能な各同期バックエンドについて：
   - 「[このプラットフォームの last_sync_time] 以降に変更されたアイテム」をクエリ
   - GitHub: git log --since
   - GDrive: modifiedTime > last_sync_time
   - Notion: last_edited_time > last_sync_time
3. 変更を比較：
   - 1つのバックエンドのみがアイテムを変更 → それを採用
   - 2つのバックエンドが同一アイテムを変更 → last_modified が勝つ
   - 時間差 < 1分 → CONFLICT としてマーク、両方のバージョンを保持
4. 勝利した変更をプライマリバックエンドに適用
5. プライマリの状態をすべての同期バックエンドにプッシュ
6. _meta/sync-log.md に同期結果を更新
7. _meta/config.md のこのプラットフォームの last_sync_time を更新（他のプラットフォームのタイムスタンプには触れない）
```

### セッション終了（早朝官のラップアップ）

```
1. すべての出力をプライマリバックエンドに書き込む
2. すべての出力を各同期バックエンドに書き込む
3. _meta/config.md の last_sync_time を更新
4. いずれかのバックエンドが失敗 → ログ記録、ブロックしない
```

---

## 競合解決

| 状況 | アクション |
|-----------|--------|
| 1つのバックエンドが変更 | その変更を採用 |
| 2つのバックエンドが同一アイテムを変更、時間差 > 1分 | last_modified が勝つ（最後の書込が勝つ） |
| 2つのバックエンドが同一アイテムを変更、時間差 ≤ 1分 | CONFLICT: 両方のバージョンを保持、丞相がユーザーに選択を求める |
| ユーザーが競合を解決 | 勝利バージョンをすべてのバックエンドにプッシュ |

---

## 削除ルール

- **削除はバックエンド間で同期されない**
- 1つのバックエンドでアイテムが削除された場合 → 他のバックエンドは `_deleted: true` をマーク（ソフトデリート）
- 次のセッションで、丞相がユーザーに確認: 「アイテムXが [バックエンド] で削除されました。すべてのバックエンドから削除しますか？」
- ユーザーが承認 → すべてのバックエンドでハードデリート
- ユーザーが拒否 → 削除されたバックエンドで復元

---

## 障害処理

| シナリオ | 処理 |
|----------|---------|
| 書込時にバックエンドがオフライン | そのバックエンドをスキップ、⚠️ を注記、sync-log.md にログ。次のセッションで自動リトライ。 |
| 同期中にクラッシュ | 次回起動時: すべてのバックエンド間で last_modified を比較、不整合を検出、最新のものから自動修復。 |
| 1つのバックエンドでデータ破損 | 丞相が異常を検出、ユーザーに確認: 「[他のバックエンド] から復元しますか？」 |
| 新しいデバイス | 設定は _meta/config.md に存在。Git clone → 設定準備完了。セカンドブレインがない場合 → セッションレベルの設定。 |
| 新しいバックエンドを追加 | 丞相が確認: 「[プライマリ] から [新しいバックエンド] へ既存データを同期しますか？」 |
| バックエンドを削除 | 丞相が確認: 「[削除されたバックエンド] のデータを保持しますか、クリーンアップしますか？」 |

---

## 設定

`_meta/config.md`（セカンドブレインリポジトリ内）に保存:

```yaml
storage:
  backends:
    - type: github
      role: primary
    - type: notion
      role: sync
  sync_log:
    - platform: claude-code
      last_sync: "2026-04-10T15:30:00Z"
    - platform: gemini-cli
      last_sync: "2026-04-10T14:00:00Z"
```

**プラットフォームごとの同期タイムスタンプ**：各プラットフォームは自身の `last_sync` 時刻を記録する。Gemini CLI が session を開始した場合、**自身の** `last_sync` を読み取り、その時刻以降の変更をクエリする — Claude Code の最終同期時刻ではない。これにより、ユーザーがプラットフォームを交互に使用した際に変更の見落としを防ぐ。

セカンドブレインがない場合 → 設定はセッションコンテキストに保存され、丞相が新しいセッションごとに確認します。

---

## 制約事項

- **複数の session が同時にセカンドブレインを操作できる** outbox パターンを使用。各 session は自身の outbox ディレクトリ（`_meta/outbox/{session-id}/`）に書き込む。次に上朝する session が全 outbox をメイン構造にマージする。共有ファイル（STATUS.md、user-patterns.md、index.md）への直接書き込みは、上朝時の Outbox マージステップでのみ行われる。
- **session-id フォーマット**：`{platform}-{YYYYMMDD}-{HHMM}`、退朝時に生成（session 開始時ではない）。例：`claude-20260412-1700`、`gemini-20260412-1900`。
- **Outbox マージロック**：マージ中は `_meta/.merge-lock` を書き込む。存在し5分未満の場合はマージをスキップして通常通り続行する。マージ完了後に削除する。
- **空の session**：session に出力がない場合（意思決定、タスク、ジャーナルエントリがない）、outbox を作成しない。
- モバイルデバイスは Notion inbox または GDrive inbox 経由で書き込み、構造化データへの直接書き込みは行わない
- すべてのアダプターは7つの標準オペレーションをサポートしなければならない

### Outbox manifest フォーマット

各 outbox ディレクトリには `manifest.md` が含まれる：

```yaml
---
session_id: "claude-20260412-1700"
platform: claude-code
model: opus
projects: [gcsb, eip]
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

## Target: projects/gcsb/index.md
## Fields to update:
- Phase: "v5.4 deployed"
- Current focus: "打磨计划书到对外版本"
```

### Patterns Delta フォーマット

`patterns-delta.md` は `user-patterns.md` に追記する内容を記録する：

```markdown
# Patterns Delta — append to user-patterns.md

### [2026-04-12] New pattern: decision speed increasing
Source: Remonstrator
Observation: Last 3 decisions made after first round of clarification.
```
