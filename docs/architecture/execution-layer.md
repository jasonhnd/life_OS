---
status: legacy
authoritative: false
superseded_by: pro/CLAUDE.md
note: "v1.7-era / pre-R-1.8.0-011 pivot. Read for historical context only; current behavior in pro/CLAUDE.md."
---

# 执行层架构 · Shell Hooks (Layer 3) + Python Tools (Layer 4)

> 本文档说明 Life OS 的执行层设计：如何让 HARD RULE 真正"hard"、如何让决策引擎不只在用户打字时才动起来。
>
> 精神参考：Hermes Agent（Nous Research，10 万 stars）。
> 实现路径：Claude Code 宿主 + 纯本地 Shell 脚本 + 独立 Python 工具（markdown 输入 / markdown 输出）。
> 不引入 Python runtime、不依赖 Vercel、不替换宿主。

---

## Hermes Local 命名合同

`Hermes Local` 是本地执行面的用户可见名称。内部术语保持为 `execution layer`、`Layer 3`、`Layer 4`，以保证规格、agent contract 和合规检查不漂移。

Hermes Local 由 `Layer 3` 运行时 backstop 与 `Layer 4` Python 工具组成。它借鉴并 fork 了 `NousResearch/hermes-agent`（MIT License）的若干本地 agent 设计与工具实现；Life OS 只吸收这些模式并改造成 markdown-first 的本地 second-brain 工作流，不嵌入完整 Hermes gateway/runtime。简明归因表见 `docs/architecture/hermes-local.md`。

## 1 · 为什么需要执行层

Life OS 从 v1.0 到 v1.6.2 一直是"纯文档系统"——16 个 subagent 的身份、职责、封驳循环全部写在 `pro/agents/*.md` 里，orchestrator 读 markdown、launch subagent、拼报告。这条路线的优点是模型无关（LLM-agnostic）、可审计、零运行时依赖。

但两件事把"纯文档"的天花板撞穿了：

### 1.1 LLM 偷懒（已被证明）

2026-04-19 COURT-START-001 incident（见 `pro/compliance/2026-04-19-court-start-violation.md`）：用户在 dev repo 说"上朝"，Claude **完全跳过** `retrospective` 子代理，在主上下文里自演几步就输出报告，并且**编造**了不存在的文件路径作为"权威 HARD RULE 源"。事后复盘结论：

> 文档里写"HARD RULE"四个字不会让它真的 hard。文档完整 + 零强制机制 ≈ 无文档。LLM 默认会找省力路径，必须用 hook / audit gate / test 强制。

这是**执行层缺失**直接导致的产品级 bug。SKILL.md 和 pro/CLAUDE.md 把规则写得无比清楚，但 orchestrator 自己就能违反——那规则对用户的保护就是零。

### 1.2 LLM 不主动（等用户打字）

Life OS 目前只有一个入口：用户在 Claude Code 里打字。这意味着：

- 早上起来 INDEX.md 没人编译
- 孤儿文件、断链、frontmatter 缺失没人巡查
- 新 session 的 embedding 没人生成
- 每日简报没人在 06:00 推到手机
- Notion 里上周的决策回顾没人整理

Hermes 的答案是把 agent 做成常驻进程 + 19 个 gateway。我们不走那条路（太重、太绑单一平台），但**"有些事必须有人在后台主动跑"这个需求是真的**。

### 1.3 两个问题，两层答案

| 问题 | 现象 | 解法 | 层次 |
|------|------|------|------|
| LLM 偷懒 | 跳过 HARD RULE / 编造路径 / salami-slice | Shell hook 拦截 trigger + 注入强制规则 + 违规登记 | Layer 3 |
| LLM 不主动 | INDEX 不更新、embedding 不生成、简报不推送 | 独立 Python 脚本可手动跑、可 cron、可 GitHub Actions | Layer 4 |

这两层合起来叫**执行层**。精神参考是 Hermes，但 Life OS 的实现路径完全自己设计。

---

## 2 · Life OS 和 Hermes 的执行层对比

| 维度 | Hermes | Life OS |
|------|--------|---------|
| Runtime | Python 3.11+ 独立进程（gateway/agent/plugins）| Claude Code 宿主 + 外围 shell/python 脚本 |
| 工具数量 | 47 个原生工具（file、terminal、browser、RL 等）| 0 个原生工具，全靠宿主 Bash/Read/Write + MCP + 自定义 Python 脚本 |
| 强制机制 | `approval.py` 的 42 条 DANGEROUS_PATTERNS + memory_tool 注入扫描 + skills_guard 70+ 模式 | Claude Code SessionStart/PreToolUse/Stop hooks + Python 脚本内部校验 |
| 并发 | 多 gateway session（Telegram / Discord / Slack 等 19 个平台——Hermes 特性）| 单设备内多 subagent 并行（ROUTER 调度）；**Life OS 不做独立 bot / 跨平台 gateway** |
| 自学习 | skill 自动创建 + RL 训练闭环（Atropos submodule）| "方法库" 概念——wiki / SOUL / DREAM 按严格准则自动写 markdown，不训模型 |
| 持久化 | SQLite FTS5 (sessions) + 8 个可选 memory provider | 纯 markdown + YAML frontmatter + git |
| 定时能力 | 内置 cronjob 工具（`cronjob_tools.py`）| macOS launchd / crontab / GitHub Actions，择一即可 |

