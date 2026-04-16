# Chinese translations for shell scripts

# start-server.sh messages
MSG_STARTUP_HEADER="llama-server 启动脚本"
MSG_STARTUP_HEADER_DELIM="========================================"
MSG_MODEL="模型：$MODEL"
MSG_HOST="主机：$HOST"
MSG_PORT="端口：$PORT"
MSG_CONTEXT="上下文：$CONTEXT_SIZE"
MSG_THREADS="线程数：$THREADS"
MSG_LOG="日志：$LOG_FILE"
MSG_MODEL_NOT_FOUND="错误：模型文件不存在"
MSG_MODEL_PLACEHOLDER="请将 GGUF 模型文件放入 $MODELS_DIR 目录"

# run-cli.sh messages
MSG_CLI_STARTUP="llama-server CLI 脚本"
MSG_CLI_PROMPT="提示：$PROMPT"
MSG_CLI_TOKENS="令牌数：$N_PREDICT"
MSG_CLI_TEMP="温度：$TEMPERATURE"

# quantize-model.sh messages
MSG_QUANT_START="开始量化..."
MSG_QUANT_INPUT="输入：$INPUT_MODEL"
MSG_QUANT_OUTPUT="输出：$OUTPUT_MODEL"
MSG_QUANT_TYPE="类型：$QUANT_TYPE"
MSG_QUANT_COMPLETE="量化完成！"

# Common messages
MSG_ERROR="错误："
MSG_INFO="信息："
MSG_WARNING="警告："
