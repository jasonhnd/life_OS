---
description: 个人方法论库管理（创建 / 更新 method 候选；archiver Phase 2 自动来源）— 100% LLM
argument-hint: create <name> | update <name> | list
allowed-tools: Read, Write, Edit, Glob, Grep
---

# /method · 方法论库管理 (v1.8.1 · zero-python)

> **⚠️ Backup mode.** 主要路径是 archiver Phase 2 退朝时自动检测 method
> candidate 并 create/update。这个命令是给"我想现在立刻 seed 一个具体
> method"的备份。详见 `pro/CLAUDE.md` → Auto-Trigger Rules → Method
> auto-create。

User invoked: `/method $ARGUMENTS`

## v1.8.1 zero-python 改造

之前 (v1.8.0 之前) 这个 prompt 调 `python -m tools.skill_manager`。
v1.8.1 把那个 .py 文件删了, 你现在用 LLM 直接做所有工作 — Read /
Write / Glob / Grep。

## 你要做的

### 子命令 `list` (默认 — 无参数也按 list 处理)

1. `Glob` 模式 `_meta/methods/**/*.md` 列出所有 method 文件
2. 对每个文件 `Read` 头 30 行抽 frontmatter (`title:` / `description:`
   / `last_modified:`)
3. 同时 `Grep` 整个 second-brain (`projects/**` + `areas/**` +
   `_meta/journal/**`) 数每个 method 被引用次数 (用 method id 或
   wikilink `[[method-X]]` 当 query)
4. 输出表:
   ```
   | method | description | last modified | refs |
   |---|---|---|---|
   | <name> | <one line> | <YYYY-MM-DD> | <N> |
   ```

### 子命令 `create <name>`

1. Slug: lowercase kebab-case, ≤ 50 chars
2. 检查 `_meta/methods/<domain>/<slug>.md` 是否已存在 (Glob); 已存在
   → 提示 user "已存在, 用 update 还是换 slug?"
3. 如果新 method 跨 domain, 让 user 选 domain (从现有 `_meta/methods/`
   下一级目录列表里挑, 或新建)
4. `Write` 文件, 用以下 frontmatter 模板:
   ```yaml
   ---
   title: "<one-line title>"
   description: "<≤ 80 chars 用途说明>"
   created: <YYYY-MM-DD>
   last_modified: <YYYY-MM-DD>
   status: tentative   # tentative | confirmed | deprecated
   triggers: []        # 什么场景触发用这个 method
   inputs: []          # 用之前需要什么信息
   outputs: []         # 用之后产出什么
   refs: []            # 引用的 wiki entries (wikilinks)
   ---

   # <title>

   ## When to use
   <2-3 行触发条件>

   ## Steps
   1. ...
   2. ...
   3. ...

   ## Failure modes
   - <这个 method 什么时候失效>

   ## Related
   - [[wiki/<domain>/<entry>]]
   ```
5. 报告: `✏️ 已创建 method: <name>。路径: _meta/methods/<domain>/<slug>.md`

### 子命令 `update <name>`

1. `Glob` 找到 `_meta/methods/**/<name>*.md` (允许部分匹配)
2. 多个匹配 → 让 user 选; 0 个匹配 → 提示 "没找到, 是不是要 create?"
3. `Read` 当前内容
4. 询问 user 改什么 (Steps 加一步? Failure modes 加一条? status 升
   tentative→confirmed?)
5. `Edit` 文件, 同时 bump `last_modified` 到今天
6. 报告: `🔧 已更新 method: <name>。修订时间: <YYYY-MM-DD HH:MM>`

## Method vs Skill 区分

- **method** = 你的个人决策方法论（"接单边界判断法"、"早朝节律检查表"）
- **skill** = Claude Code 平台 skill 包（这个 lifeos repo 本身就是一个 skill）

`/method` 管前者; skill 管理在 Claude Code 自己的 `/skills` 里。

## Anti-pattern

- 不要把单次决策当 method — method 必须是可复用的判断框架
- 不要 method 跟 wiki 混用 — wiki 是知识沉淀 (what), method 是判断流程 (how)
- 不要在主 context 调 `python -m tools.skill_manager` — 该 .py 在 v1.8.1 已删
