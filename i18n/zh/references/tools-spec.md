---
translated_from: references/tools-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
---

# Python Tools · 契约规范（Python Tools · Contract Specification）

> Life OS 执行栈的第 4 层。Shell hooks（第 3 层）让 HARD RULE 真的"硬"起来；
> Python tools 让系统自主运转。本文档是 `tools/` 下每个工具的权威契约。
>
> 参考：`docs/architecture/execution-layer.md`（设计动机）、
> `references/data-model.md`（工具操作的数据类型）、
> `references/adapter-github.md`（磁盘文件格式）。

---

## 1 · 目的（Purpose）

Python tools 操作用户 second-brain markdown 文件，负责那些不适合在
Claude Code session 内执行的批处理与后台任务。一个 session 是同步的、
交互的、受限于用户注意力的。second-brain 需要一些长时间、系统性
（触及每个文件而不依赖 LLM 创造性）、无 LLM（纯解析 + YAML 生成 +
markdown I/O）的维护。

按用户决策，所有工具**本地**运行，从 Claude Code Bash 工具或手动调用。
无 GitHub Actions、无 VPS cron、无外部 API 调用。机器归用户所有；
second-brain 是一个本地目录。

工具是**可选的**。新 Life OS 用户即使从不安装 Python，在 Claude Code
内依然拥有完整的决策引擎体验。工具添加的是维护自动化，而不是核心功能。

---

## 2 · 运行时（Runtime）

**Python 3.11+** 与 **uv** 作为包管理器与运行器（用户决策 #15）。

uv 是依赖、virtualenv、调用的单一事实来源。用户不用手动激活 virtualenv。
每个工具的调用形式是：

```bash
uv run tools/{tool_name}.py [args]
# 或通过统一 CLI：
uv run life-os-tool {command} [args]
```

`life-os-tool` 二进制由 `uv sync` 通过 `pyproject.toml` 的
`[project.scripts]` 安装，根据第一个位置参数分派到 `tools/` 下相应模块。

**为什么是 uv**：解析与安装比 pip 快，处理 Python 版本钉死，产出可复现
lockfile。新用户克隆仓库，跑 `uv sync`，每个工具都能用——不用再答
"你 venv 激活了吗"这种支持问题。

---

## 3 · 目录结构（Directory Structure）

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

`embed.py` 作为占位存在——v1.7 不带语义 embedding（用户决策 #3）；
文件记录理由并指向 `search.py` 作为 v1.7 替代方案。

---

## 4 · 设计原则（Design Principles）

不可协商的不变量。任何工具违反一条都过不了 review。

1. **markdown 输入、markdown 输出。** 永远不把 second-brain 数据转成
   JSON、CSV 或 SQLite。工具可以在 stdout 上临时吐 JSON 供管道拼接，
   但持久状态一律是 markdown。

2. **幂等。** 工具跑两次，第二次的输出应与第一次相同。`reindex.py`
   永不追加重复项。`migrate.py` 标记已应用的 migration。`backup.py`
   同日重跑也安全。

3. **v1.7 不需要 API key。** LLM 工作留在 Claude Code session 里。
   若工具需要"智能"（例如 `search.py` 排序），它只做机械部分，把语义
   判断交回给下一个 session 的子 agent。

4. **单一职责。** 一个工具，一件事。组合通过调用多个工具完成，绝不
   通过合并职责。

5. **退出码 0 成功，1 错误。** 标准 Unix。`--dry-run` 模式成功 dry run
   时退出 0。

6. **YAML frontmatter 作为元数据。** 用 `python-frontmatter` 解析。
   永远不手写 YAML 解析器。Schema 定义在 `references/data-model.md`。

7. **默认安全。** 没有显式 flag 时工具不删文件。`reconcile.py --fix`
   是 opt-in。`backup.py` 没 `--prune` 时不会轮转。拿不准时先打印
   计划，要求 `--apply`。

---

