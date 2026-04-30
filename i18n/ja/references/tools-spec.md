---
translated_from: references/tools-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
---

# Python Tools · 契約仕様書(Contract Specification)

> Life OS 実行スタックの Layer 4。Shell hooks(Layer 3)が HARD RULE を
> 本当に hard にする一方、Python tools はシステムが自走するようにします。
> 本ドキュメントは `tools/` 内のすべてのツールに対する権威的契約です。
>
> 参照: `docs/architecture/execution-layer.md`(設計根拠)、
> `references/data-model.md`(ツールが操作する型)、
> `references/adapter-github.md`(ディスク上のファイルフォーマット)。

---

## 1 · 目的(Purpose)

Python tools はユーザーの second-brain markdown ファイルに対して、Claude
Code セッション内に自然に収まらないバッチ/バックグラウンドタスクを実行し
ます。セッションは同期的、インタラクティブで、ユーザーの注意によって
境界付けられています。second-brain には長時間実行で、システマティック
(LLM の創造性抜きで全ファイルに触れる)かつ LLM フリー(純粋に
パース + YAML 生成 + markdown I/O)なメンテナンスが必要です。

ユーザー決定により、すべてのツールは **ローカル** で動作し、Claude Code
の Bash ツールまたは手動から起動されます。GitHub Actions なし、
cron-on-VPS なし、外部 API コールなし。ユーザーがマシンを所有し、
second-brain はローカルディレクトリです。

Tools は **optional** です。Python をインストールしない新規 Life OS
ユーザーも、Claude Code 内で完全な decision-engine 体験を得られます。
Tools はメンテナンス自動化を追加しますが、コア機能ではありません。

---

## 2 · ランタイム(Runtime)

