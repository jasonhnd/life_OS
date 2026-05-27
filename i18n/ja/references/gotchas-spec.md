---
spec_id: gotchas-spec.v1
description: 「pro/gotchas.md」仕様 —— プロジェクトレベル技術 gotcha 知識ベース。各エントリは"踏んだ穴 + ファイルパス + 修正方法"を記録し、ROUTER と下流 agent が新タスク前に既知問題を short-circuit できるようにする。`pro/compliance/violations.md`（プロセス違反）と `meta/sessions/`（セッション記録）と区別する。パターンは tinyhumansai/openhuman `.claude/memory.md` から借用；lifeos 実装は md-only、`memory-keeper` agent が書き込む。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, .claude/memory.md (259 行フラット単一ファイル + トピック分組)
introduced_in: v1.8.7
referenced_by:
  - pro/agents/memory-keeper.md
  - pro/agents/archiver.md (wrap-up phase 5)
  - SKILL.md (ROUTER タスク前スキャン、将来バージョン)
---

# Gotchas 仕様 v1

`pro/gotchas.md` は lifeos の**プロジェクトレベル技術 gotcha 知識ベース** —— 単一フラットファイルで非自明な挙動、ファイル固有の bug、回避策を集約し、新セッションが行動前に必ず知るべき情報を提供する。

## 他の知識ストアとの位置づけ

| ストア | 何を記録するか | ライフサイクル |
|--------|---------------|---------------|
| `meta/sessions/<sid>.md` | セッションのタイムライン + 決定 | 1 セッション 1 ファイル、アーカイブ |
| `pro/compliance/violations.md` | プロセス違反（A1/A2/A3/B/C/D/E/F + F1-F17） | append-only 監査ログ |
| `meta/wiki/<topic>.md` | 再利用可能な世界知識（"NPO 貸付には貸金業法免除なし"） | 手動キュレーション |
| `meta/concepts/<concept>.md` | シナプスグラフノード（Cortex） | hippocampus がアクティベート |
| **`pro/gotchas.md`** | **プロジェクト技術 gotcha + ファイルパス + 修正** | **memory-keeper が継続抽出** |

Gotcha は違反**ではない**（それは `compliance/violations.md` 行き）。Gotcha は再利用可能な世界知識**ではない**（それは `meta/wiki/` 行き）。Gotcha は **dev 内部 short-circuit メモリ**："次に X に触る時、まずここを見ろ"。

## ファイル位置とスコープ

- **パス**：`pro/gotchas.md`（単一ファイル、dev repo ルート域）
- **言語**：英語単一言語（プロジェクト内部 dev 知識ベース —— v1.8.7 RFC DR-03 により三言語ミラー対象外）
- **サイズ予算**：目標 ≤500 行；800 行はソフト閾値で分割議論
- **対象**：ROUTER + memory-keeper + 既に触れた領域で重大タスクを行う任意の agent

## エントリフォーマット

各 gotcha は `##` トピックグループ下の単一 bullet：

```markdown
## <トピック / コンポーネント>

- **<短いタイトル（5-10 語）>** — <挙動の説明>。<ファイルパス:行番号> 該当時。修正：<workaround または正しいアプローチ>。(#<参照: PR/issue/RFC>)
```

### フィールドルール

| フィールド | 必須 | 備考 |
|-----------|------|------|
| 短いタイトル | ✅ | 最初の 5-10 語；grep 親和 |
| 挙動の説明 | ✅ | 何が驚き / 何が失敗 / 何が非自明 |
| ファイルパス:行 | 該当時 | `src/path:LN` 形式；横断的なら省略可 |
| 修正 | ✅ | workaround または "workaround なし、X にエスカレート" |
| 参照 | ✅ | PR / issue / RFC / commit sha —— 永続的アーティファクトを指す必要あり |

### サンプルエントリ

```markdown
## archiver

- **archiver Phase 2 候補スキャンが wiki 欠落でブロック** — `meta/wiki/` ディレクトリが存在しないと Phase 2 がスキップせず固まる。修正：archiver が欠落時にディレクトリを先に作成する。(#v1.8.7-C6-task-2d)

- **archiver wrap-up phase 5（memory-keeper）v1.8.7 以降は必須** — phase 5 をスキップ = gotchas 抽出漏れ。修正：archiver Mode 0 が短セッションでも phase 5 を強制；gotchas 表は空でも phase は走る必要あり。(#RFC-v1.8.7)
```

