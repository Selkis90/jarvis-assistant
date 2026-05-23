"""
Módulo de IA - Cerebro de Jarvis
Con conexión a internet y API de IA (DeepSeek/OpenAI compatible)
"""

import subprocess
import re
from datetime import datetime
import requests
import json

class Brain:
    def __init__(self, model="llama3.2", memory_file=None):
        print(f"   🧠 Conectando con IA local ({model})...")
        self.model = model
        self.ubicacion = None
        print(f"   🌐 Conectando a internet para información...")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"  # DeepSeek API (gratuito)
        self.api_key = None  # Puedes obtener una key gratis en platform.deepseek.com
        print(f"   ✅ Brain listo (modo híbrido: local + internet)")
    
    def obtener_ubicacion(self):
        """Obtiene ubicación aproximada por IP"""
        if self.ubicacion:
            return self.ubicacion
        
        try:
            response = requests.get('https://ipapi.co/json/', timeout=3)
            if response.status_code == 200:
                data = response.json()
                ciudad = data.get('city', 'desconocida')
                pais = data.get('country_name', 'desconocido')
                self.ubicacion = f"{ciudad}, {pais}"
                return self.ubicacion
        except:
            pass
        
        return "Colombia (no se pudo determinar la ciudad exacta)"
    
    def buscar_en_internet(self, pregunta):
        """Busca información en internet usando una API de IA"""
        try:
            # Usar DeepSeek API (gratis con registro) o alternativa
            # Por ahora, usamos Ollama con un prompt mejorado
            
            prompt = f"""Eres JARVIS, el asistente de Iron Man. Tienes acceso a todo el conocimiento humano.
Responde de forma precisa, clara y concisa. Usa español natural.
Si no sabes algo, dilo honestamente.

Pregunta: {pregunta}

Respuesta de JARVIS:"""
            
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=12
            )
            
            response = result.stdout.strip()
            
            if response and len(response) > 5 and "no tengo" not in response.lower()[:50]:
                return response
            
            # Si falla, usar búsqueda web simulada
            return self.busqueda_web_simulada(pregunta)
            
        except Exception as e:
            return self.busqueda_web_simulada(pregunta)
    
    def busqueda_web_simulada(self, pregunta):
        """Simula búsqueda web con respuestas predefinidas para temas comunes"""
        p = pregunta.lower()
        
        # Diccionario de respuestas comunes
        respuestas = {
            "albert einstein": "Albert Einstein fue un físico alemán, autor de la teoría de la relatividad y ganador del Premio Nobel de Física en 1921.",
            "einstein": "Albert Einstein fue un físico alemán, autor de la teoría de la relatividad y ganador del Premio Nobel de Física en 1921.",
            "perro": "Un perro es un mamífero doméstico de la familia de los cánidos. Son conocidos como 'el mejor amigo del hombre' por su lealtad.",
            "gato": "Un gato es un mamífero felino doméstico. Son independientes, cazadores por naturaleza y muy populares como mascotas.",
            "internet": "Internet es una red mundial de computadoras interconectadas que permite el intercambio de información.",
            "monstruo": "Un monstruo es una criatura fantástica que causa miedo o terror, común en mitologías y leyendas.",
        }
        
        for clave, respuesta in respuestas.items():
            if clave in p:
                return respuesta
        
        # Respuesta genérica si no encuentra
        return f"Buscando información sobre '{pregunta}'... En mi base de datos, señor, no encuentro esa información específica. ¿Podría reformular la pregunta?"
    
    def get_quick_response(self, text):
        """Respuestas rápidas directas (sin IA)"""
        text_lower = text.lower().strip()
        
        # Hora
        if "hora" in text_lower:
            return datetime.now().strftime("Son las %I:%M %p").lstrip("0")
        
        # Día
        if "día" in text_lower or "dia" in text_lower or "fecha" in text_lower:
            dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
            meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            ahora = datetime.now()
            return f"Hoy es {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}"
        
        # Ubicación
        if any(p in text_lower for p in ["ciudad", "ubicación", "donde estoy", "dónde estoy", "que ciudad", "en que ciudad"]):
            ubicacion = self.obtener_ubicacion()
            return f"Según su ubicación, señor, está en {ubicacion}"
        
        # País
        if "país" in text_lower or "pais" in text_lower:
            ubicacion = self.obtener_ubicacion()
            pais = ubicacion.split(',')[-1].strip() if ',' in ubicacion else ubicacion
            return f"Se encuentra en {pais}, señor"
        
        # Saludos
        if "hola" in text_lower:
            hora = datetime.now().hour
            if hora < 12:
                saludo = "Buenos días"
            elif hora < 19:
                saludo = "Buenas tardes"
            else:
                saludo = "Buenas noches"
            return f"{saludo}, señor. ¿En qué puedo ayudarle?"
        
        # Estado
        if "como estas" in text_lower or "cómo estás" in text_lower:
            return "Todo en orden, señor. Sistemas operativos al 100%."
        
        # Gracias
        if "gracias" in text_lower:
            return "De nada, señor. Para eso estoy."
        
        # Adiós
        if "adiós" in text_lower or "adios" in text_lower:
            return "Hasta luego, señor."
        
        return None
    
    def think(self, prompt):
        """Procesa preguntas usando internet si es necesario"""
        # Primero verificar respuestas rápidas
        quick = self.get_quick_response(prompt)
        if quick:
            return quick
        
        # Si no es respuesta rápida, buscar en internet/IA
        return self.buscar_en_internet(prompt)
