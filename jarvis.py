#!/usr/bin/env python3
"""
JARVIS - Asistente Personal Profesional
Versión completa con memoria, caché y configuración central
"""

import sys
import time
import threading
from datetime import datetime
from pathlib import Path

# Agregar módulos al path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import *
from modules.listener import Listener
from modules.brain import Brain
from modules.voice import Voice
from modules.actions import Actions

class Jarvis:
    def __init__(self):
        print("\n" + "="*60)
        print("   🎤 JARVIS - Asistente Personal Profesional v2.0")
        print("="*60)
        
        print("\n📦 Cargando módulos:")
        
        # Inicializar módulos
        self.listener = Listener(
            model_name=WHISPER_MODEL, 
            threshold=THRESHOLD, 
            duration=DURATION
        )
        self.brain = Brain(model=OLLAMA_MODEL)
        self.voice = Voice()
        self.actions = Actions()
        
        # Calibrar micrófono
        self.listener.calibrate(2)
        
        print("\n" + "="*60)
        print("✅ JARVIS LISTO PARA TRABAJAR")
        print("="*60)
        self.show_help()
    
    def show_help(self):
        """Muestra la ayuda"""
        print("\n💡 COMANDOS DISPONIBLES:")
        print("   • ¿Qué hora es? - Hora actual")
        print("   • ¿Qué día es hoy? - Fecha actual")
        print("   • Hola Jarvis - Saludo")
        print("   • Cómo estás - Estado del sistema")
        print("   • Abrir navegador / YouTube - Abre sitios web")
        print("   • Bloquear pantalla - Bloquea la PC")
        print("   • CUALQUIER pregunta - Jarvis responde con IA")
        print("\n🎤 Habla normalmente. Presiona Ctrl+C para salir.\n")
    
    def process_command(self, text):
        """Procesa el comando"""
        # Verificar acciones del sistema
        action_result = self.actions.execute(text)
        if action_result:
            return action_result
        
        # Verificar respuestas rápidas del cerebro
        quick_response = self.brain.get_quick_response(text)
        if quick_response:
            return quick_response
        
        # Usar IA para todo lo demás
        return self.brain.think(text)
    
    def run(self):
        """Bucle principal"""
        try:
            while True:
                # Escuchar
                text = self.listener.listen()
                
                if text:
                    print(f"\n🧑 Tú: {text}")
                    print("🤔 Procesando...", end=" ", flush=True)
                    
                    response = self.process_command(text)
                    
                    print(f"\n🤖 Jarvis: {response}")
                    self.voice.speak(response)
                    print()
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego, señor!")
            sys.exit(0)

if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()
