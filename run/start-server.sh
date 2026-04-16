#!/bin/bash
# llama-server startup script
#用于部署和测试 TurboQuant 模型

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LLAMA_CPP="$BASE_DIR/llama.cpp"
MODELS_DIR="$BASE_DIR/models"
LOGS_DIR="$BASE_DIR/logs"

# 设置库路径
export LD_LIBRARY_PATH="$LLAMA_CPP/bin:$LD_LIBRARY_PATH"

# Source translation file based on LANG
I18N_FILE="${LANG%%_*}.sh"
if [ -f "$SCRIPT_DIR/i18n/$I18N_FILE" ]; then
    source "$SCRIPT_DIR/i18n/$I18N_FILE"
else
    source "$SCRIPT_DIR/i18n/en.sh"
fi

# 模型文件 (修改为实际模型名称)
MODEL="${1:-$MODELS_DIR/model.gguf}"

# 服务器配置
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
CONTEXT_SIZE="${CONTEXT_SIZE:-4096}"
THREADS="${THREADS:-$(nproc)}"

# 日志文件
LOG_FILE="$LOGS_DIR/server-$(date +%Y%m%d-%H%M%S).log"

echo "$MSG_STARTUP_HEADER_DELIM"
echo "$MSG_STARTUP_HEADER"
echo "$MSG_STARTUP_HEADER_DELIM"
echo "$MSG_MODEL"
echo "$MSG_HOST"
echo "$MSG_PORT"
echo "$MSG_CONTEXT"
echo "$MSG_THREADS"
echo "$MSG_LOG"
echo "$MSG_STARTUP_HEADER_DELIM"

# 检查模型文件
if [ ! -f "$MODEL" ]; then
    echo "$MSG_MODEL_NOT_FOUND"
    echo "$MSG_MODEL_PLACEHOLDER"
    exit 1
fi

# 启动服务器
"$LLAMA_CPP/bin/llama-server" \
    --model "$MODEL" \
    --host "$HOST" \
    --port "$PORT" \
    --ctx-size "$CONTEXT_SIZE" \
    --threads "$THREADS" \
    2>&1 | tee "$LOG_FILE"
