# アダプター: Google Drive

標準データモデルのオペレーションを、Google Drive に保存されたYAMLフロントマター付き `.md` ファイルに変換します。

## ファイル形式

**GitHubアダプターと同一**: YAMLフロントマター付きの .md ファイル。同じ形式、同じ構造です。つまり、ファイルはGitHubとGoogle Drive間でポータブルです — 変換なしでコピー/移動が可能です。

## ディレクトリ構造

GitHubセカンドブレイン構造のミラーで、Google Driveのフォルダ階層として構成されます：

```
second-brain/          ← Google Drive のルートフォルダ
├── inbox/
├── _meta/
├── projects/{name}/
├── areas/{name}/
├── wiki/
├── archive/
└── templates/
```

## オペレーション

すべてのオペレーションは Google Drive MCP ツールを使用します。

### Save(type, data)
1. 日付 + slugify されたタイトルからファイル名を生成
2. .md コンテンツを作成（フロントマター + 本文）
3. Google Drive MCP 経由で正しいフォルダパスにアップロード

### Update(type, id, data)
1. Google Drive MCP 経由で既存ファイルを読み取る
2. フロントマターをパースし、変更をマージ
3. `last_modified` タイムスタンプを更新
4. 更新されたファイルをアップロード（上書き）

### Archive(type, id)
1. Google Drive MCP 経由でファイルを `archive/{original-path}/` に移動

### Read(type, id)
1. Google Drive MCP 経由でファイルをダウンロード
2. フロントマター + 本文をパース
3. 構造化データを返す

### List(type, filters)
1. Google Drive MCP 経由で該当型のフォルダ内のファイルを一覧取得
2. 各ファイルのフロントマターをダウンロードしてパース
3. 指定されたフィールド値でフィルタリング

### Search(keyword)
1. Google Drive MCP 検索を使用（fullText contains '{keyword}'）
2. 一致するファイルをダウンロードしてパース

### ReadProjectContext(project_id)
1. `projects/{p}/` 配下のすべてのファイルを一覧取得してダウンロード

## 変更検出

同期用: Google Drive MCP クエリ `modifiedTime > '{last_sync_time}'`

最終同期以降に変更されたファイルのリストを返します。各ファイルをダウンロードしてパースします。

## 削除

GitHubと同様: フロントマターに `_deleted: true` をマーク。ユーザーが確認するまで、実際のDriveからの削除は行わない。

## Git 履歴なし

Google Drive にはgit履歴がありません。変更検出は `modifiedTime` のみに依存します。Driveの組み込みバージョン履歴がある程度の復旧機能を提供します。

## セットアップ

ユーザーに必要なもの：
1. Google Drive MCP が接続されていること
2. Driveに `second-brain` ルートフォルダが作成されていること
3. フォルダ構造が作成されていること（初回実行時に早朝官が作成可能）
