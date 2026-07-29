# Model-Tier Retirement Design

Date: 2026-07-12

Status: design-only. This document records the retirement plan. The actual repository changes are intentionally deferred to the follow-up code issue.

## Decision

Life OS must not prescribe or constrain model choice. The user chooses the model for the active session, and all Life OS subagent and maintenance work inherits that session model.

The v1.10.0 model-dispatch and tier machinery is retired in full. This includes the model dispatch policy, agent `model:` bindings, scenario `min_model_tier:` claims, `/run-eval --tier`, the generated tier matrix, and release gates that block on model-tier grounds.

## Rationale

The tier machinery contradicts the user model-autonomy principle in two ways:

1. Twenty-four agent files under `agents/*.md` pin a `model:` frontmatter field. Those bindings override or imply an override of the user's session choice: 23 agents bind `opus`, and 1 agent binds `sonnet`.
2. Scenario `min_model_tier:` claims plus the `docs/evals/tier-matrix.md` release gate assert that Life OS can decide which model tier is sufficient for a task and block releases when that tier claim fails.

That design was useful for degradation-safety experiments, but it makes Life OS a model policy engine. The owner decision on 2026-07-12 supersedes it: the system may describe what happened in a session, but it must not select, require, downgrade, or gate work by model tier.

## Full Retirement Inventory

Inventory verified by repository scan on 2026-07-12.

### Delete retired policy specs

Delete all three copies of the model dispatch policy:

- `references/model-dispatch-policy.md`
- `i18n/zh/references/model-dispatch-policy.md`
- `i18n/ja/references/model-dispatch-policy.md`

### Strip scenario tier claims

Remove `min_model_tier:` frontmatter from these 8 scenarios:

- `evals/scenarios/v1.10-bulk-ingest.md`
- `evals/scenarios/v1.10-maintenance-ledger.md`
- `evals/scenarios/v1.10-multi-window.md`
- `evals/scenarios/v1.8.7-b5-evals-required.md`
- `evals/scenarios/v1.8.7-e9-status-line.md`
- `evals/scenarios/v1.9-migration-correctness.md`
- `evals/scenarios/council-debate.md`
- `evals/scenarios/router-triage.md`

### Remove tier eval flow

Update `.claude/commands/run-eval.md`:

- Remove the `--tier <judgment|execution|batch>` argument flow.
- Remove section 3, "Tier selection".
- Remove tier-run output naming and summary fields.
- Remove the matrix regeneration contract.
- Keep normal scenario execution at the user's session/default model.

### Remove release tier gate

Update `.claude/commands/verify-release.md`:

- Remove check 12, "Degradation-safety tier gate".
- Renumber the output summary to 11 checks.
- Remove references to `references/model-dispatch-policy.md`, `min_model_tier:`, and `docs/evals/tier-matrix.md`.

Update `.claude/commands/verify-release-and-watch.md`:

- Remove tier-matrix references.
- Renumber any release-check list from 12 checks to 11 checks.

### Delete generated tier artifact

Delete:

- `docs/evals/tier-matrix.md`

This file is a generated artifact for the retired tier axis.

### Remove agent model bindings

Remove the `model:` frontmatter field from all 24 files under `agents/*.md`, so subagents inherit the user's session model:

- `agents/advisor.md` - `model: opus`
- `agents/archiver.md` - `model: opus`
- `agents/auditor.md` - `model: opus`
- `agents/concept-lookup.md` - `model: opus`
- `agents/council.md` - `model: opus`
- `agents/dispatcher.md` - `model: opus`
- `agents/execution.md` - `model: opus`
- `agents/finance.md` - `model: opus`
- `agents/governance.md` - `model: opus`
- `agents/growth.md` - `model: opus`
- `agents/gwt-arbitrator.md` - `model: opus`
- `agents/hippocampus.md` - `model: opus`
- `agents/infra.md` - `model: opus`
- `agents/knowledge-extractor.md` - `model: opus`
- `agents/memory-keeper.md` - `model: sonnet`
- `agents/monitor.md` - `model: opus`
- `agents/narrator.md` - `model: opus`
- `agents/people.md` - `model: opus`
- `agents/planner.md` - `model: opus`
- `agents/retrospective.md` - `model: opus`
- `agents/reviewer.md` - `model: opus`
- `agents/router.md` - `model: opus`
- `agents/soul-check.md` - `model: opus`
- `agents/strategist.md` - `model: opus`

