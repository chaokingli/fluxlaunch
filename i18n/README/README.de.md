[EN](README.en.md) | [中文](README.zh.md) | [DE](README.de.md)

# LLama Server GUI Manager

Ein grafisches Tool zur Verwaltung und Konfiguration von llama-server

## Funktionen

- **Serverkonfiguration** - Alle llama-server-Parameter konfigurieren
- **Modell-Download** - GGUF-Modelle von HuggingFace herunterladen
- **Prozessverwaltung** - Server starten/stoppen/neu starten
- **Statusüberwachung** - Serverstatus und Protokolle in Echtzeit anzeigen

## Installation

### 1. Systemabhängigkeiten installieren

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-tk python3.12-tk

# Wenn der obige Befehl ein Passwort erfordert, versuchen Sie:
# Mit apt (kein Passwort erforderlich)
sudo apt install python3-tk
```

### 2. Python-Abhängigkeiten installieren

```bash
cd ~/llama

# Virtuelle Umgebung erstellen (falls noch nicht geschehen)
python3 -m venv venv

# Virtuelle Umgebung aktivieren und Pakete installieren
./venv/bin/pip install customtkinter requests
```

## Verwendung

### GUI starten

```bash
# Option 1: Startskript verwenden
./run-gui.sh

# Option 2: Python direkt verwenden
./venv/bin/python -m gui.main
```

### Server konfigurieren

1. Im Tab "Serverkonfiguration" die Parameter einstellen
2. Auf "Durchsuchen..." klicken, um eine Modelldatei auszuwählen
3. Nach der Konfiguration auf "Konfiguration speichern" klicken
4. Auf "Server starten" klicken, um den Dienst zu beginnen

### Modelle herunterladen

1. Im Tab "Modellverwaltung" eine HuggingFace-URL eingeben
2. Auf "Download starten" klicken
3. Nach Abschluss des Downloads wird das Modell im `models/`-Verzeichnis gespeichert

### HuggingFace URL-Format

```
# Vollständige URL
https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf

# Kurzformat
TheBloke/Llama-2-7B-GGUF/llama-2-7b.Q4_K_M.gguf
```

## Konfigurationsspeicherort

Die Konfiguration wird automatisch unter `~/.llama-server-config.json` gespeichert

## Projektstruktur

```
~/llama/
├── gui/
│   ├── __init__.py      # Einstiegspunkt
│   ├── main.py          # GUI-Hauptprogramm
│   ├── config.py        # Konfigurationsverwaltung
│   ├── server_manager.py # Server-Prozessverwaltung
│   └── huggingface.py   # HuggingFace-Download
├── run-gui.sh           # GUI-Startskript
├── run/
│   ├── start-server.sh  # Server-Startskript
│   ├── run-cli.sh       # CLI-Ausführungsskript
│   └── quantize-model.sh # Quantisierungsskript
├── models/              # Modellverzeichnis
├── llama.cpp/           # llama.cpp-Build-Verzeichnis
└── logs/                # Protokollverzeichnis
```

## Fehlerbehebung

### GUI kann nicht gestartet werden

```bash
# Überprüfen, ob tkinter installiert ist
./venv/bin/python -c "import tkinter; print('OK')"

# Bei Fehler tkinter installieren
sudo apt-get install python3-tk
```

### llama-server nicht gefunden

Stellen Sie sicher, dass `llama.cpp/bin/llama-server` existiert. Falls nicht, muss llama.cpp kompiliert werden.

### Port bereits belegt

Wenn beim Start ein Port-in-use-Fehler angezeigt wird, können Sie:
1. Den bestehenden Server stoppen
2. Einen anderen Port verwenden
