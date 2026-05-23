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
from datetime import datetime

print("="*50)
print("🎤 JARVIS - Inteligencia Total + Voz Real")
print("="*50)

print("📝 Cargando modelo de voz...")
model = whisper.load_model("base")
print("✅ Whisper listo")

print("🧠 Conectando con IA (TinyLlama - más rápido)...")
print("🔊 Cargando motor de voz...")
print("✅ Jarvis listo!\n")

# Configuración
DURACION = 4.0
UMBRAL = 0.008
AMPLIFICACION = 2.0

def obtener_hora():
    ahora = datetime.now()
    hora = ahora.strftime("%I:%M %p").lstrip("0")
    return f"Son las {hora}"

def obtener_fecha():
    ahora = datetime.now()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"Hoy es {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}"

async def hablar(texto):
    """Jarvis habla con voz natural"""
    try:
        voz = "es-ES-AlvaroNeural"  # Voz masculina española
        communicate = edge_tts.Communicate(texto, voz)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_file = f.name
        
        await communicate.save(temp_file)
        
        subprocess.run([
            "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
            temp_file
        ], check=False)
        
        os.unlink(temp_file)
    except Exception as e:
        print(f"⚠️ Error de voz: {e}")

def hablar_sync(texto):
    """Versión síncrona para hablar"""
    asyncio.run(hablar(texto))

def preguntar_a_ia(pregunta):
    """Usa TinyLlama (más rápido) para responder"""
    try:
        prompt = f"""Eres JARVIS, asistente de Iron Man. 
Responde en español de forma natural y conversacional.
Máximo 25 palabras.

Pregunta: {pregunta}

JARVIS:"""
        
        result = subprocess.run(
            ["ollama", "run", "tinyllama", prompt],  # Cambiado a tinyllama
            capture_output=True,
            text=True,
            timeout=5  # Timeout más corto
        )
        
        respuesta = result.stdout.strip()
        if respuesta and len(respuesta) > 1:
            return respuesta
        return "No pude procesar tu pregunta."
        
    except subprocess.TimeoutExpired:
        return "Un momento, señor..."
    except Exception as e:
        return f"Error técnico. ¿Repites?"

def responder(pregunta):
    """Responde a CUALQUIER pregunta"""
    p = pregunta.lower().strip()
    
    # Respuestas rápidas (sin IA)
    if "hora" in p:
        return obtener_hora()
    if "dia" in p or "día" in p or "fecha" in p:
        return obtener_fecha()
    if "gracias" in p:
        return "De nada, para eso estoy."
    if "adios" in p or "adiós" in p:
        return "Hasta luego, señor."
    if "como te llamas" in p or "quien eres" in p:
        return "Soy Jarvis, su asistente personal."
    
    # Para todo lo demás, usar IA
    return preguntar_a_ia(p)

print("💡 Jarvis TE HABLA y responde a TODO:")
print("   • ¿Qué hora es? (rápido)")
print("   • ¿Qué día es hoy? (rápido)")
print("   • CUALQUIER otra pregunta")
print("\n🎤 Jarvis escuchando... (Ctrl+C para salir)\n")

try:
    while True:
        # Grabar
        audio = sd.rec(int(DURACION * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        
        # Amplificar
        audio = audio * AMPLIFICACION
        audio = np.clip(audio, -1, 1)
        
        energia = np.abs(audio).mean()
        
        # Barra de nivel
        barras = int(energia * 100)
        barra = "█" * min(barras, 25)
        print(f"\r🎤 [{barra:<25}] {energia:.4f}", end="", flush=True)
        
        if energia > UMBRAL:
            print()
            
            # Transcribir
            result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
            texto = result["text"].strip()
            
            if texto and len(texto) > 2:
                print(f"🧑 Tú: {texto}")
                print("🤔 Pensando...")
                
                respuesta = responder(texto)
                
                print(f"🤖 Jarvis: {respuesta}")
                hablar_sync(respuesta)  # ¡JARVIS HABLA!
                print()
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\n👋 ¡Hasta luego, señor!")
except Exception as e:
    print(f"\n❌ Error: {e}")
