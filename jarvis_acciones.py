import whisper
import sounddevice as sd
import numpy as np
import subprocess
import time
import re
import asyncio
import edge_tts
import tempfile
import os
import webbrowser
from datetime import datetime

print("="*50)
print("🎤 JARVIS - Con Poderes Reales")
print("="*50)

print("📝 Cargando modelo de voz...")
model = whisper.load_model("base")
print("✅ Whisper listo")

print("🔊 Cargando motor de voz...")
print("✅ Jarvis listo!\n")

DURACION = 4.0
UMBRAL = 0.010
AMPLIFICACION = 2.0

# ========== FUNCIONES QUE JARVIS PUEDE EJECUTAR ==========

def abrir_navegador():
    webbrowser.open("https://www.google.com")
    return "Abriendo el navegador, señor."

def abrir_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Abriendo YouTube, señor."

def buscar_en_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Buscando {query} en Google"

def apagar_pc():
    return "¿Está seguro, señor? Diga 'confirmar apagado' para apagar el equipo."

def confirmar_apagado():
    os.system("shutdown now")
    return "Apagando el sistema... hasta luego, señor."

def reiniciar_pc():
    os.system("reboot")
    return "Reiniciando el sistema..."

def bloquear_pc():
    os.system("gnome-screensaver-command -l || loginctl lock-session")
    return "Bloqueando la pantalla, señor."

def tomar_nota(nota):
    with open("notas_jarvis.txt", "a") as f:
        f.write(f"{datetime.now()}: {nota}\n")
    return f"Nota guardada: {nota}"

def leer_notas():
    try:
        with open("notas_jarvis.txt", "r") as f:
            notas = f.read()
        if notas:
            return f"Tus notas: {notas[-500:]}"
        return "No hay notas guardadas, señor."
    except:
        return "No hay notas aún."

def abrir_programa(programa):
    programas = {
        "firefox": "firefox",
        "chrome": "google-chrome",
        "terminal": "gnome-terminal",
        "editor": "gedit",
        "archivos": "nautilus"
    }
    
    for nombre, comando in programas.items():
        if nombre in programa.lower():
            os.system(f"{comando} &")
            return f"Abriendo {nombre}, señor."
    
    return f"No reconozco el programa {programa}"

def obtener_clima():
    # Simula clima (puedes conectar a API real)
    return "No tengo acceso al clima en este momento, señor."

def ayuda():
    return """Comandos disponibles:
    • Abrir navegador / Abrir YouTube
    • Buscar [algo] en Google
    • Tomar nota: [texto]
    • Leer mis notas
    • Abrir [programa]
    • Bloquear pantalla
    • Qué hora es / Qué día es hoy
    • Apagar computadora / Reiniciar"""

# ========== CONFIGURACIÓN DE VOZ ==========

async def hablar(texto):
    try:
        voz = "es-ES-AlvaroNeural"
        communicate = edge_tts.Communicate(texto, voz)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_file = f.name
        await communicate.save(temp_file)
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file], check=False)
        os.unlink(temp_file)
    except:
        pass

def hablar_sync(texto):
    asyncio.run(hablar(texto))

# ========== PROCESAR COMANDOS ==========

def ejecutar_comando(pregunta):
    p = pregunta.lower().strip()
    
    # Comandos de hora y fecha
    if "hora" in p:
        ahora = datetime.now()
        hora = ahora.strftime("%I:%M %p").lstrip("0")
        return f"Son las {hora}"
    
    if "día" in p or "fecha" in p:
        ahora = datetime.now()
        return f"Hoy es {ahora.strftime('%A %d de %B')}"
    
    # Comandos de acción REAL
    if "abrir navegador" in p or "abrir google" in p:
        return abrir_navegador()
    
    if "abrir youtube" in p or "youtube" in p:
        return abrir_youtube()
    
    if "buscar" in p and "google" in p:
        query = p.replace("buscar", "").replace("en google", "").strip()
        return buscar_en_google(query)
    
    if "apagar" in p or "apagar pc" in p or "apagar computadora" in p:
        return apagar_pc()
    
    if "confirmar apagado" in p:
        return confirmar_apagado()
    
    if "reiniciar" in p:
        return reiniciar_pc()
    
    if "bloquear" in p or "bloquear pantalla" in p:
        return bloquear_pc()
    
    if "tomar nota" in p:
        nota = p.replace("tomar nota", "").strip()
        if nota:
            return tomar_nota(nota)
        return "¿Qué nota quiere que guarde, señor?"
    
    if "leer notas" in p or "mis notas" in p:
        return leer_notas()
    
    if "abrir" in p:
        programa = p.replace("abrir", "").strip()
        return abrir_programa(programa)
    
    if "ayuda" in p or "comandos" in p:
        return ayuda()
    
    if "gracias" in p:
        return "De nada, señor"
    
    # Si no es comando, usar IA para responder
    try:
        prompt = f"Eres JARVIS. Responde natural y breve (max 20 palabras): {p}"
        result = subprocess.run(["ollama", "run", "llama3.2", prompt], capture_output=True, text=True, timeout=5)
        return result.stdout.strip() or "No entendí, señor"
    except:
        return "Repita, por favor"

# ========== MAIN ==========

print("💡 JARVIS AHORA PUEDE EJECUTAR COMANDOS REALES:")
print("   • 'Abrir navegador' - Abre Google")
print("   • 'Abrir YouTube' - Abre YouTube")
print("   • 'Buscar [algo] en Google'")
print("   • 'Tomar nota: [texto]' - Guarda notas")
print("   • 'Leer mis notas' - Muestra notas")
print("   • 'Abrir firefox / chrome / terminal'")
print("   • 'Bloquear pantalla'")
print("   • 'Qué hora es' / 'Qué día es hoy'")
print("\n🎤 Jarvis escuchando... (Ctrl+C para salir)\n")

try:
    while True:
        audio = sd.rec(int(DURACION * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        audio = audio * AMPLIFICACION
        audio = np.clip(audio, -1, 1)
        
        energia = np.abs(audio).mean()
        barras = int(energia * 100)
        barra = "█" * min(barras, 25)
        print(f"\r🎤 [{barra:<25}] {energia:.4f}", end="", flush=True)
        
        if energia > UMBRAL:
            print()
            result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
            texto = result["text"].strip()
            
            if texto and len(texto) > 2:
                print(f"🧑: {texto}")
                respuesta = ejecutar_comando(texto)
                print(f"🤖 Jarvis: {respuesta}")
                hablar_sync(respuesta)
                print()
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\n👋 ¡Hasta luego, señor!")
