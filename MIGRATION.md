# Life OS 开发环境迁移手册

> 把开发工作从一台 Mac 转到另一台。最后更新：2026-05-27（v1.9.0 ship）

> **v1.9.0 重要更新**：本手册下方诸多章节（特别是 §1.0 以前的 v1.6/v1.7/v1.8.0-1.8.4 升级路径）引用的 `bash setup-hooks.sh`、`scripts/lifeos-*.sh`、Python 依赖、hook 部署等 —— **均已在 v1.8.5 hook 层退役 + v1.8.7 md-only 本体论提交后不再适用**。
>
> v1.8.5+ 现状（保留作为历史参考的 .sh 提及说明）：
> - 所有 `scripts/hooks/*.sh` 已删除（~30 个 bash hook 退役）
> - `setup-hooks.sh`、`lifeos-version-check.sh`、`lifeos-pre-prompt-guard.sh` 等部署脚本已删除
> - 当前 setup 跑 `/install-agents`（slash 命令，替代所有历史 bash 脚本）
> - 当前 hooks 概念不再存在 — 替换为 inline LLM 程序（auditor Mode 3 等）
> - 系统依赖：仅 git + Claude Code，不再需要 Python / jq / bash 脚本运行时
>
> 对从 v1.8.7 → v1.9.0 升级，参考 §0.0 v1.9.0 升级路径（待补，等 v1.9 release 后填）。

---

## 〇、升级路径速查（按当前本地版本）

如果你是已有 lifeos 用户，要升级到 v1.8.7，按本地版本对号入座：

### 0.1 从 v1.8.6 升级（zero-friction，推荐路径）

```bash
1. cd ~/.claude/skills/life_OS && git pull origin main
2. /version-check                       # 确认本地 1.8.7
3. /install-agents --refresh            # 装新 watch 命令（verify-release-and-watch）
4. /verify-release v1.8.7               # 跑 11 个 check，全 ✅ 或 (10 PASS + 1 WARN)
```

**无迁移命令**。首次 archiver wrap-up（用户说"退朝"或"adjourn"）时会自动：
- 创建 `gotchas.md`（带 14 条 v1.8.4-1.8.7 提炼的种子）
- archiver Phase 5 调 memory-keeper agent 完成 gotchas 抽取
- retrospective Mode 0 patrol 系统化为 7 system tasks（lifeos-001 ~ 007）

v1.8.7 新功能（全部按 spec 准备好，runtime 首次跑时激活）：
- C6 gotchas + memory-keeper agent
- B4 ScheduleWakeup self-driven loops
- F11 i18n diff parity check 9（WARN 级）
- F12 5 个 WHEN-NOT-TO-ADD 反模式边界文档
- B5 evals_scenarios 必填（planner 强制）
- A1 cascade seal spec proposal（仅 spec，archiver 不实施直到 v1.9/v2.0）
- A3 concept hotness 阈值显式化
- DR-10 md-only 本体论约束（无 escape hatch，永久承诺）
- E9 status line enum（22 agent 输出契约统一）
- E10 Conscious Patrol 路径 D（retrospective Mode 0 user-in-loop checkpoint）
- Karpathy 4 心法 + DA-1/DA-2/DA-3 default anti-patterns

详见 `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` 完整 RFC + DR-01 至 DR-11 决策审计。

### 0.2 从 v1.8.5 升级（跨 2 版本，需补 v1.8.6 中间）

v1.8.6 加了 md-only 强制（禁 `.yml` / `.json`），v1.8.7 又加 `.sql` / `.db` / `.sqlite` + 升级为本体论约束。

```bash
1. cd ~/.claude/skills/life_OS && git pull origin main   # 直接拉到 v1.8.7（v1.8.6 中间状态自动跳过）
2. /version-check                       # 1.8.5 → 1.8.7 跨版本提示自动出现
3. # 检查你本地 second-brain 是否含 .yml / .json / .sql / .db / .sqlite 文件（gitignored 例外不计）
4. find ~/<your-second-brain> -type f \( -name '*.yml' -o -name '*.json' -o -name '*.sql' -o -name '*.db' -o -name '*.sqlite' \) -not -path '*/\.git/*' -not -path '*/\.claude/settings*' | head -20
   # 找到的话，根据 DR-10 改 md 或加 gitignore 例外
5. /install-agents --refresh
6. /verify-release v1.8.7
```