**关键差异**：Life OS **不复刻** Hermes runtime。Hermes 是"在 VPS 上跑的个人助理"，Life OS 是"嵌入到用户已有的 AI terminal 里的决策引擎"。执行层只吸收 Hermes 的**设计模式**（强制 + 自动化），不吸收它的**架构**（独立进程 + 多 gateway）。

换句话说：Hermes 是工人，Life OS 是朝廷。朝廷也需要胥吏（执行层），但胥吏不能喧宾夺主、不能把朝廷变成兵部衙门。

---

## 3 · Layer 3：Shell Hook 层

### 3.1 Claude Code Hook 机制基础

Claude Code 原生支持四类 hook，配置位于 `~/.claude/settings.json`：

| Hook 类型 | 触发时机 | 典型用途 |
|-----------|----------|----------|
| `SessionStart` | 每次启动 Claude Code session | 版本检测、拉取远端更新、显示晨报 |
| `UserPromptSubmit` | 用户提交每一条 prompt 前 | 检测 trigger 词、注入 HARD RULE、屏蔽危险请求 |
| `PreToolUse` | 执行工具前（Bash/Write/Edit 等）| 扫描危险命令、block 写入敏感路径、参数校验 |
| `PostToolUse` | 执行工具后 | 格式化文件、log 调用链、校验输出 |
| `Stop` | session 结束前 | 运行 completion checklist、同步 git、dump 统计 |

Hook 的生命周期很简单：宿主启动一个 shell 子进程，把上下文（JSON）喂到 stdin，进程打印到 stdout 的文本**会被注入到 LLM 上下文**。这意味着 hook 不止能"拦截"，还能**主动告诉 LLM 要做什么**。

配置示例：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$HOME/.claude/scripts/lifeos-pre-prompt-guard.sh\"",
            "timeout": 2
          }
        ],
        "description": "Life OS trigger-word guard",
        "id": "lifeos:pre-prompt-guard"
      }
    ]
  }
}
```

### 3.2 已有的 hook（v1.6.2a 基线）

目前 Life OS 只装了一个 hook。

**`scripts/lifeos-version-check.sh`**（配合 `scripts/setup-hooks.sh` 一键安装）：

```bash
#!/bin/bash
# Life OS Version Check — runs at Claude Code SessionStart
set -euo pipefail

SKILL_PATH="$HOME/.claude/skills/life_OS/SKILL.md"
CACHE_FILE="${XDG_CACHE_HOME:-$HOME/.cache}/lifeos/version-check-$(date +%Y%m%d)"

# 一天只跑一次（用当日 cache 文件做 sentinel）
if [ -f "$CACHE_FILE" ]; then cat "$CACHE_FILE"; exit 0; fi

LOCAL=$(grep -m1 '^version:' "$SKILL_PATH" | sed 's/.*"\(.*\)".*/\1/')
REMOTE=$(curl -sf --max-time 3 "https://raw.githubusercontent.com/.../SKILL.md" | grep -m1 '^version:' | sed 's/.*"\(.*\)".*/\1/' || echo "")

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "[Life OS] v${LOCAL} ✅ (latest)" | tee "$CACHE_FILE"
else
  echo "[Life OS] ⬆️ Update available: v${LOCAL} → v${REMOTE}" | tee "$CACHE_FILE"
fi
```

安装脚本（`setup-hooks.sh`）处理三件事：
1. **pre-flight**：检查 `jq` 是否安装、源脚本是否存在、现有 `settings.json` 是否合法 JSON
2. **幂等安装**：用 hook ID（`session:lifeos-version-check`）去重，重复跑不会写两遍
3. **原子写入**：先写临时文件再 mv，避免半成品 JSON 破坏 Claude Code 启动

这套"pre-flight → 幂等 → 原子"是**所有后续 hook 脚本必须遵守的模板**。

### 3.3 v1.7 计划的五个 hook

#### 3.3.1 `lifeos-pre-prompt-guard.sh` · UserPromptSubmit 拦截

**触发**：用户每提交一条 prompt。
**作用**：检测 trigger 词（"上朝"/"退朝"/"复盘"/"朝堂议政"...），**注入 HARD RULE 系统提示**，让 orchestrator 无法跳过子代理 launch。

**解决的具体 bug**：COURT-START-001（ROUTER 不读 `retrospective.md` 就自演 18 步）。

**伪代码**：

```bash
#!/bin/bash
set -euo pipefail

# 读 stdin 的 prompt JSON
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')

