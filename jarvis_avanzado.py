import whisper
import sounddevice as sd
import numpy as np
import subprocess
import time
import re
from datetime import datetime

print("="*60)
print("🎤 JARVIS AVANZADO - Asistente Personal")
print("="*60)

print("📝 Cargando modelo base (más preciso)...")
model = whisper.load_model("base")  # Cambiado de "tiny" a "base"
print("✅ Jarvis listo!\n")

DURACION = 4.0
UMBRAL = 0.006

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
    """Corrección avanzada de errores comunes"""
    texto = texto.lower()
    
    # Diccionario de correcciones
    correcciones = {
        # Hora
        r'\bobra\b': 'hora',
        r'\buro\b': 'hora',
        r'\bura\b': 'hora',
        r'que\s*obra': 'qué hora',
        r'que\s*uro': 'qué hora',
        r'qué\s*obra': 'qué hora',
        
        # Día
        r'\bdía\b': 'día',
        r'\bdias\b': 'días',
        r'que\s*día': 'qué día',
        r'que\s*dias': 'qué día',
        
        # Saludos
        r'\bola\b': 'hola',
        r'\bola\s*jarvis\b': 'hola jarvis',
        r'\bala\b': 'hola',
        
        # Fecha
        r'que\s*fecha': 'qué fecha',
        r'que\s*día\s*es\s*hoy': 'qué día es hoy',
        r'que\s*día\s*fue': 'qué día es hoy',
    }
    
    for patron, reemplazo in correcciones.items():
        texto = re.sub(patron, reemplazo, texto)
    
    # Eliminar caracteres extraños
    texto = re.sub(r'[^\w\s¿?¡!áéíóúñü]', '', texto)
    
    return texto.strip()

def responder(pregunta):
    pregunta = corregir_transcripcion(pregunta)
    
    print(f"   📝 Texto corregido: {pregunta}")
    
    # Detectar intenciones
    if re.search(r'qu[eé]\s*hora|hora\s*es|decir\s*la\s*hora', pregunta):
        return obtener_hora()
    
    if re.search(r'qu[eé]\s*d[ií]a|d[ií]a\s*es\s*hoy|qu[eé]\s*fecha', pregunta):
        return obtener_fecha()
    
    if re.search(r'hola\s*jarvis|jarvis\s*hola|saludos', pregunta):
        return "¡Hola! ¿En qué puedo ayudarte?"
    
    if re.search(r'c[oó]mo\s*est[aá]s|qu[eé] tal|todo bien', pregunta):
        return "Todo bien, señor. ¿Y usted?"
    
    if re.search(r'gracias|thank', pregunta):
        return "De nada, para eso estoy."
    
    if re.search(r'chiste|broma|risa', pregunta):
        chistes = [
            "¿Qué le dice un techo a otro? Te echo de menos.",
            "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
            "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!"
        ]
        return np.random.choice(chistes)
    
    if re.search(r'adi[oó]s|hasta luego|nos vemos', pregunta):
        return "Hasta luego, señor. Ha sido un placer."
    
    if re.search(r'iron\s*man|tony\s*stark|qu[ií]en\s*es', pregunta):
        return "Tony Stark, un genio multimillonario playboy y filántropo, también conocido como Iron Man."
    
    # Respuesta por defecto con IA
    try:
        prompt = f"""Eres JARVIS, asistente de Iron Man. Responde en español, de forma natural y amigable. Máximo 15 palabras. Pregunta: {pregunta}"""
        result = subprocess.run(
            ["ollama", "run", "llama3.2", prompt],
            capture_output=True,
            text=True,
            timeout=5
        )
        respuesta = result.stdout.strip()
        if respuesta and len(respuesta) > 2:
            return respuesta
        return "No entendí la pregunta. ¿Podrías repetir?"
    except:
        return "Disculpe, estoy procesando. ¿Repite por favor?"

print("💡 EJEMPLOS DE PREGUNTAS:")
print("   • ¿Qué hora es?")
print("   • ¿Qué día es hoy?")
print("   • Hola Jarvis")
print("   • ¿Cómo estás?")
print("   • ¿Quién es Iron Man?")
print("\n🎤 Jarvis escuchando... (Ctrl+C para salir)\n")

try:
    while True:
        print("\r🎤 Escuchando...", end="", flush=True)
        
        audio = sd.rec(int(DURACION * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        
        # Normalizar audio
        audio = audio / (np.max(np.abs(audio)) + 0.01)
        
        energia = np.abs(audio).mean()
        
        if energia > UMBRAL:
            print(f"\n🔊 Volumen detectado: {energia:.3f}")
            print("🔄 Transcribiendo...")
            
            result = model.transcribe(
                audio, 
                language="es", 
                fp16=False,
                temperature=0.0,
                no_speech_threshold=0.6,
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0
            )
            
            texto_original = result["text"].strip()
            
            if texto_original and len(texto_original) > 2:
                print(f"📝 Original: {texto_original}")
                respuesta = responder(texto_original)
                print(f"🤖 JARVIS: {respuesta}")
            else:
                print("⚠️ No se detectaron palabras claras")
            
            print()
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n👋 ¡Hasta luego! JARVIS desactivado.")
except Exception as e:
    print(f"\n❌ Error: {e}")
