import whisper
import sounddevice as sd
import numpy as np
import subprocess
import time
import re
from datetime import datetime

print("="*50)
print("🎤 JARVIS - Inteligente y Preciso")
print("="*50)

print("📝 Cargando modelo de voz...")
model = whisper.load_model("base")
print("✅ Whisper listo")

print("🧠 Conectando con IA (llama3.2 - más inteligente)...")
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

def corregir_transcripcion(texto):
    """Corrige errores comunes de Whisper"""
    texto = texto.lower().strip()
    
    # Correcciones específicas
    correcciones = {
        r'que\s*ahora\s*es': 'qué hora es',
        r'que\s*hora\s*es': 'qué hora es',
        r'que\s*dias\s*hoy': 'qué día es hoy',
        r'que\s*día\s*hoy': 'qué día es hoy',
        r'que\s*fue': 'qué fue',
        r'albert\s*einstein': 'Albert Einstein',
        r'que\s*quería\s*soy': 'quién soy',
        r'que\s*voy\s*a\s*hacer': 'qué voy a hacer',
    }
    
    for patron, reemplazo in correcciones.items():
        texto = re.sub(patron, reemplazo, texto)
    
    return texto

def responder(pregunta):
    """Responde usando IA (llama3.2)"""
    pregunta = corregir_transcripcion(pregunta)
    
    # Respuestas rápidas (sin IA)
    if "hora" in pregunta and "qué" in pregunta:
        return obtener_hora()
    if "día" in pregunta and "qué" in pregunta:
        return obtener_fecha()
    if "gracias" in pregunta:
        return "De nada, señor."
    if "adiós" in pregunta or "hasta luego" in pregunta:
        return "Hasta luego, señor."
    
    # Usar IA para todo lo demás
    try:
        prompt = f"""Eres JARVIS, asistente de Iron Man. 
Eres inteligente, amable y respondes en español.
Responde de forma natural y conversacional (máximo 30 palabras).

Usuario: {pregunta}
JARVIS:"""
        
        result = subprocess.run(
            ["ollama", "run", "llama3.2", prompt],
            capture_output=True,
            text=True,
            timeout=6
        )
        
        respuesta = result.stdout.strip()
        if respuesta and len(respuesta) > 1:
            return respuesta
        return "No entendí bien. ¿Puedes repetir?"
        
    except subprocess.TimeoutExpired:
        return "Un momento, señor..."
    except:
        return "Disculpe, ¿puede repetir la pregunta?"

print("💡 CONSEJOS PARA HABLAR CON JARVIS:")
print("   • Habla CLARO y DESPACIO")
print("   • Pronuncia bien: '¿Qué hora es?'")
print("   • Para Einstein, di: 'Albert Einstein'")
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
            texto_original = result["text"].strip()
            
            if texto_original and len(texto_original) > 2:
                print(f"📝 Dijiste: {texto_original}")
                
                respuesta = responder(texto_original)
                print(f"🤖 Jarvis: {respuesta}\n")
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\n👋 ¡Hasta luego, señor!")
