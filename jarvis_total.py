import whisper
import sounddevice as sd
import numpy as np
import subprocess
import time
import re
from datetime import datetime

print("="*50)
print("🎤 JARVIS - Inteligencia Total")
print("="*50)

print("📝 Cargando modelo de voz...")
model = whisper.load_model("base")
print("✅ Whisper listo")

print("🧠 Conectando con IA...")
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

def preguntar_a_ia(pregunta):
    """Envía cualquier pregunta a la IA y obtiene respuesta"""
    try:
        # Prompt para que la IA responda como Jarvis
        prompt = f"""Eres JARVIS, el asistente de Iron Man. 
Eres inteligente, amable y respondes en español.
Responde a esta pregunta de forma natural y conversacional (máximo 30 palabras):

Pregunta: {pregunta}

Respuesta de JARVIS:"""
        
        result = subprocess.run(
            ["ollama", "run", "llama3.2", prompt],
            capture_output=True,
            text=True,
            timeout=8
        )
        
        respuesta = result.stdout.strip()
        if respuesta and len(respuesta) > 1:
            return respuesta
        return "Lo siento, no pude procesar tu pregunta. ¿Puedes repetir?"
        
    except subprocess.TimeoutExpired:
        return "Estoy pensando... un momento por favor."
    except Exception as e:
        return f"Tengo un pequeño problema técnico. ¿Repites?"

def responder(pregunta):
    """Responde a CUALQUIER pregunta usando IA"""
    p = pregunta.lower().strip()
    
    # Primero, verificar si es una pregunta rápida (sin usar IA)
    if "hora" in p:
        return obtener_hora()
    if "dia" in p or "día" in p or "fecha" in p:
        return obtener_fecha()
    if "gracias" in p:
        return "De nada, para eso estoy."
    if "adios" in p or "adiós" in p:
        return "Hasta luego, señor. Ha sido un placer."
    
    # Para TODO lo demás, usar IA
    return preguntar_a_ia(pregunta)

print("💡 Jarvis responde a TODO lo que le preguntes:")
print("   • ¿Qué hora es?")
print("   • ¿Qué día es hoy?")
print("   • ¿Cuál es el sentido de la vida?")
print("   • ¿Quién fue Einstein?")
print("   • ¿Recomiéndame una película?")
print("   • CUALQUIER COSA que se te ocurra")
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
            print()  # Nueva línea
            
            # Transcribir
            result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
            texto = result["text"].strip()
            
            if texto and len(texto) > 2:
                print(f"\n🧑 Tú: {texto}")
                print("🤔 Pensando...")
                
                respuesta = responder(texto)
                
                print(f"🤖 Jarvis: {respuesta}\n")
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\n👋 ¡Hasta luego, señor!")
