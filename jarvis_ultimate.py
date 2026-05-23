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
import queue
import webbrowser
from datetime import datetime

# ========== CONFIGURACIÓN ==========
print("="*50)
print("🎤 JARVIS ULTIMATE - Con todas las funciones")
print("="*50)

print("📝 Cargando modelo de voz...")
model = whisper.load_model("base")
print("✅ Whisper listo")

print("🔊 Cargando motor de voz...")
print("✅ Jarvis listo!")

# Configuración de audio
DURACION = 3.5
UMBRAL = 0.003
AMPLIFICACION = 2.0

# Sistema de interrupción
interrupcion_detectada = threading.Event()
hilo_escucha_activo = True

# Sistema de comandos personalizados
ARCHIVO_COMANDOS = "comandos_jarvis.json"

# ========== FUNCIONES DE VOZ ==========
async def hablar_con_interrupcion(texto):
    """Habla permitiendo interrupción"""
    global interrupcion_detectada
    
    if not texto or len(texto) < 2:
        return
    
    print(f"\n🤖 Jarvis: {texto}")
    
    # Dividir en frases cortas
    frases = texto.replace('?', '.').replace('!', '.').split('.')
    
    for frase in frases:
        if interrupcion_detectada.is_set():
            print("🔴 [INTERRUMPIDO - Escuchando nueva orden]")
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
                
            except Exception as e:
                print(f"⚠️ Error de voz: {e}")

def hablar_sync(texto):
    """Versión síncrona para hablar"""
    asyncio.run(hablar_con_interrupcion(texto))

# ========== FUNCIONES DE INTERRUPCIÓN ==========
def verificar_interrupcion(audio):
    """Verifica si se dijo una palabra de interrupción"""
    global interrupcion_detectada
    
    try:
        result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
        texto = result["text"].strip().lower()
        
        palabras_interrupcion = ["cuidado", "para", "alto", "espera", "stop", "javier", "oye", "atencion"]
        
        for palabra in palabras_interrupcion:
            if palabra in texto:
                print(f"\n🔴 ¡INTERRUPCIÓN! Dijiste: '{texto}'")
                interrupcion_detectada.set()
                return True
        return False
    except:
        return False

