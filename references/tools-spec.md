# Python Tools · Contract Specification

> ⚠️ **PARTIALLY LEGACY (v1.7-era) — see v1.8.0 deltas below**
>
> v1.8.0 R-1.8.0-011 ("Option A" pivot) replaced several Python tools with
> LLM-driven prompts. The deltas vs this document:
> - `tools/cli.py` (the `life-os-tool {cmd}` dispatcher) was **deleted**.
>   Tools now invoked directly via `python -m tools.<name>` — no dispatcher.
> - `tools/migrate.py` was **deleted**. Migration now runs via
>   `scripts/prompts/migrate-from-v1.6.md`.
> - `tools/memory.py`, `tools/session_search.py`, several maintenance python
>   tools were **deleted** and replaced by `scripts/prompts/<job>.md` files.
> - `setup-cron.sh`, `run-cron-now.sh`, all launchd plists were **deleted**.
>   All maintenance is user-invoked.
>
> Tools that DO still exist (canonical for v1.8.0): `approval`, `export`,
> `reconcile`, `research`, `search`, `seed`, `skill_manager`, `stats`,
> `sync_notion`, plus `tools/lib/*`.

> Layer 4 of the Life OS execution stack. Shell hooks (Layer 3) make HARD RULE
> truly hard; Python tools make the system run on its own. This document is the
> authoritative contract for every tool in `tools/`.
>
> Reference: `docs/architecture/execution-layer.md` (design rationale),
> `references/data-model.md` (types tools manipulate),
> `references/adapter-github.md` (file format on disk).

---

## 1 · Purpose

Python tools operate on the user's second-brain markdown files for batch
and background tasks that don't fit naturally inside a Claude Code
session. A session is synchronous, interactive, and bounded by the user's
attention. The second-brain needs maintenance that is long-running,
systematic (touching every file without LLM creativity), and LLM-free
(pure parsing + YAML generation + markdown I/O).

Per user decision, all tools run **locally**, invoked from the Claude
Code Bash tool or manually. No GitHub Actions, no cron-on-VPS, no
external API calls. The user owns the machine; the second-brain is a
local directory.

Tools are **optional**. A new Life OS user who never installs Python
still has the full decision-engine experience inside Claude Code. Tools
add maintenance automation, not core functionality.

---

## 2 · Runtime

