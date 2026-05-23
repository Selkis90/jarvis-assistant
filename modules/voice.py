import edge_tts
import asyncio
import tempfile
import subprocess
import os

class Voice:
    def __init__(self, voice="es-ES-AlvaroNeural"):
        print(f"   🔊 Cargando motor de voz...")
        self.voice = voice
        print(f"   ✅ Voice listo")
    
    async def _speak_async(self, text):
        """Habla de forma asíncrona"""
        if not text or len(text) < 2:
            return
        
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                temp_file = f.name
            await communicate.save(temp_file)
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file])
            os.unlink(temp_file)
        except Exception as e:
            print(f"   ⚠️ Error de voz: {e}")
    
    def speak(self, text):
        """Habla (versión síncrona)"""
        asyncio.run(self._speak_async(text))
    
    def speak_quiet(self, text):
        """Habla sin mostrar texto en consola"""
        asyncio.run(self._speak_async(text))