**Python 3.11+** と、パッケージマネージャ兼ランナーとしての **uv**
(ユーザー決定 #15)。

uv が依存関係、virtualenv、起動の単一 source of truth です。ユーザーは
virtualenv を手動でアクティブ化しません。すべてのツールは次のように
起動されます:

```bash
uv run tools/{tool_name}.py [args]
# または統合 CLI 経由:
uv run life-os-tool {command} [args]
```

`life-os-tool` バイナリは `pyproject.toml` の `[project.scripts]` テーブル
経由で `uv sync` によりインストールされ、最初の位置引数に基づいて
`tools/` 配下の適切なモジュールにディスパッチします。

**なぜ uv か**: pip よりも速く解決・インストールし、Python バージョン
ピン留めを処理し、再現可能な lockfile を生成します。新規ユーザーは
リポをクローンし `uv sync` を実行するだけで、すべてのツールが動きます
— 「venv をアクティブにしましたか?」というサポート負担がなくなります。

---

## 3 · ディレクトリ構造(Directory Structure)

```
tools/
├── __init__.py
├── cli.py                 # Unified entry: `uv run life-os-tool <cmd>`
├── reindex.py             # v1.7 core — compile _meta/sessions/INDEX.md
├── reconcile.py           # v1.7 core — schema / link / orphan checker
├── stats.py               # v1.7 core — usage + quality statistics
├── embed.py               # v1.7 skip (user decision #3)
├── research.py            # v1.7 — web fetch into inbox
├── daily_briefing.py      # v1.7 — on-demand briefing (not cron)
├── backup.py              # v1.7 — tar + optional gpg
├── migrate.py             # v1.7 core — v1.6.2a → v1.7 backfill
├── search.py              # v1.7 — grep-ranked session search
├── export.py              # v1.7 — markdown → pdf/html/json/anki
├── seed.py                # v1.7 — new-user bootstrap
├── sync_notion.py         # v1.7 — Notion fallback sync
├── lib/
│   ├── __init__.py
│   ├── second_brain.py    # read/write markdown + YAML (core library)
│   ├── config.py          # load Life OS config (.life-os.toml)
│   ├── notion.py          # Notion MCP wrapper (optional)
│   └── llm.py             # Claude Code Bash integration
└── tests/
    ├── __init__.py
    ├── test_second_brain.py
    ├── test_reindex.py
    ├── test_reconcile.py
    ├── test_migrate.py
    └── fixtures/sample-brain/
```

`embed.py` は placeholder として存在します — v1.7 は semantic embeddings
なしで出荷されます(ユーザー決定 #3)。ファイルは理由をドキュメント化し、
v1.7 の代替として `search.py` を指し示します。

---

## 4 · 設計原則(Design Principles)

交渉不能な不変条件です。違反するツールはレビューで落ちます。

1. **Markdown 入力、markdown 出力。** second-brain データを JSON、CSV、
   SQLite に変換してはなりません。ツールは piping のために一時的な JSON
   を stdout に emit することはできますが、永続状態は常に markdown です。

2. **冪等(Idempotent)。** ツールを 2 回実行すると、2 回目の実行で同一
   の出力が得られます。`reindex.py` は重複を append しません。
   `migrate.py` は適用済みマイグレーションをマークします。`backup.py`
   は同日の再起動が安全です。

3. **v1.7 では API キー不要。** LLM 作業は Claude Code セッション内に
   留まります。ツールが「知性」を必要とする場合(例: `search.py` の
   ランキング)、機械的な部分を行い、意味論的判断は次セッションで
   subagent に渡します。

4. **単一責任(Single responsibility)。** 一つのツール、一つの仕事。
   合成は複数ツールを起動することで行い、責任を merge することで行って
   はなりません。

5. **Exit code 0 成功、1 エラー。** 標準 Unix。`--dry-run` モードは
   dry-run 成功で exit 0 です。

6. **YAML frontmatter as metadata。** パースには `python-frontmatter`
   を使います。YAML パーサーを手巻きしてはなりません。スキーマは
   `references/data-model.md` で定義されています。

7. **Safe by default。** 明示的なフラグなしにファイルを削除するツール
   はありません。`reconcile.py --fix` は opt-in です。`backup.py` は
   `--prune` なしではローテーションしません。疑わしいときはプランを
   print し、`--apply` を要求します。

---

## 5 · 共通ライブラリ契約(Common Library Contract)(`tools/lib/second_brain.py`)

各ツールが依存する共有ライブラリです。パース、パスの globbing、型
ディスパッチをここに集約することで重複を避けます。

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional

@dataclass
class Frontmatter:
    data: dict
    raw: str

@dataclass
class SessionSummary:
    id: str                # "claude-20260412-1700"
    date: datetime
    subject: str
    domains: List[str]
    overall_score: Optional[float]
    path: Path
    body: str
    frontmatter: Frontmatter

# Concept, Method, WikiNote, EvalEntry, Soul, SoulSnapshot follow the
# same dataclass pattern: typed frontmatter fields + body + path.
# Full field lists are in references/data-model.md §v1.7 Cortex Data
# Types. `Soul` is the in-memory view of the live SOUL.md file (all
# dimensions parsed from body sections + frontmatter per dimension).
# All six dataclasses are immutable; writes construct new instances.


class SecondBrain:
    """Typed read/write layer over the user's second-brain directory."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._validate_layout()

    # File discovery
    def list_sessions(self) -> List[SessionSummary]: ...
    def list_concepts(self, domain: Optional[str] = None) -> List[Concept]: ...
    def list_methods(self, domain: Optional[str] = None) -> List[Method]: ...
    def list_wiki_notes(self, domain: Optional[str] = None) -> List[WikiNote]: ...
    def list_eval_entries(self, last_n: int = 10) -> List[EvalEntry]: ...
    def list_snapshots(self, last_n: Optional[int] = None) -> List[SoulSnapshot]: ...

    # Read (by ID)
    def read_session(self, session_id: str) -> SessionSummary: ...
    def read_concept(self, concept_id: str) -> Concept: ...
    def read_method(self, method_id: str) -> Method: ...
    def read_wiki_note(self, domain: str, slug: str) -> WikiNote: ...
    def read_eval_entry(self, eval_id: str) -> EvalEntry: ...
    def read_snapshot(self, snapshot_id: str) -> SoulSnapshot: ...
    def read_soul(self) -> Soul: ...

    # Write (atomic temp-file-then-rename)
    def write_session(self, summary: SessionSummary) -> None: ...
    def write_concept(self, concept: Concept) -> None: ...
    def write_method(self, method: Method) -> None: ...
    def write_wiki_note(self, note: WikiNote) -> None: ...
    def write_eval_entry(self, entry: EvalEntry) -> None: ...
    def write_snapshot(self, snapshot: SoulSnapshot) -> None: ...

    # Compile (retrospective Mode 0 calls these via reindex.py)
    def compile_session_index(self) -> str: ...
    def compile_concept_index(self) -> str: ...
    def compile_method_index(self) -> str: ...
    def compile_synapses_index(self) -> str: ...

    # Health
    def iter_orphans(self) -> Iterator[Path]: ...
    def iter_broken_links(self) -> Iterator[tuple[Path, str]]: ...
    def iter_missing_frontmatter(self) -> Iterator[Path]: ...

    # Layout validation
    def _validate_layout(self) -> None:
        """
        Check that required second-brain directories exist. Creates
        missing ones silently (seed.py's idempotent guarantee). Raises
        `SecondBrainError` if the root path itself is missing or not
        a directory. Never deletes files.
        """
```

Write メソッドは **レコードレベルで immutable** です: caller が新しい
dataclass を構築し、ライブラリはインスタンスを mutate しません。
書き込みは atomic な temp-file-then-rename を使用します。

---

## 6 · 12 個のツール契約(Twelve Tool Contracts)

各ツールは以下を指定します: purpose、invocation、inputs、outputs、
side effects、exit codes、runtime budget、trigger mode。Trigger mode:

- **on-demand** — ユーザーがコマンドを打つ
- **archiver-called** — adjourn Phase 4 中に archiver から起動される
- **retrospective-called** — セッション開始時に retrospective から起動される
- **manual** — ユーザーが直接実行する(週次/月次)
- **one-time** — インストール/アップグレード毎に一度

### 6.1 `reindex.py` — Session Index コンパイル

`_meta/sessions/*.md` をスキャンし、日付降順でセッション毎に一行を持つ
`_meta/sessions/INDEX.md` を emit します。

```bash
uv run tools/reindex.py [--verbose]
```

- **Input**: `_meta/sessions/` 配下のすべての session summary ファイル
- **Output**: `_meta/sessions/INDEX.md`(atomically 上書き)
- **Side effects**: なし
- **Exit codes**: `0` 成功、`1` I/O エラーまたは読めない frontmatter
- **Runtime**: 1,000 セッションで 5 秒未満
- **Trigger**: retrospective Mode 0(primary)、バルクインポート後の
  ユーザー手動。**NOT archiver** — `references/session-index-spec.md`
  §10 anti-pattern に従い、コンパイルは retrospective の責任です
  (archiver + retrospective 間で分割すると、2 つのプラットフォームが
  同時にセッションを閉じるときレースコンディションが発生)

INDEX.md ヘッダは
`<!-- generated by tools/reindex.py — do not edit by hand -->` を含みます。

### 6.2 `reconcile.py` — 整合性チェック

4 つのチェック: orphan ファイル、broken wikilinks、欠落 YAML frontmatter、
スキーマ違反。

```bash
uv run tools/reconcile.py [--fix] [--verbose]
```

- **Input**: second-brain root 配下のすべての markdown
- **Output**: `_meta/reconcile-report-{YYYY-MM-DD}.md`。同日再実行では
  ファイルは **上書き** されます(idempotent): レポートは現在状態の
  スナップショットであり、履歴ログではありません。履歴レポートは
  タイムスタンプサフィックスではなく git で保持されます。
- **`--fix`**: 欠落 frontmatter のデフォルトを挿入、orphan を
  `archive/orphans/` に移動、削除は行いません。再実行安全 —
  fix 済みファイルはスキップされます。
- **Exit codes**: clean またはすべて fix された場合 `0`、fix 不能が
  残った場合 `1`
- **Runtime**: 5,000 ファイルで 30 秒
- **Trigger**: ユーザー週次、Mode 0 中に retrospective が呼ぶことも可
- **Idempotent**: はい — 同一 tree で 2 回実行すると同じレポートが
  生成され、2 回目は書き込みアクションを行いません

`--fix` は明白なケース(欠落 `last_modified`、欠落 `id`、orphan
クリーンアップ)のみ扱います。判断を要する call はユーザーまたは
subagent に任せます。

### 6.3 `stats.py` — 利用と品質の統計

sessions、eval-history、snapshots、SOUL にわたる period 毎の
集約です。self-review 用の markdown レポート。

```bash
uv run tools/stats.py [--period month|quarter|year] [--since YYYY-MM-DD] [--output FILE]
```

- **Input**: `_meta/sessions/`、`_meta/eval-history/`、
  `_meta/snapshots/`、`SOUL.md`
- **Output**: stdout markdown(デフォルト)。`--output FILE` 指定時は
  代わりにパスに書き出します(`_meta/self-review-{YYYY-MM}.md` への
  piping 用)。
- **デフォルト period**: `--period` も `--since` も与えられなかった
  場合、直近 30 日をカバーする `--period month` がデフォルトです。
- **Reports**: session count、平均 `overall_score`、domain 分布、
  SOUL トレンド、DREAM トリガー頻度、top 3 concept tag、
  eval-history 次元平均
- **Exit codes**: `0` 成功(空 period を含む — 「no data」を print
  するが exit 0)、`1` I/O エラー
- **Runtime**: 1 年分のデータで 10 秒未満
- **Trigger**: manual、通常月次

記述的のみ。stats.py は数字を計算し、解釈はユーザーまたは
retrospective subagent に任せます。

### 6.4 `research.py` — バックグラウンド Web フェッチ

トピックをフェッチし、HTML を markdown にクリーンアップし、日付付き
ノートを `inbox/` に append します。

```bash
uv run tools/research.py "日本永驻新政策" [--depth 3] [--max-pages 10]
```

- **Input**: なし(HTTP フェッチを実行)
- **Output**: `inbox/research-{YYYY-MM-DD}-{topic-slug}.md`
- **Topic slug**: 可能な範囲でクエリを ASCII transliterate(CJK では
  pinyin)+ 小文字化 + ハイフン化により派生します。transliterate
  できない非 ASCII クエリは SHA-1 hash prefix を使用
  (`inbox/research-{date}-{hash8}.md`)。
- **Side effects**: `httpx` 経由のネットワーク、`urllib.robotparser`
  (stdlib)を使って `robots.txt` を尊重、user agent は
  `LifeOS-research/1.7 (+local-tool)` に設定
- **`--depth N` セマンティクス**: **シード検索結果からの link-following
  depth**。`--depth 0` = 検索結果ページのみ。`--depth 1`(デフォルト)=
  各 top result をページとしてフェッチ。`--depth 2` = それらのページ
  からの outbound link を 1 層 follow。ランタイムと帯域を制限するため
  `--max-pages`(デフォルト 10)でキャップ。
- **Exit codes**: `0` 成功、`1` フェッチ失敗(次セッションが信頼しない
  ように `incomplete: true` frontmatter フラグ付きの部分ファイルを書く)
- **Runtime**: `--depth × --max-pages` により bound、デフォルト(1×10)
  でまともな接続なら通常 30 秒未満
- **Trigger**: ユーザー手動(非同期 intent capture)

v1.7 はシンプルな実装で出荷します: `httpx.get` + `markdownify`
converter、**LLM 要約なし**(ユーザー決定 #16: tools 内に外部 LLM API
なし)。より深い multi-source research は v1.7 の scope 外です。

### 6.5 `daily_briefing.py` — 今日の Briefing

SOUL、DREAM journal、active projects、inbox、直近の eval-history から
「今日重要なこと」を生成します。

```bash
uv run tools/daily_briefing.py
```

- **Input**: `SOUL.md`、DREAM journal、`projects/`、`inbox/`、
  eval-history
- **Output**: stdout markdown(retrospective が briefing に埋め込む)
- **Exit codes**: 常に `0`、空の second-brain でも
- **Runtime**: 3 秒未満
- **Trigger**: セッション開始時に Mode 0 中の retrospective、
  schedule なし。ユーザー決定により cron なし。briefing は
  ユーザーが現れたときに生成されます。

純粋なデータ集約。retrospective subagent が何を foreground にするか
決めます。

### 6.6 `backup.py` — second-brain のアーカイブ

second-brain をタイムスタンプ付き tarball としてスナップショットします。

```bash
uv run tools/backup.py [--dest /path] [--gpg KEY_ID]
```

- **Input**: second-brain root 全体
- **Output**: `{dest}/{YYYY-MM-DD}.tar.gz`(`--gpg` 付きなら
  `.tar.gz.gpg`)
- **Side effects**: 設計上 second-brain 外に書く
- **Exit codes**: `0` 成功、`1` 書き込みエラーまたは gpg key 欠落
- **Runtime**: 500 MB で 30 秒
- **Trigger**: ユーザー手動(週次推奨)

デフォルトの `--dest` は `~/second-brain-backups/` です。Retention は
manual。自動 `--prune 30d` フラグは v1.7 の scope 外です。

### 6.7 `migrate.py` — v1.6.2a → v1.7 スキーママイグレーション

one-time マイグレーション。v1.6.2a は `_meta/journal/` に decisions を
保存していました。v1.7 は `_meta/sessions/`、`_meta/concepts/`、
`_meta/snapshots/`、`_meta/eval-history/`、`_meta/methods/` を導入
します。本ツールは新しいレイアウトを backfill します。

```bash
uv run tools/migrate.py --from v1.6.2a --to v1.7 [--dry-run]
```

- **Input**: 既存の `_meta/journal/`(backfill の source of truth)、
  `SOUL.md`(読み取り専用 — synth snapshot input)、`wiki/`(読み取り
  専用 — concept anchor evidence)、`user-patterns.md`(未変更)
- **Backfill scope**: journal の直近 **3 ヶ月**(ユーザー決定 #7)。
  それより古いエントリは `_meta/journal/` にそのまま残ります。この
  ウィンドウはすべてのマイグレーションターゲットで統一 — 下記 per-target
  ルール参照。
- **Per-target ルール**(各ターゲットは自身の権威 spec に従う):
  - `_meta/sessions/{session_id}.md` + `INDEX.md` — セッション毎に
    summary を synthesize(best-effort frontmatter、pre-v1.7 フィールド
    は null)。デフォルト `platform: claude`、session-id は journal
    mtime から派生。`references/session-index-spec.md` §9 参照。
  - `_meta/concepts/**` — 6-criteria + privacy filter パイプラインを
    実行。`activation_count ≥ 3` は `_tentative/` から `{domain}/` に
    promote し `status: confirmed`。`≥ 10` は `canonical` に promote。
    エッジ weight は co-occurrence から、10 でキャップ。
    `references/concept-spec.md` §Migration 参照。
  - `_meta/snapshots/soul/**` — journal から `🔮 SOUL Delta` ブロックを
    スキャン、`provenance: synthetic` frontmatter 付きの合成 snapshot を
    emit。3 ヶ月ウィンドウ(統一)。`references/snapshot-spec.md`
    §Migration 参照。
  - `_meta/methods/_tentative/**` — 言語パターン(「approach」、
    「pattern」、「framework」、「流れ」、「やり方」、「手順」)から
    候補 method の top 5 を抽出。すべて `status: tentative` で開始、
    自動 promote しない。`references/method-library-spec.md` §15 参照。
- **明示的に migrate しないもの**:
  - `_meta/eval-history/` — **backfill なし**。v1.7 初日にフレッシュ
    スタート。`references/eval-history-spec.md` §11 参照。
  - `SOUL.md`、`wiki/`、`user-patterns.md` — synthesis の input として
    読み取り、決して変更しない。
- **Output log**: `_meta/cortex/bootstrap-status.md`(canonical、
  concept-spec と snapshot-spec によりクロス参照)。
- **Side effects**: 新ファイル書き込み、古いもの削除なし、オプションで
  `--with-backup` により `backup.py` を呼び出し
- **LLM-free**: ルールベースのファイル名 + frontmatter マッチ、
  privacy filter は archiver Phase 2 と同じ regex + LLM パイプラインを
  使用
- **Idempotent**: 再実行はコンパイル済みインデックスを上書きし、
  concepts や sessions を重複させない
- **Exit codes**: `0` 成功、`1` パースエラー(スキップされたファイルを
  ログ)
- **Runtime**: 3 ヶ月で 60 秒
- **Trigger**: v1.7 アップグレード中の one-time
- **`--dry-run`**: 書き込みなしでプランを print

### 6.8 `search.py` — クロスセッション検索

答えを含む可能性が最も高い top N セッションを返します。

```bash
uv run tools/search.py "我要不要辞职" [--top N]
```

- **Input**: `_meta/sessions/INDEX.md`(fast path)、次に関連する
  セッションファイル、クエリは argv
- **Output**: stdout にランク付きリスト(path、snippet、score)
- **Exit codes**: 常に `0`(空結果は有効)
- **Runtime**: 1,000 セッションで 3 秒未満
- **Trigger**: ユーザー手動(on-demand)

v1.7 実装は **grep + metadata ranking**、semantic search ではありません。

**ランキング式**(deterministic、LLM なし):

```
base_score =
    4.0 × hits_in_subject
  + 2.0 × hits_in_domains_or_keywords
  + 1.0 × min(hits_in_body_paragraphs, 5)   # cap body contribution
                                             # (hits_in_body_paragraphs
                                             # counts at most once per paragraph)

recency_multiplier =
    1.5  if days_since_session ≤ recency_boost_days (default 90)
    1.0  otherwise

final_score = base_score × recency_multiplier
```

`recency_boost_days` は `.life-os.toml` の `[search] recency_boost_days = 90`
で設定可能です。同点時は新しい方が優先されます。

Semantic search はユーザー決定 #3 により scope 外です。semantic
ランキングについては、ユーザーは Claude Code 内で hippocampus
subagent を起動します。

### 6.9 `export.py` — フォーマット変換

second-brain コンテンツをポータブルフォーマットにエクスポートします。

```bash
uv run tools/export.py --format pdf --scope projects/passpay
uv run tools/export.py --format html --scope wiki
uv run tools/export.py --format json --scope _meta/sessions
uv run tools/export.py --format anki --scope _meta/concepts
```

- **Input**: scope ディレクトリまたはファイルパターン
- **Output**: `exports/{scope-slug}-{YYYY-MM-DD}.{ext}`
- **Formats**:
  - `pdf` — `pandoc` 経由(外部バイナリ、`pandoc ≥ 3.0` 必要)
  - `html` — self-contained(inline CSS、外部アセットなし)、
    `markdown-it-py` を footnote + table 拡張付きで使用
  - `json` — flat 配列、各要素は `{frontmatter: {...}, body: "..."}`
  - `anki` — `genanki` 経由の `.apkg`。**Per-type フィールドマッピング**:
    - Concept: **Front** = `canonical_name` + `aliases`、**Back** =
      body + `outgoing_edges` table(weight 上位 5)
    - Method: **Front** = `name`、**Back** = `summary` + `## Steps`
      セクション
    - Wiki: **Front** = title(conclusion)、**Back** = Reasoning +
      Applicable-When セクション
    - Session summary: **Front** = `subject`、**Back** = Key Decisions
      + Outcome
- **Exit codes**: `0` 成功、`1` pandoc 欠落 / genanki 欠落 / scope 空
- **Runtime**: 100 ファイルあたり 30 秒
- **Trigger**: ユーザー手動

### 6.10 `seed.py` — 新規ユーザー Bootstrap

新規ユーザーのために empty-but-valid な second-brain を作成します。

```bash
uv run tools/seed.py --path ~/second-brain
```

- **Input**: ターゲットディレクトリパス
- **Output**: `SOUL.md` スケルトン、`.life-os.toml` スタブ、
  `projects/example-project/index.md`、`_meta/sessions/`、
  `_meta/concepts/`、`_meta/snapshots/`、`_meta/eval-history/`、
  `inbox/`、`wiki/`(各 `.gitkeep` 付き)、推奨エントリ付き
  `.gitignore` を populate したディレクトリ
- **Side effects**: `git init` を実行し初期 commit を作成
- **Exit codes**: `0` 成功、`1` ターゲットパスが存在して空でない場合
- **Runtime**: 2 秒未満
- **Trigger**: one-time、インストール中にユーザーが実行

### 6.11 `sync_notion.py` — Notion フォールバック同期

archiver のセッション内 Notion 同期(Phase 4)が失敗した場合 — MCP
切断、一時エラー、rate limit — セッション外でリトライします。

```bash
uv run tools/sync_notion.py [--retry] [--since YYYY-MM-DD] [--verbose]
```

- **Input**: `_meta/STATUS.md`、active projects、`_meta/eval-history/`、
  Notion 同期ログ
- **Output**: Notion HTTP API 経由で Notion ページを更新、
  `_meta/notion-sync-log.md` にエントリを append
- **Transport**: **公式 `notion-client` Python パッケージ** を使用
  (HTTPS 経由の Notion REST API)。これは LLM API コールではありません
  — Notion API はプレーンなデータベース API であり、Life OS の v1.6.2a
  archiver Phase 4 メカニズム(これもアクティブセッション中に MCP 経由
  で Notion と話す)と一貫しています。Python tool は同じ基盤 API と
  直接話すことで、Claude Code セッション外で走れます。
- **Token 解決**(優先順位: CLI > env var > config):
  1. `--notion-token` CLI フラグ
  2. `NOTION_TOKEN` 環境変数(推奨: launchd `EnvironmentVariables`
     または macOS Keychain)
  3. `~/second-brain/.life-os.toml` の `[notion]` セクション:
     ```toml
     [notion]
     token_env_var = "NOTION_TOKEN"  # name of env var holding token
     workspace_id = "..."
     ```
- **Workspace 解決**: tool は `_meta/config.md` の `[notion]` セクション
  から workspace / database ID を読み取る。ハードコードしない。
- **ユーザー決定 #16「v1.7 では外部 API なし」の明確化**: この決定は
  **LLM プロバイダ API**(OpenAI、Anthropic HTTP、サードパーティ
  embedding サービス)に scope されます。Notion は v1.6.2a 以来
  すでに使われているユーザーデータストレージプラットフォームであり、
  Python tool が Notion API と話すのは v1.6.2a archiver が Notion MCP
  と話すのと等価です — 同じ capability、異なる transport。
- **Exit codes**: `0` すべて同期、`1` ページ失敗あり、`2` 認証失敗
  または token 欠落、`3` ネットワーク到達不能
- **Runtime**: Notion の rate limit により bound(API キーあたり 3
  req/sec)、1 週間の更新で通常 60 秒未満
- **Idempotency**: 各ページは Life OS 側 ID(session_id、decision slug
  など)で upsert され、Notion ページの `life_os_id` プロパティに
  保存されます。再実行は同じデータを同期し、ページを重複させません。
- **Trigger**: archiver が同期失敗を報告したときのユーザー手動

### 6.12 `embed.py` — v1.7 では scope 外

Semantic embeddings は **v1.7 では scope 外** です(ユーザー決定 #3 —
embeddings なし、vector DB なし)。ファイルは notice を print して
exit 0 する placeholder としてのみ存在し、`uv run tools/embed.py` は
silent ではなくクリーンに失敗します。v1.7 は LLM-judgment retrieval
(`references/hippocampus-spec.md` 参照)と metadata + grep ランキング
(`search.py` §6.8 参照)を代わりに使用します。

```python
"""
embed.py — not implemented. Semantic embeddings are out of scope for v1.7
(user decision #3: markdown-first, LLM-judgment-only).

For retrieval inside a session: use the hippocampus subagent
(references/hippocampus-spec.md).
For batch search: use search.py (metadata + grep ranking).

Invoking this tool prints this notice and exits 0.
"""
```

---

## 7 · 依存関係(Dependencies)

`pyproject.toml` 経由で管理。uv が解決とロックを行います。

**Core**: `python-frontmatter`(YAML パース)、`pyyaml`(エンジン)、
`rich`(ターミナル出力)、`pathlib`(stdlib)。

**Optional(ツール固有)**: `httpx` + `markdownify`(`research.py`)、
`jinja2` + `markdown-it-py`(`export.py`)、`genanki`
(`export.py --format anki`)、`notion-client`(`sync_notion.py`)。

**明示的に使わないもの**:

- `openai`、`anthropic` — **LLM プロバイダ** API。LLM 作業は Claude
  Code セッションに属し、バッチスクリプトに属しません。ユーザー決定 #16。
  (Notion API は LLM API ではなく data-storage API — `notion-client`
  は `sync_notion.py` で使用される、§6.11 明確化参照。)
- `sqlite3`、`psycopg`、いずれのデータベースも — second-brain は
  markdown + git です。
- `celery`、`rq`、いずれの job queue も — tools は同期的に走ります。
- `requests` — `httpx` が同じ surface をカバー、HTTP ライブラリは
  1 つで十分です。

---

## 8 · 設定(Configuration)

ユーザー毎の config は `~/second-brain/.life-os.toml`:

```toml
[second_brain]
root = "~/second-brain"

[tools]
backup_dest = "~/second-brain-backups"

[reconcile]
auto_fix = false

[search]
recency_boost_days = 90

[export]
default_format = "pdf"
```

`tools/lib/config.py` からロードされます。すべてのツールはこの単一
モジュールから import し、`os.path.expanduser` の散発コールをしません。

**優先順位**: CLI フラグ > env vars > `.life-os.toml` > デフォルト。
Env vars は接頭辞 `LIFE_OS_` を使用(例: `LIFE_OS_BACKUP_DEST`)。
Config に必須フィールドが欠落していればツールは fast fail します。

---

## 9 · エラーハンドリング(Error Handling)

すべてのツールが同じ契約に従います:

- **予期しない例外**: トップレベルで catch、型と説明とともに stderr に
  print、exit 1。
- **Validation エラー**: fix ヒントとともに stderr に print、exit 1。
- **No-op 実行**: フレンドリーな 1 行サマリーを stdout に、exit 0。
- **`--verbose`**: ログレベルを DEBUG に。すべての logging は stderr、
  stdout は piping 可能なまま。
- **Never silently swallow**: `reconcile.py --fix` でさえ各変更を
  ログします。

---

## 10 · テスト(Testing)

すべてのツールには `tools/tests/` 配下に対応するテストファイルがあり
ます。テストは `pytest`、`tmp_path` fixture、最小のリアルなフィクスチャ
として `tools/tests/fixtures/sample-brain/` を使用します。

カバレッジはグローバル 80% 最低を満たします。クリティカルパス
(migrate、reconcile、reindex)は 90%+ を目指します — そこのバグは
ユーザーデータを壊すからです。

規約: `test_{behavior}_when_{condition}` 命名、Arrange-Act-Assert 構造、
ユーザーの実 `~/second-brain/` に決して触れない(`SecondBrain(tmp_path)`
を使用)、`httpx` には `respx`、MCP には fake bridge で境界を mock
します。

```bash
uv run pytest tools/tests/
```

---

## 11 · インストール(Installation)

リポルートから:

```bash
uv sync       # creates .venv, resolves deps, installs life-os-tool
uv add <pkg>  # adds a dependency, updates pyproject.toml + uv.lock
```

`pyproject.toml` と `uv.lock` の両方を atomically commit します。

### `pyproject.toml` スケルトン

```toml
[project]
name = "life-os-tools"
version = "1.7.0"
description = "Life OS v1.7 Python tools — markdown-first second-brain maintenance"
requires-python = ">=3.11"
readme = "README.md"
license = { text = "MIT" }
authors = [{ name = "Life OS" }]
dependencies = [
  "python-frontmatter>=1.0",
  "pyyaml>=6.0",
  "rich>=13.0",
]

[project.optional-dependencies]
research = ["httpx>=0.27", "markdownify>=0.11"]
export   = ["jinja2>=3.1", "markdown-it-py>=3.0", "genanki>=0.13"]
notion   = ["notion-client>=2.2"]

[project.scripts]
life-os-tool = "tools.cli:main"

[dependency-groups]
dev = [
  "pytest>=8.0",
  "pytest-cov>=5.0",
  "respx>=0.21",
  "ruff>=0.6",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tools/tests"]
```

### `tools/cli.py` ディスパッチ例

```python
"""
life-os-tool — unified CLI entry point.

Usage:
    uv run life-os-tool reindex [--verbose]
    uv run life-os-tool reconcile [--fix]
    uv run life-os-tool migrate --from v1.6.2a --to v1.7 [--dry-run]
    uv run life-os-tool --help
"""
import sys
from argparse import ArgumentParser

def main() -> int:
    parser = ArgumentParser(prog="life-os-tool")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Each tool registers its own argparser namespace
    for cmd in (
        "reindex", "reconcile", "stats", "research", "daily_briefing",
        "backup", "migrate", "search", "export", "seed", "sync_notion",
        "embed",
    ):
        # Subcommand name uses hyphen form on the CLI: `daily-briefing`
        cli_name = cmd.replace("_", "-")
        sp = sub.add_parser(cli_name, help=f"Run {cli_name}")
        sp.set_defaults(module=cmd)

    args, extra = parser.parse_known_args()
    # Forward remaining args to the tool's own argparse
    import importlib
    mod = importlib.import_module(f"tools.{args.module}")
    return mod.main(extra)   # each tool exports a main(argv: list[str]) -> int

if __name__ == "__main__":
    sys.exit(main())
```

すべてのツールモジュール(`tools/reindex.py`、`tools/migrate.py` など)
は `def main(argv: list[str]) -> int` を export し、自身のフラグを
パースして exit code を返します。このパターンにより各ツールを独立に
実行可能に保ちつつ(`uv run tools/reindex.py --verbose` も動く)、
統合 `life-os-tool <cmd>` エントリポイントを維持します。

---

## 12 · アンチパターン(Anti-Patterns)

重大度順に、禁止:

1. **ユーザーパスをハードコードしない。** `tools/lib/config.py` を通す。
   ハードコードされた `/Users/...` パスは他マシンや CI で壊れます。
2. **設定された second-brain root 外に書かない。** 例外: `backup.py`
   (`backup_dest` に書く)と `export.py`(`exports/` に書く)。
3. **`SKILL.md`、`pro/agents/`、`references/` を変更しない。** これら
   は Life OS システムファイルであり、ユーザーデータではありません。
4. **外部 API 経由の LLM コールを実行しない。** ユーザーはすでに
   Claude Code を持っています。`openai` や `anthropic` クライアントを
   追加すると、何の得もなくキー、クォータ、rate limit 管理をユーザーに
   強います。
5. **ネットワークアクセスを仮定しない。** `research.py` と
   `sync_notion.py` のみネットワークにアクセスできます。
6. **`sudo` や elevated permissions を要求しない。**
7. **データベースを導入しない。** ツールが速度のために SQLite が必要
   と思うなら、答えはより良い markdown インデックスです。
8. **TODO コメントを実装として出荷しない。** `raise NotImplementedError`
   のスタブ関数は `embed.py` でのみ許容されます。

---

## 13 · 関連仕様(Related Specs)

- `docs/architecture/execution-layer.md` — Layer 3(hooks)と Layer 4
  (これらの tools)の設計根拠。これを最初に読む。
- `references/hooks-spec.md` — shell hook 契約。hooks はトリガー時の
  強制、tools はバッチメンテナンス。
- `references/data-model.md` — tools が読み書きする型付きデータシェイプ
  (Decision、Task、Project など)。
- `references/adapter-github.md` — レコードが markdown + YAML
  frontmatter + git commit にマップされる方法。
- `pro/compliance/2026-04-19-court-start-violation.md` — execution layer
  を動機づけた incident。Python tools だけではそれを防げなかった
  (それは hook layer の仕事)が、もう半分を閉じる: LLM は積極的に
  state をメンテナンスしない。

---

**END**
