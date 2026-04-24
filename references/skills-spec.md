---
status: draft-v1.7.1
---

# Skill Observability Spec

## 1. Purpose

Life OS 1.7.1 introduces **Skill Observability**, a docs-only contract for inspecting locally installed skills and plugin-provided skills. The purpose of this spec is to define the user-facing CLI surface, source priority, output shape, and integration expectations for a skill inventory briefing.

The inventory is intended to answer four operational questions:

- Which skills are currently active or locally available?
- Which installed skills have an upstream update available?
- Which installed skills appear stale because they have not been updated for more than 90 days?
- Which local metadata entries cannot be parsed reliably?

This spec does not define runtime skill loading, Cortex behavior, ROUTER routing behavior, or host-specific subagent behavior. In v1.7.1, ROUTER not integrated; Cortex not integrated.

## 2. Data Sources

Skill Observability reads local installation metadata in the following priority order:

1. `~/.claude/skills/*/SKILL.md` frontmatter (`name` / `version` / `description` / `triggers` / optional `installed-at`)
2. `~/.claude/plugins/*/plugin.json`
3. future `~/.claude/skills.lock` / `plugins.lock` not implemented in v1.7.1

When the same skill id appears in more than one source, the higher-priority source wins for active display and status calculation. Source priority is fixed as `skills/ > plugins/ > future lockfiles`.

If the same skill exists in both `~/.claude/skills/` and `~/.claude/plugins/`, the `skills/` record wins. The plugin record must still be visible as shadowed telemetry, and the plugin version must be marked `(shadowed by skills://<id>)`. Shadowed plugin records do not count as active skills, do not override the winning `skills://<id>` status, and do not introduce a fifth status value.

The implementation must treat corrupt or unparseable primary metadata as a data-source failure for that record. A data source is corrupt/unparseable when required metadata cannot be read, frontmatter cannot be parsed, JSON is invalid, the upstream cache file is corrupt/unparseable, or a record cannot be normalized into the CLI output schema. Runtime upstream failures are not data-source corruption.

The canonical output columns are:

`name | version | installed-at | source | upstream-latest | status | triggers-hint`

Status values use the following emoji labels:

- `🟢 current / local`
- `🟡 update available`
- `🔴 stale (>90 days)`
- `❓ check failed`

## 3. CLI Contract

The Skill Observability CLI exposes four commands:

- `life-os-tool skills list`
- `life-os-tool skills check`
- `life-os-tool skills info <name>`
- `life-os-tool skills stale`

All commands support the common params `--format {markdown,json}` default markdown, `--offline`.

`life-os-tool skills list` prints the installed skills table using the canonical output columns. In markdown mode, the command should produce a human-readable table. In json mode, it should produce an array of normalized records with fields corresponding to the canonical columns.

`life-os-tool skills check` checks local metadata against available upstream metadata when online checks are available. With `--offline`, the command must not perform network access and must report the same columns as online output using only local metadata plus cache evidence.

`life-os-tool skills info <name>` prints detailed metadata for one skill, including its source, version, description, triggers hint, installed timestamp when available, upstream latest version when available, and current status.

`life-os-tool skills stale` lists skills with status `🔴 stale (>90 days)` and exits according to the stale status rules below.

Exit codes are fixed and complete:

- `0` ok/no update
- `1` update available
- `2` stale (>90 days)
- `3` data source corrupt/unparseable

Aggregate priority is fixed as `3 > 2 > 1 > 0`. When multiple records or conditions are present, the highest-priority exit code wins. Exit `3` is reserved for data source corrupt/unparseable only. A graceful upstream timeout or live upstream check failure marks affected records as `❓ check failed`, but does not by itself exit `3`.

The retrospective briefing may include one line:

`🧰 Skills: N active · M update · K stale`

ADVISOR optional only when >3 stale. ROUTER not integrated; Cortex not integrated.

## 4. Output Contract

The canonical markdown table columns are fixed:

`name | version | installed-at | source | upstream-latest | status | triggers-hint`

`--format {markdown,json}` defaults to markdown for every command. Markdown output should be optimized for human briefing and may include explanatory text around the canonical table. JSON output must be machine-readable and must preserve the same normalized record shape represented by the canonical columns.

Status values are fixed:

