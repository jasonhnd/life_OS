# 运行 Eval 套件

怎么跑、怎么读输出、怎么接 CI。针对 `/run-eval` slash 命令的操作手册（取代已退役的 `evals/run-eval.sh`——v1.8.5 hook 层退役、md-only 本体约束；完整规范见 `.claude/commands/run-eval.md`）。

---

## 前提条件

1. **本机装了 `claude` CLI**，且能以 `-p`（print，headless）模式运行。验证：

   ```bash
   echo "hello" | claude -p --output-format text
   ```

   应该返回一段 assistant 回复，没错就能跑 eval。

2. **当前 session 能找到 life-os skill**。在 Claude Code 里确认 `/skills` 列表能看到 `life_OS` 或 `anthropic-skills:life-os`。

3. **`/run-eval` 命令已安装**。在 Claude Code 里输入 `/` 能看到 `run-eval`（`/install-agents --refresh` 会把 `.claude/commands/run-eval.md` 装到 `~/.claude/commands/`）。

---

## 跑所有场景

```
/run-eval
```

这会按字典序把 `evals/scenarios/*.md` 里所有场景都跑一遍。输出示例：

```
── /run-eval · 20260419_231245 ──
场景数: 6

🏃 council-debate
   输出: evals/outputs/council-debate-20260419_231245.md
   ✅ PASS (exit 0)

🏃 fengbo-loop
   输出: evals/outputs/fengbo-loop-20260419_231245.md
   ✅ PASS (exit 0)

...

=== 结果汇总 ===
  PASS council-debate
  PASS fengbo-loop
  PASS large-purchase
  PASS relationship
  PASS resign-startup
  PASS router-triage

通过: 6 / 失败: 0 / 总计: 6
输出目录: evals/outputs
```

---

## 跑单个场景

```
/run-eval resign-startup
```

参数是 glob 过滤，匹配 `evals/scenarios/` 下的文件名（去掉 `.md`）。如果没有任何场景匹配，`/run-eval` 会列出所有可用场景并停下。

---

## `/run-eval` 内部是怎么工作的

`/run-eval` 不是 bash 脚本，而是 `.claude/commands/run-eval.md` 里的 slash 命令规范，由 Claude 在 Claude Code 里逐个场景执行。核心逻辑：

1. **前置检查**：`command -v claude` 确认 CLI 在。找不到（或设了 `LIFEOS_EVAL_SKIP_CLAUDE=1`）就打印 `⏭ skipping all eval scenarios (claude CLI unavailable)` 并 exit 0——跳过不算失败。

2. **列场景**：`ls evals/scenarios/*.md`，有参数就按 glob 过滤。

3. **提取 user message**：从 scenario 文件 `## User Message` / `## 用户消息` / `## ユーザーメッセージ` 下的 fenced code block 取输入（三语标题都认）。抽不出来（场景文件格式坏了）→ 标记 schema error 并 FAIL。

4. **管道给 `claude -p`**：

   ```bash
   claude -p --output-format text > evals/outputs/<scenario>-<timestamp>.md
   ```

   `--output-format text` 是关键——输出纯文本，不带 JSON wrapping，方便后续人工阅读和 diff。

5. **核对预期 + 退出码**：检查输出里该出现的 subagent launch 行、scenario `Expected Behavior` 里点名的关键模式。Exit 0 且预期满足 → PASS；否则 FAIL，把 stderr 追加到输出文件末尾便于排查。

6. **最后汇总**：打印每个场景的 PASS/FAIL，任一失败则整体 exit 1，CI 能感知到。

---

## 读输出

每次运行产生：

```
evals/outputs/{scenario_name}-{YYYYMMDD_HHMMSS}.md
```

文件内容就是 `claude -p` 返回的完整 agent 输出——Summary Report、六部分析、REVIEWER 审议、AUDITOR 反馈等全部按主题语言写在里面。

打开之后要按 `rubrics/` 对照看：

- `rubrics/agent-output-quality.md` — 逐 agent 0-2 分打分
- `rubrics/orchestrator-compliance.md` — 14 项流程 checklist

---

## 解读 PASS / FAIL

**重要警告**：PASS 只意味着 `claude -p` 进程退出码是 0 且声明的预期模式命中——**不代表输出质量过关**。

`/run-eval` 检测不了：

- REVIEWER 该否决却批准了
- 六部分数都给 7-8 的 face-saving
- 信息隔离被破坏（PLANNER 引用了 ROUTER 的推理）
- Wiki 萃取到了不该有的隐私信息

这些要**人工按 rubrics 打分**。PASS 只是「系统没崩 + 基本结构对」；质量好不好是另一个问题。

FAIL 则是明确信号：

- schema error → scenario 文件格式坏了（`## User Message` 节点缺了或没用 code block）
- exit != 0 → `claude` 本身挂了（网络、模型限流、skill 没装上）

---

## outputs/ 目录

```
evals/outputs/
├── council-debate-20260419_231245.md
├── council-debate-20260420_091502.md       # 同场景多次运行 → 比对一致性
├── fengbo-loop-20260419_231245.md
├── ...
```

- **已 gitignore**：不进版本库。每个人本地跑的结果互不污染。
- **不自动清理**：`/run-eval` 不会删历史 output。要回溯历史比较时很有用，但要自己定期清理（`rm evals/outputs/*-2026*.md`）。
- **按时间戳分文件**：同一场景多次运行不会互相覆盖，可以 `diff evals/outputs/council-debate-*.md` 看不同版本的输出差异。

---

## CI 集成

**现状**：仓库未配置 CI（没有 `.github/`）。eval 通过 `/run-eval` slash 命令在 Claude Code 里本地跑——slash 命令是 Claude 内部流程，不是能直接塞进 GitHub Actions 的 bash step。

如果以后要脚本化进 CI，思路是绕过 slash 命令、直接用 `claude -p` 包一层（`/run-eval` 内部就是这么调的）：逐个 scenario 抽 `## User Message` → `claude -p --output-format text` → 检查退出码与预期模式 → 任一失败 `exit 1`。

**路径触发很重要**（给未来 CI 的建议）：只有改了 `SKILL.md` / `hosts/` / `agents/` / `compliance/` / `gotchas.md` / `themes/` / `references/` 才值得跑 eval。改 `docs/` 或 `CHANGELOG` 不用跑——会烧 API 额度。

---

## 常见问题排查

### 跑不起来，stderr 说 `command not found: claude`

PATH 里没有 `claude`。确认装了 Claude Code CLI，确认可以在 shell 里直接 `claude --version`。

### 跑起来了但每个场景都 exit 1

打开 `evals/outputs/{name}-*.md` 看末尾的 STDERR 段。常见原因：

- 模型 rate limit → 等一下再跑或换一个 account
- skill 没被加载 → 在 Claude Code 里 `/skills` 确认 `life_OS` 在列表里
- 网络问题 → `ping api.anthropic.com`

### 场景跑过了但输出看起来不对

这就是 eval 系统的核心功能——用 `rubrics/` 人工打分。`/run-eval` 只管「进程没崩 + 结构命中」。输出质量要自己看。

### 想加新场景怎么办

去 [写新 eval 场景](writing-new-scenarios.md)。

---

## 日常使用建议

- **每次改 SKILL.md 或 hosts/CLAUDE.md 之后跑一次**（3-5 分钟）
- **发版前跑一次全套**（6 个场景，~10 分钟）
- **发版后跑一次回归**确认 production 装完还能跑
- **定期每月跑一次 consistency 检查**：同一场景跑 3 次，diff 看结果稳不稳
