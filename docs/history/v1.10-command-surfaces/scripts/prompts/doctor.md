# User-invoked prompt · Life OS Doctor (natural-language health check)

> ROUTER reads this prompt when the user asks whether Life OS is installed,
> ready, broken, misconfigured, or how to begin. This is an internal workflow
> template, not a user-facing command requirement.

## Trigger keywords

ROUTER matches these inline. Do not ask the user to type a slash command.

- 中文: `检查 Life OS` / `检查一下 LifeOS` / `现在能不能正常用` / `刚装好` / `带我开始` / `帮我开始` / `帮我自检` / `帮我修一下配置` / `为什么没保存`
- English: `check Life OS` / `is Life OS working` / `I just installed Life OS` / `walk me through starting` / `health check` / `diagnose Life OS` / `fix my setup`
- 日本語: `Life OS を確認` / `正常に使えるか確認` / `インストールしたばかり` / `始め方を案内` / `設定を直して`

## Goal

Give the user a one-screen answer to:

1. Can Life OS run here?
2. What directory am I in: system repo, second-brain, or project repo?
3. Is the second-brain reachable?
4. Is git sync healthy enough?
5. Are host-specific subagents available?
6. What should the user say next?

Doctor is read-only by default. It may propose repairs, but must not write,
delete, move, commit, push, or edit configuration unless the user explicitly
asks to repair and confirms the concrete action.

## Operating rules

- Natural language is primary. `/doctor` is not required and may not exist.
- Do not launch `retrospective`, `archiver`, PLANNER, REVIEWER, domains,
  COUNCIL, or STRATEGIST from Doctor unless the user explicitly asks to proceed.
- Do not run destructive commands. Never suggest `rm -rf` as an agent action.
- Use existing host tools only: Read, Glob, Grep, Bash for read-only inspection,
  and Write only after explicit repair confirmation.
- Keep output short. The user needs next steps, not a full audit dump.
- If you need the user to choose, present numbered choices. Use subletters only
  inside a choice that has suboptions.

## Checks

### 1. Detect current directory type

Inspect the current working directory:

- Life OS system repo if it contains `SKILL.md`, `agents/`, and `themes/`.
- second-brain if it contains `meta/` and `projects/`.
- project repo if it contains `.git/` but not the Life OS system markers.
- unknown directory otherwise.

Report this as `Directory`.

### 2. Locate Life OS skill root

Check likely roots for `SKILL.md` + `agents/router.md`:

- current directory
- `$HOME/.claude/skills/life_OS`
- `$HOME/.claude/skills/life-os`
- `$HOME/.codex/skills/life_OS`
- `$HOME/.codex/skills/life-os`
- `.agents/skills/life_OS`
- `.agents/skills/life-os`

Report `Skill root: found/missing` and the version from `SKILL.md` if found.

### 3. Check host readiness

Detect host from available files/context:

- Claude Code: `.claude/commands/` exists or user is in Claude Code.
- Gemini / Antigravity: `.agents/skills/` or `hosts/GEMINI.md` path is in use.
- Codex: `AGENTS.md` / `hosts/AGENTS.md` path is in use.

For Claude Code only, check whether native Task wrappers likely exist:

- `$HOME/.claude/agents/lifeos-retrospective.md`
- `$HOME/.claude/agents/lifeos-archiver.md`
- `$HOME/.claude/agents/lifeos-router.md`

If wrappers are missing, say: `Run /install-agents --refresh once in Claude Code`.
Do not present this as the daily user path; it is setup plumbing.

### 4. Check second-brain reachability

Find second-brain by:

- current directory if it is already a second-brain
- `meta/config.md` if current dir has one
- project-local config references if documented by the current repo
- otherwise mark `Second-brain: not found yet`

If found, check for:

- `.git/`
- `meta/`
- `projects/`
- `areas/`
- `wiki/`
- `inbox/`
- `archive/`

Missing optional folders are warnings, not blockers, unless `meta/` and
`projects/` are both missing.

### 5. Check git sync health

Run read-only git checks in the relevant repo:

```bash
git status --short --branch
git remote -v
```

Classify:

- `ready`: git repo exists and status is readable.
- `local-only`: git repo exists but no remote.
- `attention`: dirty worktree, branch divergence, or unreadable status.
- `blocked`: not a git repo and the user expected sync.

Do not pull, commit, or push during Doctor.

### 6. Produce answer

Use this exact shape:

```text
🩺 Life OS Doctor
Status: ready | needs setup | needs attention | blocked

Directory: <system repo | second-brain | project repo | unknown>
Skill root: <path | missing> · version <x.y.z | unknown>
Second-brain: <path | not found | local-only>
Git sync: <ready | local-only | needs attention | blocked>
Host: <Claude Code | Gemini | Codex | unknown> · subagents <ready | setup needed | unknown>

What this means:
- <1-3 bullets max>

Recommended next step:
1. <best next action in natural language>
2. <fallback or setup action if needed>
3. <optional advanced/setup command only if truly relevant>
```

The recommended next step should be phrased as something the user can say, for
example:

- `我刚装好 Life OS，帮我创建 second-brain 并开始。`
- `上朝`
- `检查一下当前配置，然后带我开始。`
- `帮我修一下配置。`

## Repair mode

If the user explicitly asks to repair:

1. Show the exact changes first.
2. Ask for numbered confirmation if there is more than one repair path.
3. Only perform idempotent, scoped changes after confirmation.
4. After repair, rerun the relevant Doctor checks and report before/after.

Safe repair examples:

- create missing second-brain folders after user confirms
- rerun `/install-agents --refresh` when Claude wrappers are missing
- help the user add a GitHub remote by drafting exact commands

Unsafe repair examples:

- deleting caches, worktrees, or directories
- force-pushing
- editing unrelated project files
- running migration prompts without a preview

## Final step · Maintenance ledger stamp (v1.10.0)

Per `references/maintenance-ledger-spec.md`: upsert this job's row in
`meta/maintenance-ledger.md` — create the file with its standard header if
missing; if a row for this job exists, replace it in place, otherwise insert
keeping alphabetical order. Never duplicate a row.

`| doctor | on-demand | <today YYYY-MM-DD, from a real date command — no fabrication> |`
