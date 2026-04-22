---
translated_from: references/hooks-spec.md
translator_note: auto-translated 2026-04-22, 待人工校对
---

# Shell Hooks 契约规范(Shell Hooks Contract Specification · v1.7)

> 五个 shell hook 的权威契约,在运行时强制 Life OS HARD RULE 合规。每个 hook 都是自包含的 bash 脚本,通过 stdin JSON、stdout 文本、退出码与 Claude Code host 通信。仅 Bash + jq —— 不要 Python 运行时,不要非 stdlib 依赖。

---

## 1 · 目的(Purpose)

Shell hook 存在是因为文档不是强制。LLM 会漂移。2026-04-19 COURT-START-001 事故证明了在 markdown 文件里写 "HARD RULE" 并不会让规则变硬 —— orchestrator 自己能跳过 subagent 启动、伪造文件路径、在用户多轮之间把修正切片分开。Hook 在运行时抓这种漂移。

hook 在 LLM 上下文之外的子进程里运行。LLM 没法贿赂它、忘掉它、或绕开它讲道理。hook 触发时,它要么:

- 静默放行(exit 0)—— LLM 根本看不到 hook 跑过
- 注入 system reminder(exit 0 附 stdout)—— 文本作为权威被插进 LLM 上下文
- 阻止动作(exit 2 附 stderr)—— 工具调用被取消,LLM 被告知原因

本规范定义 v1.7 所需的五个 hook、它们的契约、正则表达式模式与违规日志机制。

---

## 2 · 平台支持(Platform Support)

**仅 Claude Code(v1.7)。** 这里描述的 hook 系统在 Anthropic 的 Claude Code CLI 中原生存在。Gemini CLI 与 Codex CLI 在 v1.7 不暴露等价 hook 表面 —— 它们回退到 prompt 级强制(SKILL.md HARD RULE 声明),没有运行时兜底。

当 Gemini / Codex 发布兼容 hook 规范后,同一套五个脚本可以注册到那里。在那之前,非 Claude Code host 上的 Life OS 只拿到第 1 层(文档)与第 2 层(subagent 隔离)。这在 `docs/architecture/execution-layer.md` 里有记录。

---

## 3 · Hook 系统架构(Hook System Architecture)

### 3.1 Claude Code hook 类型

hook 在 `~/.claude/settings.json` 的 `hooks` 下声明。四个事件有意义:

| 事件 | 触发时机 | 典型用途 |
|-------|---------------|-------------|
| `UserPromptSubmit` | LLM 处理每条用户消息之前 | 检测触发词、注入 HARD RULE |
| `PreToolUse` | 任何工具调用之前 | 验证参数、阻止危险路径 |
| `PostToolUse` | 任何工具调用之后 | 验证 LLM 是否真的做了它声称的事 |
| `Stop` | session 结束时 | 验证 Completion Checklist |

匹配按工具名(`PreToolUse` / `PostToolUse`)或通配符(`UserPromptSubmit` / `Stop`)。

### 3.2 Hook 机制

Claude Code 把每个 hook 作为子进程调用,向 stdin 写 JSON 上下文对象,把 stdout 读作注入的 `system_reminder`,把 stderr 读作面向用户的诊断(仅在 block 时显示),并检查退出码:

- `0` —— 放行。非空 stdout 变成 system reminder。
- `2` —— 阻止。工具调用被取消;stdout + stderr 作为阻止原因给 LLM。
- 其他任何值 —— hook 错误。Claude Code 记录并在不阻止的前提下继续。

### 3.3 输入 JSON schema

**`UserPromptSubmit`**:`{prompt, session_id, cwd}`
**`PreToolUse` / `PostToolUse`**:`{tool_name, tool_input, tool_result, session_id, cwd, recent_user_message}`
**`Stop`**:`{session_id, final_state, transcript_path}`

每个 hook 用 `jq -r` 解析,把值当不受信任的数据 —— 恶意 prompt 可能含 shell 元字符。

---

## 4 · 违规时严格阻止(Strict Block on Violation · 用户决策 #6)

hook 检测到 HARD RULE 违规时:

1. 以退出码 `2` 退出(取消工具调用或 prompt)
2. 向 stdout 写解释 —— 变成 LLM 必须读的 `system_reminder`
3. 向 `{compliance_path}/violations.md` 追加结构化一行(路径按 §6 自动检测)

LLM 随后可以正确重试。用户在终端看到阻止解释。违规留在 git 下。

**为什么严格阻止而不是告知:** COURT-START-001 证明了文档级 HARD RULE 会被无视。硬阻止强制重新规划。用户决策 #6。

---

## 5 · v1.7 的五个 Hook(The Five v1.7 Hooks)

所有 hook 脚本住在 Life OS skill 包内的 `scripts/hooks/`,安装时落到 `~/.claude/skills/life_OS/scripts/hooks/`。

### 5.1 `pre-prompt-guard.sh`

- **事件:** `UserPromptSubmit`,matcher `*`
- **用途:** 检测触发词;注入强制启动 subagent 的 HARD RULE。
- **解决:** COURT-START-001 —— ROUTER 在主上下文里跑 retrospective 的步骤。

**契约:** 从 stdin 解析 `prompt`。若匹配触发表,向 stdout 发出一个 `<system-reminder>` 并 exit 0。否则 exit 0 且无输出。此 hook 从不 exit 2 —— 它只注入指引。

**触发表:**

| 模式 | Subagent | 模式 |
|---------|----------|------|
| `上朝` / `start` / `begin` / `はじめる` / `開始` / `朝廷開始` / `閣議開始` | `retrospective` | Start Session |
| `退朝` / `adjourn` / `done` / `end` / `お疲れ` / `終わり` / `结束` | `archiver` | Adjourn 4-phase |
| `复盘` / `review` / `早朝` / `振り返り` / `レビュー` | `retrospective` | Review Mode |
| `朝堂议政` / `debate` / `討論` | `council` | 3-round debate |
| `quick` / `快速分析` / `クイック` | — | ROUTER Express |

**检测到 `上朝` 时 stdout 示例:**

```
<system-reminder>
HARD RULE · Trigger "上朝" detected.

Required output (exactly 2 lines):
Line 1: theme-appropriate greeting
Line 2: Agent tool call for retrospective Mode 0

You MUST:
- Read pro/agents/retrospective.md BEFORE the Agent call
- Launch(retrospective) as an independent subagent
- NOT execute any step of retrospective in main context
- NOT simulate subagent output

Any deviation = HARD RULE violation, logged to compliance/violations.md.
Precedent: COURT-START-001 (2026-04-19).
</system-reminder>
```

### 5.2 `post-response-verify.sh`

- **事件:** `PostToolUse`,matcher `Task|Bash|Write|Edit`
- **用途:** 验证 LLM 在触发词后真的启动了正确的 subagent。
- **解决:** ROUTER 声称"让我启动 retrospective"但随后直接跑 Bash / Read。

**契约:** 解析 `tool_name`、`tool_input`、`recent_user_message`。若 `recent_user_message` 匹配了某触发词且 `tool_name != Task`(或 `Task` 指向错误 subagent),记录违规并以纠正提醒 exit 2。否则 exit 0。

**检测规则:**

| 最近触发 | 期望工具 | 违规条件... |
|----------------|---------------|-----------------|
| `上朝` / `start` | `Task(retrospective)` | `Bash` 读 `_meta/`、对 config 执 `Read`、直接向 journal `Write` |
| `退朝` / `adjourn` | `Task(archiver)` | 任何 `git` 命令、向 `_meta/decisions/` `Write`、archiver 返回前调用 Notion MCP |
| `复盘` / `review` | `Task(retrospective)` | 未走 subagent 直接 `Read` `_meta/sessions/INDEX.md` |

### 5.3 `pre-write-scan.sh`

- **事件:** `PreToolUse`,matcher `Write|Edit`
- **用途:** 对即将写到 SOUL / wiki / concepts / user-patterns 的内容做快速正则扫描。
- **解决:** LLM 生成的内容含注入 payload(恶意或误伤)流到长期知识文件。

**契约:** 解析 `file_path` + `content`(Edit 时为 `new_string`)。若 `file_path` 在作用域集(`SOUL.md`、`wiki/**`、`_meta/concepts/**`、`user-patterns.md`)之外,exit 0 放行。在作用域内,跑 15-pattern 正则扫描 + 不可见 Unicode 扫描。匹配任一则记录违规,带 pattern flag 以 exit 2 退出。