**注意**：v1.8.5 → v1.8.7 跳过 v1.8.6 是安全的（v1.8.6 单纯禁扩展名扩展，v1.8.7 包含 v1.8.6 所有变更）。

### 0.3 从 v1.8.4 或更早 v1.8.x 升级（跨 ≥3 版本）

⚠️ 你跨过了 v1.8.5（hook layer 退役）+ v1.8.6（md-only YAML/JSON）+ v1.8.7（md-only ontological + 7 新功能 + E9/E10/Karpathy）。

每个 minor patch 都 non-breaking 但加了 HARD RULES。推荐顺序：

```bash
1. 先读 release notes 了解累计变更：
   - meta/release-notes/v1.8.5.md
   - meta/release-notes/v1.8.6.md（如有，否则看 CHANGELOG.md v1.8.6 段）
   - meta/release-notes/v1.8.7.md
2. 读 meta/rfc/v1.8.5-cleanup-and-hardening.md（hook 退役 + EOU hardening，影响面大）
3. 读 meta/rfc/v1.8.7-openhuman-borrowed-patterns.md（v1.8.7 决策审计）
4. 然后跟 v1.8.5 升级流程一样：git pull + /install-agents --refresh + /verify-release v1.8.7
5. 第一次 session start 前检查 v1.8.5 hook 退役相关：
   - 你的 ~/.claude/settings.json 里如果还有 life-os-* hook 注册，可保留也可清理（v1.8.5+ 不依赖 hook 但旧 hook 残留不影响）
```

### 0.4 从 v1.7.x 升级（major architectural change，最贵路径）

⚠️ v1.8.0 是"100% LLM-native" pivot — 删除全部 Python tools + 全部 cron infrastructure。后续 v1.8.1-v1.8.7 持续清理 / 加 hardening / 加新功能。

```bash
1. **先读 v1.8.0 release notes** — 这是 architectural break point
   - Python tools (memory.py / search.py / cli.py / 5 个 cron jobs) 全删
   - Cron 退役（setup-cron.sh + launchd plists 全删 — v1.8.0 pivot 决策见 hosts/CLAUDE.md §"Mode 1"）
2. 备份你的 second-brain（重大架构升级前的标准动作）
3. git pull origin main
4. 解除旧 cron / launchd（如有）：
   launchctl unload ~/Library/LaunchAgents/com.lifeos.*.plist 2>/dev/null
   crontab -l | grep -v lifeos | crontab -
5. 检查 .claude/settings.json 中 lifeos hook 残留（v1.8.5 退役后无需保留但不删也不报错）
6. /install-agents --refresh
7. /verify-release v1.8.7
```

v1.7 → v1.8.7 之间累积变更跨 ~8 个版本。第一次 session start 时 retrospective Mode 0 会跑跨版本检测并在 briefing 顶部输出升级摘要。

### 0.5 全新安装（不是升级）

如果是全新装：

```bash
# Claude Code
/install-skill https://github.com/jasonhnd/life_OS

# Gemini CLI / Antigravity / Codex CLI
npx skills add jasonhnd/life_OS
```

新装直接拿到 v1.8.7 状态，无需走升级流程。

---

## 一、快速判断：哪些已在 git 里、哪些没在

### ✅ 已在 GitHub（`git clone` 自动到手）

- 全部源码：`scripts/`、`agents/`、`hosts/`、`compliance/`、`themes/`、`evals/`、`references/`
- 全部规格：`SKILL.md`、`hosts/CLAUDE.md`、`references/*.md`（含 v1.7 Cortex 11 个 spec + 架构文档 + shipping report）
- 全部 i18n：`i18n/zh/`、`i18n/ja/`（README + CHANGELOG）
- 项目配置：`pyproject.toml`、`.python-version`、`Makefile`、`.github/workflows/test.yml`
- 合规公开记录：`compliance/violations.md`、`violations.example.md`

### 🚫 gitignore，必须手动复制

| 路径 | 内容 | 为什么不在 git |
|------|------|--------------|
| `.claude/CLAUDE.md` | 项目级 Claude Code 指令（含 5 项 HARD RULE 上朝触发约束）| `.claude/` 整目录被 gitignore |
| `.claude/settings.json` | dev repo 的 UserPromptSubmit hook 配置 | 同上 |
| `.claude/settings.local.json` | 本地用户自定义设置（如有）| 同上 |
| `compliance/2026-04-19-court-start-violation.md` | COURT-START-001 完整 incident 档案（473 行）| `compliance/*.md` 排除 violations.md/example |
| `docs/installation.md`、`docs/second-brain.md`、`docs/token-estimation.md` 三语 | 本地详细安装文档 | `docs/` 整目录被 gitignore（v1.6.3 b69187c 加的）|

