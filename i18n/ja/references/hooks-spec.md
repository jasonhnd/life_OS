---
translated_from: references/hooks-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# Shell Hooks 契約仕様書(Shell Hooks Contract Specification)(v1.7)

> ランタイムで Life OS HARD RULE 遵守を強制する 5 つの shell hook に対する権威的契約です。各 hook は自己完結型の bash スクリプトで、Claude Code ホストと stdin JSON、stdout テキスト、exit code を介して通信します。Bash + jq のみ — Python ランタイムなし、stdlib 以外の依存なし。

---

## 1 · 目的(Purpose)

Shell hooks が存在する理由は、ドキュメントが強制ではないからです。LLM はドリフトします。2026-04-19 の COURT-START-001 incident は、markdown ファイルに「HARD RULE」と書いてもそのルールが hard にはならないことを証明しました — オーケストレータ自身が subagent の launch をスキップしたり、ファイルパスを捏造したり、訂正をユーザーターンを跨いで salami-slice できてしまうのです。Hooks はそのドリフトをランタイムで捕捉します。

hook は LLM コンテキスト外のサブプロセスで動きます。LLM はそれを買収できず、忘れることもできず、合理化して回避することもできません。hook が発火すると、次のいずれかになります:

- 静かにパススルー(exit 0) — LLM は hook が走ったことを知らない
- system reminder を注入(exit 0 with stdout) — テキストが権威的として LLM コンテキストに挿入される
- アクションをブロック(exit 2 with stderr) — ツールコールがキャンセルされ、理由が LLM に告げられる

本仕様は v1.7 に必要な 5 つの hook、その契約、regex パターン、違反ログ機構を定義します。

---

## 2 · プラットフォームサポート(Platform Support)

**Claude Code のみ(v1.7)。** ここで記述される hook システムは Anthropic の Claude Code CLI にネイティブに存在します。Gemini CLI と Codex CLI は v1.7 時点で同等の hook surface を公開しておらず — ランタイムバックストップなしのプロンプトレベル強制(SKILL.md の HARD RULE 記述)にフォールバックします。

Gemini / Codex が互換 hook spec を公開したら、同じ 5 スクリプトをそこに登録できます。それまで、Claude Code 以外のホストでの Life OS は Layer 1(ドキュメント)と Layer 2(subagent 隔離)のみを得ます。これは `docs/architecture/execution-layer.md` にドキュメント化されています。

---

## 3 · Hook システムアーキテクチャ(Hook System Architecture)

### 3.1 Claude Code hook タイプ

Hooks は `~/.claude/settings.json` の `hooks` 配下で宣言されます。重要なのは 4 つのイベント:

| Event | 発火タイミング | 典型用途 |
|-------|---------------|-------------|
| `UserPromptSubmit` | LLM が各ユーザーメッセージを処理する前 | trigger 検出、HARD RULE 注入 |
| `PreToolUse` | 任意のツールコール前 | 引数検証、危険パスブロック |
| `PostToolUse` | 任意のツールコール後 | LLM が主張通りのことを実行したか検証 |
| `Stop` | セッション終了時 | 完了チェックリスト検証 |

マッチングはツール名(`PreToolUse` / `PostToolUse`)またはワイルドカード(`UserPromptSubmit` / `Stop`)で行います。

### 3.2 Hook メカニクス

Claude Code は各 hook をサブプロセスとして起動し、JSON コンテキストオブジェクトを stdin に書き込み、stdout を注入される `system_reminder` として読み、stderr をユーザー向け診断(block 時のみ表示)として読み、exit code をチェックします:

- `0` — パススルー。非空の stdout は system reminder になる。
- `2` — block。ツールコールがキャンセルされ、stdout + stderr が block 理由として LLM に表示される。
- それ以外 — hook エラー。Claude Code はそれをログし、block せずに続行する。

### 3.3 入力 JSON スキーマ(Input JSON schema)

**`UserPromptSubmit`**: `{prompt, session_id, cwd}`
**`PreToolUse` / `PostToolUse`**: `{tool_name, tool_input, tool_result, session_id, cwd, recent_user_message}`
**`Stop`**: `{session_id, final_state, transcript_path}`

