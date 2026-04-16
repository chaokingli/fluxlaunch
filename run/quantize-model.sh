#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LLAMA_CPP="$BASE_DIR/llama.cpp"
MODELS_DIR="$BASE_DIR/models"

# Set library path
export LD_LIBRARY_PATH="$LLAMA_CPP/bin:$LD_LIBRARY_PATH"

LANG="${LANG:-en}"
source "$SCRIPT_DIR/i18n/${LANG%%_*}.sh" 2>/dev/null || true

echo "$MSG_QUANT_TITLE"
echo ""
echo "$MSG_QUANT_USAGE"
echo ""
echo "$MSG_QUANT_TYPES"
echo "$MSG_QUANT_TYPE_Q4_0"
echo "$MSG_QUANT_TYPE_Q4_1"
echo "$MSG_QUANT_TYPE_Q5_0"
echo "$MSG_QUANT_TYPE_Q5_1"
echo "$MSG_QUANT_TYPE_Q8_0"
echo "$MSG_QUANT_TYPE_Q2_K"
echo "$MSG_QUANT_TYPE_Q3_K_S"
echo "$MSG_QUANT_TYPE_Q3_K_M"
echo "$MSG_QUANT_TYPE_Q3_K_L"
echo "$MSG_QUANT_TYPE_Q4_K_S"
echo "$MSG_QUANT_TYPE_Q4_K_M"
echo "$MSG_QUANT_TYPE_Q5_K_S"
echo "$MSG_QUANT_TYPE_Q5_K_M"
echo "$MSG_QUANT_TYPE_Q6_K"
echo ""
echo "$MSG_QUANT_EXAMPLES"
echo "$MSG_QUANT_EXAMPLE_1"
echo "$MSG_QUANT_EXAMPLE_2"
echo "========================================"

if [ "$#" -lt 3 ]; then
    echo "$MSG_ERROR_INVALID_ARGS"
    exit 1
fi

INPUT_MODEL="$1"
OUTPUT_MODEL="$2"
QUANT_TYPE="$3"

if [[ "$INPUT_MODEL" != /* ]]; then
    INPUT_MODEL="$MODELS_DIR/$INPUT_MODEL"
fi

if [[ "$OUTPUT_MODEL" != /* ]]; then
    OUTPUT_MODEL="$MODELS_DIR/$OUTPUT_MODEL"
fi

echo ""
echo "$MSG_QUANT_INPUT"
echo "$MSG_QUANT_OUTPUT"
echo "$MSG_QUANT_TYPE"
echo ""

if [ ! -f "$INPUT_MODEL" ]; then
    echo "$MSG_ERROR_MODEL_NOT_FOUND"
    exit 1
fi

echo "$MSG_QUANT_START"
"$LLAMA_CPP/bin/llama-quantize" "$INPUT_MODEL" "$OUTPUT_MODEL" "$QUANT_TYPE"

if [ $? -eq 0 ]; then
    echo ""
    echo "$MSG_QUANTIZE_SUCCESS"
    echo "$MSG_QUANTIZE_OUTPUT_FILE"
    ls -lh "$OUTPUT_MODEL"
else
    echo ""
    echo "$MSG_ERROR_QUANTIZE_FAILED"
    exit 1
fi