## 5 · 公共库契约（Common Library Contract · `tools/lib/second_brain.py`）

所有工具依赖的共享库。把解析、path globbing、类型分派统一放在这里，
避免重复。

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

写方法在**记录级不可变**：调用方构造新 dataclass；库不原地修改实例。
写入使用原子的 temp-file-then-rename。

---

## 6 · 十二个工具契约(Twelve Tool Contracts)

每个工具规定：用途、调用、输入、输出、副作用、退出码、运行时预算、
触发模式。触发模式：

- **on-demand** —— 用户敲命令
- **archiver-called** —— 由 archiver 在 adjourn Phase 4 调用
- **retrospective-called** —— 由 retrospective 在 session 开始时调用
- **manual** —— 用户直接跑（每周或每月）
- **one-time** —— 每次安装 / 升级时一次

### 6.1 `reindex.py` — Compile Session Index(编译 session 索引)

扫描 `_meta/sessions/*.md`，产出 `_meta/sessions/INDEX.md`，按日期
降序每个 session 一行。

```bash
uv run tools/reindex.py [--verbose]
```

- **输入**：`_meta/sessions/` 下所有 session 摘要文件
- **输出**：`_meta/sessions/INDEX.md`（原子覆写）
- **副作用**：无
- **退出码**：`0` 成功，`1` I/O 错误或 frontmatter 不可读
- **运行时**：1000 个 session 下 < 5 秒
- **触发**：retrospective Mode 0（主要）；批量导入后用户手动。**不是 archiver**
  —— 根据 `references/session-index-spec.md` §10 反模式，编译是
  retrospective 的职责（把编译拆在 archiver + retrospective 之间，两个
  平台并发关闭 session 时会产生竞态条件）

INDEX.md 文件头包含
`<!-- generated by tools/reindex.py — do not edit by hand -->`。

### 6.2 `reconcile.py` — Integrity Check(完整性检查)

四项检查：orphan 文件、broken wikilink、缺失 YAML frontmatter、
schema 违规。

```bash
uv run tools/reconcile.py [--fix] [--verbose]
```

- **输入**：second-brain 根下所有 markdown
- **输出**：`_meta/reconcile-report-{YYYY-MM-DD}.md`。同日重跑文件被
  **覆写**（幂等）：报告是当前状态快照，不是历史日志。历史报告保存在
  git 里，不靠时间戳后缀。
- **`--fix`**：插入缺失的 frontmatter 默认值；把 orphan 移到
  `archive/orphans/`；从不删除。重跑安全——已修复的文件跳过。
- **退出码**：`0` 干净或已全部修复；`1` 仍有无法修复项
- **运行时**：5000 个文件 30 秒
- **触发**：用户每周；retrospective 可在 Mode 0 调用
- **幂等**：是——同一棵树跑两次产出同样的报告，第二次不做写入

`--fix` 只处理明显情况（缺 `last_modified`、缺 `id`、orphan 清理）。
判断题留给用户或子 agent。

### 6.3 `stats.py` — Usage & Quality Statistics(使用量与质量统计)

跨 session、eval-history、snapshot、SOUL 的周期聚合。用于自审的
markdown 报告。

```bash
uv run tools/stats.py [--period month|quarter|year] [--since YYYY-MM-DD] [--output FILE]
```

- **输入**：`_meta/sessions/`、`_meta/eval-history/`、
  `_meta/snapshots/`、`SOUL.md`
- **输出**：默认 stdout markdown。带 `--output FILE` 写到路径
  （便于管道进 `_meta/self-review-{YYYY-MM}.md`）。
- **默认周期**：若没给 `--period` 也没给 `--since`，默认 `--period month`
  覆盖最近 30 天。
- **报告项**：session 数、平均 `overall_score`、domain 分布、SOUL 趋势、
  DREAM 触发频率、前 3 concept tag、eval-history 维度平均分