すべての hook は `jq -r` でパースし、値を untrusted data として扱います — 悪意あるプロンプトにはシェルメタキャラクタが含まれ得ます。

---

## 4 · 違反時の厳格ブロック(Strict Block on Violation)(ユーザー決定 #6)

hook が HARD RULE 違反を検出したとき:

1. exit code `2`(ツールコールまたはプロンプトをキャンセル)
2. 説明を stdout に書く — これが LLM が読む `system_reminder` になる
3. 構造化行を `{compliance_path}/violations.md` に append(パスは §6 に従って自動検出)

LLM はそれから正しくリトライできます。ユーザーはターミナルで block 説明を見ます。違反は git 下に残ります。

**なぜ advisory ではなく厳格 block か:** COURT-START-001 はドキュメントレベルの HARD RULE が無視されることを証明しました。Hard block は再計画を強制します。ユーザー決定 #6。

---

## 5 · v1.7 の 5 Hook(The Five v1.7 Hooks)

すべての hook スクリプトは Life OS スキルパッケージ内の `scripts/hooks/` に存在し、スキルインストール時に `~/.claude/skills/life_OS/scripts/hooks/` に配置されます。

### 5.1 `pre-prompt-guard.sh`

- **Event:** `UserPromptSubmit`、matcher `*`
- **Purpose:** トリガー語を検出、subagent launch を命じる HARD RULE を注入
- **Solves:** COURT-START-001 — ROUTER が retrospective ステップをメインコンテキストで実行

**契約:** stdin から `prompt` をパース。トリガーテーブルにマッチすれば `<system-reminder>` を stdout に emit し exit 0。それ以外は出力なしで exit 0。この hook は決して exit 2 しない — guidance を注入するだけ。

**トリガーテーブル(Trigger table):**

| Pattern | Subagent | Mode |
|---------|----------|------|
| `上朝` / `start` / `begin` / `はじめる` / `開始` / `朝廷開始` / `閣議開始` | `retrospective` | Start Session |
| `退朝` / `adjourn` / `done` / `end` / `お疲れ` / `終わり` / `结束` | `archiver` | Adjourn 4-phase |
| `复盘` / `review` / `早朝` / `振り返り` / `レビュー` | `retrospective` | Review Mode |
| `朝堂议政` / `debate` / `討論` | `council` | 3-round debate |
| `quick` / `快速分析` / `クイック` | — | ROUTER Express |

**`上朝` が検出されたときの stdout 例:**

```
<system-reminder>
HARD RULE · Trigger "上朝" detected.

Required output (exactly 2 lines):
Line 1: theme-appropriate greeting
Line 2: Agent tool call for retrospective Mode 0

You MUST:
- Read pro/agents/retrospective.md BEFORE the Agent call
- Launch(retrospective) as an independent subagent
- NOT execute any step of retrospective in main context
- NOT simulate subagent output

Any deviation = HARD RULE violation, logged to compliance/violations.md.
Precedent: COURT-START-001 (2026-04-19).
</system-reminder>
```

### 5.2 `post-response-verify.sh`

- **Event:** `PostToolUse`、matcher `Task|Bash|Write|Edit`
- **Purpose:** トリガー語の後、LLM が実際に正しい subagent を launch したか検証
- **Solves:** ROUTER が「retrospective を launch します」と言いながら実際には Bash / Read を直接実行する

**契約:** `tool_name`、`tool_input`、`recent_user_message` をパース。`recent_user_message` がトリガーにマッチし、`tool_name != Task`(または `Task` が誤った subagent をターゲットにしている)場合、違反をログし、訂正 reminder とともに exit 2。それ以外は exit 0。

**検出ルール(Detection rules):**

| Recent trigger | Expected tool | Violation if... |
|----------------|---------------|-----------------|
| `上朝` / `start` | `Task(retrospective)` | `Bash` で `_meta/` を読む、`Read` で config、journal への直接 `Write` |
| `退朝` / `adjourn` | `Task(archiver)` | 任意の `git` コマンド、`_meta/decisions/` への `Write`、archiver 返却前の Notion MCP コール |
| `复盘` / `review` | `Task(retrospective)` | subagent なしで `_meta/sessions/INDEX.md` を直接 `Read` |

### 5.3 `pre-write-scan.sh`

