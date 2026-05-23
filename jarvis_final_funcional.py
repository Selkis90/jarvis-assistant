import whisper
import sounddevice as sd
import numpy as np
import subprocess
import time
import asyncio
import edge_tts
import tempfile
import os
import json
import threading
import webbrowser
from datetime import datetime

print("="*50)
print("🎤 JARVIS - Versión Funcional")
print("="*50)

print("📝 Cargando modelo de voz...")
model = whisper.load_model("base")
print("✅ Whisper listo")

print("🔊 Cargando motor de voz...")
print("✅ Jarvis listo!")

# ========== CALIBRACIÓN AUTOMÁTICA DEL MICRÓFONO ==========
print("\n🔧 Calibrando micrófono...")
print("Por favor, habla NORMAL durante 2 segundos...")

audio_cal = sd.rec(int(2 * 16000), samplerate=16000, channels=1, dtype='float32')
sd.wait()
nivel_ruido = np.abs(audio_cal.flatten()).mean()

# El umbral será la mitad del nivel de tu voz
UMBRAL = max(0.003, nivel_ruido * 0.5)
print(f"✅ Micrófono calibrado - Nivel detectado: {nivel_ruido:.4f}")
print(f"✅ Umbral configurado: {UMBRAL:.4f}\n")

DURACION = 3.5
AMPLIFICACION = 2.5

# Sistema de interrupción
interrupcion_detectada = threading.Event()
hilo_escucha_activo = True

ARCHIVO_COMANDOS = "comandos_jarvis.json"

# ========== FUNCIONES DE VOZ ==========
async def hablar_con_interrupcion(texto):
    if not texto or len(texto) < 2:
        return
    
    print(f"\n🤖 Jarvis: {texto}")
    
    frases = texto.replace('?', '.').replace('!', '.').split('.')
    
    for frase in frases:
        if interrupcion_detectada.is_set():
            print("🔴 [INTERRUMPIDO]")
            return
        
        if frase.strip():
            try:
                voz = "es-ES-AlvaroNeural"
                communicate = edge_tts.Communicate(frase.strip() + ".", voz)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    temp_file = f.name
                
                await communicate.save(temp_file)
                
                proceso = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                while proceso.poll() is None:
                    if interrupcion_detectada.is_set():
                        proceso.terminate()
                        break
                    await asyncio.sleep(0.1)
                
                os.unlink(temp_file)
            except:
                pass

def hablar_sync(texto):
    asyncio.run(hablar_con_interrupcion(texto))

# ========== FUNCIONES DE INTERRUPCIÓN ==========
def verificar_interrupcion(audio):
    try:
        result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
        texto = result["text"].strip().lower()
        
        palabras_interrupcion = ["cuidado", "para", "alto", "espera", "stop"]
        
        for palabra in palabras_interrupcion:
            if palabra in texto:
                print(f"\n🔴 ¡INTERRUPCIÓN! - '{texto}'")
                interrupcion_detectada.set()
                return True
        return False
    except:
        return False

def hilo_escucha_interrupciones():
    while hilo_escucha_activo:
        try:
            audio = sd.rec(int(1.5 * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()
            audio = audio * 2.0
            audio = np.clip(audio, -1, 1)
            
            energia = np.abs(audio).mean()
            if energia > 0.005:
                verificar_interrupcion(audio)
            time.sleep(0.1)
        except:
            pass

# ========== FUNCIONES DE COMANDOS ==========
def obtener_hora():
    ahora = datetime.now()
    hora = ahora.strftime("%I:%M %p").lstrip("0")
    return f"Son las {hora}"

def obtener_fecha():
    ahora = datetime.now()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"Hoy es {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}"

def abrir_navegador():
    webbrowser.open("https://www.google.com")
    return "Abriendo navegador"

def abrir_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Abriendo YouTube"

def procesar_orden(texto):
    p = texto.lower().strip()
    
    # Mostrar depuración
    print(f"   [DEBUG] Procesando: '{p}'")
    
    if "hora" in p:
        return obtener_hora()
    if "día" in p or "día" in p:
        return obtener_fecha()
    if "hola" in p:
        return "¡Hola! ¿En qué puedo ayudarle?"
    if "cómo estás" in p or "como estas" in p:
        return "Todo bien, señor"
    if "gracias" in p:
        return "De nada"
    if "youtube" in p:
        return abrir_youtube()
    if "navegador" in p or "google" in p:
        return abrir_navegador()
    
    # Usar IA para lo demás
    try:
        prompt = f"Eres JARVIS. Responde breve (max 20 palabras): {texto}"
        result = subprocess.run(["ollama", "run", "llama3.2", prompt], capture_output=True, text=True, timeout=5)
        return result.stdout.strip() or "No entendí"
    except:
        return "Repita, por favor"

# ========== PROGRAMA PRINCIPAL ==========
def main():
    print("\n" + "="*50)
    print("🎤 JARVIS FUNCIONAL - Probado y listo")
    print("="*50)
    print("\n💡 PRUEBA ESTAS FRASES:")
    print("   • Hola Jarvis")
    print("   • ¿Qué hora es?")
    print("   • ¿Qué día es hoy?")
    print("   • Abrir YouTube")
    print("   • Cómo estás")
    print("\n🎤 Jarvis escuchando... (Ctrl+C para salir)\n")
    
    # Iniciar hilo de interrupción
    hilo_interrupcion = threading.Thread(target=hilo_escucha_interrupciones, daemon=True)
    hilo_interrupcion.start()
    
    try:
        while True:
            # Grabar
            audio = sd.rec(int(DURACION * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()
            audio = audio * AMPLIFICACION
            audio = np.clip(audio, -1, 1)
            
            energia = np.abs(audio).mean()
            
            # Barra visual
            barras = int(energia * 100)
            barra = "█" * min(barras, 20)
            print(f"\r🎤 [{barra:<20}] {energia:.4f} - Habla si nivel > {UMBRAL:.4f}", end="", flush=True)
            
            if energia > UMBRAL:
                print()
                print("🎤 Detectado - Procesando...")
                
                if interrupcion_detectada.is_set():
                    interrupcion_detectada.clear()
                
                result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
                texto = result["text"].strip()
                
                if texto and len(texto) > 2:
                    # Limpiar palabras de interrupción
                    for palabra in ["cuidado", "para", "alto", "espera", "stop"]:
                        texto = texto.replace(palabra, "").strip()
                    
                    if texto:
                        print(f"🧑 Tú: {texto}")
                        respuesta = procesar_orden(texto)
                        hablar_sync(respuesta)
                        print()
                else:
                    print("⚠️ No entendí - Habla más claro\n")
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego, señor!")
        global hilo_escucha_activo
        hilo_escucha_activo = False

if __name__ == "__main__":
    main()
