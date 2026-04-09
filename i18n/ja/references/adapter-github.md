# アダプター: GitHub（second-brain リポジトリ）

標準データモデルのオペレーションを、Gitリポジトリに保存されたYAMLフロントマター付き `.md` ファイルに変換します。

## ファイル形式

すべてのデータレコードは `.md` ファイルです：
- **フロントマター**（`---` マーカー間のYAML）: 構造化フィールド
- **本文**: content/textフィールド

```yaml
---
type: decision
title: "Career change feasibility"
status: decided
score: 6.8
date: 2026-04-08
project: career-transition
last_modified: "2026-04-08T15:30:00Z"
---

[奏折全文をここに記載]
```

## ディレクトリパスマッピング

| データ型 | パス | ファイル名パターン |
|-----------|------|-----------------|
| Decision（プロジェクト） | `projects/{p}/decisions/` | `{date}-{slug}.md` |
| Decision（横断） | `_meta/decisions/` | `{date}-{slug}.md` |
| Task（プロジェクト） | `projects/{p}/tasks/` | `{slug}.md` |
| Task（エリア） | `areas/{a}/tasks/` | `{slug}.md` |
| JournalEntry | `_meta/journal/` | `{date}-{type}.md` |
| WikiNote | `wiki/` | `{slug}.md` |
| Project | `projects/{p}/index.md` | 固定名 |
| Area | `areas/{a}/index.md` | 固定名 |

## オペレーション

### Save(type, data)
1. 日付 + slugify されたタイトルからファイル名を生成
2. フロントマター + 本文で .md ファイルを書き込む
3. `git add` でファイルを追加

### Update(type, id, data)
1. 既存ファイルを読み取る
2. 変更されたフィールドをフロントマターにマージ
3. `last_modified` タイムスタンプを更新
4. 書き戻す
5. `git add` でファイルを追加

### Archive(type, id)
1. ファイルを `archive/{original-path}/` に移動
2. `git add` で旧パスと新パスの両方を追加

### Read(type, id)
1. .md ファイルを読み取る
2. フロントマターを構造化データにパース
3. 本文をcontentとして返す

### List(type, filters)
1. 該当型のディレクトリのファイルをglobで検索
2. 各ファイルのフロントマターをパース
3. 指定されたフィールド値でフィルタリング
4. 一致するレコードを返す

### Search(keyword)
1. `grep -r "{keyword}" ~/second-brain/` で全ディレクトリを横断検索
2. 一致するファイルのフロントマターをパース
3. ソースパス付きで結果を返す

### ReadProjectContext(project_id)
1. `projects/{p}/index.md` を読み取る
2. `projects/{p}/tasks/*.md` をglobで検索
3. `projects/{p}/decisions/*.md` をglobで検索
4. `projects/{p}/journal/*.md` をglobで検索
5. すべてをパースして返す

## 変更検出

同期用: `git log --since="{last_sync_time}" --name-only --format=""`

最終同期以降に変更されたファイルのリストを返します。各ファイルをパースして type + id + last_modified を取得します。

## 削除

フロントマターにマーク: `_deleted: true`。ユーザーがすべてのバックエンドでの確認をするまで `git rm` は行わない。

## コミット規約

すべての書込後: `git add -A && git commit -m "[life-os] {summary}" && git push`