- **Event:** `PreToolUse`、matcher `Write|Edit`
- **Purpose:** SOUL / wiki / concepts / user-patterns に向かうコンテンツの高速 regex スキャン
- **Solves:** LLM 生成コンテンツに含まれる injection payload(悪意または事故)が長期知識ファイルに到達する

**契約:** `file_path` + `content`(Edit なら `new_string`)をパース。`file_path` がスコープセット(`SOUL.md`、`wiki/**`、`_meta/concepts/**`、`user-patterns.md`)外なら exit 0 パススルー。セット内なら 15-pattern regex スキャン + invisible-Unicode スキャンを実行。いずれかにマッチすれば違反をログし、pattern flag 付きで exit 2。

この regex スキャンは安価な一次パス。LLM ベースのプライバシーチェック(ユーザー決定 #5)は archiver の knowledge extraction で後で走る — regex は高速一次防衛線。

**15 の regex パターン(The 15 regex patterns):**

| # | Pattern name | Regex |
|---|--------------|-------|
| 1 | Prompt injection — ignore instructions | `(?i)ignore (all )?(previous\|above) (instructions\|rules)\|disregard (all \|the )?system` |
| 2 | Prompt injection — reveal system | `(?i)(reveal\|output\|print\|show) (your\|the) (system prompt\|hidden instructions\|initial prompt)` |
| 3 | Prompt injection — role override | `(?i)you are now\|from now on you are\|new identity\|forget you are claude` |
| 4 | Shell injection — command substitution | `\$\([^)]{1,100}\)` |
| 5 | Shell injection — backticks | `` `[^`]{1,100}` `` |
| 6 | SQL injection — UNION / DROP / DELETE | `(?i)union\s+select\|drop\s+table\|delete\s+from\s+\w+\s+where\s+\d` |
| 7 | SQL injection — OR 1=1 | `('\|")\s*OR\s*('\|")?\d+('\|")?\s*=\s*('\|")?\d+` |
| 8 | Secret — high-entropy key | `\b[A-Z0-9]{32,}\b` |
| 9 | Secret — common prefixes | `(sk\|pk\|api\|secret\|token)_[a-zA-Z0-9]{16,}` |
| 10 | Secret — AWS access key | `\bAKIA[0-9A-Z]{16}\b` |
| 11 | Secret — GitHub token | `\bghp_[a-zA-Z0-9]{36}\b` |
| 12 | Secret — Slack token | `\bxox[pbar]-[0-9]{10,}-[a-zA-Z0-9]{24,}\b` |
| 13 | Private key block | `-----BEGIN (RSA \|DSA \|EC \|OPENSSH )?PRIVATE KEY-----` |
| 14 | Credit card | `\b(4\d{12}(\d{3})?\|5[1-5]\d{14}\|3[47]\d{13}\|6(?:011\|5\d{2})\d{12})\b` |
| 15 | PII — SSN | `\b\d{3}-\d{2}-\d{4}\b` |

**Invisible-Unicode スキャン:** U+200B、U+200C、U+200D、U+2060、U+FEFF(中間)、U+202A–U+202E(BIDI override)をブロック。これらは人間レビューから payload を隠す injection 攻撃でよく使われます。

### 5.4 `stop-session-verify.sh`

- **Event:** `Stop`、matcher `*`
- **Purpose:** adjourn flow が完全な Completion Checklist とともに完了したか検証
- **Solves:** Archiver 半完了 — Phase 1 は走るが Phase 4 がスキップされる

**契約:** stdin から `transcript_path` をパース。transcript を grep して adjourn トリガーを探す。adjourn が発火していなければ exit 0。発火していれば archiver の 4 フェーズ(`Phase 1: Archive`、`Phase 2: Knowledge Extraction`、`Phase 3: DREAM`、`Phase 4: Sync`)すべてが placeholder ではない値で現れること、加えてオーケストレータの post-archiver Notion 同期ブロックを検証。欠落または `TBD` → 違反をログ。ブロック不可(セッションはすでに終了中) — ログのみ、exit 0。

### 5.5 `pre-read-allowlist.sh`

- **Event:** `PreToolUse`、matcher `Read`
- **Purpose:** Life OS スコープ外、特に credential ファイルの read を防ぐ
- **Solves:** `~/.ssh/`、`~/.aws/credentials`、`/etc/passwd` への事故または注入による read

**契約:** `file_path` を絶対パスに解決。`cwd` 内または明示的 allowlist 内 → exit 0。denylist にマッチ → reminder とともに exit 2。それ以外 → exit 0(denylist 外では LLM を信頼)。

**Denylist:** `~/.ssh/**`、`~/.aws/**`、`~/.gcp/**`、`~/.azure/**`、`~/.docker/config.json`、`~/.kube/config`、`~/.npmrc`、`~/.pypirc`、`/etc/passwd`、`/etc/shadow`、`/etc/sudoers*`、`**/id_rsa`、`**/id_ed25519`、`**/.env`、`**/.env.*`。

**Allowlist(すべてを上書き):** `$cwd/**`、`~/.claude/skills/life_OS/**`、`~/.claude/scripts/**`、`~/.cache/lifeos/**`。

---

## 6 · Compliance パス自動検出(Compliance Path Auto-Detection)(ユーザー決定 #14)

Life OS は 2 つの異なる repo コンテキストで走ります: dev repo(スキルコードベース)とユーザーの second-brain(データ repo)。それぞれが独自のログを持ちます。

```bash
detect_compliance_path() {
  if [ -f "pro/agents/retrospective.md" ]; then
    echo "pro/compliance/violations.md"       # dev repo
  elif [ -d "_meta/" ] && [ -f "_meta/config.md" ]; then
    echo "_meta/compliance/violations.md"     # second-brain
  else
    echo "/dev/null"                          # skip logging
  fi
}
```

- `pro/agents/retrospective.md` = dev-repo マーカー
- `_meta/config.md` = second-brain マーカー
- それ以外の `cwd` は `/dev/null` — 無関係な repo に compliance ディレクトリを作らない

両方の `violations.md` ファイルは git-tracked であり、違反は repo と共に移動します。どちらのパスも `~/.claude/` には書きません — それは COURT-START-001 の後に確立された「すべての state は markdown + git」原則に反します。

---

## 7 · 違反ログフォーマット(Violations Log Format)

**ヘッダー(Header)**(初回実行時に retrospective Mode 0 が作成):

```markdown
# Compliance Violations Log

> Rolling 90-day window. Older rows archived to `archive/{year}-Q{n}.md` by `backup.py`.

| Timestamp | Type | Severity | Agent | Detail | Hook | Resolved |
|-----------|------|----------|-------|--------|------|----------|
```

**行例(Row example):**

```
| 2026-04-20T14:32:10+09:00 | CLASS_A | critical | ROUTER | Start trigger but no retrospective subagent launched | pre-prompt-guard | open |
```

**列(Columns):**

| Column | Values | Notes |
|--------|--------|-------|
| Timestamp | タイムゾーン付き ISO 8601 | `date -Iseconds` |
| Type | `CLASS_A` / `B` / `C` / `D` / `E` | §8 参照 |
| Severity | `critical` / `high` / `medium` / `low` | §8 に従う |
| Agent | `ROUTER` / `archiver` / `retrospective` / `unknown` | tool_name から推論 |
| Detail | 一行 metadata 記述 | ユーザープロンプト内容なし — PII 安全 |
| Hook | スクリプト名 | デバッグ用 |
| Resolved | `open` / `resolved-<date>` | AUDITOR または手動でフリップ |

**`Detail` のアンチパターン:** ユーザープロンプト内容、ファイル内容、secret(「redacted」でも)を含めない。metadata のみ使用 — pattern ID、ファイルパスカテゴリ、hook 名。

---

## 8 · エスカレーションラダー(Escalation Ladder)

Hooks は行を append し、`stats.py`(Layer 4)がエスカレーション判断を駆動します。

**30 日ローリングウィンドウ、同一タイプカウント:**

| Count | Action |
|-------|--------|
| ≥ 3 | 🚨 次回 `retrospective` Start Session briefing の冒頭に警告バナー |
| ≥ 5 | AUDITOR が各セッション開始時に Patrol Inspection モードを強制 |
| ≥ 10 | システミック問題 — 次バージョン spec 改訂用に `eval-history.md` にフラグ |

**重大度マッピング(Severity mapping):**

| Type | Severity | Example |
|------|----------|---------|
| `CLASS_A` | critical | ROUTER がトリガー語後に subagent launch をスキップ |
| `CLASS_B` | critical | エージェントがファイルパス / 章 / HARD RULE ソースを捏造 |
| `CLASS_C` | high | Adjourn が Completion Checklist なしで終了 |
| `CLASS_D` | critical | SOUL/wiki への Write 提案に injection パターン |
| `CLASS_E` | high | denylist パスへの Read 試行 |

エスカレーションは deterministic: `stats.py` が `violations.md` から on demand で計算し、hooks は行を append するだけ。これにより hooks は高速(< 100ms)に保たれ、エスカレーションが inspectable になります。

---

## 9 · アーカイブポリシー(Archive Policy)

`violations.md` はローリング 90 日にキャップされます。古い行は四半期ローテーションで `backup.py`(hook ではない — hooks はデータを移動しない)により移動されます。

```
pro/compliance/                          # dev repo
├── violations.md                        # current 90 days
├── archive/2026-Q2.md                   # rotated quarterly
└── 2026-04-19-court-start-violation.md  # major incident dossiers (permanent)

_meta/compliance/                        # second-brain, same structure
├── violations.md
└── archive/
```

行レベルの違反はローテーションされます。主要インシデントの dossier(再構築を引き起こしたもの)は無期限で残ります。

---

## 10 · インストール(Installation)

v1.6.2 の `setup-hooks.sh` は 1 つの SessionStart version-check hook をインストールします。v1.7 はそれを拡張して 5 つの hook すべてを atomically 登録します。

**v1.7 が追加する Settings JSON 構造:**

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-prompt-guard.sh\"", "timeout": 5}],
      "id": "life-os-pre-prompt-guard"
    }],
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-write-scan.sh\"", "timeout": 5}],
        "id": "life-os-pre-write-scan"
      },
      {
        "matcher": "Read",
        "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-read-allowlist.sh\"", "timeout": 3}],
        "id": "life-os-pre-read-allowlist"
      }
    ],
    "PostToolUse": [{
      "matcher": "Task|Bash|Write|Edit",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/post-response-verify.sh\"", "timeout": 5}],
      "id": "life-os-post-response-verify"
    }],
    "Stop": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/stop-session-verify.sh\"", "timeout": 10}],
      "id": "life-os-stop-session-verify"
    }]
  }
}
```

**事前チェック(Pre-flight checks)**(v1.6.2 `setup-hooks.sh` から継承):

1. `jq` がインストールされている
2. 既存の `settings.json` が有効な JSON
3. 5 つの hook スクリプトすべてが `scripts/hooks/` に存在し実行可能
4. 5 つすべてが idempotent(2 回インストールしても no-op)

失敗時: 理由を print し、`settings.json` を変更せず、exit 1。成功時: `settings.json.tmp` + `mv` で atomically 書き込み。

**タイムアウト(Timeouts):** pre-read は 3 秒(純パスマッチング)、prompt / write / post チェックは 5 秒(regex スキャン)、stop-verify は 10 秒(transcript パース)。hook がハングすると Claude Code はそれを kill し hook エラーとして扱う — ツールコールはブロックされません。

---

## 11 · アンインストール / 無効化(Uninstall / Disable)

**1 つの hook を削除:**

```bash
jq '.hooks.UserPromptSubmit = [.hooks.UserPromptSubmit[] | select(.id != "life-os-pre-prompt-guard")]' \
   ~/.claude/settings.json > ~/.claude/settings.json.tmp \
   && mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