### 🔧 完全在 repo 外（要在新机器重装）

| 路径 | 用途 |
|------|------|
| `~/.claude/projects/-Users-ms23m2-Google-Antigravity-life-os/memory/` | Claude 自动记忆（user/feedback/project memory）|
| `~/.claude/skills/life_OS/` | 安装版 skill（与 dev repo 不同——通过 `/install-skill` 重装）|
| `~/.claude/scripts/lifeos-version-check.sh` | setup-hooks.sh 部署的 SessionStart hook 脚本 |
| `~/.claude/scripts/lifeos-pre-prompt-guard.sh` | setup-hooks.sh 部署的 UserPromptSubmit hook 脚本 |
| `~/.claude/settings.json` | 全局 hooks 注册（被 setup-hooks.sh 改）|

### 系统依赖（新机器必装）

- Python 3.11+
- jq（hook 脚本依赖）
- bash（系统自带）
- git + GitHub 认证（SSH key 或 PAT）
- Claude Code CLI
- (可选) uv（Python 包管理 + 跑 `tools/cli.py` 子命令）
- (可选) pytest + ruff（开发期跑测试 / lint）

---

## 二、迁移步骤（按顺序）

### Step 1 · 旧机器：备份不在 git 的东西

在这台机器（`/Users/ms23m2/Google_Antigravity/life-os`）跑：

```bash
cd ~/Google_Antigravity/life-os

# 创建迁移包
mkdir -p ~/life-os-migration
cd ~/life-os-migration

# 1. 把 dev repo 里 gitignore 的关键文件打包
tar czf dev-repo-private.tar.gz \
  -C ~/Google_Antigravity/life-os \
  .claude/CLAUDE.md \
  .claude/settings.json \
  $([ -f ~/Google_Antigravity/life-os/.claude/settings.local.json ] && echo .claude/settings.local.json) \
  compliance/2026-04-19-court-start-violation.md \
  docs/

# 2. 把 Claude 自动记忆打包
# 注意：路径开头 "-" 会被 BSD tar 当 flag，必须用 "./" 前缀
if [ -d ~/.claude/projects/-Users-ms23m2-Google-Antigravity-life-os/memory ]; then
  tar czf claude-memory.tar.gz \
    -C ~/.claude/projects \
    ./-Users-ms23m2-Google-Antigravity-life-os/memory/
  echo "✅ memory 已打包"
else
  echo "(no project memory found — skipping)"
fi

# 3. 全局 Claude settings.json（含 hooks 注册）
cp ~/.claude/settings.json claude-global-settings.json 2>/dev/null

# 4. 列清单
ls -la
echo ""
echo "Migration package contents:"
ls -la ~/life-os-migration/
```

### Step 2 · 旧机器 → 新机器：传输

选一个：
- AirDrop（最简单，Mac 之间）
- iCloud Drive 共享文件夹
- USB 拷贝
- `scp -r ~/life-os-migration/ new-mac:~/`

### Step 3 · 新机器：装系统依赖

```bash
# Homebrew (如果没装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 必装
brew install python@3.11 jq git gh
brew install --cask claude-code  # 或从官网下

# 可选
brew install uv ruff
python3.11 -m pip install --user pyyaml pytest

# GitHub 认证（用 gh 或者复制 SSH key）
gh auth login
# 或 cp ~/.ssh/id_ed25519* (从旧机器) → ~/.ssh/
```

### Step 4 · 新机器：clone 仓库

```bash
mkdir -p ~/Google_Antigravity
cd ~/Google_Antigravity

git clone https://github.com/jasonhnd/life_OS.git life-os
cd life-os

# 验证：应该看到今天 44 个 commits + 5 个 tags
git log --oneline | head -10
git tag --list --sort=-v:refname | head -5
```

### Step 5 · 新机器：恢复 gitignored 文件

