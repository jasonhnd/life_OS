# 変更履歴

## バージョニングルール

このプロジェクトは **Strict SemVer** に従います：MAJOR（破壊的変更）· MINOR（新機能）· PATCH（修正・保守）。同日の変更は単一リリースにまとめ、リリースごとに git tag を打ちます。

---

## [1.8.0] - 2026-04-28 - Daily Cycle ハイブリッド化（cron + monitor + 上朝/退朝のソフト化）

> **Life OS 史上最大の単一リリース**。lifeos を「反応型 chatbot」から「ハイブリッド OS」（reactive + autonomous）へ変革。3 つの直交モードが並存：ビジネス session（長期持続）、monitor session（`/monitor`）、cron 自治（10 job + RunAtLoad）。

### 追加 · Session Modes（核心アーキテクチャ変更）

- **Mode 1 · ビジネス session**：長期持続、数日〜数週間にまたがる。**上朝/退朝はオプショナルなソフトトリガー**。
- **Mode 2 · Monitor session**：`/monitor` で運用コンソールモード。
- **Mode 3 · Cron 自治**：10 cron job + 1 RunAtLoad。

### 追加 · Cron jobs（v1.8.0 で 5 個追加、計 10 + 1 RunAtLoad）

新規：spec-compliance / wiki-decay / archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency / missed-cron-check。**v1.6.x 以来 spec で約束しながら cron トリガーが 0 だった機能を起動**。

### 追加 · Slash コマンド（2 個）

- `/monitor` — monitor モード突入
- `/run-cron <job>` — 手動トリガー

### 追加 · Hooks（3 個）

- `session-start-inbox` — cron→session ブリッジ
- `pre-task-launch` — マシンレベルで v1.7.3 carve-out 強制
- `post-task-audit-trail` — 即時 R11 audit trail チェック

### 追加 · Python ツール（4）+ Cron プロンプト（5）+ Spec ドキュメント（2）+ 新 subagent

- 4 python: `spec_compliance_report` / `wiki_decay` / `cron_health_report` / `missed_cron_check`
- 5 prompts: `scripts/prompts/{archiver-recovery,auditor-mode-2,advisor-monthly,eval-history-monthly,strategic-consistency}.md`
- 2 specs: `references/{automation-spec,session-modes-spec}.md`
- 1 subagent: `pro/agents/monitor.md`
- 1 trigger script: `scripts/run-cron-now.sh`

### 変更

- **pro/CLAUDE.md** 新規 "Session Modes (v1.8.0)" section
- **scripts/setup-cron.sh** 3 → 10 cron jobs + 1 RunAtLoad
- **scripts/setup-hooks.sh** 3 つの新 hook 登録
- **scripts/hooks/pre-prompt-guard.sh** 上朝/退朝 reminder ソフト化
- **バージョンマーカー**：SKILL.md + 3 README badge → 1.8.0

### リリース後修正（v1.8.0 に取り込み — バージョンは据え置き、「全 bug は本バージョンに属する」方針）

- **R-1.8.0-001 · `scripts/setup-hooks.sh`**：9 個の変数宣言が欠落（3× `HOOK_*_ID`、3× `V18_*_SOURCE`、3× `V18_*_DEST`）。`copy_exec` / `register_hook` で参照されているのに未定義で、setup が "未定义变量 V18_SESSION_START_INBOX_SOURCE" でエラー。line 52-54、66-68、80-82 に宣言を追加。
- **R-1.8.0-002 · `scripts/run-cron-now.sh`**：bash 4+ の `declare -A` 連想配列を使用。macOS は bash 3.2.57（GPLv2 で凍結）が標準のため、Mac でスクリプトが 100% 失敗。JOBS テーブルを `case` ベースの `job_spec()` 関数 + 別の `JOB_NAMES` リストに書き直し。データルートも `$LIFEOS_DATA_ROOT`（env）→ `$PWD`（cwd）→ 明確なエラーで失敗するように変更。
- **R-1.8.0-003 · `scripts/setup-cron.sh`**：致命的な root 混同バグ。`REPO_ROOT` が `tools/cli.py` 検索（正しい：skill ソース）と生成コマンド内の `cd` + `--root .`（誤り：ユーザーの second-brain repo であるべき）の両方に使われていました。結果：11 個の cron job すべてが空の skill ディレクトリをスキャンし、「0 sessions / 0 SOUL / 0 projects」と報告。独立した `DATA_ROOT`（`$LIFEOS_DATA_ROOT` または `$PWD` から）を導入し、`repo_command{,_pymod,_prompt}`（python：`--root "$DATA_ROOT"`、prompt：`cd "$DATA_ROOT"`）と、6 つの `print_launchd_plist*` ジェネレーター全て（`<key>WorkingDirectory</key>` は `$DATA_ROOT` から取得）に貫通。`main()` に `require_data_root()` 早期チェックを追加し、実行可能なエラーメッセージを出すようにしました。
- **R-1.8.0-004 · `tools/spec_compliance_report.py`**：root 検証 guard が `(root / "SKILL.md").is_file()` で Life OS root を判定していましたが、`SKILL.md` は skill ソースにのみ存在し、ユーザーの second-brain repo にはありません。インストールごとに "no SKILL.md" でエラー終了していました。`(root / "_meta").is_dir()` に変更し、本来のデータ root マーカーに合わせました。
- **R-1.8.0-005 · `tools/wiki_decay.py`**：R-1.8.0-004 と同じ `SKILL.md`-vs-`_meta/` ミスマッチバグ。同様に修正。
- **`tools/missed_cron_check.py`**（R-1.8.0-004 と一緒に先行修正）：line 134 に同じ `SKILL.md`-vs-`_meta/` バグパターン。次回 macOS 再起動時に RunAtLoad plist 経由で発火する見込み。R-1.8.0-004 の同じ修正を予防的に適用。
- **R-1.8.0-006 · `scripts/setup-cron.sh` · `repo_command_prompt`**：cron が起動した `claude -p` session に事前承認された Write 権限がなく、prompt ベースの全 job（archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency）が分析後に Write tool 権限プロンプトでブロック — 誰も承認しないため 5-15 分でタイムアウト。結果：exit 0 だが**何も書かれない** — 100% データロス。生成される `claude -p` コマンドに `--dangerously-skip-permissions` フラグを追加。安全境界は `cd "$DATA_ROOT"`（second-brain 外に出られない）+ prompt ファイルが `scripts/prompts/` でバージョン管理されていることで担保。
- **R-1.8.0-007 · `tools/missed_cron_check.py` · `trigger_recovery`**：`data_root/scripts/` 配下で `run-cron-now.sh` を探していたが、R-1.8.0-003 修正後の `data_root` はユーザーの second-brain — そこに `scripts/` はない。以前 v1.8.0 をインストールした Mac では、`data_root/scripts/` に R-1.8.0-002 修正前の古い `run-cron-now.sh`（`declare -A` を含む）が残っており、上流が patch されていてもそちらが呼ばれて "declare -A: invalid option" でクラッシュ。`Path(__file__).resolve().parent.parent / "scripts" / "run-cron-now.sh"` でパス解決するよう修正し、**常に現在の上流版**を呼び出すように。`LIFEOS_DATA_ROOT` を subprocess env で渡してスクリプトにデータ root を伝えます。
- **R-1.8.0-008 · `scripts/setup-cron.sh` · PATH 拡張**：launchd が起動する shell の PATH（`~/.local/bin:/opt/homebrew/bin:/usr/local/bin:...`）には Claude Code の典型的なインストール先（`~/.claude/local`、`~/.bun/bin`、`~/.npm-global/bin`、`~/.volta/bin`）が含まれておらず、`command -v claude` が false を返して `archiver-recovery`（および全 prompt job）が "claude CLI not found" で失敗。3 つのコマンドビルダー（`repo_command`、`repo_command_pymod`、`repo_command_prompt`）の PATH export 行にこれら 4 つのインストール先を追加。
- **`tools/seed.py`**：`META_GITKEEP_DIRS` から `_meta/inbox`、`_meta/runtime`、3 つの `_meta/eval-history/` サブディレクトリ（`cron-runs`、`auditor-patrol`、`recovery`）が欠落していました。`tools/seed.py` で seed された新しい second-brain repo に、v1.8.0 の cron prompt と `session-start-inbox` hook が書き込むディレクトリが存在していませんでした。同時に `_meta/inbox/notifications.md` のヘッダーも初期化し、cron→session bridge が初日から書き込み先を持つようにしました。
- **`scripts/setup-cron.sh`**（seed.py 修正の対）：`bootstrap_repo_dirs()` ヘルパーを追加し、`main` から `ensure_repo` の後に呼び出します。本修正以前に seed された**既存の** second-brain repo に対して、同じディレクトリと notifications.md ヘッダーを冪等に補完します。今は `$REPO_ROOT/_meta` ではなく `$DATA_ROOT/_meta` を keyed off（R-1.8.0-003 整理）。

- **R-1.8.0-010 · アーキテクチャ PIVOT (post-2026-04-29) · cron アーキテクチャを丸ごと廃止**：本番環境テスト 2 日後、R-1.8.0-001~009 修正後の cron アーキテクチャもユーザーの信頼性テストに失敗しました。5 つの prompt ベース cron job（archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency）がサイレントにデータを失う：cron が起動した `claude -p` session が分析完了後に prompt テンプレートの礼儀正しさで「書き込みますか？」とユーザーに尋ねる — cron は誰も見ていない、session タイムアウト、exit 0、`_meta/eval-history/` は空。`--dangerously-skip-permissions` flag（R-1.8.0-006）は OS レベルの Write 権限のみスキップでき、LLM 自身の対話礼儀はバイパスできません。結論：**cron は決定論性を要求、LLM は非決定論的、このミスマッチは patch では解消できない**。
  - **Pivot 決定（ユーザー判断）**：cron を明示的なユーザープロンプトに置き換え。ユーザーが「インデックス再構築」「月次レビュー」と言えば ROUTER が `scripts/prompts/<job>.md` を読んで内部実行。バックグラウンドプロセスなし。
  - **削除 (17 ファイル)**：`scripts/setup-cron.sh`、`scripts/run-cron-now.sh`、`scripts/commands/run-cron.md`、`tools/missed_cron_check.py`、`tools/cron_health_report.py`、`tools/reindex.py`、`tools/daily_briefing.py`、`tools/backup.py`、`tools/spec_compliance_report.py`、`tools/wiki_decay.py`、`tools/memory.py`、`tools/session_search.py`、`tools/cli.py`、`pro/agents/narrator-validator.md`、`references/automation-spec.md`、`references/session-modes-spec.md`、`docs/architecture/hermes-local.md`。さらに削除ツール用の eval scenarios 3 件。
  - **新規作成 (5 つの user-invoked prompts)**：`scripts/prompts/{reindex,daily-briefing,backup,spec-compliance,wiki-decay}.md` —— 削除された python ツールを置換。それぞれ markdown prompt で、ROUTER が読んで Read/Write/Bash/Glob/Grep で直接実行（ユーザーがキーワードで起動）。
  - **修正 (5 つの既存 prompts)**：`scripts/prompts/{archiver-recovery,auditor-mode-2,advisor-monthly,eval-history-monthly,strategic-consistency}.md` —— 「autonomous cron-triggered」フレーミングを「user-invoked from session」に変更。UNATTENDED CRON CONTRACT ブロック削除（不要）。
  - **Hooks 再構成 (3 つの hook)**：
    - `scripts/hooks/pre-prompt-guard.sh`：Cortex always-on enforcement ブロック（line 111-167）削除。Memory キーワード検出は Write tool で `~/.claude/lifeos-memory/<key>.json` に直接書き込むように変更（削除された `tools/memory.py` を呼ばない）。上朝/退朝ソフトトリガー保持。
    - `scripts/hooks/session-start-inbox.sh`：完全リライト —— 以前は cron 出力を読んでいた、現在は 10 個のメンテナンスタスクの glob で最新ファイルの mtime をスキャン（`_meta/eval-history/<job>-*.md`）、overdue 一覧を `<system-reminder>` で表示。Hook は表示のみ、実行しない；ユーザーが起動を決定。
    - `scripts/hooks/post-task-audit-trail.sh`：弱化 —— Cortex 4 subagent + narrator-validator の R11 audit trail 強制を削除。archiver + knowledge-extractor のみ trail 書き込み強制（永続状態に触れる）。
  - **Cortex を pull-based 化**（`pro/CLAUDE.md` §0.5 リライト）：4 つの Cortex subagent はメッセージごとに自動 launch しなくなりました。ROUTER がメッセージごとに「履歴/概念/SOUL を加えると応答が変わるか？」を判断；変わる → launch、変わらない → スキップ。Subagent description ファイルを全て pull-based 反映に更新。
  - **Slash command リライト**：`/monitor` は view-and-invoke コンソール（cron 監視ではない）；`/memory` は JSON ファイルを直接書き込み（python ミドルウェアなし）；`/search` は Grep tool で直接検索（SQLite FTS5 不使用）。
  - **Spec ドキュメント**：`pro/CLAUDE.md` §0.5 + Session Modes section 両方リライト。`references/hard-rules-index.md` で Cortex は always-on ではないと明記。`pro/AGENTS.md`、`pro/GEMINI.md`、`AGENTS.md` の冒頭に pivot 注釈追加（`pro/CLAUDE.md` を権威と指定、完全な内容スイープは保留）。
  - **統計**：~3500 行の cron インフラ + python ミドルウェア削除。~500 行の user-invoked prompt 内容を追加。差分：23 削除、5 新規、~25 修正。
  - **バックアップ**：`git branch backup-pre-v1.8-pivot @ 7b15509` で pivot 前の状態を保存。

- **R-1.8.0-011 · アーキテクチャ PIVOT 第二段階 (post-2026-04-29) · Bash 骨格 + cortex helpers + python ミドルウェアを全削除 → 100% LLM**：R-1.8.0-010 で cron 層を削除した後、R-1.8.0-011 で次の「決定論的 helpers」層を削除：Bash briefing 骨格、cortex Python データモデル helpers、残りのメンテナンス python ツール。目標：最小実装可能アーキテクチャ = `hooks（免疫系）+ approval.py（セキュリティ）+ 5 個の一回きり bootstrap スクリプト + その他全部 LLM が直接実行`。
  - **Pivot 決定（ユーザー判断、"全 LLM 因为我要增强实用型"）**：LLM が合理的に実行できる helper はすべて LLM 化；hooks（OS プロトコル要求）と `approval.py`（セキュリティ境界）のみコードとして残す。
  - **削除 (23 ファイル)**：
    - Cortex helpers (5)：`tools/lib/cortex/{__init__,concept,extraction,session_index,snapshot}.py`
    - Cascade .py (4)：`tools/extract.py`、`tools/rebuild_session_index.py`、`tools/rebuild_concept_index.py`、`tools/migrate.py`
    - Bash 骨格 + telemetry (4)：`scripts/retrospective-briefing-skeleton.sh`、`scripts/archiver-briefing-skeleton.sh`、`scripts/retrospective-mode-0.sh`、`scripts/archiver-phase-prefetch.sh`
    - Cortex broken FTS5 helper (1)：`scripts/lib/cortex/hippocampus_wave1_search.py`
    - 死んだテスト (9)：`tests/test_{backup,cli,daily_briefing,reindex,extraction,concept_and_snapshot,session_index,package_imports,migrate}.py`
  - **新規作成 (5 つの user-invoked prompts、削除された python ツールを置換)**：
    - `scripts/prompts/rebuild-session-index.md`、`scripts/prompts/rebuild-concept-index.md`、`scripts/prompts/migrate-from-v1.6.md`、`scripts/prompts/snapshot-cleanup.md`、`scripts/prompts/extract-concepts.md`
  - **Spec 書き直し (5 agent spec)**：
    - `pro/agents/hippocampus.md` L88-92：FTS5 SQLite helper → Grep tool で INDEX.md を直接スキャン
    - `pro/agents/retrospective.md` L47-55：Python helper パス削除、inline LLM rebuild のみ；L244 R10 boundary 書き直し
    - `pro/agents/archiver.md`：snapshot Python helper ブロック → inline Write + 明示的 YAML schema；extraction Python helper → inline tokenize/stopword/slug ステップ；SessionSummary Python helper → 直接 Write + 明示的 byte-level フォーマット契約；v1.7.2.3 rationale ブロック更新
    - `pro/CLAUDE.md` L268-286：HARD RULE briefing skeleton ブロック（retrospective + archiver）削除
  - **受け入れたコスト**：retrospective Mode 0 ~30× 遅い；archiver Adjourn 10-12 min → ~25-30 min；hippocampus Wave 1 が FTS5 stemming を失う
  - **受け入れたリスク**：SessionSummary フォーマットドリフト、Concept slug ドリフト（SHA-1 fallback で緩和）、SOUL snapshot 蓄積、6-H2 briefing で H2 欠落の可能性
  - **保持されるコード（不可侵）**：11 hooks + `tools/approval.py` + `seed.py` / `seed_concepts.py` / `skill_manager.py` + `tools/lib/{config,llm,notion,second_brain}.py` + `scripts/lib/{audit-trail.sh,sha-fallback.sh}` + R-1.8.0-010 の 10 個の cron-replacement prompts
  - **統計**：~3500 行削除、~700 行追加。差分：-2800 行。
  - **バックアップ**：`git branch backup-pre-option-A @ 744d034`。

- **R-1.8.0-012 · Monitor mode を自然言語のみで起動（post-2026-04-29 ユーザーフィードバック）**：ユーザー原文「这个不能要任何命令全部都要自然语言」。Monitor mode は自然言語キーワードで起動する必要があり、ユーザーに `/monitor` を入力させてはいけない。Slash コマンドは backup mode として残す（`/memory` `/search` `/method` と同じ扱い）。
  - **`scripts/hooks/pre-prompt-guard.sh`**：`MEMORY_KEYWORD_RE` 検出ブロックの直後に `MONITOR_KEYWORD_RE` 検出ブロックを追加。キーワード：监控模式 / 进监控 / 进 monitor / 开监控 / 监控控制台 / 看系统状态 / 看 cron / 看维护状态 / 维护控制台 / ops console / monitor mode / enter monitor / open monitor / 看 lifeos 状态 / 进运维。マッチした場合 `<system-reminder>`（`trigger=monitor`）を注入し、ROUTER に `Task(subagent_type=monitor)` を直接 launch させる —— ユーザーを `/monitor` に誘導しない。
  - **`scripts/hooks/pre-prompt-guard.sh`**（同 edit で修正 —— R-1.8.0-010 漏れ）：MEMORY ブロックのテキストがまだ ROUTER に `python -m tools.memory emit "..."` を呼ばせていたが、`tools/memory.py` は v1.8.0 pivot で削除済み。ROUTER に Write tool で `~/.claude/lifeos-memory/<sanitized-key>.json` を直接書き込むよう変更（明示的な JSON schema：`value` / `role` / `created` / オプショナル `trigger_time`）。
  - **`pro/CLAUDE.md` Special Triggers セクション**：上朝 / 退朝 / Quick Mode と並んで Monitor Mode エントリーを追加。自然言語が主経路、`/monitor` は backup と明記。
  - **`pro/CLAUDE.md` Auto-Trigger Rules セクション**：Memory auto-emit と並んで「Monitor mode auto-launch」サブセクションを追加。中/英キーワード列挙。「4 つの v1.7.3 slash コマンド」記述を 5 つに拡張（`/monitor` 含む）。
  - **`scripts/commands/monitor.md`**：先頭に「Backup mode」注記ブロックを追加。ROUTER がユーザーに slash コマンドを入力させないよう指示 —— 自然言語が主経路。Slash コマンドは：focus パラメータの精密制御（`/monitor wiki`）、auto-trigger fallback（regex ミスマッチ）、テストシナリオ用に残す。
  - **どのパスも壊さない**：`/monitor` slash コマンドはパワーユーザー向けに引き続き利用可能；`pro/agents/monitor.md` subagent 自体は未変更。エントリーパスを拡張しただけ。

