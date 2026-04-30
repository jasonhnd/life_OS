# インストールガイド

Life OSはさまざまなAIプラットフォームで使用できます。お使いのプラットフォームを選択し、手順に従ってください。

> **SKILL.md**はLife OSのコアファイルであり、三省六部制システムの全命令が含まれています。以下で複数回参照されます。
> 👉 **[こちらからSKILL.mdを取得](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**（右上の「Raw」ボタンをクリックするとプレーンテキストが表示され、コピーが簡単です）

---

## 目次

- [Claude Code（Proモード）](#claude-codeproモード)
- [Gemini CLI / Antigravity（Proモード）](#gemini-cli--antigravityproモード)
- [OpenAI Codex CLI（Proモード）](#openai-codex-cliproモード)
- [その他のプラットフォーム](#その他のプラットフォーム)
- [インストール確認](#インストール確認)
- [トラブルシューティング](#トラブルシューティング)
- [アップデート](#アップデート)
- [FAQ](#faq)

---

## Claude Code（Proモード）

これはLife OSのClaude上での完全版です：複数の独立した AI 役職が真の情報隔離と並列実行を実現します。

### 前提条件

[Claude Code](https://claude.ai/code)（Anthropicのコマンドラインツール）がインストールされている必要があります。

### インストール手順

1. ターミナルを開く
2. 以下のコマンドを入力してEnterを押す：

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

3. インストール完了を待つ。成功メッセージが表示されます
4. 完了です！全 Life OS サブエージェントが自動的に準備され、全プロジェクトで利用可能になります

### 確認方法

インストール後、Claude Codeで以下を入力してください：

```
転職すべきか分析してほしい
```

以下の形式で応答が表示されれば、インストール成功です：

```
🏛️ 丞相・上奏
📋 題目: ... | 📌 類型: ... | 💡 推奨起動: ...
```

### Proモードの特徴

- 複数の AI 役職がそれぞれ独立に動作し、互いの思考過程を見ることができない
- 六部は並列実行可能（順番待ちなし）
- 門下省は審査時に中書省がどう考えたかを見ることができない — 真の独立審査
- 全役職が最強のopusモデルを使用

---

## Gemini CLI / Antigravity（Proモード）

Proモードが[Gemini CLI](https://github.com/google-gemini/gemini-cli)と[Google Antigravity](https://idx.google.com/)で利用可能になりました。Gemini 2.5 Pro による複数の独立サブエージェントで動作します。

### インストール手順

1. ターミナル（Gemini CLI）またはAntigravityの内蔵ターミナルを開く
2. 以下のコマンドを入力：

```bash
npx skills add jasonhnd/life_OS
```

3. 完了です！システムが自動的にGeminiを検出し、`pro/GEMINI.md`をオーケストレーション用にロードします

### Antigravity固有の注意点

- Antigravityは`.agents/skills/`（ワークスペーススコープ）または`~/.gemini/antigravity/skills/`（グローバルスコープ）からスキルを読み込みます
- **重要**: `.claude/worktrees/`をプロジェクトの`.gitignore`に追加してください。Claude Codeのworktreeアーティファクトによるコンテキストオーバーフローを防止します。これはClaude Codeも使用するプロジェクトでGeminiが応答しなくなる最も一般的な原因です。

### Claude Proモードとの違い

- Geminiの最強の利用可能なモデルを自動使用（ハードコードされたバージョンなし）
- ツール名は自動マッピング（マッピング表は`pro/GEMINI.md`を参照）
- 同じワークフロー、同じ情報隔離、同じ役職セット

---

## OpenAI Codex CLI（Proモード）

Proモードが[Codex CLI](https://github.com/openai/codex)で利用可能になりました。o3 による複数の独立サブエージェントで動作します。

### インストール手順

1. ターミナルを開く
2. 以下のコマンドを入力：

```bash
npx skills add jasonhnd/life_OS
```

3. 完了です！システムが自動的にCodexを検出し、`pro/AGENTS.md`をオーケストレーション用にロードします

### Claude Proモードとの違い

- Codexの最強の利用可能なモデルを自動使用（ハードコードされたバージョンなし）
- [AGENTS.mdオープン標準](https://agents.md/)に準拠
- 同じワークフロー、同じ情報隔離、同じ役職セット

---

> **注意**: Life OSはProモードが必要です — 複数の独立サブエージェントと真の情報隔離。シングルコンテキストプラットフォーム（ChatGPT、Gemini Web、Claude.ai Web）はサポートされていません。

---

## その他のプラットフォーム

### Agent Skills標準対応プラットフォーム

お使いのAIツールが[Agent Skills標準](https://agentskills.io/)に対応している場合（例：Roo Code、Windsurf、JetBrains Junieなど）、以下のコマンドでインストールできます：

```bash
npx skills add jasonhnd/life_OS
```

互換プラットフォームの全リストは[agentskills.io](https://agentskills.io/)をご覧ください。

> **注意**: Life OSはProモード（独立サブエージェント）が必要です。Agent Skills非対応のプラットフォームとは互換性がありません。

---

## インストール確認

プラットフォームを問わず、インストール後に以下のメッセージでテストしてください：

| あなたの発言 | 表示されるべきもの |
|---------|---------------|
| 「MacBookを買うべきか分析して」 | 丞相が上奏が必要と判断し、三省六部プロセスを開始 |
| 「日本語の文章を翻訳して」 | 丞相が直接対応（プロセスは開始しない） |
| 「早朝」 | 早朝官がブリーフィングを提供 |
| 「最近迷っている」 | 丞相が翰林院の起動を確認 |

---

## トラブルシューティング

**Gemini / Antigravityが特定のプロジェクトフォルダで応答を停止する**

通常、`.claude/worktrees/`内の大きなファイル（Claude Codeセッションの残留物）が原因です。これらのworktreeコピーがGeminiのコンテキストウィンドウを溢れさせます。

> ⚠️ **手動リカバリ（人間のみ実行）** —— 以下のコマンドは破壊的操作（`rm -rf`）を含みます。エージェントは自動実行してはならず、ユーザーが自分のターミナルで手動で実行する必要があります。GLOBAL.md セキュリティ境界 #1 はエージェントが確認なしに破壊的コマンドを実行することを禁止しています。

```text
# HUMAN ONLY — DO NOT auto-execute
# 1. worktreeフォルダを削除
rm -rf .claude/worktrees/

# 2. `.claude/worktrees/`を`.gitignore`に追加（手動で編集）

# 3. Antigravity / Gemini CLIを再起動
```

**リポジトリの移動後にGit操作が`fatal: not a git repository`で失敗する**

Claude Codeのworktree参照がまだ古い場所を指しているために発生します。`.claude/worktrees/`ディレクトリにはハードコードされた絶対パスの`.git`ファイルが含まれています。

> ⚠️ **手動リカバリ（人間のみ実行）** —— 以下のコマンドは破壊的操作（`rm -rf`、`git config --unset`）を含みます。エージェントは自動実行してはならず、ユーザーが自分のターミナルで手動で実行する必要があります。GLOBAL.md セキュリティ境界 #1 はエージェントが確認なしに破壊的コマンドを実行することを禁止しています。

```text
# HUMAN ONLY — DO NOT auto-execute
# 1. git worktree参照をクリーン
git worktree prune

# 2. 古いworktreeディレクトリを削除
rm -rf .claude/worktrees/

# 3. 壊れた設定をチェック —— 存在しないパスを指している場合、下記の unset コマンドを実行
git config --get core.hooksPath
git config --unset core.hooksPath

# 4. worktree拡張フラグを削除
git config --unset extensions.worktreeConfig
```

予防策：リポジトリを移動する前（例：Dropbox → iCloud）、必ずworktreeを先にクリーンアップしてください。Claude Codeのworktreeセッション後は「keep」ではなく「remove」を選択してください。

**Gemini/CodexでProモードが有効にならない**

`npx skills add jasonhnd/life_OS`でインストールし、スキルファイルが正しい場所にあることを確認してください：
- Gemini CLI：`~/.gemini/skills/`またはプロジェクトレベルの`.agents/skills/`
- Codex CLI：`~/.codex/skills/`
- Claude Code：`~/.claude/skills/`

**コンテキストウィンドウのオーバーフロー**

プロジェクトに非常に大きなファイルがある場合、AIプラットフォームがサイレントに失敗することがあります。解決策：
- `.gitignore`を使用してビルドアーティファクト、`node_modules/`、大きなバイナリファイルを除外
- Antigravityの場合、`.agignore`ファイル（対応している場合）で無関係なディレクトリを除外

---

## アップデート

### 現在のバージョンの確認

SKILL.md先頭の`version`フィールドに現在のバージョン番号が表示されます。最新バージョンは[GitHub](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)または[変更履歴](../CHANGELOG.md)をご確認ください。

### プラットフォーム別アップデート方法

| プラットフォーム | アップデート方法 |
|----------|--------------|
| **Claude Code** | `/install-skill https://github.com/jasonhnd/life_OS` を再実行 |
| **Gemini CLI / Antigravity** | `npx skills add jasonhnd/life_OS` を再実行 |
| **Codex CLI** | `npx skills add jasonhnd/life_OS` を再実行 |

### 新バージョンの確認方法

- GitHubでこの[リポジトリをWatch](https://github.com/jasonhnd/life_OS)すると更新通知が届きます
- [変更履歴（CHANGELOG.md）](../CHANGELOG.md)をご確認ください

---

## FAQ

**Q：どのプラットフォームから始めるべきですか？**
A：[Claude Code](https://claude.ai/code)を推奨します。複数の独立サブエージェントによる完全な Pro モード、ワンコマンドインストールです。

**Q：Claude CodeとAntigravityの両方を使っています。競合しますか？**
A：いいえ。異なるオーケストレーションファイル（`CLAUDE.md` vs `GEMINI.md`）と異なるモデルマッピングを使用します。`pro/agents/*.md`ファイルは共有されます。`.claude/worktrees/`が`.gitignore`に含まれていれば、AntigravityがClaudeの一時ファイルで詰まることはありません。

**Q：Notionを接続せずに使えますか？**
A：はい。Notionはオプションのデータレイヤーです。接続しなくても全機能は正常に動作しますが、モバイルでのクロスセッションメモリは利用できません。

**Q：中国語以外の言語で使えますか？**
A：はい。システムは英語、中国語、日本語に対応しています。どの言語で質問しても正常に動作します。

**Q：快車道分析とは何ですか？**
A：リクエストが意思決定を伴わない場合（分析、調査、計画のみ）、丞相は完全な三省プロセスをスキップし、1〜3の関連部を直接起動できます。より速く、トークンも少なく、非意思決定タスクでは同等の品質を維持します。
