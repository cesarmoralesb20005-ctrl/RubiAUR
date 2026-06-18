import re
import requests
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

SUSPICIOUS_PATTERNS = [
    (r'(?i)curl\s+.*\|\s*(bash|sh|zsh)', "Ejecución directa de script remoto vía curl"),
    (r'(?i)wget\s+.*\|\s*(bash|sh|zsh)', "Ejecución directa de script remoto vía wget"),
    (r'(?i)(curl|wget)\s+.*https?://(pastebin\.com|bit\.ly|tinyurl\.com|ngrok\.io|t\.co)', "Descarga desde dominio acortador/anónimo"),
    (r'(?i)/etc/ld\.so\.preload', "Modificación de librerías precargadas del sistema (ld.so.preload)"),
    (r'(?i)~\/\.bashrc|~\/\.zshrc', "Modificación de archivos de inicio del usuario"),
    (r'(?i)~\/\.config\/autostart', "Añadiendo programas de inicio automático no estándar"),
    (r'(?i)eval\s+\$', "Ejecución de código ofuscado (eval)"),
    (r'(?i)base64\s+-d\s*\|', "Decodificación y posible ejecución de código Base64"),
    (r'(?i)rm\s+-rf\s+/\s*', "Comando destructivo (rm -rf /)"),
    (r'(?i)chattr\s+\+i', "Haciendo archivos inmutables (típico de malware para evitar ser borrado)"),
    (r'(?i)nc\s+-e\s+/bin/(bash|sh)', "Creación de Reverse Shell (Netcat)"),
    (r'(?i)>\s*/dev/(sda|nvme)', "Escritura directa a bloque de disco"),
]

class SecurityScannerSignals(QObject):
    finished = Signal(bool, list, str) # (is_clean, threats, pkgbuild_code)
    error = Signal(str)

class SecurityScannerWorker(QRunnable):
    """Worker que descarga de forma silenciosa el PKGBUILD de AUR y lo escanea en busca de malware."""
    
    def __init__(self, pkg_name):
        super().__init__()
        self.pkg_name = pkg_name
        self.signals = SecurityScannerSignals()
        
    @Slot()
    def run(self):
        try:
            url = f"https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h={self.pkg_name}"
            # Se usa un timeout prudente para evitar bloqueos
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.signals.error.emit(f"No se pudo descargar el PKGBUILD (HTTP {response.status_code}).")
                return
                
            code = response.text
            threats = []
            
            # Buscar patrones en el código
            for idx, line in enumerate(code.split('\n')):
                for pattern, reason in SUSPICIOUS_PATTERNS:
                    if re.search(pattern, line):
                        threats.append(f"Línea {idx+1}: {reason}\nCódigo: {line.strip()}")
            
            is_clean = len(threats) == 0
            self.signals.finished.emit(is_clean, threats, code)
            
        except Exception as e:
            self.signals.error.emit(str(e))
