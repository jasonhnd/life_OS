# セカンドブレイン — アーキテクチャとセットアップ

## コアアーキテクチャ

```
GitHub second-brain（ディスク）= 真実の源、完全な記録
Notion（メモリ）= 軽量ワーキングメモリ、モバイルでのアクティブトピック
CC（丞相 / 早朝官）= 両側に触れる唯一の役割
```

### データチャネル

```
モバイル: Claude.ai ↔ Notion MCP
デスクトップ: CC ↔ GitHub second-brain + Notion MCP
```

### 同期ルール

**git commit = Notion 更新、機械的に紐づけ。** ファイル変更が同期をトリガーし、純粋なチャットではトリガーしない。

---

## GitHub second-brain ディレクトリ

```
second-brain/
│
├── inbox/                    # 📥 未処理（キャプチャ、資料、メモ、生のリサーチ）
│
├── _meta/                    # 🔧 システムメタデータ
│   ├── STATUS.md             # グローバルステータスのスナップショット
│   ├── MAP.md                # ナレッジマップ
│   ├── decisions/            # 横断的な重大な決定
│   ├── journal/              # 早朝の報告、御史台/諫官レポート
│   ├── extraction-rules.md
│   ├── extraction-log.md
│   ├── lint-rules.md
│   ├── lint-state.md
│   ├── lint-reports/
│   └── roles/                # システム役割の定義
│
├── projects/{name}/          # 🎯 終点のあるもの
│   ├── index.md              # 目標、ステータス、関連エリア
│   ├── tasks/                # ネクストアクション
│   ├── decisions/            # プロジェクト固有の奏折
│   ├── research/             # プロジェクト固有のリサーチ
│   └── journal/              # プロジェクト固有のログ
│
├── areas/{name}/             # 🌊 継続的な生活領域
│   ├── index.md              # 方向性、関連プロジェクト
│   ├── goals.md              # 目標
│   ├── tasks/                # エリアタスク
│   └── notes/                # エリアノート
│
├── wiki/                     # 📚 横断的知識ネットワーク
│
├── archive/                  # 🗄️ 完了プロジェクトのアーカイブ
│
└── templates/                # 📋 テンプレート
```

## エリア一覧 (areas/)

```
career/    product/    finance/    health/    family/
social/    learning/   ops/        creation/  spirit/
```

---

## 主要コンセプト

### _meta/ — システムメタデータ

脳についての脳。以下を含みます：
- **STATUS.md**: すべてのプロジェクトとエリアにわたる現在の状況のグローバルスナップショット。セッション終了時に早朝官が更新。
- **MAP.md**: wiki/ にわたるコンセプトをリンクするナレッジマップ。
- **decisions/**: 単一のプロジェクトに属さない横断的な決定。
- **journal/**: システムレベルのログ — 早朝の報告、御史台と諫官のレポート。
- **roles/**: 品質管理のためのシステム役割定義（御史台、史官、門下省当番）。
- **lint-***: セカンドブレイン自体の品質チェックルールとレポート。
- **extraction-***: 生の素材からインサイトを抽出するためのルールとログ。

### projects/ — 終点のあるもの

各プロジェクトは独自の自己完結した世界を持ちます：タスク、決定、リサーチ、ジャーナル。プロジェクトが完了すると、フォルダ全体がarchive/に移動します。wiki/に抽出された知識はそのまま残り、成長を続けます。

### areas/ — 継続的な生活領域

終点なし、期限なし。各エリアには目標、タスク、ノートがあります。プロジェクトはエリアを参照でき、エリアはプロジェクトを生み出せます。

### wiki/ — 横断的知識

以前のzettelkasten構造を置き換えます。相互リンクされたノートのフラットまたは浅いネスト構造のwikiです。プロジェクトに縛られない — プロジェクトは終わるが、知識は生き続ける。

---

## 三省六部の出力先

| 出力 | GitHub パス |
|--------|------------|
| 決裁の奏折（プロジェクト） | `projects/{p}/decisions/` |
| 決裁の奏折（横断） | `_meta/decisions/` |
| アクションアイテム | `projects/{p}/tasks/` または `areas/{a}/tasks/` |
| 早朝の報告 | `_meta/journal/` |
| 御史台/諫官レポート | `_meta/journal/` |
| リサーチ | `projects/{p}/research/` |
| 横断的知識 | `wiki/` |
| 目標 | `areas/{a}/goals.md` |
| グローバルステータス | `_meta/STATUS.md` |

---

## Notion メモリ（4コンポーネント）

### 📬 Inbox（データベース）

モバイルとデスクトップ間のメッセージキュー。フィールド: Content / Source (Mobile/Desktop) / Status (Pending/Synced) / Time。

### 🧠 Current Status（ページ）

`_meta/STATUS.md` のミラー。セッション終了時にCCが上書き。

### 📝 Working Memory（トピックページ）

アクティブなトピックごとに1ページ（約5-10件）。アクティブでなくなったら、GitHubにアーカイブしてNotionから削除。

### 📋 Todo Board（データベース）

projects/*/tasks/ と areas/*/tasks/ から同期されたアクティブなタスク。モバイルで閲覧・チェックが可能。

---

## マルチリポジトリワークフロー

- **プロジェクトコード**（EIP、life_OS など）→ それぞれ独自のリポジトリ
- **プロジェクトについての思考**（決定、メモ、タスク）→ second-brain リポジトリ

同じCC会話が両方のディレクトリに接続します。`/save` コマンド: ファイルを書き込む → cd ~/second-brain → git commit/push → プロジェクトに戻る。

---

## データレイヤーなしの場合

セカンドブレインを設定しない場合でも、すべての機能は通常通り動作します — 永続化やクロスセッションメモリがないだけです。
