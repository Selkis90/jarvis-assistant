#!/usr/bin/env python3
"""
JARVIS - Asistente Personal Profesional
Arquitectura modular con Whisper + Ollama + Edge TTS
"""

import sys
import time
import threading
from datetime import datetime

# Importar módulos
from modules.listener import Listener
from modules.brain import Brain
from modules.voice import Voice
from modules.actions import Actions

class Jarvis:
    def __init__(self):
        print("\n" + "="*60)
        print("   🎤 JARVIS - Asistente Personal Profesional")
        print("="*60)
        
        # Inicializar módulos
        print("\n📦 Cargando módulos:")
        self.listener = Listener(model_name="base", threshold=0.006, duration=3.5)
        self.brain = Brain(model="llama3.2")
        self.voice = Voice()
        self.actions = Actions()
        
        # Calibrar micrófono
        self.listener.calibrate(2)
        
        print("\n" + "="*60)
        print("✅ JARVIS LISTO PARA TRABAJAR")
        print("="*60)
        print("\n💡 EJEMPLOS DE COMANDOS:")
        print("   • ¿Qué hora es?")
        print("   • ¿Qué día es hoy?")
        print("   • Abrir YouTube")
        print("   • ¿Quién fue Einstein?")
        print("   • Explica qué es Python")
        print("\n🎤 Habla normalmente. Presiona Ctrl+C para salir.\n")
    
    def process_command(self, text):
        """Procesa el comando y ejecuta acciones"""
        # Primero, verificar acciones rápidas
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
                    
                    # Procesar
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
