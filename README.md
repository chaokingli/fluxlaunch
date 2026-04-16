# LLama Server GUI Manager

一个用于管理和配置 llama-server 的图形化工具

## 功能

- **服务器配置** - 配置所有 llama-server 参数
- **模型下载** - 从 HuggingFace 下载 GGUF 模型
- **进程管理** - 启动/停止/重启服务器
- **状态监控** - 实时查看服务器状态和日志

## 安装

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-tk python3.12-tk

# 如果上述命令需要密码，可以尝试：
# 使用 apt (无需密码)
sudo apt install python3-tk
```

### 2. 安装 Python 依赖

```bash
cd ~/llama

# 创建虚拟环境（如果还没有）
python3 -m venv venv

# 激活虚拟环境并安装包
./venv/bin/pip install customtkinter requests
```

## 使用方法

### 启动 GUI

```bash
# 方式 1: 使用启动脚本
./run-gui.sh

# 方式 2: 直接使用 Python
./venv/bin/python -m gui.main
```

### 配置服务器

1. 在"服务器配置"标签页中设置参数
2. 点击"浏览..."选择模型文件
3. 配置完成后点击"保存配置"
4. 点击"启动服务器"开始服务

### 下载模型

1. 在"模型管理"标签页中输入 HuggingFace URL
2. 点击"开始下载"
3. 下载完成后模型会保存到 `models/` 目录

### HuggingFace URL 格式

```
# 完整 URL
https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf

# 短格式
TheBloke/Llama-2-7B-GGUF/llama-2-7b.Q4_K_M.gguf
```

## 配置保存

配置自动保存到 `~/.llama-server-config.json`

## 项目结构

```
~/llama/
├── gui/
│   ├── __init__.py      # 入口
│   ├── main.py          # GUI 主程序
│   ├── config.py        # 配置管理
│   ├── server_manager.py # 服务器进程管理
│   └── huggingface.py   # HuggingFace 下载
├── run-gui.sh           # GUI 启动脚本
├── run/
│   ├── start-server.sh  # 服务器启动脚本
│   ├── run-cli.sh       # CLI 运行脚本
│   └── quantize-model.sh # 量化脚本
├── models/              # 模型文件目录
├── llama.cpp/           # llama.cpp 编译目录
└── logs/                # 日志目录
```

## 故障排除

### GUI 无法启动

```bash
# 检查 tkinter 是否安装
./venv/bin/python -c "import tkinter; print('OK')"

# 如果报错，需要安装 tkinter
sudo apt-get install python3-tk
```

### 找不到 llama-server

确保 `llama.cpp/bin/llama-server` 存在。如果不存在，需要编译 llama.cpp。

### 端口被占用

如果启动时提示端口被占用，可以选择：
1. 停止现有服务器
2. 使用不同的端口