- `🟢 current / local`
- `🟡 update available`
- `🔴 stale (>90 days)`
- `❓ check failed`

`triggers-hint` is the comma-separated first three trigger strings in source order, for example `"start, 上朝, begin"`. If fewer than three triggers exist, include the available triggers. If no triggers are available, use `-`.

`source: local://...` marks `🟢 current / local` and is not checked against upstream. Local-only records must still appear in list and info output when their metadata can be parsed.

`--offline` output has parity with online output: it uses the same columns in markdown and the same keys in JSON. In offline mode, `upstream-latest` must show `? (cached Xd ago)` when cached evidence exists, or `? (no cache)` when no cache exists.

Shadowed plugin rows remain visible but are not active. Because the schema has no `shadowed-by` column, the required marker is appended to the plugin `version` value as `(shadowed by skills://<id>)`; the `status` field remains one of the fixed status values.

Markdown online example:

```markdown
| name | version | installed-at | source | upstream-latest | status | triggers-hint |
|---|---:|---|---|---:|---|---|
| cabinet-session | 1.7.1 | 2026-04-21 | skills://cabinet-session | 1.7.1 | 🟢 current / local | start, 上朝, begin |
| daily-review | 1.2.0 | 2026-03-10 | skills://daily-review | 1.3.0 | 🟡 update available | review, 复盘, close |
| old-capture | 0.9.0 | 2025-12-01 | skills://old-capture | 0.9.0 | 🔴 stale (>90 days) | capture, inbox, clip |
| focus-mode | 1.0.0 | 2026-04-10 | skills://focus-mode | 1.0.0 | 🟢 current / local | focus, flow, deep work |
| focus-mode | 0.8.0 (shadowed by skills://focus-mode) | 2026-03-05 | plugins://focus-mode | 1.0.0 | 🟢 current / local | focus, deep work, flow |
| scratchpad | local | ❓ | local://scratchpad | - | 🟢 current / local | note, scratch, jot |
| broken-feed | 2.0.0 | 2026-04-01 | skills://broken-feed | ? | ❓ check failed | sync, feed, ingest |
```

Markdown offline example:

```markdown
| name | version | installed-at | source | upstream-latest | status | triggers-hint |
|---|---:|---|---|---:|---|---|
| cabinet-session | 1.7.1 | 2026-04-21 | skills://cabinet-session | ? (cached 3d ago) | ❓ check failed | start, 上朝, begin |
| inbox-helper | 0.4.0 | 2026-04-02 | skills://inbox-helper | ? (no cache) | ❓ check failed | inbox, capture, triage |
| scratchpad | local | ❓ | local://scratchpad | - | 🟢 current / local | note, scratch, jot |
```

JSON online example:

```json
[
  {
    "name": "cabinet-session",
    "version": "1.7.1",
    "installed-at": "2026-04-21",
    "source": "skills://cabinet-session",
    "upstream-latest": "1.7.1",
    "status": "🟢 current / local",
    "triggers-hint": "start, 上朝, begin"
  },
  {
    "name": "daily-review",
    "version": "1.2.0",
    "installed-at": "2026-03-10",
    "source": "skills://daily-review",
    "upstream-latest": "1.3.0",
    "status": "🟡 update available",
    "triggers-hint": "review, 复盘, close"
  },
  {
    "name": "focus-mode",
    "version": "0.8.0 (shadowed by skills://focus-mode)",
    "installed-at": "2026-03-05",
    "source": "plugins://focus-mode",
    "upstream-latest": "1.0.0",
    "status": "🟢 current / local",
    "triggers-hint": "focus, deep work, flow"
  },
  {
    "name": "scratchpad",
    "version": "local",
    "installed-at": "❓",
    "source": "local://scratchpad",
    "upstream-latest": "-",
    "status": "🟢 current / local",
    "triggers-hint": "note, scratch, jot"
  }
]
```

JSON offline example:

```json
[
  {
    "name": "cabinet-session",
    "version": "1.7.1",
    "installed-at": "2026-04-21",
    "source": "skills://cabinet-session",
    "upstream-latest": "? (cached 3d ago)",
    "status": "❓ check failed",
    "triggers-hint": "start, 上朝, begin"
  },
  {
    "name": "inbox-helper",
    "version": "0.4.0",
    "installed-at": "2026-04-02",
    "source": "skills://inbox-helper",
    "upstream-latest": "? (no cache)",
    "status": "❓ check failed",
    "triggers-hint": "inbox, capture, triage"
  }
]
```