TRIGGER_RE='^(上朝|退朝|复盘|朝堂议政|开会|start|adjourn|review|debate|はじめる|お疲れ)'
if [[ "$PROMPT" =~ $TRIGGER_RE ]]; then
  TRIGGER="${BASH_REMATCH[1]}"
  case "$TRIGGER" in
    上朝|start|はじめる)
      AGENT="retrospective"
      MODE="Start Session Mode"
      ;;
    退朝|adjourn|お疲れ)
      AGENT="archiver"
      MODE="Adjourn 4-phase flow"
      ;;
    复盘|review)
      AGENT="retrospective"
      MODE="Review Mode"
      ;;
    朝堂议政|debate)
      AGENT="council"
      MODE="3-round debate"
      ;;
  esac

  cat <<EOF
<system-reminder>
HARD RULE · Trigger "$TRIGGER" detected.

Required actions (NOT optional):
1. Read pro/agents/${AGENT}.md BEFORE doing anything else
2. Launch(${AGENT}) as independent subagent in $MODE
3. Do NOT execute any step in main context
4. Do NOT simulate subagent output
5. Output exactly 2 lines:
   🌅 Trigger: ${TRIGGER} → Launching ${AGENT} subagent
   [Launch(${AGENT}) here]

Violation of this rule will be logged to pro/compliance/violations.md.
Precedent: COURT-START-001 (2026-04-19) proved that "文档级 HARD RULE" 无强制机制 = 糊弄.
</system-reminder>
EOF
fi
```

这个 hook 的价值在于：**它运行在 Claude Code 拿到 prompt 之前，注入的文字 LLM 必然看到**。比单纯在 SKILL.md 写 HARD RULE 强一个数量级。

#### 3.3.2 `lifeos-post-response-verify.sh` · PostToolUse 合规扫描

**触发**：每次工具调用完成后。
**作用**：检查 orchestrator 的输出是否符合 trigger 模板。检测到违规 → 写入 `pro/compliance/violations.md`（dev repo）或 `_meta/compliance/violations.md`（user repo）。

**检测规则**（举例）：

- 用户刚说"上朝"且 hook 注入过 HARD RULE → 扫描接下来 3 次工具调用是否包含 `Task(retrospective)` 子代理 launch。没有 = 违规。
- 用户刚说"退朝"→ 扫描是否有 `Task(archiver)`。orchestrator 自己跑 Bash 做 git commit = 违规（应由 archiver Phase 4 做）。
- 主上下文出现形如"让我先来看看……"但下一步没 launch 子代理 = salami-slice 征兆。

**违规 log 格式**：

```markdown
# Compliance Violations Log

| Timestamp | Trigger | Type | Severity | Details | Resolved |
|-----------|---------|------|----------|---------|----------|
| 2026-04-19T22:47+09:00 | 上朝 | A (skip-subagent) | P0 | ROUTER simulated 18 steps in main context | false |
| 2026-04-19T22:52+09:00 | 上朝 | B (fabricate) | P0 | Referenced non-existent `_meta/roles/CLAUDE.md` | false |
```

**升级阶梯**（由 Python 工具 `stats.py` 读 log 后决策）：

- 同类违规 ≥ 3（30 日内）→ pre-prompt-guard 注入更严格的 reminder（"你已累犯 3 次，下次将触发 AUDITOR 强制审计"）
- 同类违规 ≥ 5 → `retrospective` 晨报顶部 🚨 警示
- 同类违规 ≥ 10（90 日内）→ 每次 session start 强制 AUDITOR Compliance Patrol

**90 日归档**：`pro/compliance/violations.md` 只保留最近 90 日；更早的归档到 `pro/compliance/archive/YYYY-QN.md`。这一步由 Python 工具 `backup.py` 执行，不是 shell hook 的职责。

#### 3.3.3 `lifeos-pre-write-scan.sh` · PreToolUse 写入前扫描

**触发**：任何 `Write` 或 `Edit` 工具调用前。
**作用**：扫描即将写入的内容。如果目标路径是 `wiki/`、`SOUL.md`、`_meta/concepts/`，运行敏感信息正则扫描。检测到 = **block 写入**，返回 exit code 2 让 Claude Code 取消。

**15 条核心正则**（从 Hermes `approval.py` 移植 + Life OS 自有的 Privacy Filter）：

```bash
PATTERNS=(
  # 身份信息
  '\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'                      # 英文姓名
  '[\u4e00-\u9fa5]{2,3}(先生|女士|老师|总监|CEO|CTO)'  # 中日文姓名 + 称谓
  '\b[\w.+-]+@[\w-]+\.[\w.-]+\b'                       # 邮箱
  '\b\d{3}-\d{4}-\d{4}\b'                              # 日本手机
  '\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'  # 北美手机

  # 金额
  '\d{1,3}(,\d{3})*\s*(円|yen|JPY)'                    # 日元
  '\$\d{1,3}(,\d{3})*(\.\d{2})?'                       # 美元
  '¥\d{1,3}(,\d{3})*'                                  # 人民币

  # 账户/密钥
  '\b[A-Z0-9]{20,}\b'                                  # 通用 API key 长字符串
  '(sk|pk|api|secret)_[a-zA-Z0-9]{16,}'                # 明显 secret 前缀
  '\bAKIA[0-9A-Z]{16}\b'                               # AWS key
  '\bghp_[a-zA-Z0-9]{36}\b'                            # GitHub token

  # 公司具体名（可通过 whitelist 配置放过某些）
  '(Google|Apple|Microsoft|Amazon|Meta)'               # FAANG
  '(OpenAI|Anthropic|DeepMind)'                        # AI labs

  # URL with query params（可能含 session token）
  'https?://[^\s]+\?[^\s]*token='
)
```

**伪代码**：

```bash
#!/bin/bash
set -euo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')