此正则扫描是廉价的第一关。基于 LLM 的隐私检查(用户决策 #5)在 archiver 知识萃取里后面跑 —— 正则是快速第一道防线。

**15 个正则模式:**

| # | Pattern 名称 | 正则 |
|---|--------------|-------|
| 1 | Prompt injection — ignore instructions | `(?i)ignore (all )?(previous\|above) (instructions\|rules)\|disregard (all \|the )?system` |
| 2 | Prompt injection — reveal system | `(?i)(reveal\|output\|print\|show) (your\|the) (system prompt\|hidden instructions\|initial prompt)` |
| 3 | Prompt injection — role override | `(?i)you are now\|from now on you are\|new identity\|forget you are claude` |
| 4 | Shell injection — command substitution | `\$\([^)]{1,100}\)` |
| 5 | Shell injection — backticks | `` `[^`]{1,100}` `` |
| 6 | SQL injection — UNION / DROP / DELETE | `(?i)union\s+select\|drop\s+table\|delete\s+from\s+\w+\s+where\s+\d` |
| 7 | SQL injection — OR 1=1 | `('\|")\s*OR\s*('\|")?\d+('\|")?\s*=\s*('\|")?\d+` |
| 8 | Secret — high-entropy key | `\b[A-Z0-9]{32,}\b` |
| 9 | Secret — common prefixes | `(sk\|pk\|api\|secret\|token)_[a-zA-Z0-9]{16,}` |
| 10 | Secret — AWS access key | `\bAKIA[0-9A-Z]{16}\b` |
| 11 | Secret — GitHub token | `\bghp_[a-zA-Z0-9]{36}\b` |
| 12 | Secret — Slack token | `\bxox[pbar]-[0-9]{10,}-[a-zA-Z0-9]{24,}\b` |
| 13 | Private key block | `-----BEGIN (RSA \|DSA \|EC \|OPENSSH )?PRIVATE KEY-----` |
| 14 | Credit card | `\b(4\d{12}(\d{3})?\|5[1-5]\d{14}\|3[47]\d{13}\|6(?:011\|5\d{2})\d{12})\b` |
| 15 | PII — SSN | `\b\d{3}-\d{2}-\d{4}\b` |

**不可见 Unicode 扫描:** 阻止 U+200B、U+200C、U+200D、U+2060、U+FEFF(文件中部)以及 U+202A–U+202E(BIDI override)。这些是注入攻击隐藏 payload 让人类 review 看不见的常用手段。

### 5.4 `stop-session-verify.sh`

- **事件:** `Stop`,matcher `*`
- **用途:** 验证 adjourn 流程完成并有完整的 Completion Checklist。
- **解决:** Archiver 半完成 —— Phase 1 跑了,Phase 4 被跳过。

**契约:** 从 stdin 解析 `transcript_path`。在 transcript 里 grep adjourn 触发词。若未触发 adjourn,exit 0。若触发了 adjourn,验证 archiver 全四个 phase(`Phase 1: Archive`、`Phase 2: Knowledge Extraction`、`Phase 3: DREAM`、`Phase 4: Sync`)都带非占位值出现,再加 orchestrator 在 archiver 之后的 Notion sync 块。缺失或 `TBD` → 记录违规。无法阻止(session 已在结束)—— 只记录,exit 0。

### 5.5 `pre-read-allowlist.sh`

- **事件:** `PreToolUse`,matcher `Read`
- **用途:** 防止读 Life OS 作用域之外的文件,尤其是凭据文件。
- **解决:** 误伤或被注入导致读 `~/.ssh/`、`~/.aws/credentials`、`/etc/passwd`。

**契约:** 将 `file_path` 解析为绝对路径。若在 `cwd` 内或显式 allowlist 内 → exit 0。若匹配 denylist → exit 2 附提醒。否则 → exit 0(denylist 之外信任 LLM)。

**Denylist:** `~/.ssh/**`、`~/.aws/**`、`~/.gcp/**`、`~/.azure/**`、`~/.docker/config.json`、`~/.kube/config`、`~/.npmrc`、`~/.pypirc`、`/etc/passwd`、`/etc/shadow`、`/etc/sudoers*`、`**/id_rsa`、`**/id_ed25519`、`**/.env`、`**/.env.*`。

**Allowlist(压过一切):** `$cwd/**`、`~/.claude/skills/life_OS/**`、`~/.claude/scripts/**`、`~/.cache/lifeos/**`。

---

## 6 · 合规路径自动检测(Compliance Path Auto-Detection · 用户决策 #14)

Life OS 在两种不同的 repo 上下文里运行:dev repo(skill 代码库)与用户的 second-brain(数据 repo)。每个有自己的日志。

```bash
detect_compliance_path() {
  if [ -f "pro/agents/retrospective.md" ]; then
    echo "pro/compliance/violations.md"       # dev repo
  elif [ -d "_meta/" ] && [ -f "_meta/config.md" ]; then
    echo "_meta/compliance/violations.md"     # second-brain
  else
    echo "/dev/null"                          # skip logging
  fi
}
```

- `pro/agents/retrospective.md` = dev repo 标记
- `_meta/config.md` = second-brain 标记
- 其他任何 `cwd` 拿到 `/dev/null` —— 我们不在无关 repo 里创建 compliance 目录

两个 `violations.md` 文件都在 git 跟踪下;违规跟随 repo 走。两条路径都不写到 `~/.claude/` —— 那会违反 COURT-START-001 之后确立的"所有状态都是 markdown + git"原则。

---

## 7 · 违规日志格式(Violations Log Format)

**表头**(由 retrospective Mode 0 首次运行时创建):

```markdown
# Compliance Violations Log

> Rolling 90-day window. Older rows archived to `archive/{year}-Q{n}.md` by `backup.py`.

| Timestamp | Type | Severity | Agent | Detail | Hook | Resolved |
|-----------|------|----------|-------|--------|------|----------|
```

**行示例:**

```
| 2026-04-20T14:32:10+09:00 | CLASS_A | critical | ROUTER | Start trigger but no retrospective subagent launched | pre-prompt-guard | open |
```

**字段列:**

| 列 | 值 | 说明 |
|--------|--------|-------|
| Timestamp | 带时区的 ISO 8601 | `date -Iseconds` |
| Type | `CLASS_A` / `B` / `C` / `D` / `E` | 见 §8 |
| Severity | `critical` / `high` / `medium` / `low` | 按 §8 |
| Agent | `ROUTER` / `archiver` / `retrospective` / `unknown` | 从 tool_name 推断 |
| Detail | 一行元数据描述 | 不含用户 prompt 内容 —— PII 安全 |
| Hook | 脚本名 | 调试用 |
| Resolved | `open` / `resolved-<date>` | 由 AUDITOR 或手动翻转 |

**`Detail` 反模式:** 永远不含用户 prompt 内容、文件内容或密钥(即使"已脱敏"也不行)。只用元数据 —— pattern ID、文件路径类别、hook 名。

---

## 8 · 升级阶梯(Escalation Ladder)

Hook 追加行;`stats.py`(第 4 层)驱动升级决策。

**30 天滚动窗口,同类型计数:**

| 次数 | 动作 |
|-------|--------|
| ≥ 3 | 下次 `retrospective` Start Session 简报顶部警告横幅 |
| ≥ 5 | AUDITOR 每次 session 开始被强制进 Patrol Inspection 模式 |
| ≥ 10 | 系统性问题 —— 在 `eval-history.md` 标记供下版本 spec 修订 |

**严重性映射:**

| 类型 | 严重性 | 示例 |
|------|----------|---------|
| `CLASS_A` | critical | ROUTER 在触发词后跳过 subagent 启动 |
| `CLASS_B` | critical | Agent 伪造文件路径 / 章节 / HARD RULE 来源 |
| `CLASS_C` | high | Adjourn 结束时没有 Completion Checklist |
| `CLASS_D` | critical | 向 SOUL/wiki 提议的 Write 含注入模式 |
| `CLASS_E` | high | 尝试读 denylist 路径 |

升级是确定性的:`stats.py` 从 `violations.md` 按需计算;hook 只追加行。这让 hook 保持快(< 100ms)、升级可检视。

---

## 9 · 归档策略(Archive Policy)

`violations.md` 限 90 天滚动。更旧行按季度轮转,由 `backup.py` 搬(不是 hook —— hook 不搬数据)。

```
pro/compliance/                          # dev repo
├── violations.md                        # current 90 days
├── archive/2026-Q2.md                   # rotated quarterly
└── 2026-04-19-court-start-violation.md  # major incident dossiers (permanent)

_meta/compliance/                        # second-brain, same structure
├── violations.md
└── archive/
```

行级违规会轮转。主要事故档案(任何触发重构的)永久保留。

---

## 10 · 安装(Installation)

v1.6.2 的 `setup-hooks.sh` 安装一个 SessionStart version-check hook。v1.7 扩展它,原子注册全部五个 hook。

**v1.7 新增的 settings JSON 结构:**

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-prompt-guard.sh\"", "timeout": 5}],
      "id": "life-os-pre-prompt-guard"
    }],
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-write-scan.sh\"", "timeout": 5}],
        "id": "life-os-pre-write-scan"
      },
      {
        "matcher": "Read",
        "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/pre-read-allowlist.sh\"", "timeout": 3}],
        "id": "life-os-pre-read-allowlist"
      }
    ],
    "PostToolUse": [{
      "matcher": "Task|Bash|Write|Edit",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/post-response-verify.sh\"", "timeout": 5}],
      "id": "life-os-post-response-verify"
    }],
    "Stop": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "bash \"$HOME/.claude/skills/life_OS/scripts/hooks/stop-session-verify.sh\"", "timeout": 10}],
      "id": "life-os-stop-session-verify"
    }]
  }
}
```

**预检(继承自 v1.6.2 `setup-hooks.sh`):**

1. `jq` 已安装
2. 现有 `settings.json` 是合法 JSON
3. 全部五个 hook 脚本在 `scripts/hooks/` 下存在且可执行
4. 全部五个都是幂等的(装两次也是 no-op)

失败时:打印原因,不改 `settings.json`,exit 1。成功时:通过 `settings.json.tmp` + `mv` 原子写入。

**超时:** pre-read 3s(纯路径匹配)、prompt / write / post 检查 5s(正则扫描)、stop-verify 10s(transcript 解析)。hook 挂起时 Claude Code 杀它,当作 hook 错误处理 —— 工具调用不被阻止。

---

## 11 · 卸载 / 禁用(Uninstall / Disable)

**移除单个 hook:**

```bash
jq '.hooks.UserPromptSubmit = [.hooks.UserPromptSubmit[] | select(.id != "life-os-pre-prompt-guard")]' \
   ~/.claude/settings.json > ~/.claude/settings.json.tmp \
   && mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