- **R-1.8.0-013 · llm_wiki からの 5 つの借用（post-2026-04-29 ユーザーリサーチ後の決定）**：ユーザー原文「1，单独 2，llm 3，折中 4，全，完整」で 5 つの借用すべてを一括承認。lifeos は「プレーンテキスト + frontmatter id」から「Obsidian-vault 互換の wikilink 知識グラフ + 非同期 review queue + LLM フレンドリーな関連度シグナル + ページ分類の細分化」へ移行。出典：[nashsu/llm_wiki](https://github.com/nashsu/llm_wiki)。
  - **借用 1 · 全文 Obsidian `[[wikilinks]]` 構文**：`wiki/`、`_meta/concepts/`、`_meta/sessions/`、`_meta/methods/`、`_meta/people/`、`_meta/comparisons/`、`SOUL.md`、`_meta/STRATEGIC-MAP.md` 本文中のあらゆる相互参照を `[[id]]` または `[[id|表示名]]` で統一。Frontmatter は YAML 文字列のまま（機械パース可）、唯一の例外は `_meta/concepts/<id>.md` の `provenance.source_sessions: ["[[YYYY-MM-DD]]"]` と `outgoing_edges[].target: "[[concept-<id>]]"`。`references/wiki-spec.md` の「相互参照禁止」ルールは取消線で廃止。
  - **借用 2 · Obsidian vault レイアウト**：`tools/seed.py` が `.obsidian/app.json`（`useMarkdownLinks: false`、`newLinkFormat: shortest`、`userIgnoreFilters` で `_meta/runtime/` 除外）、`.obsidian/core-plugins.json`（graph + backlinks + outgoing-links + tag-pane 有効化）、`.obsidian/.gitignore`（workspace.json などデバイス局所状態の除外）を書き出すように。ユーザーは second-brain を Obsidian で直接開いてグラフビュー + バックリンクパネルを使える。仕様：`references/obsidian-spec.md`。
  - **借用 3 · 非同期 Review Queue（「ユーザー対応が必要なもの」の単一エントリー）**：`_meta/review-queue.md` がそれまで 7 箇所に散らばっていた todo を 1 つの優先順序付きリストに統合（auditor-patrol / advisor-monthly / strategic-consistency / archiver-recovery / eval-history-monthly 各レポートの action item + violations.md + cron notifications.md）。YAML 項目スキーマ：`id`（`r{YYYY-MM-DD}-{NNN}`）/ `created` / `source` / `type` / `priority`（P0/P1/P2）/ `summary` / `detail_path` / `related`（wikilinks）/ `suggested_action` / `status`（open/reviewed/resolved/dismissed）/ `closed_at` / `closed_by`。in-place 状態変更（必ず Edit、Write 禁止）；resolved > 100 項目は `_meta/review-queue/archive/{YYYY-MM}.md` へ自動アーカイブ（折衷策、ユーザー選択 3 に対応）。仕様：`references/review-queue-spec.md`。新ウォーカー prompt `scripts/prompts/review-queue.md`（「处理 queue」/「看 queue」/「review queue」）が項目を 1 件ずつ A（実行）/ R（見たが対応保留）/ D（dismiss）/ S（skip）/ Q（quit）の選択肢で処理。
  - **借用 4 · 4 シグナル LLM フレンドリー関連度モデル（hippocampus Wave 2 単純加重式を置換）**：`relevance(candidate, current) = 3 × direct_link_count + 4 × source_overlap_count + 2 × common_neighbor_count + 1 × type_affinity`。カウント（Adamic-Adar の `1/log(degree)` ではなく）を採用したのは LLM が log を確実に計算できないため（ユーザー選択 2「LLM 簡略版」に対応）。Type affinity マトリクス：同一タイプ 1.0、関連（concept↔wiki/person/method）0.5、無関係 0.0。変更箇所：`references/hippocampus-spec.md` Wave 2 + `pro/agents/hippocampus.md`。
  - **借用 5 · ページ分類の細分化 —— people と comparisons がそれぞれ独立ディレクトリに**：新規 `_meta/people/<id>.md`（people をファーストクラスエンティティに；canonical_name / aliases / relationship / privacy_tier / mention_count / concepts_linked wikilinks；仕様：`references/people-spec.md`）と `_meta/comparisons/<id>.md`（決定対比をファーストクラスエンティティに；options / criteria / decision / confidence / outcome 追跡；仕様：`references/comparison-spec.md`）、ユーザー選択 1「单独，独立ディレクトリで frontmatter type フィールドのみではない」に対応。Sources/synthesis/queries は分離せず（sessions/wiki と重複）。
  - **新規仕様ファイル（4）**：`references/people-spec.md`、`references/comparison-spec.md`、`references/obsidian-spec.md`、`references/review-queue-spec.md`。
  - **修正仕様ファイル（3）**：`references/wiki-spec.md`（ページ分類 + wikilink convention セクション、「相互参照禁止」を取消線）、`references/concept-spec.md`（wikilink convention に frontmatter 例外フィールド例）、`references/hippocampus-spec.md`（Wave 2 4 シグナル式）。
  - **修正 subagent（5）**：`pro/agents/hippocampus.md`（Wave 2 spec 同期）、`pro/agents/archiver.md`（Phase 2 ルーティング + wikilink 書き込み HARD RULE + review queue append）、`pro/agents/knowledge-extractor.md`（同じルーティング/wikilink/queue HARD RULE）、`pro/agents/retrospective.md`（Mode 0 ブリーフィング wikilinks + 項目あれば ## Open Review Queue H2 セクション出力）、`pro/agents/monitor.md`（Review Queue Dashboard）。
  - **修正 prompt（5 メンテナンス + 2 新規）**：5 つの v1.8.0 メンテナンス prompt（`auditor-mode-2.md` / `advisor-monthly.md` / `strategic-consistency.md` / `archiver-recovery.md` / `eval-history-monthly.md`）すべてに「v1.8.0 R-1.8.0-013 · Review Queue Append (HARD RULE)」セクションとソース固有 YAML テンプレートを追加。新規 `scripts/prompts/review-queue.md`（借用 3 のウォーカー）と `scripts/prompts/migrate-to-wikilinks.md`（既存コンテンツの全量 wikilink 移行、ユーザー選択 4「全，完整」に対応）。
  - **修正ツール（1）**：`tools/seed.py` —— 3 つの新規 `META_GITKEEP_DIRS`（`_meta/people`、`_meta/comparisons`、`_meta/review-queue/archive`）、定数 `_REVIEW_QUEUE` / `_OBSIDIAN_APP_JSON` / `_OBSIDIAN_CORE_PLUGINS` / `_OBSIDIAN_GITIGNORE`、関数 `_write_obsidian_vault(target)` を `_seed_scaffolding()` に接続。スモークテスト合格。
  - **修正 hook（1）**：`scripts/hooks/session-start-inbox.sh` —— `_meta/review-queue.md` の `## Open items` セクションを awk でパースし P0/P1/P2 別カウント；SessionStart system-reminder に `📋 Review queue: N P0 / M P1 / K P2 open. Latest: <summary>. Say "看 queue" to walk through.` を出力。
  - **R-1.8.0-013 セルフ監査修正（同コミット）**：並列 agent 監査で 7 つの実バグを発見、ユーザー原文「全部干完，不要再留任何 bug 了」に従い同リリース内ですべて修正：
    - **HIGH · awk priority 正規表現が未アンカー** —— パターン `/priority: P0/` が `summary: "因为 priority: P0 上周没处理"` のような本文プローズにマッチして二重カウント。`^[[:space:]]*priority:[[:space:]]*P0([^0-9]|$)` にアンカー（GNU awk の `\b` ワード境界に依存しない）。スペース無し（`priority:P0`）、複数スペース（`priority:    P0`）の variant も正しく扱う。
    - **HIGH · CHANGELOG が session-start hook 出力に `Latest: <summary>` を約束していたが hook はカウントのみ出力** —— awk を拡張して最新 open 項目の最初の `summary:` を捕獲、80 文字で切詰、`Latest: ${REVIEW_QUEUE_LATEST}` 行で出力。bash で tab 分離。`[[person-*]]` 項目で `privacy_tier: high` の場合のプライバシーフィルター注記追加。
    - **HIGH · `source_session(s)` フィールド名の単複不一致** —— `references/comparison-spec.md`（単数、決定の瞬間）と `references/concept-spec.md`（複数、累積する証拠）の命名違い。`references/wiki-spec.md` 例外フィールドリストで意味的区別を明記、`pro/agents/archiver.md` + `pro/agents/knowledge-extractor.md` を両方の名前と各 cardinality の理由を引用するよう同期。
    - **HIGH · 4 シグナル `type_affinity` の related 集合が不足** —— CHANGELOG は `concept↔wiki/person/method` を引用したが spec + agent は `concept↔wiki, concept↔person` のみ。すべてを `concept ↔ wiki, concept ↔ person, concept ↔ method, wiki ↔ method, person ↔ comparison` に揃えた。
    - **MEDIUM · advisor-monthly に `outcome-unmeasured` type enum 欠落** —— type リストに追加 + priority 拡張で P2 を含む（comparison-spec の outcome-tracking フローで「90 日経過しても comparison に ## Outcome なし」を検出するため）。
    - **MEDIUM · awk エラーの暗黙呑み込み** —— awk コマンドから `2>/dev/null` を削除、パーサ回帰エラーを SessionStart hook log に浮上させる（暗黙的に空文字列を出力するのではなく）。新規 vault のファイル不在は `|| true` で引き続きカバー。
    - **LOW · pre-prompt-guard の 2 hook ブロックが同時発火** —— REVIEW_QUEUE + MIGRATE_WIKILINKS 両方のキーワードを含むメッセージで 2 つの競合する `<system-reminder>` を注入。両ブロックに `[ "$ACTIVITY_REMINDER" != "yes" ]` first-match-wins ガードを追加。
    - **LOW · `_OBSIDIAN_GITIGNORE` 定数名が repo ルートの `_GITIGNORE` と重複** —— `tools/seed.py` 244 行目に vault 内部のものであることを inline コメントで明記。
    - **LOW · トリガーキーワードリストが hook + pro/CLAUDE.md + walker prompt の間でドリフト** —— `scripts/hooks/pre-prompt-guard.sh` REVIEW_QUEUE_RE を canonical source に指定、CLAUDE.md と `scripts/prompts/review-queue.md` をそれに合わせる。
  - **R-1.8.0-013 第 2 ラウンドセルフ監査修正（同コミット）**：6 agent 並列ディープ監査（python-reviewer + silent-failure-hunter + code-reviewer + security-reviewer + comment-analyzer + type-design-analyzer）でさらに **15 個のバグ**を発見、3 つの CRITICAL/HIGH を含み、それらは全ての新規 vault で Obsidian 統合を静かに壊していた。すべて修正：
    - **HIGH · Obsidian core-plugin ID が間違っていた** —— `tools/seed.py` が `.obsidian/core-plugins.json` に `"backlink"`、`"outgoing-link"`、`"starred"` を書き込んでいたが、Obsidian の実際の plugin ID は `"backlinks"`、`"outgoing-links"`、`"bookmarks"`（最後は Obsidian 1.2 / 2023 年 8 月に `starred` から改名）。Obsidian は未認識の plugin ID を黙って無視するため、すべての新規 lifeos vault は Obsidian で開いた時にバックリンクパネル / 出向リンクパネル / ブックマークパネルが静かに無効化されていた。3 つの ID を全て修正 + Obsidian ドキュメント URL の説明コメントを追加。
    - **HIGH · `.obsidian/.gitignore` に `cache`、`plugins/`、`themes/` が欠落** —— ユーザーがインストールしたコミュニティプラグイン / テーマがデバイスごとなのに静かに git にコミットされ、リポジトリを汚染。エントリを追加 + `hot-reload.json`（開発フロー）+ なぜ 2 つの `.gitignore` ファイルが必要か（Obsidian Sync は vault-root `.gitignore` を読まない）の説明コメントを追加。
    - **HIGH · awk parser が CRLF + BOM で破綻** —— Windows エディタで保存された `_meta/review-queue.md` が CRLF や BOM を含むと、静かに 0 カウントを生成。`{ sub(/\r$/, "") }` 最初の awk ルール + `NR == 1 { sub(/^\xef\xbb\xbf/, "") }` BOM 削除を追加。
    - **HIGH · awk substr() が UTF-8 をバイト単位で切る** —— POSIX awk substr はバイトインデックスのため、`substr($0, 1, 77)` が 3 バイトの中国語文字をバイト中央で切断し、無効な UTF-8 ゴミを出力する可能性。`substr($0, 1, 67) "..."` に縮小（`length > 70` ガード付き）、3 バイトの安全マージン確保。block-scalar ガード（`if ($0 ~ /^[|>][-+]?[[:space:]]*$/) { next }`）も追加し、YAML `summary: |\n  text` が `Latest: |` として表示されないよう修正。
    - **HIGH · YAML 三重ブラケット構文が無効** —— `references/people-spec.md` と `references/comparison-spec.md` の例で `concepts_linked: [[[concept-id-1]], [[concept-id-2]]]` を wikilink 配列のつもりで書いていたが、PyYAML は素の `[[x]]` を入れ子リスト `[['x']]` としてパースする、wikilink 文字列ではない。実証検証済。クォート付き文字列に修正：`concepts_linked: ["[[concept-id-1]]", "[[concept-id-2]]"]`。両 spec に required-fields リスト + 不変条件ドキュメントも追加。
    - **HIGH · concept-spec に矛盾する 2 つの `outgoing_edges` schema** —— 82 行目の元版は `to: concept_id`、`via:`、`last_reinforced:`、R-1.8.0-013 で追加された 417 行目は `target: "[[]]"`、`via:` なし、`last_co_activated:`。実装はランダムにどちらかを選ぶ。整理：82 行目を canonical wikilink schema、414 行目は移行前後の対比例として注記。誤解を招く `weight: -2` 例を削除（負の重みは lifecycle / decay でどこにも定義されていない）。
    - **HIGH · `migrate-to-wikilinks.md` に単語境界要件が欠落** —— 素朴な名前置換は "Algorithm" を `[[person-al]]gorithm` に破壊する可能性（"Al" という名前の人がいる場合）。明示的な `\bword\b` 境界ルール + wikilinks-inside-wikilinks ガード + slug 衝突ハンドリング（concept-spec § 4.2 に従う）+ クロスプラットフォーム Windows PowerShell バックアップコマンド + 明示的実行順序ノート（Phase 5 バックアップは数値順序が逆でも Phase 2 書き込みより前に実行される必要あり）を追加。
    - **HIGH · review-queue に id ゼロパディングルール + 並行性モデル + アーカイブ順序が欠落** —— `r{TODAY}-{NNN}` が曖昧（001 か 1 か？）。文書化：常に 3 桁ゼロパディングで辞書順ソート可能に。lock-free 楽観的並行性プロトコル（append 前再読み込み + 衝突時 verify-and-retry）を追加。明示的アーカイブ順序ルール（`closed_at` 昇順、月は `closed_at` から解析）を追加。
    - **HIGH · review-queue + comparison ステータスに後退ガードなし** —— `dismissed → open` は無効と記述されていたが強制されていなかった。MONOTONE / 一方向 DAG として明示的に文書化。`closed_at` / `closed_by` は `status != open` 時に REQUIRED 非 null と宣言。Comparison `decision` は `options[*]` のいずれか OR "deferred" OR "none" でなければならない。`confidence` は [0.0, 1.0] 内必須。`revisited` 配列は最大 50 エントリに制限（オーバーフローは body `## Audit trail` にローテート）。people-spec enum に `relationship: organization` を追加（ルーティングルールで参照されていたが enum に欠落）。
    - **HIGH · people-spec privacy_tier にマシンバリデータなし** —— `high` 層は散文のみの強制だった。Privacy Validator セクション追加：post-write lint が body 内の 10+ 桁数字、街路アドレス正規表現、メール、canonical 以外の氏名をスキャン → CLASS_C 違反 + P0 review-queue アイテム。各層が何を許可するか定義する operational tier テーブル（low/medium/high）を追加。monotonicity 不変条件追加：`last_mentioned >= first_mentioned`、`mention_count` append-only。
    - **MEDIUM · pre-prompt-guard.sh の中国語マッチングが locale 依存** —— POSIX/C locale で実行すると、上朝/退朝/监控模式/处理 queue などのマルチバイト UTF-8 トリガー語を誤比較する可能性。スクリプト早期に `export LC_ALL=C.UTF-8 LANG=C.UTF-8`（en_US.UTF-8 フォールバック）を grep 前に追加。
    - **LOW · concept-spec 内の古い `tools/migrate.py` 参照** —— このファイルは R-1.8.0-011 pivot で削除されたが、spec 内でまだ 3 回参照されていた（148、319、351 行）。代替の `scripts/prompts/migrate-from-v1.6.md` に更新。
    - **LOW · 相互排他コメントが誤解を招く** —— 「ROUTER は 2 つの競合する system-reminder ブロックを受け取る」と書いていたが、実際の害は banner が不一致な 1 つの結合ブロックに連結されること。コメントを書き直して実際の害を説明。
    - **LOW · MIGRATE_WIKILINKS_EOF heredoc のフェーズ番号が実行順でない**（0,1,5,2,3,4,6）—— LLM が順番に追うと混乱。実行順の 1-10 番号付きリストに書き直し + ソース prompt のフェーズ番号がなぜ異なるかの明示的ノート追加。

- **R-1.8.0-013 ユーザー読み取り専用 repo 監査（同コミット）**：ユーザーが独立して 67 個の tracked `.py/.sh/.yml` ファイル全てを監査（R-1.8.0-013 より広範囲）し、9 個のアクション項目を発見。「全部干完，不要再留任何 bug 了」マンデートに従い同リリース内ですべて受け入れ修正：
  - **CRITICAL · `scripts/hooks/pre-bash-approval.sh` fail-OPEN**：3 つの fail-open パスが approval bridge クラッシュ時に危険コマンドを静かに通過させていた（ImportError、JSON パース失敗、空出力）。3 つのパス全て fail-CLOSED に書き直し —— bridge エラーは現在コマンドをブロックし、stderr 経由で診断情報をユーザーに提示（rc=$BRIDGE_RC + キャプチャされた stderr + LIFEOS_YOLO_MODE=1 バイパス手順）。「未インストール」のケースは依然通過（存在しない guard を強制できない）が、他のあらゆるパスはデフォルトで拒否。
  - **CRITICAL · `tools/research.py` SSRF**：研究ツールが検索結果から任意の `http(s)` URL を取得、private-network denylist なし —— 細工された検索結果を介して内部ネットワークプローブとして使用される可能性。`_is_private_ip()` 追加（IPv4 RFC1918 / loopback / link-local / クラウドメタデータ + IPv6 ::1 / fc00::/7 / fe80::/10 + リテラル hostname denylist：`localhost`、`metadata.google.internal`、`metadata.azure.com`、AWS 169.254.169.254 など）をカバー。`_is_safe_url()` 追加で非 http(s) スキーム拒否 + IP チェック実行。任意のネットワーク I/O 前に `_fetch_text` に配線してブロック。ブロックされた URL は stderr に表示し、operator が拒否を見られるよう。`_MAX_RESPONSE_BYTES = 5 MB` 切り詰めも追加でメモリ制限。
  - **CRITICAL · `tools/sync_notion.py` BaseException キャッチ**：ページごとの同期ループが `BaseException` をキャッチし、`KeyboardInterrupt` / `SystemExit` を呑み込んで Ctrl-C を「page failed」としてログ。`(KeyboardInterrupt, SystemExit): raise` を最初に、次に `Exception` で実際の同期失敗を処理するよう変更。インタプリタシグナルが正しく伝播するように。
  - **CRITICAL · `tools/approval.py` Tirith サイレントミス**：オプションの `tools.tirith_security` モジュールの ImportError は静かに呑み込まれていたが、`setup-hooks.sh` の説明は「tirith enabled」と謳っていた。Tirith 利用不可時の一回限り stderr warning + モジュールレベル `_TIRITH_UNAVAILABLE_WARNED` フラグを追加（コマンドごとではなくプロセスごとに 1 回 warn）。`setup-hooks.sh` 説明を「optional tirith if installed」に更新し、開示が現実と一致するように。
  - **CRITICAL · `tools/seed_concepts.py` fresh clone で破綻**：R-1.8.0-011 cortex-helper クリーンアップで削除された `tools.lib.cortex.{concept,extraction}` モジュールに依存、よって `import tools.seed_concepts` はすべての fresh clone で失敗（`python -c` で実証検証済）。機能は LLM 駆動の `scripts/prompts/extract-concepts.md` と `scripts/prompts/rebuild-concept-index.md` で既に置換済。デッドモジュール + テスト（`tests/test_seed_concepts.py`）削除。
  - **HIGH · `.github/workflows/test.yml` ruff `continue-on-error: true`**：lint 回帰が静かに通過。`continue-on-error` を削除。既存ベースラインのクリーンアップが必要 —— 16 個の lint エラーを修正（12 個自動 + 4 個手動：`B023` `approval.py:455` `get_input` スレッド関数のクロージャバインディングバグ、`SIM105` try/except/pass → `contextlib.suppress`、`PTH105/108` `os.replace/unlink` → `Path.replace/unlink`、`SIM102` `skill_manager.py:272` ネスト if 結合）。Ruff ベースラインがクリーンに。
  - **HIGH · `.github/workflows/test.yml` bash 構文チェックが `scripts/lib/*.sh` を漏らす**：ハードコード glob は `scripts/*.sh scripts/hooks/*.sh evals/run-eval.sh tests/hooks/test_*.sh` だけ列挙。`git ls-files '*.sh'` に変更し、任意のディレクトリ下の新規 shell ファイルが自動的にカバーされるように。現在 tracked の 18 個の `.sh` 全てが `bash -n` をパスすることを検証。
  - **HIGH · `scripts/hooks/pre-write-scan.sh` JSON 正規表現パース**：jq 不在時に `grep/sed` 正規表現で JSON パースしていたが、エスケープされた引用符 / 複数行コンテンツ / ネストされたフィールドで失敗 → スキャンされていない書き込みのサイレントリーク。Python JSON パーサーを中間層フォールバックとして追加（Python は Claude Code が動作するあらゆる場所で利用可能；`\x1f` unit separator で file_path と content を安全に区切る）。最終手段の正規表現パスは現在センシティブパス（`/_meta/`、`/SOUL.md`、`/wiki/`、`/.env`、`/secrets`）に対して FAIL-CLOSED —— ブロック + jq か python のインストールをユーザーに伝える。
  - **MEDIUM · `tools/search.py` config 例外を呑み込む**：bare `except Exception` が破損した config と ImportError / AttributeError（config loader の実バグ）の両方を隠す。`(FileNotFoundError, OSError, ValueError, KeyError)` + stderr warning に絞り込み、破損 config を可視化しつつ recency_boost_days=90 デフォルトフォールバックを保持。
  - **MEDIUM · `tools/export.py` pandoc に timeout なし**：不正な入力やファイルシステムストールで無限待機。`subprocess.run` に `timeout=60` 追加 + 新しい `subprocess.TimeoutExpired` handler で入力ファイルサイズと是正ヒントを stderr に報告。

ネット：11 ファイル修正、2 ファイル削除（seed_concepts.py + test）。以前の hook テストは全てパス。3 個の既存の `test_stop_session_verify.sh` 失敗は未変（最後の変更は v1.7.3、本監査とは無関係）。

- **R-1.8.0-013 ユーザー第 3 ラウンド監査（同コミット）**：ユーザーが HEAD `d7639fc` で第 3 ラウンドの独立監査を実施、以前のラウンド 1/2 で捕捉できなかった 7 つの問題を発見。すべて確認・修正。第 3 ラウンドの強みはラウンド 2 のセキュリティ/パース修正の**境界**を攻撃したこと：
  - **CRITICAL · `tools/lib/second_brain.py:60` CRLF frontmatter が無視される**：parser は文字どおりの `content.startswith("---\n")` を使用していたため、Windows CRLF 行末で保存されたファイルは「frontmatter なし」と判定され、body=ファイル全体になっていた。実証検証済。正規表現 `^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n` に置換し LF/CRLF/混合 + フェンス末尾の空白を許容。`tests/test_second_brain.py` に 4 つの回帰テスト追加（CRLF parsed、CRLF no-frontmatter、混合行末、フェンス末尾空白）—— 25 個の frontmatter テスト全合格。
  - **CRITICAL · `tools/research.py:381` SSRF guard が DNS を解決しない**：以前の修正はリテラル IP と hostname denylist のみチェックだったため、`internal.corp.example` が `10.0.0.1` を指すと通過してしまう。`socket.getaddrinfo()` 解決 + 全 A/AAAA レコードへの IP チェックを追加。DNS 失敗（NXDOMAIN/timeout）は**安全でない**として扱う（fail-CLOSED + stderr 表示）。合成 hostname を使うテストフィクスチャは `LIFEOS_RESEARCH_SKIP_DNS_SSRF=1` 環境変数でオプトアウト（プロダクションコードは絶対設定しない）。
  - **CRITICAL · `tools/research.py:354` リダイレクトチェーンバイパス**：`httpx.Client(follow_redirects=True)` は元の URL のみ SSRF チェックが走るため、公開 URL が 302→ プライベート IP すれば完全にバイパス可能。`follow_redirects=False` に変更、`_fetch_text` で Location ヘッダを手動で歩く（最大 5 ホップ）、ホップごとに `_is_safe_url()` 再実行。相対リダイレクトは `urljoin` で解決。
  - **CRITICAL · `tools/research.py:452` resp.text が body 全体をメモリにロード**：以前の max_bytes 切り詰めは httpx が応答全体をメモリにロード**した後**に発生 —— メモリ保護として無意味。`client.stream()` + バイトカウンタを使い `max_bytes` でストリーム途中停止する `_fetch_text` に書き直し。`.stream()` を持たない FakeClient のテストは非ストリーミング分岐に落ちる（依然 post-load 切り詰めで保護）—— モックは小さい合成 body を返すので安全。
  - **CRITICAL · `scripts/hooks/pre-bash-approval.sh:75` missing-source fail-OPEN**：`tools/approval.py` がどの候補パスにも見つからない時、hook が exit 0（=承認）。私のラウンド 2 修正は「存在しない guard を強制できない」と主張したが、監査人は正しく反論 —— **セキュリティソース欠落自体が critical 状態**。fail-CLOSED に変更し完全な診断（検索したパス、`setup-hooks.sh` での復旧手順、`LIFEOS_YOLO_MODE=1` エスケープハッチ）を追加。新規 `tests/hooks/test_pre_bash_approval.sh` 6 ケース追加（safe / hardline / empty / malformed JSON / missing source fail-CLOSED / YOLO bypass）—— 9 アサーション全合格。
  - **WARNING · `tools/search.py:302` 例外が意味的に不十分**：以前の修正は `(FileNotFoundError, OSError, ValueError, KeyError)` に絞ったが、プロジェクトには専用の `ConfigError` クラス（「config が壊れている」のカノニカルシグナル）がある。`except (ConfigError, FileNotFoundError)` に変更 —— config loader の実バグ（ImportError、AttributeError）はユーザーに伝播するように。
  - **WARNING · `tools/lib/notion.py:215` rich_text > 2000 文字のサイレント失敗**：`_body_to_children` は body 全体を 1 つの rich_text オブジェクトでラップしていたが、Notion API は各オブジェクトの content > 2000 文字を拒絶。長い body の同期はサイレントに失敗していた。1900 文字での段落境界チャンキング追加（段落自体が長い場合はハードスプリット）、チャンクごとに 1 つの paragraph ブロックを発行。空 body は引き続き 1 つの空 paragraph を発行（旧動作と一致）。新規定数 `_NOTION_RICH_TEXT_MAX = 1900`。

検証：
- 18 個の tracked .sh すべて `bash -n` パス
- Ruff baseline: All checks passed
- `pytest tests/test_research.py`（28 テスト）+ `test_second_brain.py`（25 テスト）+ `test_sync_notion.py`（14 テスト）= 67 パス
- Hook テストスイート：6/7 パス（唯一失敗 `test_stop_session_verify` は v1.7.3 以来の既存失敗、未変）
- 新規 `tests/hooks/test_pre_bash_approval.sh`: 9/9 アサーションパス

アーキテクチャ注記（先送り —— 監査言及だが本ラウンド範囲外）：
- `tools/approval.py:713` 224 行 god 関数を 5 層に分割
- 2 hook の重複 session discovery → `_lib.sh` ヘルパー
- `tools/lib/config.py:137` 119 行 load_config 分割
- `evals/run-tool-eval.sh:223` frontmatter `eval`（repo-trust スコープで緩和、未除去）
- research/notion の `Any` types → `Protocol` 定義
- `ApprovalDecision` TypedDict
- `tools/search.py:212` SQLite/FTS sessions index
- `tools/export.py:210` ストリーミング generator
- `--notion-token-stdin` UX 改善
- Hook JSON parser 重複除去
- `setup-hooks.sh:310` SKILL.md install meta 分離

これらは真の改善だが、各々が複数時間のリファクタリング；「安全性/正確性を先に修正、複雑性負債は後」に従い明示的に先送り。

### マイグレーション

```bash
# あなたの second-brain repo（_meta/、SOUL.md、wiki/ がある所）の中で実行：
cd /path/to/your/second-brain
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
bash ~/.claude/skills/life_OS/scripts/setup-cron.sh install
# cd できない場合：LIFEOS_DATA_ROOT=/path/to/second-brain bash ... install
```

第二の脳のデータマイグレーション不要。v1.7.x データは完全互換。`$PWD`（または `$LIFEOS_DATA_ROOT`）に `_meta/` がない場合、install は明確なメッセージでエラー終了します — 設定ミスは静かに間違った root をスキャンするのではなく、明確に失敗します。`bootstrap_repo_dirs` は冪等 — 既にディレクトリがある repo での再実行も安全。macOS で再インストール後：`launchctl unload ~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist && launchctl load ~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist` で新しい `WorkingDirectory` と `--root` を反映。

### Audit 結論（v1.8.0 final）

v1.7.3 audit が発見した「spec で約束したが自動化されていない」ギャップが close。AUDITOR Mode 2 / ADVISOR monthly / eval-history monthly / strategic consistency / wiki decay / spec compliance / archiver recovery / boot catch-up すべて ✅。

ユーザーフィードバック：「Hermes 和 cortex 的问题」→「为什么设计好了但没跑起来」→「不要 routines 也能实现」→「我不可能每天都开新 session」→「完整版必须一次性全部做完」。

---

## [1.7.3] - 2026-04-26 / 2026-04-27 - Cortex 強制起動 + 自動トリガー + archiver Phase 2 切り出し + デッドコード 4 モジュール削除

> 「ツールを実際に使える状態にする」release window。3 ラウンドの反復を全て単一 v1.7.3 リリースに squash：
>
> 1. **v1.7.3 base (2026-04-26)**：Cortex always-on hook、4 slash commands、approval guard wired、4 dead modules removed。
> 2. **v1.7.3 自動トリガーパッチ (2026-04-27)**：ユーザーフィードバック後、slash コマンドをバックアップモードに降格。pre-prompt-guard.sh に memory キーワード検出を追加。
> 3. **v1.7.3 archiver 切り出し (2026-04-27)**：Phase 2 を専用 `knowledge-extractor` subagent に切り出し、80%+ の最近の archiver placeholder 違反を修正。spec 一貫性修正 + stop-session-verify LLM_FILL 検出。
>
> 3 ラウンド全てを単一 v1.7.3 リリースに統合（ユーザー要求：「版本号不能变，还是 1.7.3，都要在这个版本里面全部修完」）。

### 追加

- **Cortex always-on 強制起動 (hook 注入)**：`scripts/hooks/pre-prompt-guard.sh` がプロンプト長 80 文字以上または決定キーワード検出時に `<system-reminder>` ブロック（trigger=cortex）を出力し、ROUTER が回答前に 5 つの Cortex subagent（hippocampus / concept-lookup / soul-check / gwt-arbitrator / narrator-validator）を並列起動するよう強制します。v1.7.2 audit が発見したサイレント degradation を修正。短い会話フィラー（「了解」「続けて」）は Cortex をスキップ。
- **4 つの slash コマンドを Claude Code に接続**：新規 `scripts/commands/{compress,search,memory,method}.md` ソースファイル；`scripts/setup-hooks.sh` がインストール時に `~/.claude/commands/` にコピー。コマンド：
  - `/compress [focus]` — インラインコンテキスト圧縮、`_meta/compression/<sid>-compress-<ts>.md` にアーカイブ。
  - `/search <query>` — `tools.session_search` CLI による FTS5 クロスセッション検索。
  - `/memory emit|read|remove|path` — `tools.memory` CLI による 24-48h 短期記憶。
  - `/method create|update|list` — `tools.skill_manager` CLI によるメソッドライブラリ管理。
- **Approval guard 接続 (PreToolUse Bash hook)**：新規 `scripts/hooks/pre-bash-approval.sh` が全 Bash コマンドを `tools/approval.py` にブリッジ。v1.7.2 のギャップを修正：47 個の危険コマンドパターン + hardline + tirith guards が 0 caller だった状態を解消。Hook が stdin JSON を読み、`check_dangerous_command()` を実行、exit 0（サイレント承認）または exit 2 + stderr（理由付きでブロック）。バイパス：`export LIFEOS_YOLO_MODE=1`。`life-os-pre-bash-approval` として登録（PreToolUse · matcher Bash · timeout 5s）。
- **Memory 自動 emit 検出（自動トリガーパッチ · 2026-04-27）**：`pre-prompt-guard.sh` も中/英/日 memory キーワード（記一下 / remind me / 覚えて / TODO 等）を検出し、`<system-reminder>`（trigger=memory）を注入して ROUTER に `python -m tools.memory emit` を自動実行させ、`/memory` へのリダイレクトを防ぎます。Hook activity log に `trigger=memory` 値を追加。
- **pro/CLAUDE.md → Auto-Trigger Rules セクション（自動トリガーパッチ · 2026-04-27）**：memory 自動 emit、compress 自動提案、search 自動トリガー（Cortex hippocampus 経由）、method 自動 create（archiver Phase 2 → knowledge-extractor 経由）を明文化。原則：「ROUTER がユーザーに slash コマンドへの切り替えを求めるのは UX バグ — 直接アクションを実行する」。
- **knowledge-extractor subagent (Phase 2 切り出し · 2026-04-27)**：新規 `pro/agents/knowledge-extractor.md`（Opus tier、[Read, Grep, Glob, Bash, Write] tools）。7 つの Phase 2 sub-step（wiki 六基準ゲート / SOUL 変化 / methods / concepts + Hebbian / SessionSummary / snapshot / strategic-map）を実行し、7 つの永続ファイルを書きます。同時に 7 つの extraction reports を `_meta/runtime/<sid>/extraction/*.md` に書いて archiver が読み戻せるようにします。R11 audit trail を `_meta/runtime/<sid>/knowledge-extractor.json` に。理由：以前の monolithic archiver は 80%+ の placeholder 違反（最近 10+ 回の adjourn 実行が `pro/compliance/violations.md` 2026-04-25 〜 2026-04-27 に記録）があり、一回の invocation で全てを処理する必要があったため。ROUTER は archiver の前に必ず knowledge-extractor を launch する必要があります。

### 変更

- **narrator-validator audit trail HARD RULE**：`pro/agents/narrator-validator.md` の frontmatter `tools` を `[Read]` から `[Read, Bash, Write]` に拡張；新規 "Audit Trail (R11, HARD RULE)" セクション追加、YAML 返却前に `_meta/runtime/<sid>/narrator-validator.json` の書き込みを必須化。
- **バージョンマーカー**：`SKILL.md` frontmatter と 3 つの README badge を `1.7.3` に更新。
- **spec ドキュメントを inline 圧縮へ更新**：`SKILL.md` Trigger Execution Templates の `/compress` セクション、`references/hard-rules-index.md` manual compression bullet、`evals/scenarios/cortex-retrieval.md` CX11 positive case を、削除された `tools/context_compressor.py` を ROUTER inline 圧縮へ置き換える形に書き換え。
- **4 つの slash コマンドファイルをバックアップモードに降格（自動トリガーパッチ · 2026-04-27）**：各 `scripts/commands/{compress,search,memory,method}.md` の先頭に "⚠️ Backup mode" header を追加、対応する pro/CLAUDE.md Auto-Trigger Rules サブセクションへリンク。Slash コマンドは以下の用途で機能保持：(1) ユーザー精密制御、(2) 開発者スモークテスト、(3) 自動トリガー fallback。
- **archiver.md Phase 2 切り出し + spec 一貫性修正（切り出し · 2026-04-27）**：`pro/agents/archiver.md` line 77 修正（以前の "12-section Adjourn Report Completeness Contract" は v1.7.2 旧表記、v1.7.2.3 の "6-H2" に整合）。Phase 2 spec 全面書き換え：主要パスは `knowledge-extractor` subagent へ委譲；legacy 7-sub-step inline spec は fallback として保持。`pro/CLAUDE.md` Step 10 更新：ROUTER は必ず先に `knowledge-extractor` を launch、その後 `archiver`。新 launch 順序テンプレート。
- **stop-session-verify hook LLM_FILL 検出（切り出し · 2026-04-27）**：`scripts/hooks/stop-session-verify.sh check_phase()` 強化。以前は phase header 行の TBD / `{...}` / "placeholder" のみ検出。現在は各 phase header 後 30 行内の未充填 `<!-- LLM_FILL: ... -->` パターンと `LLM_FILL:` 文字列もスキャンし、`placeholder_phases` としてマーク。最近の archiver 違反の真の根本原因（LLM が Bash skeleton をそのまま出力して placeholder を埋めない）を捕捉。

### 削除（4 つのデッドコードモジュール · 1830 行）

- **`tools/prompt_cache.py` 削除**（118 行 0 caller）：Claude Code サブスクリプション環境では無意味。
- **`tools/mcp_server.py` 削除**（227 行 0 caller 0 client 接続）：MCP stdio wrapper は client に接続されたことがない。
- **`tools/context_compressor.py` 削除**（1370 行 0 caller）：圧縮は ROUTER inline 実行。
- **`tools/manual_compression_feedback.py` 削除**（51 行 0 caller）：削除された compressor の出力 helper。
- **`docs/architecture/prompt-cache-strategy.md` 削除**：削除された prompt_cache の spec doc。
- **`docs/architecture/mcp-server.md` 削除**：削除された mcp_server の spec doc。
- **`docs/architecture/hermes-local.md` 整理**：`related:` frontmatter から削除モジュール参照を削除；Borrow/Fork Surface モジュールリストを v1.7.3 の実際状態に書き換え（approval は wired、memory + session_search + skill_manager は保持）；`context_compressor` naming-note 段落を削除。

### マイグレーション

`bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` を再実行して以下を完了：
1. 4 つの新しい slash コマンドを `~/.claude/commands/` にインストール
2. 新規 `life-os-pre-bash-approval` PreToolUse(Bash) hook を登録
3. `pre-prompt-guard.sh` を更新（Cortex always-on + memory キーワード検出を追加）
4. `stop-session-verify.sh` を更新（LLM_FILL 検出 + 30 行 section body スキャンを追加）

インストール後、Claude が実行する全ての Bash コマンドが 47 個の危険パターンでスクリーニングされます；ブロックされた場合、stderr に 🛡️ 守門人 メッセージが表示されます。

第二の脳のマイグレーションは不要。

### Audit 結論（v1.7.3 final 後）

v1.7.2 の全ての dead-weight 発見 + v1.7.3 archiver 違反の根本原因が close：
- Cortex always-on：強制（hook 注入）✅
- approval.py 47 patterns：wired（PreToolUse Bash hook）✅
- 4 つのデッドコードモジュール削除（1830 行）✅
- Slash コマンド接続 + 自動トリガー優先のためバックアップモードに降格 ✅
- Memory 自動 emit：hook がキーワード検出して ROUTER 自動 emit を強制 ✅
- archiver Phase 2 を knowledge-extractor subagent に切り出し ✅
- archiver.md spec 内部一貫性を回復（12-section vs 6-H2 修正）✅
- stop-session-verify LLM_FILL 検出を追加 ✅

このリリース window を駆動したユーザーフィードバック：
1. 「我为什么要用这样的方式来启动这些命令？这些命令不可以直接自动启动吗？」→ 自動トリガーパッチ
2. 「重新检查一下上朝流程和退朝流程」→ 80%+ archiver placeholder 違反を露呈 → 切り出し
3. 「C 还是1.7.3」+「版本号不能变，还是 1.7.3，都要在这个版本里面全部修完」→ 全変更を単一 v1.7.3 リリースに squash

---

## [1.7.2.3] - 2026-04-26 - RETROSPECTIVE skeleton ownership

> Subagent D ownership patch。対象は `pro/agents/retrospective.md`、`SKILL.md`、3つの README、3つの CHANGELOG のみです。

### 変更

- **RETROSPECTIVE の責務を縮小**: `pro/agents/retrospective.md` は、ROUTER が Bash skeleton で Mode 0 の約80%を事前レンダリングすることを明記しました。
- **単一の LLM fill slot**: subagent は `<!-- LLM_FILL: today_focus_and_pending_decisions -->` だけを約5-15行で埋め、Today's Focus と Pending Decisions を書きます。ROUTER がそのブロックを skeleton に差し込みます。
- **バージョン表記**: `SKILL.md` と README badges を `1.7.2.3` に更新しました。
- **install_sha フィールドによる SHA gap 修正**: `SKILL.md` frontmatter に `commit_sha` と `install_date` フィールドを追加しました。`setup-hooks.sh` は git clone deployment 時にこれらを自動書き込みします。新しい `scripts/lib/sha-fallback.sh` は 3 段階の解決を提供します: `SKILL.md` frontmatter → `.install-meta` JSON → `git rev-parse HEAD` → `unknown`。install-skill deployment で発生する `Local commit SHA: unknown` bug を解消します。
- **SOUL/DREAM 表示復活(v1.6.x 体験へ回帰)**: `scripts/retrospective-briefing-skeleton.sh` が `SOUL.md` 全文と最新 `_meta/journal/*-dream.md` 全文を Bash で fenced markdown block に逐字 paste するようになりました。LLM はその上に delta 解釈(confidence trend / today implications)のみを追加し、SOUL/DREAM の構造的内容を圧縮できません。`pro/agents/retrospective.md` ## 2 / ## 3 spec を「Bash paste 全文 + LLM 趨勢解釈」モデルへ更新。v1.7.2.1 の過剰減算(SOUL Health を「変化次元のみ」、DREAM を「1-2 文 digest」へ圧縮)の副作用を撤回。
- **退朝 12 H2 → 6 H2 + LLM token budget(速度修正)**: `pro/agents/archiver.md` Adjourn Report Completeness Contract を 12 H2 から 6 コア H2(Phase 0/1/2/3/4 + Completion Checklist)へ縮小。AUDITOR Mode 3 / Subagent self-check / 子代理调用清单 / Hook fired / total tokens-cost を Completion Checklist 配下の H3 サブ項目へ折り畳みました。新規「Phase 2/3 LLM Token Budget」HARD RULE: Phase 2 narrative ≤ 1500 tokens(wiki/SOUL/method/concept/strategic/SessionSummary/snapshot/last_activity 合算)、Phase 3 narrative ≤ 800 tokens。verbatim DREAM journal は budget に含まない(Bash paste)。速度目標: archiver Adjourn 25 分 → 10-12 分。
- **archiver-briefing-skeleton.sh 新規(archiver の Bash 骨格)**: 新 `scripts/archiver-briefing-skeleton.sh` は `retrospective-briefing-skeleton.sh` の設計を模倣 — 6 H2 Adjourn Report 骨格を出力し、Phase 0/1/4 + 計測事実(outbox path / decision-task-journal counts / wiki-SOUL-DREAM stat / git status / Stop hook health)を Bash paste します。LLM は `<!-- LLM_FILL -->` placeholder(Phase 2/3 narrative + Completion Checklist 値)のみを埋めます。`pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` Step 10 Adjourn Session に配線済み。既存 `archiver-phase-prefetch.sh`(R11 audit trail)と相補的。
- **Session Binding HARD RULE 書き直し(プロダクト方向修正)**: `pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` の Session Binding HARD RULE を明確化: **discussion scope ≠ data write scope**。Session binding は**データ永続化**(decisions/wiki/SOUL がどのプロジェクトに書かれるか)を制約し、**議論話題**は制約しない。ROUTER はユーザーが提起したあらゆる議題(財務 / 戦略 / 対人 / クロスプロジェクト / 抽象)に直接対応する。ROUTER は明示的なユーザー要請がない限り「本窗口角色只做 X」/「请转到其他窗口」/「translate to planner trigger paste for another window」/「召唤翰林院 panel」の deflect 表現を禁止。13 ラウンドの hardening が累積させた「LLM が session binding を業務話題禁止区域と誤読する」副作用を撤回。Life OS を意思決定思考アシスタントの初心へ復元。

### 移行

second-brain の移行は不要です。

---

## [1.7.2.1] - 2026-04-26 - レポート形状とテーマ美観の引き算ホットフィックス

> 引き算だけの小さなホットフィックスです。見えるルールを減らし、テーマの美しさを戻し、バージョンマーカー位置を固定します。v1.7.2.1 を超える新しいバージョン線は追加しません。

### 変更

- **テーマ美観を復元**：ユーザー向け briefing は、コンプライアンス足場に支配されず、現在のテーマの視覚言語へ戻ります。
- **レポート表面を縮小**：ユーザーに見えるレポート形状を 17 個の H2 ブロックから 6 個へ減らし、過剰な儀式ではなく必要な流れを見せます。
- **バージョンマーカーを固定**：バージョンマーカーは安定した予測可能な位置に置き、手動確認とスクリプト確認を容易にします。

### 削除

- **wrapper 必須要件を削除**：compressed paste wrappers は、ユーザー可視のレポート構造として必須ではなくなりました。
- **ユーザーパスのルールを削減**：重複する表示ルールを取り除き、監査モデルを実行可能なまま保ちつつ、毎回の応答が手続き的に見えすぎないようにしました。

### プロダクト重心の再調整（v1.7.2.2 notes）

- **AUDITOR はデフォルトで静かに**：AUDITOR はデフォルトで静かなバックグラウンド検証へ移り、重大な blocker、escalation、またはユーザーが明示的に audit 結果を求めた場合だけ主経路に出ます。
- **Compliance Watch の前置なし**：`Compliance Watch` signals はユーザー可視 briefing の 1 行目に prepend されず、audit / background channels に残ります。
- **新しい H2 構造**：ユーザー向けレポートは新しい H2 構造を採用し、compliance scaffolding ではなく briefing の実質、決定、next actions、evidence を中心にします。
- **trail `SESSION_ID` lock**：runtime audit trails は現在の `SESSION_ID` に lock され、trail evidence が現在の session に結びつき、別 session context へ drift しないようにします。
- **second-brain を前景へ戻す**：system audit は意図的に background へ移り、ユーザーの second-brain content、priorities、working memory が foreground に戻ります。

### 移行

second-brain データ移行は不要です。

---

## [1.7.2] - 2026-04-26 - Hermes Local、Cortex 常時化、圧縮強化

> ローカル実行面、Cortex オーケストレーション、透明な圧縮レポートのためのパッチリリースです。

### 追加

- **Hermes Local 名称と帰属**：`Hermes Local` は Life OS のローカル防護と自動化に対するユーザー向け名称です。内部 / spec ラベルは引き続き `execution layer`、`Layer 3`、`Layer 4` のままです。docs は、借用 / fork したローカルツールコンポーネントを `NousResearch/hermes-agent`（MIT License）に帰属させるようになりました。
- **Hermes Local fork モジュール領域**：6 つの借用 / fork モジュール領域を記録し帰属を明示しました：`tools/approval.py`、`tools/context_compressor.py` + `tools/manual_compression_feedback.py`、`tools/prompt_cache.py`、`tools/memory.py`、`tools/session_search.py`、`tools/skill_manager.py`。Life OS の compressor module 名は `context_compressor` です。
- **cron と MCP ローカル自動化**：ローカルの reindex / daily briefing / backup 予定ジョブを冪等に設定する `scripts/setup-cron.sh` を追加しました。さらに `tools/mcp_server.py` と `docs/architecture/mcp-server.md` により、Life OS CLI tools への任意の MCP stdio 入口を追加しました。
- **Method library と eval-history ループ**：method candidate extraction、method context injection、`_meta/eval-history/` writeback、monthly self-review readback を追加し、反復する手順シグナルとコンプライアンスシグナルを閉ループ化しました。

### 変更

- **Cortex 常時オーケストレーション**：Cortex が有効な場合、Step 0.5 は Start Session と direct-handle 候補を含むすべてのユーザーメッセージで試行されます。必要な index が欠けている場合は `tools/migrate.py` auto-bootstrap を実行し、静かに skip せず `degradation_summary` で degrade します。
- **ROUTER paste compression**：v1.7.1 のサブエージェント全文重複貼り付けを、compressed paste wrappers + R11 audit-trail links に置き換えました。ROUTER は `tools/context_compressor.py` の semantics を使い、実質的な主張、決定、blocker、副作用、証拠を保持します。
- **手動 `/compress` trigger**：ROUTER は `/compress [focus]` をユーザー起点の context compression として扱い、`tools/manual_compression_feedback.py` の semantics に従って message count、概算 token、no-op notice を返します。

### 修正

- **Version check prefetch**：retrospective Mode 0 は ROUTER が pre-fetch した Step 8 marker を消費し、local / remote version details を Platform + Version Check にコピーし、remote check を `lifeos-version-check.sh --force` で実行します。これにより stale cache や subagent re-run の挙動が release drift を隠せなくなりました。

### 移行

second-brain データ移行は不要です。任意で、ローカル予定ジョブには `bash scripts/setup-cron.sh install` を実行し、MCP stdio server を使う場合にのみ `mcp` をインストールしてください。

---

## [1.7.1] - 2026-04-25 - バージョン、i18n、hard-rule 索引

> 透明性、オーケストレーション証拠、hook 信頼性、i18n ドリフト制御、コンプライアンス索引にまたがる 27 件の強化をまとめたパッチです。

### 追加

- **Token 透明性**：briefing とオーケストレーションメモで、token に関わる実行、スキップ、エスカレーション理由を明示し、一般的な要約で隠さないようにしました。
- **Hard-rule 索引**：`references/hard-rules-index.md` に現在の権威ある HARD RULE ソースと host ごとの marker 数を記録し、README の古い固定数を外しました。
- **Pre-commit i18n ドリフトガード**：`.git/hooks/pre-commit` が `bash scripts/lifeos-compliance-check.sh i18n-sync` を実行し、ローカル commit 前に翻訳ドリフトを止めます。
- **v1.7.1 リリースノート**：英語、中国語、日本語の README / CHANGELOG で Added / Fixed / Migration の内容を揃えました。

### 修正

- **ROUTER 出力の忠実性**：ROUTER はサブエージェント報告をそのまま貼り付け、圧縮や無言の要約をせず、triage reasoning を下流エージェントから隔離します。
- **AUDITOR 証拠経路**：AUDITOR は同じ LLM 判断に頼らず、プログラム的チェック、Bash stdout 証拠、source-count marker、version/path 検証、briefing-completeness 分類を優先します。
- **Hook 信頼性**：hook activity の可視性、hook health check、stop-hook 動作、marker disambiguation を強化し、欠落や曖昧な backstop を見つけやすくしました。
- **Cortex と DREAM 表示**：Cortex context emit、明示的な GWT arbitration、frame markdown resolution、DREAM full-output display の契約を明確化しました。
- **Git 安全性と force push 対応**：force push 状況は通常化せずエスカレーションし、リリース文書も危険な復旧手順を示唆しないようにしました。
- **i18n audit cleanup**：ローカライズ済み README / CHANGELOG を揃え、明らかな混在言語のリリースノート漏れを減らしました。

**R9 修正(根本原因):**
- stop-session-verify.sh ADJOURN_RE: 全文 grep から末尾 50 行のみに変更。dev session で archiver/adjourn 仕様を議論する際の false-positive を解消(旧版は transcript 任意位置の "adjourn"/"退朝"/"dismiss" 字面にマッチ)。v1.7.2 への持ち越しを廃止 — v1.7.1 内で修正完了。

**R10 アーキテクチャ転換（「5 項目 skip」問題を本当に閉じる）:**
- retrospective Mode 0：18 個のステップのうち 11 個を、scripts/retrospective-mode-0.sh 経由で ROUTER が事前取得するようにしました（Bash literal stdout のため、LLM はスキップできません）。ステップ 2/3/4/5/8/10/11/12/13/14/17 は決定的です。LLM が扱うのはステップ 1/6/9/16/18（判断が必要なもの）のみです。
- 新しい違反クラス C-step-skipped（P0）：briefing 内で 11 個の [STEP N · ...] marker のいずれかが欠落している場合。
- LLM compliance ceiling への構造的回答 — spec ルールでは LLM の振る舞いを強制できません。プログラム的な Bash 出力はスキップできません。

**R11 Audit Trail ファイルチャネル:**
- すべての subagent が実行時監査トレイルを `_meta/runtime/<session_id>/<subagent>-<step>.json` に書き出します。AUDITOR は ROUTER の LLM 貼り付け channel 2 を信頼するのではなく、channel 1 でこれらのファイルをプログラム的に読みます。
- 新しい違反クラスを 3 つ追加しました：`C-no-audit-trail`、`C-trail-incomplete`、`B-trail-mismatch`。
- 新しい補助スクリプトと仕様：`scripts/lib/audit-trail.sh`、`scripts/archiver-phase-prefetch.sh`、`references/audit-trail-spec.md`。Step 10a Notion sync はユーザー確認なしで自動実行されます。

**R12 fresh invocation contract:**
- すべての `上朝` / `退朝` トリガーは毎回フル実行が必要です。LLM は前回の briefing や adjourn report を再利用できません。
- `retrospective-mode-0.sh` は既存の `index_rebuild_state` データを検出した場合 `rebuild=force` と扱い、キャッシュ済み index 状態による Start Session rebuild のスキップを許しません。
- 新しい P0 違反クラス `C-fresh-skip` を追加しました。禁止フレーズ、length collapse、fresh marker 欠落は fresh-invocation scenario で検出します。
- Runtime audit trail JSON に `fresh_invocation:true` と `trigger_count_in_session` を追加します。

### 移行

1. `.git/hooks/pre-commit` を導入または保持し、ローカル commit 前に `i18n-sync` を実行してください。
2. リリース文書を編集した後は `bash scripts/lifeos-compliance-check.sh i18n-sync` を実行してください。
3. 現在の HARD RULE 数は `references/hard-rules-index.md` を参照してください。second-brain データ移行は不要です。

---

## [1.7.0.1] - 2026-04-25 · Briefing Contract + Hook Self-check + Cortex Config

> v1.7 GA contract を締め直すパッチリリースです。最終 briefing は固定の必須セクションを持ち、Mode 0 の前に hook インストール状態を自己チェックし、Cortex の有効化は `_meta/config.md` による opt-in に統一されます。

### 修正

- **lifeos-version-check.sh キャッシュ鮮度** — `--force` フラグとリモート SHA ベースのキャッシュ失効を追加。同日内のリモート新リリースでキャッシュがスタックしなくなった。
- **Briefing 完全性を検証可能に** — Start Session と Adjourn の出力は固定見出しと具体値を出す必要があり、欠落や placeholder は `C-brief-incomplete` として記録されます。
- **RETROSPECTIVE が hooks の存在を仮定しないよう修正** — Mode 0 は pre-session hook health check を実行し、Claude Code hook backstop が未導入または不完全な場合は正確な `setup-hooks.sh` 復旧コマンドを表示します。
- **Cortex config パスを統一** — R1 で誤って導入したパス分裂を撤回 — Cortex 設定は v1.7.0 既発リリースのまま `_meta/config.md` に統一、`cortex_enabled: false` をデフォルトの opt-in として維持。
- **Cortex のデフォルトを明確化** — config 不在時は `cortex_enabled: false` に degrade し、ユーザーが明示的に有効化するまで Cortex は OFF / opt-in です。
- **AUDITOR Mode 3 のプログラム検査** — AUDITOR は LLM 推論ではなく Bash（`lifeos-compliance-check.sh` + `grep`）を呼び出すようになり、2026-04-25 testbed-machine の「private repo」ケースを通してしまった同一ソース由来のコンファビュレーションを排除しました。

### 追加

- **反コンファビュレーション強化** — Step 8 が Bash literal stdout の貼り付けを強制、ROUTER が ground truth を事前取得、AUDITOR Mode 3 が虚構フレーズ blacklist + ツール呼び出し evidence を走査、B-fabricate-toolcall 違反サブクラス追加。2026-04-25 「private repo」虚構ケース解消。
- **Briefing Completeness Contract** — RETROSPECTIVE と ARCHIVER の最終レポートが、固定位置の必須セクションと最小 evidence fields を定義しました。
- **Briefing 欠落の compliance taxonomy** — `C-brief-incomplete` は missing headings、session/source metadata、escalation behavior を base Class C とは別に記録します。
- **`briefing-completeness` compliance check** — `scripts/lifeos-compliance-check.sh` が regression run で retrospective / archiver briefing headings を検証できるようになりました。
- **レイヤー 1 フックの自動インストール** — retrospective Step 0 + archiver Phase 0 + ROUTER トリガー検出がフック欠如を検知すると自動で `setup-hooks.sh` を実行。`git pull` 後の手動インストール不要。
- **PRIMARY-SOURCE PRECOMPUTE briefing マーカー** — wiki/sessions/concepts の実測カウントは `[Wiki count: measured X · index Y · drift Δ=Z]` 形式で briefing に必ず表示されるようになりました。欠落 → `C-brief-incomplete`；|Δ|≥3 かつ `⚠️ DRIFT` なし → `B-source-drift`。
- **STATUS.md の古さ検出** — retrospective Step 0.5 が STATUS last-updated と git HEAD の経過日数を確認し、≥7 日なら briefing の STATUS narrative を抑制します。新しい `B-source-stale` クラスを追加。
- **30d-≥3 Compliance Watch 自動バナー** — retrospective が `violations.md` を読み、しきい値を超えた場合は briefing 1 行目に `🚨 Compliance Watch: <class> (X/30d)` を自動付与します。欠落 → `C-banner-missing`。
- **ROUTER による subagent 出力のファクトチェック** — `SKILL.md` は ROUTER に、ユーザーへ表示する前に Bash を呼び出して briefing 内の数値・バージョン・パス主張を検証することを義務付けます。subagent self-check + AUDITOR Mode 3 に続く第三の防御層です。

### v1.7.0 からの移行

1. Cortex を暗黙に有効化していた可能性のある second-brain を確認し、Cortex を動かす場所だけ `_meta/config.md` で有効化します。
2. opt-in する workspaces では `_meta/config.md` に `cortex_enabled: true` を追加し、それ以外は field なし、または `false` のままにします。
3. Mode 0 が hook health warning を出した場合は、`bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` で Claude Code hooks を再インストールします。
4. Start Session / Adjourn eval baselines に固定 briefing headings を追加し、`briefing-completeness` を実行します。

---

## [1.7.0] - 2026-04-22 · Cortex 認知層 · 正式リリース

> Cortex が alpha から卒業し GA 正式リリース。`v1.7.0-alpha.2` 後の 65 commits で残存 TBD をクローズ:5 つの shell hook のランタイム強制 + 共通 `_lib.sh`、`life-os-tool` CLI に統合された 10 個の Python ツール、3 個の共有 Python ライブラリ、`docs/` 公開ドキュメント群、三言語の認知レイヤー文書、CLAUDE / GEMINI / AGENTS 3 ホストに同期した Step 0.5 / Step 7.5 契約、そして既存の v1.6.2a second-brain をすべて保護する移行パス。

### ✨ ハイライト

- **Cortex プリルーター認知層 GA** — alpha オプトイン終了;完全契約 + 決定論的劣化
- **5 つの shell hook がランタイム強制** — pre-prompt-guard / pre-write-scan / pre-read-allowlist / post-response-verify / stop-session-verify、共通 `_lib.sh`
- **10 個の Python ツールを `life-os-tool` に統合** — reindex / reconcile / stats / research / daily-briefing / backup / migrate / search / export / seed(+ embed プレースホルダー + sync-notion)
- **3 個の Python ライブラリ** — `tools/lib/{config, llm, notion}` がすべてのツールの共通基盤
- **三言語ユーザーガイド出荷** — 6 つの新 Cortex ガイド (EN) + cortex-spec / hippocampus-spec の中日翻訳
- **ホスト非依存オーケストレーション契約** — Step 0.5 (プリルーター認知) + Step 7.5 (Narrator 検証) が CLAUDE.md / GEMINI.md / AGENTS.md (root + `pro/`) で規範化
- **Life OS agents を Claude Code ネイティブ subagents として登録** — install 時に 22 個の `pro/agents/*.md` 定義から Task-spawnable な 21 個の `~/.claude/agents/lifeos-*.md` wrapper を生成し、ROUTER-internal の narrator template は除外するため、`Task(lifeos-retrospective)` が `general-purpose` に fallback しなくなる

### 機能

- **Cortex サブエージェント (プリルーター認知層)** — hippocampus 3 波セッション検索 · GWT top-5 信号 salience 調停 · コンセプトグラフマッチ + シナプス探索 · SOUL 次元競合チェック · Narrator 引用ラップ · Narrator-Validator 監査 (Sonnet 層)
- **Shell hooks (5 つの強制ポイント + 共通ライブラリ)**
  - `pre-prompt-guard.sh` — UserPromptSubmit タイミングでの Class B/C ポリシー + Cortex 有効化ゲート
  - `pre-write-scan.sh` — `second-brain/wiki/**` など保護対象への注入をブロック
  - `pre-read-allowlist.sh` — SSH/シークレット denylist + cwd allowlist
  - `post-response-verify.sh` — `[COGNITIVE CONTEXT]` 区切り + adjourn チェックリスト検証
  - `stop-session-verify.sh` — セッション終了時のコンプライアンスセーフティネット (Adjourn Phase 4 在位、narrator 引用規律)
  - `scripts/hooks/_lib.sh` — 5 hook で共用するヘルパー (パス解決、JSON 読み取り、ログ)
- **Python ツール (10 出荷 + 1 プレースホルダー + 1 Notion sync = `life-os-tool` 配下 12)**
  - `reindex` — session INDEX + concept INDEX + SYNAPSES を一括再構築
  - `reconcile` — SOUL / Wiki / Strategic-Map と session summaries のドリフト検出
  - `stats` — 違反エスカレーションラダー + `--period / --since / --output` 分析
  - `research` — deep-research スキャフォールド (Exa で web/code/company)
  - `daily_briefing` — INDEX / STATUS / SOUL top-5 から朝ブリーフィング生成
  - `backup` — 30d アーカイブ / 90d 削除ローテーション + 違反ログ四半期アーカイブ
  - `migrate` — v1.6.2a → v1.7 マイグレーションランナー (3 ヶ月 backfill ウィンドウ)
  - `search` — 部分文字列 + コンセプト slug の second-brain 横断検索
  - `export` — second-brain を可搬バンドルにシリアライズ
  - `seed` — ユーザーテンプレートから空の second-brain をブートストラップ
  - `embed` — プレースホルダー (明示的 no-op、v1.7 決定「ベクタ DB 不採用」に準拠)
  - `sync_notion` — Notion 双方向ミラー (`tools/lib/notion.py` 経由)
- **Python ライブラリ** — `tools/lib/config.py` (env + pyproject 解決) · `tools/lib/llm.py` (リトライ + トークン会計付き LLM 呼び出しラッパー) · `tools/lib/notion.py` (Notion API クライアント)
- **オーケストレーション** — Step 0.5 (プリルーター認知層) と Step 7.5 (Narrator 検証) を CLAUDE.md、GEMINI.md、AGENTS.md (root + `pro/` の両階層) に同期;契約はホスト非依存に
- **ブートストラップツール** — `tools/seed_concepts.py` + second-brain ブートストラップ用のユーザー向け 3 テンプレート;11 テスト

### ドキュメント

- **6 つの新 Cortex ユーザーガイド** を `docs/user-guide/cortex/` に配置
  - `overview.md` — 「Cortex とは」入口
  - `hippocampus-recall.md` — 3 波セッション検索の仕組み
  - `concept-graph-and-methods.md` — コンセプトノード昇格 + メソッドライブラリ信号
  - `narrator-citations.md` — `[S:][D:][SOUL:]` 引用の読み方と trace 方法
  - `gwt-arbitration.md` — salience 公式と信号が top-5 に選ばれる理由
  - `auditor-eval-history.md` — eval-history セルフフィードバックループ
- `docs/guides/v1.7-migration.md` — 「アップグレード後の最初の 1 週間:日常体験対照」節を追加
- `devdocs/architecture/cortex-integration.md` — **deprecated** としてマーク、spec freeze と整合 (真理源は `references/cortex-spec.md`)
- `docs/architecture/system-overview.md` — `_meta/` シャードパス + Step 0.5 / Step 7.5 オーケストレーション図を更新
- `docs/getting-started/what-is-life-os.md` — Cortex を Second Brain と Decision Engine に並ぶ第三の柱として明示
- `MIGRATION.md` — 開発機切り替えハンドオフガイド (dash 始まりパスの tar 構文 bug を修正)

### i18n

- `i18n/{zh,ja}/references/{concept,cortex,eval-history,gwt,hippocampus,hooks,method-library,narrator,session-index,snapshot,tools}-spec.md` — 凍結済み v1.7 仕様 11 本の中日訳
- `i18n/{zh,ja}/docs/getting-started/what-is-life-os.md` + `i18n/{zh,ja}/docs/user-guide/cortex/*.md` — ローカライズ済み導入ページ + 6 本の Cortex ユーザーガイド
- `README.md` + `i18n/{zh,ja}/README.md` — 3 言語でテーマ順、言語スイッチャー、意思決定サンプル表現を整合

### インフラストラクチャ

- **CI** — pytest テストスイートが **184 → 400 (+216)**;ruff 警告 **50+ → 0**;bash 構文チェック **11/11** パス
- **Makefile** — 開発コマンド (test / lint / format / build-docs) を統合
- `UV_LINK_MODE=copy` を `~/.bashrc` に書き込み、`uv sync` 時の Dropbox ハードリンク競合を解消
- `.github/workflows/test.yml` pytest マトリクスを 10 個の新ツールモジュール + 3 個の新ライブラリモジュールまで拡張
- `evals/scenarios/hook-compliance/` に 8 個の新 hook コンプライアンスシナリオ (01-start-compliant-launch 〜 08-arbitrary-prompt-silent)

### 破壊的変更 / 移行

- **v1.6.2a → v1.7.0** のユーザーは `uv run life-os-tool migrate` を実行する必要がある — マイグレーションツールは直近 3 ヶ月の journal / snapshot データを新しい `_meta/cortex/` シャードレイアウトに backfill する
- v1.7.0 では Cortex が **新規インストールでデフォルト有効** (v1.7.0-alpha のオプトイン既定から反転);既存 second-brain は `cortex_enabled` 設定をそのまま継承
- 完全な移行手順:`docs/guides/v1.7-migration.md`

### コンプライアンス

- Cortex GA 運用中に **2 件の事案ドシエ** を記録
  - `backup/pro/compliance/2026-04-19-court-start-violation.md` — アーカイブ済 (解決済、学びを L1/L2 hook に吸収)
  - Narrator-spec 違反 — **2026-04-22 解決済み** (Step 7.5 narrator-validator 契約へ反映)

### 変更ファイル (抜粋,alpha.2 以降の commits)

```
65b0d57 docs(i18n): publish zh/ja v1.7 specs and Cortex guide translations
170ca07 docs: publish v1.7 public docs trees (exclude plugin-system drafts)
8e47d61 docs(release): path docs/→devdocs/ in 8 specs + CHANGELOG SHA rewrite + tri-lingual sync
91b7896 chore(tests): remove unused pytest import in seed_concepts cleanup
fdf8748 chore(cli/tests): wire 10 v1.7 tools, fix Windows encoding, and track compliance dossiers
1b41f85 feat(tools): add seed.py + tests
9159e38 feat(tools): add migrate.py + tests
f2d5a1d feat(tools): add research.py + tests
b33f7dd feat(tools): extend stats.py aggregates and add sync_notion.py
7240446 feat(tools): add daily_briefing.py + tests
d2d43d8 feat(tools): add export.py + tests
b7e7335 feat(tools): add reconcile.py + tests
f8a26c6 feat(tools): embed.py placeholder + search.py (S5+S4 parallel-sprint merge)
032bdc7 feat(tools): add reindex.py + tests
2b7226f test(hooks): add 8 hook-compliance eval scenarios
0e5128b chore(hooks): extend setup-hooks.sh for v1.7 all 5 hooks
63e923e feat(hooks): add pre-read-allowlist.sh
5ff0d32 feat(hooks+lib): stop-session-verify.sh + Notion lib + pyproject (S1+S2 parallel-sprint merge)
4a2590f docs(orchestration): update root AGENTS.md with host-agnostic Step 0.5/7.5 contract
4ae2a65 feat(hooks): add pre-write-scan.sh
bf7f87e docs(orchestration): sync Step 0.5/7.5 to pro/AGENTS.md
877c629 feat(lib): add tools/lib/llm.py + tests
efa339d feat(lib): add tools/lib/config.py + tests
1414677 feat(hooks): add post-response-verify.sh
7c1fd3a docs(orchestration): sync Step 0.5/7.5 to GEMINI.md
a503301 feat(hooks): add pre-prompt-guard.sh
```

(このほか `tools/seed_concepts.py` + テンプレート、`MIGRATION.md`、`Makefile`、後続の spec/docs 公開コミット、三言語 CHANGELOG 3 件の同期。)

---

## [1.7.0-alpha.2] - 2026-04-21 · v1.7.0-alpha 後続フォローアップバンドル

> 📚 **包括的概要**: [`references/v1.7-shipping-report-2026-04-21.md`](../../references/v1.7-shipping-report-2026-04-21.md) を参照 — v1.6.3 COURT-START-001 修正と v1.7 Cortex の両ラインをカバーする単一ページのナラティブ。「今日何が出荷されたか？」の出発点として推奨。

> v1.7.0-alpha タグ後の 13 commits — alpha CHANGELOG の TBD クローズ + ツール/テストインフラ追加。v1.7.0 安定版にロール予定。

### 🔧 新ツール

- `tools/cli.py` — 統合サブコマンドディスパッチャ；`pyproject.toml` で `life-os-tool` コンソールスクリプト有効化
- `tools/backup.py` — スナップショットローテーション (30d アーカイブ、90d 削除) + violations ログ四半期アーカイブ
- `scripts/lifeos-compliance-check.sh` — `check_adjourn()` + `check_cortex()` 実装 (alpha プレースホルダーをクローズ)
- `tools/lib/cortex/__init__.py` — 22 個のヘルパーシンボルをパッケージレベルでエクスポート

### 📋 新 eval シナリオ

- `evals/scenarios/adjourn-compliance.md` — Class C/D/E + A3 検出
- `evals/scenarios/cortex-retrieval.md` — CX1-CX7 検出 + 劣化パス

### ✅ テストスイート拡張

- `tests/test_backup.py` — 19 テスト
- `tests/test_cli.py` — 8 テスト
- `tests/test_compliance_check.py` — 11 subprocess ベーステスト
- `tests/test_integration.py` — 7 エンドツーエンド統合テスト

**総テスト数：122、すべて 0.68s で合格。**

### 🚀 CI

- `.github/workflows/test.yml` — pytest マトリクス + bash 構文 + スモークテスト

### 📚 アーキテクチャドキュメント

- `references/cortex-architecture.md` — エンドツーエンドデータフロー + 情報隔離マトリクス + 失敗カスケード + コストプロファイル + 合規マップ

### 🔌 配線磨き

- `pro/CLAUDE.md` Information Isolation テーブルを v1.7 サブエージェント 6 つすべてに拡張
- `pro/agents/archiver.md` に "Phase 2 Mid-Step — SOUL Snapshot" を追加

### 🐛 バグ修正

- `tools/cli.py` `_print_usage(stream=sys.stdout)` デフォルト値評価タイミング bug
- `scripts/lifeos-compliance-check.sh` `set -e` + `grep -c` サイレント終了 bug
- 正規表現 `\s` (GNU 限定) → POSIX `[[:space:]]` 移植性

### 変更ファイル (alpha 以降の commits)

```
b1bf474 feat: tools/cli.py dispatcher + check_cortex() + pyproject scripts entry
4fa8db9 feat: check_adjourn() implementation + cortex-retrieval eval scenario
81c96ec feat: v1.7.0-alpha follow-up — backup.py + adjourn eval + CI workflow
2fecaa9 test: end-to-end integration tests for Cortex pipeline (7 tests)
72c942c feat: tools.lib.cortex package exports + Info Isolation table + archiver snapshot step
eb477a5 feat: tests/test_cli + test_compliance_check + cortex-architecture doc
```

（加えて 1ce61d1 v1.7.0-alpha リリース commit そのもの。）

---

## [1.7.0-alpha] - 2026-04-21 · Cortex プリルーター認知層

> Life OS 史上初の Layer 2 アーキテクチャアップグレード。クロスセッション記憶・コンセプトグラフ・アイデンティティ信号をあらゆる意思決定ワークフローへの入力として追加。本日 19 commits で v1.7 を仕様ドラフトから機能完成まで推進。

### 🧠 プリルーター認知層 (オーケストレーター Step 0.5)

`_meta/config.md` で `cortex_enabled: true` を設定すると、すべての非 Start-Session ユーザーメッセージは ROUTER トリアージ**前**に 4 つの並列サブエージェントを通過：

```
user message
    ↓
Step 0.5 (プリルーター認知層)
    ├─ hippocampus       → 3 波セッション検索 (5-7 セッション)
    ├─ concept-lookup    → コンセプトグラフマッチ (5-10 コンセプト)
    └─ soul-check        → SOUL 次元信号 (top 5)
         ↓
    gwt-arbitrator        → salience 式で top-5 信号選定
         ↓
[COGNITIVE CONTEXT] ブロックを user message に前置
    ↓
Step 1 (注釈付き入力で ROUTER トリアージ)
```

REVIEWER 最終審査後、オプションの `narrator` が Summary Report の実質的主張を `[source:signal_id]` 引用で包装。`narrator-validator` (Sonnet 層) が引用規律を監査。

### 📋 6 つの新サブエージェント (~900 行の markdown 契約)

| エージェント | ファイル | spec |
|-------------|---------|------|
| hippocampus | `pro/agents/hippocampus.md` | `references/hippocampus-spec.md` |
| concept-lookup | `pro/agents/concept-lookup.md` | `references/concept-spec.md` |
| soul-check | `pro/agents/soul-check.md` | soul-spec + gwt-spec §6 から派生 |
| gwt-arbitrator | `pro/agents/gwt-arbitrator.md` | `references/gwt-spec.md` |
| narrator | `pro/agents/narrator.md` | `references/narrator-spec.md` |
| narrator-validator | `pro/agents/narrator-validator.md` | narrator-spec validator セクション |

6 エージェントすべて情報隔離を強制：同層 Pre-Router エージェントの出力を拒否。すべて読み取り専用 — 変更は archiver Phase 2 でのみ発生。

### 🐍 Python ツール (~1500 行 · pure stdlib + pyyaml)

| モジュール | 用途 |
|-----------|------|
| `tools/lib/second_brain.py` | 11 second-brain 型のデータクラス + frontmatter parser/dumper + パス解決 |
| `tools/lib/cortex/session_index.py` | SessionSummary IO + INDEX.md コンパイル (冪等) |
| `tools/lib/cortex/concept.py` | Concept IO + INDEX/SYNAPSES コンパイル + Hebbian 更新 |
| `tools/lib/cortex/snapshot.py` | SoulSnapshot IO + アーカイブポリシー (30d/90d) |
| `tools/stats.py` | コンプライアンス違反エスカレーションラダー実行 |

### 🔧 4 CLI ツール

```bash
uv run tools/rebuild_session_index.py [--root PATH] [--dry-run]
uv run tools/rebuild_concept_index.py [--root PATH] [--dry-run] [--no-synapses]
uv run tools/stats.py [--violations PATH] [--json]
bash scripts/setup-hooks.sh   # SessionStart + UserPromptSubmit hooks を自動登録
```

### ✅ 77 pytest テスト — すべて 0.23 秒で合格

| ファイル | テスト数 |
|---------|---------|
| `tests/test_second_brain.py` | 15 (frontmatter / データクラス / パス) |
| `tests/test_session_index.py` | 16 (truncate / write / compile / rebuild / 冪等) |
| `tests/test_concept_and_snapshot.py` | 18 (concept IO / INDEX / SYNAPSES / Hebbian / スナップショットポリシー) |
| `tests/test_stats.py` | 18 (parse / エスカレーション / 閾値 / パス解決) |

```bash
python3 -m pytest tests/ -v        # 77 passed in 0.23s
```

### 🚦 デフォルト OFF (オプトイン)

Cortex は v1.7.0-alpha でデフォルト無効。ユーザーは：

```bash
echo "cortex_enabled: true" >> _meta/config.md
```

second-brain に ≥30 セッションが蓄積されてから有効化推奨。コスト：~$0.05-0.25/turn (Pre-Router サブエージェント全体での Opus トークン)。

### 📊 Cortex 合規分類 (AUDITOR Mode 3 に追加)

| コード | 名称 | 重大度 |
|-------|------|------|
| CX1 | Skip Pre-Router subagents | P1 |
| CX2 | Skip GWT arbitrator | P1 |
| CX3 | Missing [COGNITIVE CONTEXT] delimiters | P1 |
| CX4 | Hippocampus session cap exceeded | P1 |
| CX5 | GWT signal cap exceeded | P1 |
| CX6 | Cortex isolation breach | P0 |
| CX7 | Cortex write breach | P0 |

`cortex_enabled: false` の時 CX チェックすべてスキップ。

### 📁 変更ファイル (19 commits)

Specs: `references/{cortex,hippocampus,gwt,concept,snapshot,session-index,narrator,hooks,tools,eval-history,method-library}-spec.md` + 既存 references 8 件修正。
サブエージェント: `pro/agents/{hippocampus,gwt-arbitrator,concept-lookup,soul-check,narrator,narrator-validator}.md`。
配線: `pro/CLAUDE.md`、`pro/agents/{archiver,retrospective,auditor}.md`。
ツール: `tools/lib/{second_brain.py,cortex/*}`、`tools/{stats,rebuild_session_index,rebuild_concept_index}.py`。
プロジェクト: `pyproject.toml`、`.python-version`、`tools/README.md`。
テスト: `tests/{__init__,test_second_brain,test_session_index,test_concept_and_snapshot,test_stats}.py`。
Hooks: `scripts/lifeos-compliance-check.sh` (v1.6.3 チェーンの L5 クロージャ)。
ドキュメント: README 3 言語 + CHANGELOG 3 言語 (本 commit)。

### 🚧 既知の制限 / 未対応

- **本番検証保留** — alpha は pytest + 仕様準拠でテスト済だが、実際の user second-brain での大規模実戦未実施
- **`concept-lookup` はエッジトラバーサルしない** — Wave 1 のみ；Wave 2/3 は hippocampus の領域
- **Narrator validator** Phase 2 はセルフチェックループ；スタンドアロン validator サブエージェントは Phase 2.5 で
- **`tools/backup.py`** スナップショットアーカイブローテーション：v1.7.0 安定版に延期
- **adjourn-compliance eval シナリオ** はまだプレースホルダー

### 移行

既存ユーザー (v1.6.3b → v1.7.0-alpha)：
1. skill 再インストール：`/install-skill https://github.com/jasonhnd/life_OS`
2. hooks セットアップ再実行：`bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`
3. (オプション) Python ツールインストール：`cd ~/.claude/skills/life_OS && uv sync`
4. (オプション) Cortex 有効化：`echo "cortex_enabled: true" >> {your-second-brain}/_meta/config.md`

デフォルト OFF は既存ユーザーがオプトインしない限り動作変化ゼロを意味する。v1.6.3 5 層コンプライアンス防御は引き続き有効・変更なし。

---

## [1.6.3b] - 2026-04-21 · AUDITOR Mode 3 自動トリガー結線完了

> v1.6.3 は Mode 3（Compliance Patrol）仕様を `pro/agents/auditor.md` に出荷したが、**実際には誰も呼び出していなかった**。ユーザー second-brain での初稼働がギャップを確認：retrospective Mode 0 完了・ブリーフィング表示後に AUDITOR Compliance Patrol レポートが現れず。5 層防御の Layer 4 が不活性状態。

### 🔧 修正

`pro/CLAUDE.md` Orchestration Code of Conduct にルール #7 を追加：

> **AUDITOR Compliance Patrol 自動トリガー** — 各 `retrospective` Mode 0（Start Session）完了後または `archiver` 戻り後、オーケストレーターは `auditor` を Mode 3（Compliance Patrol）で起動しなければならない。スキップ不可。HARD RULE。

契約を明示化する 3 つの補助ドキュメント更新：

- `pro/agents/retrospective.md` — "Auto-Follow: AUDITOR Compliance Patrol" セクション追加。オーケストレーターが Mode 0 戻り後に Mode 3 を連結することを記述。サブエージェント自身は AUDITOR を起動しない。
- `pro/agents/auditor.md` — Mode 3 "When to run" セクションに明示的トリガー契約を追加：オーケストレーター起動、自己起動ではない、`pro/CLAUDE.md` ルール #7 へのクロスリファレンス。
- `SKILL.md` — バージョン 1.6.3a → 1.6.3b。

### 📊 5 層防御ステータス（v1.6.3b 以降）

| Layer | ステータス |
|-------|----------|
| L1 · UserPromptSubmit hook | ✅ v1.6.3 出荷 · setup-hooks.sh で自動インストール（v1.6.3a）|
| L2 · Pre-flight Compliance Check | ✅ 出荷 + 2026-04-21 本番検証 |
| L3 · Subagent Self-Check | ✅ 出荷 + 2026-04-21 本番検証 |
| L4 · AUDITOR Compliance Patrol（Mode 3）| ✅ 仕様出荷（v1.6.3）· **トリガー結線完了（v1.6.3b）** |
| L5 · Eval 回帰 | ✅ シナリオ出荷（v1.6.3）· auto-runner 拡張は v1.7 へ延期 |

### 修正ファイル

- `SKILL.md`（バージョン 1.6.3a → 1.6.3b）
- `pro/CLAUDE.md`（+ Orchestration ルール #7）
- `pro/agents/retrospective.md`（+ Auto-Follow セクション）
- `pro/agents/auditor.md`（Mode 3 "When to run" トリガー契約明確化）
- `README.md` + 三言語（バッジ）
- `CHANGELOG.md` + 三言語

### 移行

ユーザー操作不要。既存の v1.6.3a インストールは次セッションでルール #7 を自動的に取り込む。今後すべての Start Session と Adjourn の終わりに AUDITOR Compliance Patrol レポートが出力される。違反なし時の出力形式：

```
🔱 [theme: auditor] · Compliance Patrol (v1.6.3)
✅ All 6 Start Session compliance checks passed
No violations logged. Session adheres to v1.6.3 HARD RULES.
```

---

## [1.6.3a] - 2026-04-21 · v1.6.3 ホットパッチ · Layer 1 インストールギャップ + Hook 偽陽性ガード

> v1.6.3 の本番初稼働（同日、ユーザー second-brain 内）で Layer 2-5 が end-to-end に動作することを検証。同時に 2 つの実 gap が顕在化：
> 1. **Layer 1（UserPromptSubmit hook）は自動登録されていない** — `/install-skill` はファイルをコピーするが `~/.claude/settings.json` を変更しない。デフォルトインストールでは L1 防御が出荷されない。
> 2. **Hook regex がペースト内容で偽発火** — トリガーワードを含む転送ペーストが誤って reminder を発火させた。

### 🔧 修正 1 — Layer 1 インストール自動化

`scripts/setup-hooks.sh` リファクタリング：
- 単一実行で SessionStart hook（バージョンチェック）と UserPromptSubmit hook（Layer 1 防御）を両方インストール
- `register_hook()` ヘルパー関数を追加し、イベントタイプ間で DRY 冪等登録
- 冪等：安全に複数回実行可能；既登録 hook はスキップ
- 後方互換：既存 v1.6.3 インストールに影響なし；再実行で L1 をクリーンに追加

インストール / アップグレード後にユーザーが一度実行：
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```

### 🔧 修正 2 — Hook 偽陽性削減

`scripts/lifeos-pre-prompt-guard.sh` regex マッチング前に 2 つの事前チェックを追加：
- **長さチェック**：prompt 全体 ≤ 500 文字（長い prompt = 会話的 / ペースト、トリガーではない）
- **最初の行チェック**：最初の非空行 ≤ 100 文字（段落形式のイントロを持つペーストブロックを除外）

トリガーワード regex は**最初の行のみ**でマッチング（以前は複数行）。トリガーワードを含む転送ペーストは hook を発火させなくなった。

### 🆕 Class F · 偽陽性

`references/compliance-spec.md` Type Taxonomy と `pro/compliance/violations.md` Type Legend に追加：

| コード | 名称 | デフォルト重大度 |
|-------|------|--------------|
| **F** | False positive | P2（情報的）— hook がペースト / 引用コンテンツで発火、実ユーザートリガーではない。エスカレーションラダーから除外。|

最初の Class F エントリ記録：2026-04-21T13:42 — dev repo で v1.6.3 本番検証転送をペーストして hook 発火。Assistant がペーストコンテキストを正しく識別し retrospective 起動を拒否。修正 2 で緩和済み。

### 📋 COURT-START-001 ステータス更新

`pro/compliance/violations.md` の 4 件の incident エントリに本番検証証拠を追記：
- L2（Pre-flight Compliance Check）— 2026-04-21 ユーザー second-brain で動作検証
- L3（Subagent Self-Check）— 2026-04-21 ユーザー second-brain で動作検証
- L4（AUDITOR Compliance Patrol）+ L5（eval 回帰）— 観察ウィンドウ待ち

`partial → true` 遷移は `references/compliance-spec.md` 通り eval 回帰パス + 30 日無再発ウィンドウ待ち。

### 修正ファイル

- `SKILL.md`（バージョン 1.6.3 → 1.6.3a）
- `scripts/setup-hooks.sh`（リファクタ + register_hook ヘルパー + UserPromptSubmit 登録）
- `scripts/lifeos-pre-prompt-guard.sh`（+ 長さチェック + 最初の行抽出）
- `references/compliance-spec.md`（+ Class F を Type Taxonomy に追加）
- `pro/compliance/violations.md`（+ Class F を legend に、+ 1 件の F エントリ、+ 4 件の COURT-START-001 に L2/L3 検証注釈）
- `pro/compliance/violations.example.md`（+ Example 11 Class F）
- `README.md` + 三言語（バージョンバッジ + v1.6.3a ホットパッチ注記）
- `CHANGELOG.md` + 三言語

### 移行

既存 v1.6.3 インストール：
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
Layer 1 防御を有効化。他の操作不要；L2-5 は変更なし。

新規インストール：同じ 1 行コマンドですべてを一度に有効化。

---

## [1.6.3] - 2026-04-21 · COURT-START-001 修正 · 五層防御

> ユーザーが Life OS 開発 repo で「上朝」と発言した際、ROUTER は retrospective サブエージェントをスキップし、メインコンテキストで 18 ステップを模倣実行し、存在しないパス `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation` を権威ソースとして捏造した。ユーザーの反応：「こんな Life OS を他人にどう渡せと？？？受け入れられない。」本リリースはあらゆる HARD RULE を本当に hard にする五層防御を提供する。

### 🛡️ A / B クラス違反に対する五層防御

COURT-START-001 根本原因：ドキュメントは完全、だが**すべての HARD RULE は記述的——強制メカニズムはゼロ**。作者本人でも LLM に欺かれる；一般ユーザーが欺かれるのは必然。5 つの独立した防御層が各トリガーワードを守る：

1. **Hook レイヤー** — `scripts/lifeos-pre-prompt-guard.sh` が `UserPromptSubmit` で発火、トリガーワード（上朝 / start / 閣議開始 / 退朝 / など、9 テーマすべてをカバー）を検出し、HARD RULE テキスト + 違反分類を `<system-reminder>` としてアシスタントの応答前にコンテキストへ注入。
2. **Pre-flight Compliance Check** — `SKILL.md` が ROUTER にツール呼び出し前の 1 行確認を強制：`🌅 Trigger: [語] → Theme: [名] → Action: Launch([agent]) [Mode]`。欠如 = クラス A3 違反として記録。
3. **サブエージェント自己チェック** — `pro/agents/retrospective.md` Mode 0 の第一文は必須：`✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation). Reading pro/agents/retrospective.md. Starting Step 1: THEME RESOLUTION.`。サブエージェントが実際に起動したことを証明。
4. **AUDITOR Compliance Patrol（Mode 3）** — `pro/agents/auditor.md` に Mode 3 を追加、7 クラス分類（A1/A2/A3/B/C/D/E）と Start Session / Adjourn パスの 6 項目検出。各 retrospective Mode 0 と archiver 完了後に自動実行。
5. **Eval 回帰** — `evals/scenarios/start-session-compliance.md` が COURT-START-001 の 6 つの失敗モードを Quality Checkpoints として固定化、grep ベースの失敗検出コマンド付き。

### 📋 違反分類（7 クラス）

| コード | 名称 | デフォルト重大度 |
|-------|------|--------------|
| A1 | サブエージェントスキップ — ROUTER がメインコンテキストでサブエージェントのステップを模倣 | P0 |
| A2 | ディレクトリチェックスキップ — dev repo が retrospective Step 2 をバイパス | P1 |
| A3 | Pre-flight スキップ — 最初の応答に `🌅 Trigger: ...` 行がない | P1 |
| B | 事実の捏造 — 存在しないパス / セクションを権威として参照 | P0 |
| C | フェーズ未完了 — archiver が 4 フェーズ完走前に終了 | P0 |
| D | プレースホルダー値 — Completion Checklist に `TBD` / `{...}` / 空値 | P1 |
| E | メインコンテキストでのフェーズ実行 — ROUTER がメインコンテキストで Phase 1-4 ロジックを実行 | P0 |

### 📁 デュアルリポ compliance ログ（md + git · ユーザー制約準拠）

ユーザー明示要求：「ローカル sh コマンド実行は受け入れられるが、データベースは md ファイルと GitHub ストレージでなければならない。」違反は以下に永続化：

- `pro/compliance/violations.md` — dev repo（公開、Life OS と共に配布）
- `_meta/compliance/violations.md` — ユーザー second-brain（プライベート、ユーザーごとに独立）

同じフォーマット：`| Timestamp | Trigger | Type | Severity | Details | Resolved |`。

**エスカレーションラダー**（v1.7 の `tools/stats.py` で実装、それまでは開発者が手動観察）：
- 30 日以内に同種 ≥3 件 → hook リマインダーを強化
- 30 日以内に同種 ≥5 件 → retrospective briefing 冒頭に `🚨 Compliance Watch` を追加
- 90 日以内に同種 ≥10 件 → AUDITOR が毎 Start Session で Compliance Patrol 実行

### 🗂️ 新規ファイル

- `scripts/lifeos-pre-prompt-guard.sh` — UserPromptSubmit hook（bash、chmod +x 済）
- `.claude/settings.json` — dev repo 用 hook 登録
- `references/compliance-spec.md` — 完全仕様：分類、デュアルリポ戦略、書き込み / 読み取りパス、エスカレーションラダー、アーカイブ、解決プロトコル、プライバシー
- `pro/compliance/violations.md` — dev-repo ライブログ（COURT-START-001 からの 5 件のシードエントリ付き）
- `pro/compliance/violations.example.md` — クラスごとに 10 件の例 + grep レシピ
- `pro/compliance/2026-04-19-court-start-violation.md` — 完全 incident アーカイブ（473 行、12 セクション）
- `evals/scenarios/start-session-compliance.md` — COURT-START-001 の 6 つの失敗モードの回帰テスト

### ✏️ 修正ファイル

- `.claude/CLAUDE.md` — Start Session トリガー用 HARD RULE セクションを追加
- `SKILL.md` — バージョン 1.6.2a → 1.6.3、Start Session ルーティング前に Pre-flight Compliance Check セクション追加
- `pro/agents/retrospective.md` — 実行ステップ前にサブエージェント自己チェックブロック
- `pro/agents/auditor.md` — Mode 3（Compliance Patrol）、7 クラス分類 + 検出ロジック

### 🔄 解決プロトコル

違反は `false → partial → true` と 3 つのゲートを通過して遷移：
- **Gate 1**（`false → partial`）：根本修正がリリース済（Details フィールドにバージョン明記）
- **Gate 2**（`partial → true`）：eval 回帰パス + 30 日経過 + 非再発（バージョン + eval-id + 観察日を記載）

COURT-START-001 の 4 件の incident エントリは本リリースで `partial` に遷移。`true` への遷移には `evals/scenarios/start-session-compliance.md` パス + 30 日観察ウィンドウが必要。

### 移行

既存インストールにユーザー操作は不要。アップグレード後の初回 Start Session で：
- hook 登録（dev repo のみ、`.claude/settings.json` 経由）
- Pre-flight 行が必須に
- AUDITOR が初回 retrospective Mode 0 後に Compliance Patrol を実行
- violations.md が欠如時は自動作成（空テーブル）

デュアルリポ違反記録を有効にしたい second-brain ユーザーは `references/compliance-spec.md` に従い、自身の `.claude/settings.json` に hook ブロックを追加する。

---

## [1.6.2a] - 2026-04-19 · Notion 同期をオーケストレーターに移管

> archiver subagent が「Notion MCP 未接続」と報告していた。原因は Notion MCP ツールが環境固有であり subagent 内で利用できないため。Notion 同期を archiver から分離し、MCP ツールアクセスを持つオーケストレーター（メインコンテキスト）で実行するように変更。

### 変更

- **archiver.md**：Phase 4 を git のみに縮小。Notion 同期を削除し MCP ツール制限の明記を追加
- **CLAUDE.md**：新規 Step 10a — オーケストレーターが archiver 完了後に Notion 同期を実行
- **GEMINI.md / AGENTS.md**：Step 10a を同期
- **SKILL.md**：退朝テンプレートを更新し、Notion 同期を archiver 後のステップとして追加

---

## [1.6.2] - 2026-04-17 · 退朝防御 + Wiki/SOUL 自動書き込み + DREAM 10 トリガー

> 3つの強化を同時リリース：(1) 退朝フローの部分スキップを不可能に；(2) wiki と SOUL が厳格な基準下で自動書き込み、ユーザー確認を不要に；(3) DREAM に 10 個の具体的な自動トリガーアクションを追加。

### 🛡️ 退朝 3 層防御

以前のバグ：ROUTER が ARCHIVER サブエージェントを起動せず、メインコンテキストで Phase 2（知識抽出）を実行し、4 フェーズのフローを分断することがあった。

3 つの独立した防御：
- **SKILL.md + archiver.md の文言強化** — ROUTER がメインコンテキストで Phase 内容を実行することを HARD RULE で禁止；archiver.md に「Subagent-Only Execution」ブロックを明示
- **退朝ステートマシン（pro/CLAUDE.md）** — 合法/違法な状態遷移を列挙；AUDITOR が違反を user-patterns.md に記録
- **強制起動テンプレート** — SKILL.md に「Trigger Execution Templates (HARD RULE)」セクションを追加し、Start Session / Adjourn / Review の正確な出力形式を固定

### 📚 Wiki 自動書き込み（ユーザー確認なし）

以前：archiver が wiki 候補を列挙してユーザーに選択を求めた。フローを中断し、スキップを助長した。

現在：archiver が **6 つの厳格な基準 + プライバシーフィルター** の下で自動書き込み：
1. プロジェクト横断で再利用可能
2. あなたではなく世界について（価値観 → SOUL、wiki ではない）
3. **個人プライバシーゼロ** — 名前、金額、アカウント ID、特定の会社、家族/友人情報、追跡可能な日付+場所の組み合わせ → 剥ぎ取り；剥ぎ取ると結論が無意味になる場合 → 破棄
4. 事実または方法論
5. 複数の証拠点（≥2 独立）
6. 既存の wiki と矛盾しない（矛盾 → 既存エントリーの `challenges: +1`、競合エントリーは作成しない）

初期信頼度：3+ 証拠 → 0.5；ちょうど 2 → 0.3；1 以下 → 破棄。

ユーザー事後ナッジ：ファイル削除 = 廃止；「最近の wiki を取り消し」で最新の自動書き込みをロールバック；`confidence` を 0.3 未満に手動設定で抑制。

### 🔮 SOUL 自動書き込み + 継続ランタイム

以前：SOUL 次元はユーザー確認でのみ作成；定期的にのみ表示。

現在：
- **ADVISOR が決定ごとに自動更新** — Summary Report 後、既存の SOUL 次元の `evidence_count` または `challenges` をインクリメント；≥2 証拠点の新次元を検出した場合、`confidence: 0.3` で自動書き込み、「What SHOULD BE」フィールドはユーザーが後で記入できるよう故意に空白
- **REVIEWER が SOUL を強制参照** — 各決定で関連する SOUL 次元を引用するか、「直接関連する次元なし、この決定は新次元を開く可能性」を明示
- **SOUL ヘルスレポートをブリーフィング固定位置に** — 各上朝、Pre-Session Preparation の直後の最初のブロックが 🔮 SOUL Health Report（トレンド矢印付き現在プロファイル、新たに自動検出された入力待ち次元、競合警告、30+ 日休眠次元、軌跡デルタ）

信頼度の公式は不変：`confidence = evidence_count / (evidence_count + challenges × 2)`。

### 💤 DREAM 10 個の自動トリガーアクション（REM ステージ）

REM は 10 個の具体的なパターンを評価し、一致すれば自動実行：

| # | パターン | 自動アクション |
|---|---------|--------------|
| 1 | 新しいプロジェクト関係 | STRATEGIC-MAP 候補書き込み + ブリーフィング目立つ位置 |
| 2 | 行動 ≠ driving_force | 次 ADVISOR 入力に注入 |
| 3 | Wiki が新証拠で反駁された | 該当エントリーの `challenges: +1` |
| 4 | SOUL 次元が 30+ 日休眠 | ブリーフィング警告 |
| 5 | プロジェクト横断認識が未使用 | 次 DISPATCHER に強制注入 |
| 6 | 決定疲労を検出 | 「今日は重大な決定をしない」を提案 |
| 7 | driving_force 価値ドリフト | SOUL 修訂を自動提案 |
| 8 | 古いコミットメント（30+ 日行動なし） | ブリーフィングで呼び戻し |
| 9 | 感情的決定パターン | 次 REVIEWER に感情状態チェックを追加 |
| 10 | 同じ決定の繰り返し | ブリーフィングで「コミットメントを避けていませんか？」 |

全フラグは dream journal の `triggered_actions` YAML ブロックに書き込まれる。次の上朝で RETROSPECTIVE が固定の「💤 DREAM Auto-Triggers」ブリーフィングブロックに表示。

### 🔬 設計の詳細化（詳細仕様）

上記 4 本の概念柱に加え、v1.6.2 は詳細な動作仕様も提供：

**DREAM トリガー検出ロジック** —— 10 個のトリガーそれぞれが以下を備えます：
- **ハード閾値**（定量的ルール、自動発火）
- **ソフトシグナル**（LLM 定性的手掛かり、`mode: soft` で発火、AUDITOR レビュー必須）
- 明確なデータソース、24 時間の重複抑制、構造化出力

例：決定疲労 = 「24 時間以内に 5 件以上の決定 かつ 後半平均スコア ≤ 前半 - 2」；価値ドリフト = 「30 日で 3 件以上の挑戦 かつ 新規支持証拠 ≤1 かつ confidence 低下 >30%」；古いコミットメント = 「『X をする』の正規表現一致 + 30 日間対応する完了なし」；感情的決定 = 「ADVISOR の感情フラグ + REVIEWER 冷却助言 + セッション継続」；繰り返し決定 = 「トピックキーワードが過去 30 日の 2 件以上の決定と 70% 以上重複」。全 10 件は `references/dream-spec.md` を参照。

**ADVISOR SOUL Runtime の統合** —— 旧読み取り専用「SOUL 行動監査」セクションを新しい自動更新メカニズムに統合。単一の統合フロー：次元ごとの影響（支持／挑戦／中立）→ evidence/challenge デルタ書き込み → 新次元検出 → 競合警告 → 🔮 SOUL Delta ブロック出力。退朝時だけでなく、すべての決定で実行。

**トレンド矢印のための SOUL スナップショットメカニズム** —— archiver Phase 2 はセッション終了時に `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md` へ最小スナップショットをダンプ（数値メタデータのみ、内容の重複なし）。RETROSPECTIVE は次回上朝時に最新スナップショットを読み、以下を計算：
- `confidence_Δ > +0.05` → ↗
- `confidence_Δ < -0.05` → ↘
- `|confidence_Δ| ≤ 0.05` → →
特殊状態：🌟 コアに昇格、⚠️ コアから降格、💤 休眠、❗ 競合ゾーン。アーカイブ方針：>30 日 → `_archive/`、>90 日 → 削除（git + Notion で保持）。

**REVIEWER SOUL 3 層参照戦略** —— SOUL 次元が多い場合のノイズを防ぐ：
- **Tier 1**（confidence ≥ 0.7）：すべて参照、上限なし — コアアイデンティティは必ず考慮
- **Tier 2**（0.3 ≤ confidence < 0.7）：強／弱マッチ判定により意味的に最も関連する 3 件を選択
- **Tier 3**（confidence < 0.3）：カウントのみ、表に出さない（ADVISOR が Delta で追跡）

決定が Tier 1 次元に挑戦 → REVIEWER が Summary Report の冒頭に ⚠️ SOUL CONFLICT 警告を追加（半否決信号）。評価された各 Tier 2 次元は採否理由を列挙、AUDITOR が品質をレビュー。

### 修正ファイル

- `SKILL.md`（バージョン + トリガーテンプレート）
- `pro/CLAUDE.md`（ステートマシン + wiki/SOUL 自動書き込み記述）
- `pro/GEMINI.md` / `pro/AGENTS.md`（クロスプラットフォーム Gemini CLI + Codex CLI 一致性）
- `pro/agents/archiver.md`（Phase 2 自動書き込み + スナップショットダンプ + Phase 3 10 トリガー検出ロジック）
- `pro/agents/advisor.md`（統合 SOUL Runtime：5 ステップ、決定ごと）
- `pro/agents/reviewer.md`（3 層 SOUL 参照戦略）
- `pro/agents/retrospective.md`（Step 11 を 11.1-11.6 に拡張：スナップショット読み込み + トレンド計算）
- `references/wiki-spec.md` + 三言語（6 基準 + プライバシーフィルター + ユーザーナッジ）
- `references/soul-spec.md` + 三言語（自動書き込み + スナップショットメカニズム + 階層参照）
- `references/dream-spec.md` + 三言語（10 トリガーのサブセクション化、ハード／ソフト検出）
- `references/data-layer.md` + 三言語（`_meta/snapshots/` をディレクトリツリーに追加 + 自動書き込みを反映）
- `README.md` + 三言語（v1.6.2 の新機能 + セクション V 書き直し + アーキテクチャ図）
- `CHANGELOG.md` + 三言語

### 移行

ユーザーの操作は不要。既存の wiki/SOUL エントリーは引き続き動作。新エントリーは次セッションから自動書き込み。アップグレード後の初回上朝は「トレンドデータなし」と表示、2 回目のセッションでスナップショットベースラインを確立するまで。特定の自動書き込みエントリーを削除せずに抑制するには：frontmatter で `confidence: 0.0` に設定。

---

## [1.6.1] - 2026-04-16 · 9テーマ — あらゆる文化、あらゆるスタイル

> テーマシステムが3テーマから9テーマに拡張。各言語で歴史的・現代政府・企業の3つの統治スタイルを選択可能に。

### 新テーマ

**English**（計3テーマ）：
- 🏛️ Roman Republic — Consul、Tribune（veto の発明者）、Senate
- 🇺🇸 US Government — Chief of Staff、Attorney General、Treasury、GAO
- 🏢 Corporate — CEO、General Counsel、CFO（既存、変更なし）

**中文**（計3テーマ）：
- 🏛️ 三省六部 — 丞相、中書省、門下省（既存、変更なし）
- 🇨🇳 中国政府 — 国務院総理、発改委、全人代常務委、審計署
- 🏢 公司部門 — 総経理、戦略企画部、法務コンプライアンス部、内部監査部

**日本語**（計3テーマ）：
- 🏛️ 明治政府 — 内閣総理大臣、参議、枢密院、大蔵省、元老
- 🏛️ 霞が関 — 内閣官房長官、内閣法制局、財務省（既存、変更なし）
- 🏢 企業 — 社長室、経営企画部、法務部、経理部、内部監査室

### テーマ選択 UI の更新

セレクターが言語別にグループ化。トリガーワード推論がよりスマートに：
- 「上朝」→ 三省六部を自動ロード（唐朝固有の語）
- 「閣議開始」→ 霞が関を自動ロード（現代政府固有の語）
- 汎用トリガー（「はじめる」「开始」"start"）→ その言語の3つのサブ選択肢を表示

---

## [1.6.0] - 2026-04-15 · Theme Engine — ひとつのエンジン、すべての文化へ

> ある日本人ユーザーが Life OS を試した。体験は悪かった——ロジックが間違っていたからではなく、「三省六部」が中国の文化的概念であり、非中国語圏のユーザーにとって学習障壁になっていたからだ。v1.6.0 は意思決定エンジンと文化的な表現を分離することでこの問題を解決する。

### 変更の核心

Life OS は**汎用意思決定エンジン**と**交換可能な文化テーマ**の構成になった。ガバナンスロジック（立案 → 審査 → 拒否 → 実行 → 監査）はすべてのテーマで同一——変わるのは名称、語調、比喩だけ。

### 三層アーキテクチャ

**Layer 1: Engine** — 16の agent が機能的 ID を持つ（ROUTER, PLANNER, REVIEWER, DISPATCHER, 6つのドメインアナリスト, AUDITOR, ADVISOR, COUNCIL, RETROSPECTIVE, ARCHIVER, STRATEGIST）。言語中立、文化中立。

**Layer 2: Theme** — 交換可能な文化スキン。機能的 ID を馴染みのある名称にマッピング：
- `zh-classical` — 三省六部（唐朝の統治制度）：丞相、中書省、門下省、六部、御史台……
- `ja-kasumigaseki` — 霞が関（日本の中央省庁）：内閣官房長官、内閣法制局、財務省、会計検査院……
- `en-csuite` — C-Suite（企業エグゼクティブ）：Chief of Staff、General Counsel、CFO、Internal Audit……

**Layer 3: Locale** — ユーザーの言語を自動検出し、マッチするテーマを推奨。いつでも切り替え可能。

### テーマ選択 UI

セッション開始時に、RETROSPECTIVE エージェントがシンプルな選択画面を提示する：
```
🎨 テーマを選んでください：
 a) 🏛️ 三省六部 — 唐朝の統治制度（中国古典）
 b) 🏛️ 霞が関 — 日本の中央省庁
 c) 🏛️ C-Suite — 企業エグゼクティブ構造（英語）

