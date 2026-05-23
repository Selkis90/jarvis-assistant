import subprocess
import webbrowser
import os

class Actions:
    def __init__(self):
        print(f"   🖥️ Cargando módulo de acciones...")
        self.commands = {
            "abrir navegador": self.open_browser,
            "abrir google": self.open_google,
            "abrir youtube": self.open_youtube,
            "bloquear pantalla": self.lock_screen,
            "abrir terminal": self.open_terminal,
        }
        print(f"   ✅ Actions listo ({len(self.commands)} comandos)")
    
    def open_browser(self):
        webbrowser.open("https://www.google.com")
        return "Abriendo navegador, señor"
    
    def open_google(self):
        webbrowser.open("https://www.google.com")
        return "Abriendo Google"
    
    def open_youtube(self):
        webbrowser.open("https://www.youtube.com")
        return "Abriendo YouTube"
    
    def lock_screen(self):
        os.system("gnome-screensaver-command -l 2>/dev/null || loginctl lock-session 2>/dev/null")
        return "Pantalla bloqueada"
    
    def open_terminal(self):
        os.system("gnome-terminal &")
        return "Abriendo terminal"
    
    def execute(self, command_text):
        """Ejecuta un comando si coincide"""
        for cmd, func in self.commands.items():
            if cmd in command_text.lower():
                return func()
        return None
