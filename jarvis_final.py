import whisper
import sounddevice as sd
import numpy as np
import subprocess
import time
import re
from datetime import datetime

print("="*50)
print("🎤 JARVIS - Asistente Personal")
print("="*50)

print("📝 Cargando modelo...")
model = whisper.load_model("base")
print("✅ Jarvis listo!\n")

DURACION = 3.5
UMBRAL = 0.010

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
    texto = texto.lower().strip()
    
    # Correcciones rápidas
    texto = re.sub(r'\b(que|qe|ke)\s*(ahora|ora|ura|obra)\b', 'qué hora', texto)
    texto = re.sub(r'\b(que|qe|ke)\s*(dia|día)\s*(es|fue|soy)\b', 'qué día es hoy', texto)
    texto = re.sub(r'\bola\b', 'hola', texto)
    texto = re.sub(r'\bcomo\s+estas\b', 'cómo estás', texto)
    texto = re.sub(r'\bgracias\b', 'gracias', texto)
    texto = re.sub(r'\bchiste\b', 'chiste', texto)
    texto = re.sub(r'\biron\s*man\b', 'iron man', texto)
    
    return texto

def responder(pregunta):
    pregunta = corregir_transcripcion(pregunta)
    
    # Detectar intenciones
    if "hora" in pregunta:
        return obtener_hora()
    
    if "dia" in pregunta or "día" in pregunta or "fecha" in pregunta:
        return obtener_fecha()
    
    if "hola" in pregunta:
        return "¡Hola! ¿En qué puedo ayudarte?"
    
    if "como estas" in pregunta or "cómo estás" in pregunta:
        return "Todo bien, señor. ¿Y usted?"
    
    if "gracias" in pregunta:
        return "De nada, para eso estoy."
    
    if "chiste" in pregunta:
        chistes = [
            "¿Qué le dice un techo a otro? Te echo de menos.",
            "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
            "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!"
        ]
        return np.random.choice(chistes)
    
    if "adios" in pregunta or "adiós" in pregunta:
        return "Hasta luego, señor."
    
    if "iron man" in pregunta or "tony stark" in pregunta:
        return "Tony Stark, un multimillonario, ingeniero y superhéroe."
    
    # Si no reconoce, usar Ollama
    try:
        prompt = f"Responde en español de forma amigable y corta (máximo 15 palabras): {pregunta}"
        result = subprocess.run(
            ["ollama", "run", "llama3.2", prompt],
            capture_output=True,
            text=True,
            timeout=4
        )
        respuesta = result.stdout.strip()
        if respuesta and len(respuesta) > 2:
            return respuesta
        return "No entendí, ¿puedes repetir?"
    except:
        return "Repite por favor, no te escuché bien."

print("💡 Pregúntame:")
print("   • ¿Qué hora es?")
print("   • ¿Qué día es hoy?")
print("   • Hola Jarvis")
print("   • ¿Cómo estás?")
print("   • Cuéntame un chiste")
print("   • ¿Quién es Iron Man?")
print("\n🎤 Escuchando... (Ctrl+C para salir)\n")

try:
    while True:
        audio = sd.rec(int(DURACION * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        
        energia = np.abs(audio).mean()
        
        if energia > UMBRAL:
            result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
            texto = result["text"].strip()
            
            if texto and len(texto) > 2:
                respuesta = responder(texto)
                print(f"\n🧑: {texto}")
                print(f"🤖: {respuesta}\n")
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\n👋 ¡Hasta luego, señor!")
