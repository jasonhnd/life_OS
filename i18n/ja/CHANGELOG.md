# 変更履歴

## バージョニングルール

このプロジェクトは **Strict SemVer** に従います：MAJOR（破壊的変更）· MINOR（新機能）· PATCH（修正・保守）。同日の変更は単一リリースにまとめ、リリースごとに git tag を打ちます。

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
  - Narrator-spec 違反 — **決議保留** (次回 Compliance Patrol で追跡)

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
