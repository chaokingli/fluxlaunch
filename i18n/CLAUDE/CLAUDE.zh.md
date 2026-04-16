<!-- Language: English | 语言：英文 | Sprache: Englisch -->
[**EN**](CLAUDE.en.md) | [**中文**](CLAUDE.zh.md) | [**DE**](CLAUDE.de.md)

# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

这是一个 **llama.cpp 部署项目**，用于运行支持 TurboQuant 的 GGUF 模型。项目结构将编译好的 llama.cpp 安装与常用操作的 shell 脚本封装在一起。

## 目录结构

```
~/llama/
├── llama.cpp/        # 编译好的 llama.cpp (CMake 构建，Release 模式)
├── models/           # GGUF 模型文件
├── run/              # 工具脚本
├── gui/              # GUI 应用程序 (CustomTkinter)
└── logs/             # 服务器和 CLI 日志
```

## 命令

### GUI 应用程序

```bash
# 启动 GUI 管理器
python gui/main.py
```

### 启动 llama-server

```bash
# 默认：端口 8080, 上下文 4096, 自动线程数
./run/start-server.sh [model.gguf]

# 使用环境变量覆盖
HOST=0.0.0.0 PORT=8080 CONTEXT_SIZE=4096 THREADS=8 ./run/start-server.sh models/model.gguf
```

### 运行 llama-cli

```bash
# 默认提示词："你好", 256 tokens, 温度 0.7
./run/run-cli.sh [model.gguf] [prompt]

# 示例
./run/run-cli.sh models/llama.gguf "Hello"
```

### 量化模型

```bash
./run/quantize-model.sh <input.gguf> <output.gguf> <quant_type>

# 量化类型：Q4_K_M, Q5_K_M, Q8_0, Q3_K_S, Q3_K_M, Q3_K_L, Q4_K_S, Q6_K 等
./run/quantize-model.sh model-f16.gguf model-q4.gguf Q4_K_M
```

### 直接访问二进制文件

```bash
export LD_LIBRARY_PATH=/home/cklee/llama/llama.cpp/bin:$LD_LIBRARY_PATH

llama.cpp/bin/llama-server --model models/model.gguf --port 8080
llama.cpp/bin/llama-cli --model models/model.gguf --prompt "Hello"
llama.cpp/bin/llama-quantize input.gguf output.gguf Q4_K_M
```

## 架构

### GUI 应用程序 (gui/)

- **main.py** - 应用程序入口，主窗口
- **config.py** - 配置管理（保存/加载 JSON）
- **server_manager.py** - 进程生命周期（启动/停止/重启）
- **huggingface.py** - HuggingFace 模型下载逻辑

### llama.cpp 二进制文件

位于 `llama.cpp/bin/`：
- **llama-server** - HTTP API 服务器
- **llama-cli** - CLI 推理
- **llama-quantize** - 模型量化
- **llama-bench** - 性能基准测试
- **llama-perplexity** - 模型评估

### 库文件

- `libllama.so` - 主 llama 库
- `libggml.so` - 张量库
- `libggml-cpu.so` - CPU 后端
- `libmtmd.so` - 多模态支持

### 脚本

所有脚本位于 `run/`：
- 设置 `LD_LIBRARY_PATH` 以包含 llama.cpp/bin
- 在 `logs/` 中创建带时间戳的日志
- 支持环境变量配置
- 运行前验证模型文件是否存在

## 构建信息

llama.cpp 预编译配置：
- CMake (Release 模式，-O3)
- 启用共享库
- GCC 13

如需重新编译 llama.cpp，请在 `llama.cpp/` 目录中使用标准 CMake 命令。

## 环境变量

| 变量 | 默认值 | 说明 |
|----------|---------|-------------|
| HOST | 0.0.0.0 | 服务器绑定地址 |
| PORT | 8080 | 服务器端口 |
| CONTEXT_SIZE | 4096 | 上下文窗口大小 |
| THREADS | nproc | CPU 线程数 |
| N_PREDICT | 256 | 最大生成 token 数 |
| TEMPERATURE | 0.7 | 采样温度 |

## 依赖

- Python 3.x
- CustomTkinter: `pip install customtkinter`
- Requests: `pip install requests` (用于 HuggingFace 下载)
- Tkinter: `apt install python3-tk` (GUI 系统包)

## GUI 应用程序

启动 GUI 管理器：

```bash
./run-gui.sh
# 或
./venv/bin/python -m gui.main
```

## GUI 功能

1. **服务器配置** - 配置所有 llama-server 参数：
   - 模型路径、主机、端口
   - 上下文大小、线程数、批次大小
   - 温度、GPU 层数、缓存容量
   - Flash attention 选项

2. **模型管理** - 模型管理：
   - 通过 URL 从 HuggingFace 下载
   - 支持进度条和取消
   - 本地模型浏览器
   - 热门 GGUF 仓库列表

3. **状态监控** - 状态监控：
   - 实时服务器状态
   - 服务器日志查看器
   - 打开浏览器访问 API 端点