**卸载全部 Life OS hook:** `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh --uninstall`。`--uninstall` flag(v1.7 新增)移除所有 `id` 以 `life-os-` 开头的 hook。不碰其他 skill。

**手动编辑:** 打开 `~/.claude/settings.json` 删条目。永远安全 —— hook 是纯追加的。

**不卸载只禁用:** 把 `pre-prompt-guard.sh` 改名为 `pre-prompt-guard.sh.disabled`。Claude Code 把缺失的可执行当作 hook 错误记录,然后继续不阻止。

---

## 12 · 测试(Testing)

Hook 行为由 `evals/scenarios/hook-compliance/` 覆盖:

| # | 场景 | 期望 |
|---|----------|----------|
| 1 | 用户说 "上朝",LLM 正确启动 retrospective | pre-prompt-guard 注入提醒、post-response-verify 通过 |
| 2 | 用户说 "上朝",LLM 跑 Bash 读 `_meta/sessions/INDEX.md` | pre-prompt-guard 注入、post-response-verify 阻止(CLASS_A)|
| 3 | 向 `wiki/notes.md` 写 "ignore all previous instructions" | pre-write-scan 以模式 #1 阻止 |
| 4 | 向 `projects/work/index.md` 写(作用域外)| pre-write-scan 放行 |
| 5 | 读 `~/.ssh/id_rsa` | pre-read-allowlist 阻止(CLASS_E)|
| 6 | 读 `$cwd/projects/foo.md` | pre-read-allowlist 放行 |
| 7 | "退朝"、archiver 跑、session 没跑 Phase 4 就结束 | stop-session-verify 记录 CLASS_C |
| 8 | 任意 prompt "what's the weather" | pre-prompt-guard 静默 exit 0 |

