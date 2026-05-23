import whisper
import sounddevice as sd
import numpy as np
import time

class Listener:
    def __init__(self, model_name="base", threshold=0.008, duration=3.5):
        print(f"   📡 Cargando modelo Whisper ({model_name})...")
        self.model = whisper.load_model(model_name)
        self.threshold = threshold
        self.duration = duration
        self.sample_rate = 16000
        print(f"   ✅ Listener listo (umbral: {threshold})")
    
    def calibrate(self, seconds=2):
        """Calibra el umbral según el ambiente"""
        print(f"   🔧 Calibrando micrófono (habla normal {seconds}s)...")
        audio = sd.rec(int(seconds * self.sample_rate), 
                       samplerate=self.sample_rate, 
                       channels=1, dtype='float32')
        sd.wait()
        level = np.abs(audio.flatten()).mean()
        self.threshold = max(0.005, level * 0.4)
        print(f"   ✅ Umbral calibrado: {self.threshold:.4f}")
        return self.threshold
    
    def listen(self):
        """Escucha y transcribe"""
        audio = sd.rec(int(self.duration * self.sample_rate), 
                       samplerate=self.sample_rate, 
                       channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        
        # Normalizar
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        energy = np.abs(audio).mean()
        
        if energy < self.threshold:
            return None
        
        result = self.model.transcribe(audio, language="es", fp16=False, temperature=0.0)
        text = result["text"].strip()
        
        return text if len(text) > 2 else None