**Python 3.11+** and **uv** as package manager and runner (user
decision #15).

uv is the single source of truth for dependencies, virtualenv, and
invocation. Users do not activate virtualenvs manually. Every tool is
invoked as:

```bash
# v1.8.0 (current): direct module invocation
uv run python -m tools.{tool_name} [args]

# Pre-v1.8.0 (REMOVED in R-1.8.0-011 — tools/cli.py dispatcher deleted):
# uv run life-os-tool {command} [args]
```

The `life-os-tool` console script and `tools/cli.py` dispatcher were
**removed in R-1.8.0-011**. Callers now invoke modules directly via
`python -m tools.<name>`. The `[project.scripts]` table in `pyproject.toml`
no longer registers the dispatcher entry.

**Why uv**: resolves and installs faster than pip, handles Python version
pinning, and produces reproducible lockfiles. New users clone the repo,
run `uv sync`, and every tool works — no "did you activate the venv?"
support burden.

---

## 3 · Directory Structure

```
tools/
├── __init__.py
│  (cli.py removed in R-1.8.0-011 — invoke modules directly)
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

`embed.py` exists as a placeholder — v1.7 ships without semantic
embeddings (user decision #3); the file documents the rationale and
points to `search.py` for the v1.7 alternative.

---

## 4 · Design Principles

Non-negotiable invariants. Any tool that violates one fails review.

1. **Markdown input, markdown output.** Never convert second-brain data
   into JSON, CSV, or SQLite. Tools may emit transient JSON on stdout
   for piping, but persistent state is always markdown.

2. **Idempotent.** Running a tool twice produces identical output on the
   second run. `reindex.py` never appends duplicates. `migrate.py`
   marks applied migrations. `backup.py` is safe to re-invoke same day.

3. **No API keys required in v1.7.** LLM work stays inside the Claude
   Code session. If a tool needs "intelligence" (e.g., `search.py`
   ranking), it does the mechanical part and hands semantic judgment
   back to a subagent in the next session.

4. **Single responsibility.** One tool, one job. Compose by invoking
   multiple tools, never by merging responsibilities.

5. **Exit code 0 success, 1 error.** Standard Unix. `--dry-run` modes
   exit 0 on a successful dry run.

6. **YAML frontmatter as metadata.** Use `python-frontmatter` for
   parsing. Never hand-roll YAML parsers. Schemas are defined in
   `references/data-model.md`.

7. **Safe by default.** No tool deletes files without an explicit flag.
   `reconcile.py --fix` is opt-in. `backup.py` never rotates without
   `--prune`. When in doubt, print the plan and require `--apply`.

---

## 5 · Common Library Contract (`tools/lib/second_brain.py`)

The shared library every tool depends on. Consolidating parsing, path
globbing, and type dispatch here avoids duplication.

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

Write methods are **immutable at the record level**: callers construct a
new dataclass; the library does not mutate instances. Writes use atomic
temp-file-then-rename.

---

## 6 · Twelve Tool Contracts

Each tool specifies: purpose, invocation, inputs, outputs, side effects,
exit codes, runtime budget, and trigger mode. Trigger modes:

- **on-demand** — user types a command
- **archiver-called** — invoked by archiver during adjourn Phase 4
- **retrospective-called** — invoked by retrospective at session start
- **manual** — user runs directly (weekly or monthly)
- **one-time** — once per install / upgrade

### 6.1 `reindex.py` — Compile Session Index

Scan `_meta/sessions/*.md`, emit `_meta/sessions/INDEX.md` with one row
per session sorted by date descending.

```bash
uv run tools/reindex.py [--verbose]
```

- **Input**: all session summary files under `_meta/sessions/`
- **Output**: `_meta/sessions/INDEX.md` (overwritten atomically)
- **Side effects**: none
- **Exit codes**: `0` success, `1` on I/O error or unreadable frontmatter
- **Runtime**: < 5 seconds for 1,000 sessions
- **Trigger**: retrospective Mode 0 (primary); user manual after bulk
  import. **NOT archiver** — compilation is retrospective's responsibility
  per `references/session-index-spec.md` §10 anti-pattern (splitting
  compile across archiver + retrospective produces race conditions when
  two platforms close sessions concurrently)

INDEX.md header includes
`<!-- generated by tools/reindex.py — do not edit by hand -->`.

### 6.2 `reconcile.py` — Integrity Check

Four checks: orphan files, broken wikilinks, missing YAML frontmatter,
schema violations.

```bash
uv run tools/reconcile.py [--fix] [--verbose]
```

- **Input**: all markdown under second-brain root
- **Output**: `_meta/reconcile-report-{YYYY-MM-DD}.md`. On same-day
  re-run the file is **overwritten** (idempotent): the report is a
  snapshot of current state, not a history log. Historical reports
  are kept in git, not via timestamp suffixes.
- **`--fix`**: inserts missing frontmatter defaults; moves orphans to
  `archive/orphans/`; never deletes. Safe to re-run — already-fixed
  files are skipped.
- **Exit codes**: `0` if clean or all fixed; `1` if unfixable remain
- **Runtime**: 30 seconds for 5,000 files
- **Trigger**: user weekly; retrospective may call during Mode 0
- **Idempotent**: yes — running twice on the same tree produces the
  same report and takes no write action the second time

`--fix` handles only obvious cases (missing `last_modified`, missing
`id`, orphan cleanup). Judgment calls are left to the user or a subagent.

### 6.3 `stats.py` — Usage & Quality Statistics

Per-period aggregates across sessions, eval-history, snapshots, SOUL.
Markdown report for self-review.

```bash
uv run tools/stats.py [--period month|quarter|year] [--since YYYY-MM-DD] [--output FILE]
```

- **Input**: `_meta/sessions/`, `_meta/eval-history/`,
  `_meta/snapshots/`, `SOUL.md`
- **Output**: stdout markdown (default). With `--output FILE` writes
  to path instead (for piping into `_meta/self-review-{YYYY-MM}.md`).
- **Default period**: if neither `--period` nor `--since` is given,
  defaults to `--period month` covering the last 30 days.
- **Reports**: session count, avg `overall_score`, domain distribution,
  SOUL trend, DREAM trigger frequency, top 3 concept tags,
  eval-history dimension averages
- **Exit codes**: `0` success (including empty period — prints "no
  data" but exits 0); `1` on I/O error
- **Runtime**: < 10 seconds for a year of data
- **Trigger**: manual, typically monthly

Descriptive only. stats.py computes numbers; interpretation is for the
user or retrospective subagent.

### 6.4 `research.py` — Background Web Fetch

Fetch a topic, clean HTML to markdown, append a dated note to `inbox/`.

```bash
uv run tools/research.py "日本永驻新政策" [--depth 3] [--max-pages 10]
```

- **Input**: none (performs HTTP fetches)
- **Output**: `inbox/research-{YYYY-MM-DD}-{topic-slug}.md`
- **Topic slug**: derived by ASCII-transliterating the query where
  possible (pinyin for CJK) + lowercasing + hyphenating. Non-ASCII
  queries that can't transliterate use a SHA-1 hash prefix
  (`inbox/research-{date}-{hash8}.md`).
- **Side effects**: network via `httpx`; respects `robots.txt` using
  `urllib.robotparser` (stdlib); user agent set to
  `LifeOS-research/1.7 (+local-tool)`
- **`--depth N` semantics**: **link-following depth from the seed
  search result**. `--depth 0` = search results page only. `--depth 1`
  (default) = fetch each top result as a page. `--depth 2` = also
  follow one layer of outbound links from those pages. Capped by
  `--max-pages` (default 10) to bound runtime and bandwidth.
- **Exit codes**: `0` success; `1` on fetch failure (writes a partial
  file with an `incomplete: true` frontmatter flag so the next session
  knows not to trust it)
- **Runtime**: bounded by `--depth × --max-pages`; at defaults (1×10)
  typically under 30s on decent connection
- **Trigger**: user manual (asynchronous intent capture)

v1.7 ships a simple implementation: `httpx.get` + `markdownify`
converter, **no LLM summarization** (user decision #16: no external
LLM APIs in tools). Deeper multi-source research is out of scope for v1.7.

### 6.5 `daily_briefing.py` — Today's Briefing

Generate "what matters today" from SOUL, DREAM journal, active projects,
inbox, recent eval-history.

```bash
uv run tools/daily_briefing.py
```

- **Input**: `SOUL.md`, DREAM journal, `projects/`, `inbox/`,
  eval-history
- **Output**: stdout markdown (retrospective embeds in its briefing)
- **Exit codes**: `0` always, even with empty second-brain
- **Runtime**: < 3 seconds
- **Trigger**: retrospective during Mode 0 at session start, not
  scheduled. Per user decision, no cron; briefings are generated when
  the user shows up.

Pure data aggregation. The retrospective subagent decides what to
foreground.

### 6.6 `backup.py` — Archive Second-Brain

Snapshot the second-brain as a timestamped tarball.

```bash
uv run tools/backup.py [--dest /path] [--gpg KEY_ID]
```

- **Input**: entire second-brain root
- **Output**: `{dest}/{YYYY-MM-DD}.tar.gz` (or `.tar.gz.gpg` with `--gpg`)
- **Side effects**: writes outside second-brain by design
- **Exit codes**: `0` success; `1` on write error or missing gpg key
- **Runtime**: 30 seconds for 500 MB
- **Trigger**: user manual (recommended weekly)

Default `--dest` is `~/second-brain-backups/`. Retention is manual; an
automatic `--prune 30d` flag is out of scope for v1.7.

### 6.7 `migrate.py` — v1.6.2a → v1.7 Schema Migration

One-time migration. v1.6.2a stored decisions in `_meta/journal/`; v1.7
introduces `_meta/sessions/`, `_meta/concepts/`, `_meta/snapshots/`,
`_meta/eval-history/`, `_meta/methods/`. This tool backfills the new
layout.

```bash
uv run tools/migrate.py --from v1.6.2a --to v1.7 [--dry-run]
```

- **Input**: existing `_meta/journal/` (source of truth for backfill),
  `SOUL.md` (read-only — synth snapshot input), `wiki/` (read-only —
  concept anchor evidence), `user-patterns.md` (untouched)
- **Backfill scope**: last **3 months** of journal (user decision #7).
  Older entries remain in `_meta/journal/` untouched. This window is
  uniform across all migration targets — see the per-target rules below.
- **Per-target rules** (each target honours its own authoritative spec):
  - `_meta/sessions/{session_id}.md` + `INDEX.md` — synthesises per-session
    summaries (best-effort frontmatter, null for pre-v1.7 fields).
    Defaults `platform: claude`, derives session-id from journal mtime.
    See `references/session-index-spec.md` §9.
  - `_meta/concepts/**` — runs the 6-criteria + privacy filter pipeline.
    `activation_count ≥ 3` promotes from `_tentative/` to `{domain}/`
    with `status: confirmed`; `≥ 10` promotes to `canonical`. Edge
    weights from co-occurrence, capped at 10. See
    `references/concept-spec.md` §Migration.
  - `_meta/snapshots/soul/**` — scans journal for `🔮 SOUL Delta` blocks,
    emits synthetic snapshots with `provenance: synthetic` frontmatter.
    3-month window (aligned). See `references/snapshot-spec.md` §Migration.
  - `_meta/methods/_tentative/**` — extracts top-5 candidate methods from
    language patterns ("approach", "pattern", "framework", "流れ", "やり方",
    "手順"). All start `status: tentative`, never auto-promoted. See
    `references/method-library-spec.md` §15.
- **Explicitly NOT migrated**:
  - `_meta/eval-history/` — **no backfill**. Starts fresh at v1.7 day one.
    See `references/eval-history-spec.md` §11.
  - `SOUL.md`, `wiki/`, `user-patterns.md` — read as inputs for synthesis,
    never modified.
- **Output log**: `_meta/cortex/bootstrap-status.md` (canonical; cross-
  referenced by concept-spec and snapshot-spec).
- **Side effects**: writes new files; does not delete old; optionally
  calls `backup.py` with `--with-backup`
- **LLM-free**: rule-based filename and frontmatter matching; privacy
  filter uses the same regex + LLM pipeline as archiver Phase 2
- **Idempotent**: re-running overwrites the compiled indices without
  duplicating concepts or sessions
- **Exit codes**: `0` success; `1` on parse error (skipped file logged)
- **Runtime**: 60 seconds for 3 months
- **Trigger**: one-time during v1.7 upgrade
- **`--dry-run`**: prints plan without writing

### 6.8 `search.py` — Cross-Session Search

Return top N sessions most likely to contain an answer.

```bash
uv run tools/search.py "我要不要辞职" [--top N]
```

- **Input**: `_meta/sessions/INDEX.md` (fast path), then relevant
  session files; query on argv
- **Output**: stdout ranked list (path, snippet, score)
- **Exit codes**: `0` always (empty results are valid)
- **Runtime**: < 3 seconds for 1,000 sessions
- **Trigger**: user manual (on-demand)

v1.7 implementation is **grep + metadata ranking**, not semantic search.

**Ranking formula** (deterministic, no LLM):

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

`recency_boost_days` is configurable in `.life-os.toml` under
`[search] recency_boost_days = 90`. Ties break by newer-first.

Semantic search is out of scope per user decision #3. For semantic
ranking, the user invokes the hippocampus subagent inside Claude Code.

### 6.9 `export.py` — Format Conversion

Export second-brain content into portable formats.

```bash
uv run tools/export.py --format pdf --scope projects/passpay
uv run tools/export.py --format html --scope wiki
uv run tools/export.py --format json --scope _meta/sessions
uv run tools/export.py --format anki --scope _meta/concepts
```

- **Input**: scope directory or file pattern
- **Output**: `exports/{scope-slug}-{YYYY-MM-DD}.{ext}`
- **Formats**:
  - `pdf` — via `pandoc` (external binary; requires `pandoc ≥ 3.0`)
  - `html` — self-contained (inline CSS, no external assets); uses
    `markdown-it-py` with footnote + table extensions
  - `json` — flat array; each element `{frontmatter: {...}, body: "..."}`
  - `anki` — `.apkg` via `genanki`. **Per-type field mapping**:
    - Concept: **Front** = `canonical_name` + `aliases`; **Back** =
      body + `outgoing_edges` table (top 5 by weight)
    - Method: **Front** = `name`; **Back** = `summary` + `## Steps`
      section
    - Wiki: **Front** = title (conclusion); **Back** = Reasoning +
      Applicable-When sections
    - Session summary: **Front** = `subject`; **Back** = Key Decisions
      + Outcome
- **Exit codes**: `0` success; `1` if pandoc missing / genanki missing
  / scope empty
- **Runtime**: 30 seconds per 100 files
- **Trigger**: user manual

### 6.10 `seed.py` — New-User Bootstrap

Create an empty-but-valid second-brain for a new user.

```bash
uv run tools/seed.py --path ~/second-brain
```

- **Input**: target directory path
- **Output**: directory populated with `SOUL.md` skeleton,
  `.life-os.toml` stub, `projects/example-project/index.md`,
  `_meta/sessions/`, `_meta/concepts/`, `_meta/snapshots/`,
  `_meta/eval-history/`, `inbox/`, `wiki/` (each with `.gitkeep`), and
  a `.gitignore` with recommended entries
- **Side effects**: runs `git init` and creates initial commit
- **Exit codes**: `0` success; `1` if target path exists and is non-empty
- **Runtime**: < 2 seconds
- **Trigger**: one-time, run by the user during install

### 6.11 `sync_notion.py` — Notion Fallback Sync

When archiver's in-session Notion sync (Phase 4) fails — MCP
disconnected, transient error, rate limit — retry outside the session.

```bash
uv run tools/sync_notion.py [--retry] [--since YYYY-MM-DD] [--verbose]
```

- **Input**: `_meta/STATUS.md`, active projects, `_meta/eval-history/`,
  Notion sync log
- **Output**: Notion pages updated via the Notion HTTP API; entries
  appended to `_meta/notion-sync-log.md`
- **Transport**: uses the **official `notion-client` Python package**
  (Notion REST API over HTTPS). This is NOT an LLM API call — Notion
  API is a plain database API, consistent with Life OS's v1.6.2a
  archiver Phase 4 mechanism (which also speaks to Notion, via MCP
  during an active session). The Python tool speaks the same
  underlying API directly so it can run outside a Claude Code session.
- **Token resolution** (precedence: CLI > env var > config):
  1. `--notion-token` CLI flag
  2. `NOTION_TOKEN` environment variable (recommended: launchd
     `EnvironmentVariables` or macOS Keychain)
  3. `[notion]` section of `~/second-brain/.life-os.toml`:
     ```toml
     [notion]
     token_env_var = "NOTION_TOKEN"  # name of env var holding token
     workspace_id = "..."
     ```
- **Workspace resolution**: tool reads `_meta/config.md` `[notion]`
  section for workspace / database IDs; never hardcoded.
- **Clarification on user decision #16 ("No external API in v1.7")**:
  that decision scopes to **LLM provider APIs** (OpenAI, Anthropic
  HTTP, third-party embedding services). Notion is a user data
  storage platform already in use since v1.6.2a; the Python tool
  speaking to Notion API is equivalent to v1.6.2a archiver speaking
  to Notion MCP — same capability, different transport.
- **Exit codes**: `0` all synced; `1` any page failed; `2` auth
  failure or missing token; `3` network unreachable
- **Runtime**: bounded by Notion rate limits (3 req/sec per API key);
  typically < 60 seconds for a week of updates
- **Idempotency**: each page is upserted by its Life OS-side ID
  (session_id, decision slug, etc.) stored in the Notion page's
  `life_os_id` property. Re-running syncs the same data without
  duplicating pages.
- **Trigger**: user manual, when archiver reports sync failure

### 6.12 `embed.py` — Out of Scope for v1.7

Semantic embeddings are **out of scope for v1.7** (user decision #3 — no
embeddings, no vector DBs). The file exists only as a placeholder that
prints a notice and exits 0, so `uv run tools/embed.py` fails cleanly
rather than silently. v1.7 uses LLM-judgment retrieval (see
`references/hippocampus-spec.md`) and metadata + grep ranking (see
`search.py` §6.8) instead.

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

## 7 · Dependencies

Managed via `pyproject.toml`. uv resolves and locks.

**Core**: `python-frontmatter` (YAML parsing), `pyyaml` (engine), `rich`
(terminal output), `pathlib` (stdlib).

**Optional (tool-specific)**: `httpx` + `markdownify` (`research.py`),
`jinja2` + `markdown-it-py` (`export.py`), `genanki` (`export.py --format anki`),
`notion-client` (`sync_notion.py`).

**Explicitly NOT used**:

- `openai`, `anthropic` — **LLM provider** APIs. LLM work belongs in
  the Claude Code session, not batch scripts. User decision #16.
  (Notion API is a data-storage API, not an LLM API — `notion-client`
  IS used by `sync_notion.py`, see §6.11 clarification.)
- `sqlite3`, `psycopg`, any database — second-brain is markdown + git.
- `celery`, `rq`, any job queue — tools run synchronously.
- `requests` — `httpx` covers the same surface; one HTTP library is
  enough.

---

## 8 · Configuration

Per-user config at `~/second-brain/.life-os.toml`:

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

Loaded by `tools/lib/config.py`. All tools import from this single
module; no scattered `os.path.expanduser` calls.

**Precedence**: CLI flags > env vars > `.life-os.toml` > defaults. Env
vars use prefix `LIFE_OS_` (e.g., `LIFE_OS_BACKUP_DEST`). Tools fail
fast if config is missing required fields.

---

## 9 · Error Handling

Every tool obeys the same contract:

- **Unexpected exceptions**: caught at top level, printed to stderr with
  type and description. Exit 1.
- **Validation errors**: printed to stderr with a fix hint. Exit 1.
- **No-op runs**: friendly one-line summary to stdout. Exit 0.
- **`--verbose`**: log level to DEBUG. All logging on stderr so stdout
  remains usable for piping.
- **Never silently swallow**: even `reconcile.py --fix` logs each change.

---

## 10 · Testing

Every tool has a corresponding test file under `tools/tests/`. Tests
use `pytest`, `tmp_path` fixtures, and
`tools/tests/fixtures/sample-brain/` as a minimal realistic fixture.

Coverage meets the global 80% minimum. Critical paths (migrate,
reconcile, reindex) aim for 90%+ because bugs there corrupt user data.

Conventions: `test_{behavior}_when_{condition}` naming;
Arrange-Act-Assert structure; never touch the user's real
`~/second-brain/` (use `SecondBrain(tmp_path)`); mock boundaries with
`respx` for `httpx` and a fake bridge for MCP.

```bash
uv run pytest tools/tests/
```

---

## 11 · Installation

From repo root:

```bash
uv sync       # creates .venv, resolves deps, installs life-os-tool
uv add <pkg>  # adds a dependency, updates pyproject.toml + uv.lock
```

Commit both `pyproject.toml` and `uv.lock` atomically.

### `pyproject.toml` skeleton

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

### `tools/cli.py` dispatch example

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

Every tool module (`tools/reindex.py`, `tools/migrate.py`, etc.) exports
`def main(argv: list[str]) -> int` that parses its own flags and
returns an exit code. This pattern keeps each tool independently
runnable (`uv run tools/reindex.py --verbose` works too) while
preserving a unified `life-os-tool <cmd>` entry point.

---

## 12 · Anti-Patterns

Forbidden, in order of severity:

1. **Do not hardcode user paths.** Go through `tools/lib/config.py`.
   Hardcoded `/Users/...` paths break on other machines and in CI.
2. **Do not write outside the configured second-brain root.**
   Exceptions: `backup.py` (writes to `backup_dest`) and `export.py`
   (writes to `exports/`).
3. **Do not modify `SKILL.md`, `pro/agents/`, or `references/`.** Those
   are Life OS system files, not user data.
4. **Do not run LLM calls via external APIs.** The user already has
   Claude Code. Adding `openai` or `anthropic` clients forces the user
   to manage keys, quotas, and rate limits for no gain.
5. **Do not assume network access.** Only `research.py` and
   `sync_notion.py` may access the network.
6. **Do not require `sudo` or elevated permissions.**
7. **Do not introduce a database.** If a tool thinks it needs SQLite
   for speed, the answer is a better markdown index.
8. **Do not ship TODO comments as the implementation.** Stub functions
   that `raise NotImplementedError` are acceptable only in `embed.py`.

---

## 13 · Related Specs

- `docs/architecture/execution-layer.md` — design rationale for Layer 3
  (hooks) and Layer 4 (these tools). Read this first.
- `references/hooks-spec.md` — shell hook contracts. Hooks are
  trigger-time enforcement; tools are batch maintenance.
- `references/data-model.md` — typed data shapes (Decision, Task,
  Project, etc.) that tools read and write.
- `references/adapter-github.md` — how records map onto markdown + YAML
  frontmatter + git commits.
- `pro/compliance/2026-04-19-court-start-violation.md` — the incident
  that motivated the execution layer. Python tools alone would not have
  prevented it (that is the hook layer's job), but they close the other
  half: LLMs don't proactively maintain state.

---

**END**