a、b、c のいずれかを入力
```

- **テーマ選択はセッション単位**——異なるターミナルウィンドウで異なるテーマを使用でき、互いに影響しない
- テーマ選択はセッションを超えて保持されない。新しいセッションのたびに再選択する
- セッション中いつでも「テーマ切り替え」と言えば変更できる

### 具体的な変更

- **16の agent ファイルをリネーム**：中国語ピンイン（chengxiang.md, zhongshu.md...）→ 機能的英語（router.md, planner.md...）
- **themes/ ディレクトリを作成**：3つのテーマファイル（各約60行）でロールマッピング、語調、トリガーワード、出力タイトルを定義
- **i18n agent の重複を排除**：48の agent ファイル（16 × 3言語）→ 16ファイル。テーマが表示を担当、agent がロジックを担当
- **約42の翻訳済み agent / オーケストレーションファイルを削除**：不要に——agent ごとに1つの真実の源
- **departments.md → domains.md**：六部 → Six Domains（PEOPLE, FINANCE, GROWTH, EXECUTION, GOVERNANCE, INFRA）
- **すべてのオーケストレーションプロトコルを更新**：CLAUDE.md、AGENTS.md、GEMINI.md が機能的 ID を使用
- **すべてのリファレンスドキュメントを更新**：data-layer、data-model、strategic-map-spec、wiki-spec、soul-spec、dream-spec、scene-configs
- **すべての eval シナリオを更新**：テストケースが機能的 ID を使用（router-triage.md、council-debate.md）

### なぜこれが重要か

- **日本のユーザー**は財務省、法務省、会計検査院を目にする——学習コストゼロ
- **英語のユーザー**は CFO、General Counsel、Internal Audit を目にする——直感的に理解可能
- **中国語のユーザー**は依然として丞相、中書省、門下省を目にする——何も失われない
- **開発者**は48ではなく16の agent ファイルを保守する——ロジック変更は1回で済む
- **新テーマ**は約60行のファイル1つで済む——エンジンの変更は不要

### ゼロ機能損失

28のハードルールすべてが維持。すべてのスコアリング基準は完全。すべての出力フォーマットは維持（テーマ依存の名称付き）。SOUL、DREAM、Wiki、Strategic Map、Completion Checklist、封駁ループ、セッションライフサイクル——すべてが同一に動作。完全な34項目の保存チェックリストに対して検証済み。

---

## [1.5.0] - 2026-04-15 · 戦略マップ — プロジェクトアシスタントからライフストラテジストへ

> Life OS は個々のプロジェクトを見事に分析できたが、プロジェクト間のつながりには盲目だった。多くのアクティブなプロジェクトが依存関係、リソース、隠れた戦略的目的を共有する中、システムには関係レイヤーが必要だった。戦略マップはまさにそれを追加し、SOUL、Wiki、DREAM と深く統合して統一された認知システムを形成する。

### 問題

多くのプロジェクトがある。あるプロジェクトは他に知識を供給し、あるプロジェクトはあなたの限られた時間を共有する。表向きの目的と本当の動機が異なるものもある。1つが停滞すると、気づかないうちに他の3つがブロックされる。しかし朝のブリーフィングにはフラットなリストが表示されるだけ — 関係性なし、優先順位なし、「今日は実際に何をすべきか？」もなし。

### 新機能

**戦略ライン** — 戦略的目的別にプロジェクトをグループ化。各ラインには `purpose`（公式）、`driving_force`（本当の動機）、`health_signals`（監視項目）がある。複数のプロジェクトが異なる役割で1つのラインに貢献：`critical-path`、`enabler`、`accelerator`、`insurance`。

**フローグラフ** — プロジェクト間の流れを定義：`cognition`（知識）、`resource`（成果物）、`decision`（制約）、`trust`（関係資本）。プロジェクト A の決定がプロジェクト B の前提を無効にした場合、システムが警告する。

**ナラティブ・ヘルスアセスメント** — 「6/10 🟡」のスコアリングを廃止。Klein の認識駆動型意思決定モデルに基づき、プロジェクトをヘルスアーキタイプにマッチング（🟢 着実な進捗 / 🟡 制御された待機 / 🟡 勢いの減衰 / 🔴 制御不能な停滞 / 🔴 方向のドリフト / ⚪ 休眠）し、ナラティブを記述：何が起きているか、何を意味するか、何をすべきか。

**朝のブリーフィングのアップグレード** — フラットな「エリアステータス」リストが、戦略ラインでグループ化された戦略概要に変わり、ブラインドスポット検出と実行可能な推奨事項が付属：
- 🥇 最もレバレッジの高いアクション（工数見積もりと不作為のコスト付き）
- 🥈 注目に値する
- 🟢 無視して安全（能動的な認知抑制で認知負荷を軽減）
- ❓ 決定が必要（ユーザーが埋めるべき構造的ギャップ）

**クロスレイヤー統合** — 戦略マップは SOUL、Wiki、DREAM と1つのシステムとして連携：
- SOUL × 戦略：driving_force が表明した価値観と一致しているか確認
- Wiki × フロー：cognition フローが実際に wiki の知識を運んでいるか検証（ペーパーフローの検出）
- DREAM × 戦略：REM ステージがフローグラフをスキャフォールディングとしてクロスレイヤーインサイトを発見
- パターン × 戦略：行動が戦略的優先事項と矛盾する場合にフラグ

**ブラインドスポット検出** — 予測符号化神経科学に基づく：システムは存在するものだけでなく、欠けているものを能動的に探す。未所属のプロジェクト、途切れたフロー、無視された driving_force、欠落した生活次元、準備なしで迫る時間ウィンドウ。

### Agent 統合

| Agent | 戦略マップの活用方法 |
|-------|-------------------|
| 早朝官 | 上朝時に STRATEGIC-MAP.md をコンパイル（ステップ 8.5）。ブリーフィングを戦略ラインでグループ化 |
| 丞相 | プロジェクト横断の質問を戦略ライン用語で構成。役割別に時間配分を推奨 |
| 中書省 | フローが存在する場合、プロジェクト横断の影響次元を追加。enabler の依存リスクをフラグ |
| 門下省 | 決定の伝播（下流への影響）+ SOUL-戦略の整合を確認 |
| 兵部 | 戦略的役割でタスク優先度を重み付け。待機期間の活用を推奨 |
| 起居郎 | 新しい関係を検出（Phase 2 候補）。last_activity を更新。DREAM REM をフローグラフのスキャフォールディングで強化 |

### データアーキテクチャ

- `_meta/strategic-lines.md` — 戦略ライン定義（ユーザー定義、config.md と同様）
- `projects/{p}/index.md` strategic フィールド — プロジェクトごとの関係（既存の status/priority フィールドと同様）
- `_meta/STRATEGIC-MAP.md` — コンパイルビュー（STATUS.md / wiki/INDEX.md と同様 — 手動編集禁止）
- 認知パイプライン：5ステージ → 6ステージ（Associate と Emerge の間に「Strategize」を追加）
- 既存パターンに準拠：単一の真実の源、outbox マージ、ユーザー確認済み候補、ゼロからの成長

### 設計基盤

認知科学研究に基づく：
- **目標システム理論**（Kruglanski 2002）— 二層構造の意図（purpose vs driving_force）
- **認識駆動型意思決定**（Klein 1998）— アーキタイプマッチング＋ナラティブ評価（数値スコアに代わる）
- **予測符号化**（Friston 2005）— 欠落モニタリングによるブラインドスポット検出
- **コントロールの期待値**（Shenhav et al. 2013）— 努力と機会コストを考慮したレバレッジベースのアクション推奨
- **偏向競争**（Desimone & Duncan 1995）— 「無視して安全」を能動的認知抑制として

---

## [1.4.4b] - 2026-04-15 · タイムスタンプ捏造の防止

> LLM が session-id 生成時にシステムクロックを読まずにタイムスタンプを捏造していた。すべての session-id 生成指示に date コマンドの実行を明示的に要求。テンプレート式仕様からコマンド式仕様に変更。

### 変更

- **qiju.md**：session-id ステップをテンプレート形式から「date コマンドを実行し、実際の出力を使用。HARD RULE。」に変更
- **data-layer.md + data-model.md**：session-id 生成を同じコマンド式表現に同期
- すべての変更を EN/ZH/JA の三言語に適用

---

## [1.4.4a] - 2026-04-15 · エージェントファイルロードの強制

> LLM が退朝時に qiju.md を読まず、記憶だけで簡略版を実行していた。3層の強制措置を追加：SKILL.md のルーティングを「必ずファイルを読む」に変更、qiju.md に必須完了チェックリストを追加、オーケストレーション規範に第6条を追加。

### 強制メカニズムの変更

- **SKILL.md**：上朝/退朝のルーティングを「Xにルーティング」→「`pro/agents/X.md` を必ず読み subagent として起動すること。HARD RULE。」に変更
- **qiju.md**：必須完了チェックリスト追加——各フェーズに実際の値（commit hash、Notion同期状態など）の記入が必要。未記入項目 = 退朝未完了。
- **オーケストレーション行動規範**：第6条追加——「トリガーワードは必ずエージェントファイルをロード。定義ファイルを読まずに記憶で役割を実行してはならない。HARD RULE。」

### 同日の監査修正も含む

- zaochao.md git 健全性チェック：自動修復→検出→報告→確認（GLOBAL.md セキュリティ境界 #1）
- GLOBAL.md：「完全な思考過程」→「公開可能な推論サマリー」（クロスモデル移植性）
- 14→16 subagent 数修正
- AGENTS.md デッドリンク notion-schema.md 修正
- adapter-github.md：復旧コマンドを text ブロック＋手動確認ヘッダーに変更
- evals/run-eval.sh：終了コードキャプチャ、パスサニタイズ、三言語ヘッダー対応
- setup-hooks.sh：ファイル書き込み前のプリフライト検証
- lifeos-version-check.sh：XDG キャッシュパス、grep ベースのバージョン解析

---

## [1.4.4] - 2026-04-14 · 起居郎——セッション終了スペシャリスト

> 早朝官を 2 つの役職に分割：早朝官はセッション開始（読み取り）、起居郎はセッション終了（書き込み）を担当。DREAM は起居郎に統合——独立エージェント起動なし。

### 📝 新役職：起居郎

唐代の朝廷で皇帝の言行を記録した官職にちなんで命名。「退朝」と言うと起居郎がすべてを処理：

- **Phase 1 — アーカイブ**：decisions/tasks/journal → outbox
- **Phase 2 — 知識抽出**（コア責務）：全セッション素材から Session Candidate（wiki + SOUL）を抽出 → ユーザーがその場で確認
- **Phase 3 — DREAM**：3日間の深度レビュー → DREAM Candidate（wiki + SOUL）→ 次回上朝で確認
- **Phase 4 — 同期**：git push + Notion同期（4つの具体操作）

### 主な改善
- 知識抽出が起居郎のコアミッション——298行ファイルの step 6.5 ではなくなった
- DREAM が退朝フローに統合——エージェント起動が1回減、「最後にスキップされるステップ」ではなくなった
- セッション対話サマリーが起居郎に渡される——丞相の直接対応対話からも知識抽出可能に
- Notion同期が明示的に保証——4つの具体書き込み、失敗時は明確に報告
- 16 役職（旧 15）：早朝官 + 起居郎が旧統合役職を置き換え
- `dream.md` 削除——`qiju.md` に完全統合

---

## [1.4.3e] - 2026-04-13 · SKILL.md スリム化——純粋なルーティングファイル

> SKILL.md を 384 行から 93 行に圧縮。Lite Mode を廃止。すべての詳細な役職定義、出力フォーマット、設定は agent ファイルとリファレンスドキュメントに配置。

### Token 節約
- **SKILL.md**：384 → 93 行（−291 行 ≈ −4,700 tokens/session）
- 削除：御史台/諫官/政事堂/早朝官の詳細説明、上奏文フォーマット、ストレージ設定、Lite Mode フロー、二種の審議比較表、Pro Mode インストール詳細
- 削除されたすべてのコンテンツは agent ファイル（`pro/agents/*.md`）またはリファレンスファイル（`references/*.md`）に既存

### 行動規範の再配置
- 丞相関連ルール（8 条）は SKILL.md に残留
- オーケストレーションルール（#2 封駁、#7 自動トリガー、#11 完全出力、#14 真の subagent、#9 デグレード）を `pro/CLAUDE.md` 新設「オーケストレーション行動規範」セクションに移動
- ユニバーサルエージェントルールは `pro/GLOBAL.md` でカバー済み

### 六部オンデマンド選択
- `zhongshu.md`：新設「六部選択（HARD RULE）」——関連する部のみを理由付きで割り当て
- `shangshu.md`：新設「割り当て済みの部のみ発令（HARD RULE）」——未割り当ての部には発令しない

### Lite Mode 廃止
- Life OS の核心的価値は独立した subagent によるチェック・アンド・バランス——単一コンテキストのシミュレーションはこの目的に反する
- README インストール表：Lite Mode 行を削除、単一コンテキストプラットフォームは非サポートの注記を追加

---

## [1.4.3d] - 2026-04-13 · バージョンチェックを出力フォーマットの必須フィールドに

> バージョン検出を独立した指示（LLM がスキップする）から朝議前準備出力テンプレートの必須フィールド（LLM が確実に記入する）に移動。

- **バージョン表示がテンプレートフィールドに**：`🏛️ Life OS: v[ローカル] | 最新: v[リモート]`、更新方法をインライン表示
- **zaochao.md Mode 0 + Mode 1**：ステップ 3 が WebFetch でリモートバージョンを取得、ローカル・リモート両方が必須出力フィールド
- **chengxiang.md**：朝議前準備フォーマットを同じバージョン表示に同期
- **SKILL.md**：冗長なバージョン自己チェックセクションを削除（出力フォーマットに移動）
- 根拠：LLM は出力テンプレートを確実に記入する（HARD RULE #13）、独立指示をスキップしても記入する

---

## [1.4.3c] - 2026-04-13 · バージョン自己チェックを SKILL.md に移動

> バージョン検出をエージェントファイルから SKILL.md に移動——すべての LLM が最初に読むファイル。古いエージェントファイルが自身の更新を検出できないブートストラップパラドックスを解決。

- **バージョン自己チェックセクション**を SKILL.md 最上部（丞相指示の前）に追加：WebFetch でリモートバージョンを確認、更新を促す、失敗を報告
- **zaochao.md 簡素化**：Mode 0 と Mode 1 のバージョンチェックが SKILL.md を参照するように変更、WebFetch ロジックの重複を排除
- zaochao.md や他のエージェントファイルが古くても動作する——SKILL.md は常に最初に読まれる

---

## [1.4.3b] - 2026-04-13 · 退朝フローでのナレッジ抽出

> Wiki 抽出がもはや DREAM のみに依存しない。退朝フローがセッション出力を直接スキャンし、DREAM 実行前に wiki 候補をユーザーに提示するようになった。

- **退朝ナレッジ抽出（ステップ 6.5）**：ラップアップおよび退朝モードがセッション出力から再利用可能な結論をスキャン → ユーザーに wiki 候補を提示 → 確認されたエントリを outbox wiki/ に書き込み
- **Outbox wiki マージ**：上朝マージが outbox 内の wiki/ ファイルを処理 → wiki/{domain}/{topic}.md に移動
- **DREAM 重複チェック**：DREAM N3 が退朝フローで wiki 候補がすでに抽出されたかを確認（manifest 経由）→ 再提案をスキップし、見逃された結論のみに集中
- **Outbox フォーマット**：manifest.md の outputs に `wiki` カウントを追加

---

## [1.4.3a] - 2026-04-13 · Wiki & SOUL 初期化ガイダンス

> wiki/ と SOUL.md が未初期化であることをシステムが検出し、初回セットアップとレガシー移行をユーザーにガイドするようになった。

- **Wiki 初回初期化**：早朝官が空の wiki/ または INDEX.md の欠如を検出 → 既存の decisions/journal から結論の抽出を提案
- **Wiki レガシー移行**：旧フォーマットの wiki ファイル（フロントマターのない調査レポート）を検出 → 結論の抽出とオリジナルのアーカイブを提案
- **SOUL ブートストラップ**：SOUL.md が存在しない場合、DREAM が最初の退朝時に user-patterns.md から初期エントリを提案
- **上朝検出**：ステップ 5.5（SOUL チェック）と 10.5（wiki 健全性チェック）がブリーフィングで初期化ステータスを報告

---

## [1.4.3] - 2026-04-13 · Wiki 活性化 — ナレッジパイプラインが動き出す

> 認知パイプラインの「定着 → 創発」段階がついに機能。Wiki は空のディレクトリからアクティブなナレッジ参加者へ。

### 📚 Wiki 仕様（`references/wiki-spec.md`）

Wiki はセカンドブレインに設計されていたが、どのワークフローにも接続されていなかった — 書き込むエージェントも、読み取るエージェントもいなかった。今や四つの要素がすべて揃った：

- **誰が書くか**：DREAM が N3 段階で wiki 候補を提案する（SOUL 候補と並行して）
- **いつ書くか**：退朝のたびに、ユーザーが次の上朝時に確認
- **誰が読むか**：丞相が wiki/INDEX.md を読み取り、門下省が整合性を確認し、御史台が健全性を監査
- **いつ読むか**：セッション開始時、決定審査時、巡検時

### 🔍 丞相のナレッジマッチング

丞相がルーティング前に wiki/INDEX.md をスキャンするようになった。現在のドメインに高確信度のエントリが存在する場合：「📚 この領域にはすでに N 件の確立された結論があります。既知の知識から始めますか？それとも一から調査しますか？」 — ユーザーが同意すれば冗長な分析をスキップ。

### ⚖️ 門下省の Wiki 整合性チェック

門下省が新しい結論を確立された wiki エントリと照合するようになった。矛盾が検出された場合：「⚠️ これは [wiki エントリ]（確信度 X）と矛盾します。」分析の修正が必要か、wiki の更新が必要か。

### 🔱 御史台の Wiki 健全性監査

巡検で wiki の健全性をカバーするようになった：確信度 < 0.3 かつ 90日以上更新なしのエントリ（廃止を提案）、challenges > evidence のエントリ（レビューを提案）、決定はあるが wiki エントリがないドメイン（ナレッジギャップ）。

### 📨 尚書省の Wiki コンテキスト

丞相が関連する wiki エントリにフラグを立てると、尚書省がそれを派遣に含める：「📚 既知の前提 — ここから始めよ、再導出するな。」

### 🧠 認知パイプラインの再整理

パイプラインが実際の情報フローを反映するようになった：`知覚 → 捕捉 → 判断 → 定着 → 連想 → 創発`。定着は SOUL（人）と Wiki（知識）に分岐する。連想は丞相が新しいリクエストを wiki と照合する時に起こる。創発は DREAM の REM ステージが領域横断のつながりを発見する時に起こる。

### 設計原則

新しいエージェントなし、新しいフローなし。Wiki は既存のリズムに接続された：DREAM が書く → 早朝官が INDEX を編纂 → 丞相が読む → 門下省がチェック → 御史台が監査。

---

## [1.4.2] - 2026-04-12 · Outbox — 並列セッション、コンフリクトゼロ

> 複数のセッションが異なるプロジェクトで同時に作業可能に。git コンフリクトなし、ロックなし。各セッションは退朝時に自分の outbox に書き込み、次に上朝したセッションがすべてをマージします。

### 📮 Outbox アーキテクチャ

旧モデルは同時に一つのセッションのみを想定し、`.lock` ファイルで並行性を警告していました。新モデルは並列を受け入れます：

- **各セッションは退朝時に自分の隔離ディレクトリに書き込む**（`_meta/outbox/{session-id}/`）— 決定、タスク、日記、index delta、patterns delta、manifest
- **退朝中に共有ファイルへの直接書込みなし** — `projects/`、`STATUS.md`、`user-patterns.md` はマージまで一切触れない
- **マージは上朝時に実行** — 次に上朝したセッションがすべての outbox をスキャンし、時系列順にメイン構造へマージ、STATUS.md をコンパイル、クリーンアップ
- **session-id = `{platform}-{YYYYMMDD}-{HHMM}`**、退朝時に生成（セッション開始時ではない）
- **ゼロコンフリクト保証** — 異なるディレクトリ、異なるファイル、同一パスへの並行書込みなし
- **merge-lock** — 同時上朝という極端なケースのセーフティネット（< 5分、自動クリーンアップ）

### カバーされるシナリオ

- 単一セッション通常フロー ✅
- 複数プラットフォーム交互使用 ✅
- 複数ウィンドウ並列 ✅
- 複数コンピュータ ✅
- 複数日にまたがるセッション ✅
- 同一セッション複数回の上朝/退朝 ✅
- 空セッション（出力なし、outbox なし）✅
- push 失敗（ローカル保存、次回リトライ）✅
- Lite ユーザー（セカンドブレインなし、outbox なし）✅
- モバイル Notion キャプチャ（inbox/、変更なし）✅

### 修正ファイル

- `pro/agents/zaochao.md` — Mode 0/1 に outbox マージ追加、Mode 3/4 を outbox 書込みに変更
- `references/data-model.md` — session lock 削除、outbox ルール + manifest/delta 形式追加
- `references/data-layer.md` — ディレクトリ構造 + Housekeeping/Wrap-Up フロー更新
- `references/adapter-github.md` — commit convention を outbox パターンに変更
- `SKILL.md` — ストレージ設定に並列セッション説明追加

---

## [1.4.1] - 2026-04-12 · SOUL + DREAM — システムがあなたを知り始める

> SOUL.md はあなたの決断から成長し、あなたが誰かを記録する。DREAM はあなたがいない間に記憶を処理する — 睡眠中の脳のように。二つが合わさり、Life OS に自己認識のフィードバックループを与える。

### 🔮 SOUL — ユーザーパーソナリティアーカイブ

価値観、信念、アイデンティティ — 証拠ベースのエントリとしてゼロから成長。各エントリには二つの面がある：実際に何をしているか（実態）とどうありたいか（理想）。その差距が成長の余地。

- **自然に成長** — 空白から始まり、決断と行動から蓄積
- **4つのソース** — DREAM が発見、諫官が観察、翰林院が浮上、あなた自身が直接書込
- **ユーザー確認必須** — システムが提案し、あなたが決める。自動書込なし
- **Confidence スケーリング** — 新エントリは諫官のみに影響；深く検証されたエントリはシステム全体に影響
- **各役職は異なる読み方** — 丞相はより鋭い質問、中書省は関連次元を追加、門下省は価値の整合性、諫官は行動監査、翰林院は思想家マッチング

### 💤 DREAM — AI 睡眠サイクル

退朝のたびにシステムは「眠る」— 人間の睡眠構造に着想：

- **N1-N2（整理）** — 受信箱の分類、期限切れタスクのフラグ、孤立ファイルの発見
- **N3（固化）** — 繰り返すテーマを wiki に抽出、行動パターン更新、SOUL 候補提案
- **REM（接続）** — 領域横断のつながり発見、価値-行動整合性チェック、予想外の洞察生成
- **スコープ**：直近3日間のみ。ドリームレポートは `_meta/journal/` に保存、次の上朝で提示
- **新エージェント**：`pro/agents/dream.md`

### 📐 新リファレンスファイル

- `references/soul-spec.md` — SOUL フォーマット、ライフサイクル、confidence 計算、役職別使用ルール
- `references/dream-spec.md` — DREAM トリガー、三ステージ、出力形式、制約

---

## [1.4.0] - 2026-04-12 · 人類の叡智の殿堂 + 三省の深化 + 唯一の情報源

> 翰林院が人類の叡智の殿堂へと進化し、五つのコア役職が全面的に強化され、STATUS.md と index.md のバージョン不整合というアーキテクチャレベルのバグを修正 — index.md が唯一の権威ある情報源、STATUS.md はそこからコンパイルされます。

### 🏗️ アーキテクチャ修正 — 唯一の情報源

`projects/{p}/index.md` がプロジェクトのバージョン、フェーズ、ステータスの権威ある情報源となりました。`_meta/STATUS.md` は index.md ファイルからコンパイルされ、手書きは禁止です。STATUS.md と index.md のバージョン番号が不一致になるバグを修正しました。御史台巡検にバージョン整合性の lint ルールを追加。

### 🎋 翰林院 → 人類の叡智の殿堂

翰林院はもはや「第一原理 + ソクラテス + オッカムの剃刀」だけの場所ではありません。今のあなたは、ソクラテスと人生を語り合い、マスクとビジネスロジックを解剖し、老子とニーチェに人生の意味を論じさせることができます。

- **18分野・70名超の思想家** — 科学から哲学、東洋思想から法と正義まで、人類文明の重要な次元をすべて網羅
- **深いロールプレイ** — 「ソクラテスの方法を使う」のではなく、ソクラテス本人があなたと対話します。彼の口調、彼の事例、彼の問い返し方で
- **三つの対話モード** — 一対一の深掘り（個人探求）、円卓会議（複数の思想家が各自の見解を述べる）、ディベート（賛否の激突）
- **独立 subagent** — 各思想家は独立した context で動作し、翰林院自身が進行役を務めます
- **締めの儀式** — 思想家からの別れの言葉 → 翰林院があなたの思考の変化を総括 → second-brain へ保存

### 🔍 門下省 — 「形式的な確認」から「真の最後の砦」へ

- **10/10/10 後悔テスト** — 10分後・10ヶ月後・10年後、三つの時間軸で必ず個別に回答を求めます。「後悔しないだろう」という曖昧な答えは受け付けません
- **レッドチーム審査** — 計画が必ず失敗すると仮定した上で、最も脆弱な前提・最も運頼みの部分・意図的に軽視されているリスクを洗い出します
- **否決フォーマットの構造化** — 否決はもはや一言の「不可」では済みません。どの次元が問題か・本質は何か・具体的にどう修正するかを明確に述べる必要があります

### 🏛️ 政事堂 — 「曖昧なトリガー」から「定量ルール + 構造化ディベート」へ

- **定量トリガー** — 二部門のスコア差が3点以上、または一部門が「やる」・他が「やらない」と判断した場合、自動的に朝堂議政を発動
- **独立 agent の新設** — `zhengshitang.md`、3ラウンドの構造化ディベート：陳述 → 対決 → 最終立場 → 裁定
- **尚書省が進行役、ユーザーが裁定** — ディベートにはルールと字数制限があり、独白の場にはなりません

### 📨 尚書省 — 「タスク配分」から「インテリジェントスケジューリング」へ

- **依存関係の検出** — 「戸部の結論が兵部の方針に影響する」といった部門間の依存関係を自動認識し、Aグループを先に実行してからBグループを動かします
- **照会メカニズム** — 兵部が「戸部から一つ数字をもらいたい：使える資金はいくらか」と問い合わせられ、尚書省が中継します。完全なレポートは公開されません

### 🏛️ 丞相 — 意図の明確化を分類化

- **五種の分類戦略** — 意思決定系（判断基準は？制約は？）・計画系（目標は？リソースは？）・困惑系（感情は？本当の悩みは？）・振り返り系（基準は？次元は？）・情報系（直接処理）
- **感情分離プロトコル** — 感情と意思決定が混在している場合、まず一言で感情に寄り添い、それから事実を切り分けます

### 💬 諫官 — 「観察」から「学習」へ

- **行動パターン学習ループ** — 新しいパターンや変化を発見するたびに、マークして user-patterns.md に書き込みます
- **セッション横断のトレンド分析** — 直近3回のレポートを比較：リスク志向・意思決定の速さ・実行力・注目次元の変化傾向
- **ポジティブ強化** — 悪い点だけを指摘するのではありません。前回「もっと果断に」とアドバイスして今回それができていたら、必ず明確に褒めます

### ⚖️ システムレベル

- **「二つの議」比較表** — SKILL.md に政事堂 vs 翰林院の違いを追加：一方は「やるべきか」を議論し、もう一方は「あなたは何者か」を探求します
- **丞相のルーティングルール** — データの矛盾は政事堂へ、価値観の迷いは翰林院へ

---

## [1.3.1] - 2026-04-12 · プロセスは必ず見えるように

> すべての subagent に完全な思考プロセスの開示を強制し、Pro モードでは本物の subagent を必ず起動するようにしました。

- **emoji の強制** — すべての subagent の出力に 🔎/💭/🎯 のマークが必須。省略は規約違反
- **本物の subagent の強制** — Pro 環境では各役職を独立した agent 呼び出しにする必要があります。単一 context でのシミュレーションは禁止
- **役職境界のロック** — HARD RULE #17：定義済みの15役職のみ。通政使司・大理寺などシステム外の官職を勝手に追加することは禁止
- **inbox は丞相へ** — 丞相がメールボックス管理を正式に引き継ぎ
- **上朝の自動更新** — 早朝官が GitHub のバージョンを確認し、新バージョンが見つかれば自動でプラットフォームのアップデートコマンドを実行
- **git ヘルスチェック** — 上朝前に worktree の残留と hooksPath の断絶を確認
- **ko/es の削除** — 韓国語とスペイン語のプレースホルダーを削除。EN/ZH/JA を維持
- **tag の整理** — 旧 tag 13個 → 正しい Strict SemVer の tag 5個
- **second-brain の整理** — テンプレートに front matter を補完し、旧ディレクトリ（gtd/records/zettelkasten）を削除

---

## [1.3.0] - 2026-04-10 · 三プラットフォーム Pro Mode + ストレージ抽象化レイヤー

> Life OS が Claude Code 専用から Claude + Gemini + Codex の三プラットフォーム Pro Mode へと拡張され、データストレージが Notion のハードコードからプラガブルな三バックエンド構成に変わりました。

### ストレージ抽象化レイヤー

標準データモデル（6種類・7種類の操作）を一つ用意し、三つの選択可能なバックエンド（GitHub / Google Drive / Notion）に対応。どれを選んでもその adapter が読み込まれます。複数のバックエンドを使う場合は自動同期し、競合時は last-write-wins またはユーザーに確認します。

### クロスプラットフォーム Pro Mode

14の agent 定義を共用し、オーケストレーションファイルをプラットフォームごとに分割：`CLAUDE.md`（Claude Code）・`GEMINI.md`（Gemini CLI / Antigravity）・`AGENTS.md`（Codex CLI）。各プラットフォームが自動的に最強のモデルを使用。ハードコードなし。

### トリガーワードの標準化

英語・中文・日本語の三言語トリガーワードを正式に定義し、Claude と Codex の「上朝」時の動作の不一致を解消しました。

---

## [1.2.0] - 2026-04-08 · 国際化 + アーキテクチャの統合

> 全34ファイルを英語（主版）に翻訳し、中文・日本語の完全翻訳も完成。システムアーキテクチャを大幅に統合しました。

### 国際化

英語が主版となり、中文と日本語は i18n 翻訳として位置づけ。README を再設計し、shields.io バッジとビジュアル階層を追加しました。

### アーキテクチャの統合

- **pro/GLOBAL.md** — 14 agent の共通ルールを単一の権威ある情報源として切り出し、各 agent ファイルを30%スリム化
- **認知パイプライン** — 五段階の情報フロー：感知 → 捕捉 → 関連付け → 判断 → 定着 → 創発
- **御史台の巡察モード** — 意思決定レビュー以外の第二の動作モード。六部それぞれが second-brain 内の管轄区域を自ら巡察
- **知識抽出の四ステップ訓練** — ユーザーが決定 → サンプルを蓄積 → LLM がルールを帰納 → 定期的に補正

### 🔴 破壊的変更

second-brain のディレクトリ再構成：`zettelkasten/` → `wiki/`、`records/` → `_meta/journal/`、新たに `_meta/` システムメタデータレイヤーを追加。

---

## [1.1.1] - 2026-04-05 · データレイヤーの転換

> GitHub の second-brain が Notion に代わってデータの主ライブラリとなり、Notion はモバイル端末のワーキングメモリへと役割を変えました。

- **GitHub をメインライブラリに** — .md + front matter、GTD + PARA + Zettelkasten を融合
- **早朝官の三モード** — 家事（自動）・審視（ユーザー起動）・締め（フロー後）
- **セッションバインド** — 各セッションで project/area を一つに固定し、すべての読み書きをその範囲内に限定
- **退朝コマンド** — GitHub へ push + Notion をリフレッシュ
- **CC 強制 Pro** — Claude Code を検出したら必ず独立 subagent を起動

---

## [1.1.0] - 2026-04-04 · ドキュメント + リサーチプロセス + 記憶レイヤー

> 完全なドキュメント体系が稼働し、すべての agent がリサーチプロセスを表示できるようになり、丞相には記憶レイヤーと思考ツールが加わりました。

- **マルチプラットフォームインストールガイド** — 7プラットフォームの詳細手順
- **全14 agent に 🔎/💭/🎯 リサーチプロセス表示を追加**
- **諫官21項目の観察能力** — 認知バイアス・感情検知・行動追跡・意思決定品質
- **丞相の意図明確化** — 上奏前に2〜3ラウンドの対話を行い、直接エスカレーションしない
- **上朝指標ダッシュボード** — DTR / ACR / OFR + 4つの週次指標
- **12の標準シナリオ設定** — キャリア・投資・移住・起業などの主要な意思決定シナリオをカバー

---

## [1.0.0] - 2026-04-03 · 初期リリース

> 三省六部制の個人内閣システムが正式に公開。15の役職、制衡と分権。

- 15役職：丞相 + 三省 + 六部 + 御史台 + 諫官 + 政事堂 + 早朝官 + 翰林院
- Lite モード（単一 context）+ Pro モード（14独立 subagent）
- 10の標準シナリオ設定
- 六部 × 四司の詳細な職能定義
- Apache-2.0 License
