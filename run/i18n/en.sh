# English translations for shell scripts

# start-server.sh messages
MSG_STARTUP_HEADER="llama-server Startup Script"
MSG_STARTUP_HEADER_DELIM="========================================"
MSG_MODEL="Model: $MODEL"
MSG_HOST="Host: $HOST"
MSG_PORT="Port: $PORT"
MSG_CONTEXT="Context: $CONTEXT_SIZE"
MSG_THREADS="Threads: $THREADS"
MSG_LOG="Log: $LOG_FILE"
MSG_MODEL_NOT_FOUND="Error: Model file not found"
MSG_MODEL_PLACEHOLDER="Please place GGUF model files in $MODELS_DIR directory"

# run-cli.sh messages
MSG_CLI_STARTUP="llama-server CLI Script"
MSG_CLI_PROMPT="Prompt: $PROMPT"
MSG_CLI_TOKENS="Tokens: $N_PREDICT"
MSG_CLI_TEMP="Temperature: $TEMPERATURE"

# quantize-model.sh messages
MSG_QUANT_START="Starting quantization..."
MSG_QUANT_INPUT="Input: $INPUT_MODEL"
MSG_QUANT_OUTPUT="Output: $OUTPUT_MODEL"
MSG_QUANT_TYPE="Type: $QUANT_TYPE"
MSG_QUANT_COMPLETE="Quantization complete!"

# Common messages
MSG_ERROR="Error:"
MSG_INFO="Info:"
MSG_WARNING="Warning:"
