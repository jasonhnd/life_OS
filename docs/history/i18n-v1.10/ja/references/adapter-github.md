# アダプター: GitHub（second-brain リポジトリ）

標準データモデルのオペレーションを、Gitリポジトリに保存されたYAMLフロントマター付き `.md` ファイルに変換します。

## ファイル形式

すべてのデータレコードは `.md` ファイルです：
- **フロントマター**（`---` マーカー間のYAML）: 構造化フィールド
- **本文**: content/textフィールド

```yaml
---
id: dec-2026-04-08-001
title: "Career change feasibility"
type: change
projects: [career-transition]
domains: [governance]
reviewed_by: REVIEWER
reviewed_at: 2026-04-08
decision: "<one-line decision>"
rationale: "<why>"
applied_methods: []
journal_date: 2026-04-08
---

[奏折全文をここに記載]
```

## ディレクトリパスマッピング

| データ型 | パス | ファイル名パターン |
|-----------|------|-----------------|
| Decision（v1.9 統合） | `meta/decisions/{YYYY-MM}/` | `dec-{YYYY-MM-DD}-{NNN}.md` |
| Task（プロジェクト） | `projects/{p}/tasks/` | `{slug}.md` |
| Task（エリア） | `areas/{a}/tasks/` | `{slug}.md` |
| JournalEntry（v1.9 時間軸） | `meta/journal/` | `{YYYY-MM-DD}.md`（日次単一ファイル、複数エントリ追記） |
| WikiNote | `wiki/` | `{slug}.md` |
| Project | `projects/{p}/index.md` | 固定名（lifecycle_stage frontmatter 含む；archived も `projects/` に残る） |
| Area | `areas/{a}/index.md` | 固定名 |
| UserPatterns（v1.9） | `meta/user-patterns.md` | 固定名（v1.9 で root から移動） |

> **v1.9 変更**：決定は `meta/decisions/{YYYY-MM}/` に統合（`projects/*/decisions/` 分割なし）；journal は時間軸 canonical（`projects/*/journal/` なし）；archived プロジェクトは frontmatter で `projects/` に残る（`archive/` なし）；`user-patterns.md` は `meta/` に移動。

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

**v1.9 セマンティクス分割**（DR-1.9.4）：
- **プロジェクト**：移動しない。`projects/{id}/index.md` frontmatter に `lifecycle_stage: archived` + `archived_at` + `archived_at_source` を設定。wikilinks 保護のため `projects/` に残す。`git add projects/{id}/index.md`。
- **その他の型**（sessions、eval など）：各ツリー内の legacy サブアーカイブ（例 `meta/eval-history/_archive/`）。プロジェクト archive ではなく、有効なまま。

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
3. `meta/decisions/*/*.md`（v1.9、projects frontmatter でフィルタ） をglobで検索
4. `meta/journal/*.md`（v1.9、projects frontmatter でフィルタ） をglobで検索
5. すべてをパースして返す

## 変更検出

同期用: `git pull` がリモート変更をマージ；変更一覧は `git log ORIG_HEAD..HEAD --name-only --format=""`

最終同期以降に変更されたファイルのリストを返します。各ファイルをパースして type + id + last_modified を取得します。

## 削除

ファイルを削除して `git rm`、commit する；削除は他の変更と同様に次の push/pull で伝播。単一バックエンド —— ソフト削除 `_deleted: true` トゥームストーンやクロスバックエンド確認はなし。

## コミット規約

### 退朝時（outbox への書き込み）

```bash
git add meta/outbox/{session-id}/
git commit -m "[life-os] session {session-id} output"
git push
```

outbox ディレクトリのみをステージングする。退朝時はメインファイル（projects/、STATUS.md、meta/user-patterns.md）には絶対に触れない。

### 上朝時（outbox のマージ）

```bash
# outbox の内容をメインディレクトリにマージした後（v1.9 パス）:
git add projects/ areas/ meta/decisions/ meta/journal/ meta/methods/ meta/STATUS.md meta/user-patterns.md SOUL.md
git rm -r meta/outbox/{merged-session-ids}/
git commit -m "[life-os] merge {N} outbox sessions"
git push
```

### 一般ルール

**`git add -A` や `git add .` は絶対に使わない** — 機密ファイル（.env、.claude/、credentials、一時ファイル）を誤ってコミットする恐れがある。Life OS が明示的に書き込んだファイルのみをステージングすること。

## Worktree のメンテナンス

Claude Code は `.claude/worktrees/` 配下に一時的な worktree を作成する。これが問題を引き起こすことがある：

1. **クロスプラットフォームの干渉**: Gemini / Antigravity が大きな worktree ディレクトリによってコンテキストが溢れる可能性がある
2. **リポジトリ移行後のパス破損**: リポジトリが移動された場合（例: Dropbox → iCloud）、worktree の `.git` ファイルが古いパスを指し、すべての git 操作が壊れる

### 予防策

- `.claude/worktrees/` を `.gitignore` に追加する
- Claude Code の worktree session 終了後は **remove**（keepではなく）を選択する
- リポジトリを別の場所に移行する前に先にクリーンアップする（ターミナルで手動実行すること）：

```text
# ユーザー手動復旧コマンド — 自動実行禁止；人間の確認が必要
git worktree prune
rm -rf .claude/worktrees/
git config --unset core.hooksPath   # 設定されている場合
```

### 復旧手順

`fatal: not a git repository: /old/path/.git/worktrees/...` と報告された場合、以下のコマンドを**ターミナルで手動実行**すること（エージェントはユーザーの明示的な確認なしにこれらを実行してはならない — GLOBAL.md セキュリティ境界 #1 参照）：

```text
# ユーザー手動復旧コマンド — 自動実行禁止；人間の確認が必要
git worktree prune                  # git レベルの参照をクリーン
rm -rf .claude/worktrees/           # 古い worktree ディレクトリを削除
git config --unset core.hooksPath   # 壊れた hooks パスを削除
git config --unset extensions.worktreeConfig  # worktree 拡張フラグを削除
```