# 只扫 wiki / SOUL / concepts
case "$FILE" in
  */wiki/*|*/SOUL.md|*/_meta/concepts/*) ;;
  *) echo "$INPUT"; exit 0 ;;
esac

for PAT in "${PATTERNS[@]}"; do
  if echo "$CONTENT" | grep -Eq "$PAT"; then
    echo "[Hook] BLOCKED: sensitive pattern matched: $PAT" >&2
    echo "[Hook] File: $FILE" >&2
    echo "[Hook] Run 'git diff' locally, strip PII, then retry Write." >&2
    exit 2
  fi
done

echo "$INPUT"
```

#### 3.3.4 `lifeos-stop-session-verify.sh` · Stop hook

**触发**：session 即将结束。
**作用**：如果这个 session 触发过"退朝"，验证 archiver 的 Completion Checklist 是否完整输出。缺失 → 写违规 log。

```bash
#!/bin/bash
set -euo pipefail

TRANSCRIPT="$1"  # Claude Code 会把 transcript 路径作为参数传进来

# 有没有触发过退朝？
if grep -q "退朝\|adjourn\|お疲れ" "$TRANSCRIPT"; then
  # 有没有 archiver 的 4 phase 完成标记？
  EXPECTED=("Phase 1: Archive" "Phase 2: Knowledge Extraction" "Phase 3: DREAM" "Phase 4: Sync")
  for PHASE in "${EXPECTED[@]}"; do
    if ! grep -q "$PHASE" "$TRANSCRIPT"; then
      echo "[Hook] Adjourn violation: missing $PHASE" >&2
      # 写违规 log
      LOG="./pro/compliance/violations.md"
      [ -f "$LOG" ] || LOG="./_meta/compliance/violations.md"
      echo "| $(date -Iseconds) | 退朝 | C (incomplete) | P1 | Missing $PHASE | false |" >> "$LOG"
    fi
  done
fi
```

#### 3.3.5 `pre-read-allowlist.sh` · PreToolUse (Read) 敏感路径防护

**触发**：每次 `Read` 工具调用前。
**作用**：阻止 Read 指向 denylist 路径（`~/.ssh/**`、`~/.aws/credentials`、`/etc/passwd` 等敏感位置）。
**解决的具体风险**：prompt 注入诱导 Read 凭据文件、误操作读取系统密钥。

**契约**：把 `file_path` 解析成绝对路径。在 `cwd` 或显式 allowlist 内 → exit 0。匹配 denylist → exit 2 + reminder。其他情况 → exit 0（对 denylist 以外的路径信任 LLM）。

**Denylist**：`~/.ssh/**`、`~/.aws/**`、`~/.gcp/**`、`~/.azure/**`、`~/.docker/config.json`、`~/.kube/config`、`~/.npmrc`、`~/.pypirc`、`/etc/passwd`、`/etc/shadow`、`/etc/sudoers*`、`**/id_rsa`、`**/id_ed25519`、`**/.env`、`**/.env.*`。

**Allowlist（覆盖上述）**：`$cwd/**`、`~/.claude/skills/life_OS/**`、`~/.claude/scripts/**`、`~/.cache/lifeos/**`。

完整契约见 `references/hooks-spec.md` §5.5。

**注**：v1.6.2a 的 `lifeos-version-check.sh`（SessionStart 版本比对）**继续使用**，不在 v1.7 的"五个新 hook"里——它是 v1.6.2 已在线的基线 hook，v1.7 只是叠加新的 5 个。Session 启动时的晨报 briefing 由 retrospective Mode 0 负责（spec 层面），不由 shell hook 注入。

### 3.4 违规登记（`compliance/violations.md`）的设计

**双仓库策略**（源自 COURT-START-001 决议）：

```
dev repo (life-os):
  pro/compliance/
    violations.md              ← 开发者自己的违规 log（git 追踪）
    violations.example.md      ← 格式示例
    archive/2026-Q2.md         ← 90 日外归档
    2026-04-19-court-start-violation.md  ← 重大 incident 完整档案

user repo (second-brain):
  _meta/compliance/
    violations.md              ← 用户的违规 log（跟 second-brain 一起 git push）
    archive/{YYYY-Q}.md
```

**绝对禁止**：把违规 log 写到 `~/.claude/` 本地私有路径。产品级状态必须 markdown + git，否则：

- 用户换设备 → 历史丢失
- 别人 clone repo → 零防御
- 不可审计

**路径解析**（hook 自动判断当前是 dev 还是 use repo）：

```bash
if [ -f "./pro/agents/retrospective.md" ]; then
  LOG="./pro/compliance/violations.md"       # dev repo
elif [ -f "./_meta/config.md" ]; then
  LOG="./_meta/compliance/violations.md"     # user second-brain
else
  LOG=""                                     # 其他 repo，不记录
fi
```

---

## 4 · Layer 4：Python 工具层

### 4.1 设计哲学

四条硬规矩：

1. **单一职责**：每个工具只干一件事。`reindex.py` 只编译 INDEX、`embed.py` 只算 embedding，不混。
2. **操作 markdown 原件**：输入是 `second-brain/**/*.md`，输出也是 markdown（或 YAML frontmatter 增量）。**不建新 schema、不碰 SQLite**。
3. **独立于 Claude Code**：命令行可直接跑 `python -m lifeos.tools.reindex ~/second-brain`，不依赖任何 AI 在线。
4. **markdown 输入 / markdown 输出**：每个工具的 I/O 都是 markdown。这是 Life OS 最核心的约束——Python 是**外围胥吏**，不是**核心文官**。

### 4.2 目录结构

```
life-os/tools/
├── __init__.py
├── cli.py                     # 统一入口：life-os-tool <cmd> [args]
├── reindex.py                 # 扫 _meta/sessions/ → 编译 INDEX.md
├── reconcile.py               # 检查孤儿文件 / 断链 / frontmatter 缺失
├── stats.py                   # 统计 AUDITOR / REVIEWER / 违规 log
├── research.py                # 后台研究（Exa / SerpAPI / firecrawl）
├── embed.py                   # 给 session 生成 embedding，存到 YAML
├── daily_briefing.py          # 生成今日 3 行简报
├── backup.py                  # 加密备份（tar + gpg）
├── migrate.py                 # schema 迁移（v1.6.2a → v1.7 frontmatter 变化）
├── search.py                  # 跨 session 语义搜索
├── export.py                  # second-brain → PDF / HTML / JSON
├── seed.py                    # 新用户初始化 _meta/ 目录结构
├── sync_notion.py             # 容错的 Notion 同步（orchestrator 兜底）
├── lib/
│   ├── second_brain.py        # 读写 markdown + YAML frontmatter 的基础库
│   ├── embeddings.py          # OpenAI / local embedding 封装
│   ├── notion.py              # Notion API client
│   ├── config.py              # 读 _meta/config.md
│   └── privacy.py             # 3.3.3 的 15 条 regex 共享给 Python 端
├── tests/
│   ├── test_reindex.py
│   ├── test_reconcile.py
│   └── fixtures/second-brain-sample/
└── pyproject.toml
```

安装方式：`pip install -e ./tools`，之后 `life-os-tool --help`。不**必须**装——不装 Python 的用户仍然能用 Life OS 的全部决策功能，只是没有"胥吏"帮忙打杂。

### 4.3 12 个核心工具

#### ① `reindex.py` — 编译 INDEX.md

**作用**：扫 `second-brain/_meta/sessions/*.md` 的 frontmatter（subject / domains / score），编译成 `_meta/sessions/INDEX.md`，给 `retrospective` 晨报和 `ROUTER` 主题框架用。海马体级加速。

**输入**：`second-brain/_meta/sessions/**/*.md`
**输出**：`second-brain/_meta/sessions/INDEX.md`
**运行**：手动 `life-os-tool reindex` / cron 每 6 小时 / GitHub Action on push
**代码骨架**：

```python
# tools/reindex.py
from pathlib import Path
from .lib.second_brain import load_frontmatter, render_table