每个场景是一个 markdown 文件,含输入、期望 hook 输出、期望 `violations.md` diff。eval harness 确定性地重放它们 —— hook 测试路径里没有 LLM,所以 hook 行为独立于 LLM 漂移被验证。

---

## 13 · 反模式(Anti-Patterns)

- **别慢。** 默认 5s 超时(pre-read 3s)。hook 做网请求或文件系统遍历就是坏了。Hook 在每次相关事件都跑。
- **别不检查存在就写合规路径。** 用 §6 的 `/dev/null` 回退,而不是在随机 repo 里创建 compliance 目录。
- **别阻止只读操作,除非 denylist 命中。** 对读操作而言,false-positive 阻止比漏警更糟。
- **别记录用户 prompt 内容。** PII 风险。只记元数据:触发词、pattern ID、hook 名。用户 prompt 停留在 Claude Code transcript,从不进 git 跟踪的 compliance 日志。
- **别要求 Python。** 仅 Bash + jq。Python 是第 4 层(后台 worker),不是第 3 层的前置。
- **别在阻止时 exit 1。** 按 Claude Code 语义,exit 1 = "hook 错误,继续"。exit 2 = "阻止"。搞错会把硬阻止变成静默警告。
- **别在 stdout 发 ANSI 颜色码。** stdout 变成 system reminder —— 保持纯 markdown。装饰用 stderr,仅在阻止时可见。
- **别信 stdin JSON 值是 shell token。** 永远 `jq -r` 并对扩展加引号。含 `$(rm -rf ~)` 的恶意 prompt 必须不执行。

