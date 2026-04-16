[EN](README.en.md) | [中文](README.zh.md) | [DE](README.de.md)

# LLama Server GUI Manager

A graphical tool for managing and configuring llama-server

## Features

- **Server Configuration** - Configure all llama-server parameters
- **Model Download** - Download GGUF models from HuggingFace
- **Process Management** - Start/stop/restart server
- **Status Monitoring** - View server status and logs in real-time

## Installation

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-tk python3.12-tk

# If the above command requires a password, try:
# Using apt (no password required)
sudo apt install python3-tk
```

### 2. Install Python Dependencies

```bash
cd ~/llama

# Create virtual environment (if not already done)
python3 -m venv venv

# Activate virtual environment and install packages
./venv/bin/pip install customtkinter requests
```

## Usage

### Start GUI

```bash
# Option 1: Use the launch script
./run-gui.sh

# Option 2: Use Python directly
./venv/bin/python -m gui.main
```

### Configure Server

1. In the "Server Configuration" tab, set parameters
2. Click "Browse..." to select a model file
3. After configuration, click "Save Configuration"
4. Click "Start Server" to begin service

### Download Models

1. In the "Model Management" tab, enter a HuggingFace URL
2. Click "Start Download"
3. After download completes, the model will be saved to the `models/` directory

### HuggingFace URL Format

```
# Full URL
https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf

# Short format
TheBloke/Llama-2-7B-GGUF/llama-2-7b.Q4_K_M.gguf
```

## Configuration Save Location

Configuration is automatically saved to `~/.llama-server-config.json`

## Project Structure

```
~/llama/
├── gui/
│   ├── __init__.py      # Entry point
│   ├── main.py          # GUI main program
│   ├── config.py        # Configuration management
│   ├── server_manager.py # Server process management
│   └── huggingface.py   # HuggingFace download
├── run-gui.sh           # GUI launch script
├── run/
│   ├── start-server.sh  # Server startup script
│   ├── run-cli.sh       # CLI run script
│   └── quantize-model.sh # Quantization script
├── models/              # Model file directory
├── llama.cpp/           # llama.cpp build directory
└── logs/                # Log directory
```

## Troubleshooting

### GUI Cannot Start

```bash
# Check if tkinter is installed
./venv/bin/python -c "import tkinter; print('OK')"

# If error, install tkinter
sudo apt-get install python3-tk
```

### Cannot Find llama-server

Ensure `llama.cpp/bin/llama-server` exists. If not, you need to build llama.cpp.

### Port Already in Use

If you receive a port-in-use error on startup, you can:
1. Stop the existing server
2. Use a different port