def reindex(brain_root: Path) -> str:
    sessions = sorted((brain_root / "_meta/sessions").glob("**/*.md"))
    rows = []
    for s in sessions:
        fm = load_frontmatter(s)  # returns dict or None
        if not fm: continue
        rows.append({
            "date": fm.get("date"),
            "subject": fm.get("subject", "(unknown)"),
            "domains": ",".join(fm.get("domains", [])),
            "score": fm.get("overall_score", "-"),
            "path": str(s.relative_to(brain_root)),
        })
    table = render_table(rows, headers=["date","subject","domains","score","path"])
    (brain_root / "_meta/sessions/INDEX.md").write_text(f"# Session Index\n\n{table}\n")
    return f"indexed {len(rows)} sessions"
```

#### ② `reconcile.py` — 结构体检

**作用**：四个检查——孤儿文件（在 `projects/` 但没被 `INDEX.md` 引用）、断链（markdown link 指向不存在的路径）、frontmatter 缺失（`_meta/sessions/` 下没 YAML header 的文件）、主题 × 路径不一致（frontmatter 说 `domains: [finance]` 但文件在 `projects/health/` 下）。

**输入**：整个 `second-brain/`
**输出**：`second-brain/_meta/reconcile-report-{date}.md`
**运行**：每次 `retrospective` housekeeping 时 trigger / 每周一 cron / pre-push git hook
**代码骨架**：

```python
# tools/reconcile.py
def reconcile(brain: Path) -> dict:
    issues = {"orphan": [], "broken_link": [], "missing_fm": [], "mismatch": []}
    all_files = set(brain.glob("**/*.md"))
    indexed = set(parse_index_paths(brain / "_meta/sessions/INDEX.md"))
    issues["orphan"] = [f for f in all_files if f not in indexed and "sessions" in f.parts]
    for f in all_files:
        for link in extract_markdown_links(f):
            if not (brain / link).exists():
                issues["broken_link"].append((f, link))
    return issues
