# Life OS Eval 体系

用固定场景反复测试 Draft-Review-Execute 和 Six Domains 流程的输出质量，量化一致性和合规性。

## 使用方法

### 手动测试

在 Claude Code 中安装 life-os skill 后，直接输入场景中的用户消息，观察完整流程输出。

### 自动化测试

在 Claude Code 里运行 `/run-eval` slash 命令（替代已退役的 `evals/run-eval.sh`——属于 v1.8.5 hook 层退役 + md-only 本体约束的一部分）：

```
/run-eval                 # 跑所有场景
/run-eval resign-startup  # 按名字 glob 跑单个场景
```

`/run-eval` 用 `claude -p` 批处理模式逐个跑场景，输出保存到 `evals/outputs/`。完整流程见 `.claude/commands/run-eval.md`。

## 目录结构

```
evals/
├── README.md              # 本文件
├── scenarios/             # 固定测试场景（*.md——路由、合规、版本专项）
├── regression-fixtures/   # 回归用例 fixture（*.md）
├── rubrics/               # 评分标准
│   ├── agent-output-quality.md    # 各 agent 输出质量
│   └── orchestrator-compliance.md # 流程合规性
└── outputs/               # 测试输出（gitignored）
```

## 评估维度

1. **格式合规**：各 agent 是否遵循指定的输出格式
2. **评分分布**：是否全部 7-8 分（面子分检测）
3. **Reviewer 实质性**：是否每次都准奏（走形式检测）
4. **信息隔离**：agent 输出有没有引用它不该看到的内容
5. **可执行性**：行动建议是否具体到可执行
6. **一致性**：同一场景跑多次，核心结论是否一致
7. **快车道路由**：非决策类请求是否正确触发快车道而非完整朝议
8. **领域选择准确性**：Router/Planner 是否为场景选择了正确的领域
9. **Wiki 提取质量**：Archiver 在 End Session 时是否将可复用结论提取到 wiki