def hilo_escucha_interrupciones():
    """Hilo separado que escucha constantemente interrupciones"""
    print("🎤 Modo interrupción activado - Di 'CUIDADO' o 'PARA' para interrumpir")
    
    while hilo_escucha_activo:
        try:
            audio = sd.rec(int(1.5 * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()
            audio = audio * 2.0
            audio = np.clip(audio, -1, 1)
            
            energia = np.abs(audio).mean()
            
            if energia > 0.008:
                verificar_interrupcion(audio)
            
            time.sleep(0.1)
        except:
            pass

# ========== FUNCIONES DE COMANDOS PERSONALIZADOS ==========
def cargar_comandos():
    """Carga comandos personalizados"""
    if os.path.exists(ARCHIVO_COMANDOS):
        with open(ARCHIVO_COMANDOS, 'r') as f:
            return json.load(f)
    return {}

def guardar_comando(frase, accion):
    """Guarda un comando personalizado"""
    comandos = cargar_comandos()
    comandos[frase.lower()] = accion
    with open(ARCHIVO_COMANDOS, 'w') as f:
        json.dump(comandos, f, indent=2)
    return f"Comando '{frase}' guardado"

def ejecutar_comando_personalizado(comando):
    """Ejecuta un comando personalizado"""
    if comando["tipo"] == "web":
        webbrowser.open(comando["url"])
        return f"Abriendo {comando['url']}"
    elif comando["tipo"] == "programa":
        os.system(f"{comando['nombre']} &")
        return f"Abriendo {comando['nombre']}"
    elif comando["tipo"] == "terminal":
        resultado = subprocess.run(comando["comando"], shell=True, capture_output=True, text=True)
        if resultado.stdout:
            return resultado.stdout[:200]
        return f"Comando ejecutado: {comando['comando']}"
    return "Comando ejecutado"

# ========== COMANDOS INTEGRADOS ==========
def abrir_navegador():
    webbrowser.open("https://www.google.com")
    return "Abriendo navegador, señor"

def abrir_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Abriendo YouTube, señor"

def buscar_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Buscando {query} en Google"

def tomar_nota(nota):
    with open("notas_jarvis.txt", "a", encoding='utf-8') as f:
        f.write(f"{datetime.now()}: {nota}\n")
    return f"Nota guardada: {nota}"

def leer_notas():
    try:
        with open("notas_jarvis.txt", "r", encoding='utf-8') as f:
            notas = f.read()
        if notas:
            return f"Tus últimas notas: {notas[-500:]}"
        return "No hay notas guardadas"
    except:
        return "No hay notas aún"

def abrir_programa(programa):
    programas = {
        "firefox": "firefox", "chrome": "google-chrome", "navegador": "firefox",
        "terminal": "gnome-terminal", "consola": "gnome-terminal",
        "editor": "gedit", "bloc": "gedit", "código": "code", "vscode": "code"
    }
    
    for nombre, comando in programas.items():
        if nombre in programa.lower():
            os.system(f"{comando} &")
            return f"Abriendo {nombre}, señor"
    
    return f"No conozco el programa '{programa}'"

def bloquear_pantalla():
    os.system("gnome-screensaver-command -l 2>/dev/null || loginctl lock-session 2>/dev/null")
    return "Pantalla bloqueada, señor"

def obtener_clima():
    return "Conectando a servicio de clima... (función en desarrollo)"

def obtener_hora():
    ahora = datetime.now()
    hora = ahora.strftime("%I:%M %p").lstrip("0")
    return f"Son las {hora}"

def obtener_fecha():
    ahora = datetime.now()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"Hoy es {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}"

def mostrar_ayuda():
    ayuda = """
    🎮 COMANDOS DISPONIBLES:
    
    📅 BÁSICOS:
    • ¿Qué hora es? - Dice la hora
    • ¿Qué día es hoy? - Dice la fecha
    • Hola Jarvis - Saludo
    • ¿Cómo estás? - Estado
    • Gracias / Adiós - Cortesía
    
    🌐 INTERNET:
    • Abrir navegador - Abre Google
    • Abrir YouTube - Abre YouTube
    • Buscar [algo] en Google
  
    📝 NOTAS:
    • Tomar nota: [texto] - Guarda nota
    • Leer mis notas - Muestra notas
  
    💻 SISTEMA:
    • Abrir [programa] - Firefox, Chrome, Terminal, VS Code
    • Bloquear pantalla - Bloquea el equipo
  
    🛑 CONTROL:
    • CUIDADO, PARA, STOP - Interrumpe a Jarvis
    • Guardar comando - Crea comandos personalizados
  
    🤖 INTELIGENCIA:
    • CUALQUIER pregunta - Jarvis responde con IA
    """
    return ayuda

# ========== PROCESAMIENTO DE ÓRDENES ==========
def procesar_orden(texto):
    """Procesa la orden y devuelve respuesta"""
    p = texto.lower().strip()
    
    # Comandos básicos
    if "hora" in p:
        return obtener_hora()
    if "día" in p or "fecha" in p:
        return obtener_fecha()
    if "hola" in p:
        return "¡Hola! ¿En qué puedo ayudarle, señor?"
    if "cómo estás" in p or "como estas" in p:
        return "Todo bien, señor. ¿Y usted?"
    if "gracias" in p:
        return "De nada, para eso estoy."
    if "adiós" in p or "adios" in p:
        return "Hasta luego, señor."
    if "ayuda" in p or "comandos" in p:
        return mostrar_ayuda()
    
    # Comandos de sistema
    if "abrir navegador" in p or "abrir google" in p:
        return abrir_navegador()
    if "abrir youtube" in p:
        return abrir_youtube()
    if "buscar" in p and "google" in p:
        query = p.replace("buscar", "").replace("en google", "").strip()
        return buscar_google(query)
    if "tomar nota" in p:
        nota = p.replace("tomar nota", "").replace(":", "").strip()
        if nota:
            return tomar_nota(nota)
        return "¿Qué nota quiere que guarde, señor?"
    if "leer notas" in p or "mis notas" in p:
        return leer_notas()
    if "abrir" in p:
        programa = p.replace("abrir", "").strip()
        return abrir_programa(programa)
    if "bloquear pantalla" in p or "bloquear" in p:
        return bloquear_pantalla()
    if "clima" in p or "tiempo" in p:
        return obtener_clima()
    
    # Comandos personalizados
    comandos = cargar_comandos()
    for frase, accion in comandos.items():
        if frase in p:
            return ejecutar_comando_personalizado(accion)
    
    # Guardar nuevo comando
    if "guardar comando" in p:
        return "Para guardar un comando, usa el menú de configuración"
    
    # Si no reconoce, usar IA
    try:
        prompt = f"Eres JARVIS, asistente de Iron Man. Responde de forma natural y breve (máximo 25 palabras) en español: {texto}"
        result = subprocess.run(["ollama", "run", "llama3.2", prompt], capture_output=True, text=True, timeout=6)
        return result.stdout.strip() or "No entendí, señor. ¿Puede repetir?"
    except subprocess.TimeoutExpired:
        return "Un momento, señor..."
    except:
        return "Disculpe, ¿puede repetir la pregunta?"

# ========== PROGRAMA PRINCIPAL ==========
def main():
    print("\n" + "="*50)
    print("🎤 JARVIS ULTIMATE - Totalmente equipado")
    print("="*50)
    print("\n💡 CARACTERÍSTICAS:")
    print("   ✅ Te escucha continuamente")
    print("   ✅ Te responde por VOZ")
    print("   ✅ Puedes INTERRUMPIR diciendo 'CUIDADO'")
    print("   ✅ Abre programas y navegadores")
    print("   ✅ Guarda y lee notas")
    print("   ✅ Comandos PERSONALIZABLES")
    print("   ✅ Responde CUALQUIER pregunta con IA")
    print("\n🎤 Jarvis escuchando... (Ctrl+C para salir)\n")
    
    # Iniciar hilo de interrupción
    hilo_interrupcion = threading.Thread(target=hilo_escucha_interrupciones, daemon=True)
    hilo_interrupcion.start()
    
    try:
        while True:
            # Barra de nivel visual
            if not interrupcion_detectada.is_set():
                print("\r🎤 Escuchando...", end="", flush=True)
            
            # Grabar audio
            audio = sd.rec(int(DURACION * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()
            audio = audio * AMPLIFICACION
            audio = np.clip(audio, -1, 1)
            
            energia = np.abs(audio).mean()
            
            # Mostrar nivel
            barras = int(energia * 100)
            barra = "█" * min(barras, 25)
            print(f"\r🎤 [{barra:<25}] {energia:.4f}", end="", flush=True)
            
            if energia > UMBRAL:
                print()
                
                # Limpiar interrupción si existe
                if interrupcion_detectada.is_set():
                    interrupcion_detectada.clear()
                
                # Transcribir
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
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego, señor!")
        global hilo_escucha_activo
        hilo_escucha_activo = False

if __name__ == "__main__":
    main()
