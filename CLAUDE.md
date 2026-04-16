# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **llama.cpp deployment project** for running GGUF models with TurboQuant support. The project structure wraps a compiled llama.cpp installation with shell scripts for common operations.

## Directory Structure

```
~/llama/
├── llama.cpp/        # Compiled llama.cpp (CMake build, release mode)
├── models/           # GGUF model files
├── run/              # Utility scripts
├── gui/              # GUI application (CustomTkinter)
└── logs/             # Server and CLI logs
```

## Commands

### GUI Application

```bash
# Start the GUI manager
python gui/main.py
```

### Start llama-server

```bash
# Default: port 8080, context 4096, auto threads
./run/start-server.sh [model.gguf]

# With environment overrides
HOST=0.0.0.0 PORT=8080 CONTEXT_SIZE=4096 THREADS=8 ./run/start-server.sh models/model.gguf
```

### Run llama-cli

```bash
# Default prompt: "你好", 256 tokens, temp 0.7
./run/run-cli.sh [model.gguf] [prompt]

# Example
./run/run-cli.sh models/llama.gguf "Hello"
```

### Quantize Models

```bash
./run/quantize-model.sh <input.gguf> <output.gguf> <quant_type>

# Quantization types: Q4_K_M, Q5_K_M, Q8_0, Q3_K_S, Q3_K_M, Q3_K_L, Q4_K_S, Q6_K, etc.
./run/quantize-model.sh model-f16.gguf model-q4.gguf Q4_K_M
```

### Direct Binary Access

```bash
export LD_LIBRARY_PATH=/home/cklee/llama/llama.cpp/bin:$LD_LIBRARY_PATH

llama.cpp/bin/llama-server --model models/model.gguf --port 8080
llama.cpp/bin/llama-cli --model models/model.gguf --prompt "Hello"
llama.cpp/bin/llama-quantize input.gguf output.gguf Q4_K_M
```

## Architecture

### GUI Application (gui/)

- **main.py** - App entry point, main window
- **config.py** - Configuration management (save/load JSON)
- **server_manager.py** - Process lifecycle (start/stop/restart)
- **huggingface.py** - HF model download logic

### llama.cpp Binaries

Located in `llama.cpp/bin/`:
- **llama-server** - HTTP API server
- **llama-cli** - CLI inference
- **llama-quantize** - Model quantization
- **llama-bench** - Performance benchmarking
- **llama-perplexity** - Model evaluation

### Libraries

- `libllama.so` - Main llama library
- `libggml.so` - Tensor library
- `libggml-cpu.so` - CPU backend
- `libmtmd.so` - Multimodal support

### Scripts

All scripts in `run/`:
- Set `LD_LIBRARY_PATH` to include llama.cpp/bin
- Create timestamped logs in `logs/`
- Support environment variable configuration
- Validate model file existence before running

## Build Information

llama.cpp is pre-compiled with:
- CMake (Release mode, -O3)
- Shared libraries enabled
- GCC 13

To rebuild llama.cpp, work in the `llama.cpp/` directory using standard CMake commands.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Server bind address |
| PORT | 8080 | Server port |
| CONTEXT_SIZE | 4096 | Context window size |
| THREADS | nproc | CPU thread count |
| N_PREDICT | 256 | Max tokens to predict |
| TEMPERATURE | 0.7 | Sampling temperature |

## Dependencies

- Python 3.x
- CustomTkinter: `pip install customtkinter`
- Requests: `pip install requests` (for HuggingFace downloads)
- Tkinter: `apt install python3-tk` (system package for GUI)

## GUI Application

Start the GUI manager:

```bash
./run-gui.sh
# or
./venv/bin/python -m gui.main
```

## GUI Features

1. **服务器配置** - Configure all llama-server parameters:
   - Model path, host, port
   - Context size, threads, batch size
   - Temperature, GPU layers, cache capacity
   - Flash attention option

2. **模型管理** - Model management:
   - Download from HuggingFace with URL
   - Progress bar and cancel support
   - Local model browser
   - Popular GGUF repositories list

3. **状态监控** - Status monitoring:
   - Real-time server status
   - Server logs viewer
   - Open browser to API endpoint