**Life OS hook すべてをアンインストール:** `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh --uninstall`。`--uninstall` フラグ(v1.7 で追加)は `id` が `life-os-` で始まるすべての hook を削除します。他のスキルに触れません。

**手動編集:** `~/.claude/settings.json` を開きエントリを削除。常に安全 — hooks は純粋に加算的。

**アンインストールせずに無効化:** `pre-prompt-guard.sh` → `pre-prompt-guard.sh.disabled` にリネーム。Claude Code は欠落した実行ファイルを hook エラーとしてログし、ブロックせずに続行します。

---

## 12 · テスト(Testing)

Hook の挙動は `evals/scenarios/hook-compliance/` でカバーされます:

| # | Scenario | Expected |
|---|----------|----------|
| 1 | ユーザーが「上朝」、LLM が retrospective を正しく launch | pre-prompt-guard が reminder 注入、post-response-verify が pass |
| 2 | ユーザーが「上朝」、LLM が `_meta/sessions/INDEX.md` 読み取りに Bash | pre-prompt-guard 注入、post-response-verify block(CLASS_A) |
| 3 | 「ignore all previous instructions」付きの `wiki/notes.md` への Write | pre-write-scan が pattern #1 でブロック |
| 4 | `projects/work/index.md`(スコープ外)への Write | pre-write-scan がパススルー |
| 5 | `~/.ssh/id_rsa` の Read | pre-read-allowlist がブロック(CLASS_E) |
| 6 | `$cwd/projects/foo.md` の Read | pre-read-allowlist がパススルー |
| 7 | 「退朝」、archiver 実行、Phase 4 なしでセッション終了 | stop-session-verify が CLASS_C をログ |
| 8 | 任意のプロンプト「what's the weather」 | pre-prompt-guard が静かに exit 0 |

