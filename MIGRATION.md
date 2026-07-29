# Migrating to Life OS v1.11

v1.11 is an architectural break: `SKILL.md` becomes the sole universal runtime
authority, and fixed commands, agent chains, lifecycle rituals, and Git
requirements are retired.

Migration of the Life OS product never authorizes inspection or modification of
a real second-brain.

## What remains compatible

- Existing v1.9 and v1.10 Markdown data remains readable.
- Existing directory names and record frontmatter may remain as they are.
- Legacy phrases and slash-command names may still be understood as natural
  language intent.
- Git-backed second-brains continue to work.
- Existing agent names remain available as optional perspectives.

No bulk rewrite is required for v1.11.

## What changed

| Before v1.11 | v1.11 |
|---|---|
| Universal behavior distributed across skill, hosts, agents, and specs | `SKILL.md` is the sole authority |
| Fixed orchestration and lifecycle stages | Model-selected method |
| Closed agent registry | Optional templates plus ad hoc roles |
| Command- and prompt-first capabilities | Natural-language capabilities |
| Git repository treated as the persistence backend | Explicitly bound local Markdown directory |
| Pull, commit, or push tied to lifecycle language | Git actions only when requested or included in scope |
| Procedure-based validation | Outcome- and evidence-based verification |

Retired command, prompt, spec, and eval surfaces remain under `docs/history/`
for provenance. They are not current instructions.

## Product update

Update the Life OS files using the installation mechanism appropriate to your
host: a host skill registry, a local copy, or a repository checkout are all
valid mechanics.

After updating:

1. confirm that the host can read the root `SKILL.md`;
2. remove any host configuration that still treats an archived command or
   prompt as mandatory;
3. do not run historical migration prompts automatically;
4. start with a normal natural-language request.

Git may be used to update a repository checkout, but Git is not a product
runtime requirement.

## Second-brain binding

Full Mode requires one user-approved local Markdown directory.

- Select the exact directory yourself.
- State whether access is read-only or read/write.
- Do not bind the Life OS development repository.
- Do not infer a binding from `.git`, `SOUL.md`, or familiar folder names.
- Do not search other directories for a second-brain.

Without a binding, continue in Conversation-Only Mode. The model may help, but
it must not claim durable persistence.

## Optional data migration

Request a structural migration only when you actually want one. A responsible
migration should:

- identify the exact bound target;
- preview material changes;
- preserve user-authored content and unrelated structure;
- select recovery evidence proportionate to the risk;
- work without Git;
- verify changed records and report anything not migrated.

Git history may be useful recovery evidence, but a backup copy, scoped export,
or another local preservation method may be more appropriate. The model chooses
the method based on the task and available capabilities.

Installation, update, start, review, save, done, end, and adjourn never imply a
bulk migration.

## Legacy host wrappers

Old slash commands and installed agent wrappers are optional compatibility
surfaces at most. Missing wrappers must lead to direct-model fallback rather
than product failure.

No v1.11 capability requires a command file under `.claude/commands/` or a
fixed prompt under `scripts/`.

## Release boundary

Changing local files, committing, pushing, opening a pull request, tagging, and
publishing a release are separate actions. Perform only the actions included in
the current request and verify each external mutation independently.