- **退出码**：`0` 成功（包括空周期——打印"no data"但退 0）；`1` I/O 错误
- **运行时**：一年数据 < 10 秒
- **触发**：手动，通常按月

仅描述性。stats.py 只算数；解释交给用户或 retrospective 子 agent。

### 6.4 `research.py` — Background Web Fetch(后台网页抓取)

抓某主题，把 HTML 清洗成 markdown，追加带日期的笔记到 `inbox/`。

```bash
uv run tools/research.py "日本永驻新政策" [--depth 3] [--max-pages 10]
```

- **输入**：无（执行 HTTP 抓取）
- **输出**：`inbox/research-{YYYY-MM-DD}-{topic-slug}.md`
- **Topic slug**：由查询 ASCII 转写推导（CJK 用拼音）+ 小写 + 加连字符。
  无法转写的非 ASCII 查询用 SHA-1 哈希前缀
  （`inbox/research-{date}-{hash8}.md`）。
- **副作用**：通过 `httpx` 联网；用 `urllib.robotparser`（stdlib）
  遵守 `robots.txt`；user agent 设为
  `LifeOS-research/1.7 (+local-tool)`
- **`--depth N` 语义**：**从种子搜索结果起的跟链深度**。`--depth 0`
  = 仅搜索结果页。`--depth 1`（默认）= 把每条头部结果作为页面抓取。
  `--depth 2` = 再跟一层那些页面的外链。受 `--max-pages`（默认 10）
  限制，以约束运行时与带宽。
- **退出码**：`0` 成功；`1` 抓取失败（写部分文件并在 frontmatter 打
  `incomplete: true` 标，让下个 session 知道不可信）
- **运行时**：受 `--depth × --max-pages` 约束；默认值（1×10）下
  在体面连接上通常 30 秒以内
- **触发**：用户手动（异步意图捕获）

v1.7 发简单实现：`httpx.get` + `markdownify` 转换器，**无 LLM 摘要**
（用户决策 #16：工具内不用外部 LLM API）。更深的多源研究不在 v1.7 范围。

### 6.5 `daily_briefing.py` — Today's Briefing(今日简报)

从 SOUL、DREAM journal、active project、inbox、最近 eval-history
生成"今天什么重要"。

```bash
uv run tools/daily_briefing.py
```

- **输入**：`SOUL.md`、DREAM journal、`projects/`、`inbox/`、
  eval-history
- **输出**：stdout markdown（retrospective 嵌入其简报）
- **退出码**：`0` 总是，包括 second-brain 为空
- **运行时**：< 3 秒
- **触发**：retrospective 在 Mode 0 的 session 开始时调用，不调度。
  按用户决策，无 cron；简报在用户出现时才生成。

纯数据聚合。retrospective 子 agent 决定把什么放到前台。

### 6.6 `backup.py` — Archive Second-Brain(归档 second-brain)

把 second-brain 快照成带时间戳的 tarball。

```bash
uv run tools/backup.py [--dest /path] [--gpg KEY_ID]
```

- **输入**：整个 second-brain 根
- **输出**：`{dest}/{YYYY-MM-DD}.tar.gz`（或带 `--gpg` 的 `.tar.gz.gpg`）
- **副作用**：按设计写到 second-brain 之外
- **退出码**：`0` 成功；`1` 写错误或 gpg key 缺失
- **运行时**：500 MB 下 30 秒
- **触发**：用户手动（建议每周）

默认 `--dest` 是 `~/second-brain-backups/`。保留手动；自动
`--prune 30d` flag 不在 v1.7 范围。

### 6.7 `migrate.py` — v1.6.2a → v1.7 Schema Migration(模式迁移)

一次性迁移。v1.6.2a 把决策存在 `_meta/journal/`；v1.7 引入
`_meta/sessions/`、`_meta/concepts/`、`_meta/snapshots/`、
`_meta/eval-history/`、`_meta/methods/`。此工具回填新布局。

