# セカンドブレイン — アーキテクチャとセットアップ

## コアアーキテクチャ

```
GitHubセカンドブレイン（ディスク）= 信頼できる唯一の情報源、完全な記録
Notion（メモリ）= 軽量なワーキングメモリ、モバイルでアクティブなトピック
CC（丞相/早朝官）= 両側に触れる唯一の役職
```

### データチャネル

```
モバイル: Claude.ai ↔ Notion MCP
デスクトップ: CC ↔ GitHubセカンドブレイン + Notion MCP
```

### 同期ルール

**git commit = Notion更新、機械的に結合。** ファイル変更は同期をトリガーする。純粋なチャットはトリガーしない。

---

## GitHubセカンドブレインディレクトリ

3つの方法論の融合：**GTDが行動を駆動し、PARAが構造を組織し、Zettelkastenが知識を成長させる。**

```
second-brain/
├── inbox/                    # GTDエントリー：未処理アイテムがまずここに入る
├── projects/{project}/       # PARA·P：目標と期限のあるもの
│   ├── index.md             # 目標、状態、関連エリア
│   ├── tasks/               # ネクストアクション
│   ├── decisions/           # 三省六部の奏折
│   ├── notes/               # 作業ノート
│   └── research/            # プロジェクト固有の調査
├── areas/{area}/             # PARA·A：維持すべき継続的な生活領域
│   ├── index.md             # 方向性、関連プロジェクト
│   ├── goals.md             # 目標
│   └── tasks/               # プロジェクトに属さないエリアタスク
├── zettelkasten/             # 知識の成長
│   ├── fleeting/            # フリーティングアイデア
│   ├── literature/          # インプット（読んだもの）
│   └── permanent/           # アウトプット（自分の洞察、相互リンク）
├── records/                  # ライフデータ
│   ├── journal/             # 日誌、早朝ブリーフィング、御史台/諫官報告
│   ├── meetings/
│   ├── contacts/
│   ├── finance/
│   └── health/
├── gtd/                      # GTDシステム
│   ├── waiting/             # 他者待ち
│   ├── someday/             # いつか/多分
│   └── reviews/             # レビュー記録
├── archive/                  # 完了プロジェクトはここへ移動
└── templates/
```

## エリアリスト（areas/）

```
career/    product/    finance/    health/    family/
social/    learning/   ops/        creation/  spirit/
```

---

## GTDフロー

```
何か思いつく → inbox/
  ├── 行動可能、プロジェクトに属する → projects/{p}/tasks/
  ├── 行動可能、エリアに属する → areas/{a}/tasks/
  ├── 他者待ち → gtd/waiting/
  ├── 後で → gtd/someday/
  ├── 知識であってタスクではない → zettelkasten/
  └── 不要 → 削除
```

## Zettelkastenの成長

```
フリーティングアイデア → zettelkasten/fleeting/
記事を読んだ → zettelkasten/literature/
  → 洞察を蒸留 → zettelkasten/permanent/（既存ノートにリンク）
```

## プロジェクト → 知識のブリッジ

プロジェクトがアーカイブされる時、作業ノートは一緒に移動する。永久ノートはzettelkastenに残り、成長を続ける。

---

## Notionメモリ（3コンポーネント）

### 📬 インボックス（データベース）

モバイルとデスクトップ間のメッセージキュー。フィールド：Content / Source（Mobile/Desktop）/ Status（Pending/Synced）/ Time。

### 🧠 現在の状態（ページ）

グローバルスナップショット、各セッション終了時にCCが上書き。含む：進行中のもの、直近の判断、オープンな質問、今週の注力。

### 📝 ワーキングメモリ（トピックページ）

アクティブなトピックごとに1ページ（約5-10）。含む：背景、現在のステージ、重要な判断、技術的アイデア、オープンな質問、ネクストステップ。アクティブでなくなったらGitHubにアーカイブし、Notionから削除。

---

## マルチリポジトリワークフロー

- **プロジェクトコード**（EIP、life_OSなど）→ それぞれ独自のリポジトリ
- **プロジェクトについての思考**（判断、ノート、タスク）→ セカンドブレインリポジトリ

同一のCC会話が両方のディレクトリを接続する。`/save`コマンド：ファイル書き込み → cd ~/second-brain → git commit/push → プロジェクトに復帰。

---

## 三省六部出力先

| 出力 | GitHubパス |
|--------|------------|
| 判断の奏折 | `projects/{p}/decisions/` |
| アクションアイテム | `projects/{p}/tasks/` |
| レビュー / 御史台 / 諫官 | `records/journal/` |
| 調査 | `zettelkasten/literature/` |
| 一般的洞察 | `zettelkasten/permanent/` |
| 目標 | `areas/{a}/goals.md` |

---

## データレイヤーなしの場合

セカンドブレインをセットアップしなくても、全機能は通常通り動作します。永続化とセッション間メモリが利用できないだけです。
