"""
Configuración central de Jarvis
Todas las constantes y parámetros en un solo lugar
"""

import os
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).parent.parent
MODULES_DIR = BASE_DIR / "modules"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Crear directorios si no existen
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de Whisper
WHISPER_MODEL = "base"  # tiny, base, small, medium, large
WHISPER_DEVICE = "cpu"  # cuda para GPU, cpu para CPU

# Configuración de audio
SAMPLE_RATE = 16000
DURATION = 4.0
THRESHOLD = 0.008
AMPLIFICATION = 2.0

# Configuración de Ollama
OLLAMA_MODEL = "llama3.2"
OLLAMA_TIMEOUT = 10
OLLAMA_TEMPERATURE = 0.7
OLLAMA_MAX_TOKENS = 150

# Configuración de voz
VOICE_LANGUAGE = "es-ES"
VOICE_NAME = "AlvaroNeural"  # AlvaroNeural (masculino) o ElviraNeural (femenino)
VOICE_SPEED = 1.0

# Comandos del sistema
SYSTEM_COMMANDS = {
    "abrir navegador": "firefox",
    "abrir firefox": "firefox",
    "abrir chrome": "google-chrome",
    "abrir terminal": "gnome-terminal",
    "abrir editor": "gedit",
    "bloquear pantalla": "gnome-screensaver-command -l 2>/dev/null || loginctl lock-session",
    "apagar": "shutdown now",
    "reiniciar": "reboot",
}