```bash
uv run tools/migrate.py --from v1.6.2a --to v1.7 [--dry-run]
```

- **输入**：已有 `_meta/journal/`（回填的事实来源）、`SOUL.md`
  （只读——synth snapshot 输入）、`wiki/`（只读——concept 锚点证据）、
  `user-patterns.md`（不动）
- **回填范围**：最近 **3 个月** 的 journal（用户决策 #7）。更旧的条目
  留在 `_meta/journal/` 不动。这个窗口对所有迁移目标统一——见下面
  逐目标规则。
- **逐目标规则**（每个目标遵守自己的权威规范）：
  - `_meta/sessions/{session_id}.md` + `INDEX.md` —— 合成逐 session 摘要
    （best-effort frontmatter，v1.7 之前的字段为 null）。默认
    `platform: claude`，从 journal mtime 推导 session-id。
    见 `references/session-index-spec.md` §9。
  - `_meta/concepts/**` —— 跑 6 准则 + 隐私过滤器流水线。
    `activation_count ≥ 3` 从 `_tentative/` 提升到 `{domain}/`，
    状态为 `status: confirmed`；`≥ 10` 提升为 `canonical`。边权
    来自共现，上限 10。见 `references/concept-spec.md` §Migration。
  - `_meta/snapshots/soul/**` —— 扫 journal 里的 `🔮 SOUL Delta` 块，
    产出 `provenance: synthetic` frontmatter 的合成快照。3 个月窗口
    （对齐）。见 `references/snapshot-spec.md` §Migration。
  - `_meta/methods/_tentative/**` —— 从语言模式（"approach"、"pattern"、
    "framework"、"流れ"、"やり方"、"手順"）里抽取前 5 个候选方法。
    全以 `status: tentative` 开始，永不自动晋升。见
    `references/method-library-spec.md` §15。
- **明确不迁移**：
  - `_meta/eval-history/` —— **不回填**。v1.7 第一天清零起步。
    见 `references/eval-history-spec.md` §11。
  - `SOUL.md`、`wiki/`、`user-patterns.md` —— 作为合成输入被读，永不修改。
- **输出日志**：`_meta/cortex/bootstrap-status.md`（canonical；被
  concept-spec 与 snapshot-spec 交叉引用）。
- **副作用**：写新文件；不删旧文件；`--with-backup` 可选触发 `backup.py`
- **LLM-free**：基于规则的文件名与 frontmatter 匹配；隐私过滤器用和
  archiver Phase 2 相同的正则 + LLM 流水线
- **幂等**：重跑会覆写编译后的索引，不会复制 concept 或 session
- **退出码**：`0` 成功；`1` 解析错误（跳过的文件被记录）
- **运行时**：3 个月 60 秒
- **触发**：v1.7 升级时一次性
- **`--dry-run`**：打印计划但不写

### 6.8 `search.py` — Cross-Session Search(跨 session 搜索)

返回最可能含答案的前 N 个 session。

```bash
uv run tools/search.py "我要不要辞职" [--top N]
```

- **输入**：`_meta/sessions/INDEX.md`（快路径），然后相关 session
  文件；argv 上给查询
- **输出**：stdout 排名列表（path、snippet、score）
- **退出码**：`0` 总是（空结果合法）
- **运行时**：1000 个 session 下 < 3 秒
- **触发**：用户手动（on-demand）

v1.7 实现是 **grep + 元数据排名**，不是语义搜索。

**排名公式**（确定性，无 LLM）：

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

`recency_boost_days` 在 `.life-os.toml` 的
`[search] recency_boost_days = 90` 可配置。打平时新者优先。

语义搜索按用户决策 #3 不在范围内。需要语义排序时，用户在 Claude Code
里调用 hippocampus 子 agent。

### 6.9 `export.py` — Format Conversion(格式转换)

把 second-brain 内容导出为可移植格式。

