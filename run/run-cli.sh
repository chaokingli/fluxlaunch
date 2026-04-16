#!/bin/bash
# llama-cli 运行脚本
# 用于测试 TurboQuant 模型推理

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LLAMA_CPP="$BASE_DIR/llama.cpp"
MODELS_DIR="$BASE_DIR/models"
LOGS_DIR="$BASE_DIR/logs"

# 设置库路径
export LD_LIBRARY_PATH="$LLAMA_CPP/bin:$LD_LIBRARY_PATH"

# 模型文件 (修改为实际模型名称)
MODEL="${1:-$MODELS_DIR/model.gguf}"

# CLI 配置
PROMPT="${2:-你好}"
N_PREDICT="${N_PREDICT:-256}"
TEMPERATURE="${TEMPERATURE:-0.7}"
CONTEXT_SIZE="${CONTEXT_SIZE:-4096}"
THREADS="${THREADS:-$(nproc)}"

# 日志文件
LOG_FILE="$LOGS_DIR/cli-$(date +%Y%m%d-%H%M%S).log"

echo "========================================"
echo "llama-cli 运行脚本"
echo "========================================"
echo "模型：$MODEL"
echo "提示词：$PROMPT"
echo "预测长度：$N_PREDICT"
echo "温度：$TEMPERATURE"
echo "上下文：$CONTEXT_SIZE"
echo "线程数：$THREADS"
echo "日志：$LOG_FILE"
echo "========================================"

# 检查模型文件
if [ ! -f "$MODEL" ]; then
    echo "错误：模型文件不存在：$MODEL"
    echo "请将 GGUF 模型文件放入 $MODELS_DIR 目录"
    exit 1
fi

# 运行 CLI
"$LLAMA_CPP/bin/llama-cli" \
    --model "$MODEL" \
    --prompt "$PROMPT" \
    --n-predict "$N_PREDICT" \
    --temp "$TEMPERATURE" \
    --ctx-size "$CONTEXT_SIZE" \
    --threads "$THREADS" \
    2>&1 | tee "$LOG_FILE"
