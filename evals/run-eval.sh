#!/bin/bash
# Life OS Eval Runner
# 用 claude -p 批量跑测试场景，输出保存到 evals/outputs/

set -e

EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
SCENARIOS_DIR="$EVAL_DIR/scenarios"
OUTPUTS_DIR="$EVAL_DIR/outputs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$OUTPUTS_DIR"

# 如果指定了场景名，只跑那个
if [ -n "$1" ]; then
    SCENARIOS=("$SCENARIOS_DIR/$1.md")
else
    SCENARIOS=("$SCENARIOS_DIR"/*.md)
fi

echo "=== Life OS Eval Runner ==="
echo "时间: $TIMESTAMP"
echo "场景数: ${#SCENARIOS[@]}"
echo ""

for scenario_file in "${SCENARIOS[@]}"; do
    if [ ! -f "$scenario_file" ]; then
        echo "❌ 场景文件不存在: $scenario_file"
        continue
    fi

    scenario_name=$(basename "$scenario_file" .md)
    output_file="$OUTPUTS_DIR/${scenario_name}_${TIMESTAMP}.md"

    # 从场景文件中提取用户消息（``` 代码块中的内容）
    user_message=$(sed -n '/^## 用户消息/,/^## /{/```/,/```/{/```/d;p;}}' "$scenario_file")

    if [ -z "$user_message" ]; then
        echo "❌ 无法提取用户消息: $scenario_name"
        continue
    fi

    echo "🏃 运行场景: $scenario_name"
    echo "   输出: $output_file"

    # 用 claude -p 运行，使用 life-os skill
    echo "$user_message" | claude -p \
        --output-format text \
        > "$output_file" 2>&1 || true

    echo "   ✅ 完成"
    echo ""
done

echo "=== 所有场景完成 ==="
echo "输出目录: $OUTPUTS_DIR"
echo ""
echo "下一步: 对照 rubrics/ 中的评分标准，人工评审输出质量"