```bash
uv run tools/export.py --format pdf --scope projects/passpay
uv run tools/export.py --format html --scope wiki
uv run tools/export.py --format json --scope _meta/sessions
uv run tools/export.py --format anki --scope _meta/concepts
```

- **输入**：scope 目录或文件 pattern
- **输出**：`exports/{scope-slug}-{YYYY-MM-DD}.{ext}`
- **格式**：
  - `pdf` —— 通过 `pandoc`（外部二进制；要求 `pandoc ≥ 3.0`）
  - `html` —— 自包含（内联 CSS、无外部资源）；用带脚注 + 表格扩展的
    `markdown-it-py`
  - `json` —— 平坦数组；每元素 `{frontmatter: {...}, body: "..."}`
  - `anki` —— 通过 `genanki` 的 `.apkg`。**按类型字段映射**：
    - Concept：**Front** = `canonical_name` + `aliases`；**Back** =
      正文 + `outgoing_edges` 表（按权重前 5）
    - Method：**Front** = `name`；**Back** = `summary` + `## Steps`
      小节
    - Wiki：**Front** = 标题（结论）；**Back** = Reasoning +
      Applicable-When 小节
    - Session summary：**Front** = `subject`；**Back** = Key Decisions
      + Outcome
- **退出码**：`0` 成功；`1` 若缺 pandoc / 缺 genanki / scope 为空
- **运行时**：每 100 个文件 30 秒
- **触发**：用户手动

### 6.10 `seed.py` — New-User Bootstrap(新用户引导)

为新用户创建一个空-但-合法的 second-brain。

```bash
uv run tools/seed.py --path ~/second-brain
```

- **输入**：目标目录路径
- **输出**：填充了 `SOUL.md` 骨架、`.life-os.toml` 占位、
  `projects/example-project/index.md`、`_meta/sessions/`、
  `_meta/concepts/`、`_meta/snapshots/`、`_meta/eval-history/`、
  `inbox/`、`wiki/`（各带 `.gitkeep`）以及带建议条目的 `.gitignore`
  的目录
- **副作用**：跑 `git init` 并创建初始 commit
- **退出码**：`0` 成功；`1` 若目标路径已存在且非空
- **运行时**：< 2 秒
- **触发**：一次性，安装时由用户跑

### 6.11 `sync_notion.py` — Notion Fallback Sync(Notion 兜底同步)

当 archiver 会话内的 Notion sync（Phase 4）失败时——MCP 断开、瞬时
错误、限流——在 session 外重试。

```bash
uv run tools/sync_notion.py [--retry] [--since YYYY-MM-DD] [--verbose]
```

- **输入**：`_meta/STATUS.md`、active project、`_meta/eval-history/`、
  Notion sync log
- **输出**：通过 Notion HTTP API 更新 Notion 页面；条目追加到
  `_meta/notion-sync-log.md`
- **传输**：使用**官方 `notion-client` Python 包**（Notion REST API
  over HTTPS）。这**不是** LLM API 调用——Notion API 是普通的
  database API，与 Life OS v1.6.2a archiver Phase 4 机制一致（后者
  也通过 MCP 在 active session 中跟 Notion 通话）。Python 工具直接
  讲相同的底层 API，这样它可以在 Claude Code session 外运行。
- **token 解析**（优先级：CLI > env var > config）：
  1. `--notion-token` CLI flag
  2. `NOTION_TOKEN` 环境变量（推荐：launchd `EnvironmentVariables`
     或 macOS Keychain）
  3. `~/second-brain/.life-os.toml` 的 `[notion]` 段：
     ```toml
     [notion]
     token_env_var = "NOTION_TOKEN"  # name of env var holding token
     workspace_id = "..."
     ```
- **workspace 解析**：工具读 `_meta/config.md` 的 `[notion]` 段获取
  workspace / database ID；绝不硬编码。