## 何を捕捉するか（memory-keeper 入力ルール）

捕捉する：
- ✅ lifeos 自身の agent / コマンド / spec 相互作用の非自明な挙動
- ✅ ファイル固有 bug とその workaround
- ✅ コードベースまたはランタイムでの "X に見えるが実際は Y" の驚き
- ✅ ユーザが明示的に強調した厳格な不変条件
- ✅ クロスバージョン移行の落とし穴

捕捉**しない**：
- ❌ 単発セッション内容（sessions/ を使う）
- ❌ プロセス違反（compliance/violations.md を使う）
- ❌ lifeos 自身と無関係な再利用可能な世界知識（meta/wiki/ を使う）
- ❌ ユーザ個人情報（アイデンティティレベルなら SOUL.md；瞬時なら sessions/）
- ❌ pro/CLAUDE.md または他の権威ソースで既に文書化されている内容

## 更新方法

memory-keeper agent は `pro/gotchas.md` の**唯一の書き込み者**。人間の直接編集は許可されるが推奨されない —— 重複排除をバイパスし、フォーマット非準拠エントリを生む可能性がある。

更新フロー（memory-keeper は archiver wrap-up phase 5 から呼ばれる）：

1. memory-keeper が現在の `pro/gotchas.md` を読む
2. 現セッションをスキャンして新 gotcha 候補を探す
3. 各候補について：
   - 既存エントリと重複排除（短いタイトルの部分文字列マッチ）
   - エントリフォーマット準拠を検証
   - 該当する `##` セクションに追記（必要なら新セクション作成）
4. レポート出力：候補 N 件発見、M 件重複排除、K 件追記
5. archiver phase 5 完了シグナルへ戻る

## 初期シード（v1.8.7 ship 要件）

RFC §7 退出基準により、memory-keeper の v1.8.7 release セッションでの初回実行は以下のソースをスキャンして ≥10 件のシードエントリを生産する必要がある：

- `meta/rfc/v1.8.4-*.md`
- `meta/rfc/v1.8.5-cleanup-and-hardening.md`
- `meta/rfc/v1.8.6-*.md`
- `pro/compliance/violations.md`（フィルタ：根本原因が技術的で、純プロセスでないエントリ）

シードエントリも gotcha（技術的）であり、プロセス違反ではない。

## 重複排除と保持

- **重複排除**：短いタイトルの部分文字列マッチ —— 新候補の短いタイトルが既存エントリの部分文字列なら、重複作成せず既存にマージ（挙動説明を拡張するか新ファイルパスを追加）
- **保持**：gotcha は自動失効しない。底層問題がコードベースで永久修正**かつ**修正検証後にのみ削除される
- **削除手順**：memory-keeper がエントリを `<!-- removed v1.X.Y: fixed in <ref> -->` でマーク（ファイル内にコメントとして保持、監査用）、または将来の `pro/gotchas-resolved.md` アーカイブに移動

## 失敗モード

| 失敗 | 検出 | 復旧 |
|------|------|------|
| memory-keeper が重複エントリを書く | AUDITOR Mode 7 M7-1（存在チェック + 重複排除完全性チェック） | memory-keeper を dedup-strict フラグで再実行 |
| エントリに `(#<ref>)` 参照なし | AUDITOR Mode 7 M7-1 | memory-keeper がエントリを拒否；archiver phase 5 失敗 |
| ファイルが 800 行超 | 人手レビュー | セクションでサブファイル分割（稀；最早 v1.9+ で発生想定） |
| フォーマットドリフト（スキーマ非適合エントリ） | AUDITOR Mode 7 M7-1 | memory-keeper が次回実行時に再フォーマット |

## 関連 spec

- `pro/agents/memory-keeper.md` —— agent 定義
- `references/compliance-spec.md` —— gotchas と violations の区別
- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.1 C6 —— 本 spec の起源