```bash
cd ~/Google_Antigravity/life-os

# 解包刚才传过来的私有文件
tar xzf ~/life-os-migration/dev-repo-private.tar.gz

# 验证
ls -la .claude/CLAUDE.md .claude/settings.json
ls -la compliance/2026-04-19-court-start-violation.md
ls docs/
```

### Step 6 · 新机器：恢复 Claude 自动记忆

```bash
# 重要：路径硬编码到旧用户名 ms23m2 — 新机器用户名不同的话需要改
# 假设新用户名也是 ms23m2，路径不变：
mkdir -p ~/.claude/projects/
tar xzf ~/life-os-migration/claude-memory.tar.gz \
  -C ~/.claude/projects/

# 如果新机器 cwd 路径不同（比如 ~/Code/life-os 而非 ~/Google_Antigravity/life-os），
# 需要重命名 memory 目录：
# mv ~/.claude/projects/-Users-ms23m2-Google-Antigravity-life-os \
#    ~/.claude/projects/-Users-{new}-{new-path}
```

### Step 7 · 新机器：装 life_OS skill 到 ~/.claude/

```bash
# 用 Claude Code 装最新 release
claude code
# 然后在 Claude Code 里：
> /install-skill https://github.com/jasonhnd/life_OS

# 或手动：
mkdir -p ~/.claude/skills
cp -r ~/Google_Antigravity/life-os ~/.claude/skills/life_OS
```

### Step 8 · 新机器：注册 hooks（v1.6.3a 加的自动安装）

> ⚠️ **v1.8.5+ OBSOLETE** — `setup-hooks.sh` 已退役（hook layer 整体退役）。当前路径：在 Claude Code 跑 `/install-agents` slash 命令注册 agent wrappers。下方说明仅作历史参考。

```bash
# pre-v1.8.5 only — script no longer exists
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```

这个脚本曾经会：
1. 把 `lifeos-version-check.sh` + `lifeos-pre-prompt-guard.sh` 拷贝到 `~/.claude/scripts/`
2. 在 `~/.claude/settings.json` 注册 SessionStart + UserPromptSubmit hooks
3. 是幂等的——已注册的会跳过

如果你之前在旧机器手动改过 `~/.claude/settings.json`，可以参考 `claude-global-settings.json`（迁移包里那份）merge 自定义部分。

### Step 9 · ~~新机器：装 Python deps~~（v1.8.1+ OBSOLETE）

> ⚠️ **v1.8.1+ OBSOLETE** — Layer 4 Python tools/ 在 v1.8.1 Wave 2 整体删除（zero-python pivot）。当前 lifeos 是 100% markdown，不需要 Python。下方说明仅作历史参考。

```bash
# pre-v1.8.1 only — tools/ deleted entirely
cd ~/Google_Antigravity/life-os
uv sync --extra dev
```

### Step 10 · 新机器：验证

> ⚠️ **大部分子步骤 v1.8.1/v1.8.5+ OBSOLETE** — make test / make bash-check / make lint / Python CLI / hook 触发测试都依赖已退役的层。**当前验证**：跑 `/verify-release v1.9.0`（slash 命令，含 11 check）。下方说明仅作历史参考。

```bash
# pre-v1.8.5 historical verification (most steps no longer applicable)
cd ~/Google_Antigravity/life-os

# 1. 184 个测试 (v1.8.1 deleted Python; no longer available)
# make test

# 2. Bash 脚本语法 (v1.8.5 deleted scripts/hooks/*.sh; no longer available)
# make bash-check

# 3. lint (Python deleted)
# make lint

# 4. CLI smoke (tools/cli.py deleted v1.8.1)
# python3 tools/cli.py list

# 5. Hook 触发测试 (scripts/lifeos-pre-prompt-guard.sh deleted v1.8.5)
# echo '{"prompt":"上朝"}' | bash scripts/lifeos-pre-prompt-guard.sh | head -3

# 7. Git 状态干净 (still applicable)
git status
# 期望: working tree clean
```

**v1.9.0 当前验证路径**：在 Claude Code 中跑 `/verify-release v1.9.0` slash 命令。

### Step 11 · 新机器：实战

打开新 session 测试：