The retrospective briefing line is fixed:

`🧰 Skills: N active · M update · K stale`

`N active` counts parseable active skills, including local-only skills. Shadowed plugin records do not increment `N active`. `M update` counts skills with status `🟡 update available`. `K stale` counts skills with status `🔴 stale (>90 days)`.

## 5. Upstream Check

`life-os-tool skills check` may perform upstream checks unless `--offline` is supplied. Upstream checks use anonymous API only; authenticated tokens, write APIs, and user-account APIs are out of scope for v1.7.1.

Supported upstream endpoints are fixed:

- `GET https://api.github.com/repos/<owner>/<repo>/releases/latest`
- `GET https://registry.npmjs.org/<pkg>/latest`
- `GET https://pypi.org/pypi/<pkg>/json`

The upstream cache path is fixed:

`~/.cache/life-os/skills-upstream.json`

The cache TTL is 24h. Fresh cached data at or below 24h old may be treated as reliable and may be used instead of a network request. Stale cached data older than 24h is stale-cache-as-evidence: it may be shown in output and may support `🟡 update available` if it reports a newer version than the installed version, but it must not prove `🟢 current / local`. If stale cache is the only available upstream evidence and it does not establish an update, mark the record `❓ check failed`.

`--offline` must not perform network access. Offline output must keep the same columns as online output. For upstream-backed records, `upstream-latest` must be `? (cached Xd ago)` when any cache entry exists, or `? (no cache)` when no cache entry exists. Local-only records may use `-` for `upstream-latest` because no upstream check exists.

The upstream timeout is 5s per skill. A timeout, malformed live upstream response, unsupported upstream source, or live upstream parsing failure is a graceful check failure: mark the affected record `❓ check failed`, continue processing other records, and do not exit `3` for that reason alone. Exit `3` is used only for data source corrupt/unparseable, such as invalid local frontmatter, invalid `plugin.json`, a corrupt/unparseable `~/.cache/life-os/skills-upstream.json`, or a record that cannot be normalized into the output schema.

Staleness calculation uses this baseline order:

1. Use `installed-at` from `SKILL.md` frontmatter when present.
2. If `installed-at` is missing, use the filesystem mtime of the primary metadata file, such as `SKILL.md` or `plugin.json`.
3. If neither value is available, set `installed-at` to `❓` and do not classify the record as stale from age alone.

Status calculation:

- `🟢 current / local` when the local version is current against reliable upstream data, or when `source: local://...` marks a local-only skill.
- `🟡 update available` when reliable upstream data or stale-cache-as-evidence reports a newer latest version than the installed version.
- `🔴 stale (>90 days)` when the installed skill has not been updated for more than 90 days according to the staleness baseline.
- `❓ check failed` when upstream status cannot be reliably parsed or checked and no higher-priority stale/update status is established for that record.

`life-os-tool skills list` should not require live network access. It may use local metadata and cache data. `life-os-tool skills stale` may use the same status calculation as `skills check`, but with output filtered to `🔴 stale (>90 days)`.

## 6. Integration Boundaries

This is a docs-only v1.7.1 contract. It does not require code, tests, scripts, workflow changes, Makefile changes, `pyproject` changes, `SKILL.md` changes, or `pro/agents` changes.

Skill Observability may be surfaced as a retrospective briefing line:

`🧰 Skills: N active · M update · K stale`

ADVISOR optional if >3 stale. ADVISOR may provide hygiene recommendations for stale skills, but does not own status calculation.

ROUTER no integration. Cortex no integration.

## 7. Anti-patterns

Skill Observability is observability only. It reports local installation state, upstream comparison state, and stale metadata state; it must not become a routing, execution, memory, or recovery mechanism.

Forbidden integrations:

- ROUTER task selection based on skills status. `life-os-tool skills list`, `life-os-tool skills check`, `life-os-tool skills info <name>`, and `life-os-tool skills stale` may inform a human briefing, but they must not alter ROUTER task selection or execution paths.
- Narrator wrapping. Skill Observability output is operational telemetry, not a Summary Report claim stream, and does not receive narrator `signal_id` citation wrapping.
- Failure handler chain. Exit codes from the skills commands are CLI contract signals only; they must not invoke Life OS failure handlers, workflow recovery, AUDITOR emergency escalation, or automatic remediation.
- Cortex writes. Skill Observability must not write to `_meta/sessions/`, `_meta/concepts/`, `_meta/snapshots/`, GWT signal stores, SOUL, wiki, methods, strategic map, or eval history.
- Hidden network writes. Upstream checks may read only the fixed anonymous endpoints; they must not publish telemetry, mutate registries, authenticate to user accounts, or modify upstream resources.
- Status reinterpretation. Do not replace the fixed status emoji vocabulary: `🟢 current / local`, `🟡 update available`, `🔴 stale (>90 days)`, `❓ check failed`.
- Exit-code drift. Do not redefine the fixed exit codes: `0` ok/no update, `1` update available, `2` stale (>90 days), `3` data source corrupt/unparseable.

The only allowed system-facing surface is the retrospective briefing line:

`🧰 Skills: N active · M update · K stale`

ADVISOR may recommend cleanup when `K stale` is greater than 3, but this is advisory hygiene guidance only. ADVISOR must not own status calculation, suppress command output, trigger execution, or write Cortex artifacts.

## 8. Migration

v1.7.1 migration is documentation-first and non-invasive. Existing skills and plugins remain valid unless their metadata cannot be parsed into the canonical output columns:

`name | version | installed-at | source | upstream-latest | status | triggers-hint`

Recommended migration sequence:

1. Run `life-os-tool skills list --format {markdown,json}` to inspect local parseability and display shape.
2. Run `life-os-tool skills check --offline` to verify local metadata without network access.
3. Run `life-os-tool skills check` when online upstream checks are desired.
4. Run `life-os-tool skills stale` to isolate records with `🔴 stale (>90 days)`.
5. Run `life-os-tool skills info <name>` for any record that needs human inspection.

The data source priority remains fixed during migration:

1. `~/.claude/skills/*/SKILL.md` frontmatter (`name` / `version` / `description` / `triggers` / optional `installed-at`)
2. `~/.claude/plugins/*/plugin.json`
3. future `~/.claude/skills.lock` / `plugins.lock` not implemented in v1.7.1

During migration, `skills/` records shadow same-id `plugins/` records. Shadowed plugin versions must be marked `(shadowed by skills://<id>)` and must not count as active skills.

Upstream checks remain read-only and limited to the fixed anonymous endpoints:

- `GET https://api.github.com/repos/<owner>/<repo>/releases/latest`
- `GET https://registry.npmjs.org/<pkg>/latest`
- `GET https://pypi.org/pypi/<pkg>/json`

Migration must preserve the common params `--format {markdown,json}` and `--offline` for every command. `--offline` must prevent network access, keep output columns identical to online mode, and may rely only on local metadata plus cache evidence. The upstream cache path remains `~/.cache/life-os/skills-upstream.json` with a 24h TTL.

No migration step may require code edits, generated scripts, workflow changes, Makefile changes, `pyproject` changes, `SKILL.md` changes, or `pro/agents` changes. If an implementation later appears, it must conform to this spec rather than expanding the v1.7.1 docs-only boundary.

## 9. Versioning

This document is the v1.7.1 docs-only contract for Skill Observability. Version changes are governed by compatibility of the user-facing CLI and normalized output schema.

Patch-compatible changes may clarify wording, add examples, or document additional non-normative guidance without changing commands, params, exit codes, status values, data sources, upstream endpoints, cache semantics, or integration boundaries.

Minor-version changes are required for any additive CLI behavior, additional upstream endpoint, new output field, new diagnostic mode, or changed stale threshold. Additive behavior must keep the existing commands valid:

- `life-os-tool skills list`
- `life-os-tool skills check`
- `life-os-tool skills info <name>`
- `life-os-tool skills stale`

Major-version changes are required for any breaking change to:

- common params `--format {markdown,json}` and `--offline`
- exit codes `0` ok/no update, `1` update available, `2` stale (>90 days), `3` data source corrupt/unparseable
- status values `🟢 current / local`, `🟡 update available`, `🔴 stale (>90 days)`, `❓ check failed`
- canonical output columns
- data source priority and shadowing semantics
- upstream endpoints
- observability-only integration boundary