- **对用户决策 #16("v1.7 无外部 API")的澄清**：该决策范围是
  **LLM provider API**（OpenAI、Anthropic HTTP、第三方 embedding
  服务）。Notion 是自 v1.6.2a 起已在用的用户数据存储平台；Python
  工具跟 Notion API 通话等价于 v1.6.2a archiver 跟 Notion MCP
  通话——同一能力，不同传输。
- **退出码**：`0` 全部同步；`1` 任一页失败；`2` 鉴权失败或 token
  缺失；`3` 网络不可达
- **运行时**：受 Notion 限流（每 API key 3 req/sec）约束；一周更新
  通常 < 60 秒
- **幂等性**：每页由 Notion 页面 `life_os_id` 属性中存的 Life OS 侧 ID
  （session_id、decision slug 等）upsert。重跑同步相同数据但不重复
  页面。
- **触发**：用户手动，archiver 报告 sync 失败时

### 6.12 `embed.py` — v1.7 不在范围(Out of Scope for v1.7)

语义 embedding 在 v1.7 **不在范围**（用户决策 #3 —— 无 embedding、
无 vector DB）。文件只作为占位存在，打印通知后 exit 0，确保
`uv run tools/embed.py` 以干净方式失败，而不是静默。v1.7 用 LLM-judgment
检索（见 `references/hippocampus-spec.md`）和元数据 + grep 排名
（见 `search.py` §6.8）替代。

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

## 7 · 依赖(Dependencies)

通过 `pyproject.toml` 管理。uv 做解析与锁定。

**核心**：`python-frontmatter`（YAML 解析）、`pyyaml`（引擎）、`rich`
（终端输出）、`pathlib`（stdlib）。

**可选（按工具）**：`httpx` + `markdownify`（`research.py`）、
`jinja2` + `markdown-it-py`（`export.py`）、`genanki`（`export.py --format anki`）、
`notion-client`（`sync_notion.py`）。

**明确不使用**：

- `openai`、`anthropic` —— **LLM provider** API。LLM 工作属于 Claude Code
  session，而不是批处理脚本。用户决策 #16。
  （Notion API 是数据存储 API，不是 LLM API —— `notion-client`
  被 `sync_notion.py` 使用，见 §6.11 澄清。）
- `sqlite3`、`psycopg`、任何数据库 —— second-brain 是 markdown + git。
- `celery`、`rq`、任何任务队列 —— 工具同步运行。
- `requests` —— `httpx` 覆盖相同表面；一个 HTTP 库就够。

---

## 8 · 配置(Configuration)

每用户配置在 `~/second-brain/.life-os.toml`：

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

由 `tools/lib/config.py` 加载。所有工具从这单一模块导入；不得散落
`os.path.expanduser` 调用。

**优先级**：CLI flag > env var > `.life-os.toml` > 默认值。环境变量
前缀 `LIFE_OS_`（例 `LIFE_OS_BACKUP_DEST`）。必填字段缺失时工具
fail fast。

---

## 9 · 错误处理(Error Handling)

每个工具遵守同一契约：

- **未预期异常**：顶层捕获，打印类型与描述到 stderr。Exit 1。
- **验证错误**：打印到 stderr 并附修复提示。Exit 1。
- **空操作**：友好的一行摘要到 stdout。Exit 0。
- **`--verbose`**：日志级别调 DEBUG。所有日志走 stderr，让 stdout
  可供管道使用。
- **绝不静默吞**：连 `reconcile.py --fix` 也要把每项变更打出来。

---

## 10 · 测试(Testing)

每个工具在 `tools/tests/` 下有对应测试文件。测试用 `pytest`、
`tmp_path` fixture，以及 `tools/tests/fixtures/sample-brain/` 作为
最小真实 fixture。

覆盖率满足全局 80% 下限。关键路径（migrate、reconcile、reindex）
目标 90%+，因为那里的 bug 会污染用户数据。

