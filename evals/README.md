# Life OS Eval 体系

用固定场景反复测试三省六部流程的输出质量，量化一致性和合规性。

## 使用方法

### 手动测试

在 Claude Code 中安装 life-os skill 后，直接输入场景中的用户消息，观察完整流程输出。

### 自动化测试

```bash
# 跑所有场景
./evals/run-eval.sh

# 跑单个场景
./evals/run-eval.sh resign-startup
```

脚本使用 `claude -p` 逐个跑场景，输出保存到 `evals/outputs/` 目录。

## 目录结构

```
evals/
├── README.md              # 本文件
├── run-eval.sh            # 自动化测试脚本
├── scenarios/             # 固定测试场景
│   ├── resign-startup.md  # 辞职创业（全六部）
│   ├── large-purchase.md  # 大额消费（户部+兵部+刑部）
│   └── relationship.md    # 人际关系（吏部+工部+刑部+礼部）
├── rubrics/               # 评分标准
│   ├── agent-output-quality.md    # 各 agent 输出质量
│   └── orchestrator-compliance.md # 流程合规性
└── outputs/               # 测试输出（gitignored）
```

## 评估维度

1. **格式合规**：各 agent 是否遵循指定的输出格式
2. **评分分布**：是否全部 7-8 分（面子分检测）
3. **门下省实质性**：是否每次都准奏（走形式检测）
4. **信息隔离**：agent 输出有没有引用它不该看到的内容
5. **可执行性**：行动建议是否具体到可执行
6. **一致性**：同一场景跑多次，核心结论是否一致