各シナリオは input、期待される hook 出力、期待される `violations.md` diff を持つ markdown ファイル。Eval harness は決定論的に再生 — hook テストパスに LLM なし、したがって hook 挙動は LLM ドリフトと独立に検証されます。

---

## 13 · アンチパターン(Anti-Patterns)

- **遅くならない。** デフォルトタイムアウト 5 秒(pre-read は 3 秒)。Web リクエストやファイルシステムウォークをする hook は壊れている。Hooks は関連イベントごとに走る。
- **存在確認なしで compliance パスに書かない。** 無関係な repo に任意ディレクトリを作るのではなく、§6 の `/dev/null` フォールバックを使う。
- **read-only 操作を denylist マッチ以外でブロックしない。** False-positive ブロックは read の missed warning より悪い。
- **ユーザーのプロンプト内容をログしない。** PII リスク。metadata のみログ: トリガー語、pattern ID、hook 名。ユーザープロンプトは Claude Code transcript に留まり、git-tracked な compliance ログには決して入らない。
- **Python を要求しない。** Bash + jq のみ。Python は Layer 4(バックグラウンドワーカー)、Layer 3 の前提条件ではない。
- **ブロック時に exit 1 しない。** Claude Code セマンティクスでは exit 1 = 「hook エラー、続行」、exit 2 = 「block」。これを間違えると hard block が silent warning になる。
- **stdout に ANSI カラーコードを emit しない。** stdout は system reminder になる — プレーン markdown を保つ。装飾には stderr を使い、block 時のみ表示されるようにする。
- **stdin JSON 値をシェルトークンとして信頼しない。** 常に `jq -r` して展開をクオート。`$(rm -rf ~)` を含む悪意あるプロンプトが実行されてはならない。

---

## 14 · 関連仕様(Related Specs)

- `references/data-layer.md` — データレイヤー境界、`compliance/violations.md` は他の `_meta/` surface と並んでここに存在
- `references/eval-history-spec.md` — AUDITOR eval-history 次元 `process_compliance` は hooks がフラグした違反パターンを consume する
- `references/tools-spec.md` — hooks を補完する Python Layer 4 ツール(`stats.py`、`backup.py`、`reconcile.py`)
- `references/cortex-spec.md` — 全体 Cortex アーキテクチャ。Hooks はその markdown-first 不変条件を守る
- `pro/compliance/2026-04-19-court-start-violation.md` — この spec を正当化する founding incident
- `docs/architecture/execution-layer.md` — 完全な Layer 3(hooks)+ Layer 4(Python tools)アーキテクチャ
- `scripts/setup-hooks.sh` — v1.6.2 のインストーラテンプレート、v1.7 の拡張インストーラが継承する
- `scripts/lifeos-version-check.sh` — v1.6.2 の唯一の hook、「pre-flight、idempotent、atomic」パターンの参照

`violations.md` データモデルは本仕様の §7 で定義されます(フォーマット、列、エスカレーションラダー)。cortex-spec では定義されていません。

**END**
