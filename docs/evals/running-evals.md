# 运行 Eval 套件

怎么跑、怎么读输出、怎么接 CI。针对 `evals/run-eval.sh` 的操作手册。

---

## 前提条件

1. **本机装了 `claude` CLI**，且能以 `-p`（print，headless）模式运行。验证：

   ```bash
   echo "hello" | claude -p --output-format text
   ```

   应该返回一段 assistant 回复，没错就能跑 eval。

2. **当前 session 能找到 life-os skill**。在 Claude Code 里确认 `/skills` 列表能看到 `life_OS` 或 `anthropic-skills:life-os`。

3. **脚本有执行权限**：`chmod +x evals/run-eval.sh`（通常 clone 下来就有）。

---

## 跑所有场景

```bash
./evals/run-eval.sh
```

这会按字典序把 `evals/scenarios/*.md` 里所有场景都跑一遍。输出示例：

```
=== Life OS Eval Runner ===
时间: 20260419_231245
场景数: 6

🏃 运行场景: council-debate
   输出: /path/to/evals/outputs/council-debate_20260419_231245.md
   ✅ 通过 (exit 0)

🏃 运行场景: fengbo-loop
   输出: /path/to/evals/outputs/fengbo-loop_20260419_231245.md
   ✅ 通过 (exit 0)

...

=== 结果汇总 ===
  PASS council-debate
  PASS fengbo-loop
  PASS large-purchase
  PASS relationship
  PASS resign-startup
  PASS router-triage

通过: 6 / 失败: 0 / 总计: 6
输出目录: /path/to/evals/outputs
```

---

## 跑单个场景

```bash
./evals/run-eval.sh resign-startup
```

场景名就是 `evals/scenarios/` 下的文件名去掉 `.md`。路径安全：脚本用 `basename` 取，防止 `../../etc/passwd` 这种 traversal。

如果场景名不存在，脚本会列出所有可用场景并退出。

---

## 脚本内部是怎么工作的

`evals/run-eval.sh` 的关键逻辑（约 100 行）：

1. **提取 user message**：用 `sed` 从 scenario 文件里 `## 用户消息` / `## User Message` / `## ユーザーメッセージ` 下的 fenced code block 抽出内容。三语标题都支持。

   ```bash
   user_message=$(sed -n '/^## \(用户消息\|User Message\|ユーザーメッセージ\)/,/^## /{/```/,/```/{/```/d;p;}}' "$scenario_file")
   ```

   如果抽不出来（场景文件格式坏了），标记为 schema error 并 FAIL。

2. **管道给 claude -p**：

   ```bash
   echo "$user_message" | claude -p --output-format text > "$output_file" 2>"${output_file}.stderr"
   ```

   `--output-format text` 是关键——输出纯文本，不带 JSON wrapping，方便后续人工阅读和 diff。

3. **处理退出码**：

   - Exit 0 → PASS
   - Exit ≠ 0 → FAIL，把 stderr 追加到输出文件末尾便于排查

4. **最后汇总**：打印每个场景的 PASS/FAIL，脚本整体有任一失败则 exit 1，CI 能感知到。

---

## 读输出

每次运行产生：

```
evals/outputs/{scenario_name}_{YYYYMMDD_HHMMSS}.md
```

文件内容就是 `claude -p` 返回的完整 agent 输出——Summary Report、六部分析、REVIEWER 审议、AUDITOR 反馈等全部按主题语言写在里面。

打开之后要按 `rubrics/` 对照看：

- `rubrics/agent-output-quality.md` — 逐 agent 0-2 分打分
- `rubrics/orchestrator-compliance.md` — 14 项流程 checklist

---

## 解读 PASS / FAIL

**重要警告**：PASS 只意味着 `claude -p` 进程退出码是 0——**不代表输出质量过关**。

脚本检测不了：

- REVIEWER 该否决却批准了
- 六部分数都给 7-8 的 face-saving
- 信息隔离被破坏（PLANNER 引用了 ROUTER 的推理）
- Wiki 萃取到了不该有的隐私信息

这些要**人工按 rubrics 打分**。PASS 只是「系统没崩」；质量好不好是另一个问题。

FAIL 则是明确信号：

- schema error → scenario 文件格式坏了（`## User Message` 节点缺了或没用 code block）
- exit != 0 → `claude` 本身挂了（网络、模型限流、skill 没装上）

---

## outputs/ 目录

```
evals/outputs/
├── council-debate_20260419_231245.md
├── council-debate_20260420_091502.md       # 同场景多次运行 → 比对一致性
├── fengbo-loop_20260419_231245.md
├── ...
```

- **已 gitignore**：不进版本库。每个人本地跑的结果互不污染。
- **不自动清理**：脚本不会删历史 output。要回溯历史比较时很有用，但要自己定期清理（`rm evals/outputs/*_2026*.md`）。
- **按时间戳分文件**：同一场景多次运行不会互相覆盖，可以 `diff evals/outputs/council-debate_*.md` 看不同版本的输出差异。

---

## CI 集成

`run-eval.sh` 在任一场景失败时 `exit 1`，可以直接用在 GitHub Actions：

```yaml
# .github/workflows/eval.yml（示例，目前未配置）
name: Eval regression
on:
  pull_request:
    paths:
      - 'SKILL.md'
      - 'pro/**'
      - 'themes/**'
      - 'references/**'

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install claude CLI
        run: |
          # 按 Anthropic 官方安装路径装
          npm install -g @anthropic-ai/claude
      - name: Authenticate
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: claude auth
      - name: Run eval suite
        run: ./evals/run-eval.sh
      - name: Upload outputs on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: eval-outputs
          path: evals/outputs/
```

**路径触发很重要**：只有改了 SKILL.md / pro/ / themes/ / references/ 才跑 eval。改 docs/ 或改 CHANGELOG 不用跑——会烧 API 额度。

**Failure artifact**：失败时把 outputs/ 上传成 artifact，可以下载下来本地看，不用开 CI 的 log 挨条翻。

**目前现状**：CI 还没接入。本地手动跑。下一个 minor version 考虑加。

---

## 常见问题排查

### 跑不起来，stderr 说 `command not found: claude`

PATH 里没有 `claude`。确认装了 Claude Code CLI，确认可以在 shell 里直接 `claude --version`。

### 跑起来了但每个场景都 exit 1

打开 `evals/outputs/{name}_*.md` 看末尾的 STDERR 段。常见原因：

- 模型 rate limit → 等一下再跑或换一个 account
- skill 没被加载 → 在 Claude Code 里 `/skills` 确认 `life_OS` 在列表里
- 网络问题 → `ping api.anthropic.com`

### 场景跑过了但输出看起来不对

这就是 eval 系统的核心功能——用 `rubrics/` 人工打分。脚本只管「进程没崩」。输出质量要自己看。

### 想加新场景怎么办

去 [写新 eval 场景](writing-new-scenarios.md)。

---

## 日常使用建议

- **每次改 SKILL.md 或 pro/CLAUDE.md 之后跑一次**（3-5 分钟）
- **发版前跑一次全套**（6 个场景，~10 分钟）
- **发版后跑一次回归**确认 production 装完还能跑
- **定期每月跑一次 consistency 检查**：同一场景跑 3 次，diff 看结果稳不稳
