# データレイヤーアーキテクチャ

全エージェントはデータの読み書き時にこのファイルを参照する。

## 二層ストレージ

- **GitHubセカンドブレイン（ディスク）**：信頼できる唯一の情報源、全ての完全な記録と履歴を保存
- **Notion（メモリ）**：軽量なワーキングメモリ、現在アクティブなトピックのコンテキストのみを保存、モバイルからの深い議論をサポート
- **CC（丞相/早朝官）が両側に触れる唯一の役職**であり、全ての同期を担当

## データチャネル

```
モバイル: Claude.ai ↔ Notion MCP（ここでチャットと保存）
デスクトップ: CC ↔ GitHubセカンドブレイン + Notion MCP（CCが全同期を処理）
```

## 同期ルール

**git commit = Notion更新、機械的に結合、判断不要。**

セカンドブレインリポジトリにファイル変更がある場合、Notionに同期する。ファイルを生成しない純粋なチャット議論は同期をトリガーしない。

---

## GitHubディレクトリ構造

3つの方法論の融合：**GTDが行動を駆動し、PARAが構造を組織し、Zettelkastenが知識を成長させる。**

```
second-brain/
│
├── inbox/                          # GTDエントリー：未処理アイテムがまずここに入る
│
├── projects/                       # PARA·P：目標と期限のあるもの
│   └── {project}/
│       ├── index.md               # 目標、状態、関連エリア
│       ├── tasks/                 # ネクストアクション
│       ├── decisions/             # 三省六部の奏折
│       ├── notes/                 # 作業ノート
│       └── research/              # プロジェクト固有の調査
│
├── areas/                          # PARA·A：維持すべき継続的な生活領域
│   └── {area}/
│       ├── index.md               # 方向性、関連プロジェクト、現在の状態
│       ├── goals.md               # 目標
│       └── tasks/                 # プロジェクトに属さないエリアタスク
│
├── zettelkasten/                   # 知識の成長
│   ├── fleeting/                  # フリーティングアイデア
│   ├── literature/                # 読んだもの、学んだこと
│   └── permanent/                 # 自分の洞察、相互リンク
│
├── records/                        # ライフデータ
│   ├── journal/                   # 日誌、早朝ブリーフィング、レビュー、御史台/諫官報告
│   ├── meetings/
│   ├── contacts/
│   ├── finance/
│   └── health/
│
├── gtd/                            # GTDシステム
│   ├── waiting/                   # 他者待ち
│   ├── someday/                   # いつか/多分
│   └── reviews/                   # 週次/月次レビュー
│
├── archive/                        # 完了プロジェクトはここへ移動
│
└── templates/
```

## エリアリスト（areas/）

```
areas/
├── career/        # キャリア開発
├── product/       # プロダクト＆起業
├── finance/       # 財務管理
├── health/        # 健康
├── family/        # 家族
├── social/        # 社会的関係
├── learning/      # 学習
├── ops/           # 生活運営
├── creation/      # クリエイティブワーク
├── spirit/        # 精神的幸福
└── work-project/  # 現在の仕事プロジェクト（例）
```

---

## 三省六部出力先

| 出力 | GitHubパス |
|--------|------------|
| 判断の奏折 | `projects/{p}/decisions/` or `areas/{a}/decisions/` |
| アクションアイテム | `projects/{p}/tasks/` or `areas/{a}/tasks/` |
| レビュー / 御史台 / 諫官報告 | `records/journal/` |
| 調査分析 | `projects/{p}/research/` or `zettelkasten/literature/` |
| 一般的洞察 | `zettelkasten/permanent/` |
| 目標 | `areas/{a}/goals.md` |

---

## Notionメモリ（4コンポーネント）

### 📬 インボックス（データベース）

モバイルとデスクトップ間の情報受け渡し用メッセージキュー。

| フィールド | 型 | 説明 |
|-------|------|-------------|
| Content | Title | 一文またはキーポイント |
| Source | Select | Mobile / Desktop |
| Status | Select | Pending / Synced |
| Time | Created time | 自動 |

### 🧠 現在の状態（ページ）

グローバルスナップショット、各セッション終了時にCCが上書き。含む：進行中のもの、直近の重要判断、オープンな質問、今週の注力。

### 📝 ワーキングメモリ（トピックページ）

アクティブなトピックごとに1ページ。含む：背景、現在のステージ、重要な判断、技術的アイデア、オープンな質問、ネクストステップ。約5-10のアクティブなトピック。アクティブでなくなったらGitHubにアーカイブし、Notionから削除。

### 📋 Todoボード（データベース）

セカンドブレインのtasks/から同期されたアクティブタスクリスト。モバイルで閲覧・チェック可能。CCが次のセッションでGitHubに逆同期。

| フィールド | 型 | 説明 |
|-------|------|-------------|
| Task | Title | タスク名 |
| Project | Select | 親プロジェクト |
| Status | Select | Todo / In Progress / Done |
| Priority | Select | P0 / P1 / P2 |
| Due | Date | 期限 |

---

## 早朝官データ操作

### 庶務モード（会話開始時）

```
1. ~/second-brain/inbox/ を読む（未処理アイテム）
2. ~/second-brain/projects/ と areas/ の index.md ファイルを読む（現在の状態）
3. second-brain/projects/*/decisions/ で関連する履歴判断を検索
4. user-patterns.md を読む
5. Notion 📬 インボックスを確認（モバイルからの新メッセージ） → second-brain/inbox/ に取り込む
6. プラットフォーム認識 + バージョンチェック
```

### 退朝モード（プロセス終了時）

```
1. 奏折 → second-brain/projects/{p}/decisions/ or areas/{a}/decisions/
2. アクションアイテム → second-brain/projects/{p}/tasks/ or areas/{a}/tasks/
3. 御史台報告 → second-brain/records/journal/
4. 諫官報告 → second-brain/records/journal/
5. user-patterns.md を更新
6. git add + commit + push（セカンドブレインリポジトリへ）
7. Notion同期：🧠 現在の状態 + 📝 関連トピックのワーキングメモリを更新
```

### レビューモード

```
1. second-brain/projects/*/tasks/ を走査して完了率を計算
2. second-brain/areas/*/goals.md で目標の進捗を読む
3. second-brain/records/journal/ で直近の日誌を読む
4. second-brain/gtd/reviews/ で前回のレビュー記録を読む
5. ファイルからメトリクスダッシュボードを計算
```

## 丞相の履歴検索

丞相はもはやデータを直接照会しない — 早朝官の庶務モードが全コンテキストを準備済み。

## 諫官データ取得

```
1. user-patterns.md を読む
2. second-brain/records/journal/ 直近3件の諫官報告を読む
3. second-brain/projects/*/decisions/ 直近5件の判断を読む
4. second-brain/projects/*/tasks/ を走査して完了率を計算
```

## 劣化ルール

- セカンドブレインリポジトリに到達不能 → 「⚠️ セカンドブレイン利用不可、今回のセッション出力は未アーカイブ」と注記
- Notion利用不可 → モバイル同期のみ影響、コア機能には影響なし
- 両方とも利用不可 → 通常通り動作、出力は会話に表示されるが永続化されない
