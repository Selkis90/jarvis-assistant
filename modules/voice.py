"""
Módulo de voz - Boca de Jarvis
Edge TTS con caché para respuestas rápidas
"""

import edge_tts
import asyncio
import tempfile
import subprocess
import os
import hashlib
from pathlib import Path

class Voice:
    def __init__(self, voice="es-ES-AlvaroNeural", cache_dir="data/voice_cache"):
        print(f"   🔊 Cargando motor de voz...")
        self.voice = voice
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = {}
        print(f"   ✅ Voice listo (caché: {self.cache_dir})")
    
    def _get_cache_key(self, text):
        """Genera clave de caché para el texto"""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def _speak_async(self, text):
        """Habla de forma asíncrona con caché"""
        if not text or len(text) < 2:
            return
        
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        try:
            # Verificar caché
            if cache_file.exists():
                subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(cache_file)])
                return
            
            # Generar nuevo audio
            communicate = edge_tts.Communicate(text, self.voice)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                temp_file = f.name
            
            await communicate.save(temp_file)
            
            # Guardar en caché
            import shutil
            shutil.copy(temp_file, cache_file)
            
            # Reproducir
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file])
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"   ⚠️ Error de voz: {e}")
    
    def speak(self, text):
        """Habla (versión síncrona)"""
        asyncio.run(self._speak_async(text))
    
    def clear_cache(self):
        """Limpia la caché de voz"""
        for file in self.cache_dir.glob("*.mp3"):
            file.unlink()
        return f"Caché limpiada ({len(list(self.cache_dir.glob('*.mp3')))} archivos)"