### Clean active references

Clean references to retired model-tier machinery from:

- `references/agent-spec.md`
- `i18n/zh/references/agent-spec.md`
- `i18n/ja/references/agent-spec.md`
- `references/maintenance-ledger-spec.md`
- `i18n/zh/references/maintenance-ledger-spec.md`
- `i18n/ja/references/maintenance-ledger-spec.md`
- `hosts/CLAUDE.md`
- `hosts/AGENTS.md`
- `hosts/GEMINI.md`
- `agents/dispatcher.md`
- `docs/user-guide/making-decisions/reading-the-summary-report.md`

For mirrored references, keep `## ` section counts aligned across English, Chinese, and Japanese copies after the cleanup.

### Update hard-rule index if needed

Inspect `references/hard-rules-index.md`.

The current v1.10.0 section lists `references/model-dispatch-policy.md` and describes host model-binding lines as host references. Remove or rewrite those entries as part of the code issue.

If any line containing the literal `HARD RULE` marker is removed from a counted source file, update the per-host counts table in `references/hard-rules-index.md` in the same change. Do not change counts for role-local markers unless the index's counting method is intentionally expanded.

## History Is Never Rewritten

Do not edit historical release records merely to erase v1.10.0 tier mentions. These files keep their historical text:

- `CHANGELOG.md`
- `i18n/zh/CHANGELOG.md`
- `i18n/ja/CHANGELOG.md`
- `docs/reference/version-history.md`
- `_meta/release-notes/`

Historical docs may continue to mention `model-dispatch-policy`, `min_model_tier`, and `tier-matrix` as records of what shipped at that time.

## Drift Protection

Register these retired tokens in `.claude/commands/check-spec-drift.md`:

- `model-dispatch-policy`
- `min_model_tier`
- `tier-matrix`

Any hit in an active file is forbidden-token drift after the retirement code issue lands.

Explicit exemptions:

- `CHANGELOG.md`
- `i18n/*/CHANGELOG.md`
- `docs/reference/version-history.md`
- `_meta/release-notes/`
- `docs/design/model-tier-retirement.md`

The retirement doc is exempt because it is the design record for this deletion. Historical release records are exempt because history is not rewritten.

## Execution Order For The Code Issue

Use one single-topic merged commit for the retirement implementation.

1. Delete the three model-dispatch policy files and `docs/evals/tier-matrix.md`.
2. Strip all 8 scenario `min_model_tier:` fields.
3. Remove all 24 `model:` frontmatter fields from `agents/*.md`.
4. Remove the `/run-eval --tier` flow and generated matrix contract.
5. Remove `/verify-release` check 12 and tier-matrix watch references; renumber summaries to 11 checks.
6. Clean active references in specs, hosts, dispatcher, and user guide docs.
7. Update `references/hard-rules-index.md` if host HARD RULE marker counts changed.
8. Add the retired tokens and exemptions to `/check-spec-drift`.

Do not bump versions, create tags, publish release notes, or modify historical changelog text in this code issue.

## Verification Plan

After the code issue changes are made:

1. Run a repo-wide grep for retired tokens:

   ```bash
   rg -n "model-dispatch-policy|min_model_tier|tier-matrix" .
   ```

   The only remaining hits should be exempted historical files and `docs/design/model-tier-retirement.md`.

2. Verify there are no remaining agent model bindings:

   ```bash
   rg -n "^model:" agents/*.md
   ```

   Expected result: no matches.

3. Verify mirrored reference section counts remain aligned for every surviving mirrored file touched by the retirement:

   ```bash
   rg -n "^## " references/agent-spec.md i18n/zh/references/agent-spec.md i18n/ja/references/agent-spec.md
   rg -n "^## " references/maintenance-ledger-spec.md i18n/zh/references/maintenance-ledger-spec.md i18n/ja/references/maintenance-ledger-spec.md
   ```

   English, Chinese, and Japanese counts must match for each mirrored spec family.

4. Run `/check-spec-drift`.

   Expected result: pass, with no forbidden-token findings outside the explicit exemptions.

5. Confirm the implementation diff remains single-topic and contains no version bump, tag, release-note publication, or historical changelog edits.
