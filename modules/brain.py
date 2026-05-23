import subprocess
import json
import re

class Brain:
    def __init__(self, model="llama3.2"):
        print(f"   🧠 Conectando con IA ({model})...")
        self.model = model
        self.context = []
        print(f"   ✅ Brain listo")
    
    def think(self, prompt, max_tokens=100, temperature=0.7):
        """Envía prompt a la IA y obtiene respuesta"""
        try:
            # Sistema prompt para Jarvis
            system_prompt = """Eres JARVIS, el asistente de Iron Man.
Características:
- Hablas español de forma natural
- Eres inteligente, servicial y con un toque de humor
- Respuestas cortas y directas (máximo 2-3 frases)
- Usas términos como "señor", "maestro" ocasionalmente
- NUNCA dices que eres una IA de texto, eres JARVIS"""

            full_prompt = f"{system_prompt}\n\nUsuario: {prompt}\nJARVIS:"
            
            result = subprocess.run(
                ["ollama", "run", self.model, full_prompt],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            response = result.stdout.strip()
            if not response:
                return "No entendí, señor. ¿Puede repetir?"
            
            # Guardar contexto
            self.context.append({"user": prompt, "assistant": response})
            if len(self.context) > 10:
                self.context = self.context[-10:]
            
            return response
            
        except subprocess.TimeoutExpired:
            return "Un momento, señor... estoy procesando."
        except Exception as e:
            return f"Error técnico. ¿Repite?"
    
    def get_quick_response(self, text):
        """Respuestas rápidas sin usar IA"""
        text_lower = text.lower()
        
        if "hora" in text_lower:
            from datetime import datetime
            return datetime.now().strftime("Son las %I:%M %p").lstrip("0")
        
        if "día" in text_lower or "fecha" in text_lower:
            from datetime import datetime
            return datetime.now().strftime("Hoy es %A %d de %B")
        
        if "hola" in text_lower:
            return "¡Hola! ¿En qué puedo ayudarle, señor?"
        
        if "como estas" in text_lower:
            return "Todo bien, señor. ¿Y usted?"
        
        if "gracias" in text_lower:
            return "De nada, para eso estoy."
        
        return None
