#!/bin/bash
# Life OS Eval Runner
# 用 claude -p 批量跑测试场景，输出保存到 evals/outputs/

set -e

EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
SCENARIOS_DIR="$EVAL_DIR/scenarios"
OUTPUTS_DIR="$EVAL_DIR/outputs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FAIL_COUNT=0
PASS_COUNT=0

mkdir -p "$OUTPUTS_DIR"

# 如果指定了场景名，只跑那个（路径安全：只取 basename，防止目录遍历）
if [ -n "$1" ]; then
    SAFE_NAME="$(basename "$1" .md)"
    CANDIDATE="$SCENARIOS_DIR/${SAFE_NAME}.md"
    if [ ! -f "$CANDIDATE" ]; then
        echo "❌ 场景不存在: $SAFE_NAME"
        echo "   可用场景:"
        ls "$SCENARIOS_DIR"/*.md 2>/dev/null | xargs -I{} basename {} .md | sed 's/^/     /'
        exit 1
    fi
    SCENARIOS=("$CANDIDATE")
else
    SCENARIOS=("$SCENARIOS_DIR"/*.md)
fi

echo "=== Life OS Eval Runner ==="
echo "时间: $TIMESTAMP"
echo "场景数: ${#SCENARIOS[@]}"
echo ""

RESULTS=()

for scenario_file in "${SCENARIOS[@]}"; do
    if [ ! -f "$scenario_file" ]; then
        echo "❌ 场景文件不存在: $scenario_file"
        RESULTS+=("SKIP $(basename "$scenario_file" .md)")
        continue
    fi

    scenario_name=$(basename "$scenario_file" .md)
    output_file="$OUTPUTS_DIR/${scenario_name}_${TIMESTAMP}.md"

    # 从场景文件中提取用户消息（支持多语言标题：用户消息 / User Message / ユーザーメッセージ）
    user_message=$(sed -n '/^## \(用户消息\|User Message\|ユーザーメッセージ\)/,/^## /{/```/,/```/{/```/d;p;}}' "$scenario_file")

    if [ -z "$user_message" ]; then
        echo "❌ 无法提取用户消息: $scenario_name"
        echo "   期望格式: '## 用户消息' 或 '## User Message' 或 '## ユーザーメッセージ' 下的 fenced code block"
        RESULTS+=("FAIL $scenario_name (schema error: no user message section found)")
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    echo "🏃 运行场景: $scenario_name"
    echo "   输出: $output_file"

    # 用 claude -p 运行，捕获退出码
    EXIT_CODE=0
    echo "$user_message" | claude -p \
        --output-format text \
        > "$output_file" 2>"${output_file}.stderr" || EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "   ✅ 通过 (exit 0)"
        RESULTS+=("PASS $scenario_name")
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "   ❌ 失败 (exit $EXIT_CODE)"
        # 追加 stderr 到输出文件末尾，便于审查
        if [ -s "${output_file}.stderr" ]; then
            echo "" >> "$output_file"
            echo "--- STDERR (exit code $EXIT_CODE) ---" >> "$output_file"
            cat "${output_file}.stderr" >> "$output_file"
        fi
        RESULTS+=("FAIL $scenario_name (exit $EXIT_CODE)")
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    # 清理临时 stderr 文件
    rm -f "${output_file}.stderr"
    echo ""
done

echo "=== 结果汇总 ==="
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo ""
echo "通过: $PASS_COUNT / 失败: $FAIL_COUNT / 总计: ${#SCENARIOS[@]}"
echo "输出目录: $OUTPUTS_DIR"
echo ""
echo "下一步: 对照 rubrics/ 中的评分标准，人工评审输出质量"

# 有失败场景时以非零退出码退出
if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
fi
