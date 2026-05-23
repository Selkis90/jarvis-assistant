import json
import os
import subprocess
import webbrowser

ARCHIVO_COMANDOS = "mis_comandos.json"

def cargar_comandos():
    """Carga los comandos guardados"""
    if os.path.exists(ARCHIVO_COMANDOS):
        with open(ARCHIVO_COMANDOS, 'r') as f:
            return json.load(f)
    return {}

def guardar_comandos(comandos):
    """Guarda los comandos"""
    with open(ARCHIVO_COMANDOS, 'w') as f:
        json.dump(comandos, f, indent=2)

def agregar_comando():
    """Agrega un nuevo comando"""
    print("\n" + "="*50)
    print("➕ AGREGAR NUEVO COMANDO")
    print("="*50)
    
    frase = input("📝 ¿Qué frase quieres que entienda? (ej: 'abrir facebook'): ").lower().strip()
    tipo = input("🔧 ¿Qué tipo de acción? (1=abrir web, 2=ejecutar programa, 3=comando terminal): ")
    
    if tipo == "1":
        url = input("🌐 URL completa (ej: https://facebook.com): ")
        accion = {"tipo": "web", "url": url}
    elif tipo == "2":
        programa = input("💻 Nombre del programa (ej: firefox, code, gedit): ")
        accion = {"tipo": "programa", "nombre": programa}
    elif tipo == "3":
        comando = input("⌨️ Comando de terminal (ej: ls -la): ")
        accion = {"tipo": "terminal", "comando": comando}
    else:
        print("❌ Tipo no válido")
        return
    
    comandos = cargar_comandos()
    comandos[frase] = accion
    guardar_comandos(comandos)
    
    print(f"\n✅ Comando guardado! Cuando digas '{frase}', Jarvis hará la acción.")

def ver_comandos():
    """Muestra todos los comandos guardados"""
    comandos = cargar_comandos()
    
    if not comandos:
        print("\n📭 No hay comandos guardados aún.")
        return
    
    print("\n" + "="*50)
    print("📋 MIS COMANDOS GUARDADOS")
    print("="*50)
    
    for i, (frase, accion) in enumerate(comandos.items(), 1):
        print(f"\n{i}. 🎤 Frase: '{frase}'")
        if accion["tipo"] == "web":
            print(f"   🌐 Acción: Abrir {accion['url']}")
        elif accion["tipo"] == "programa":
            print(f"   💻 Acción: Ejecutar {accion['nombre']}")
        elif accion["tipo"] == "terminal":
            print(f"   ⌨️ Acción: Comando '{accion['comando']}'")

def eliminar_comando():
    """Elimina un comando"""
    comandos = cargar_comandos()
    
    if not comandos:
        print("\n📭 No hay comandos para eliminar.")
        return
    
    ver_comandos()
    
    frase = input("\n🗑️ Frase a eliminar: ").lower().strip()
    
    if frase in comandos:
        del comandos[frase]
        guardar_comandos(comandos)
        print(f"✅ Comando '{frase}' eliminado.")
    else:
        print(f"❌ No encontré '{frase}'")

def menu():
    """Menú principal"""
    while True:
        print("\n" + "="*50)
        print("🎮 CONFIGURACIÓN DE JARVIS")
        print("="*50)
        print("1. ➕ Agregar nuevo comando")
        print("2. 📋 Ver mis comandos")
        print("3. 🗑️ Eliminar comando")
        print("4. 🚀 Ejecutar Jarvis con mis comandos")
        print("5. ❌ Salir")
        
        opcion = input("\n👉 Elige una opción: ")
        
        if opcion == "1":
            agregar_comando()
        elif opcion == "2":
            ver_comandos()
        elif opcion == "3":
            eliminar_comando()
        elif opcion == "4":
            ejecutar_jarvis_con_comandos()
            break
        elif opcion == "5":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida")

def ejecutar_accion(accion):
    """Ejecuta la acción según el tipo"""
    if accion["tipo"] == "web":
        webbrowser.open(accion["url"])
        return f"Abriendo {accion['url']}"
    elif accion["tipo"] == "programa":
        os.system(f"{accion['nombre']} &")
        return f"Abriendo {accion['nombre']}"
    elif accion["tipo"] == "terminal":
        os.system(accion["comando"])
        return f"Ejecutando {accion['comando']}"
    return "Acción completada"

def ejecutar_jarvis_con_comandos():
    """Ejecuta Jarvis con los comandos personalizados"""
    import whisper
    import sounddevice as sd
    import numpy as np
    import subprocess
    import time
    import asyncio
    import edge_tts
    import tempfile
    import os
    from datetime import datetime
    
    print("\n🚀 Iniciando Jarvis con tus comandos...")
    
    model = whisper.load_model("base")
    comandos = cargar_comandos()
    
    async def hablar(texto):
        try:
            communicate = edge_tts.Communicate(texto, "es-ES-AlvaroNeural")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                temp_file = f.name
            await communicate.save(temp_file)
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file])
            os.unlink(temp_file)
        except:
            pass
    
    def hablar_sync(texto):
        asyncio.run(hablar(texto))
    
    print(f"✅ Comandos cargados: {len(comandos)} comandos personalizados")
    print("\n🎤 Jarvis escuchando... (Ctrl+C para salir)\n")
    
    try:
        while True:
            audio = sd.rec(int(3.5 * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()
            audio = audio * 2.0
            audio = np.clip(audio, -1, 1)
            
            energia = np.abs(audio).mean()
            
            if energia > 0.010:
                result = model.transcribe(audio, language="es", fp16=False, temperature=0.0)
                texto = result["text"].strip().lower()
                
                if texto and len(texto) > 2:
                    print(f"🧑: {texto}")
                    
                    # Verificar comandos personalizados
                    ejecutado = False
                    for frase, accion in comandos.items():
                        if frase in texto:
                            respuesta = ejecutar_accion(accion)
                            print(f"🤖 Jarvis: {respuesta}")
                            hablar_sync(respuesta)
                            ejecutado = True
                            break
                    
                    # Si no es comando personalizado, usar IA
                    if not ejecutado:
                        if "hora" in texto:
                            hora = datetime.now().strftime("%I:%M %p").lstrip("0")
                            respuesta = f"Son las {hora}"
                        elif "dia" in texto:
                            respuesta = f"Hoy es {datetime.now().strftime('%A')}"
                        else:
                            prompt = f"Eres JARVIS. Responde breve: {texto}"
                            result = subprocess.run(["ollama", "run", "llama3.2", prompt], capture_output=True, text=True, timeout=5)
                            respuesta = result.stdout.strip() or "No entendí"
                        
                        print(f"🤖 Jarvis: {respuesta}")
                        hablar_sync(respuesta)
                    
                    print()
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")

if __name__ == "__main__":
    menu()
