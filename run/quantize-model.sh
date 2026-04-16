#!/bin/bash
# 模型量化脚本
# 用于将 GGUF 模型量化为不同精度

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LLAMA_CPP="$BASE_DIR/llama.cpp"
MODELS_DIR="$BASE_DIR/models"

# 设置库路径
export LD_LIBRARY_PATH="$LLAMA_CPP/bin:$LD_LIBRARY_PATH"

echo "========================================"
echo "模型量化工具"
echo "========================================"
echo ""
echo "用法：$0 <输入模型> <输出模型> <量化类型>"
echo ""
echo "量化类型:"
echo "  Q4_0   - 4-bit, 最小精度损失"
echo "  Q4_1   - 4-bit, 更高精度"
echo "  Q5_0   - 5-bit, 最小精度损失"
echo "  Q5_1   - 5-bit, 更高精度"
echo "  Q8_0   - 8-bit, 几乎无损"
echo "  Q2_K   - 2-bit, 使用 K-quants"
echo "  Q3_K_S - 3-bit, small"
echo "  Q3_K_M - 3-bit, medium"
echo "  Q3_K_L - 3-bit, large"
echo "  Q4_K_S - 4-bit, small (推荐)"
echo "  Q4_K_M - 4-bit, medium (推荐)"
echo "  Q5_K_S - 5-bit, small"
echo "  Q5_K_M - 5-bit, medium"
echo "  Q6_K   - 6-bit, K-quants"
echo ""
echo "示例:"
echo "  $0 model-f16.gguf model-q4.gguf Q4_K_M"
echo "  $0 model-q4.gguf model-q8.gguf Q8_0"
echo "========================================"

# 参数检查
if [ "$#" -lt 3 ]; then
    echo "错误：参数不足"
    exit 1
fi

INPUT_MODEL="$1"
OUTPUT_MODEL="$2"
QUANT_TYPE="$3"

# 处理路径
if [[ "$INPUT_MODEL" != /* ]]; then
    INPUT_MODEL="$MODELS_DIR/$INPUT_MODEL"
fi

if [[ "$OUTPUT_MODEL" != /* ]]; then
    OUTPUT_MODEL="$MODELS_DIR/$OUTPUT_MODEL"
fi

echo ""
echo "输入模型：$INPUT_MODEL"
echo "输出模型：$OUTPUT_MODEL"
echo "量化类型：$QUANT_TYPE"
echo ""

# 检查输入模型
if [ ! -f "$INPUT_MODEL" ]; then
    echo "错误：输入模型不存在：$INPUT_MODEL"
    exit 1
fi

# 执行量化
echo "开始量化..."
"$LLAMA_CPP/bin/llama-quantize" "$INPUT_MODEL" "$OUTPUT_MODEL" "$QUANT_TYPE"

if [ $? -eq 0 ]; then
    echo ""
    echo "量化完成!"
    echo "输出文件：$OUTPUT_MODEL"
    ls -lh "$OUTPUT_MODEL"
else
    echo ""
    echo "量化失败!"
    exit 1
fi
