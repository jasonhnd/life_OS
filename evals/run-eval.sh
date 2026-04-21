#!/bin/bash
# Life OS Eval Runner
# 用 claude -p 批量跑测试场景，输出保存到 evals/outputs/
#
# v1.6.3c (2026-04-21): adds Layer 5 compliance auto-detection. After each
# scenario, if scripts/lifeos-compliance-check.sh exists and the scenario has
# a defined check, runs it and tracks separately from scenario exit-code pass/fail.

set -e

EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
SCENARIOS_DIR="$EVAL_DIR/scenarios"
OUTPUTS_DIR="$EVAL_DIR/outputs"
COMPLIANCE_SCRIPT="$EVAL_DIR/../scripts/lifeos-compliance-check.sh"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FAIL_COUNT=0
PASS_COUNT=0
COMPLIANCE_FAIL_COUNT=0

mkdir -p "$OUTPUTS_DIR"

# ─── claude CLI availability gate ────────────────────────────────────────────
# If the claude CLI is not on PATH (common on Windows Git Bash, minimal CI
# runners, or any host without the Anthropic Claude Code CLI installed), skip
# all scenarios gracefully with exit 0 instead of cascading `exit 127` for
# every scenario. `LIFEOS_EVAL_SKIP_CLAUDE=1` forces skip even when claude is
# installed — use this from CI when you want to short-circuit the eval step.
if [ "${LIFEOS_EVAL_SKIP_CLAUDE:-0}" = "1" ]; then
    echo ""
    echo "⏭  LIFEOS_EVAL_SKIP_CLAUDE=1 set — skipping all eval scenarios."
    echo ""
    echo "=== 结果汇总 ==="
    echo "通过: 0 / 失败: 0 / 跳过: 0 / 总计: 0 (forced skip via env)"
    echo ""
    exit 0
fi
if ! command -v claude >/dev/null 2>&1; then
    echo ""
    echo "⏭  claude CLI not found on PATH — skipping all eval scenarios."
    echo "    This is expected on Windows Git Bash or any env without the"
    echo "    Anthropic Claude Code CLI installed."
    echo "    Install: https://claude.com/code or re-run on a host with \`claude\`."
    echo "    Override from CI: set LIFEOS_EVAL_SKIP_CLAUDE=1 to silence."
    echo ""
    echo "=== 结果汇总 ==="
    echo "通过: 0 / 失败: 0 / 跳过: 0 / 总计: 0 (claude CLI missing)"
    echo ""
    exit 0
fi

# 如果指定了场景名，只跑那个（路径安全：只取 basename，防止目录遍历）
if [ -n "${1:-}" ]; then
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
if [ -x "$COMPLIANCE_SCRIPT" ]; then
    echo "Compliance check: 启用 ($COMPLIANCE_SCRIPT)"
else
    echo "Compliance check: 禁用 (脚本不存在或不可执行: $COMPLIANCE_SCRIPT)"
fi
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
        echo "   ✅ exit 0"
        SCENARIO_RESULT="PASS"
    else
        echo "   ❌ exit $EXIT_CODE"
        # 追加 stderr 到输出文件末尾，便于审查
        if [ -s "${output_file}.stderr" ]; then
            echo "" >> "$output_file"
            echo "--- STDERR (exit code $EXIT_CODE) ---" >> "$output_file"
            cat "${output_file}.stderr" >> "$output_file"
        fi
        SCENARIO_RESULT="FAIL (exit $EXIT_CODE)"
    fi
    rm -f "${output_file}.stderr"

    # ─── v1.6.3c: Layer 5 compliance auto-detection ──────────────────────────
    COMPLIANCE_RESULT=""
    if [ -x "$COMPLIANCE_SCRIPT" ]; then
        echo "" >> "$output_file"
        echo "--- Compliance Check ($(date -Iseconds)) ---" >> "$output_file"

        if COMPLIANCE_OUT=$(bash "$COMPLIANCE_SCRIPT" "$output_file" "$scenario_name" 2>&1); then
            echo "   ✅ compliance check passed"
            echo "$COMPLIANCE_OUT" >> "$output_file"
            COMPLIANCE_RESULT="compliance:pass"
        else
            CC_EXIT=$?
            if [ "$CC_EXIT" -eq 1 ]; then
                echo "   🚫 compliance check FAILED"
                echo "$COMPLIANCE_OUT" | sed 's/^/      /'
                echo "$COMPLIANCE_OUT" >> "$output_file"
                COMPLIANCE_FAIL_COUNT=$((COMPLIANCE_FAIL_COUNT + 1))
                COMPLIANCE_RESULT="compliance:FAIL"
            else
                echo "   ⚠️ compliance check error (exit $CC_EXIT)"
                echo "$COMPLIANCE_OUT" >> "$output_file"
                COMPLIANCE_RESULT="compliance:error"
            fi
        fi
    fi

    # Aggregate scenario + compliance into one result line
    if [ "$SCENARIO_RESULT" = "PASS" ] && [ "$COMPLIANCE_RESULT" = "compliance:FAIL" ]; then
        RESULTS+=("FAIL $scenario_name (exit 0 but compliance violations)")
        FAIL_COUNT=$((FAIL_COUNT + 1))
    elif [ "$SCENARIO_RESULT" = "PASS" ]; then
        RESULTS+=("PASS $scenario_name${COMPLIANCE_RESULT:+ ($COMPLIANCE_RESULT)}")
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        RESULTS+=("FAIL $scenario_name ($SCENARIO_RESULT${COMPLIANCE_RESULT:+ + $COMPLIANCE_RESULT})")
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo ""
done

echo "=== 结果汇总 ==="
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo ""
echo "通过: $PASS_COUNT / 失败: $FAIL_COUNT / 总计: ${#SCENARIOS[@]}"
if [ "$COMPLIANCE_FAIL_COUNT" -gt 0 ]; then
    echo "Compliance violations: $COMPLIANCE_FAIL_COUNT scenarios"
    echo "Append violations to pro/compliance/violations.md per references/compliance-spec.md"
fi
echo "输出目录: $OUTPUTS_DIR"
echo ""
echo "下一步: 对照 rubrics/ 中的评分标准，人工评审输出质量"

# 有失败场景或合规违规时以非零退出码退出
if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
fi
