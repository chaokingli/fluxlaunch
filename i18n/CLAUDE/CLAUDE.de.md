<!-- Language: English | 语言：英文 | Sprache: Englisch -->
[**EN**](CLAUDE.en.md) | [**中文**](CLAUDE.zh.md) | [**DE**](CLAUDE.de.md)

# CLAUDE.md

Diese Datei bietet Anleitung für Claude Code (claude.ai/code) bei der Arbeit mit Code in diesem Repository.

## Projektübersicht

Dies ist ein **llama.cpp-Bereitstellungsprojekt** zum Ausführen von GGUF-Modellen mit TurboQuant-Unterstützung. Die Projektstruktur kapselt eine kompilierte llama.cpp-Installation mit Shell-Skripten für häufige Operationen ein.

## Verzeichnisstruktur

```
~/llama/
├── llama.cpp/        # Kompiliertes llama.cpp (CMake-Build, Release-Modus)
├── models/           # GGUF-Modelldateien
├── run/              # Hilfskripte
├── gui/              # GUI-Anwendung (CustomTkinter)
└── logs/             # Server- und CLI-Protokolle
```

## Befehle

### GUI-Anwendung

```bash
# GUI-Manager starten
python gui/main.py
```

### llama-server starten

```bash
# Standard: Port 8080, Kontext 4096, automatische Threads
./run/start-server.sh [model.gguf]

# Mit Umgebungvariablen-Überschreibungen
HOST=0.0.0.0 PORT=8080 CONTEXT_SIZE=4096 THREADS=8 ./run/start-server.sh models/model.gguf
```

### llama-cli ausführen

```bash
# Standard-Prompt: "你好", 256 Tokens, Temperatur 0.7
./run/run-cli.sh [model.gguf] [prompt]

# Beispiel
./run/run-cli.sh models/llama.gguf "Hello"
```

### Modelle quantisieren

```bash
./run/quantize-model.sh <input.gguf> <output.gguf> <quant_type>

# Quantisierungstypen: Q4_K_M, Q5_K_M, Q8_0, Q3_K_S, Q3_K_M, Q3_K_L, Q4_K_S, Q6_K, usw.
./run/quantize-model.sh model-f16.gguf model-q4.gguf Q4_K_M
```

### Direkter Binärzugriff

```bash
export LD_LIBRARY_PATH=/home/cklee/llama/llama.cpp/bin:$LD_LIBRARY_PATH

llama.cpp/bin/llama-server --model models/model.gguf --port 8080
llama.cpp/bin/llama-cli --model models/model.gguf --prompt "Hello"
llama.cpp/bin/llama-quantize input.gguf output.gguf Q4_K_M
```

## Architektur

### GUI-Anwendung (gui/)

- **main.py** - App-Einstiegspunkt, Hauptfenster
- **config.py** - Konfigurationsverwaltung (JSON speichern/laden)
- **server_manager.py** - Prozesslebenszyklus (starten/stoppen/neustarten)
- **huggingface.py** - HuggingFace-Modell-Download-Logik

### llama.cpp-Binärdateien

Befindlich in `llama.cpp/bin/`:
- **llama-server** - HTTP-API-Server
- **llama-cli** - CLI-Inferenz
- **llama-quantize** - Modellquantisierung
- **llama-bench** - Performance-Benchmarking
- **llama-perplexity** - Modellbewertung

### Bibliotheken

- `libllama.so` - Haupt-llama-Bibliothek
- `libggml.so` - Tensor-Bibliothek
- `libggml-cpu.so` - CPU-Backend
- `libmtmd.so` - Multimodale Unterstützung

### Skripte

Alle Skripte in `run/`:
- Setzen `LD_LIBRARY_PATH` um llama.cpp/bin einzuschließen
- Erstellen zeitgestempelte Protokolle in `logs/`
- Unterstützen Umgebungvariablen-Konfiguration
- Validieren Modelldatei-Existenz vor Ausführung

## Build-Informationen

llama.cpp ist vorkompiliert mit:
- CMake (Release-Modus, -O3)
- Geteilte Bibliotheken aktiviert
- GCC 13

Um llama.cpp neu zu kompilieren, arbeiten Sie im `llama.cpp/`-Verzeichnis mit Standard-CMake-Befehlen.

## Umgebungvariablen

| Variable | Standard | Beschreibung |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Server-Bindeadresse |
| PORT | 8080 | Server-Port |
| CONTEXT_SIZE | 4096 | Kontextfenstergröße |
| THREADS | nproc | CPU-Thread-Anzahl |
| N_PREDICT | 256 | Maximal vorherzusagende Tokens |
| TEMPERATURE | 0.7 | Sampling-Temperatur |

## Abhängigkeiten

- Python 3.x
- CustomTkinter: `pip install customtkinter`
- Requests: `pip install requests` (für HuggingFace-Downloads)
- Tkinter: `apt install python3-tk` (Systempaket für GUI)

## GUI-Anwendung

GUI-Manager starten:

```bash
./run-gui.sh
# oder
./venv/bin/python -m gui.main
```

## GUI-Funktionen

1. **Serverkonfiguration** - Alle llama-server-Parameter konfigurieren:
   - Modellpfad, Host, Port
   - Kontextgröße, Threads, Batch-Größe
   - Temperatur, GPU-Layer, Cache-Kapazität
   - Flash-Attention-Option

2. **Modellverwaltung** - Modellverwaltung:
   - Download von HuggingFace mit URL
   - Fortschrittsbalken und Abbruchunterstützung
   - Lokaler Modell-Browser
   - Liste beliebter GGUF-Repositories

3. **Statusüberwachung** - Statusüberwachung:
   - Echtzeit-Serverstatus
   - Server-Protokollanzeige
   - Browser zu API-Endpunkt öffnen
