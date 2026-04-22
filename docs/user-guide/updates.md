# 更新 · 查看版本、升级、读 CHANGELOG

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Life OS 迭代很快。v1.6.x 阶段每 2-3 周一个小版本，每 1-2 月一个 feature release。你需要知道：

1. 当前装的是什么版本
2. 什么时候升级
3. 怎么升级
4. 新版本里有什么

这篇讲这些。

---

## 查看当前版本

### 方法 1 · SKILL.md front matter

Life OS 的版本号存在 `SKILL.md` 最顶端：

```yaml
---
name: life-os
version: "1.6.2a"
description: "..."
---
```

这是权威源。其他所有地方的版本号（3 份 README、3 份 CHANGELOG）必须和这里一致。

查看方式：

```bash
head -5 ~/.claude/skills/life_OS/SKILL.md
```

或者直接在 CC 会话里问："当前 Life OS 版本？" — ROUTER 会读 SKILL.md 告诉你。

### 方法 2 · 晨报

每次 Start Session 的 18 步流程里，Step 8（Platform + Version Check）会把本地版本 + GitHub 最新版本都放进晨报：

```
🏛️ Life OS v1.6.2a (local) · v1.6.3 (latest on GitHub) — 有更新可用
```

如果最新版本更新了 → 晨报会提醒。

### 方法 3 · 每日自动检查

如果装了 `setup-hooks.sh`（见下方），每天第一次 Session Start 会调用 `lifeos-version-check.sh`，自动 WebFetch 最新版本做对比。不用手动查。

---

## 每个平台的更新命令

Life OS 是一个 skill，不是 npm 包 — 没有统一的 `lifeos update`。但每个平台有自己的升级方式。

### Claude Code（skill）

```bash
cd ~/.claude/skills/life_OS && git pull
```

或者 CC 会话里说：

```
你：升级 Life OS
ROUTER：检查到 v1.6.3 可用。执行 git pull...
        ✅ 升级到 v1.6.3。
```

升级后：下一次 Start Session 会自动生效。正在运行的会话不受影响（已加载的 SKILL.md 不会重读）。

### Claude Desktop（.claude.json 里注册的 skill）

Life OS skill 本质也是一个 git repo。`cd` 到 skill 目录 `git pull`。重启 Claude Desktop。

### Gemini CLI

Gemini CLI 的 skills 机制不同 — 每个平台 orchestrator 文件（`pro/GEMINI.md`）独立维护。升级步骤：

1. `cd ~/.gemini/skills/life_OS && git pull`（或你的本地 skill 路径）
2. Gemini 下次启动自动读新版本。

### Codex CLI

同理：

1. `cd ~/.codex/skills/life_OS && git pull`
2. `pro/AGENTS.md` 是 Codex 的 orchestrator 文件。

### 手动升级（fallback）

不想用 git pull？直接去 GitHub repo 下载 zip，解压覆盖本地 skill 目录。

保留你自己的 `_meta/` + `projects/` + `areas/` 不动（那是 second-brain，不是 skill 代码）。

---

## In-Session 触发词

会话中途想升级？说 "update" / "升级" / "更新"。

```
你：update

ROUTER：
  当前版本: v1.6.2a (2026-04-15)
  最新版本: v1.6.3 (2026-04-20)
  
  v1.6.3 更新内容:
  - 新增：xxx
  - 修复：xxx
  
  升级操作:
  $ cd ~/.claude/skills/life_OS && git pull
  
  升级后本次会话不会切换到新版本，下次 Start Session 生效。
  
  要我现在执行吗？(y/n)

你：y

ROUTER：
  [执行 cd + git pull]
  ✅ 升级完成。下次 Start Session 自动使用 v1.6.3。
```

ROUTER 做的事：读本地 SKILL.md 当前版本 + WebFetch 远程最新版本 + 对比 + 展示 CHANGELOG 摘要 + 可选执行 git pull。

### 为什么升级不影响当前会话

SKILL.md 是 CC 在会话开始时加载的。会话运行中 CC 不会重读。所以：

- 你现在这个会话用的还是旧版本。
- 下次 Start Session → 读最新 SKILL.md → 走新流程。

如果急需用新版本特性 → 退朝本次会话 + 重新 Start Session。

---

## 每日自动检查 · setup-hooks.sh

Claude Code 有 hooks 机制可以在 Session Start 时自动执行脚本。Life OS 附带一个每日版本检查的 hook。

### 安装

```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```

做的事：

1. Pre-flight：检查 jq 依赖 + settings.json 有效性。
2. 把 `lifeos-version-check.sh` 复制到 `~/.claude/scripts/`。
3. 给 `~/.claude/settings.json` 加一个 SessionStart hook，id = `session:lifeos-version-check`。

