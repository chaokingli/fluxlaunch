#!/bin/bash
# llama-cli running script
# For testing TurboQuant model inference

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LLAMA_CPP="$BASE_DIR/llama.cpp"
MODELS_DIR="$BASE_DIR/models"
LOGS_DIR="$BASE_DIR/logs"

# Set default language and source translations
LANG="${LANG:-en}"
I18N_FILE="${LANG%%_*}.sh"
if [ -f "$SCRIPT_DIR/i18n/$I18N_FILE" ]; then
    source "$SCRIPT_DIR/i18n/$I18N_FILE"
else
    source "$SCRIPT_DIR/i18n/en.sh"
fi

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

echo "$MSG_STARTUP_HEADER_DELIM"
echo "$MSG_CLI_STARTUP"
echo "$MSG_STARTUP_HEADER_DELIM"
echo "$MSG_MODEL"
echo "$MSG_CLI_PROMPT"
echo "$MSG_CLI_TOKENS"
echo "$MSG_CLI_TEMP"
echo "$MSG_CONTEXT"
echo "$MSG_THREADS"
echo "$MSG_LOG"
echo "$MSG_STARTUP_HEADER_DELIM"

# 检查模型文件
if [ ! -f "$MODEL" ]; then
    echo "$MSG_MODEL_NOT_FOUND: $MODEL"
    echo "$MSG_MODEL_PLACEHOLDER"
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