```bash
cd ~/Google_Antigravity/life-os
# 启动 Claude Code，发"上朝"
# 验证 5 层防御真触发：
# - L1 hook 在你说"上朝"时注入 reminder（看到 system-reminder 块）
# - L2 ROUTER 输出 🌅 Trigger: ... → Action: Launch(retrospective) Mode 0
# - L3 retrospective 子代理首句 ✅ I am the RETROSPECTIVE subagent
# - L4 末尾出 🔱 ✅ Compliance Patrol passed (AUDITOR Mode 3)
# - L5 跑 evals/run-eval.sh start-session-compliance（待 claude -p 实测）
```

---

## 三、新机器上的差异点

如果新用户名 ≠ `ms23m2`：
- 改 `~/.claude/projects/-Users-{你的}-Google-Antigravity-life-os/memory/` 路径
- 旧路径里的硬编码（如 `compliance/violations.md` 的 `<system-reminder>` 路径）会自适应——hook 用 `$CLAUDE_PROJECT_DIR` 解析

如果新 cwd 路径 ≠ `~/Google_Antigravity/life-os`：
- Claude 自动记忆 memory 目录命名包含路径，需重命名（见 Step 6）

如果新机器没装 jq：
- `setup-hooks.sh` 会报错并给出手动配置指引

---

## 四、最小迁移（懒人版）

如果你只关心 dev repo 本身、不要 hooks、不要自动记忆：

```bash
# 新机器
brew install git python@3.11
gh auth login
cd ~/wherever
git clone https://github.com/jasonhnd/life_OS.git life-os
cd life-os
python3.11 -m pip install --user pyyaml pytest
make test  # 验证 184 测试通过
```

完事。可以开发但少了：项目级 HARD RULE 强制（`.claude/CLAUDE.md`）、本地 hook 防御、Claude 跨 session 记忆。能 commit/push 即可。

---

## 五、迁移包内容核对清单

打包后检查（旧机器）：

```bash
ls -la ~/life-os-migration/
# 应该有：
# dev-repo-private.tar.gz       (.claude/ + compliance/{incident}.md + docs/)
# claude-memory.tar.gz          (Claude 自动记忆，可能为空)
# claude-global-settings.json   (~/.claude/settings.json 副本)
```

新机器解包后核对：

```bash
cd ~/Google_Antigravity/life-os
ls -la .claude/
# 应有：CLAUDE.md, settings.json (+ settings.local.json 如果有)

ls compliance/
# 应有：violations.md, violations.example.md (in git) + 2026-04-19-court-start-violation.md (just restored)

ls docs/ i18n/zh/docs/ i18n/ja/docs/
# 应有：installation.md, second-brain.md, token-estimation.md ×3 langs

ls ~/.claude/projects/-Users-{你}-Google-Antigravity-life-os/memory/
# 应有：MEMORY.md + 若干 .md 记忆文件
```

---

## 六、常见问题

**Q: GitHub repo 里有敏感信息吗？**
A: 没有。所有 PII（人名、金额、具体公司、家人朋友）都被 archiver Phase 2 的 privacy filter 过滤了。compliance/ 里的 incident 档案被 gitignore（含个人 use repo 的对话引用）。

**Q: 我在旧机器有些 v1.6.3 之前的 commits 还没 push 怎么办？**
A: 跑 `git log origin/main..HEAD` 看本地超前 commits。如果有：先 push 再迁移。今天的 44 commits 我全部 push 了，应该没残留。

**Q: 新机器装完后 Cortex 默认是 OFF 吗？**
A: 是。dev repo 里没有 `meta/config.md`（dev repo 不是 second-brain）。只有在 use repo 才会读 cortex_enabled 配置。dev repo 始终 dev 模式。

**Q: 我可以同时用两台机器吗？**
A: 可以——v1.4.2 outbox 架构就是为多设备并行设计的。每台机器开 session 时各写自己 outbox，下次 Start Session 时合并。但 dev repo 跨机器要小心 git push/pull 顺序，避免 force-push。

**Q: skill 装完后还要做什么？**
A: 跑一次 `setup-hooks.sh` 注册 hooks（Step 8）。然后开 Claude Code 测一次"上朝"看 5 层防御是否真激活（Step 11）。

---

## 七、关联文档

- `docs/history/v1.7-shipping-report-2026-04-21.md` — 今天的 shipping 全景
- `references/cortex-architecture.md` — Cortex 数据流
- `compliance/2026-04-19-court-start-violation.md` — COURT-START-001 incident 档案（迁移包里）
- `docs/installation.md` — 标准安装指引（迁移包里）
- `Makefile` — `make help` 看所有 dev 命令