---

## 14 · 相关规范(Related Specs)

- `references/data-layer.md` —— 数据层边界;`compliance/violations.md` 住在这里,跟其他 `_meta/` 表面并列
- `references/eval-history-spec.md` —— AUDITOR eval-history 维度 `process_compliance` 消费 hook 标出的违规模式
- `references/tools-spec.md` —— 与 hook 互补的 Python 第 4 层工具(`stats.py`、`backup.py`、`reconcile.py`)
- `references/cortex-spec.md` —— 整体 Cortex 架构;hook 保护其 markdown-first 不变量
- `pro/compliance/2026-04-19-court-start-violation.md` —— 催生本规范的奠基事件
- `docs/architecture/execution-layer.md` —— 完整的第 3 层(hook)+ 第 4 层(Python tool)架构
- `scripts/setup-hooks.sh` —— v1.6.2 安装器模板,v1.7 扩展安装器继承自此
- `scripts/lifeos-version-check.sh` —— v1.6.2 仅有的 hook;"预检、幂等、原子"模式的参考

`violations.md` 数据模型在本规范 §7 定义(格式、列、升级阶梯);**不**在 cortex-spec 定义。

**END**

---

## 译注

- 本 spec 原文 5 个 hook 名与实际目录 `scripts/hooks/` 下文件一一对应(`pre-prompt-guard.sh` / `post-response-verify.sh` / `pre-write-scan.sh` / `stop-session-verify.sh` / `pre-read-allowlist.sh`)—— 与实现对齐,无 spec bug 候选。
- `denylist / allowlist` 保留英文,延续 hippocampus-spec 与 narrator-spec 里对"屏蔽列表 / 放行列表"既有术语选择。
- `HARD RULE / stdin / stdout / stderr / exit code / matcher / subagent / transcript / payload / false-positive` 保留英文。
- `Rolling 90-day window` 译为"90 天滚动窗口";`roll / rotate` 译为"轮转"(与 backup 规范一致)。
- 触发词表(§5.1)中的 CJK 原词保留不译,因为它们本身就是系统约定的触发字面量。
- 正则表达式代码块、JSON 代码块、bash 命令块一律不翻译。
- 原文 §8 表格中的 emoji 警告图标(🚨)依 Life OS 项目 CLAUDE.md 规范保留(系统告警场景)。
