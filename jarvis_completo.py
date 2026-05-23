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
print("🎤 JARVIS - Escucha, Piensa y HABLA")
print("="*50)

print("📝 Cargando modelo de voz...")
model = whisper.load_model("base")
print("✅ Whisper listo")

print("🧠 Conectando con IA (llama3.2)...")
print("🔊 Cargando motor de voz...")
print("✅ Jarvis listo!\n")

DURACION = 4.0
UMBRAL = 0.010
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
        voz = "es-ES-AlvaroNeural"  # Voz masculina
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

def responder(pregunta):
    p = pregunta.lower().strip()
    
    # Respuestas rápidas
    if "hora" in p and ("qué" in p or "que" in p):
        return obtener_hora()
    if "día" in p or "fecha" in p:
        return obtener_fecha()
    if "gracias" in p:
        return "De nada, señor."
    if "adiós" in p or "hasta luego" in p:
        return "Hasta luego, señor."
    if "hola" in p:
        return "¡Hola! ¿En qué puedo ayudarle?"
    if "cómo estás" in p:
        return "Todo bien, señor. ¿Y usted?"
    
    # Usar IA para el resto
    try:
        prompt = f"""Eres JARVIS, asistente de Iron Man.
Responde en español, natural y amable. Máximo 20 palabras.

Pregunta: {p}
JARVIS:"""
        
        result = subprocess.run(
            ["ollama", "run", "llama3.2", prompt],
            capture_output=True,
            text=True,
            timeout=6
        )
        respuesta = result.stdout.strip()
        return respuesta if respuesta else "No entendí la pregunta"
        
    except:
        return "Un momento, señor..."

print("💡 Jarvis te ESCUCHA, PIENSA y TE HABLA:")
print("   • ¿Qué hora es?")
print("   • ¿Qué día es hoy?")
print("   • ¿Cómo estás?")
print("   • CUALQUIER otra pregunta")
print("\n🎤 Escuchando... (Ctrl+C para salir)\n")

try:
    while True:
        audio = sd.rec(int(DURACION * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        
        audio = audio * AMPLIFICACION
        audio = np.clip(audio, -1, 1)
        
        energia = np.abs(audio).mean()
        
        # Barra de nivel
        barras = int(energia * 100)
        barra = "█" * min(barras, 25)
        print(f"\r🎤 [{barra:<25}] {energia:.4f}", end="", flush=True)
        
        if energia > UMBRAL:
            print()
            
            result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
            texto = result["text"].strip()
            
            if texto and len(texto) > 2:
                print(f"🧑: {texto}")
                
                respuesta = responder(texto)
                print(f"🤖 Jarvis: {respuesta}")
                
                # ¡JARVIS HABLA!
                hablar_sync(respuesta)
                print()
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\n👋 ¡Hasta luego, señor!")
except Exception as e:
    print(f"\n❌ Error: {e}")
