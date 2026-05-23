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

# Calibrado específico para tu micrófono
DURACION = 3.5
UMBRAL = 0.0134  # Calibrado según tu voz

def obtener_hora():
    ahora = datetime.now()
    hora = ahora.strftime("%I:%M %p").lstrip("0")
    return f"Son las {hora}"

def obtener_fecha():
    ahora = datetime.now()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"Hoy es {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}"

def responder(pregunta):
    p = pregunta.lower().strip()
    
    # Depuración (comenta si no quieres verlo)
    print(f"   [DEBUG] Entendí: '{p}'")
    
    # Palabras clave
    if "hora" in p:
        return obtener_hora()
    
    if "dia" in p or "día" in p or "fecha" in p:
        return obtener_fecha()
    
    if "hola" in p or "saludos" in p:
        return "¡Hola! ¿En qué puedo ayudarte?"
    
    if "como estas" in p or "cómo estás" in p or "como está" in p:
        return "Todo bien, señor. ¿Y usted?"
    
    if "gracias" in p or "thank" in p:
        return "De nada, para eso estoy."
    
    if "chiste" in p or "broma" in p or "cuentame" in p:
        chistes = [
            "¿Qué le dice un techo a otro? Te echo de menos.",
            "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
            "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!"
        ]
        return np.random.choice(chistes)
    
    if "adios" in p or "adiós" in p or "hasta luego" in p:
        return "Hasta luego, señor. Ha sido un placer."
    
    if "iron man" in p or "tony stark" in p or "quien es" in p:
        return "Tony Stark, un multimillonario, ingeniero y superhéroe, también conocido como Iron Man."
    
    if "que puedes hacer" in p or "que haces" in p or "funciones" in p:
        return "Puedo decirte la hora, la fecha, contarte chistes, saludarte y responder preguntas básicas."
    
    # Respuesta genérica
    return None

print("💡 COMANDOS DISPONIBLES:")
print("   • ¿Qué hora es?")
print("   • ¿Qué día es hoy?")
print("   • Hola Jarvis")
print("   • ¿Cómo estás?")
print("   • Cuéntame un chiste")
print("   • ¿Quién es Iron Man?")
print("   • Adiós")
print("\n🎤 Jarvis escuchando... (Ctrl+C para salir)\n")

try:
    while True:
        # Grabar
        audio = sd.rec(int(DURACION * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        
        # Verificar nivel
        energia = np.abs(audio).mean()
        
        if energia > UMBRAL:
            # Transcribir
            result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
            texto = result["text"].strip()
            
            if texto and len(texto) > 2:
                respuesta = responder(texto)
                if respuesta:
                    print(f"\n🧑 Tú: {texto}")
                    print(f"🤖 Jarvis: {respuesta}\n")
                else:
                    # No responder si no entiende
                    pass
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\n👋 ¡Hasta luego, señor!")
