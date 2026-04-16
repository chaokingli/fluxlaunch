#!/bin/bash
# 启动 LLama Server GUI 管理程序

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 直接在脚本目录运行
cd "$SCRIPT_DIR"

# 优先使用虚拟环境
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
    echo "使用虚拟环境 Python"
else
    # 使用系统 Python
    PYTHON="python3"
    echo "使用系统 Python"
fi

# 检查依赖
$PYTHON -c "import customtkinter, tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "错误：缺少依赖模块"
    echo ""
    if [ -f "venv/bin/python" ]; then
        echo "请运行："
        echo "  ./venv/bin/pip install customtkinter requests"
    else
        echo "请运行："
        echo "  sudo apt-get install python3-tk"
        echo "  pip3 install customtkinter requests"
    fi
    exit 1
fi

# 启动 GUI
echo "正在启动 LLama Server Manager..."
exec $PYTHON -m gui.main