安装是幂等的 — 可以重复跑不会重复加 hook。

### 效果

每次 CC Session Start（不只是 Life OS 的上朝，任何 CC 会话启动）会调用脚本。脚本：

1. 检查上次执行时间。
2. 如果距上次 < 24h → 跳过（避免频繁查 GitHub）。
3. 距上次 ≥ 24h → WebFetch GitHub 的 SKILL.md 拿最新版本。
4. 对比本地 SKILL.md。
5. 如果有新版 → 在会话开头输出一行提示："🏛️ Life OS v1.6.3 可用（本地 v1.6.2a）"。

不升级没事 — 只是提醒。你决定什么时候升。

### 卸载

去 `~/.claude/settings.json` 删 `session:lifeos-version-check` 那项。

---

## 怎么读 CHANGELOG

Life OS 有 3 份 CHANGELOG（三语 HARD RULE）：

- `CHANGELOG.md` — 英文
- `i18n/zh/CHANGELOG.md` — 中文
- `i18n/ja/CHANGELOG.md` — 日文

中文的在 `i18n/zh/`。升级前读这个。

### 格式

```markdown
# CHANGELOG

## v1.6.2a · 2026-04-15

### Fixes
- 修复 Notion sync 在 orchestrator 上下文丢失的问题

## v1.6.2 · 2026-04-12

### Features
- Adjourn 防御：检测非法转移
- wiki/SOUL 自动写入
- DREAM 10 个 triggered_actions
- 设计 refinements

### Breaking
- （如有）

### Migration
- （如需手动迁移说明）

## v1.6.1 · ...
```

### 关注什么

按优先级：

1. **Breaking**（破坏性变更）— 必读。会影响你的 second-brain 数据或工作流。
2. **Migration**（迁移指南）— 升级前必做的手动步骤。
3. **Features**（新特性）— 看看有没有想用的。
4. **Fixes**（修复）— 如果你之前被 bug 坑过，看有没有修好。
5. **Internal**（内部）— 一般不用看。

### Semver 约定

Life OS 松散遵守 semver：

- **Major**（1.x → 2.0）：数据模型不兼容。需要手动迁移 second-brain。
- **Minor**（1.6 → 1.7）：新功能。向后兼容。second-brain 不需动。
- **Patch**（1.6.2 → 1.6.2a）：bug 修复。安全升级。

字母后缀（`a`、`b`）= hotfix。通常在同一个 minor 里快速修一个 bug。

**v2.0 目前还没发布**。所有变更在 1.x 内。

---

## 升级前的清单

正常升级不需要做任何准备。但以下情况要注意：

### Major 版本升级

看 CHANGELOG 的 Breaking + Migration 段。通常要：

1. 退朝当前所有会话（保证所有 outbox 合并完）。
2. 本地 second-brain git pull + git push（保持和远程一致）。
3. 运行 CHANGELOG 里给的迁移脚本（如果有）。
4. 升级 skill。
5. Start Session 验证。

### 关键决策进行中

如果你在一个复杂决策的中途（3D6M 走了一半），先退朝 → 升级 → 重新 Start Session 继续。不要升级一半让当前会话跑在混合状态。

### 多台设备

如果你在多台设备上用 Life OS（桌面 + 笔记本 + 手机），升级一台后：

- 二次同步会自动处理兼容问题。
- 但如果是 Major 升级，建议所有设备一起升，避免一台新版一台旧版写出格式不一致的数据。

---

## 降级

极少需要，但要做可以：

```bash
cd ~/.claude/skills/life_OS
git checkout v1.6.1   # 或任何历史 tag
```

降级后 next Session Start 用旧版本。

注意：**如果新版本写了新数据结构**（比如 v1.6.0 加了 strategic 字段），降级到 v1.5.x 可能读不懂那些字段。不会崩，但会忽略。

实际操作：Life OS 的每次升级都保持向后兼容读取 — 老版本总能读新版本写的东西，哪怕忽略一些字段。所以降级基本安全。

---

## 一句话总结

**日常**：

- 查版本 → 晨报里看，或 `head -5 SKILL.md`。
- 升级 → `cd skill-dir && git pull`，或会话里说 "update"。
- 新版本有什么 → 读 `i18n/zh/CHANGELOG.md`。

**少见操作**：

- 自动每日检查 → `bash scripts/setup-hooks.sh`（装一次）。
- 降级 → `git checkout {tag}`。
- Major 升级 → 读 Migration + 先同步所有设备。

升级不危险。不升级也不危险。有新功能想用了再升。
