#!/bin/bash
# LLama Server GUI Manager

LANG="${LANG:-en}"
source "$(dirname "${BASH_SOURCE[0]}")/run/i18n/${LANG%%_*}.sh" 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 直接在脚本目录运行
cd "$SCRIPT_DIR"

# 优先使用虚拟环境
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
    echo "$MSG_USE_VENV"
else
    # 使用系统 Python
    PYTHON="python3"
    echo "$MSG_USE_SYSTEM"
fi

# 检查依赖
$PYTHON -c "import customtkinter, tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "$MSG_MISSING_DEPS"
    echo ""
    if [ -f "venv/bin/python" ]; then
        echo "$MSG_PLEASE_RUN"
        echo "  ./venv/bin/pip install customtkinter requests"
    else
        echo "$MSG_PLEASE_RUN"
        echo "  $MSG_INSTALL_TK"
        echo "  $MSG_INSTALL_PKGS"
    fi
    exit 1
fi

# 启动 GUI
echo "$MSG_STARTING_GUI"
exec $PYTHON -m gui.main