```

#### ③ `stats.py` — 质量统计

**作用**：读所有 session 的 Summary Report frontmatter + `compliance/violations.md` + AUDITOR 评分，生成数字化健康报告。直接喂给 `self-review` journal。

**输入**：sessions + violations + audit logs
**输出**：stdout table + `_meta/self-review-{YYYY-MM}.md`
**运行**：每月 1 日 cron / 手动 `life-os-tool stats --month 2026-04`
**关键指标**：AUDITOR 平均分、REVIEWER 否决率、COUNCIL 触发率、Express path 命中率、违规累计数、最常见 domain、最长决策耗时。

#### ④ `research.py` — 后台研究

**作用**：收到一批研究任务（来自 session 的 "needs investigation" 标记），并行跑 Exa / firecrawl / SerpAPI，把结果写到 `_meta/research-queue/{topic}-{date}.md`。下次 session `retrospective` 读到后呈给 ROUTER。

**输入**：`_meta/research-queue/pending/*.md`（每个文件一条 query）
**输出**：`_meta/research-queue/done/{topic}.md`（markdown 研究报告）
**运行**：每晚 23:00 cron / 用户手动触发 `life-os-tool research --from pending/`
**为什么不做成 subagent**：研究任务不需要实时，提前一晚跑完、早上送到晨报里价值最大。这正是"LLM 不主动"需要 Layer 4 补位的典型场景。

#### ⑤ `embed.py` — v1.7 Out of Scope（占位文件）

**状态**：v1.7 **不实现**语义 embedding（用户决策 #3：markdown-first，LLM-judgment-only，不引入向量 DB / embedding provider）。

`tools/embed.py` 在 v1.7 只是一个 placeholder：调用它打印 notice 并 exit 0，避免被误用。session-level 语义检索在 Claude Code session 内由 hippocampus subagent 用 LLM judgment 完成（见 `references/hippocampus-spec.md`）；批量搜索用 `search.py` 的 metadata + grep ranking。完整上下文见 `references/tools-spec.md` §6.12。

#### ⑥ `daily_briefing.py` — 晨报

**作用**：生成今日简报——昨日 session 数、待处理 inbox、DREAM auto-trigger 条目、SOUL 健康摘要、strategic lines 最新活动。输出 markdown 到 `_meta/briefings/{date}.md`；用户可自行配置本地通知（macOS `osascript` / `terminal-notifier` 等）。**v1.7 不内置 Telegram / 跨平台推送**——用户决策明确剥离，坚持本地化。

**输入**：整个 second-brain 最近 24h 变更
**输出**：`_meta/briefings/YYYY-MM-DD.md` + 推送
**运行**：launchd / cron 06:00 每日
**和 `retrospective` 晨报的区别**：`retrospective` 是"session start 时在 CLI 里呈现"，`daily_briefing` 是"不管你开不开 CLI，06:00 都推到手机"。两者内容可以一致，触发点不同。

#### ⑦ `backup.py` — 加密备份

**作用**：`tar czf` 整个 second-brain，gpg 对称加密，上传到 S3 / B2 / 本地外置盘。带版本轮转（保留 7 日、4 周、12 月）。

**输入**：second-brain 路径 + 加密 key（环境变量）
**输出**：`backup-YYYY-MM-DD.tar.gz.gpg`
**运行**：每晚 02:00 cron
**安全性**：加密 key 不写 config 文件，通过 `LIFEOS_BACKUP_KEY` 环境变量注入；launchd plist 用 `EnvironmentVariables` 或 macOS Keychain 读取。

#### ⑧ `migrate.py` — schema 迁移

**作用**：Life OS 版本升级时 frontmatter 字段变化（例：v1.6.2a 没有 `strategic_role`，v1.7 需要每个 project 加）。migrate 脚本扫全部文件，按 migration 规则批量改写。

**输入**：second-brain + 目标版本号
**输出**：修改后的 second-brain + `_meta/migration-log-{from}-to-{to}.md`
**运行**：手动触发 `life-os-tool migrate --to 1.7.0`，跑前自动 `backup.py`
**幂等**：每条 migration 规则带 `applied_in` 标记，已迁移的文件跳过。

#### ⑨ `search.py` — 跨 session 语义搜索

**作用**：用户问"三个月前我怎么决定要不要离职"，CLI 里跑 `life-os-tool search "quit job decision"`，工具用 `embed.py` 产生的 embedding 做 cosine 相似度，返回 top 5 session + 摘要。

**输入**：query string + `_meta/sessions/` embedding
**输出**：stdout 的 ranked list（session path + 相似度 + 一句摘要）
**运行**：手动触发
**为什么不做成 subagent 工具**：作为 CLI 起步简单、无上下文污染。未来可以包一层 MCP server 暴露给宿主。

#### ⑩ `export.py` — 导出

**作用**：把 second-brain 导成 PDF（年度决策集）、HTML（静态站，自部署到 Netlify）、JSON（数据科学分析用）。分别通过 pandoc / mkdocs / json schema。

**输入**：second-brain 子集（按 date range / project / domain 过滤）
**输出**：`exports/{format}/{name}.{ext}`
**运行**：手动 / 每季度 cron 生成季度总结

#### ⑪ `seed.py` — 新用户初始化

**作用**：新用户第一次用 Life OS 时跑一次，在目标路径创建标准目录结构（`_meta/`、`projects/`、`areas/`、`wiki/`）、写空 `config.md` 模板、创建示例 session 让 retrospective 有东西可读。

**输入**：目标路径 + 用户信息（姓名、时区、语言、主题偏好）
**输出**：完整初始化的 second-brain
**运行**：安装时一次性
**和 `scripts/setup-hooks.sh` 的关系**：setup-hooks 管宿主层面的 hook 注册，seed 管用户数据层面的目录结构。两个解耦，各负其责。

#### ⑫ `sync_notion.py` — Notion 兜底同步

**作用**：archiver Phase 4 的 Notion 同步如果失败（MCP 不可用 / 网络抽风 / rate limit），orchestrator 会在 Completion Checklist 里标 `failed`。这时用户可以手动跑 `life-os-tool sync-notion --since 2026-04-19` 把遗漏补上。

**输入**：second-brain + Notion API token + 日期范围
**输出**：Notion 页面更新 + `_meta/notion-sync-log.md`
**运行**：手动补救 / 或作为 Notion MCP 不可用时的 fallback

### 4.4 定时运行方式（本地优先，v1.7 不用 GitHub Actions）

Life OS 的 Python 工具**不要求**任何定时执行（用户决策 #1：v1.7 所有工具从 Claude Code Bash 本地触发，不引入 GitHub Actions / cron-on-VPS / 远程调度）。但如果你想"每天 06:00 自动推简报"，下面两条纯本地路径任选：

#### 4.4.1 macOS launchd（最适合个人设备）

`~/Library/LaunchAgents/com.lifeos.daily-briefing.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.lifeos.daily-briefing</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/env</string>
    <string>life-os-tool</string>
    <string>daily-briefing</string>
    <string>--push</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
  <key>EnvironmentVariables</key>
  <dict>
    <key>LIFEOS_BRAIN_PATH</key><string>/Users/you/second-brain</string>
  </dict>
  <key>StandardOutPath</key>
  <string>/tmp/lifeos-briefing.log</string>
</dict>
</plist>
```

加载：`launchctl load ~/Library/LaunchAgents/com.lifeos.daily-briefing.plist`

#### 4.4.2 crontab（Linux/WSL）

```cron
# m h dom mon dow  command
0  6 * * *  /usr/bin/env life-os-tool daily-briefing --push
0  2 * * *  /usr/bin/env life-os-tool backup
0 23 * * *  /usr/bin/env life-os-tool research --from pending/
0  */6 * * *  /usr/bin/env life-os-tool reindex
```

#### 4.4.3 GitHub Actions / 远程 cron · Out of Scope for v1.7

用户决策 #1：v1.7 所有工具从 **Claude Code Bash 本地触发**。GitHub Actions workflow、VPS 上的 cron、云端 scheduler 等远程调度形态全部 out of scope for v1.7——理由是 v1.7 Python 工具的设计前提是"用户坐在自己机器前、由本地 Claude Code 触发"，远程调度会引入 secret 管理、网络依赖、跨设备 git 冲突等复杂度，和 markdown-first + 本地优先的主线不吻合。

个人机器上的 launchd（4.4.1）或 crontab（4.4.2）已经够用；再不够就手动（4.4.4）。

#### 4.4.4 干脆不定时

全部手动也行。Python 工具是**方便工具**，不是**必需依赖**。Life OS 的决策引擎在 Claude Code 里完整可用。

---

## 5 · 两层如何协同

以一个完整的"退朝"场景看 Layer 3 + Layer 4 怎么联手。

**T0 · 用户输入**：`退朝`

**T1 · Layer 3：`lifeos-pre-prompt-guard.sh` 拦截**
- 检测到 trigger "退朝"
- 向 stdin 注入 `<system-reminder>HARD RULE: Launch(archiver)...</system-reminder>`

**T2 · Layer 2：orchestrator 收到 HARD RULE，规规矩矩输出**
```
📝 退朝 — 开始归档流程 (4 phases)...
[Task(archiver) as subagent]
```

**T3 · Layer 2：archiver 4 phases 完整跑完**
- Phase 1 Archive
- Phase 2 Knowledge Extraction（wiki + SOUL auto-write）
- Phase 3 DREAM（10 auto-trigger 检测）
- Phase 4 Sync（git push + orchestrator 做 Notion sync）
- 输出 Completion Checklist

**T4 · Layer 3：`lifeos-stop-session-verify.sh` 验证**
- 扫 transcript 确认 4 phases 都出现
- 确认 Completion Checklist 所有字段非 placeholder
- 否则 append 违规 log

**T5 · Layer 4：`reindex.py` 手动或本地 launchd**
- 新 session 的 frontmatter 被扫进 `_meta/sessions/INDEX.md`
- 下次 `retrospective` 晨报直接读到（retrospective 在 Mode 0 里自动调用 reindex，不依赖定时器）

**T6 · Layer 4：`search.py` 的 metadata + grep ranking**
- v1.7 不生成 embedding（out of scope — 用户决策 #3）
- 搜索通过 session frontmatter 字段 + 全文 grep + 时效加权实现
- session 内的语义检索走 hippocampus subagent（LLM judgment，Cortex Step 0.5）

**T7 · Layer 4：次日 06:00 `daily_briefing.py`**
- 读昨日新 session 的结论
- 读 `violations.md` 最近 7 日
- 读 DREAM auto-trigger 是否撞到"决策疲劳"
- 输出到 `_meta/briefings/{date}.md`，用户可选择配置本地通知

Layer 3 负责**不让 LLM 糊弄**；Layer 4 负责**让系统自己动起来**。两层各自独立——hook 不装也能用 Python 工具，Python 不装 hook 也能工作。但两层都齐全时，Life OS 就不再是"等用户打字的决策框架"，而是"有纪律、有胥吏的朝廷"。

---

## 6 · 路线图

整个执行层计划**全部在 v1.7 里做完**。内部按推进顺序分三块：

**v1.7 · 阶段一 — 执行层 MVP**

- Layer 3：`pre-prompt-guard` + `post-response-verify` + `pre-write-scan` + `stop-session-verify` + `pre-read-allowlist`（共 5 个 hook，完整契约见 `references/hooks-spec.md`）
- Layer 4：`reindex` + `reconcile` + `stats` + `daily_briefing`（前 4 个 Python 工具）
- 违规 log 双仓库机制正式上线（`pro/compliance/` + `_meta/compliance/`）
- 文档：本文件 + `docs/guides/hooks-install.md` + `docs/guides/python-tools-install.md`

**v1.7 · 阶段二 — 扩展与自动化**

- Layer 4：`research` + `search` + `backup` + `migrate` + `sync_notion` + `export` + `seed`（其余 7 个 Python 工具；`embed` 为 out-of-scope 占位，不在本阶段实现）
- 提供 launchd / crontab 两套本地模板（GitHub Actions 及远程调度 out of scope——用户决策 #1）
- 违规升级阶梯由 `stats.py` 驱动（≥3 次同类 → 升级 hook 严格度）
- self-review journal 自动生成（月度）

**v1.7 · 阶段三 — Life OS as agent（本地自主运行）**

- 本地 launchd / crontab 接通每日 briefing + 本地通知（macOS 原生等），**不做 Telegram bot / 远程消息 gateway**（用户明确剥离 v1.7 scope）
- MCP server 包装 Python 工具，让宿主 LLM 能直接调用 `search` / `reindex` 而不必 shell out
- evals 自动化触发（N 次 session 后跑 `evals/run-eval.sh`，结果反哺 AUDITOR patrol 规则）

三阶段全部在 v1.7 交付后，Life OS 才算摆脱"Claude Code 插件"的形态，成为真正的个人决策 OS。

---

## 7 · 设计原则复核

写完这份设计再对照自检一遍：

- ✅ Hermes 是精神参考，Life OS 实现是自己的（不复刻 gateway / RL / plugin registry）
- ✅ 不引入 Python runtime（Life OS 本体不变成 Python 进程，Python 是外围胥吏）
- ✅ Python tools 是外围脚本，不是核心（不装也能用 Life OS 全功能）
- ✅ Shell hook 是 Claude Code 原生机制（不发明新 hook 类型）
- ✅ 没有 Vercel 依赖（launchd / cron / GitHub Actions 任一即可，本地优先）
- ✅ 所有状态 markdown + git（违规 log、research queue、briefing、self-review 全是 md）
- ✅ 区分 dev repo 和 user repo（双仓库 compliance 策略）
- ✅ 模型无关（hook 逻辑是 shell，Python 工具不绑 Claude API，embedding 可换本地模型）

执行层的价值不是让 Life OS 更"智能"，而是让已有的智能**真的 hard**、真的**主动**。这两件事在 v1.7 做到位，Life OS 的自主运行才有地基。

---

## 附 · 相关文档

- `pro/compliance/2026-04-19-court-start-violation.md` — COURT-START-001 完整事件档案
- `devdocs/research/2026-04-19-hermes-analysis.md` — Hermes Agent 深度调研
- `docs/architecture/16-agents.md` — Layer 2 的 16 个 subagent 定义
- `docs/architecture/hard-rules-catalog.md` — Layer 1 的全部 HARD RULE 清单
- `docs/architecture/markdown-first.md` — 为什么所有状态必须 md + git
- `scripts/setup-hooks.sh` — 当前 v1.6.2a 的 hook 安装脚本（模板）
- `scripts/lifeos-version-check.sh` — 当前唯一在线的 hook 实现（参考）
- `pro/GLOBAL.md` — 所有 agent 共享的安全边界

**END**
