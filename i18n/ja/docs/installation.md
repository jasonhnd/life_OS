# インストールガイド

Life OSはさまざまなAIプラットフォームで使用できます。お使いのプラットフォームを選択し、手順に従ってください。

> **SKILL.md**はLife OSのコアファイルであり、三省六部制システムの全命令が含まれています。以下で複数回参照されます。
> 👉 **[こちらからSKILL.mdを取得](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**（右上の「Raw」ボタンをクリックするとプレーンテキストが表示され、コピーが簡単です）

---

## 目次

- [Claude Code（推奨、Proモード）](#claude-code推奨proモード)
- [Claude.ai Web / デスクトップ（Liteモード）](#claudeai-web--デスクトップliteモード)
- [Cursor](#cursor)
- [VS Code + GitHub Copilot](#vs-code--github-copilot)
- [Gemini CLI](#gemini-cli)
- [OpenAI Codex CLI](#openai-codex-cli)
- [ChatGPT](#chatgpt)
- [Gemini Web](#gemini-web)
- [その他のプラットフォーム](#その他のプラットフォーム)
- [Pro vs Liteモード比較](#pro-vs-liteモード比較)
- [インストール確認](#インストール確認)
- [アップデート](#アップデート)
- [FAQ](#faq)

---

## Claude Code（推奨、Proモード）

これはLife OSの完全版です：14の独立したAI役職が真の情報隔離と並列実行を実現します。

### 前提条件

[Claude Code](https://claude.ai/code)（Anthropicのコマンドラインツール）がインストールされている必要があります。

### インストール手順

1. ターミナルを開く
2. 以下のコマンドを入力してEnterを押す：

```bash
/install-skill https://github.com/jasonhnd/life_OS
```

3. インストール完了を待つ。成功メッセージが表示されます
4. 完了です！14のサブエージェントが自動的に準備され、全プロジェクトで利用可能になります

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

- 14のAI役職がそれぞれ独立に動作し、互いの思考過程を見ることができない
- 六部は並列実行可能（順番待ちなし）
- 門下省は審査時に中書省がどう考えたかを見ることができない — 真の独立審査
- 全役職が最強のopusモデルを使用

---

## Claude.ai Web / デスクトップ（Liteモード）

### 方法1：プロジェクトナレッジ（推奨、永続的）

1. [claude.ai](https://claude.ai/) を開いてログイン
2. サイドバーの**Projects**を見つけ、**+ New Project**をクリック
3. プロジェクトに名前をつける（例：「Life OS」）
4. プロジェクトをクリックして開く
5. **Project Settings**を見つけ、**Add to project knowledge**をクリック
6. SKILL.mdファイルをダウンロード：👉 **[こちらからダウンロード](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**（右上の⬇️ダウンロードボタンをクリック、または「Raw」をクリックしてCtrl+S / Cmd+Sで保存）
7. ダウンロードした`SKILL.md`ファイルをProject Knowledgeにアップロード
8. 完了です！このプロジェクト内の全ての新しい会話に三省六部の機能が備わります

### 方法2：単一会話（一時的なお試し）

1. [claude.ai](https://claude.ai/) を開いて新しい会話を開始
2. SKILL.mdファイルをダウンロード：👉 **[こちらからダウンロード](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)**
3. `SKILL.md`ファイルを会話ウィンドウに**ドラッグ**
4. 質問を開始

> 方法2は現在の会話でのみ有効です。閉じた後は再アップロードが必要です。

### デスクトップアプリ

Claudeデスクトップアプリ（macOS / Windows）はWeb版と同じ操作で、Project Knowledgeに対応しています。

---

## Cursor

[Cursor](https://cursor.com/) はAgent Skills標準をサポートするAIコードエディタです。

### インストール手順

1. Cursorを開く
2. 内蔵ターミナルを開く（ショートカット：`` Ctrl+` `` または `` Cmd+` ``）
3. 以下のコマンドを入力してEnterを押す：

```bash
npx skills add jasonhnd/life_OS
```

4. インストール完了を待つ
5. 完了です！CursorのAIチャット（Cmd+L / Ctrl+L）で利用可能になります

---

## VS Code + GitHub Copilot

[VS Code](https://code.visualstudio.com/) にGitHub Copilot拡張機能を入れるとAgent Skillsに対応します。

### 前提条件

[GitHub Copilot拡張機能](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)がインストールされている必要があります。

### インストール手順

1. VS Codeを開く
2. 内蔵ターミナルを開く（ショートカット：`` Ctrl+` ``）
3. 以下のコマンドを入力してEnterを押す：

```bash
npx skills add jasonhnd/life_OS
```

4. インストール完了を待つ
5. 完了です！Copilot Chatで利用可能になります

---

## Gemini CLI

[Gemini CLI](https://github.com/google-gemini/gemini-cli) はGoogleのコマンドラインAIツールで、Agent Skills標準に対応しています。

### インストール手順

1. ターミナルを開く
2. 以下のコマンドを入力してEnterを押す：

```bash
npx skills add jasonhnd/life_OS
```

3. 完了です！Gemini CLIの会話で利用可能になります

---

## OpenAI Codex CLI

[Codex CLI](https://github.com/openai/codex) はOpenAIのコマンドラインAIツールで、Agent Skills標準に対応しています。

### インストール手順

1. ターミナルを開く
2. 以下のコマンドを入力してEnterを押す：

```bash
npx skills add jasonhnd/life_OS
```

3. 完了です！Codex CLIの会話で利用可能になります

---

## ChatGPT

[ChatGPT](https://chat.openai.com/) はAgent Skills標準に対応していないため、手動セットアップが必要です。

### 方法1：カスタムGPTの作成（推奨、永続的）

1. [chat.openai.com](https://chat.openai.com/) を開いてログイン（Plusサブスクリプションが必要）
2. サイドバーの**Explore GPTs**をクリック
3. 右上の**+ Create**をクリック
4. **Configure**タブで：
   - **Name**：`Life OS` と入力
   - **Description**：`三省六部制パーソナルキャビネットシステム` と入力
   - **Instructions**：👉 **[SKILL.md生テキスト](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)** を開き、全選択（Ctrl+A / Cmd+A）、コピー（Ctrl+C / Cmd+C）し、Instructionsフィールドに貼り付け
5. 右上の**Save**をクリックし、「Only me」を選択
6. 完了です！ChatGPTサイドバーの「Life OS」GPTを見つけてクリックし、会話を開始

> **注意**：ChatGPTのInstructionsには文字数制限があります（約8000文字）。貼り付け後に制限に達した場合は、SKILL.mdの「10 標準シナリオ」以下のコンテンツを削除し、コアの役職定義とプロセス説明のみを残してください。

### 方法2：単一会話（一時的なお試し）

1. [chat.openai.com](https://chat.openai.com/) を開いて新しい会話を開始
2. 👉 **[SKILL.md生テキスト](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)** を開く
3. 全選択、コピー、会話に貼り付けて送信
4. 質問を開始

> 現在の会話でのみ有効です。

---

## Gemini Web

[Gemini](https://gemini.google.com/) はGems機能を通じてLife OSを使用できます。

### Gems経由（推奨、永続的）

1. [gemini.google.com](https://gemini.google.com/) を開いてGoogleアカウントでログイン
2. サイドバーの**Gem manager**を見つけ、**New Gem**をクリック
3. 設定で：
   - **Name**：`Life OS` と入力
   - **Instructions**：👉 **[SKILL.md生テキスト](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)** を開き、全選択、コピーし、Instructionsフィールドに貼り付け
4. **Save**をクリック
5. 完了です！Gemsリストの「Life OS」を見つけてクリックし、会話を開始

### 単一会話（一時的なお試し）

SKILL.mdの全コンテンツを新しい会話に直接貼り付けて、質問を開始してください。

---

## その他のプラットフォーム

### Agent Skills標準対応プラットフォーム

お使いのAIツールが[Agent Skills標準](https://agentskills.io/)に対応している場合（例：Roo Code、Windsurf、JetBrains Junieなど）、以下のコマンドでインストールできます：

```bash
npx skills add jasonhnd/life_OS
```

互換プラットフォームの全リストは[agentskills.io](https://agentskills.io/)をご覧ください。

### Agent Skills非対応プラットフォーム

汎用的な方法：
1. 👉 **[SKILL.md生テキスト](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)** を開く
2. 全選択してコピー
3. プラットフォームのSystem Prompt / Instructions / Custom Instructionsに貼り付け

ほとんどのAIプラットフォームは何らかの形式のカスタムインストラクションに対応しています。

---

## Pro vs Liteモード比較

| | Lite | Pro（Claude Code） |
|--|------|-------------------|
| 役職隔離 | 全役職が同一会話内、コンテキスト共有 | 各役職が独立に動作、互いに見えない |
| 門下省審査 | 中書省の推論が見える（独立性が弱まる） | 見えない、真に独立した判断 |
| 六部実行 | 1つずつ順番に | 同時並列 |
| モデル | プラットフォームの現在のモデル | 全役職がopusを使用 |
| インストール | SKILL.mdのアップロード/貼り付け | コマンド1つ |
| 対応プラットフォーム | 30以上 | Claude Code限定 |

**Liteモードでも価値があります**：単一会話内であっても、六部が異なる角度から分析し、門下省が感情的審査を行い、諫官が行動パターンを監視する — これらのメカニズムにより、AIに直接質問するよりも包括的な分析が得られます。

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

## アップデート

### 現在のバージョンの確認

SKILL.md先頭の`version`フィールドに現在のバージョン番号が表示されます。最新バージョンは[GitHub](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)または[変更履歴](../CHANGELOG.md)をご確認ください。

### プラットフォーム別アップデート方法

| プラットフォーム | アップデート方法 |
|----------|--------------|
| **Claude Code** | `/install-skill https://github.com/jasonhnd/life_OS` を再実行、旧バージョンを自動上書き |
| **Claude.ai** | Project Settings → 旧SKILL.mdを削除 → [新バージョン](https://github.com/jasonhnd/life_OS/blob/main/SKILL.md)を再アップロード |
| **Cursor / VS Code等** | `npx skills add jasonhnd/life_OS` を再実行、自動上書き |
| **ChatGPT** | Life OS GPTを編集 → Instructionsを[新しいSKILL.mdコンテンツ](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)に置き換え |
| **Gemini** | Life OS Gemを編集 → Instructionsを[新しいSKILL.mdコンテンツ](https://raw.githubusercontent.com/jasonhnd/life_OS/main/SKILL.md)に置き換え |

### 新バージョンの確認方法

- GitHubでこの[リポジトリをWatch](https://github.com/jasonhnd/life_OS)すると更新通知が届きます
- [変更履歴（CHANGELOG.md）](../CHANGELOG.md)をご確認ください

---

## FAQ

**Q：AIツールを使ったことがありません。どのプラットフォームから始めるべきですか？**
A：[Claude.ai](https://claude.ai/)（Web版、無料登録）から始めて、Project Knowledge経由でインストールしてください。最もシンプルなセットアップで、完全な体験が得られます。

**Q：Liteモードで六部は並列実行できますか？**
A：できません。並列実行はProモード（Claude Code）限定です。Liteモードでは全役職が1つの会話内で順次実行されます。

**Q：Notionを接続せずに使えますか？**
A：はい。Notionはオプションのデータレイヤーです。接続しなくても全機能は正常に動作しますが、セッション間のメモリは利用できません。

**Q：SKILL.mdが長すぎてプラットフォームに収まりません。どうすればいいですか？**
A：「10 標準シナリオ」と「トークン消費見積もり」以下のコンテンツを削除し、コアの役職定義とプロセス説明のみを残してください（約4000文字）。

**Q：中国語以外の言語で使えますか？**
A：はい。システム命令は中国語ですが、どの言語で質問しても正常に動作します。

**Q：会話のたびに再インストールが必要ですか？**
A：インストール方法によります。Project Knowledge（Claude.ai）、カスタムGPT（ChatGPT）、Gems（Gemini）、`/install-skill`（Claude Code）は一度のインストールで永続的に使用可能です。「単一会話」方式のみ毎回繰り返す必要があります。