Until a later spec explicitly supersedes this document, Life OS hosts must treat Skill Observability as human-facing telemetry. It must not drive ROUTER task selection, narrator wrapping, failure handler chains, or Cortex writes.

## References

- `references/tools-spec.md` - broader Life OS surface and skills command overview
- `references/cortex-spec.md` - Cortex boundary; Skill Observability has no Cortex writes
- `references/narrator-spec.md` - narrator boundary; Skill Observability output is not narrator-wrapped
- `pro/AGENTS.md` - Codex host orchestration contract; this spec does not add host subagents
- `SKILL.md` - root Life OS behavior source; this spec does not modify runtime skill loading

**END**

## §Design Rationale

Skill Observability exists because Life OS can be extended by locally installed skills and plugin-provided companion tools, but those extensions should remain visible to the user instead of silently becoming part of the decision workflow. The archived companion-tools guidance treats external skills and tools as optional helpers around Life OS, not as replacements for ROUTER, Cortex, the 16-agent workflow, or the markdown-first source of truth.

The design therefore keeps observability additive. It answers inventory and hygiene questions: what is installed, where it came from, whether an upstream version appears newer, whether local metadata is stale, and which trigger hints may help a human recognize intended usage. These facts are useful in Start Session briefings, environment checks, migrations, and machine setup, but they must not mutate task selection, memory, or agent semantics.

The `triggers-hint` field is intentionally a hint, not a routing table. Archived user-facing docs describe it as a way to help users understand when a skill might be relevant; the spec keeps ROUTER and Cortex uninvolved so that skill metadata cannot become an implicit planning or memory substrate.

Skill status is also advisory by design. Update availability and stale metadata are hygiene signals that help users decide whether to reinstall, inspect, or ignore a skill. The system must not auto-update, auto-disable, or auto-remediate skills from these signals because local skills may be personal, experimental, pinned for compatibility, or intentionally offline.

The source-priority rule preserves predictable local control. A directly installed `skills://<id>` record wins over a plugin-provided record with the same id because explicit local installation is the clearest user intent. Shadowed plugin telemetry remains visible so the user can diagnose duplicates without expanding the active-skill set.

The cross-platform boundary follows the archived multi-platform architecture: shared skill and agent definitions should remain host-agnostic where possible, while host-specific behavior belongs in `pro/CLAUDE.md`, `pro/GEMINI.md`, and `pro/AGENTS.md`. Skill Observability may report local installation state on any host, but it must not introduce host-specific subagents or reinterpret platform orchestration.

## §Migration

When migrating older companion-tool documentation into the v1.7.1 spec set, keep product guidance and normative contract separate. User-facing recommendations for tools such as visual-design skills, document-conversion CLIs, or memory plugins belong in user-guide or companion-tool docs; `references/skills-spec.md` should retain only the Skill Observability contract and its integration boundaries.

`devdocs/human-docs-archive/2026-04-24/MIGRATION.md` Step 7 is useful historical evidence for local skill setup, especially the `~/.claude/skills/life_OS` installation path and reinstall flow. Treat those details as environment setup guidance, not as a cross-platform normative requirement. Claude-only install commands must not be generalized into Gemini or Codex behavior unless the relevant host orchestration file defines that behavior.

Migration from older docs should preserve these boundaries:

- No automatic skill updates.
- No ROUTER dispatch based on skill status.
- No Cortex reads or writes.
- No narrator wrapping.
- No failure-handler or recovery-chain integration.
- No new subagent semantics.
- No change to the fixed output columns, status vocabulary, exit codes, source priority, shadowing rule, or upstream endpoint list.

If an older doc describes a companion tool as useful for a Life OS task, migrate that description as advisory user guidance rather than as a requirement that the tool be installed. If an older doc describes a skill inventory or health check, map it to the four Skill Observability commands and the single retrospective briefing line defined above.

If future migration work needs richer origin context than the archived companion-tools and migration docs provide, use `devdocs/human-docs-archive/2026-04-24/docs/architecture/` as the historical architecture record, while keeping `references/*.md` authoritative for current contracts.
