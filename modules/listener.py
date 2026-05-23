"""
Módulo de escucha - Oídos de Jarvis
Con filtro de ruido mejorado
"""

import whisper
import sounddevice as sd
import numpy as np
import time
import re
from collections import deque

class Listener:
    def __init__(self, model_name="base", threshold=0.008, duration=3.5):
        print(f"   📡 Cargando modelo Whisper ({model_name})...")
        self.model = whisper.load_model(model_name)
        self.threshold = threshold
        self.duration = duration
        self.sample_rate = 16000
        self.last_texts = deque(maxlen=2)
        self.voice_profile = None
        self.silence_counter = 0
        print(f"   ✅ Listener listo")
    
    def calibrate(self, seconds=2):
        """Calibra el umbral con tu voz"""
        print(f"   🔧 Por favor, habla NORMAL durante {seconds} segundos (SOLO TÚ)...")
        audio = sd.rec(int(seconds * self.sample_rate), 
                       samplerate=self.sample_rate, 
                       channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        level = np.abs(audio).mean()
        self.threshold = max(0.006, level * 0.5)
        print(f"   ✅ Calibrado con TU voz - Umbral: {self.threshold:.4f}")
        return self.threshold
    
    def clean_text(self, text):
        """Limpia y corrige errores de transcripción"""
        if not text:
            return None
        
        text = text.lower().strip()
        
        # Correcciones comunes
        correcciones = {
            "que ahora es": "qué hora es",
            "que hora es": "qué hora es",
            "que ahora son": "qué hora es",
            "que horas son": "qué hora es",
            "que dia es hoy": "qué día es hoy",
            "que dia es": "qué día es hoy",
            "que dias hoy": "qué día es hoy",
            "el dia fue": "qué día es hoy",
            "hola": "hola",
            "como estas": "cómo estás",
            "gracias": "gracias",
        }
        
        for incorrecto, correcto in correcciones.items():
            if incorrecto in text:
                text = correcto
                break
        
        if len(text) < 3:
            return None
        
        if text in self.last_texts:
            return None
        
        self.last_texts.append(text)
        
        return text.strip()
    
    def listen(self):
        """Escucha y transcribe - Mejorado contra congelamiento"""
        try:
            audio = sd.rec(int(self.duration * self.sample_rate), 
                           samplerate=self.sample_rate, 
                           channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()
            
            # Normalizar y amplificar
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val
            
            audio = np.clip(audio * 2.0, -1, 1)
            
            energy = np.abs(audio).mean()
            
            # Si hay mucho silencio, resetear contador
            if energy < 0.003:
                self.silence_counter += 1
                if self.silence_counter > 10:
                    self.silence_counter = 0
                return None
            else:
                self.silence_counter = 0
            
            if energy < self.threshold:
                return None
            
            result = self.model.transcribe(
                audio, 
                language="es", 
                fp16=False, 
                temperature=0.0,
                no_speech_threshold=0.6
            )
            text = result["text"].strip()
            
            if not text or len(text) < 2:
                return None
            
            text = self.clean_text(text)
            
            return text
            
        except Exception as e:
            return None