约定：`test_{behavior}_when_{condition}` 命名；Arrange-Act-Assert
结构；绝不碰用户真实的 `~/second-brain/`（用 `SecondBrain(tmp_path)`）；
用 `respx` mock `httpx` 边界，用假 bridge mock MCP。

```bash
uv run pytest tools/tests/
```

---

## 11 · 安装(Installation)

从 repo 根：

```bash
uv sync       # creates .venv, resolves deps, installs life-os-tool
uv add <pkg>  # adds a dependency, updates pyproject.toml + uv.lock
```

`pyproject.toml` 与 `uv.lock` 原子提交。

### `pyproject.toml` 骨架

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

### `tools/cli.py` 分派示例

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

每个工具模块（`tools/reindex.py`、`tools/migrate.py` 等）导出
`def main(argv: list[str]) -> int`，解析自己的 flag 并返回退出码。
这种模式让每个工具独立可跑（`uv run tools/reindex.py --verbose`
也行），同时保留统一的 `life-os-tool <cmd>` 入口。

---

## 12 · 反模式(Anti-Patterns)

禁止事项，按严重性排序：

1. **不得硬编码用户路径。** 走 `tools/lib/config.py`。硬编码
   `/Users/...` 在其他机器和 CI 里都坏。
2. **不得写到配置的 second-brain 根之外。** 例外：`backup.py`（写到
   `backup_dest`）与 `export.py`（写到 `exports/`）。
3. **不得修改 `SKILL.md`、`pro/agents/` 或 `references/`。** 那些是
   Life OS 系统文件，不是用户数据。
4. **不得通过外部 API 跑 LLM 调用。** 用户已经有 Claude Code。添加
   `openai` 或 `anthropic` 客户端强迫用户管理 key、配额、限流，毫无收益。
5. **不得假设有网络。** 只有 `research.py` 和 `sync_notion.py` 可以
   访问网络。
6. **不得要求 `sudo` 或提升权限。**
7. **不得引入数据库。** 如果某个工具觉得它需要 SQLite 来提速，答案是
   一个更好的 markdown 索引。
8. **不得把 TODO 注释当成实现交付。** `raise NotImplementedError` 的
   stub 函数只在 `embed.py` 可接受。

---

## 13 · 相关规范(Related Specs)

- `docs/architecture/execution-layer.md` —— 第 3 层（hook）与第 4 层
  （本工具集）的设计动机。先读这个。
- `references/hooks-spec.md` —— shell hook 契约。hook 是触发时刻的
  强制；tool 是批量维护。
- `references/data-model.md` —— 工具读写的类型化数据形状（Decision、
  Task、Project 等）。
- `references/adapter-github.md` —— 记录如何映射到 markdown + YAML
  frontmatter + git commit。
- `pro/compliance/2026-04-19-court-start-violation.md` —— 促成执行层
  的事故。Python 工具单独无法阻止它（那是 hook 层的职责），但它们
  补上另一半：LLM 不会主动维护状态。

---

**END**

---

## 译注

- 本 spec 原文只描述 12 个工具（§6.1–§6.12），但实际 `tools/cli.py` 已注册 **16 个** subcommand —— 比 spec 多 4 个：`rebuild-session-index`、`rebuild-concept-index`、`extract`、`seed-concepts`。翻译按原文保持 12 工具结构；源 spec 需补 4 项或显式把它们列为"外围工具"。此差异已在本次翻译交付报告中作为 spec bug 候选上报。
- `orphan` = 孤立文件（无引用），`wikilink` = `[[...]]` 双方括号链接，`frontmatter` = Markdown 文件头的 YAML 元数据块；术语沿用 Obsidian 社区惯用写法。
- `dataclass / argparse / fixture / mtime / upsert / launchd / Keychain` 等技术术语保留英文。
- `session-id / topic-slug / workspace / database / rate limit / token` 保留英文，避免回译歧义。
- 章节序号中的 ` · `（中点）沿用英文原文格式（原文用 `·` 分隔章节号与标题）。
