"""
Módulo de IA - Cerebro de Jarvis
Respuestas directas garantizadas + ubicación
"""

import subprocess
import re
from datetime import datetime
import requests

class Brain:
    def __init__(self, model="llama3.2", memory_file=None):
        print(f"   🧠 Conectando con IA ({model})...")
        self.model = model
        self.ubicacion = None
        print(f"   ✅ Brain listo")
    
    def obtener_ubicacion(self):
        """Obtiene ubicación aproximada por IP"""
        if self.ubicacion:
            return self.ubicacion
        
        try:
            # Usar servicio gratuito de geolocalización
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
        
        # Ubicación / Ciudad
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
        
        # Celular
        if "celular" in text_lower:
            return "Un celular es un dispositivo móvil para comunicación y aplicaciones, señor."
        
        # Computadora
        if "computador" in text_lower or "computadora" in text_lower:
            return "Una computadora es una máquina que procesa datos y ejecuta programas, señor."
        
        return None
    
    def think(self, prompt):
        """Procesa preguntas que no están en respuestas rápidas"""
        respuestas_por_defecto = [
            f"En relación a '{prompt}', no tengo suficiente información en mi base de datos, señor.",
            f"Disculpe, señor. No he sido programado para responder sobre '{prompt}'.",
            f"No tengo datos sobre '{prompt}', señor. ¿Necesita algo más?",
        ]
        
        import random
        return random.choice(respuestas_por_defecto)
